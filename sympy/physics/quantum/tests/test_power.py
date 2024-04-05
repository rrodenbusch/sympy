from sympy import symbols
from sympy.core.power import Pow as cPow
from sympy.core.singleton import S
from sympy.physics.quantum import Operator, IdentityOperator
from sympy.physics.quantum.power import Pow as qPow

def test_Pow_inheritance():
    import sympy.core.power
    import sympy.physics.quantum.power
    (a,b) = symbols('a:b')
    assert isinstance( qPow(a,b), sympy.core.power.Pow  )
    assert isinstance( qPow(a,b), sympy.physics.quantum.power.Pow  )

    assert isinstance( cPow(a,b), sympy.core.power.Pow )
    assert not isinstance( cPow(a,b), sympy.physics.quantum.power.Pow )

def test_Pow_zero():
    (a,b) = symbols('a:b')
    opa = Operator()

    assert qPow(a,0) == S.One
    assert cPow(a,0) == S.One
    assert isinstance(qPow(opa,0), IdentityOperator)
    assert isinstance(qPow(opa,S.Zero), IdentityOperator)
