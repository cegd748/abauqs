from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *


def get_LoadPoint_U2_RF2(odb_name):
    odb = openOdb(path=odb_name)
    step1 = odb.steps['step-1']
    region = step1.historyRegions['Node ARC-SHELL-1.1261']
    U2Data = region.historyOutputs['U2'].data
    RF2Data = region.historyOutputs['RF2'].data
    dispFile = open('load-displacement.dat', 'w')
    for i in range(len(U2Data)):
        dispFile.write('%.2f   %.0f\n' % (-U2Data[i][1], -2 * RF2Data[i][1] / 1000))
    dispFile.close()

get_LoadPoint_U2_RF2("5w3p-HanLinHai-0-5.odb")