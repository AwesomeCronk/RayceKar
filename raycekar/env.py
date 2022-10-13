import struct

from raycekar.coord import *
from raycekar.gl import contacts


class scene():
    def __init__(self):
        self.objects = []

    def addObject(self, newObject: object):
        assert isinstance(newObject, object)
        id = len(self.objects)
        self.objects.append(newObject)
        return id

    def removeObject(self, id: int):
        del self.objects[id]

    def compileBufferData(self):
        typeData = b''
        intData = b''
        floatData = b''

        for object in self.objects:
            typeData += struct.pack('i', objectTypes.index(type(object)))
            objectIntData, objectFloatData = object.compileBufferData()
            intData += objectIntData
            floatData += objectFloatData

        return typeData, intData, floatData


class object():
    def __init__(self, pos: vec3, rot: quat):
        self.pos = pos
        self.rot = rot

    def move(self, pos: vec3, relative=False):
        if relative: self.pos += self.rot * pos
        else: self.pos = pos

    def rotate(self, rot: quat, relative=False):
        self.rot = rot

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

class sphere(object):
    def __init__(self, pos: vec3, rad: float):
        self.pos = pos
        self.rad = rad

    def resize(self, rad: float):
        self.rad = rad

    def compileBufferData(self):
        intData = b''
        floatData = struct.pack(
            'ffff',
            *self.pos,
            self.rad
        )
        return intData, floatData

class box(object):
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


objectTypes = [
    camera,
    sphere,
    box
]


def getContact(pos: vec2):
    from raycekar.gl import viewportSize
    return contacts.scene[pos.x + (viewportSize.x * pos.y)]
