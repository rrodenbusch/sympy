""" Manage the necessary attributes to define an Abstract Algebra


    See Also
    ========



"""
from .expr import Expr

class AlgebraicOp(Expr):
    """ Manage the internals of the Add, Mul and Pow operations """
    @property
    def _op_priority(self):
        if self.algebra is not None:
            return self.algebra._op_priority
        return super()._op_priority

    # Add and Mul are AssocOps which accept kwargs _sympify and evaluate; pass them along
    def __add__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(self, other, algebra=self.algebra)
        return super().__add__(other, **kwargs)

    def __radd__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(other, self, algebra=self.algebra)
        return super().__radd__(other, **kwargs)

    def __sub__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(self, -other, algebra=self.algebra)
        return super().__sub__(other, **kwargs)

    def __rsub__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__add__', None)
            if _handler is not None:
                return _handler(other, -self, algebra=self.algebra)
        return super().__rsub__(other, **kwargs)

    def __mul__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__mul__', None)
            if _handler is not None:
                return _handler(self, other, algebra=self.algebra)
        return super().__mul__(other, **kwargs)

    def __rmul__(self, other, **kwargs):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__mul__', None)
            if _handler is not None:
                return _handler(other, self, algebra=self.algebra)
        return super().__rmul__(other, **kwargs)

    def __pow__(self, other, mod=None):
        if self.algebra is not None:
            _handler = getattr(self.algebra, '__pow__', None)
            if _handler is not None:
                return _handler(self, other, algebra=self.algebra)
        return super().__pow__(other, mod=mod)


class BasicAlgebra:
    """ Configuration of the algebra for use by Add, Mul, Pow operations """
    __slots__ = ( '_op_priority', '__mul__', '__add__', '__pow__', '_pow',
                  '__radd__', '__rmul__',  )

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

class AbstractExpr(type):
    """ Metaclass to create and save the algebra for operators usage """

    # def __call__(self):
    #    # Create and then inspect the instance to setup the algebra configuration
    #     pass

    pass