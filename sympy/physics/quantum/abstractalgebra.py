""" Classes for abstract algebras such as Fields or Operator Algebras

    AbstractAlgebra: base class for the algebra
    opExpr: elements of the Field
    opAdd: addition operator for the Field; assumed to be commutative and associative
    opMul: multiplication operator for the Field; assumed to be non-commutative
    opPow: variant of opMul. Raises Exception if exp <= 0 and inverse does not exist
    opSymbol: abstract element of the Field based on Symbol
    op_symbols: function to return a list opSymbol similar to symbols function

"""

from sympy.core.expr import Expr
import sympy.core.add
import sympy.core.mul
import sympy.core.power

from sympy.core.basic import ordering_of_classes


def _all_priority_args( *args, **kwargs ):
    all_args = []
    for o in args:
        if hasattr( o, 'args' ) and len( o.args ):
            all_args.extend( _all_priority_args( *o.args ) )
        if hasattr( o, '_op_priority' )  and type( o ) is not AbstractAlgebra:
            all_args.append( o )
    return all_args


def _args_top_priority( self, *args, **kwargs ):
    return max( 10.0, *[x._op_priority for x in _all_priority_args( *self.args, *args )] )


def _top_priority_arg( self, *args, **kwargs ):
    all_args = _all_priority_args( self, *args )
    priority = max( 10.0, *( [x._op_priority for x in all_args] ) )
    if getattr( self, '_op_priority', 0 ) > priority:
        return self
    arg = next( ( x for x in all_args if x._op_priority == priority ), None )
    return arg


def _get_unique_attrs( e, name, deep=True ):
    # Return a list of all methods from the args list matching name
    attrs = {}
    handled = opAdd, opMul, opPow
    if hasattr( e, 'args' ):
        for arg in e.args:
            if isinstance( arg, handled ):
                arg_attrs = _get_unique_attrs( arg, name )
                for arg_attr in arg_attrs:
                    attrs[arg_attr] = 1
            elif isinstance( arg, opExpr ) and hasattr( arg, name ):
                attrs[getattr( arg, name )] = 1
    return attrs.keys()


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


def _rebuild_expr( expr, deep=True ):
    """ Restore correct class for any expressions modified to contain core expressions

    This is a simplify helper function to restore any class improperly mapped to Add, Mul, Pow
    during simplification of composite expression

    """
    handled = opAdd, opMul, opPow
    if ( hasattr( expr, 'args' ) and deep ) or not isinstance( expr, handled ):
        if deep:
            sargs = [ _rebuild_expr( x, deep=deep ) for x in expr.args ]
        else:
            sargs = expr.args[::]
        arg = _top_priority_arg( expr, *sargs )
        if expr.is_Add:
            return getattr( arg, '_add_handler', sympy.core.add.Add )( *sargs )
        elif expr.is_Mul:
            return getattr( arg, '_mul_handler', sympy.core.mul.Mul )( *sargs )
        elif expr.is_Pow:
            return getattr( arg, '_pow_handler', sympy.core.power.Pow )( *sargs )
        elif isinstance( expr, AbstractAlgebra ):
            return expr.func( *sargs )
    return expr


class AbstractAlgebra( Expr ):
    """
    Base class for abstract algebras such as Fields or Operator Algebras

    Explanation
    ===========

    An AbstractAlgebra is class which supports operations chosen by the
    'call_highest_priority' decorator.  Operations derived from this
    class will adopt the highest _op_priority of all arguments
    and will choose the first argument with the highest priority to
    handle the call. Custom subclasses that want to define their
    own binary special methods should set an _op_priority value
    that is higher than the default.

    Notes
    =====

    NOTE on _op_priority from base.core.expr.Expr

        ***************
        * Arithmetics *
        ***************
        Expr and its subclasses use _op_priority to determine which object
        passed to a binary special method (__mul__, etc.) will handle the
        operation. In general, the 'call_highest_priority' decorator will choose
        the object with the highest _op_priority to handle the call.
        Custom subclasses that want to define their own binary special methods
        should set an _op_priority value that is higher than the default.

        **NOTE**:
        This is a temporary fix, and will eventually be replaced with
        something better and more powerful.  See issue 5510.

    Note on MutableDenseMatrix

        The MutableDenseMatrix does not inherit from Expr and will
        be excluded from the search for highest priority arguments.

    Note on sympy.core.function.Function
        The class Function does not inspect arguments for the _op_priority
        of arguments so operations on them may exit an Operator Algebra
        and revert to a field of Real or Complexes.

    Note on sympy.simplify.symplify
        The simplification function and helpers will force many returns to the core
        operators (Add, Mul, Pow). After simplification expressions will need to
        be restored to elements of the Algebra. (see _rebuild_expr)

    See Also
    ========

    sympy.core.basic.Expr
    sympy.matrices.MutableDenseMatrix
    sympy.core.

    """
    # _op_priority = 15.0

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
        """ Return -1, 0, 1 if the object is less than, equal, greater than """

        # basic._cmp_name does not allow easy addition to the
        # ordering of classes so do comparison here if x or y is
        # algebraic operation
        from sympy.core.basic import Basic
        UNKNOWN = len( ordering_of_classes ) + 1
        i1 = getattr( self, '_class_order', None )
        if i1 is None:
            n1 = self.__class__.__name__
            try:
                i1 = ordering_of_classes.index( n1 )
            except ValueError:
                i1 = UNKNOWN

        i2 = getattr( other, '_class_order', None )
        if i2 is None:
            n2 = other.__class__.__name__
            try:
                i2 = ordering_of_classes.index( n2 )
            except ValueError:
                i2 = UNKNOWN

        if i1 == UNKNOWN and i2 == UNKNOWN:
            c = ( n1 > n2 ) - ( n1 < n2 )
        else:
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

    # def __repr__( self ):
    #     repr = super().__repr__()
    #     return repr

    def simplify( self, *args, **kwargs ):
        return self.__eval_simplify( *args, **kwargs )

    def __eval_simplify( self, *args, **kwargs ):
        expr = self
        if hasattr( self, 'args' ):
            sfuncs = _get_unique_attrs( self, '_eval_simplify', deep=True )
            for sfunc in sfuncs:
                expr = sfunc( expr, *args, **kwargs )

        # Avoid infinite recursion with _eval_simplify
        expr = Expr.simplify( expr, **kwargs )
        # Rebuild expression for proper classes

        expr = _rebuild_expr( expr, deep=True )
        return expr


from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow
from sympy import sympify
from sympy.core.singleton import S


class opExpr( AbstractAlgebra ):

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


from sympy.core.symbol import Symbol, symbols


class opSymbol( Symbol, opExpr ):
    """ Symbol class to ensure symbols remain in the Ring """
    # Add property to support operator compare since adding
    # the new class name to the ordering_of_classes list in basic
    _class_order = ordering_of_classes.index( 'Symbol' )


def op_symbols( names, *args, cls=Symbol, **kwargs ):
    retvals = symbols( names, *args, cls=opSymbol, **kwargs )
    return retvals


class opAdd( AbstractAlgebra, Add ):
    # Note from sympy.core.basic:
    # ===========================
    #     If a class that overrides __eq__() needs to retain the
    #     implementation of __hash__() from a parent class, the
    #     interpreter must be told this explicitly by setting
    #     __hash__ : Callable[[object], int] = <ParentClass>.__hash__.
    #     Otherwise the inheritance of __hash__() will be blocked,
    #     just as if __hash__ had been explicitly set to None.

    _class_order = ordering_of_classes.index( 'Add' )
    precedence = 40

    def __new__( cls, *args, **kwargs ):
        cls = Add
        for arg in args:
            if isinstance( arg, AbstractAlgebra ):
                cls = opAdd
                break
        return Add.__new__( cls, *args, **kwargs )

    def __eq__( self, other ):
        if not isinstance( other, opAdd ) and isinstance( other, sympy.core.add.Add ):
            other = opAdd( *other.args )
        return super().__eq__( other )

    __hash__ = sympy.core.add.Add.__hash__


class opMul( AbstractAlgebra, Mul ):

    _class_order = ordering_of_classes.index( 'Mul' )
    precedence = 50

    def __new__( cls, *args, **kwargs ):
        cls = Mul
        for arg in args:
            if isinstance( arg, AbstractAlgebra ):
                cls = opMul
                break
        return Mul.__new__( cls, *args, **kwargs )

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


class opPow( AbstractAlgebra, Pow ):

    _class_order = ordering_of_classes.index( 'Pow' )
    precedence = 60

    def __new__( cls, *args, **kwargs ):
        if len( args ) > 1 and sympify( args[1] ) is S.Zero:
            arg = _top_priority_arg( args[0], args[1] )
            pow_handler = getattr( arg, '_pow_handler', _no_handler )
            if pow_handler is not opPow:
                return pow_handler( args[0], args[1] )
        obj = Pow.__new__( cls, *args, **kwargs )
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
