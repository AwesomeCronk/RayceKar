import struct

from raycekar.coord import *
from raycekar.gl import contacts


### Base object classes ###
class object():
    def __init__(self, pos: vec3, rot: quat):
        self.pos = pos
        self.rot = rot

    def move(self, pos: vec3, relative=False):
        if relative: self.pos += self.rot * pos
        else: self.pos = pos

    def rotate(self, rot: quat, relative=False):
        self.rot = rot

    def compileBufferData(self):
        intData = b''
        floatData = b''
        return intData, floatData

class camera(object):
    def __init__(self, pos: vec3, rot: quat, fov: float):
        self.pos = pos
        self.rot = rot
        self.fov = fov

    def setFov(self, newFov: float):
        self.fov = newFov

    def compileBufferData(self):
        intData = b''
        floatData = struct.pack(
            'ffffffff',
            *self.pos, rad(self.fov),
            *self.rot
        )
        return intData, floatData
 
class shape(object): pass

class light(object): pass


class scene():
    def __init__(self):
        self.cameras = []
        self.shapes = []
        self.lights = []

    def addCamera(self, newCamera: camera):
        assert isinstance(newCamera, camera)
        id = len(self.cameras)
        self.cameras.append(newCamera)
        return id

    def addShape(self, newShape: shape):
        assert isinstance(newShape, shape)
        id = len(self.shapes)
        self.shapes.append(newShape)
        return id

    def addLight(self, newLight: light):
        pass

    def removeObject(self, id: int):
        del self.objects[id]

    def compileBufferData(self):
        shapeTypeData = b''
        shapeIntData = b''
        shapeFloatData = b''

        # Put the camera at the beginning of the shape buffers
        # This is temporary until camera support takes off
        shapeTypeData += struct.pack('i', objectTypes.index(camera))
        objectIntData, objectFloatData = self.cameras[0].compileBufferData()
        shapeIntData += objectIntData
        shapeFloatData += objectFloatData

        for shape in self.shapes:
            shapeTypeData += struct.pack('i', objectTypes.index(type(shape)))
            objectIntData, objectFloatData = shape.compileBufferData()
            shapeIntData += objectIntData
            shapeFloatData += objectFloatData

        lightTypeData = b''
        lightFloatData = b''

        for light in self.lights:
            typeData += struct.pack('i', objectTypes.index(type(light)))
            objectFloatData = light.compileBufferData()
            lightFloatData += objectFloatData

        return (shapeTypeData, shapeIntData, shapeFloatData), (lightTypeData, lightFloatData)


### Shapes ###
class sphere(shape):
    def __init__(self, pos: vec3, radius: float):
        self.pos = pos
        self.radius = radius

    def resize(self, rad: float):
        self.rad = rad

    def compileBufferData(self):
        intData = b''
        floatData = struct.pack(
            'ffff',
            *self.pos,
            self.radius
        )
        return intData, floatData

class box(shape):
    def __init__(self, pos: vec3, rot: quat, dim: vec3):
        self.pos = pos
        self.rot = rot
        self.dim = dim

    def resize(self, newDim: vec3):
        self.dim = newDim

    def compileBufferData(self):
        intData = b''
        floatData = struct.pack(
            'ffffffffffff',
            *self.pos, 0.0,
            *self.rot,
            *self.dim, 0.0
        )
        return intData, floatData


### Lights ###
class pointLight(light):
    def __init__(self, pos: vec3, radius: float, intensity: float, falloff: float, color):
        self.pos = pos
        self.radius = radius
        self.intensity = intensity
        self.falloff = falloff
        self.color = color

    def compileBufferData(self):
        intData = b''
        floatData = struct.pack(
            'f' * 9,
            *self.pos,
            self.radius,
            self.intensity,
            self.falloff,
            self.color
        )
        return intData, floatData


# `objectTypes` is used to calculate the shape ID to match to renderScene.glsl
objectTypes = [
    camera,
    sphere,
    box,
    pointLight
]


def getContact(pos: vec2):
    from raycekar.gl import viewportSize
    return contacts.scene[pos.x + (viewportSize.x * pos.y)]
