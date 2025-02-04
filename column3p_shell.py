from abaqus import *
from abaqusConstants import *
from caeModules import *
from tube_shell import Tube

class Column(Tube):
    def __init__(self, shearkey_nums, shearkey_h=4.0, shearkey_w=8.0, shearkey_s=40, shearkey_p=20,
                 pad_thickness=20, pad_pos=50, pad_hole_radius=30, pad_hole_pos=[0.42, 0.42],
                 model_name='Model-1', part_name='column-shell',
                 height1=150, width1=150, height2=50, width2=50, radius1=25, thickness=8, length=800,
                 tube_name='Set-tube', pad_name='Set-pad', shearkey_name='Set-shearkey'):
        super().__init__(model_name, part_name, height1, width1, height2, width2, radius1, thickness, length)
        self.shearkey_nums = shearkey_nums
        self.shearkey_h = shearkey_h
        self.shearkey_w = shearkey_w
        self.shearkey_s = shearkey_s
        self.shearkey_p = shearkey_p
        self.pad_thickness = pad_thickness
        self.pad_pos = pad_pos
        self.pad_hole_radius = pad_hole_radius
        self.pad_hole_pos = pad_hole_pos
        self.__generatePad()
        self.__generateShearkey()
        self.sets = _ColumnSet(model_name, part_name, tube_name, pad_name, shearkey_name, shearkey_nums)

    def __generatePad(self):
        plane_z = self.length - self.pad_pos + 0.5 * self.pad_thickness
        p = mdb.models[self.model_name].parts[self.part_name]
        p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE,offset=plane_z)
        f, e1, d1 = p.faces, p.edges, p.datums
        t = p.MakeSketchTransform(sketchPlane=d1[2], sketchUpEdge=e1[19],
                                  sketchPlaneSide=SIDE1, sketchOrientation=RIGHT,
                                  origin=(0.0, 0.0, plane_z))
        s1 = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__',sheetSize=2000, gridSpacing=50, transform=t)
        p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
        s1 = _Sketch3(self.model_name, '__profile__', self.height1, self.width1, self.height2,
                      self.width2, self.radius1, self.thickness, 0.5, self.pad_hole_radius, self.pad_hole_pos)
        f1, e, d2 = p.faces, p.edges, p.datums
        p.Shell(sketchPlane=d2[2], sketchUpEdge=e[10], sketchPlaneSide=SIDE1,
                sketchOrientation=RIGHT, sketch=s1)

        del mdb.models[self.model_name].sketches['__profile__']

    def __generateShearkey(self):
        p = mdb.models[self.model_name].parts[self.part_name]
        p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0.0)
        delta = 0.1
        e, d = p.edges, p.datum
        edge1 = e.findAt(coordinates=(self.width1 - 0.5*self.thickness, column.radius1 + delta, 0))
        t = p.MakeSketchTransform(sketchPlane=d[4], sketchUpEdge=edge1,
                                  sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
        sweep_path = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__',
                                                     sheetSize=1600, gridSpacing=40, transform=t)
        _Sketch3(self.model_name, '__sweep__', self.height1, self.width1, self.height2,
                   self.width2, self.radius1, self.thickness, 1)

        p = mdb.models[self.model_name].parts[self.part_name]
        s1 = mdb.models[self.model_name].ConstrainedSketch(
            name='__profile__',sheetSize=2000, gridSpacing=50,
            transform=(-1.0, 0.0, 0.0, 0.0, 0.0, 1.0, -0.0, 1.0, -0.0,
                       self.width1 - self.width2 - self.thickness, self.height1 - self.thickness, 0.0))
        for i in range(self.shearkey_nums):
            pos = i * self.shearkey_s + self.shearkey_p
            s1.Arc3Points(point1=(0.0, pos - 0.5 * self.shearkey_w),
                         point2=(0.0, pos + 0.5 * self.shearkey_w),
                         point3=(self.shearkey_h, pos))
            s1.Line(point1=(0.0, pos - 0.5 * self.shearkey_w),
                   point2=(0.0, pos + 0.5 * self.shearkey_w))

        e, d = p.edges, p.datums
        edge2 = e.findAt(coordinates=(self.radius1, self.height1 - self.thickness * 0.5, delta))
        p.SolidSweep(pathPlane=d[4], pathUpEdge=edge1, sketchUpEdge=edge2,
                     pathOrientation=RIGHT, path=sweep_path, sketchOrientation=RIGHT, profile=s1,
                     keepInternalBoundaries=ON)
        del mdb.models[self.model_name].sketches['__profile__']
        del mdb.models[self.model_name].sketches['__sweep__']

class _ColumnSet:
    def __init__(self, model_name, part_name, tube_name,
                 pad_name, shearkey_name, shearkey_nums):
        self.tube = tube_name
        self.pad = pad_name
        self.shearkey = shearkey_name
        self.__createSet(model_name, part_name, shearkey_nums)

    def __createSet(self, model_name, part_name, shearkey_nums):
        p = mdb.models[model_name].parts[part_name]

        f = p.faces
        #factor !=  0.5 in __generatePad, faces = f.getSequenceFromMask(mask=('[#7fe ]',), )
        faces = f.getSequenceFromMask(mask=('[#1ffffe ]',), )
        p.Set(faces=faces, name=self.tube)


        faces = f.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(faces=faces, name=self.pad)

        bi_string = ''
        for i in range(shearkey_nums):
            bi_string = '1' + bi_string
        hex_string = hex(int(bi_string, 2))[2:]
        shearkeys_mask = '[#' + hex_string + ' ]'
        c = p.cells
        cells = c.getSequenceFromMask(mask=(shearkeys_mask,), )
        p.Set(cells=cells, name=self.shearkey)

def _Sketch3(model_name, sketch_name, height1, width1, height2, width2, radius1, thickness, factor, pad_hole_radius=0, pad_hole_pos=[]):
    sketch = mdb.models[model_name].sketches[sketch_name]
    g, v, d, c = sketch.geometry, sketch.vertices, sketch.dimensions, sketch.constraints
    vertices = ((0, 0), (0, height1), (width1 - width2, height1), (width1 - width2, height1 - height2),
                (width1, height1 - height2), (width1, 0), (0, 0))
    for i in range(len(vertices) - 1):
        sketch.Line(point1=vertices[i], point2=vertices[i + 1])

    sketch.FilletByRadius(radius=radius1, curve1=g[2], nearPoint1=(0, radius1), curve2=g[7],
                          nearPoint2=(radius1, 0))
    sketch.FilletByRadius(radius=radius1, curve1=g[2], nearPoint1=(0, height1 - radius1), curve2=g[3],
                          nearPoint2=(radius1, height1))
    sketch.FilletByRadius(radius=radius1, curve1=g[6], nearPoint1=(width1, radius1), curve2=g[7],
                          nearPoint2=(width1 - radius1, 0))
    sketch.FilletByRadius(radius=radius1 - thickness, curve1=g[4],
                          nearPoint1=(width1 - width2, height1 - height2 + radius1 - thickness),
                          curve2=g[5], nearPoint2=(width1 - width2 + radius1 - thickness, height1 - height2))
    sketch.offset(distance=thickness * factor, objectList=(g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9], g[10], g[11]),
                  side=LEFT)
    sketch.delete(objectList=(g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9], g[10], g[11]))
    if pad_hole_radius:
        sketch.CircleByCenterPerimeter(center=(width1 * pad_hole_pos[0], height1* pad_hole_pos[1]),
                                       point1=(width1 * pad_hole_pos[0], height1* pad_hole_pos[1] - pad_hole_radius))
    return sketch

column = Column(3, 3.78, 8.91)