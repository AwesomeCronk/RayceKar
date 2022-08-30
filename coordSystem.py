from math import sqrt, sin, cos, acos, pi

def degToRad(deg): return deg * pi / 180

def radToDeg(rad): return rad * 180 / pi


### Vectors ###
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
    def __mul__(self, other):
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

    def normalize(self):
        return self / length(self)

class vec2(_vec): _size = 2
class vec3(_vec): _size = 3
class vec4(_vec): _size = 4

def vecN(*values):
    size = len(values)
    if size == 2: return vec2(*values)
    if size == 3: return vec3(*values)
    if size == 4: return vec4(*values)
    else: raise ValueError('vectors of size {} are not supported'.format(size))


### Quaternions ###
# All quaternion code adapted from https://stackoverflow.com/a/4870905/12170254
class quaternion():
    def __init__(self, n, ni, nj, nk):
        self.n = n
        self.ni = ni
        self.nj = nj
        self.nk = nk

    def __repr__(self):
        return '({} {} {}i {} {}j {} {}k'.format(
            self.n,
            '+' if self.ni >= 0 else '-', self.ni,
            '+' if self.nj >= 0 else '-', self.nj,
            '+' if self.nk >= 0 else '-', self.nk
        )

    __str__ = __repr__

    def fromAxisAngle(axis, angle):
        return quaternion(
            cos(angle / 2),
            axis[0] * sin(angle / 2),
            axis[1] * sin(angle / 2),
            axis[2] * sin(angle / 2)
        )

    def toAxisAngle(self):
        return vec3(self.ni, self.nj, self.nk), acos(self.n) * 2


    # Multiplication of quaternions and vectors
    def _mulQuat(self, quat):
        q0 = self; q1 = quat
        return quaternion(
            q0.n  * q1.n  - q0.ni * q1.ni - q0.nj * q1.nj - q0.nk * q1.nk,
            q0.n  * q1.ni + q0.ni * q1.n  + q0.nj * q1.nk - q0.nk * q1.nj,
            q0.n  * q1.nj + q0.nj * q1.n  + q0.nk * q1.ni - q0.ni * q1.nk,
            q0.n  * q1.nk + q0.nk * q1.n  + q0.ni * q1.nj - q0.nj * q1.ni
        )

    def _mulVec(self, vec):
        vecQuat = quaternion(0, *vec)
        resultQuat = (self * vecQuat) * self.conjugate()
        return vec3(resultQuat.ni, resultQuat.nj, resultQuat.nk)

    def __mul__(self, other):
        if isinstance(other, quaternion): return self._mulQuat(other)
        elif isinstance(other, vec3): return self._mulVec(other)


    # Functions relating to quaternion manipulation
    def length(self):
        return sum([comp * comp for comp in (self.n, self.ni, self.nj, self.nk)])

    def normalize(self):
        mag = length(self)
        return quaternion(self.n / mag, self.ni / mag, self.nj / mag, self.nk / mag)

    def conjugate(self):
        return quaternion(self.n, -self.ni, -self.nj, -self.nk)


### Operators ###
# These have their own section because they may or may not operate on both vectors and quaternions
def length(thing): return thing.length()

def normalize(thing): return thing.normalize()
