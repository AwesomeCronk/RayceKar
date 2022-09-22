import struct

from raycekar.coord import *


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


# Empty base class to make it easy to ensure only objects are in the scene
class object():
    pass

class camera(object):
    def __init__(self, pos: vec3, rot: quat, fov: float):
        self.pos = pos
        self.rot = rot
        self.fov = fov

    def move(self, newPos: vec3):
        self.pos = newPos

    def rotate(self, newRot: quat):
        self.rot = newRot

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
        
    def move(self, newPos: vec3):
        self.pos = newPos

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

    def move(self, newPos: vec3):
        self.pos = newPos

    def rotate(self, newRot):
        self.rot = newRot

    def resize(self, newDim):
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
