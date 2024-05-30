from sympy.core.basicalgebra import BasicAlgebra, default_algebra #, _no_handler
from sympy.core.basic import ordering_of_classes

from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow
# from sympy.core.expr import Expr
from sympy import Symbol


class AbstractAdd( Add ):
    __slots__ = ( '_class_order', )

    def __init__( self, *args, **kwargs ):
        self._class_order = ordering_of_classes.index( 'Add' )


class AbstractMul( Mul ):
    __slots__ = ( '_class_order', )

    def __init__( self, *args, **kwargs ):
        self._class_order = ordering_of_classes.index( 'Mul' )


class AbstractPow( Pow ):
    __slots__ = ( '_class_order', )

    def __init__( self, *args, **kwargs ):
        self._class_order = ordering_of_classes.index( 'Pow' )


class AbstractSymbol( Symbol ):
    __slots__ = ( '_algebra', '_op_priority', '_add_handler', '_mul_handler', '_pow_handler', '_class_order' )

    @property
    def algebra( self ):
        return self._algebra

    @algebra.setter
    def algebra( self, value ):
        self._algebra = value
        if value is not None:
            self._op_priority = value._op_priority
            self._add_handler = value._add_handler
            self._mul_handler = value._mul_handler
            self._pow_handler = value._pow_handler

    def __add__( self, other, *args, **kwargs ):
        if getattr( other, '_op_priority', 0 ) > self._op_priority:
            return getattr( other, '_add_handler', self._add_handler )( self, other, *args, **kwargs )
        return self._add_handler( self, other, *args, **kwargs )

    def __radd__( self, other, *args, **kwargs ):
        if getattr( other, '_op_priority', 0 ) > self._op_priority:
            return getattr( other, '_add_handler', self._add_handler )( other, self, *args, **kwargs )
        return self._add_handler( other, self, *args, **kwargs )

    def __mul__( self, other, *args, **kwargs ):
        if getattr( other, '_op_priority', 0 ) > self._op_priority:
            return getattr( other, '_mul_handler', self._mul_handler )( self, other, *args, **kwargs )
        return self._mul_handler( self, other, *args, **kwargs )

    def __rmul__( self, other, *args, **kwargs ):
        if getattr( other, '_op_priority', 0 ) > self._op_priority:
            return getattr( other, '_mul_handler', self._mul_handler )( other, self, *args, **kwargs )
        return self._mul_handler( other, self, *args, **kwargs )

    def __pow__( self, other, *args, **kwargs ):
        if getattr( other, '_op_priority', 0 ) > self._op_priority:
            return getattr( other, '_pow_handler', self._pow_handler )( self, other, *args, **kwargs )
        return self._pow_handler( self, other, *args, **kwargs )

    def __new__( cls, *args, **kwargs ):
        kwargs['commutative'] = False
        obj = super().__new__( cls, *args, **kwargs )
        obj.algebra = kwargs.get( 'algebra', default_algebra() )
        obj._class_order = ordering_of_classes.index( 'Symbol' )
        return obj

    def _hashable_content( self ):
        if self.algebra is None:
            _retval = super()._hashable_content()
        else:
            _retval = ( self.algebra._hashable_content(), *super()._hashable_content() )
        return _retval


def test_default_algebra():
    A = Symbol('A', commutative=False)
    B = Symbol('B', commutative=False)

    AB = A*B
    BA = B*A
    B2A = B*2.0*A
    BA2 = B*A*2.0
    assert isinstance(AB, Mul)
    assert AB != BA
    assert B2A == BA2



def test_basicalgebra_properties():
    algebra_140 = BasicAlgebra( 140, Add, AbstractMul, Pow, True )
    algebra_130 = BasicAlgebra( 130, AbstractAdd, Mul, AbstractPow, True )
    A = AbstractSymbol( 'A' )
    B = AbstractSymbol( 'B' )

    A.algebra = algebra_130
    C = A * B
    assert C._op_priority == 130
    assert C._add_handler is AbstractAdd
    assert C._mul_handler is Mul
    assert C._pow_handler is AbstractPow
    assert isinstance( C, Mul )
    assert not isinstance( C, AbstractMul )

    B.algebra = algebra_140
    C = A * B
    assert C._op_priority == 140
    assert C._add_handler is Add
    assert C._mul_handler is AbstractMul
    assert C._pow_handler is Pow
    assert isinstance( C, Mul )
    assert isinstance( C, AbstractMul )

    C = 2.0 * A
    assert C._op_priority == 130
    assert C._add_handler is AbstractAdd
    assert C._mul_handler is Mul
    assert C._pow_handler is AbstractPow
    assert isinstance( C, Mul )
    assert not isinstance( C, AbstractMul )

    C = 2.0 * B
    assert C._op_priority == 140
    assert C._add_handler is Add
    assert C._mul_handler is AbstractMul
    assert C._pow_handler is Pow
    assert isinstance( C, Mul )
    assert isinstance( C, AbstractMul )


def test_basicalgebra_construction():
    b = BasicAlgebra()

    assert isinstance( b, BasicAlgebra )
    assert b._op_priority == 10.0
    assert b._add_handler is Add
    assert b._mul_handler is Mul
    assert b._pow_handler is Pow
