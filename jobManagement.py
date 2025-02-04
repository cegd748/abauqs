from abaqus import *
from abaqusConstants import *
from caeModules import *
import myAssembly3p
import myAssembly4p

def resetModel():
    mdb.close()

def submitJob(job_name):
    mdb.jobs[job_name].submit(consistencyChecking=OFF)

def wait_job(job_name):
    mdb.jobs[job_name].waitForCompletion()

class CreateJobINP:
    def __init__(self, myAssembly, job_name, cpu_nums, gpu_nums, note='', queue=None, memory_percent=90):
        self.job_name = job_name
        self.cpu_nums = cpu_nums
        self.gpu_nums = gpu_nums
        self.note = note
        self.queue = queue
        self.memory_percent = memory_percent
        self.__createINP(myAssembly)

    def __createINP(self, myAssembly):
        mdb.Job(name=self.job_name, model=myAssembly.model_name, description=self.note, type=ANALYSIS,
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=self.memory_percent,
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1,
                multiprocessingMode=DEFAULT, numCpus=self.cpu_nums, numDomains=self.cpu_nums, numGPUs=self.gpu_nums)
        mdb.jobs[self.job_name].writeInput(consistencyChecking=OFF)