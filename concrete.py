from abaqus import *
from abaqusConstants import *
from caeModules import *
from itube import Itube
from column3p import Column

class _ConcreteSet:
    def __init__(self, model_name, part_name, length, itube:Itube, column:Column,
                 outer_concrete_name, inner_concrete_name, other_concrete_name):
        self.model_name = model_name
        self.part_name = part_name
        self.outer_concrete = outer_concrete_name
        self.inner_concrete = inner_concrete_name
        self.other_concrete = other_concrete_name
        if length > itube.length - itube.pad_thickness:
            self.__partition(itube, column, length)
            self.__createSetPlanA()
        else:
            self.__createSetPlanB()

    def __partition(self, itube:Itube, column:Column, length):
        p = mdb.models[self.model_name].parts[self.part_name]

        offset_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1)
        offset_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1)
        height1 = itube.height1
        width1 = itube.width1
        zMid = itube.length - itube.pad_thickness
        deltaZ = 0.1
        pickedCells = p.cells
        pickedEdges = p.edges.getByBoundingBox(
            xMin=offset_x, xMax=width1 + offset_x,
            yMin=offset_y, yMax=height1 + offset_y,
            zMin=zMid - deltaZ, zMax=zMid + deltaZ)
        pickedline = p.edges.findAt(coordinates=(0, column.radius1 - column.thickness, 0.5 * column.shearkey_p))
        p.PartitionCellByExtrudeEdge(line=pickedline, cells=pickedCells, edges=pickedEdges, sense=REVERSE)

    def __createSetPlanA(self):
        p = mdb.models[self.model_name].parts[self.part_name]

        cells = p.cells.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(cells=cells, name=self.outer_concrete)

        cells = p.cells.getSequenceFromMask(mask=('[#9 ]',), )
        p.Set(cells=cells, name=self.inner_concrete)

        cells = p.cells.getSequenceFromMask(mask=('[#2 ]',), )
        p.Set(cells=cells, name=self.other_concrete)

    def __createSetPlanB(self):
        p = mdb.models[self.model_name].parts[self.part_name]

        cells = p.cells.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(cells=cells, name=self.outer_concrete)

        cells = p.cells.getSequenceFromMask(mask=('[#6 ]',), )
        p.Set(cells=cells, name=self.inner_concrete)

def _Sketch(s, offset_x, offset_y, radius1, radius2, width1, width2, height1, height2, offset_line=0):
    vertices = ((0 + offset_x, 0 + offset_y), (0 + offset_x, height1 + offset_y), (width1 - width2 + offset_x, height1 + offset_y),
    (width1 - width2 + offset_x, height1 - height2 + offset_y),
    (width1 + offset_x, height1 - height2 + offset_y), (width1 + offset_x, 0 + offset_y), (0 + offset_x, 0 + offset_y))
    lines = []
    for i in range(len(vertices) - 1):
        line = s.Line(point1=vertices[i], point2=vertices[i + 1])
        lines.append(line)

    lines.append(s.FilletByRadius(radius=radius1, curve1=lines[0], nearPoint1=(0 + offset_x, radius1 + offset_y),
                                  curve2=lines[5], nearPoint2=(radius1 + offset_x, 0 + offset_y)))
    lines.append(s.FilletByRadius(radius=radius1, curve1=lines[0], nearPoint1=(0 + offset_x, height1 - radius1 + offset_y),
                         curve2=lines[1], nearPoint2=(radius1 + offset_x, height1 + offset_y)))
    lines.append(s.FilletByRadius(radius=radius1, curve1=lines[4], nearPoint1=(width1 + offset_x, radius1 + offset_y),
                                  curve2=lines[5], nearPoint2=(width1 - radius1 + offset_x, 0 + offset_y)))
    lines.append(s.FilletByRadius(radius=radius2, curve1=lines[2], nearPoint1=(width1 - width2 + offset_x, height1 - height2 + radius2 + offset_y),
                                  curve2=lines[3], nearPoint2=(width1 - width2 + radius2 + offset_x, height1 - height2 + offset_y)))
    if offset_line:
        s.offset(distance=offset_line, objectList=lines, side=LEFT)

    return s

class Concrete:
    def __init__(self, itube:Itube, column:Column, model_name='Model-1', part_name='concrete', length=0,
                 outer_concrete_name='outer', inner_concrete_name='inner', other_concrete_name='other'):
        self.model_name = model_name
        self.part_name = part_name
        self.length = length if length else itube.length - itube.pad_thickness
        self.concrete = self.__GenerateConcrete(itube, column)
        self.sets = _ConcreteSet(model_name, part_name, self.length, itube, column,
                                 outer_concrete_name, inner_concrete_name, other_concrete_name)

    def __GenerateConcrete(self, itube:Itube, column:Column):
        self.__GenerateEntity(itube, column)
        self.__CutItubeTube(itube, column)
        self.__GenerateProtruding(itube, column)
        self.__SweepItubeShearkey(itube, column)
        self.__SweepColumnShearkey(itube, column)

        return mdb.models[self.model_name].parts[self.part_name]

    def __GenerateEntity(self, itube:Itube, column:Column):
        sketch = mdb.models[self.model_name].ConstrainedSketch(name='sketch_concrete', sheetSize=200.0)

        radius1 = column.radius1 - column.thickness
        radius2 = column.radius1
        height1 = column.height1 - 2 * column.thickness
        width1 = column.width1 - 2 * column.thickness
        height2 = column.height2
        width2 = column.width2

        sketch = _Sketch(sketch, 0, 0, radius1, radius2, width1, width2, height1, height2)

        concrete = mdb.models[self.model_name].Part(name=self.part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        concrete.BaseSolidExtrude(sketch=sketch, depth=self.length)
        del mdb.models[self.model_name].sketches['sketch_concrete']

    def __CutItubeTube(self, itube:Itube, column:Column):
        p = mdb.models[self.model_name].parts[self.part_name]
        f, e = p.faces, p.edges
        t = p.MakeSketchTransform(sketchPlane=f[11], sketchUpEdge=e[2], sketchPlaneSide=SIDE2, sketchOrientation=LEFT, origin=(0.0, 0.0, 0.0))
        s = mdb.models[self.model_name].ConstrainedSketch(name='__profile__', sheetSize=400, gridSpacing=10, transform=t)

        offset_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1)
        offset_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1)
        height1 = itube.height1
        height2 = itube.height2
        width1 = itube.width1
        width2 = itube.width2
        radius1 = itube.radius1
        radius2 = itube.radius1 - itube.thickness
        offset_line = itube.thickness

        s = _Sketch(s, offset_x, offset_y, radius1, radius2, width1, width2, height1, height2, offset_line)
        p.CutExtrude(sketchPlane=f[11], sketchUpEdge=e[2], sketchPlaneSide=SIDE2, sketchOrientation=LEFT, sketch=s, depth=itube.length - itube.pad_thickness, flipExtrudeDirection=ON)

        del mdb.models[self.model_name].sketches['__profile__']

    def __GenerateProtruding(self, itube:Itube, column:Column):
        p = mdb.models[self.model_name].parts[self.part_name]

        offset_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1 + 2 * itube.thickness)
        offset_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1 + 2 * itube.thickness)
        height1 = itube.height1 - 2 * itube.thickness
        height2 = itube.height2
        width1 = itube.width1 - 2 * itube.thickness
        width2 = itube.width2
        radius1 = itube.radius1 - itube.thickness
        radius2 = itube.radius1

        f = p.faces.findAt(coordinates=(radius1 + offset_x, radius1 + offset_y, 0))
        e = p.edges.findAt(coordinates=(width1 + offset_x, radius1 + 0.5 * (height1 - height2 - radius1) + offset_y, 0))
        t = p.MakeSketchTransform(sketchPlane=f, sketchUpEdge=e, sketchPlaneSide=SIDE2, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
        s = mdb.models[self.model_name].ConstrainedSketch(name='__profile__', sheetSize=400, gridSpacing=10, transform=t)
        p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
        s = _Sketch(s, offset_x, offset_y, radius1, radius2, width1, width2, height1, height2)
        p.SolidExtrude(sketchPlane=f, sketchUpEdge=e, sketchPlaneSide=SIDE2, sketchOrientation=RIGHT, sketch=s,
                       depth=itube.pad_thickness, flipExtrudeDirection=ON, keepInternalBoundaries=ON)

        del mdb.models[self.model_name].sketches['__profile__']

    def __SweepItubeShearkey(self, itube:Itube, column:Column):
        offset_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1)
        offset_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1)
        height1 = itube.height1
        height2 = itube.height2
        width1 = itube.width1
        width2 = itube.width2
        radius1 = itube.radius1
        radius2 = itube.radius1 - itube.thickness

        s = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__',sheetSize=400, gridSpacing=10,
            transform=(1.0, 0.0, -0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, offset_x, radius1 + offset_y, 0.0))
        p = mdb.models[self.model_name].parts[self.part_name]

        for i in range(itube.shearkey_nums):
            pos = i * itube.shearkey_s + itube.shearkey_p
            s.Arc3Points(point1=(0.0, pos - 0.5 * itube.shearkey_w),
                         point2=(0.0, pos + 0.5 * itube.shearkey_w),
                         point3=(-itube.shearkey_h, pos))
            s.Line(point1=(0.0, pos - 0.5 * itube.shearkey_w),
                   point2=(0.0, pos + 0.5 * itube.shearkey_w))

        face = p.faces.findAt(coordinates=(0.5*offset_x, 0.5*(column.height1 - 2 * column.thickness), 0))
        EdgesId = face.getEdges()
        pathEdgesId = EdgesId[:int(0.5 * len(EdgesId))]
        pathEdgesList = []
        for edgeId in pathEdgesId:
            pathEdgesList.append(p.edges[edgeId])
        pathEdges = part.EdgeArray(pathEdgesList)
        h = min(itube.length - itube.pad_thickness, self.length)
        referenceEdge = p.edges.findAt(coordinates=(width1 + offset_x, height1 - height2 + offset_y, 0.5 * h))
        p.CutSweep(path=pathEdges, sketchUpEdge=referenceEdge, sketchOrientation=RIGHT,
                   profile=s)
        del mdb.models[self.model_name].sketches['__profile__']

    def __SweepColumnShearkey(self, itube:Itube, column:Column):
        height1 = column.height1 - 2 * column.thickness
        height2 = column.height2
        width1 = column.width1 - 2 * column.thickness
        width2 = column.width2
        radius1 = column.radius1 - column.thickness
        radius2 = column.radius1
        grout_thickness_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1)
        grout_thickness_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1)

        s = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__', sheetSize=400, gridSpacing=10,
            transform=(-1.0, 0.0, 0.0, 0.0, -0.0, 1.0, 0.0, 1.0, 0.0, 0.0, height1 - radius1, 0.0))
        p = mdb.models[self.model_name].parts[self.part_name]

        for i in range(column.shearkey_nums):
            pos = i * column.shearkey_s + column.shearkey_p
            s.Arc3Points(point1=(0.0, pos - 0.5 * column.shearkey_w),
                         point2=(0.0, pos + 0.5 * column.shearkey_w),
                         point3=(-column.shearkey_h, pos))
            s.Line(point1=(0.0, pos - 0.5 * column.shearkey_w),
                   point2=(0.0, pos + 0.5 * column.shearkey_w))

        face = p.faces.findAt(coordinates=(0.5 * grout_thickness_x, 0.5 * height1, 0))
        EdgesId = face.getEdges()
        pathEdgesId = EdgesId[int(0.5 * len(EdgesId)):]
        pathEdgesList = []
        for edgeId in pathEdgesId:
            pathEdgesList.append(p.edges[edgeId])
        pathEdges = part.EdgeArray(pathEdgesList)
        h = self.length
        referenceEdge = p.edges.findAt(coordinates=(width1 - width2, height1, 0.5 * h))
        p.CutSweep(path=pathEdges, sketchUpEdge=referenceEdge, sketchOrientation=LEFT,
                   profile=s)
        del mdb.models[self.model_name].sketches['__profile__']