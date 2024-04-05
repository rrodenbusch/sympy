"""sympy.physics.quantum subclass of sympy.core.Pow"""

import sympy
from sympy import sympify
from sympy.core.singleton import S
from sympy.utilities.exceptions import sympy_deprecation_warning

class Pow( sympy.core.power.Pow ):
    _op_priority = 110
    def __new__(cls, *args, **kwargs):
        if len(args) > 1 and sympify(args[1]) is S.Zero:
            (b,e,obj) = (args[0],S.Zero,None)
            if isinstance(b, sympy.physics.quantum.qexpr.QExpr) and hasattr(b, '_identity'):
                return b._identity()
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
