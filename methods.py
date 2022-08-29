from math import sqrt

class _vec():
    def __init__(self, *values):
        if getattr(self, '_size', None) is None: raise Exception('should not instantiate _vec, but should use vec2, vec3, or vec4')
        if len(values) != self._size: raise ValueError('need {} values, {} given'.format(self._size, len(values)))
        else: self.values = values

    # Bits to make Python interactions work
    def __repr__(self):
        return '<{}>'.format(', '.join([str(value) for value in self.values]))

    __str__ = __repr__  # They do the same thing so...

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return self._size

    def _ensureSameSize(self, other):
        if self._size != other._size: raise ValueError('cannot add vec{} and vec{}'.format(self._size, other._size))


    # Add and subtract other vectors
    def __add__(self, other):
        self._ensureSameSize(other)
        return vecN(*[self[i] + other[i] for i in range(self._size)])

    def __sub__(self, other):
        self._ensureSameSize(other)
        return vecN(*[self[i] - other[i] for i in range(self._size)])

    # Multiply and subtract by scalar values
    def __mult__(self, other):
        return vecN(*[self[i] * other for i in range(self._size)])

    def __truediv__(self, other):
        return vecN(*[self[i] / other for i in range(self._size)])

    def __floordiv__(self, other):
        return vecN(*[self[i] // other for i in range(self._size)])


    # Other functions relating to vector manipulation
    def __abs__(self):
        return vecN(*[abs(self[i]) for i in range(self._size)])

    # Length of a vector is just applying the pythagorean theorem
    def length(self):
        return sqrt(sum([value * value for value in self.values]))


class vec2(_vec): _size = 2
class vec3(_vec): _size = 3
class vec4(_vec): _size = 4

def vecN(*values):
    size = len(values)
    if size == 2: return vec2(*values)
    if size == 3: return vec3(*values)
    if size == 4: return vec4(*values)
    else: raise ValueError('vectors of size {} are not supported'.format(size))

def length(vector): return vector.length()

def sdfBox(rayPos: vec3, boxPos: vec3, boxDim: vec3):
    assert isinstance(rayPos, vec3)
    assert isinstance(boxPos, vec3)
    assert isinstance(boxDim, vec3)
    diff = abs(rayPos - boxPos) - (boxDim / 2)
    print(diff)
    diff = vec3(*[max(diff[i], 0) for i in range(3)])
    print(diff)
    return length(diff)
