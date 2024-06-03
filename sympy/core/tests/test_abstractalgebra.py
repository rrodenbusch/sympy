from sympy.core.abstractalgebra import BasicAlgebra, AlgebraicOp
from sympy.core.expr import Expr
# from sympy.testing.pytest import XFAIL


def test_basic_algebra_class():
    b = BasicAlgebra()
    assert b._op_priority == 10

    b = BasicAlgebra(_op_priority = 100)
    assert b._op_priority == 100


def test_create_algebraicop():
    b = AlgebraicOp()
    assert isinstance( b, Expr)
