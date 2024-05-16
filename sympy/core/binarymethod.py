from .expr import Expr


def _all_args( *args ):
    all_args = []
    for o in args:
        if hasattr( o, 'args' ) and len( o.args ):
            all_args.extend( _all_args( *o.args ) )
        if hasattr( o, '_op_priority' )  and not isinstance( o, BinaryMethod ):
            all_args.append( o )
    return all_args


def _args_top_priority( self, *args, **kwargs ):
    return max( 10.0, *[x._op_priority for x in _all_args( *self.args, *args )] )


def _top_priority_arg( self, *args, **kwargs ):
    all_args = _all_args( *self.args, *args )
    priority = max( 10.0, *[x._op_priority for x in all_args] )
    arg = next( ( x for x in all_args if x._op_priority == priority ), None )
    return arg


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

    The MutableDenseMatrix does not inherit from Expr and will
    be excluded from the search for highest priority arguments.

    See Also
    ========

    sympy.core.basic.Expr
    sympy.matrices.MutableDenseMatrix



    """

    @property
    def _op_priority( self ):
        return _args_top_priority( self )

    def __add__( self, other ):
        arg = _top_priority_arg( self, other )
        if not hasattr( arg, '_add_handler' ):
            return NotImplemented

        return arg._add_handler( self, other )

    def __mul__( self, other ):
        arg = _top_priority_arg( self, other )
        if not hasattr( arg, '_mul_handler' ):
            return NotImplemented

        return arg._mul_handler( self, other )

    def _pow( self, other ):
        arg = _top_priority_arg( self, other )
        if not hasattr( arg, '_pow_handler' ):
            return NotImplemented

        return arg._pow_handler( self, other )
