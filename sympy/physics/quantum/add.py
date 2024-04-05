"""sympy.physics.quantum subclass of sympy.core.Add"""

import sympy.core.add
from .power import Pow
class Add( sympy.core.Add ):

    _obj_priority = 100
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __pow__(self,*args, **kwargs):
        return Pow(self, *args, **kwargs)

    def __add__(self,other):
        lres = sympy.core.Add(self,other)
        return lres

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

    __hash__ = sympy.core.Add.__hash__
