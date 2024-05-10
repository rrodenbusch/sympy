from .expr import Expr
from .singleton import S


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


class BinaryMethod( Expr ):
    """
    A binary special method (__mul__, etc.).

    Explanation
    ===========

    A binary special method is class which can be chosen by the
    'call_highest_priority' decorator.  A BinaryMethod will adopt
    the _op_priority of the argument with the highest _op_priority
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
        if not hasattr(arg,'_add_handler'):
            return NotImplemented
        handler = arg._add_handler
        retval = handler( self, other )
        # retval2 = self._top_priority_arg().__mul__( other )
        return retval

    def __mul__( self, other ):
        arg = _top_priority_arg( self, other  )
        if not hasattr(arg,'_mul_handler'):
            return NotImplemented

        handler = arg._mul_handler
        retval = handler( self, other )
        # retval2= self._top_priority_arg().__mul__( other )
        return retval

    def _pow( self, other ):
        arg = _top_priority_arg( self, other, handler='_pow_handler' )
        if not hasattr(arg,'_pow_handler'):
            return NotImplemented
        handler = arg._pow_handler
        retval = handler( self, other )
        # retval2 = self._top_priority_arg()._pow( other )
        return retval

    # def _top_priority_add( self, other ):
    #     return self._top_priority_arg().__add__( other )
    #
    # def _top_priority_radd( self, other ):
    #     return self._top_priority_arg().__radd__( other )
    #
    # def _top_priority_sub( self, other ):
    #     return self._top_priority_arg().__sub__( other )
    #
    # def _top_priority_rsub( self, other ):
    #     return self._top_priority_arg().__rsub__( other )
    #
    # def _top_priority_mul( self, other ):
    #     return self._top_priority_arg().__mul__( other )
    #
    # def _top_priority_rmul( self, other ):
    #     return self._top_priority_arg().__rmul__( other )
    #
    # def _top_priority_pow( self, other ):
    #     return self._top_priority_arg()._pow( other )
    #
    # def _top_priority_rpow( self, other ):
    #     return self._top_priority_arg().__rpow__( other )
    #
    # def _top_priority_truediv( self, other ):
    #     denom = other ** S.NegativeOne
    #     if self is S.One:
    #         return denom
    #     else:
    #         return self._top_priority_mul( denom )
    #
    # def _top_priority_rtruediv( self, other ):
    #     denom = self ** S.NegativeOne
    #     if other is S.One:
    #         return denom
    #     else:
    #         return other * denom
    #
    # def _top_priority_mod( self, other ):
    #     return self._top_priority_mod( other )
    #
    # def _top_priority_rmod( self, other ):
    #     return self._top_priority_arg().__rmod__( other )
    #
    # def _top_priority_floordiv( self, other ):
    #     return self._top_priority_arg().__floordiv__( other )
    #
    # def _top_priority_rfloordiv( self, other ):
    #     return self._top_priority_arg().__rfloordiv__( other )
    #
    # def _top_priority_divmod( self, other ):
    #     return self._top_priority_arg().__divmod__( other )
    #
    # def _top_priority_rdivmod( self, other ):
    #     return self._top_priority_arg().__rdivmod__( other )

    # def __radd__( self, other ):
    #     return self._top_priority_arg().__radd__( other )
    #
    # def __sub__( self, other ):
    #     return self._top_priority_arg().__sub__( other )
    #
    # def __rsub__( self, other ):
    #     return self._top_priority_arg().__rsub__( other )

    # def __rmul__( self, other ):
    #     return self._top_priority_arg().__rmul__( other )

    # def __pow__( self, other, mod=None ) -> Expr:
    #     if mod is None:
    #         return self._pow( other )

    # def __rpow__( self, other ):
    #     return self._top_priority_arg().__rpow__( other )
    #
    # def __truediv__( self, other ):
    #     denom = other ** S.NegativeOne
    #     if self is S.One:
    #         return denom
    #     else:
    #         return self._top_priority_arg().__mul__( denom )
    #
    # def __rtruediv__( self, other ):
    #     denom = self._top_priority_arg()._pow( S.NegativeOne )
    #     if other is S.One:
    #         return denom
    #     else:
    #         return self ** denom
    #
    # def __mod__( self, other ):
    #     return self._top_priority_arg().__mod__( other )
    #
    # def __rmod__( self, other ):
    #     return  self._top_priority_arg().__rmod__( other )
    #
    # def __floordiv__( self, other ):
    #     return self._top_priority_arg().__floordiv__( other )
    #
    # def __rfloordiv__( self, other ):
    #     return self._top_priority_arg().__rfloordiv__( other )
    #
    # def __divmod__( self, other ):
    #     return self._top_priority_arg().__divmod__( other )
    #
    # def __rdivmod__( self, other ):
    #     return self._top_priority_arg().__rdivmod__( other )

