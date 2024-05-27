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


class BasicAlgebra:

    __slots__ = ( '__op_priority', '__add_handler', '__mul_handler', '__pow_handler', )

    @property
    def _op_priority( self ):
        return self.__op_priority

    @_op_priority.setter
    def _op_priority( self, value ):
        if not isinstance( value, ( float, int ) ):
            raise ValueError( f'_op_priority must be float or integer; found {type(value)}' )
        self.__op_priority = value

    @property
    def _add_handler( self ):
        return self.__add_handler

    @_add_handler.setter
    def _add_handler( self, value ):
        if not isinstance( value, Expr ):
            raise TypeError( '_add_handler must be subclass of Expr; found {type(value)}' )
        self.__add_handler = value

    @property
    def _mul_handler( self ):
        return self.__mul_handler

    @_mul_handler.setter
    def _mul_handler( self, value ):
        if not isinstance( value, Expr ):
            raise TypeError( '_mul_handler must be subclass of Expr; found {type(value)}' )
        self.__mul_handler = value

    @property
    def _pow_handler( self ):
        return self.__pow_handler

    @_pow_handler.setter
    def _pow_handler( self, value ):
        if not isinstance( value, Expr ):
            raise TypeError( '_pow_handler must be subclass of Expr; found {type(value)}' )
        self.__pow_handler = value

    def __init__( self, *args, **kwargs ):
        self.__op_priority = kwargs.get( '_op_priority', 10.0 )
        self.__add_handler = kwargs.get( '_add_handler', Add )
        self.__mul_handler = kwargs.get( '_mul_handler', Mul )
        self.__pow_handler = kwargs.get( '_pow_handler', Pow )
