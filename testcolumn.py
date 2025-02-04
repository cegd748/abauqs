from abaqus import *
from abaqusConstants import *
from caeModules import *
from column4p import Column
from partitionColumn4p import PartitionColumn
#from steelMaterial import SteelMaterial
from meshColumn4p import MeshColumn

column = Column(shearkey_nums=5, part_name='column')

#Material(column, ((450, 0), (550, 0.05)))
PartitionColumn(column, 15)
MeshColumn(15, column, 2, 0, 2, 2, 4, 2, 2, False, False, True, True, True)