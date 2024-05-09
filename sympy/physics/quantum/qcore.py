""" Base class for extension of core Add, Mul and Pow classes
    Used to prevent:
        1. pow(b, 0), Expr.pow(0), or Expr**0 from returning S.One (1) immediately
            if the exponent is Zero,
        2. collect() from exceptioning due to non-commutative symbols
        3. expand() from returning core Add, Mul or Pow class

    TBD:
       Create function exp as subclass of functions.elementary.exponential.exp to
        support rotation operators expressed as exp(i*theta*Op) [theta:real, Op:Operator]
"""
import sympy
from sympy import sympify, simplify
from sympy.core.singleton import S
from sympy.utilities.exceptions import sympy_deprecation_warning
from sympy.core.decorators import call_highest_priority

from sympy.physics.quantum.collect import collect
from sympy.physics.quantum import Dagger, Commutator
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


def _map_QCore( e, deep=True ):
    """ Restore correct class for any expressions containing core expressions """
    if hasattr( e, 'args' ) and ( deep or not isinstance( e, QCore ) ):
        if deep:
            sargs = [ _map_QCore( x, deep=deep ) for x in e.args ]
        else:
            sargs = e.args
        if isinstance( e, sympy.core.add.Add ):
            return Add( *sargs, evaluate=False )
        if isinstance( e, sympy.core.mul.Mul ):
            return Mul( *sargs, evaluate=False )
        if isinstance( e, sympy.core.power.Pow ):
            return Pow( *sargs, evaluate=False )
    return e


def _get_unique_attrs( v, name, deep=True ):
    # Collect simplify methods for arguments
    attrs = {}
    if hasattr( v, 'args' ):
        for arg in v.args:
            if isinstance( arg, ( Add, Mul, Pow ) ):
                arg_attrs = _get_unique_attrs( arg, name )
                for arg_attr in arg_attrs:
                    attrs[arg_attr] = 1
            elif isinstance( arg, QCore ) and hasattr( arg, name ):
                attrs[getattr( arg, name )] = 1
    return attrs.keys()


class QCore( Expr ):
    is_scalar = False
    is_commutative = False

    def doit( self, *args, **kwargs ):
        return _map_QCore( super().doit( *args, **kwargs ) )

    def dagger( self ):
        return Dagger( self )

    def commute( self, other ):
        return Commutator( self, other )

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

    def expand( self, *args, **kwargs ):
        return super().expand( *args, **kwargs )

    def _eval_expand_add( self, *args, **kwargs ):
        if hasattr( super(), '_eval_expand_add' ):
            return _map_QCore( super()._eval_expand_mul( *args, **kwargs ) )
        return self

    def _eval_expand_mul( self, *args, **kwargs ):
        if hasattr( super(), '_eval_expand_mul' ):
            return _map_QCore( super()._eval_expand_mul( *args, **kwargs ) )
        return self

    def _eval_expand_power_base( self, *args, **kwargs ):
        if hasattr( super(), '_eval_expand_power_base' ):
            return _map_QCore( super()._eval_expand_power_base( *args, **kwargs ) )
        return self

    def _eval_expand_power_exp( self, *args, **kwargs ):
        if hasattr( super(), '_eval_expand_power_exp' ):
            return _map_QCore( super()._eval_expand_power_exp( *args, **kwargs ) )
        return self

    def simplify( self, *args, **kwargs ):
        return self._eval_simplify( *args, **kwargs )

    def diff( self, s ):
        return _map_QCore( super().diff( s ) )

    def _eval_derivative( self, s ):
        return _map_QCore( super()._eval_derivative( s ) )

    def _eval_simplify( self, *args, **kwargs ):
        expr = self
        if hasattr( self, 'args' ):
            sfuncs = _get_unique_attrs( self, '_eval_simplify', deep=True )
            for sfunc in sfuncs:
                expr = sfunc( expr, *args, **kwargs )

        # Avoid infinite recursion with _eval_simplify
        if isinstance( expr, Add ):
            expr = sympy.core.add.Add( *expr.args )
        elif isinstance( expr, Mul ):
            expr = sympy.core.mul.Mul( *expr.args )
        elif isinstance( expr, Pow ):
            expr = sympy.core.power.Pow( *expr.args )

        expr = simplify( expr, *args, **kwargs )
        return _map_QCore( expr )

    def _key( self ):
        return ( self.__class__, *[x.__hash__() for x in self.args] )


class Add( QCore, sympy.core.add.Add ):

    @property
    def _op_priority( self ):
        return 105

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

    def __repr__( self ):
        return '+'.join( [str( x ) for x in self.args] )

    def __str__( self ):
        return self.__repr__()

    def __hash__( self ):
        return hash( self._key() )


class Mul( QCore, sympy.core.mul.Mul ):

    @property
    def _op_priority( self ):
        return 110

    def _eval_power( self, e, *args, **kwargs ):
        # Do not evaluate p**e since it may return core.pow object
        p = Pow( self, e, evaluate=False )
        if e.is_Rational or e.is_Float:
            return p._eval_expand_power_base()
        return p

    def __repr__( self ):
        return '*'.join( [str( x ) for x in self.args] )

    def __str__( self ):
        return self.__repr__()

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

    def __hash__( self ):
        return hash( self._key() )


class Pow( QCore, sympy.core.power.Pow ):

    @property
    def _op_priority( self ):
        return 115

    def __new__( cls, *args, **kwargs ):
        if len( args ) > 1 and sympify( args[1] ) is S.Zero:
            ( b, e, ) = ( args[0], S.Zero, )
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

    def __hash__( self ):
        return hash( self._key() )


def _set_evalf_entry():
    """ Add the evalf processor functions to the global table """
    from sympy.core.evalf import evalf_table, evalf_add, evalf_mul, evalf_pow
    global evalf_table
    evalf_table[Add] = evalf_add
    evalf_table[Mul] = evalf_mul
    evalf_table[Pow] = evalf_pow


_set_evalf_entry()
