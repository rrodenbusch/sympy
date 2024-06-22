"""Support classes for Abstract Algebras


    AbstractAlgebra: The class defining the abstract algebra.
    AbstractAlgebraOp: The subclass of Expr which implements any operations
        in the algebra which differ from the core/default algebra
    AbstractAlgebraMeta: A meta-class than any class may include which will
        automatically generate and manage the abstract algebra for the class.

    abstract_algebra_attributes: The tuple of attributes used to implement
        the abstract algebra. If a class defines any of these and uses
        metaclass=AbstractAlgebraMeta, then an algebra will be automatically
        implemented.


    Explanation
    ===========

    The default algebra of sympy, defined in sympy.core, is a field over
    Real or Complex numbers. Matrices receive special consideration in the
    default algebra as well through specific treatment in the various classes
    and functions. Other algebras, such as rings, operator algebras or the
    C*Algebra, common in quantum physics, require abstraction from this default
    algebra.  The abstract algebra classes rely on the @call_highest_priority
    decorator and associated _op_priority attribute.


    Priority of algebras
    ====================

    AbstractAlgebraMeta selects from algebras in the following order:
        1. An algebra defined by the class itself,
        2. An implicit algebra defined in the class,
        3. An algebra defined by the bases of the class.

    A class implicitly defines an algebra if it has an _op_priority
    greater than the default value, Expr._op_priority. The AbstractAlgebra
    is built from the _op_priority and any class methods listed in
    abstract_algebra_attributes.


    Supported Methods
    =================

    __add__, __radd__, __mul__, and __rmul__ handle the algebraic operations.
    __pow__ and _pow handle inverses and repeated multiplication, A*A=A**2
    collect supports methods to handle non-commutative elements in the algebra


    See Also
    ========

        Expr, Add, Mul, Pow

"""
from .expr import Expr
abstract_algebra_attributes = ('_op_priority',
                               '__add__', '__radd__',
                               '__pow__', '_pow',
                               '__mul__', '__rmul__',
                               '__truediv__', '__rtruediv__',
                               'collect', 'simplify',
                               )


class AbstractAlgebra():
    """
    The class holding operations which differ from the numeric field algebra
    defined by the core sympy.

    Explanation
    ===========

    The default algebra of sympy, defined in sympy.core, is a field over
    Real or Complex numbers. Matrices receive special consideration in the
    default algebra as well through specific treatment in the various classes
    and functions. Other algebras, such as rings, operator algebras or the
    C*Algebra, common in quantum physics, require abstraction from this default
    algebra.  The abstract algebra classes rely on the @call_highest_priority
    decorator and associated _op_priority attribute.

    """
    __slots__ = ('cls_name',) + abstract_algebra_attributes

    def __init__(self, _op_priority = Expr._op_priority, **kwargs):
        self._op_priority = _op_priority
        for method in abstract_algebra_attributes:
            if method in kwargs:
                setattr(self, method, kwargs[method])
        self.cls_name = kwargs.get('cls_name', 'Unknown')

    def __repr__(self):
        return f"{self.cls_name}.AbstractAlgebra"


class AbstractAlgebraOp(Expr):
    """
    Implement methods of abstract algebra in core classes Add, Mul and Pow
    """

    @property
    def _op_priority(self):
        if  type(self.algebra) is AbstractAlgebra:
            return self.algebra._op_priority
        return super()._op_priority

    def __add__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(self, other, algebra = self.algebra)
        return super().__add__(other, **kwargs)

    def __radd__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(other, self, algebra = self.algebra)
        return super().__radd__(other, **kwargs)

    def __sub__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(self, -other, algebra = self.algebra)
        return super().__sub__(other, **kwargs)

    def __rsub__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(other, -self, algebra = self.algebra)
        return super().__rsub__(other, **kwargs)

    def __mul__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__mul__', None)
            if _handler is not None:
                return _handler(self, other, algebra = self.algebra)
        return super().__mul__(other, **kwargs)

    def __rmul__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__mul__', None)
            if _handler is not None:
                return _handler(other, self, algebra = self.algebra)
        return super().__rmul__(other, **kwargs)

    def __truediv__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__truediv__', None)
            if _handler is not None:
                return _handler(self, other, algebra = self.algebra)
        return super().__truediv__(other, **kwargs)

    def __rtruediv__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__rtruediv__', None)
            if _handler is not None:
                return _handler(self, other, algebra = self.algebra)
        return super().__rtruediv__(other, **kwargs)

    def __pow__(self, other, mod = None):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__pow__', None)
            if _handler is not None:
                return _handler(self, other, algebra = self.algebra)
        return super().__pow__(other, mod = mod)

    def _pow(self, other, **kwargs):
        # Return NotImplemented to return control to Pow.
        if self.algebra is not None:
            _handler = getattr(self.algebra, '_pow', None)
            if _handler is not None:
                return _handler(self, other, algebra = self.algebra)
        return super()._pow(other, **kwargs)

    def collect(self, syms, *args, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, 'collect', None)
            if _handler is not None:
                return _handler(self, syms, *args, **kwargs)
            kwargs['algebra'] = self.algebra
            expr = super().collect(syms, *args, **kwargs)
            expr.algebra = self.algebra
            return expr

        return super().collect(syms, *args, **kwargs)

    def simplify(self, *args, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, 'simplify', None)
            if _handler is not None:
                return _handler(self, *args, **kwargs)
            kwargs['algebra'] = self.algebra
            expr = super().simplify(*args, **kwargs)
            expr.algebra = self.algebra
            return expr

        return super().simplify(*args, **kwargs)

    def expand(self, *args, **kwargs):
        if self.algebra is not None:
            # Preserve the algebra in the result
            kwargs['algebra'] = self.algebra
            expr = super().expand(*args, **kwargs)
            expr.algebra = self.algebra
            return expr

        return super().expand(*args, **kwargs)

    def subs(self, *args, **kwargs):
        if self.algebra is not None:
            # Preserve the algebra in the result
            kwargs['algebra'] = self.algebra
            expr = super().subs(*args, **kwargs)
            expr.algebra = self.algebra
            return expr

        return super().subs(*args, **kwargs)


class AbstractAlgebraMeta(type):
    """
    Metaclass to generate an AbstractAlgebra for a class


    Priority of algebras
    ====================

    AbstractAlgebraMeta selects from algebras in the following order:
        1. An algebra defined by the class itself,
        2. An implicit algebra defined in the class,
        3. An algebra defined by the bases of the class.

    A class implicitly defines an algebra if it has an _op_priority
    greater than the default, Expr._op_priority. The algebra consists
    of the defined _op_priority and any of class methods from the
    abstract_algebra_attributes list.


    See Also
    ========

        sympy.core.basic.Expr
        sympy.core.add.Add
        sympy.core.mul.Mul
        sympy.core.power.Pow
    """

    def __new__(cls, name, bases, dct):
        # If an algebra is defined in the class, use it
        if 'algebra' in dct:
            dct['_op_priority'] = dct['algebra']._op_priority
            return super().__new__(cls, name, bases, dct)

        # If class priority is greater than the default, build the algebra
        if '_op_priority' in dct and dct['_op_priority'] > Expr._op_priority:
            dct['algebra'] = AbstractAlgebra(**dct, cls_name = name)
            return super().__new__(cls, name, bases, dct)

        return super().__new__(cls, name, bases, dct)
