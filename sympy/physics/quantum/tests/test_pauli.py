""" Pauli operator basis tests

    TODO:
    See XFAIL test cases for TBD enhancements. Some changes may be
    internal to AbstractAlgebra classes

    Commutators return core.Mul sometimes
        forced type conversion in __eq__ hides issue
        @XFAIL test_commutator_type_fails()

    evalf() of matrix inside opMul doesn't expand into matrix
    evalf() -> Function() class [e.g. sin() exits the Ring]
    expand().simplify()

"""

from sympy import symbols
import sympy.core.mul
from sympy.physics.quantum.abstractalgebra import AbstractAlgebra, opAdd, opMul, opPow
from sympy.core.numbers import I
from sympy.matrices import Matrix, ImmutableDenseMatrix
from sympy.printing.latex import latex
from sympy.physics.quantum import ( Dagger, Commutator, AntiCommutator, qapply,
                                   Operator, represent )
from sympy.physics.quantum.pauli import ( SigmaOpBase, SigmaI, SigmaX, SigmaY, SigmaZ,
                                         SigmaMinus, SigmaPlus,
                                         qsimplify_pauli, qcollect_pauli )
from sympy.physics.quantum.pauli import SigmaZKet, SigmaZBra
from sympy.testing.pytest import raises, XFAIL

si, sx, sy, sz = SigmaI(), SigmaX(), SigmaY(), SigmaZ()
si1, sx1, sy1, sz1 = SigmaI( 1 ), SigmaX( 1 ), SigmaY( 1 ), SigmaZ( 1 )
si2, sx2, sy2, sz2 = SigmaI( 2 ), SigmaX( 2 ), SigmaY( 2 ), SigmaZ( 2 )

sm, sp = SigmaMinus(), SigmaPlus()
sm1, sp1 = SigmaMinus( 1 ), SigmaPlus( 1 )
A, B = Operator( "A" ), Operator( "B" )


def test_pauli_operators_types():

    assert isinstance( si, SigmaOpBase ) and isinstance( si, SigmaI )
    assert isinstance( sx, SigmaOpBase ) and isinstance( sx, SigmaX )
    assert isinstance( sy, SigmaOpBase ) and isinstance( sy, SigmaY )
    assert isinstance( sz, SigmaOpBase ) and isinstance( sz, SigmaZ )
    assert isinstance( sm, SigmaOpBase ) and isinstance( sm, SigmaMinus )
    assert isinstance( sp, SigmaOpBase ) and isinstance( sp, SigmaPlus )


def test_pauli_operators_commutator():

    Commutator( SigmaZ(), SigmaX() ).doit()

    assert Commutator( sx, sy ).doit() == 2 * I * sz
    assert Commutator( sy, sz ).doit() == 2 * I * sx
    assert Commutator( sz, sx ).doit() == 2 * I * sy

    assert Commutator( si, sx ).doit() == 0
    assert Commutator( si, sy ).doit() == 0
    assert Commutator( si, sz ).doit() == 0


def test_pauli_operators_commutator_with_labels():

    assert Commutator( sx1, sy1 ).doit() == 2 * I * sz1
    assert Commutator( sy1, sz1 ).doit() == 2 * I * sx1
    assert Commutator( sz1, sx1 ).doit() == 2 * I * sy1

    assert Commutator( si1, sx1 ).doit() == 0
    assert Commutator( si1, sy1 ).doit() == 0
    assert Commutator( si1, sz1 ).doit() == 0

    assert Commutator( sx2, sy2 ).doit() == 2 * I * sz2
    assert Commutator( sy2, sz2 ).doit() == 2 * I * sx2
    assert Commutator( sz2, sx2 ).doit() == 2 * I * sy2

    assert Commutator( si2, sx2 ).doit() == 0
    assert Commutator( si2, sy2 ).doit() == 0
    assert Commutator( si2, sz2 ).doit() == 0

    assert Commutator( sx1, sy2 ).doit() == 0
    assert Commutator( sy1, sz2 ).doit() == 0
    assert Commutator( sz1, sx2 ).doit() == 0
    assert Commutator( si1, si2 ).doit() == 0


def test_pauli_operators_anticommutator():

    assert AntiCommutator( sy, sz ).doit() == 0
    assert AntiCommutator( sz, sx ).doit() == 0
    assert AntiCommutator( sx, sm ).doit() == 1
    assert AntiCommutator( sx, sp ).doit() == 1


def test_pauli_operators_adjoint():

    assert Dagger( si ) == si
    assert Dagger( sx ) == sx
    assert Dagger( sy ) == sy
    assert Dagger( sz ) == sz

    assert si.dagger() == si
    assert sx.dagger() == sx
    assert sy.dagger() == sy
    assert sz.dagger() == sz

    assert sx1.dagger() == sx1
    assert sx.dagger() != sx1
    assert sx1.dagger() != sx


def test_pauli_operators_adjoint_with_labels():

    assert Dagger( si1 ) == si1
    assert Dagger( sx1 ) == sx1
    assert Dagger( sy1 ) == sy1
    assert Dagger( sz1 ) == sz1

    assert Dagger( si1 ) != si2
    assert Dagger( sx1 ) != sx2
    assert Dagger( sy1 ) != sy2
    assert Dagger( sz1 ) != sz2


def test_pauli_operators_multiplication():

    assert si ** 2 == si
    assert sx ** 2 == si
    assert sy ** 2 == si
    assert sz ** 2 == si

    assert si ** 3 == si
    assert sx ** 3 == sx
    assert sy ** 3 == sy
    assert sz ** 3 == sz

    assert qsimplify_pauli( si * sx ) == sx
    assert qsimplify_pauli( si * sy ) == sy
    assert qsimplify_pauli( si * sz ) == sz

    assert qsimplify_pauli( sx * sx ) == si
    assert qsimplify_pauli( sy * sy ) == si
    assert qsimplify_pauli( sz * sz ) == si

    assert qsimplify_pauli( sx * sy ) == I * sz
    assert qsimplify_pauli( sy * sz ) == I * sx
    assert qsimplify_pauli( sz * sx ) == I * sy

    assert qsimplify_pauli( sy * sx ) == -I * sz
    assert qsimplify_pauli( sz * sy ) == -I * sx
    assert qsimplify_pauli( sx * sz ) == -I * sy


def test_pauli_operators_multiplication_with_labels():

    assert qsimplify_pauli( si1 * sx1 ) == sx1
    assert qsimplify_pauli( si1 * sy1 ) == sy1
    assert qsimplify_pauli( si1 * sz1 ) == sz1

    assert qsimplify_pauli( sx1 * sx1 ) == si1
    assert qsimplify_pauli( sy1 * sy1 ) == si1
    assert qsimplify_pauli( sz1 * sz1 ) == si1
    assert qsimplify_pauli( sx1 * sy1 * sx2 * sy2 ) == -sz1 * sz2
    assert qsimplify_pauli( sy1 * sz1 * sz2 * sx2 ) == -sx1 * sy2


def test_pauli_instances():
    ( a, b, c ) = symbols( 'a b c' )
    mul_expr_xy = sx1 * sx2
    mul_expr_xz = sy1 * sz2
    mul_expr_yz = sy1 * sz2
    add_expr_xy = sx1 + sx2
    add_expr_xz = sy1 + sz2
    add_expr_yz = sy1 + sz2

    assert isinstance( mul_expr_xy, opMul )
    assert isinstance( mul_expr_xz, opMul )
    assert isinstance( mul_expr_yz, opMul )

    assert isinstance( mul_expr_xy, AbstractAlgebra )
    assert isinstance( mul_expr_xz, AbstractAlgebra )
    assert isinstance( mul_expr_yz, AbstractAlgebra )

    assert isinstance( mul_expr_xy, sympy.core.mul.Mul )
    assert isinstance( mul_expr_xz, sympy.core.mul.Mul )
    assert isinstance( mul_expr_yz, sympy.core.mul.Mul )

    assert isinstance( add_expr_xy, opAdd )
    assert isinstance( add_expr_xz, opAdd )
    assert isinstance( add_expr_yz, opAdd )

    assert isinstance( add_expr_xy, AbstractAlgebra )
    assert isinstance( add_expr_xz, AbstractAlgebra )
    assert isinstance( add_expr_yz, AbstractAlgebra )

    assert isinstance( add_expr_xy, sympy.core.add.Add )
    assert isinstance( add_expr_xz, sympy.core.add.Add )
    assert isinstance( add_expr_yz, sympy.core.add.Add )

    assert isinstance( mul_expr_xy ** b, opPow )
    assert isinstance( mul_expr_xy ** b, AbstractAlgebra )
    assert isinstance( mul_expr_xy ** b, sympy.core.power.Pow )

    assert isinstance( add_expr_xy ** b, opPow )
    assert isinstance( add_expr_xy ** b, AbstractAlgebra )
    assert isinstance( add_expr_xy ** b, sympy.core.power.Pow )


def test_pauli_power_quantum():
    ( a, b ) = symbols( 'a:b' )
    ax = a * SigmaX()
    by = a * SigmaY()
    assert isinstance( a * SigmaI() * SigmaY(), opMul )
    assert isinstance( a * SigmaI() + b * SigmaI(), opAdd )
    assert isinstance( SigmaX() ** a, opPow )
    assert ( a * SigmaX() + b * SigmaY() ) ** 0 == SigmaI()
    assert opPow( a * SigmaX() + b * SigmaY(), 0 ) == SigmaI()

    assert SigmaX() ** 0 == SigmaI()
    assert ( SigmaX() + SigmaY() ) ** 0 == SigmaI()
    assert ( SigmaX() * SigmaY() ) ** 0 == SigmaI()
    assert ( a * SigmaX() + b * SigmaY() ) ** 0 == SigmaI()

    assert opPow( sx, a ).subs( a, 0 ) == si
    assert opPow( sx1, a ).subs( a, 0 ) == si1
    assert opPow( sx, a ).subs( a, b ) == sx ** b

    assert isinstance( ax * by, opMul )


def test_pauli_expand():
    from sympy import cos, sin, pi, I
    from sympy.physics.quantum.collect import collect

    i = I
    ( ex, ey, ez ) = symbols( 'ex ey ez' )
    ( thx, thy, thz, ) = symbols( 'Tx Ty Tz' )
    all = ( si, sx, sy, sz ) = ( SigmaI(), SigmaX(), SigmaY(), SigmaZ() )

    EX = cos( ex ) * si + i * sin( ex ) * sx
    RX = cos( thx / 2 ) * si + i * sin( thx / 2 ) * sx
    EZ = cos( ez ) * si + i * sin( ez ) * sz
    RZ = cos( thz / 2 ) * si + i * sin( thz / 2 ) * sz

    RYGate = EZ * RZ.subs( {thz:-1 * pi / 2} ) * EX * RX.subs( {thx:thy} ) * EZ * RZ.subs( {thz:pi / 2} )
    assert isinstance( RYGate, AbstractAlgebra )
    assert isinstance( RYGate.collect( all ), AbstractAlgebra )
    assert collect( RYGate, all ) == RYGate.collect( all )
    assert isinstance( RYGate.expand(), AbstractAlgebra )
    assert collect( RYGate.expand(), all ) == RYGate.expand().collect( all )


def test_pauli_collect():
    from sympy import sin
    from sympy.physics.quantum.collect import collect

    ( a, b, c, d, ) = symbols( 'a:d' )
    all = ( si, sx, sy, sz ) = ( SigmaI(), SigmaX(), SigmaY(), SigmaZ() )

    testcases = ( ( [a * sx + b * sx + c * sy + d * sy, all, ], ( a + b ) * sx + ( c + d ) * sy, ),
                 ( [a * si + b * sz + c * si + d * sz, all, ], ( a + c ) * si + ( b + d ) * sz, ),
                 ( [( a + d ) * sx + b * d * sx + c * sy + d * sy, all, ], ( a + d + b * d ) * sx + ( c + d ) * sy, ),
                 ( [( a + d ) * sz + b * d * si + c * si + d * sz, all, ], ( b * d + c ) * si + ( a + 2 * d ) * sz, ),
                 ( [( a + d ) * sz + b * d * si + c * si + d * sz, ( si, ), ], ( b * d + c ) * si + ( a + d ) * sz + d * sz, ),
                 ( [sx, ( sx, sy, a, ), ], sx, ),
                )

    for ( args, result ) in testcases:
        assert collect( *args ) == result

    for ( args, result ) in testcases:
        ( e, syms ) = args
        assert e.collect( syms ) == result

    assert collect( sin( ( a + ( d + ( b * si + c * si ) ) ) ), all ) == sin( a + d + ( b + c ) * si )


def test_pauli_qcollect_pauli():
    ( a, b, c, d, ) = symbols( 'a:d' )
    all = ( si, sx, sy, sz ) = ( SigmaI(), SigmaX(), SigmaY(), SigmaZ() )

    testcases = ( ( [a * sx + b * sx + c * sy + d * sy, all, ], ( a + b ) * sx + ( c + d ) * sy, ),
                 ( [a * si + b * sz + c * si + d * sz, all, ], ( a + c ) * si + ( b + d ) * sz, ),
                 ( [( a + d ) * sx + b * d * sx + c * sy + d * sy, all, ], ( a + d + b * d ) * sx + ( c + d ) * sy, ),
                 ( [( a + d ) * sz + b * d * si + c * si + d * sz, all, ], ( b * d + c ) * si + ( a + 2 * d ) * sz, ),
                 ( [( a + d ) * sz + b * d * si + c * si + d * sz, ( si, ), ], ( b * d + c ) * si + ( a + d ) * sz + d * sz, ),
                )

    for ( args, result ) in testcases:
        assert qcollect_pauli( *args ) == result

    testcases = ( ( ( ( a + d ) * sz + b * d * si + c * si + d * sz, ( si, ), ), ( b * d + c ) * si + ( a + 2 * d ) * sz, ),
                )
    for ( args, result ) in testcases:
        assert qcollect_pauli( *args ) != result

    raises( ValueError, lambda: qcollect_pauli( a * sx + b * sy, ( a * si, ) ) )


def test_pauli_states():
    si, sx, sz = SigmaI(), SigmaX(), SigmaZ()

    up = SigmaZKet( 0 )
    down = SigmaZKet( 1 )

    assert qapply( sx * up ) == down
    assert qapply( sx * down ) == up
    assert qapply( sz * up ) == up
    assert qapply( sz * down ) == -down
    assert qapply( si * down ) == down
    assert qapply( si * up ) == up

    up = SigmaZBra( 0 )
    down = SigmaZBra( 1 )

    assert qapply( up * sx, dagger=True ) == down
    assert qapply( down * sx, dagger=True ) == up
    assert qapply( up * sz, dagger=True ) == up
    assert qapply( down * sz, dagger=True ) == -down
    assert qapply( down * si, dagger=True ) == down
    assert qapply( up * si, dagger=True ) == up

    assert Dagger( SigmaZKet( 0 ) ) == SigmaZBra( 0 )
    assert Dagger( SigmaZBra( 1 ) ) == SigmaZKet( 1 )
    raises( ValueError, lambda: SigmaZBra( 2 ) )
    raises( ValueError, lambda: SigmaZKet( 2 ) )


def test_commute():

    assert sx.commute( sy ) == Commutator( sx, sy )
    assert sx.commute( sy ).doit() == 2 * I * sz
    assert sy.commute( sz ).doit() == 2 * I * sx
    assert sy.commute( sz ).doit().evalf() == Matrix( [[0, 2.0 * I], [2.0 * I, 0]] )

    assert isinstance( Commutator( SigmaZ(), SigmaX() ).doit(), opMul )


def test_evalf():
    from sympy import exp
    ( a, b, ) = symbols( 'a b' )

    assert ( a * exp( SigmaX() ) ).evalf() == a * exp( SigmaX() )
    assert ( a * exp( SigmaX( 1, suppress_evalf=True ) ) ).evalf() == a * exp( SigmaX( 1 ) )

    assert si.evalf() == Matrix( [[1, 0], [0, 1]] )
    assert sx.evalf() == Matrix( [[0, 1], [1, 0]] )
    assert sy.evalf() == Matrix( [[0, -I], [I, 0]] )
    assert sz.evalf() == Matrix( [[1, 0], [0, -1]] )
    assert sm.evalf() == Matrix( [[0, 0], [1, 0]] )
    assert sp.evalf() == Matrix( [[0, 1], [0, 0]] )

    assert isinstance( si.evalf(), ImmutableDenseMatrix )
    assert isinstance( sx.evalf(), ImmutableDenseMatrix )
    assert isinstance( sy.evalf(), ImmutableDenseMatrix )
    assert isinstance( sz.evalf(), ImmutableDenseMatrix )
    assert isinstance( sm.evalf(), ImmutableDenseMatrix )
    assert isinstance( sp.evalf(), ImmutableDenseMatrix )

    assert si.evalf() == represent( si )
    assert sx.evalf() == represent( sx )
    assert sy.evalf() == represent( sy )
    assert sz.evalf() == represent( sz )
    assert sm.evalf() == represent( sm )
    assert sp.evalf() == represent( sp )


def test_hash():
    assert hash( sx ) == hash( SigmaX() )
    assert hash( sx1 ) == hash( SigmaX( 1 ) )
    assert hash( sm ) != hash( sm1 )

    assert hash( sx ) != hash( sy )
    assert hash( sy ) != hash( sz )
    assert hash( sz ) != hash( si )

    assert hash( sx ) == hash( SigmaX( suppress_evalf=False ) )
    assert hash( sx ) != hash( SigmaX( suppress_evalf=True ) )


def test_use_name():
    assert sm.use_name is False
    assert sm1.use_name is True
    assert sx.use_name is False
    assert sx1.use_name is True

    assert SigmaX( 0 ).use_name is True
    assert SigmaX( False ).use_name is False
    assert SigmaX( None ).use_name is False
    assert SigmaX().use_name is False


def test_printing():
    assert latex( si ) == r'{\sigma_I}'
    assert latex( si1 ) == r'{\sigma_I^{(1)}}'
    assert latex( sx ) == r'{\sigma_x}'
    assert latex( sx1 ) == r'{\sigma_x^{(1)}}'
    assert latex( sy ) == r'{\sigma_y}'
    assert latex( sy1 ) == r'{\sigma_y^{(1)}}'
    assert latex( sz ) == r'{\sigma_z}'
    assert latex( sz1 ) == r'{\sigma_z^{(1)}}'
    assert latex( sm ) == r'{\sigma_-}'
    assert latex( sm1 ) == r'{\sigma_-^{(1)}}'
    assert latex( sp ) == r'{\sigma_+}'
    assert latex( sp1 ) == r'{\sigma_+^{(1)}}'


def test_represent():
    assert represent( si ) == Matrix( [[1, 0], [0, 1]] )
    assert represent( sx ) == Matrix( [[0, 1], [1, 0]] )
    assert represent( sy ) == Matrix( [[0, -I], [I, 0]] )
    assert represent( sz ) == Matrix( [[1, 0], [0, -1]] )
    assert represent( sm ) == Matrix( [[0, 0], [1, 0]] )
    assert represent( sp ) == Matrix( [[0, 1], [0, 0]] )


def test_pauli_complete():
    from sympy import cos, sin, pi, I as i
    ( ex, ey, ez ) = symbols( 'ex ey ez' )
    ( thx, thy, thz, thz1, thz2, ) = symbols( 'Tx Ty Tz Tz1 Tz2' )
    ( si, sx, sy, sz ) = ( SigmaI(), SigmaX(), SigmaY(), SigmaZ() )

    EX = cos( ex ) * si + i * sin( ex ) * sx
    RX = cos( thx / 2 ) * si + i * sin( thx / 2 ) * sx
    EZ = cos( ez ) * si + i * sin( ez ) * sz
    RZ = cos( thz / 2 ) * si + i * sin( thz / 2 ) * sz

    FYGate = EZ * RZ.subs( {thz:thz1} ) * EX * RX.subs( {thx:thy} ) * EZ * RZ.subs( {thz: thz2} )
    expected = cos( thy / 2 + ex ) * si + i * sin( thy / 2 + ex ) * sy

    assert FYGate.subs( {thz1:-1 * pi / 2, thz2:pi / 2, thx:thy, ez:0, ey:ex} ).expand().simplify() == expected
