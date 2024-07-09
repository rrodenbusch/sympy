from sympy.core.operatoralgebra import OperatorAlgebra, OperatorAlgebraExpr, OperatorAlgebraMeta
from sympy.core.expr import Expr
from sympy.core.symbol import symbols

from sympy.testing.pytest import raises

def _new_pow(self, *args, **kwargs):
    pass


class BaseExpr(OperatorAlgebraExpr):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._algebra = cls._algebra
        return obj


class AExpr(BaseExpr, metaclass = OperatorAlgebraMeta):
    _op_priority = 110
    _algebra = OperatorAlgebra(_op_priority = 120, _pow = _new_pow)

    def __rtruediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e

    def __truediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e


class BExpr(BaseExpr, metaclass = OperatorAlgebraMeta):
    _op_priority = 50

    def __rtruediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e

    def __truediv__(self, other, *args, **kwargs):
        if isinstance(other, BaseExpr):
            return NotImplemented
        e = Expr.__truediv__(self, other)
        e._algebra = kwargs.get('algebra', BExpr._algebra)
        return e

    def _pow(self, *args, **kwargs):
        return super()._pow(*args, **kwargs)


class CExpr(BaseExpr, metaclass = OperatorAlgebraMeta):
    _op_priority = 130
    _algebra = OperatorAlgebra(_op_priority = 140, _pow = _new_pow, cls_name = 'cexpr')

    def __init__(self, *args, **kwargs):
        if 'algebra' in kwargs:
            self._algebra = kwargs['algebra']

    def __rtruediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e

    def __truediv__(self, other, *args, **kwargs):
        e = NotImplemented
        return e


def test_operatoralgebra_class():
    b = OperatorAlgebra()
    assert b._op_priority == 10

    b = OperatorAlgebra(_op_priority = 100)
    assert b._op_priority == 100


def test_operatoralgebra_create():
    b = OperatorAlgebraExpr()
    assert isinstance(b, Expr)


def test_operatoralgebra_repr():
    assert repr(OperatorAlgebra(cls_name = 'test_repr')) == 'test_repr.OperatorAlgebra'
    assert repr(OperatorAlgebra()) == 'Unknown.OperatorAlgebra'
    assert repr(AExpr()._algebra) == 'Unknown.OperatorAlgebra'
    assert repr(BExpr()._algebra) == 'BExpr.OperatorAlgebra'
    assert repr(CExpr()._algebra) == 'cexpr.OperatorAlgebra'


def test_operatoralgebra_div():
    A = AExpr()
    B = BExpr()
    (a, b) = symbols('a b')

    raises(TypeError, lambda: A / b)
    raises(TypeError, lambda: A / B)
    raises(TypeError, lambda: A / 2)
    raises(TypeError, lambda: 2 / B)

    assert(A * b**-1 == 1/b * A)

    C = (B * b**-1)
    D = C / 2
    assert(C._algebra == BExpr._algebra)
    assert(D._algebra == BExpr._algebra)


def test_operatoralgebra_copy():
    org = BExpr._algebra
    new = BExpr._algebra.copy()

    assert id(org) == id(BExpr._algebra)
    assert id(new) != id(BExpr._algebra)
    assert org.__slots__ == new.__slots__
    for attr in org.__slots__:
        assert( getattr(org, attr) == getattr(new, attr))
    priority = org._op_priority
    new._op_priority = org._op_priority + 1
    assert org._op_priority == priority
    assert new._op_priority != priority


def test_operatoralgebra_expr():
    a = AExpr()
    assert isinstance(a, Expr)
    assert a._op_priority == 120
    assert hasattr(a, '_algebra')
    assert a._algebra._pow == _new_pow

    b = BExpr()
    assert isinstance(b, Expr)
    assert b._op_priority == 50
    assert b._algebra._pow == BExpr._pow

    c = CExpr()
    assert c._op_priority == 140
    assert c._algebra._pow == _new_pow

    d = CExpr(algebra = OperatorAlgebra(_op_priority = 150))

    assert d._op_priority == 140
    assert d._algebra._op_priority == 150
    assert d._algebra._pow == Expr._pow
