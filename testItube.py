from abaqus import *
from abaqusConstants import *
from caeModules import *
from partitionItube import *
from itube import Itube
from meshItube import MeshItube
from steelMaterial import SteelMaterial

itube = Itube(length=230, shearkey_nums=5, part_name='itube5w')
SteelMaterial(itube, ((450, 0), (550, 0.05)))
PartitionItube(itube)
MeshItube(12, itube, 2, 4, 2, 4,
          2, False, True)

