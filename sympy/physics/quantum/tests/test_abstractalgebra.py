from sympy.algebras.basicalgebra import BasicAlgebra
from sympy.physics.quantum.abstractalgebra import AbstractAlgebra, get_algebra, _no_handler


def test_get_algebra():
    from sympy import Add, Mul, Pow, ImmutableDenseMatrix, MatAdd, MatMul

    b = get_algebra()

    assert isinstance( b, BasicAlgebra )
    assert b._op_priority == 10.0
    assert b._add_handler is Add
    assert b._mul_handler == Mul
    assert b._pow_handler is Pow

    m = get_algebra( ImmutableDenseMatrix( [[1, 0, ], [0, 1]] ) )
    assert m._op_priority == 10.001
    assert m._add_handler is MatAdd
    assert m._mul_handler is MatMul
    assert m._pow_handler is _no_handler


def test_abstractalgebra_construction():
    from sympy.core.expr import Expr
    a = AbstractAlgebra()

    assert isinstance( a, AbstractAlgebra )
    assert isinstance( a, Expr )
