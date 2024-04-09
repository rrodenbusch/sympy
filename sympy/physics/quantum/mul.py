"""sympy.physics.quantum subclass of sympy.core.Mul

   TODO:
        1. Create a base class for power, add and mul to
          simply the sub-classes Pow, Add and Mul
"""

import sympy.core.mul
from sympy.physics.quantum.collect import collect
import sympy.physics.quantum.add
import sympy.physics.quantum.power
from sympy.core.decorators import call_highest_priority
class Mul( sympy.core.mul.Mul ):

    @property
    def _op_priority(self):
        return 105

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __radd__(self, other, *args, **kwargs):
        return sympy.physics.quantum.add.Add(other, self, *args, **kwargs)

    def __add__(self, *args, **kwargs):
        return sympy.physics.quantum.add.Add(self, *args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return super().__new__(Mul, self, *args, **kwargs)

    def __rmul__(self, other, *args, **kwargs):
        return super().__new__(Mul, other, self, *args, **kwargs)

    def __pow__(self,*args, **kwargs):
        return sympy.physics.quantum.power.Pow(self, *args, **kwargs)

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__(self,other):
        if isinstance(other, sympy.core.mul.Mul):
            other = Mul(*other.args)
        return super().__eq__(other)

    __hash__ = sympy.core.mul.Mul.__hash__

    @call_highest_priority('collect')
    def collect(self, syms, *args, **kwargs):
        return sympy.physics.quantum.collect.collect(self, syms, *args, **kwargs)
