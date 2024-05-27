from sympy.algebras.basicalgebra import BasicAlgebra
from sympy.physics.quantum.abstractalgebra import _no_handler
from sympy import ImmutableDenseMatrix, MatAdd, MatMul


def test_basicalgebra_construction():
    from sympy.core.add import Add
    from sympy.core.mul import Mul
    from sympy.core.power import Pow

    b = BasicAlgebra()

    assert isinstance( b, BasicAlgebra )
    assert b._op_priority == 10.0
    assert b._add_handler is Add
    assert b._mul_handler == Mul
    assert b._pow_handler is Pow
