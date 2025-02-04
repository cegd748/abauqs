from abaqus import *
from abaqusConstants import *
from caeModules import *
from concrete import Concrete
from column3p import Column

from itube import Itube

class PartitionConcrete:
    def __init__(self, itube:Itube, column:Column, concrete:Concrete, more_partition=True):
        self.more_partition = more_partition
        self.__partition(itube, column, concrete)

    def __partition(self, itube:Itube, column:Column, concrete:Concrete):
        self.__partitionOuterXY(itube, column, concrete)
        self.__partitionZ(itube, column, concrete)
        self.__partitionInnerXY(itube, column, concrete)

    def __partitionOuterXY(self, itube:Itube, column:Column, concrete:Concrete):
        offset_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1)
        offset_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1)
        height1 = column.height1 - 2 * column.thickness
        width1 = column.width1 - 2 * column.thickness

        p = mdb.models[concrete.model_name].parts[concrete.part_name]
        sketchFace = p.faces.findAt(coordinates=(column.radius1 - column.thickness, column.radius1 - column.thickness, 0))
        sketchEdge = p.edges.findAt(coordinates=(width1, column.radius1 - column.thickness + 0.1, 0))
        t = p.MakeSketchTransform(sketchPlane=sketchFace, sketchUpEdge=sketchEdge, sketchPlaneSide=SIDE2, origin=(0.0, 0.0, 0.0))
        s = mdb.models[concrete.model_name].ConstrainedSketch(name='__profile__', sheetSize=400, gridSpacing=10, transform=t)

        #radius1
        dH1 = offset_x + itube.radius1
        dV1 = offset_y + itube.radius1

        s.Line(point1=(dH1, dV1), point2=(0, 0))
        s.Line(point1=(dH1, dV1), point2=(0, dV1))
        s.Line(point1=(dH1, dV1), point2=(dH1, 0))

        s.Line(point1=(dH1, height1 - dV1), point2=(0, height1))
        s.Line(point1=(dH1, height1 - dV1), point2=(0, height1 - dV1))
        s.Line(point1=(dH1, height1 - dV1), point2=(dH1, height1))

        s.Line(point1=(width1 - dH1, dV1), point2=(width1, 0))
        s.Line(point1=(width1 - dH1, dV1), point2=(width1 - dH1, 0))
        s.Line(point1=(width1 - dH1, dV1), point2=(width1, dV1))

        # radius2
        dH2 = (column.width1 - 2 * column.thickness - column.width2 -
               (itube.width1 - itube.width2) - offset_x + column.radius1)
        dV2 = (column.height1 - 2 * column.thickness - column.height2 -
               (itube.height1 - itube.height2) - offset_y + column.radius1)
        x2 = width1 - column.width2 + column.radius1
        y2 = height1 - column.height2 + column.radius1

        s.Line(point1=(x2, y2), point2=(x2 - dH2, y2 - dV2))
        s.Line(point1=(x2, y2), point2=(x2 - dH2, y2))
        s.Line(point1=(x2, y2), point2=(x2, y2 - dV2))

        #other
        s.Line(point1=(itube.width1 - itube.width2 + offset_x, itube.height1 + offset_y),
                            point2=(width1 - column.width2, height1))
        s.Line(point1=(itube.width1 + offset_x, itube.height1 - itube.height2 + offset_y),
                            point2=(width1, height1 - column.height2))

        p.PartitionFaceBySketch(sketchUpEdge=sketchEdge, faces=sketchFace, sketch=s)
        del mdb.models[concrete.model_name].sketches['__profile__']

        p = mdb.models[concrete.model_name].parts[concrete.part_name]

        pickLine = p.edges.findAt(coordinates=(column.radius1 - column.thickness, 0, 0.5 * column.shearkey_p))
        pickedCells = p.sets[concrete.sets.outer_concrete].cells

        deltaH = 0.1
        faces = p.faces.getByBoundingBox(xMin=0, xMax=width1,
                                         yMin=0, yMax=height1,
                                         zMin=-deltaH, zMax=deltaH)
        excludeFace = p.faces.findAt(coordinates=(itube.radius1 + offset_x, itube.radius1 + offset_y, 0))
        excludeEdges1Id = excludeFace.getEdges()
        facesList = [face for face in faces if face.index != excludeFace.index]
        faceArray = part.FaceArray(facesList)
        subEdgesArray = faceArray.getExteriorEdges()

        EdgesArray = p.edges.getByBoundingBox(xMin=0, xMax=width1,
                                              yMin=0, yMax=height1,
                                              zMin=-deltaH, zMax=deltaH)
        pickedEdges = []
        for pickedEdge in EdgesArray:
            if pickedEdge.index not in {exteriorEdge.index for exteriorEdge in subEdgesArray}:
                if pickedEdge.index not in excludeEdges1Id:
                    pickedEdges.append(pickedEdge)

        p.PartitionCellByExtrudeEdge(line=pickLine, cells=pickedCells, edges=pickedEdges, sense=REVERSE)

    def __partitionZ(self, itube:Itube, column:Column, concrete:Concrete):
        p = mdb.models[concrete.model_name].parts[concrete.part_name]
        datumz_offset = []
        itubeEndPos = itube.length - itube.pad_thickness

        for i in range(column.shearkey_nums):
            pos = column.shearkey_p + i * column.shearkey_s
            datumz_offset.append(pos)
        for i in range(itube.shearkey_nums):
            pos = itube.shearkey_p + i * itube.shearkey_s
            datumz_offset.append(pos)
        if concrete.length > itubeEndPos:
            datumz_offset.append(itubeEndPos)

        datumz_offset = sorted(set(datumz_offset))

        if self.more_partition:
            prepos = 0
            size = len(datumz_offset)
            maxShearkeyW = max(column.shearkey_w, itube.shearkey_w)
            cutLength = 1.6 * maxShearkeyW
            for i in range(size):
                if abs(prepos - datumz_offset[i]) >= cutLength:
                    datumz_offset.append((prepos + datumz_offset[i]) / 2)
                prepos = datumz_offset[i]

            if concrete.length <= itubeEndPos:
                if itubeEndPos - prepos >= cutLength:
                    datumz_offset.append((itubeEndPos + prepos) / 2)

        datumz_offset.sort()
        datumz_index = []
        for offsetZ in datumz_offset:
            datumz = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=offsetZ)
            datumz_index.append(datumz.id)

        d = p.datums
        for index in datumz_index:
            pickedCells = p.sets[concrete.sets.outer_concrete].cells
            p.PartitionCellByDatumPlane(datumPlane=d[index], cells=pickedCells)

        if concrete.length > itubeEndPos:
            pickedCells = p.sets[concrete.sets.inner_concrete].cells
            p.PartitionCellByDatumPlane(datumPlane=d[datumz_index[-1]], cells=pickedCells)

    def __partitionInnerXY(self, itube:Itube, column:Column, concrete:Concrete):
        p = mdb.models[concrete.model_name].parts[concrete.part_name]
        offset_x = 0.5 * (column.width1 - 2 * column.thickness - itube.width1)
        offset_y = 0.5 * (column.height1 - 2 * column.thickness - itube.height1)
        datumx_offset = [itube.radius1 + offset_x,
                         itube.width1 - itube.width2 - itube.thickness + offset_x,
                         itube.width1 - itube.width2 - itube.thickness + itube.radius1 + offset_x,
                         itube.width1 - itube.radius1 + offset_x]
        datumy_offset = [itube.radius1 + offset_y,
                         itube.height1 - itube.height2 - itube.thickness + offset_y,
                         itube.height1 - itube.height2 - itube.thickness + itube.radius1 + offset_y,
                         itube.height1 - itube.radius1 + offset_y]

        datumx_index = []
        for offsetX in datumx_offset:
            datumx = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetX)
            datumx_index.append(datumx.id)
        datumy_index = []
        for offsetY in datumy_offset:
            datumy = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offsetY)
            datumy_index.append(datumy.id)

        d = p.datums
        for index in datumx_index:
            pickedCells = p.sets[concrete.sets.inner_concrete].cells
            p.PartitionCellByDatumPlane(datumPlane=d[index], cells=pickedCells)
        for index in datumy_index:
            pickedCells = p.sets[concrete.sets.inner_concrete].cells
            p.PartitionCellByDatumPlane(datumPlane=d[index], cells=pickedCells)