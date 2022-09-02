import struct

from coord import *

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

        for o, object in enumerate(self.objects):
            # print('Compiling scene data for object {} ({})'.format(o, object))
            typeData += struct.pack('i', objectTypes.index(type(object)))
            objectIntData, objectFloatData = object.compileBufferData()
            intData += objectIntData
            floatData += objectFloatData

        return typeData, intData, floatData

# Empty base class to make it easy to ensure only objects are in the scene
class object():
    pass


# Note for compileBufferData definitions:
# Try to make the vectors line up on increments of 4. It's just easier later.

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
            *self.pos,
            self.fov,
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


objectTypes = [
    camera,
    sphere
]
