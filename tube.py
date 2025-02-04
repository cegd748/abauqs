from abaqus import *
from abaqusConstants import *
from caeModules import *

def _Sketch(model_name, sketch_name, height1, width1, height2, width2, radius1, thickness):
    sketch = mdb.models[model_name].ConstrainedSketch(name=sketch_name, sheetSize=200.0)
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
    sketch.offset(distance=thickness, objectList=(g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9], g[10], g[11]),
                  side=LEFT)
    return sketch

class Tube:
    def __init__(self, model_name, part_name, height1, width1, height2, width2, radius1, thickness, length):
        self.__model_name = model_name
        self.__part_name = part_name
        self.__height1 = height1
        self.__height2 = height2
        self.__width1 = width1
        self.__width2 = width2
        self.__radius1 = radius1
        self.__thickness = thickness
        self.__length = length
        self.__check_legality()
        self.__tube = self.__GenerateTube()

    def __check_legality(self):
        check = not self.model_name or not self.part_name
        if check: raise ValueError('name empty')

        check = (self.width1 <= 0 or self.width2 <= 0 or self.height1 <= 0 or self.height2 <= 0 or
                          self.thickness <= 0 or self.radius1 <= 0 or self.length <= 0)
        if check: raise ValueError('non positive value')

        check = (self.width1 - self.width2 - 2 * self.thickness <= 0 or
                                         self.height1 - self.height2 - 2 * self.thickness <= 0)
        if check: raise ValueError('tube concave corners too large')

    @property
    def model_name(self):
        return self.__model_name
    @property
    def part_name(self):
        return self.__part_name
    @property
    def height1(self):
        return self.__height1
    @property
    def height2(self):
        return self.__height2
    @property
    def width1(self):
        return self.__width1
    @property
    def width2(self):
        return self.__width2
    @property
    def radius1(self):
        return self.__radius1
    @property
    def thickness(self):
        return self.__thickness
    @property
    def length(self):
        return self.__length
    @property
    def tube(self):
        return self.__tube

    def __GenerateTube(self):
        sketch = _Sketch(self.__model_name, 'sketch1', self.__height1, self.__width1,
                         self.__height2, self.__width2, self.__radius1, self.__thickness)
        tube = mdb.models[self.__model_name].Part(name=self.__part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        tube.BaseSolidExtrude(sketch=sketch, depth=self.__length)
        del mdb.models[self.__model_name].sketches['sketch1']
        return tube

    def new_height1(self, value):
        self.__alt_parameter('height1', value)
        return self.__tube
    def new_height2(self, value):
        self.__alt_parameter('height2', value)
        return self.__tube
    def new_width1(self, value):
        self.__alt_parameter('width1', value)
        return self.__tube
    def new_width2(self, value):
        self.__alt_parameter('width2', value)
        return self.__tube
    def new_radius1(self, value):
        self.__alt_parameter('radius1', value)
        return self.__tube
    def new_thickness(self, value):
        self.__alt_parameter('thickness', value)
        return self.__tube
    def new_length(self, value):
        self.__alt_parameter('depth1', value)
        return self.__tube

    def __alt_parameter(self, name, value):
        if name == 'height1': self.__height1 = value
        elif name == 'height2': self.__height2 = value
        elif name == 'width1': self.__width1 = value
        elif name == 'width2': self.__width2 = value
        elif name == 'radius1': self.__radius1 = value
        elif name == 'thickness': self.__thickness = value
        elif name == 'depth1': self.__length = value
        else: return

        if name == 'depth1':
            self.__tube.features['Solid extrude-1'].setValues(depth=self.__length)
        else:
            sketch = _Sketch(self.__model_name, 'sketch1', self.__height1, self.__width1,
                             self.__height2, self.__width2, self.__radius1, self.__thickness)
            self.__tube.features['Solid extrude-1'].setValues(sketch=sketch)
            del mdb.models[self.__model_name].sketches['sketch1']
        self.__tube.regenerate()