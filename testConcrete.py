from abaqus import *
from abaqusConstants import *
from caeModules import *
from column3p import Column
from itube import Itube
from concrete import Concrete
from partitionConcrete import PartitionConcrete
from meshConcrete import MeshConcrete

itube = Itube(length=230, shearkey_nums=5, part_name='itube')
column = Column(shearkey_nums=5, part_name='column')
concrete = Concrete(itube, column, part_name='concrete', length=230)
PartitionConcrete(itube, column, concrete, more_partition=False)
MeshConcrete(itube, column, concrete, outter_size=12, more_partition=False)