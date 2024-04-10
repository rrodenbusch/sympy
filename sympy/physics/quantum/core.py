""" Base class for extension of core Add, Mul and Pow classes"""
import sympy
from sympy import sympify
from sympy.core.singleton import S
from sympy.utilities.exceptions import sympy_deprecation_warning
from sympy.core.decorators import call_highest_priority

from sympy.physics.quantum.collect import collect
import sympy.core.add
import sympy.core.mul
import sympy.core.power

class qCore():
    @property
    def _op_priority(self):
        return 100

    def __radd__(self, other, *args, **kwargs):
        return Add(other, self, *args, **kwargs)

    def __add__(self, *args, **kwargs):
        return Add(self, *args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return Mul(self, *args, **kwargs)

    def __rmul__(self, other, *args, **kwargs):
        return Mul(other, self, *args, **kwargs)

    def __pow__(self,*args, **kwargs):
        return Pow(self, *args, **kwargs)

    @call_highest_priority('collect')
    def collect(self, syms, *args, **kwargs):
        return collect(self, syms, *args, **kwargs)


class Add(qCore, sympy.core.add.Add):
    @property
    def _op_priority(self):
        return 105

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__(self,other):
        if not isinstance(other, Add) and isinstance(other, sympy.core.add.Add):
            other = Add(*other.args)
        return super().__eq__(other)

    __hash__ = sympy.core.add.Add.__hash__


class Mul(qCore, sympy.core.mul.Mul):
    @property
    def _op_priority(self):
        return 110

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__(self,other):
        if not isinstance(other, Mul) and isinstance(other, sympy.core.mul.Mul):
            other = Mul(*other.args)
        return super().__eq__(other)

    __hash__ = sympy.core.mul.Mul.__hash__


class Pow(qCore, sympy.core.power.Pow):
    @property
    def _op_priority(self):
        return 115

    def __new__(cls, *args, **kwargs):
        if len(args) > 1 and sympify(args[1]) is S.Zero:
            (b,e,obj) = (args[0],S.Zero,None)
            if hasattr(b, 'mul_identity'):
                return b.mul_identity
            elif isinstance(b, (Pow, Mul, Add) ):
                idents = {}
                for arg in b.args:
                    ident = Pow(arg,S.Zero)
                    if ident is not S.One:
                        idents[type(ident)] = ident
                if len(idents) == 1:
                    return list(idents.values())[0]
                elif len(idents):
                    sympy_deprecation_warning(f"""
    Use of multiple Identity() types in expressions is deprecated (in this case, the types
    are {idents.keys()}).""",
                        deprecated_since_version="1.12",
                        active_deprecations_target="mixed-identity-type-expr",
                        stacklevel=4,
                    )
                    return S.One
                else:
                    return S.One

            if hasattr(b, '_eval_power'):
                obj = b._eval_power(e)
            if obj is None and hasattr(b,'_pow'):
                obj = b._pow(e, **kwargs)
            if obj is not None:
                return obj

        return super().__new__(cls, *args, **kwargs)

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__(self,other):
        if not isinstance(other,Pow) and isinstance(other, sympy.core.power.Pow):
            other = Pow(*other.args)
        return super().__eq__(other)

    __hash__ = sympy.core.power.Pow.__hash__
