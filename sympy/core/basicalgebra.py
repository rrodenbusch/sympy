""" Manage the necessary attributes to define an Abstract Algebra

   BasicAlgebra:  class with properties necessary to define an abstract algebra
       _op_prioirty: Manage _op_priority for the algebra. Will contain the highest
                      value of _op_priority from all args
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
from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow


def _no_handler( *args, **kwargs ):
    return NotImplemented

def default_algebra():
    return BasicAlgebra(10, Add, Mul, Pow, False )

""" TODO:
  if argument has an algebra, no need to inspect it's args
"""
def _all_priority_args( *args, **kwargs ):
    all_args = []
    for o in args:
        if hasattr( o, 'args' ) and len( o.args ):
            all_args.extend( _all_priority_args( *o.args ) )
        # if hasattr( o, '_op_priority' )  and type( o ) is not AbstractAlgebra:
        if hasattr( o, '_op_priority' ):
            all_args.append( o )
    return all_args


def _top_priority_arg( self, *args, **kwargs ):
    all_args = _all_priority_args( self, *args )
    if len(all_args):
        priority = max( 10.0, *( [x._op_priority for x in all_args] ) )
        if getattr( self, '_op_priority', 0 ) > priority:
            return self
        if len(all_args) == 1:
            return all_args[0]
        arg = next( ( x for x in all_args if x._op_priority == priority ), None )
        return arg
    return self


def check_algebra( cls, *args, **kwargs ):
    """ Define the abstract algebra and compute result if an abstract algebra is returned
    """
    algebra = get_algebra( *args, **kwargs )
    if algebra is None:
        return ( NotImplemented, None )

    # Compute expression if any embedded handlers are not the core Add, Mul, Pow
    # Any handler that wishes to return control the core operations should return NotImplemented
    # skipped = [Add, Mul, Pow]
    return ( NotImplemented, algebra )

    # # Calculate from the handler and return
    # if cls is Add or isinstance( cls, Add ):
    #     pass
    # if cls is Mul or isinstance( cls, Mul ):
    #     pass
    # if cls is Pow or isinstance( cls, Pow ):
    #     pass
    # return ( NotImplemented, algebra )



def get_algebra( *args, **kwargs ):
    """ TODO: Need to make sure that the attributes are an AbstractAlgebra,
            otherwise return None so it is default operations """
    if len( args ):
        arg = _top_priority_arg( *args )
        is_AbstractAlgebra=getattr( arg, '_op_priority', 10 ) > 100
        if is_AbstractAlgebra:
            return getattr(arg, 'algebra',
                           BasicAlgebra( _op_priority=getattr( arg, '_op_priority', 10.0 ),
                                         _add_handler=getattr( arg, '_add_handler', Add ),
                                         _mul_handler=getattr( arg, '_mul_handler', Mul ),
                                         _pow_handler=getattr( arg, '_pow_handler', Pow ),
                                         is_AbstractAlgebra=True )
                           )

class BasicAlgebra:

    # __slots__ = ( '__op_priority', '__add_handler', '__mul_handler', '__pow_handler',
    #               '__is_AbstractAlgebra' )

    __slots__ = ( '_op_priority', '_add_handler', '_mul_handler', '_pow_handler',
                  'is_AbstractAlgebra' )


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

    def __init__( self, _op_priority=10, _add_handler=Add, _mul_handler=Mul, _pow_handler=Pow,
                  is_AbstractAlgebra = False ):
        self._op_priority = _op_priority
        self._add_handler = _add_handler
        self._mul_handler = _mul_handler
        self._pow_handler = _pow_handler
        self.is_AbstractAlgebra = is_AbstractAlgebra

    def _hashable_content(self):
        return ( self._op_priority, self._add_handler, self._mul_handler, self._pow_handler,
                 self.is_AbstractAlgebra, )
