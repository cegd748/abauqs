from abaqus import *
from abaqusConstants import *
from caeModules import *
from column4p import Column
from itube import Itube
from concrete import Concrete
from arcShell import ArcShell
from myAssembly4p import MyAssembly
from myInteraction4p import MyInteraction
from myStep import MyStep
from myBoundary4p import MyBoundary

itube = Itube(length=150, shearkey_nums=3)
column = Column(shearkey_nums=3)
concrete = Concrete(itube, column)
shell = ArcShell()
assembly1 = MyAssembly(itube, column, concrete, shell)
step1 = MyStep(assembly1, timeMarks=ON)
interaction1 = MyInteraction(assembly1)
MyBoundary(assembly1, step1, displacement= -60)