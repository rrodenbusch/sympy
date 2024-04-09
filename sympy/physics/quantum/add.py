"""sympy.physics.quantum subclass of sympy.core.Add

   TODO:
        1. Create a base class for power, add and mul to
          simply the sub-classes Pow, Add and Mul
"""

import sympy.core.add
from sympy.physics.quantum.collect import collect
import sympy.physics.quantum.mul
import sympy.physics.quantum.power
from sympy.core.decorators import call_highest_priority
class Add( sympy.core.add.Add ):

    @property
    def _obj_priority(self):
        return 100

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __radd__(self, other, *args, **kwargs):
        return Add(other,self, *args, **kwargs)

    def __add__(self, *args, **kwargs):
        return sympy.physics.quantum.add.Add(self, *args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return sympy.physics.quantum.mul.Mul(self, *args, **kwargs)

    def __rmul__(self, other, *args, **kwargs):
        return sympy.physics.quantum.mul.Mul(other, self, *args, **kwargs)

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
        if isinstance(other, sympy.core.add.Add):
            other = Add(*other.args)
        return super().__eq__(other)

    __hash__ = sympy.core.add.Add.__hash__

    @call_highest_priority('collect')
    def collect(self, syms, *args, **kwargs):
        return sympy.physics.quantum.collect.collect(self, syms, *args, **kwargs)
