from sympy.core.expr import Expr
import sympy.core.add
import sympy.core.mul
import sympy.core.power


def _all_args( *args ):
    all_args = []
    for o in args:
        if hasattr( o, 'args' ) and len( o.args ):
            all_args.extend( _all_args( *o.args ) )
        if hasattr( o, '_op_priority' )  and not isinstance( o, AlgebraicOperation ):
            all_args.append( o )
    return all_args


def _args_top_priority( self, *args, **kwargs ):
    return max( 10.0, *[x._op_priority for x in _all_args( *self.args, *args )] )


def _top_priority_arg( self, *args, **kwargs ):
    all_args = _all_args( *self.args, *args )
    priority = max( 10.0, *[x._op_priority for x in all_args] )
    if getattr( self, '_op_priority', 0 ) > priority:
        return self
    arg = next( ( x for x in all_args if x._op_priority == priority ), None )
    return arg


def _no_handler( *args, **kwargs ):
    return NotImplemented


class AlgebraicOperation( Expr ):
    """
    Base class for Algebraic Operations (__mul__, etc.).

    Explanation
    ===========

    An AlgebraicOperation is class which can be chosen by the
    'call_highest_priority' decorator.  Operators derived from this
    class will adopt the highest _op_priority of all arguments
    and will choose the first argument with the highest priority to
    handle the call. Custom subclasses that want to define their
    own binary special methods should set an _op_priority value
    that is higher than the default.

    **NOTE**:
    This is a temporary fix, and will eventually be replaced with
    something better and more powerful.  See issue 5510.

    **Decprecation Note**
    ..deprecated:: 1.7

       Using arguments that aren't subclasses of :class:`~.Expr` in core
       operators (:class:`~.Mul`, :class:`~.Add`, and :class:`~.Pow`) is
       deprecated. See :ref:`non-expr-args-deprecated` for details.

    Notes
    =====

    The MutableDenseMatrix does not inherit from Expr and will
    be excluded from the search for highest priority arguments.

    The class Function does not inspect arguments for the _op_priority
    of arguments so operations on them may exit an Operator Algebra
    and revert to a field of Real or Complexes.

    See Also
    ========

    sympy.core.basic.Expr
    sympy.core.power.Pow
    sympy.matrices.MutableDenseMatrix

    """

    @property
    def _op_priority( self ):
        return _args_top_priority( self )

    @property
    def _add_handler( self ):
        return opAdd

    @property
    def _mul_handler( self ):
        return opMul

    @property
    def _pow_handler( self ):
        return opPow

    def __add__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_add_handler', _no_handler )( self, other )

    def __radd__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_add_handler', _no_handler )( other, self )

    def __mul__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_mul_handler', _no_handler )( self, other )

    def __rmul__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_mul_handler', _no_handler )( other, self )

    def __pow__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_pow_handler', _no_handler )( self, other )

    def _pow( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_pow_handler', _no_handler )( self, other )

    def _eval_add( self, other ):
        return opAdd( self, other, evaluate=False )

    def _eval_mul( self, other ):
        return opMul( self, other, evaluate=False )

    def _eval_power( self, e ):
        return opPow( self, e, evaluate=False )

    # @call_highest_priority( 'collect' )
    def collect( self, syms, *args, **kwargs ):
        arg = _top_priority_arg( self )
        return getattr( arg, '_collect_handler', _no_handler )( self, syms, *args, **kwargs )


from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow
from sympy import sympify
from sympy.core.singleton import S


class opAdd( AlgebraicOperation, Add ):

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__( self, other ):
        if not isinstance( other, opAdd ) and isinstance( other, sympy.core.add.Add ):
            other = opAdd( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.add.Add.__hash__


class opMul( AlgebraicOperation, Mul ):

    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.
    def __eq__( self, other ):
        if not isinstance( other, opMul ) and isinstance( other, sympy.core.mul.Mul ):
            other = opMul( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.mul.Mul.__hash__


class opPow( AlgebraicOperation, Pow ):

    def __new__( cls, *args, **kwargs ):
        if len( args ) > 1 and sympify( args[1] ) is S.Zero:
            arg = _top_priority_arg( args[0], args[1] )
            return getattr( arg, '_pow_handler', _no_handler )( args[0], args[1] )
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
            other = opPow( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.power.Pow.__hash__


class opExpr( Expr ):

    @property
    def _add_handler( self ):
        return opAdd

    @property
    def _mul_handler( self ):
        return opMul

    @property
    def _pow_handler( self ):
        return opPow

    def __radd__( self, other, *args, **kwargs ):
        return opAdd( other, self, *args, **kwargs )

    def __add__( self, *args, **kwargs ):
        return opAdd( self, *args, **kwargs )

    def __mul__( self, *args, **kwargs ):
        return opMul( self, *args, **kwargs )

    def __rmul__( self, other, *args, **kwargs ):
        return opMul( other, self, *args, **kwargs )

    def __pow__( self, *args, **kwargs ):
        return opPow( self, *args, **kwargs )


def _set_evalf_entry():
    """ Add the evalf processor functions to the global table """
    from sympy.core.evalf import evalf_table, evalf_add, evalf_mul, evalf_pow
    global evalf_table
    evalf_table[opAdd] = evalf_add
    evalf_table[opMul] = evalf_mul
    evalf_table[opPow] = evalf_pow


_set_evalf_entry()
