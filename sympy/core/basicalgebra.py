""" Manage the necessary attributes to define an Abstract Algebra

   BasicAlgebra:  class with properties necessary to define an abstract algebra
       _op_prioirty: Manage _op_priority for the algebra. Will contain the highest
                      value of _op_priority from all args
        __add__, __mul__, .... :
    No Handlers:  That's just for dispatchers
       _add_handler: _add_handler from the highest priority argument with
                      the attribute defined
       _mul_handler: _mul_handler from the highest priority argument with
                      the attribute defined
       _pow_handler: _pow_handler from the highest priority argument with
                      the attribute defined


    See Also
    ========

    AbstractAlgebra

"""
# from sympy.core.add import Add
# from sympy.core.mul import Mul
# from sympy.core.power import Pow


# def _no_handler( *args, **kwargs ):
#     return NotImplemented
#
#
# def _all_priority_args( *args, **kwargs ):
#     all_args = []
#     for o in args:
#         algebra = getattr( o, 'algebra', None )
#         if algebra is None:
#             if hasattr( o, 'args' ) and len( o.args ):
#                 all_args.extend( _all_priority_args( *o.args ) )
#             if hasattr( o, '_op_priority' ):
#                 all_args.append( o )
#         else:
#             all_args.append( o )
#     return all_args
#
#
# def _top_priority_arg( *args, **kwargs ):
#     all_args = _all_priority_args( *args )
#     if len( all_args ):
#         if len( all_args ) == 1:
#             return all_args[0]
#         priority = max( 10.0, *( [x._op_priority for x in all_args] ) )
#         # if getattr( self, '_op_priority', 0 ) > priority:
#         #     return self
#         arg = next( ( x for x in all_args if x._op_priority == priority ), None )
#         return arg
#     # return self
#
#
# def get_algebra( *args, **kwargs ):
#     if len( args ):
#         arg = _top_priority_arg( *args )
#         if arg is not None:
#             algebra = getattr( arg, 'algebra', None )
#             if algebra is not None:
#                 return algebra
#
#             is_AbstractAlgebra = getattr( arg, '_op_priority', 10 ) > 100
#             if is_AbstractAlgebra:
#                 return getattr( arg, 'algebra',
#                                BasicAlgebra( _op_priority=getattr( arg, '_op_priority', 10.0 ),
#                                              _add_handler=getattr( arg, '_add_handler', Add ),
#                                              _mul_handler=getattr( arg, '_mul_handler', Mul ),
#                                              _pow_handler=getattr( arg, '_pow_handler', Pow ),
#                                              is_AbstractAlgebra=True )
#                                )
#
#
# def check_algebra( cls, *args, **kwargs ):
#     """ Retrieve an abstract algebra and compute result if a handler is defined.
#
#         Handlers should return NotImplemented to invoke the core operations of Add, Mul, Pow.
#         Directly calling the core operations will result in a recursion error.
#         None is a valid return value.
#     """
#     algebra = get_algebra( *args, **kwargs )
#     if algebra is None:
#         return ( NotImplemented, None )
#
#     # Compute expression if any embedded handlers are not the core Add, Mul, Pow
#     # Any handler that wishes to return control the core operations should return NotImplemented
#     #     calling the core operations Add, Mul, Pow directly will cause recursion errors.
#     return ( NotImplemented, algebra )
#
#     if isinstance( cls, Add ):
#         handler = getattr( algebra, '_add_handler', _no_handler )
#         if handler == Add:
#             return ( NotImplemented, algebra )
#         else:
#             return ( handler( cls, *args, **kwargs ), algebra )
#     if isinstance( cls, Mul ):
#         handler = getattr( algebra, '_mul_handler', _no_handler )
#         if handler == Mul:
#             return ( NotImplemented, algebra )
#         else:
#             return ( handler( cls, *args, **kwargs ), algebra )
#     if isinstance( cls, Pow ):
#         handler = getattr( algebra, '_pow_handler', _no_handler )
#         if handler == Pow:
#             return ( NotImplemented, algebra )
#         else:
#             return ( handler( cls, *args, **kwargs ), algebra )


class BasicAlgebra:

    # __slots__ = ( '__op_priority', '__add_handler', '__mul_handler', '__pow_handler',
    #               '__is_AbstractAlgebra' )

    __slots__ = ( '_op_priority', '__mul__', '__add__', '__pow__', '_pow',
                  '__radd__', '__rmul__',  )

    # @property
    # def is_AbstractAlgebra( self ):
    #     return self.__is_AbstractAlgebra
    #
    # @property
    # def _op_priority( self ):
    #     return self.__op_priority
    #
    # @_op_priority.setter
    # def _op_priority( self, value ):
    #     self.__op_priority = value
    #
    # @property
    # def _add_handler( self ):
    #     return self.__add_handler
    #
    # @_add_handler.setter
    # def _add_handler( self, value ):
    #     self.__add_handler = value
    #
    # @property
    # def _mul_handler( self ):
    #     return self.__mul_handler
    #
    # @_mul_handler.setter
    # def _mul_handler( self, value ):
    #     self.__mul_handler = value
    #
    # @property
    # def _pow_handler( self ):
    #     return self.__pow_handler
    #
    # @_pow_handler.setter
    # def _pow_handler( self, value ):
    #     self.__pow_handler = value

    def __init__( self, _op_priority=10, __add__=None, __mul__=None, __pow__=None,
                  _pow=None, __radd__=None, __rmul__=None, ):
        self._op_priority = _op_priority
        if __add__ is not None:
            self.__add__ = __add__
        if __mul__ is not None:
            self.__mul__ = __mul__
        if __pow__ is not None:
            self.__pow__ = __pow__
        if _pow is not None:
            self._pow = _pow

    # def _hashable_content( self ):
    #     return ( self._op_priority, self._add_handler, self._mul_handler, self._pow_handler,
    #              self.is_AbstractAlgebra, )
