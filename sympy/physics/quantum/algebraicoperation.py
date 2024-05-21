from sympy.core.expr import Expr
import sympy.core.add
import sympy.core.mul
import sympy.core.power

from sympy.core.basic import ordering_of_classes


def _all_args( *args, **kwargs ):
    all_args = []
    for o in args:
        if hasattr( o, 'args' ) and len( o.args ):
            all_args.extend( _all_args( *o.args ) )
        if hasattr( o, '_op_priority' )  and type( o ) is not AlgebraicOperation:
            all_args.append( o )
    return all_args


def _args_top_priority( self, *args, **kwargs ):
    return max( 10.0, *[x._op_priority for x in _all_args( *self.args, *args )] )


def _top_priority_arg( self, *args, **kwargs ):
    all_args = _all_args( self, *args )  # *self.args vs self
    priority = max( 10.0, *list( [x._op_priority for x in all_args] ) )
    if getattr( self, '_op_priority', 0 ) > priority:
        return self
    arg = next( ( x for x in all_args if x._op_priority == priority ), None )
    return arg


def _no_handler( *args, **kwargs ):
    return NotImplemented


def binary_op_wrapper( self, other, method_name=None, default=None ):
    if hasattr( other, '_op_priority' ):
        if other._op_priority > self._op_priority:
            f = getattr( other, method_name, default )
            if f is not None:
                return f
    f = getattr( self, method_name, default )
    return f


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
    _op_priority = 15.0

    # @property
    # def identity(self):
    #     return self._identity
    # @identity.setter
    # def identity(self, value):
    #     self._identity = value

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

    def __neg__( self ):
        arg = _top_priority_arg( self, )
        return getattr( arg, '_mul_handler', _no_handler )( S.NegativeOne, self )

    def __add__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_add_handler', _no_handler )( self, other )

    def __radd__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_add_handler', _no_handler )( other, self )

    def __sub__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_add_handler', _no_handler )( self, -other )

    def __rsub__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_add_handler', _no_handler )( other, -self )

    def __mul__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_mul_handler', _no_handler )( self, other )

    def __rmul__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_mul_handler', _no_handler )( other, self )

    def _pow( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_pow_handler', _no_handler )( self, other )

    def __pow__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_pow_handler', _no_handler )( self, other )

    def __rpow__( self, other ):
        arg = _top_priority_arg( self, other )
        return getattr( arg, '_pow_handler', _no_handler )( other, self )

    def __truediv__( self, other ):
        # if other is S.One:
        #     return self
        arg = _top_priority_arg( self, other )
        denom = getattr( arg, '_pow_handler', _no_handler )( other, S.NegativeOne )
        if self is S.One:
            return denom
        else:
            return getattr( arg, '_mul_handler', _no_handler )( self, denom )

    def __rtruediv__( self, other ):
        arg = _top_priority_arg( self, other )
        denom = getattr( arg, '_pow_handler', _no_handler )( self, S.NegativeOne )
        if other is S.One:
            return denom
        else:
            return getattr( arg, '_mul_handler', _no_handler )( other, denom )

    # Methods from Expr (__pos__, __abs__, __mod__, __rmod__, __floordiv__, __rfloordiv__, __divmod__, __rdivmod__ )

    def compare( self, other ):
        # basic._cmp_name does not allow easy addition to the
        # ordering of classes so do comparison here if x or y is
        # algebraic operation
        from sympy.core.basic import Basic
        i1 = getattr( self, '_class_order', None )
        if i1 is None:
            n1 = self.__class__.__name__
            try:
                i1 = ordering_of_classes.index( n1 )
            except ValueError:
                i1 = len( ordering_of_classes ) + 1

        i2 = getattr( other, '_class_order', None )
        if i2 is None:
            n2 = other.__class__.__name__
            try:
                i2 = ordering_of_classes.index( n2 )
            except ValueError:
                i2 = len( ordering_of_classes ) + 1

        c = ( i1 > i2 ) - ( i1 < i2 )
        if c:
            return c

        st = self._hashable_content()
        ot = other._hashable_content()
        c = ( len( st ) > len( ot ) ) - ( len( st ) < len( ot ) )
        if c:
            return c
        for l, r in zip( st, ot ):
            l = Basic( *l ) if isinstance( l, frozenset ) else l
            r = Basic( *r ) if isinstance( r, frozenset ) else r
            if isinstance( l, Basic ):
                c = l.compare( r )
            else:
                c = ( l > r ) - ( l < r )
            if c:
                return c
        return 0

    # Expr evaluation hint methods.  Calls Expr._eval_expand_'hint'
    def _eval_add( self, other ):
        return opAdd( self, other, evaluate=False )

    def _eval_mul( self, other ):
        return opMul( self, other, evaluate=False )

    def _eval_power( self, e ):
        return opPow( self, e, evaluate=False )

    def collect( self, syms, *args, **kwargs ):
        arg = _top_priority_arg( self )
        return getattr( arg, '_collect_handler', _no_handler )( self, syms, *args, **kwargs )

    def __repr__( self ):
        repr = super().__repr__()
        return repr


from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow
from sympy import sympify
from sympy.core.singleton import S


# AlgebraicOperation
class opExpr( AlgebraicOperation ):

    @property
    def _op_priority( self ):
        return 20.0  # Above basic, matrices, algebraic operators, but below opAdd, opMul,

    def __radd__( self, other, *args, **kwargs ):
        return opAdd( other, self, *args, **kwargs )

    def __add__( self, *args, **kwargs ):
        return opAdd( self, *args, **kwargs )

    def __sub__( self, other ):
        obj = opAdd( self, -other )
        return obj

    def __rsub__( self, other ):
        obj = opAdd( other, -self )
        return obj

    def __neg__( self ):
        # Mul has its own __neg__ routine, so we just
        # create a 2-args Mul with the -1 in the canonical
        # slot 0.
        c = self.is_commutative
        obj = opMul._from_args( ( S.NegativeOne, self ), c )
        return obj

    def __mul__( self, *args, **kwargs ):
        return opMul( self, *args, **kwargs )

    def __rmul__( self, other, *args, **kwargs ):
        return opMul( other, self, *args, **kwargs )

    def __pow__( self, *args, **kwargs ):
        return opPow( self, *args, **kwargs )


from sympy.core.basic import Atom
from sympy.core.symbol import Symbol, symbols


class opSymbol( Symbol, opExpr ):
    """ Symbol class to ensure symbols remain in the Ring """
    # Add property to support operator compare since adding
    # the new class name to the ordering_of_classes list in basic
    _class_order = ordering_of_classes.index( 'Symbol' )


def op_symbols( names, *args, cls=Symbol, **kwargs ):
    retvals = symbols( names, *args, cls=opSymbol, **kwargs )
    return retvals


class opAdd( AlgebraicOperation, Add ):
    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.

    _class_order = ordering_of_classes.index( 'Add' )

    def __eq__( self, other ):
        if not isinstance( other, opAdd ) and isinstance( other, sympy.core.add.Add ):
            other = opAdd( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.add.Add.__hash__


class opMul( AlgebraicOperation, Mul ):

    _class_order = ordering_of_classes.index( 'Mul' )

    # _args_type = opExpr
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

    _class_order = ordering_of_classes.index( 'Pow' )

    def __new__( cls, *args, **kwargs ):
        if len( args ) > 1 and sympify( args[1] ) is S.Zero:
            arg = _top_priority_arg( args[0], args[1] )
            pow_handler = getattr( arg, '_pow_handler', _no_handler )
            if pow_handler is not opPow:
                return pow_handler( args[0], args[1] )
        obj = super().__new__( cls, *args, **kwargs )
        return obj

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


def _set_evalf_entry():
    """ Add the evalf processor functions to the global table """
    from sympy.core.evalf import evalf_table, evalf_add, evalf_mul, evalf_pow
    global evalf_table
    evalf_table[opAdd] = evalf_add
    evalf_table[opMul] = evalf_mul
    evalf_table[opPow] = evalf_pow


_set_evalf_entry()
