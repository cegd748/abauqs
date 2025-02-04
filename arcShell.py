from abaqus import *
from abaqusConstants import *
from caeModules import *

class _AceShellSet:
    def __init__(self, model_name, part_name, load_point_name, geometry_set_name, load_face_name):
        self.load_point_name = load_point_name
        self.load_face_name = load_face_name
        self.geometry_set_name = geometry_set_name
        self.__generateFace(model_name, part_name)
        self.__generateSet(model_name, part_name)

    def __generateFace(self, model_name, part_name):
        p = mdb.models[model_name].parts[part_name]
        s = p.faces
        side2Faces = s.getSequenceFromMask(mask=('[#1 ]',), )
        p.Surface(side2Faces=side2Faces, name=self.load_face_name)

    def __generateSet(self, model_name, part_name):
        p = mdb.models[model_name].parts[part_name]
        r = p.referencePoints
        refPoints = (r[2],)
        p.Set(referencePoints=refPoints, name=self.load_point_name)
        f = p.faces
        faces = f.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(faces=faces, name=self.geometry_set_name)

class ArcShell:
    def __init__(self, model_name='Model-1', part_name='arc-shell', radius=40, length=210,
                 load_point_name='load-point', geometry_set_name='shell', load_face_name='load-face'):
        self.model_name = model_name
        self.part_name = part_name
        self.radius = radius
        self.length = length
        self.__generateArcShell()
        self.__generateReferencePoint()
        self.sets = _AceShellSet(model_name, part_name, load_point_name, geometry_set_name, load_face_name)

    def __generateArcShell(self):
        s1 = mdb.models[self.model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
        s1.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
        s1.Line(point1=(self.radius, 0.0), point2=(self.radius, self.length))
        p = mdb.models[self.model_name].Part(name=self.part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        p = mdb.models[self.model_name].parts[self.part_name]
        p.BaseShellRevolve(sketch=s1, angle=90.0, flipRevolveDirection=ON)
        del mdb.models[self.model_name].sketches['__profile__']

    def __generateReferencePoint(self):
        p = mdb.models[self.model_name].parts[self.part_name]
        p.ReferencePoint(point=(0.0, 0.5 * self.length, 0.0))