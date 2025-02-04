from abaqus import *
from abaqusConstants import *
from caeModules import *
from column4p import Column
from arcShell import ArcShell
from itube import Itube
from concrete import Concrete
from myAssembly4p import MyAssembly

itube = Itube(length=150, shearkey_nums=3)
column = Column(shearkey_nums=3)
shell = ArcShell()
concrete = Concrete(itube, column)
assembly1 = MyAssembly(itube, column, concrete, shell)