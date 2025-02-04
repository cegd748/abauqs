from abaqus import *
from abaqusConstants import *
from caeModules import *
from itube import Itube


class ItubeSet:
    def __init__(self, itube: Itube, tube_name='Set-tube',
                 pad_name='Set-pad', shearkey_name='Set-shearkey'):
        self.tube = tube_name
        self.pad = pad_name
        self.shearkey = shearkey_name
        self.itube = itube
        self.__createSet(itube)

    def __createSet(self, itube: Itube):

        p = mdb.models[itube.model_name].parts[itube.part_name]
        c = p.cells

        cells = c.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(cells=cells, name=self.tube)

        cells = c.getSequenceFromMask(mask=('[#2 ]',), )
        p.Set(cells=cells, name=self.pad)

        bi_string = '00'
        for i in range(itube.shearkey_nums):
            bi_string = '1' + bi_string
        hex_string = hex(int(bi_string, 2))[2:]
        shearkeys_mask = '[#' + hex_string + ' ]'
        cells = c.getSequenceFromMask(mask=(shearkeys_mask,), )
        p.Set(cells=cells, name=self.shearkey)