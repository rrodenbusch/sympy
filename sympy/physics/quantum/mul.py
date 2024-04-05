"""sympy.physics.quantum subclass of sympy.core.Mul"""

import sympy.core.mul
from .power import Pow
class Mul( sympy.core.mul.Mul ):

    _op_priority = 105
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __pow__(self,*args, **kwargs):
        return Pow(self, *args, **kwargs)

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
