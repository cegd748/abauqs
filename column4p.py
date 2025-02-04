from abaqus import *
from abaqusConstants import *
from caeModules import *
from tube import Tube

class Column(Tube):
    def __init__(self, shearkey_nums, shearkey_h=4, shearkey_w=8, shearkey_s=40, shearkey_p=20,
                 pad_thickness=20, pad_pos=50, pad_hole_radius=30, pad_hole_pos=[0.42, 0.42],
                 model_name='Model-1', part_name='column',
                 height1=150, width1=150, height2=50, width2=50, radius1=25, thickness=8, length=800,
                 pad2_pos=350, pad2_thickness=20, pad2_margin=30, pad3_thickness=20, pad3_width=60,
                 tube_name='Set-tube', pad_name='Set-pad',  pad2_name='Set-pad2', pad3_name='Set-pad3', shearkey_name='Set-shearkey'):
        super().__init__(model_name, part_name, height1, width1, height2, width2, radius1, thickness, length)
        self.shearkey_nums = shearkey_nums
        self.shearkey_h = shearkey_h
        self.shearkey_w = shearkey_w
        self.shearkey_s = shearkey_s
        self.shearkey_p = shearkey_p
        self.pad_thickness = pad_thickness
        self.pad_pos = pad_pos
        self.pad_hole_radius = pad_hole_radius
        self.pad_hole_pos = pad_hole_pos
        self.pad2_pos = pad2_pos
        self.pad2_thickness = pad2_thickness
        self.pad2_margin = pad2_margin
        self.pad3_thickness = pad3_thickness
        self.pad3_width = pad3_width
        self.__generatePad()
        self.__generatePad2()
        self.__generatePad3()
        self.__generateShearkey()
        self.sets = _ColumnSet(model_name, part_name, tube_name, pad_name, pad2_name, pad3_name, shearkey_name, shearkey_nums)

    def __generatePad(self):
        plane_z = self.length - self.pad_pos + 0.5 * self.pad_thickness
        p = mdb.models[self.model_name].parts[self.part_name]
        dp = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,offset=plane_z)
        d = p.datums
        e = p.edges.findAt(coordinates=(0, self.radius1 + 0.5 * (self.height1 - 2 * self.radius1), 0))
        t = p.MakeSketchTransform(sketchPlane=d[dp.id], sketchUpEdge=e,
                                  sketchPlaneSide=SIDE1, sketchOrientation=LEFT,
                                  origin=(0.0, 0.0, plane_z))
        s1 = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__',sheetSize=2000, gridSpacing=50, transform=t)
        s1 = _SketchPad(self.model_name, '__profile__', self.height1, self.width1, self.height2,
                        self.width2, self.radius1, self.thickness, self.pad_hole_radius, self.pad_hole_pos)
        p.SolidExtrude(sketchPlane=d[dp.id], sketchUpEdge=e, sketchPlaneSide=SIDE1,
                       sketchOrientation=LEFT, sketch=s1, depth=self.pad_thickness,
                       flipExtrudeDirection=ON, keepInternalBoundaries=ON)
        del mdb.models[self.model_name].sketches['__profile__']

    def __generatePad2(self):
        plane_z = self.pad2_pos + 0.5 * self.pad2_thickness
        p = mdb.models[self.model_name].parts[self.part_name]
        dp = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=plane_z)
        e = p.edges.findAt(coordinates=(0, self.radius1 + 0.5 * (self.height1 - 2 * self.radius1), 0))
        d = p.datums
        t = p.MakeSketchTransform(sketchPlane=d[dp.id], sketchUpEdge=e,
                                  sketchPlaneSide=SIDE1, sketchOrientation=LEFT,
                                  origin=(0.0, 0.0, plane_z))
        s1 = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__', sheetSize=2000, gridSpacing=50, transform=t)
        s1 = _SketchPad2(self.model_name, '__profile__', self.height1, self.width1, self.height2,
                        self.width2, self.radius1, self.thickness, self.pad2_margin)
        p.SolidExtrude(sketchPlane=d[dp.id], sketchUpEdge=e, sketchPlaneSide=SIDE1,
                       sketchOrientation=LEFT, sketch=s1, depth=self.pad2_thickness,
                       flipExtrudeDirection=ON, keepInternalBoundaries=ON)
        del mdb.models[self.model_name].sketches['__profile__']

    def __generatePad3(self):
        p = mdb.models[self.model_name].parts[self.part_name]
        f = p.faces.findAt(coordinates=(self.width1 + self.pad2_margin, 0.5 * self.height1, self.pad2_pos))
        e = p.edges.findAt(coordinates=(self.width1 + self.pad2_margin, 0.5 * self.height1, self.pad2_pos - 0.5 * self.pad2_thickness))
        t = p.MakeSketchTransform(sketchPlane=f, sketchUpEdge=e,
                                  sketchPlaneSide=SIDE1, sketchOrientation=RIGHT,
                                  origin=(self.width1 + self.pad2_margin, self.height1, self.pad2_pos))
        s = mdb.models[self.model_name].ConstrainedSketch(name='__profile__',
                                                    sheetSize=400, gridSpacing=10, transform=t)
        p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
        s.rectangle(point1=(-0.5 * self.pad3_width, 0.0), point2=(0.5 * self.pad3_width, self.pad3_thickness))
        p.SolidExtrude(sketchPlane=f, sketchUpEdge=e, sketchPlaneSide=SIDE1,
                       sketchOrientation=RIGHT, sketch=s, depth=self.width1 + 2 * self.pad2_margin,
                       flipExtrudeDirection=ON, keepInternalBoundaries=ON)
        del mdb.models[self.model_name].sketches['__profile__']

    def __generateShearkey(self):
        s1 = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__',sheetSize=2000, gridSpacing=50,
            transform=(-1.0, 0.0, 0.0, 0.0, 0.0, 1.0, -0.0, 1.0, -0.0,
                       self.width1 - self.width2 - self.thickness, self.height1 - self.thickness, 0.0))
        p = mdb.models[self.model_name].parts[self.part_name]
        for i in range(self.shearkey_nums):
            pos = i * self.shearkey_s + self.shearkey_p
            s1.Arc3Points(point1=(0.0, pos - 0.5 * self.shearkey_w),
                         point2=(0.0, pos + 0.5 * self.shearkey_w),
                         point3=(self.shearkey_h, pos))
            s1.Line(point1=(0.0, pos - 0.5 * self.shearkey_w),
                   point2=(0.0, pos + 0.5 * self.shearkey_w))
        deltaZ = 0.1
        e = p.edges.findAt(coordinates=(self.radius1, self.height1, deltaZ))
        pickedEdges = p.edges.getByBoundingBox(
            xMin=0, xMax=self.width1,
            yMin=0, yMax=self.height1,
            zMin=-deltaZ, zMax=deltaZ)
        p.SolidSweep(path=pickedEdges[int(0.5 * len(pickedEdges)) : ], sketchUpEdge=e, sketchOrientation=RIGHT,
                     profile=s1, keepInternalBoundaries=ON)
        del mdb.models[self.model_name].sketches['__profile__']

class _ColumnSet:
    def __init__(self, model_name, part_name, tube_name,
                 pad_name, pad2_name, pad3_name, shearkey_name, shearkey_nums):
        self.tube = tube_name
        self.pad = pad_name
        self.pad2 = pad2_name
        self.pad3 = pad3_name
        self.shearkey = shearkey_name
        self.__createSet(model_name, part_name, shearkey_nums)

    def __createSet(self, model_name, part_name, shearkey_nums):
        p = mdb.models[model_name].parts[part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#7 ]',), )
        p.Set(cells=cells, name=self.tube)

        cells = c.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(cells=cells, name=self.pad)

        cells = c.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(cells=cells, name=self.pad2)

        cells = c.getSequenceFromMask(mask=('[#20 ]',), )
        p.Set(cells=cells, name=self.pad3)

        bi_string = '000000'
        for i in range(shearkey_nums):
            bi_string = '1' + bi_string
        hex_string = hex(int(bi_string, 2))[2:]
        shearkeys_mask = '[#' + hex_string + ' ]'
        cells = c.getSequenceFromMask(mask=(shearkeys_mask,), )
        p.Set(cells=cells, name=self.shearkey)

def _SketchPad(model_name, sketch_name, height1, width1, height2, width2, radius1, thickness, pad_hole_radius, pad_hole_pos):
    sketch = mdb.models[model_name].sketches[sketch_name]
    g, v, d, c = sketch.geometry, sketch.vertices, sketch.dimensions, sketch.constraints
    vertices = ((0, 0), (0, height1), (width1 - width2, height1), (width1 - width2, height1 - height2),
                (width1, height1 - height2), (width1, 0), (0, 0))
    lines = []
    for i in range(len(vertices) - 1):
        lines.append(sketch.Line(point1=vertices[i], point2=vertices[i + 1]))

    sketch.FilletByRadius(radius=radius1, curve1=lines[0], nearPoint1=(0, radius1), curve2=lines[5],
                          nearPoint2=(radius1, 0))
    sketch.FilletByRadius(radius=radius1, curve1=lines[0], nearPoint1=(0, height1 - radius1), curve2=lines[1],
                          nearPoint2=(radius1, height1))
    sketch.FilletByRadius(radius=radius1, curve1=lines[4], nearPoint1=(width1, radius1), curve2=lines[5],
                          nearPoint2=(width1 - radius1, 0))
    sketch.FilletByRadius(radius=radius1 - thickness, curve1=lines[2],
                          nearPoint1=(width1 - width2, height1 - height2 + radius1 - thickness),
                          curve2=lines[3], nearPoint2=(width1 - width2 + radius1 - thickness, height1 - height2))
    sketch.CircleByCenterPerimeter(center=(width1 * pad_hole_pos[0], height1 * pad_hole_pos[1]),
                               point1=(width1 * pad_hole_pos[0],
                                       height1 * pad_hole_pos[1] - pad_hole_radius))
    return sketch

def _SketchPad2(model_name, sketch_name, height1, width1, height2, width2, radius1, thickness, pad2_margin):
    sketch = mdb.models[model_name].sketches[sketch_name]
    vertices = [(0, 0), (0, height1), (width1 - width2, height1), (width1 - width2, height1 - height2),
                (width1, height1 - height2), (width1, 0), (0, 0)]
    lines = []
    for i in range(len(vertices) - 1):
        lines.append(sketch.Line(point1=vertices[i], point2=vertices[i + 1]))

    sketch.FilletByRadius(radius=radius1, curve1=lines[0], nearPoint1=(0, radius1), curve2=lines[5],
                          nearPoint2=(radius1, 0))
    sketch.FilletByRadius(radius=radius1, curve1=lines[0], nearPoint1=(0, height1 - radius1), curve2=lines[1],
                          nearPoint2=(radius1, height1))
    sketch.FilletByRadius(radius=radius1, curve1=lines[4], nearPoint1=(width1, radius1), curve2=lines[5],
                          nearPoint2=(width1 - radius1, 0))
    sketch.FilletByRadius(radius=radius1 - thickness, curve1=lines[2],
                          nearPoint1=(width1 - width2, height1 - height2 + radius1 - thickness),
                          curve2=lines[3], nearPoint2=(width1 - width2 + radius1 - thickness, height1 - height2))
    sketch.delete((lines[1], ))
    vertices = [(radius1, height1), (-pad2_margin, height1), (-pad2_margin, -pad2_margin),
                (width1 + pad2_margin, -pad2_margin), (width1 + pad2_margin, height1), (width1 - width2, height1)]
    for i in range(len(vertices) - 1):
        lines.append(sketch.Line(point1=vertices[i], point2=vertices[i + 1]))

    return sketch
