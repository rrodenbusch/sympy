""" Base class for extension of core Add, Mul and Pow classes
    Used to prevent:
        1. pow(b, 0), Expr.pow(0), or Expr**0 from returning S.One (1) immediately
            if the exponent is Zero,
        2. collect() from exceptioning due to non-commutative symbols
        3. expand() from returning core Add, Mul or Pow class
"""
import sympy
from sympy import sympify
from sympy.core.singleton import S
from sympy.utilities.exceptions import sympy_deprecation_warning
from sympy.core.decorators import call_highest_priority

from sympy.physics.quantum.collect import collect
from sympy.core import Expr
import sympy.core.add
import sympy.core.mul
import sympy.core.power

__all__ = [
    'QCore',
    'Add',
    'Mul',
    'Pow',
    'collect',
]


class QCore( Expr ):

    @property
    def _op_priority( self ):
        return 100

    def __radd__( self, other, *args, **kwargs ):
        return Add( other, self, *args, **kwargs )

    def __add__( self, *args, **kwargs ):
        return Add( self, *args, **kwargs )

    def __mul__( self, *args, **kwargs ):
        return Mul( self, *args, **kwargs )

    def __rmul__( self, other, *args, **kwargs ):
        return Mul( other, self, *args, **kwargs )

    def __pow__( self, *args, **kwargs ):
        return Pow( self, *args, **kwargs )

    @call_highest_priority( 'collect' )
    def collect( self, syms, *args, **kwargs ):
        return collect( self, syms, *args, **kwargs )


class Add( QCore, sympy.core.add.Add ):

    @property
    def _op_priority( self ):
        return 105

    def _eval_expand_add( self, *args, **kwargs ):
        return super()._eval_expand_add( *args, **kwargs )

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__( self, other ):
        if not isinstance( other, Add ) and isinstance( other, sympy.core.add.Add ):
            other = Add( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.add.Add.__hash__


class Mul( QCore, sympy.core.mul.Mul ):

    @property
    def _op_priority( self ):
        return 110

    def _eval_power( self, e, *args, **kwargs ):
        # Evaluation may force return sympy.core type
        p = Pow( self, e, evaluate=False )
        if e.is_Rational or e.is_Float:
            return p._eval_expand_power_base()
        return p

    def _eval_expand_mul( self, *args, **kwargs ):
        return super()._eval_expand_mul( *args, **kwargs )

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__( self, other ):
        if not isinstance( other, Mul ) and isinstance( other, sympy.core.mul.Mul ):
            other = Mul( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.mul.Mul.__hash__


class Pow( QCore, sympy.core.power.Pow ):

    @property
    def _op_priority( self ):
        return 115

    def _eval_expand_power_base( self, *args, **kwargs ):
        return super()._eval_expand_power_base( *args, **kwargs )

    def _eval_expand_power_exp( self, *args, **kwargs ):
        return super()._eval_expand_power_base( *args, **kwargs )

    def __new__( cls, *args, **kwargs ):
        if len( args ) > 1 and sympify( args[1] ) is S.Zero:
            ( b, e, obj ) = ( args[0], S.Zero, None )
            if hasattr( b, 'mul_identity' ):
                return b.mul_identity
            elif isinstance( b, ( Pow, Mul, Add ) ):
                idents = {}
                for arg in b.args:
                    ident = Pow( arg, S.Zero )
                    if ident is not S.One:
                        idents[type( ident )] = ident
                if len( idents ) == 1:
                    return list( idents.values() )[0]
                elif len( idents ):
                    sympy_deprecation_warning( f"""
    Use of multiple Identity() types in expressions is deprecated (in this case, the types
    are {idents.keys()}).""",
                        deprecated_since_version="1.12",
                        active_deprecations_target="mixed-identity-type-expr",
                        stacklevel=4,
                    )
                    return S.One
                else:
                    return S.One
            if kwargs.get( 'evaluate', False ):
                p = None
                if hasattr( b, '_eval_power' ):
                    p = b._eval_power( e )
                if p is None and hasattr( b, '_pow' ):
                    p = b._pow( e, **kwargs )
                if p is not None:
                    return p

        return super().__new__( cls, *args, **kwargs )

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__( self, other ):
        if not isinstance( other, Pow ) and isinstance( other, sympy.core.power.Pow ):
            other = Pow( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.power.Pow.__hash__
