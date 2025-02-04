from abaqus import *
from abaqusConstants import *
from caeModules import *
from arcShell import ArcShell

class MeshArcshell:
    def __init__(self, arcshell:ArcShell, global_size=10,  length_size=0):
        self.global_size = global_size
        self.length_size = length_size
        self.__setSeed(arcshell)
        self.__mesh(arcshell)

    def __setSeed(self, arcshell:ArcShell):
        p = mdb.models[arcshell.model_name].parts[arcshell.part_name]
        p.seedPart(size=self.global_size, deviationFactor=0.1, minSizeFactor=0.1)
        if self.length_size:
            pickedEdges = p.edges.getSequenceFromMask(mask=('[#5 ]',), )
            p.seedEdgeBySize(edges=pickedEdges, size=self.length_size, deviationFactor=0.1,
                             constraint=FINER)

    def __mesh(self, arcshell:ArcShell):
        p = mdb.models[arcshell.model_name].parts[arcshell.part_name]
        p.generateMesh()