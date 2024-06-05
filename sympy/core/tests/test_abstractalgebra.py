from sympy.core.abstractalgebra import AbstractAlgebra, AbstractAlgebraOp, AbstractAlgebraMeta
from sympy.core.expr import Expr


def test_abstractalgebra_class():
    b = AbstractAlgebra()
    assert b._op_priority == 10

    b = AbstractAlgebra(_op_priority=100)
    assert b._op_priority == 100


def test_create_abstractalgebraop():
    b = AbstractAlgebraOp()
    assert isinstance(b, Expr)

def _new_pow(self, *args, **kwargs):
    pass


class AExpr(Expr, metaclass=AbstractAlgebraMeta):
    _op_priority = 110
    algebra = AbstractAlgebra(_op_priority=120, _pow=_new_pow)


class BExpr(Expr, metaclass=AbstractAlgebraMeta):
    _op_priority = 50

    def _pow(self, *args, **kwargs):
        return super()._pow(*args, **kwargs)


class CExpr(Expr, metaclass=AbstractAlgebraMeta):
    _op_priority = 130
    algebra = AbstractAlgebra(_op_priority=140, _pow=_new_pow, class_name='cexpr')

    def __init__(self, *args, **kwargs):
        if 'algebra' in kwargs:
            self.algebra = kwargs['algebra']


def test_abstractalgebra_repr():
    assert repr(AbstractAlgebra(class_name='test_repr')) == 'test_repr.AbstractAlgebra'
    assert repr(AbstractAlgebra()) == 'Unknown.AbstractAlgebra'
    assert repr(AExpr().algebra) == 'Unknown.AbstractAlgebra'
    assert repr(BExpr().algebra) == 'BExpr.AbstractAlgebra'
    assert repr(CExpr().algebra) == 'cexpr.AbstractAlgebra'



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

    d = CExpr(algebra=AbstractAlgebra(_op_priority=150))

    assert d._op_priority == 140
    assert d.algebra._op_priority == 150
    assert not hasattr(d.algebra, '_pow')
