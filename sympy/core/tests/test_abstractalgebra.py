from sympy.core.abstractalgebra import AbstractAlgebra, AbstractAlgebraOp, AbstractAlgebraMeta
from sympy.core.expr import Expr
from sympy.core.symbol import symbols

from sympy.testing.pytest import raises


def test_abstractalgebra_class():
    b = AbstractAlgebra()
    assert b._op_priority == 10

    b = AbstractAlgebra(_op_priority = 100)
    assert b._op_priority == 100


def test_create_abstractalgebraop():
    b = AbstractAlgebraOp()
    assert isinstance(b, Expr)


def _new_pow(self, *args, **kwargs):
    pass


class BaseExpr(Expr):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj.algebra = cls.algebra
        return obj


class AExpr(BaseExpr, metaclass = AbstractAlgebraMeta):
    _op_priority = 110
    algebra = AbstractAlgebra(_op_priority = 120, _pow = _new_pow)

    # def __new__(cls, *args, **kwargs):
    #     obj = super().__new__(cls, *args, **kwargs)
    #     obj.algebra = cls.algebra
    #     return obj

    def __rtruediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e

    def __truediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e


class BExpr(BaseExpr, metaclass = AbstractAlgebraMeta):
    _op_priority = 50

    # def __new__(cls, *args, **kwargs):
    #     obj = super().__new__(cls, *args, **kwargs)
    #     obj.algebra = cls.algebra
    #     return obj

    def __rtruediv__(self, other, *args, **kwargs):
        # This makes division by the element
        e = NotImplemented
        return e

    def __truediv__(self, other, *args, **kwargs):
        if isinstance(other, BaseExpr):
            return NotImplemented
        e = Expr.__truediv__(self, other)
        e.algebra = kwargs.get('algebra', BExpr.algebra)
        return e

    def _pow(self, *args, **kwargs):
        return super()._pow(*args, **kwargs)


class CExpr(BaseExpr, metaclass = AbstractAlgebraMeta):
    _op_priority = 130
    algebra = AbstractAlgebra(_op_priority = 140, _pow = _new_pow, cls_name = 'cexpr')

    def __init__(self, *args, **kwargs):
        if 'algebra' in kwargs:
            self.algebra = kwargs['algebra']

    def __rtruediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e

    def __truediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e


def test_abstractalgebra_repr():
    assert repr(AbstractAlgebra(cls_name = 'test_repr')) == 'test_repr.AbstractAlgebra'
    assert repr(AbstractAlgebra()) == 'Unknown.AbstractAlgebra'
    assert repr(AExpr().algebra) == 'Unknown.AbstractAlgebra'
    assert repr(BExpr().algebra) == 'BExpr.AbstractAlgebra'
    assert repr(CExpr().algebra) == 'cexpr.AbstractAlgebra'


def test_abstractalgebra_div():
    A = AExpr()
    B = BExpr()
    (a, b) = symbols('a b')

    # truediv and rtruediv not supported in AbstractAlgebra
    raises(TypeError, lambda: A / b)
    raises(TypeError, lambda: A / B)
    raises(TypeError, lambda: A / 2)
    raises(TypeError, lambda: 2 / B)

    assert(A * b**-1 == 1/b * A)

    C = (B * b**-1)
    D = C / 2
    assert(C.algebra == BExpr.algebra)
    assert(D.algebra == BExpr.algebra)


def test_create_abstractexpr():
    a = AExpr()
    assert isinstance(a, Expr)
    assert a._op_priority == 120
    assert hasattr(a, 'algebra')
    assert a.algebra._pow == _new_pow

    b = BExpr()
    assert isinstance(b, Expr)
    assert b._op_priority == 50
    assert b.algebra._pow == BExpr._pow

    c = CExpr()
    assert c._op_priority == 140
    assert c.algebra._pow == _new_pow

    d = CExpr(algebra = AbstractAlgebra(_op_priority = 150))

    assert d._op_priority == 140
    assert d.algebra._op_priority == 150
    # assert not hasattr(d.algebra, '_pow')
