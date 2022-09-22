from math import sqrt, sin, cos, acos, pi


### Angles ###
class deg:
    def __init__(self, value):
        if isinstance(value, rad): self.value = value.value * 180 / pi
        elif isinstance(value, deg): self.value = value.value
        else: self.value = value

    def __str__(self):
        return '{} deg'.format(self.value)

    __repr__ = __str__

    def __add__(self, other):
        return deg(self.value + deg(other).value)

    def __sub__(self, other):
        return deg(self.value - deg(other).value)

    def __mul__(self, other):
        if isinstance(other, deg): raise NotImplementedError()
        elif isinstance(other, rad): raise NotImplementedError()
        else:
            return deg(self.value * other)

    def __truediv__(self, other):
        if isinstance(other, deg): return self.value / other.value
        elif isinstance(other, rad): return self.value / deg(other).value
        else: return deg(self.value / other)

    def __floordiv__(self, other):
        if isinstance(other, deg): return self.value // other.value
        elif isinstance(other, rad): return self.value // deg(other).value
        else: return deg(self.value // other)

    def __mod__(self, other):
        if isinstance(other, deg): return deg(self.value % other.value)
        elif isinstance(other, rad): return deg(self.value % deg(other).value)
        else: return deg(self.value % other)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

class rad:
    def __init__(self, value):
        if isinstance(value, deg): self.value = value.value * pi / 180
        elif isinstance(value, rad): self.value = value.value
        else: self.value = value

    def __str__(self):
        return '{} rad'.format(self.value)

    __repr__ = __str__

    def __add__(self, other):
        return rad(self.value + rad(other).value)

    def __sub__(self, other):
        return rad(self.value - rad(other).value)

    def __mul__(self, other):
        if isinstance(other, deg): raise NotImplementedError()
        elif isinstance(other, rad): raise NotImplementedError()
        else:
            return rad(self.value * other)

    def __truediv__(self, other):
        if isinstance(other, deg): return self.value / rad(other).value
        elif isinstance(other, rad): return self.value / other.value
        else: return rad(self.value / other)

    def __floordiv__(self, other):
        if isinstance(other, deg): return self.value // rad(other).value
        elif isinstance(other, rad): return self.value // other.value
        else: return rad(self.value // other)

    def __mod__(self, other):
        if isinstance(other, deg): return rad(self.value % rad(other).value)
        elif isinstance(other, rad): return rad(self.value % other.value)
        else: return rad(self.value % other)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)


### Vectors ###
class _vec():
    def __init__(self, *values):
        if getattr(self, '_size', None) is None: raise Exception('should not instantiate _vec, but should use vec2, vec3, or vec4')
        if len(values) != self._size: raise ValueError('need {} values, {} given'.format(self._size, len(values)))
        else: self.values = values
        
        self.x = self.values[0]
        self.y = self.values[1]
        if self._size >= 3: self.z = self.values[2]
        if self._size >= 4: self.w = self.values[3]

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
class quat():
    def __init__(self, n, ni, nj, nk):
        self.n = n
        self.ni = ni
        self.nj = nj
        self.nk = nk
        self.components = [n, ni, nj, nk]

    def __repr__(self):
        return '({} {} {}i {} {}j {} {}k'.format(
            self.n,
            '+' if self.ni >= 0 else '-', self.ni,
            '+' if self.nj >= 0 else '-', self.nj,
            '+' if self.nk >= 0 else '-', self.nk
        )

    __str__ = __repr__

    def __getitem__(self, index):
        return self.components[index]

    def fromAxisAngle(axisAngle: vec4):
        return quat(
            cos(rad(axisAngle.w) / 2),
            axisAngle.x * sin(rad(axisAngle.w) / 2),
            axisAngle.y * sin(rad(axisAngle.w) / 2),
            axisAngle.z * sin(rad(axisAngle.w) / 2)
        )

    def toAxisAngle(self):
        return vec4(self.ni, self.nj, self.nk, acos(self.n) * 2)


    # Multiplication of quaternions and vectors
    def _mulQuat(self, other):
        q0 = self; q1 = other
        return quat(
            q0.n  * q1.n  - q0.ni * q1.ni - q0.nj * q1.nj - q0.nk * q1.nk,
            q0.n  * q1.ni + q0.ni * q1.n  + q0.nj * q1.nk - q0.nk * q1.nj,
            q0.n  * q1.nj + q0.nj * q1.n  + q0.nk * q1.ni - q0.ni * q1.nk,
            q0.n  * q1.nk + q0.nk * q1.n  + q0.ni * q1.nj - q0.nj * q1.ni
        )

    def _mulVec(self, other: vec3):
        vecQuat = quat(0, *other)
        resultQuat = (self * vecQuat) * self.conjugate()
        return vec3(resultQuat.ni, resultQuat.nj, resultQuat.nk)

    def __mul__(self, other):
        if isinstance(other, quat): return self._mulQuat(other)
        elif isinstance(other, vec3): return self._mulVec(other)


    # Functions relating to quaternion manipulation
    def length(self):
        return sum([comp * comp for comp in (self.n, self.ni, self.nj, self.nk)])

    def normalize(self):
        mag = length(self)
        return quat(self.n / mag, self.ni / mag, self.nj / mag, self.nk / mag)

    def conjugate(self):
        return quat(self.n, -self.ni, -self.nj, -self.nk)


### Operators ###
# These have their own section because they may or may not operate on both vectors and quaternions
def length(thing): return thing.length()

def normalize(thing): return thing.normalize()
