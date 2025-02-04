from abaqus import *
from abaqusConstants import *
from caeModules import *
from column4p import Column
from itube import Itube
from concrete import Concrete
from arcShell import ArcShell
from meshArcshell import MeshArcshell
from myInteraction4p import MyInteraction
from myStep import MyStep
from myBoundary4p import MyBoundary
from partitionColumn4p import PartitionColumn
from meshColumn4p import MeshColumn
from partitionItube import PartitionItube
from meshItube import MeshItube
from partitionConcrete import PartitionConcrete
from meshConcrete import MeshConcrete
from steelMaterial import SteelMaterial
from concreteMaterial import ConcreteMaterial
from myAssembly4p import MyAssembly
from jobManagement import *

itube = Itube(length=150, shearkey_nums=3)
column = Column(shearkey_nums=3)
concrete = Concrete(itube, column)
shell = ArcShell()
MeshArcshell(shell, global_size=2.5, length_size=5)

assembly1 = MyAssembly(itube, column, concrete, shell)
step1 = MyStep(assembly1)
interaction1 = MyInteraction(assembly1)
MyBoundary(assembly1, step1, displacement= -70)

PartitionItube(itube)
MeshItube(12, itube, 2, 4, 2, 4, 2)
SteelMaterial(itube)

PartitionColumn(column, 15)
MeshColumn(15, column, 2, 0, 2, 2, 4, pad2_1corner_WEDGE=True)
SteelMaterial(column)

PartitionConcrete(itube, column, concrete, more_partition=False)
MeshConcrete(itube, column, concrete, more_partition=False, outter_size=12)
ConcreteMaterial(concrete)







