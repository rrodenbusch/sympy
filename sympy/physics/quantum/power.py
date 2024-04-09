"""sympy.physics.quantum subclass of sympy.core.Pow

    For powers of zero(0), check the arguments for the existence of
    mul_identity and return the mul_identity operator instead of
    S.One.

    Supports the collection of non-commutative operators via the .collect.collect
    function.

   TODO:
        1. Create a base class for power, add and mul to
          simply the sub-classes Pow, Add and Mul
"""


import sympy.core.power
import sympy.physics.quantum.add
import sympy.physics.quantum.mul
from sympy import sympify
from sympy.core.singleton import S
from sympy.utilities.exceptions import sympy_deprecation_warning
from sympy.core.decorators import call_highest_priority

class Pow( sympy.core.power.Pow ):
    _op_priority = 110
    def __new__(cls, *args, **kwargs):
        if len(args) > 1 and sympify(args[1]) is S.Zero:
            (b,e,obj) = (args[0],S.Zero,None)
            if hasattr(b, 'mul_identity'):
                return b.mul_identity
            elif isinstance(b, (Pow, sympy.physics.quantum.mul.Mul, sympy.physics.quantum.add.Add) ):
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
        if isinstance(other, sympy.core.power.Pow):
            other = Pow(*other.args)
        return super().__eq__(other)

    __hash__ = sympy.core.power.Pow.__hash__

    @call_highest_priority('collect')
    def collect(self, syms, *args, **kwargs):
        return sympy.physics.quantum.collect.collect(self, syms, *args, **kwargs)
