from abaqus import *
from abaqusConstants import *

model = mdb.models['Model-1']
part = model.parts['itube1']

datums = part.datums
for datum_id in datums.keys():
    print(datum_id)