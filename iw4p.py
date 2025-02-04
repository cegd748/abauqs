from abaqus import *
from abaqusConstants import *
from caeModules import *

from column4p import Column
from partitionColumn4p import PartitionColumn
from meshColumn4p import MeshColumn

from itube import Itube
from partitionItube import PartitionItube
from meshItube import MeshItube

from concrete import Concrete
from partitionConcrete import PartitionConcrete
from meshConcrete import MeshConcrete

from arcShell import ArcShell
from meshArcshell import MeshArcshell

from steelMaterial import SteelMaterial
from concreteMaterial import ConcreteMaterial

from myAssembly4p import MyAssembly
from myStep import MyStep
from myStep import StepType
from myInteraction4p import MyInteraction
from myBoundary4p import MyBoundary

from jobManagement import *
import time

shearkey_nums = [2, 3, 5]
itube_shearkey_w = [9.48, 9.46, 10.33]
itube_shearkey_h = [4.50, 4.33, 4.61]
column_shearkey_w = [9.38, 8.91, 9.09]
column_shearkey_h = [3.99, 3.78, 4.04]
concrete_length = [118, 152, 229]

for i, num in enumerate(shearkey_nums):
    if i in {2, 5}:
        continue
    itube_length = num * 40 + 30
    itube = Itube(length=itube_length, shearkey_nums=num, shearkey_w=itube_shearkey_w[i], shearkey_h=itube_shearkey_h[i])
    column = Column(shearkey_nums=num, shearkey_w=column_shearkey_w[i], shearkey_h=column_shearkey_h[i])
    concrete = Concrete(itube, column, length=concrete_length[i])
    loadShell = ArcShell()
    assembly1 = MyAssembly(itube, column, concrete, loadShell)
    step1 = MyStep(assembly1, step_type=StepType.STATIC_STEP, maxInc=0.002, initInc=0.001)
    interaction1 = MyInteraction(assembly1)
    MyBoundary(assembly1, step1, displacement= -40)

    SteelMaterial(column)
    myPartitionColumn = PartitionColumn(column, 14, 100)
    MeshColumn(column, myPartitionColumn, 2, 6, 2,
               2, 4, 2, 2, 25, 15, True)

    SteelMaterial(itube)
    myPartitionItube= PartitionItube(itube)
    MeshItube( itube, myPartitionItube, 12, 2, 6, 2, 4,
               2, True, True)

    ConcreteMaterial(concrete)
    myPartitionConcrete = PartitionConcrete(itube, column, concrete, more_partition=False)
    MeshConcrete(itube, column, concrete, myPartitionConcrete, global_size=6, innner_size=12, radius1_outside_elements=2,
                 radius1_inside_elements=1, radius2_elements=2, shearkey_elements=6)

    SteelMaterial(loadShell)
    MeshArcshell(loadShell)

    """job_name = f"{num}w4p"
    CreateJobINP(assembly1, job_name=job_name, cpu_nums=12, gpu_nums=1)
    start_time = time.time()
    submitJob(job_name)
    print(f"start compute {num}w4p")
    wait_job(job_name)
    end_time = time.time()
    used_time = end_time - start_time
    print(f"{job_name} completed, used time: {used_time // 3600} : {(used_time % 3600) // 60} : {used_time % 60}")
    resetModel()"""