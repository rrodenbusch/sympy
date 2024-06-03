from sympy.core.abstractalgebra import BasicAlgebra
from sympy.core.basic import ordering_of_classes

from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow
from sympy import Symbol

from sympy.testing.pytest import XFAIL


def test_basic_algebra_class():
    b = BasicAlgebra()
    assert b._op_priority == 10

    b = BasicAlgebra(_op_priority = 100)
    assert b._op_priority == 100
