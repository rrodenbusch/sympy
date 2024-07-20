"""Support classes for Abstract Operator Algebras


    OperatorAlgebra: The class defining the abstract algebra.
    OperatorAlgebraExpr: The subclass of Expr which implements any operations
        in the algebra which differ from the core/default algebra
    OperatorAlgebraMeta: A meta-class than any class may include which will
        automatically generate and manage the operator algebra for the class.

    operator_algebra_attributes: The tuple of attributes used to implement
        the algebra. If a inherits OperatroAlgebraMeta as a metaclass,
        then an algebra will be automatically defined.


    Explanation
    ===========

    The default algebra of sympy, defined in sympy.core, is a field over
    Real or Complex numbers. Matrices receive special consideration in the
    default algebra as well through specific treatment in the various classes
    and functions. Other algebras, such as rings, operator algebras or the
    C*Algebra, common in quantum physics, require abstraction from this default
    algebra.  The operator algebra classes rely on the @call_highest_priority
    decorator and associated _op_priority attribute.


    Priority of algebras
    ====================

    OperatorAlgebraMeta selects from algebras in the following order:
        1. An algebra defined by the class itself,
        2. An implicit algebra defined in the class,
        3. An algebra defined by the bases of the class. [TBD]

    A class implicitly defines an algebra if it has an _op_priority
    greater than the default value, Expr._op_priority. The OperatorAlgebra
    is built from the _op_priority and any class methods listed in
    operator_algebra_attributes.


    Supported Methods
    =================

    __add__, __radd__, __mul__, and __rmul__ handle the algebraic operations.
    __pow__ and _pow handle inverses and repeated multiplication, A*A=A**2
    collect supports methods to handle non-commutative elements in the algebra


    See Also
    ========

        Expr, Add, Mul, Pow


    To Do
    =====
    Implement the metaclass search the class bases for an algebra.

"""
from .expr import Expr
from .basic import Basic

operator_algebra_attributes = ('_op_priority',
                               '__add__', '__radd__',
                               '__pow__', '_pow',
                               '__mul__', '__rmul__',
                               '__truediv__', '__rtruediv__',
                               'collect', 'simplify',
                               )

default_algebra = {'_op_priority' : Expr._op_priority,
                   '__add__' : Expr.__add__,
                   '__radd__' : Expr.__radd__,
                   '__pow__' : Expr.__pow__,
                   '_pow' : Expr._pow,
                   '__mul__' : Expr.__mul__,
                   '__rmul__' : Expr.__rmul__,
                   '__truediv__' : Expr.__truediv__,
                   '__rtruediv__' : Expr.__rtruediv__,
                   'collect' : None,   # call super() explicitly and retain algebra on result
                   'simplify' : Basic.simplify,
                   }


class OperatorAlgebra():
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
    algebra.  The operator algebra classes rely on the @call_highest_priority
    decorator and associated _op_priority attribute.

    """
    __slots__ = ('cls_name',) + operator_algebra_attributes

    def __init__(self, **kwargs):
        for attr in operator_algebra_attributes:
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
            else:
                setattr(self, attr, default_algebra[attr] )
        self.cls_name = kwargs.get('cls_name', 'Unknown')

    def copy(self, *args, **kwargs):
        new = OperatorAlgebra(cls_name=self.cls_name)
        for attr in operator_algebra_attributes:
            setattr(new, attr, getattr(self, attr, None))
        return new

    def _hashable_content(self):
        return set([getattr(self,x,None) for x in self.__slots__])

    def __repr__(self):
        return f"{self.cls_name}.OperatorAlgebra"

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        if not isinstance(other,OperatorAlgebra):
            return False
        for attr in self.__slots__:
            if getattr(self, attr) != getattr(other,attr):
                return False
        return True


class OperatorAlgebraExpr(Expr):
    """
    Implement methods of operator algebra in core classes Add, Mul and Pow
    """

    @property
    def _op_priority(self):
        return getattr(self._algebra, '_op_priority', Expr._op_priority)


    def __add__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__add__(self, other)

        _handler = getattr(self._algebra, '__add__', Expr.__add__)
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __radd__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__radd__(self, other)

        _handler = getattr(self._algebra, '__radd__', Expr.__radd__)
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __sub__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__sub__(self, other)

        _handler = getattr(self._algebra, '__sub__', Expr.__sub__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __rsub__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__rsub__(self, other)

        _handler = getattr(self._algebra, '__rsub__', Expr.__rsub__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __mul__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__mul__(self, other)

        _handler = getattr(self._algebra, '__mul__', Expr.__mul__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __rmul__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__rmul__(self, other)

        _handler = getattr(self._algebra, '__rmul__', Expr.__rmul__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __truediv__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__truediv__(self, other)

        _handler = getattr(self._algebra, '__truediv__', Expr.__truediv__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __rtruediv__(self, other, **kwargs):
        if self._algebra is None:
            return Expr.__rtruediv__(self, other)

        _handler = getattr(self._algebra, '__rtruediv__', Expr.__rtruediv__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def __pow__(self, other, mod = None):
        if self._algebra is None:
            return Expr.__pow__(self, other)

        _handler = getattr(self._algebra, '__pow__', Expr.__pow__ )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def _pow(self, other, **kwargs):
        if self._algebra is None:
            return Expr._pow(self, other)

        _handler = getattr(self._algebra, '_pow', Expr._pow )
        obj = _handler(self,other)
        obj._algebra = self._algebra
        return obj


    def collect(self, syms, *args, **kwargs):
        if self._algebra is None:
            return super().collect(syms, *args, **kwargs)

        _handler = getattr(self._algebra, 'collect', None)
        if _handler is not None:
            return _handler(self, syms, *args, **kwargs)
        expr = super().collect(syms, *args, **kwargs)
        expr._algebra = self._algebra
        return expr


    def simplify(self, *args, **kwargs):
        if self._algebra is None:
            return super().simplify(*args, **kwargs)

        _handler = getattr(self._algebra, 'simplify', None)
        if _handler is not None:
            return _handler(self, *args, **kwargs)
        expr = super().simplify(*args, **kwargs)
        expr._algebra = self._algebra
        return expr


    def subs(self, *args, **kwargs):
        if self._algebra is None:
            return super().subs(*args, **kwargs)

        expr = super().subs(*args, **kwargs)
        expr._algebra = self._algebra
        return expr


class OperatorAlgebraMeta(type):
    """
    Metaclass to generate an OperatorAlgebra for a class


    Priority of algebras
    ====================

    OperatorAlgebraMeta selects from algebras in the following order:
        1. An algebra defined by the class itself,
        2. An implicit algebra defined in the class,
        3. An algebra defined by the bases of the class.

    A class implicitly defines an algebra if it has an _op_priority
    greater than the default, Expr._op_priority. The algebra consists
    of the defined _op_priority and any of class methods from the
    operator_algebra_attributes list.


    See Also
    ========

        sympy.core.basic.Expr
        sympy.core.add.Add
        sympy.core.mul.Mul
        sympy.core.power.Pow
    """

    def __new__(cls, name, bases, dct):
        # If an algebra is defined in the class, use it
        if '_algebra' in dct:
            dct['_op_priority'] = dct['_algebra']._op_priority
            return super().__new__(cls, name, bases, dct)

        # If class priority is greater than the default, build the algebra
        if '_op_priority' in dct and dct['_op_priority'] > Expr._op_priority:
            dct['_algebra'] = OperatorAlgebra(**dct, cls_name = name)
            return super().__new__(cls, name, bases, dct)

        return super().__new__(cls, name, bases, dct)
