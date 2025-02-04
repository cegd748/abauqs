from abaqus import *
from abaqusConstants import *
from caeModules import *
from itube import Itube

class PartitionItube:
    def __init__(self, itube: Itube):
        self.__partition(itube)

    def __partition(self, itube:Itube):
        self.__partition_z(itube)
        self.__partition_xy(itube)

    def __partition_z(self, itube: Itube):
        p = mdb.models[itube.model_name].parts[itube.part_name]
        datumz_index = []
        datumz = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=itube.pad_thickness)
        datumz_index.append(datumz.id)
        ini_p = itube.pad_thickness + itube.shearkey_p
        for i in range(itube.shearkey_nums):
            datumz = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                         offset=ini_p - 0.5 * itube.shearkey_w + i * itube.shearkey_s)
            datumz_index.append(datumz.id)
            datumz = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,
                                         offset=ini_p + 0.5 * itube.shearkey_w + i * itube.shearkey_s)
            datumz_index.append(datumz.id)
        d = p.datums
        for i in datumz_index:
            pickedCells = p.cells
            p.PartitionCellByDatumPlane(datumPlane=d[i], cells=pickedCells)

    def __partition_xy(self, itube: Itube):
        p = mdb.models[itube.model_name].parts[itube.part_name]

        x_pos = [0, itube.radius1, itube.width1 - itube.width2 - itube.thickness,
                 itube.width1 - itube.width2, itube.width1 - itube.width2 + itube.radius1 - itube.thickness,
                 itube.width1 - itube.radius1, itube.width1 - itube.thickness, itube.width1]
        y_pos = [0, itube.radius1, itube.height1 - itube.height2 - itube.thickness,
                 itube.height1 - itube.height2, itube.height1 - itube.height2 + itube.radius1 - itube.thickness,
                 itube.height1 - itube.radius1, itube.height1 - itube.thickness, itube.height1]
        datumx_index = []
        datumy_index = []
        for i in range(len(x_pos)):
            datumx = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x_pos[i])
            datumx_index.append(datumx.id)
        for i in range(len(y_pos)):
            datumy = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=y_pos[i])
            datumy_index.append(datumy.id)

        d = p.datums

        #1
        pickedCells = p.cells
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[1]], cells=pickedCells)
        pickedCells = p.cells
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[1]], cells=pickedCells)

        pad_xMin = -0.5 * (itube.pad_width - itube.width1)
        pad_xMax = itube.width1 + 0.5 * (itube.pad_width - itube.width1)
        pad_yMin = -0.5 * (itube.pad_height - itube.height1)
        pad_yMax = itube.height1 + 0.5 * (itube.pad_height - itube.height1)
        pad_zMin = 0
        pad_zMax = itube.pad_thickness
        tube_xMin = 0
        tube_xMax = itube.width1
        tube_yMin = 0
        tube_yMax = itube.height1
        tube_zMin = 0
        tube_zMax = itube.length

        #2
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[1], xMax=pad_xMax,
            yMin=pad_yMin, yMax=y_pos[1],
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[5]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=pad_xMin, xMax=x_pos[1],
            yMin=y_pos[1], yMax=pad_yMax,
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[5]], cells=pickedCells)

        #3
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[1], xMax=pad_xMax,
            yMin=y_pos[1], yMax=pad_yMax,
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[4]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[1], xMax=pad_xMax,
            yMin=y_pos[1], yMax=pad_yMax,
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[4]], cells=pickedCells)

        #4
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[1], xMax=x_pos[4],
            yMin=y_pos[4], yMax=pad_yMax,
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[2]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[4], xMax=pad_xMax,
            yMin=y_pos[1], yMax=y_pos[4],
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[2]], cells=pickedCells)

        #5
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[4], xMax=pad_xMax,
            yMin=y_pos[2], yMax=pad_yMax,
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[6]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[2], xMax=pad_xMax,
            yMin=y_pos[4], yMax=pad_yMax,
            zMin=0, zMax=tube_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[6]], cells=pickedCells)

        #6
        pickedCells = p.cells.getByBoundingBox(
            xMin=pad_xMin, xMax=pad_xMax,
            yMin=pad_yMin, yMax=pad_yMax,
            zMin=pad_zMin, zMax=pad_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[0]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=pad_xMin, xMax=pad_xMax,
            yMin=pad_yMin, yMax=pad_yMax,
            zMin=pad_zMin, zMax=pad_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[7]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=pad_xMin, xMax=pad_xMax,
            yMin=pad_yMin, yMax=pad_yMax,
            zMin=pad_zMin, zMax=pad_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[0]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=pad_xMin, xMax=pad_xMax,
            yMin=pad_yMin, yMax=pad_yMax,
            zMin=pad_zMin, zMax=pad_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[7]], cells=pickedCells)

        #7
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[2], xMax=x_pos[4],
            yMin=y_pos[7], yMax=pad_yMax,
            zMin=pad_zMin, zMax=pad_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumx_index[3]], cells=pickedCells)
        pickedCells = p.cells.getByBoundingBox(
            xMin=x_pos[7], xMax=pad_xMax,
            yMin=y_pos[2], yMax=y_pos[4],
            zMin=pad_zMin, zMax=pad_zMax)
        p.PartitionCellByDatumPlane(datumPlane=d[datumy_index[3]], cells=pickedCells)

        #8
        corner_shearkeys = []
        x = x_pos[3]
        y = y_pos[7] + 0.5 * itube.shearkey_h
        z = itube.pad_thickness + itube.shearkey_p
        for i in range(itube.shearkey_nums):
            corner_shearkeys.append(((x, y, z + i * itube.shearkey_s), ))
        pickedCells = p.cells.findAt(*corner_shearkeys)
        corner_shearkeys.clear()
        datum1 = p.DatumPointByCoordinate(coords=(x_pos[3], y_pos[7], 0.0)).id
        datum2 = p.DatumPointByCoordinate(coords=(x_pos[3], y_pos[7], 1)).id
        datum3 = p.DatumPointByCoordinate(coords=(x_pos[3] + 1, y_pos[7] + 1, 0.0)).id
        p.PartitionCellByPlaneThreePoints(point1=d[datum1], point2=d[datum2],
                                          cells=pickedCells, point3=d[datum3])
        x = x_pos[7]
        y = y_pos[3] + 0.5 * itube.shearkey_h
        z = itube.pad_thickness + itube.shearkey_p
        for i in range(itube.shearkey_nums):
            corner_shearkeys.append(((x, y, z + i * itube.shearkey_s), ))
        pickedCells = p.cells.findAt(*corner_shearkeys)
        datum1 = p.DatumPointByCoordinate(coords=(x_pos[7], y_pos[3], 0.0)).id
        datum2 = p.DatumPointByCoordinate(coords=(x_pos[7], y_pos[3], 1)).id
        datum3 = p.DatumPointByCoordinate(coords=(x_pos[7] + 1, y_pos[3] + 1, 0.0)).id
        p.PartitionCellByPlaneThreePoints(point1=d[datum1], point2=d[datum2],
                                          cells=pickedCells, point3=d[datum3])