from abaqus import *
from abaqusConstants import *
from caeModules import *
from column3p import Column
from itube import Itube
from concrete import Concrete
from myInteraction3p import MyInteraction
from myStep import MyStep
from myBoundary3p import MyBoundary
from partitionColumn3p import PartitionColumn
from meshColumn3p import MeshColumn
from partitionItube import PartitionItube
from meshItube import MeshItube
from partitionConcrete import PartitionConcrete
from meshConcrete import MeshConcrete
from steelMaterial import SteelMaterial
from concreteMaterial import ConcreteMaterial
from myAssembly3p import MyAssembly
from jobManagement import *

itube = Itube(length=150, shearkey_nums=3)
column = Column(shearkey_nums=3)
concrete = Concrete(itube, column)


assembly1 = MyAssembly(itube, column, concrete, itube.model_name)
step1 = MyStep(assembly1)
interaction1 = MyInteraction(assembly1)
MyBoundary(assembly1, step1, displacement= -70)

PartitionItube(itube)
MeshItube(12, itube, 2, 4, 2, 4, 2)
SteelMaterial(itube)

PartitionColumn(column, 15)
MeshColumn(15, column, 2, 4, 2, 2, 4)
SteelMaterial(column)

PartitionConcrete(itube, column, concrete, more_partition=False)
MeshConcrete(itube, column, concrete, more_partition= False, outter_size=12)
ConcreteMaterial(concrete)






