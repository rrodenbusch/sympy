"""Pauli operators and states"""

from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.numbers import I
from sympy.core.power import Pow
from sympy.core.singleton import S
from sympy.core.sympify import sympify
from sympy.core.expr import Expr
from sympy.core.function import Function
from sympy.core.symbol import Symbol
from sympy.functions.elementary.exponential import exp
from sympy.physics.quantum import Operator, Ket, Bra, IdentityOperator, Commutator
from sympy.physics.quantum import ComplexSpace
from sympy.matrices import Matrix, ImmutableMatrix
from sympy.functions.special.tensor_functions import KroneckerDelta

__all__ = [
    'SigmaI', 'SigmaX', 'SigmaY', 'SigmaZ', 'SigmaMinus', 'SigmaPlus', 'SigmaZKet',
    'SigmaZBra', 'qsimplify_pauli', 'qcollect_pauli',
]

from sympy.core.abstractalgebra import AbstractAlgebraMeta


class SigmaOpBase(Operator, metaclass=AbstractAlgebraMeta):
    """Pauli sigma operator, base class"""

    @property
    def name(self):
        return self.args[0]

    def dagger(self):  # New
        return self._eval_adjoint()

    def adjoint(self):  # New
        return self.dagger()

    def commute(self, other):  # New
        return Commutator(self, other)

    @property
    def suppress_evalf(self):  # New
        return self._suppress_evalf

    def _pauli_evalf(self, *args, **kwargs):  # Diff
        if self.suppress_evalf:
            return self

        return ImmutableMatrix (
            self._represent_default_basis(format=kwargs.get('format', 'sympy'))
            )

    @property
    def _eval_evalf(self, *args, **kwargs):  # New
        return self._pauli_evalf

    @property
    def use_name(self):
        return bool(self.args[0]) is not False or (self.args[0] == 0)

    @classmethod
    def default_args(self):
        return (False,)

    def __new__(cls, *args, **hints):
        _suppress_evalf = hints.pop('suppress_evalf', False)
        e = Operator.__new__(cls, *args, **hints)
        e._suppress_evalf = _suppress_evalf
        return e

    def _key(self):  # New
        return (self.__class__, self._suppress_evalf, *[x.__hash__() for x in self.args])

    def __hash__(self):  # New
        return hash(self._key())

    def _eval_commutator_BosonOp(self, other, **hints):
        return S.Zero

    def _eval_power(self, e):  # Moved up from each class
        if isinstance(self, SigmaI):
            return self
        elif e.is_Integer and e.is_positive:
            if int(e) % 2:
                return self
            else:
                return SigmaI(self.name)

    @staticmethod
    def _eval_collect(e, syms, *args, **kwargs):  # New
        return qcollect_pauli(e, syms, *args, **kwargs)

    def evalf(self, *args, **kwargs):  # New
        return self._pauli_evalf(self, *args, **kwargs)

    def _sympyrepr(self, printer, *args):  # New
        if self.use_name:
            return "%s(%s)" % (
                self.__class__.__name__, printer._print(self.args[0])
            )
        return "%s()" % (self.__class__.__name__)

    def _sympystr(self, printer, *args):  # New
        return self._sympyrepr(printer, *args)

    #=============  Abstract Algebra Definitions ============
    _op_priority = 200

    def __mul__(self, other, **kwargs):  # New
        if isinstance(other, SigmaI):
            return self
        kwargs['algebra'] = SigmaOpBase.algebra
        return Mul(self, other, **kwargs)

    def _pow(self, other, *args, **kwargs):
        if isinstance(self, SigmaI) or sympify(other) is S.Zero:
            if isinstance(self, SigmaOpBase):
                return(SigmaI(self.name))
            """ TODO: Need to check all args of base have the same name,
                    if name is same return SigmaI with that name,
                Otherwise raise exception NoInverseError
            """
            return SigmaI()
        return NotImplemented

    def __pow__(self, other, *args, **kwargs):  # New
        if isinstance(self, SigmaI) or sympify(other) is S.Zero:
            if isinstance(self, SigmaOpBase):
                return(SigmaI(self.name))
            """ TODO: Need to check all args of base have the same name,
                    if name is same return SigmaI with that name,
                Otherwise raise exception NoInverseError
            """
            return SigmaI()
        else:
            kwargs['algebra'] = SigmaOpBase.algebra
            return Pow(self, other, **kwargs)

    def collect(self, syms, *args, **kwargs):  # New
        from sympy.physics.quantum.collect import collect as qcollect

        return qcollect(self, syms, *args, **kwargs)

    def simplify(self, *args, **kwargs):
        from sympy import simplify

        kwargs['algebra'] = self.algebra
        expr = qsimplify_pauli(self, *args, **kwargs)
        expr = simplify(expr)
        expr.algebra = self.algebra
        return expr



class SigmaI(SigmaOpBase, IdentityOperator):
    """Pauli sigma Identity operator

    Parameters
    ==========

    name : str
        An optional string that labels the operator. Pauli operators with
        different names commute. SigmaI commutes with all operators

    Examples
    ========

    >>> from sympy.physics.quantum import represent
    >>> from sympy.physics.quantum.pauli import SigmaI
    >>> sI = SigmaI()
    >>> sI
    SigmaI()
    >>> represent(sI)
    Matrix([
    [1,  0],
    [0,  1]])
    """

    def __new__(cls, *args, **hints):
        return SigmaOpBase.__new__(cls, *args)

    def _eval_commutator_SigmaZ(self, other, **hints):
        return S.Zero

    def _eval_commutator_SigmaX(self, other, **hints):
        return S.Zero

    def _eval_commutator_SigmaY(self, other, **hints):
        return S.Zero

    def _eval_commutator_SigmaI(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaI(self, other, **hints):
        return 2 * other

    def _eval_anticommutator_SigmaX(self, other, **hints):
        return 2 * other

    def _eval_anticommutator_SigmaY(self, other, **hints):
        return 2 * other

    def _eval_anticommutator_SigmaZ(self, other, **hints):
        return 2 * other

    def _eval_adjoint(self):
        return self

    def _print_contents_latex(self, printer, *args):
        if self.use_name:
            return r'{\sigma_I^{(%s)}}' % str(self.name)
        else:
            return r'{\sigma_I}'

    def _print_contents(self, printer, *args):
        return 'SigmaI()'

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[1, 0], [0, 1]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')

class SigmaX(SigmaOpBase):
    """Pauli sigma x operator

    Parameters
    ==========

    name : str
        An optional string that labels the operator. Pauli operators with
        different names commute.

    Examples
    ========

    >>> from sympy.physics.quantum import represent
    >>> from sympy.physics.quantum.pauli import SigmaX
    >>> sx = SigmaX()
    >>> sx
    SigmaX()
    >>> represent(sx)
    Matrix([
    [0, 1],
    [1, 0]])
    """

    def __new__(cls, *args, **hints):
        return SigmaOpBase.__new__(cls, *args, **hints)

    def _eval_commutator_SigmaY(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return 2 * I * SigmaZ(self.name)

    def _eval_commutator_SigmaZ(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return -2 * I * SigmaY(self.name)

    def _eval_commutator_BosonOp(self, other, **hints):
        return S.Zero

    def _eval_commutator_SigmaI(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaI(self, other, **hints):
        return 2 * self

    def _eval_anticommutator_SigmaY(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaZ(self, other, **hints):
        return S.Zero

    def _eval_adjoint(self):
        return self

    def _print_contents_latex(self, printer, *args):
        if self.use_name:
            return r'{\sigma_x^{(%s)}}' % str(self.name)
        else:
            return r'{\sigma_x}'

    def _print_contents(self, printer, *args):
        return 'SigmaX()'

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[0, 1], [1, 0]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')


class SigmaY(SigmaOpBase):
    """Pauli sigma y operator

    Parameters
    ==========

    name : str
        An optional string that labels the operator. Pauli operators with
        different names commute.

    Examples
    ========

    >>> from sympy.physics.quantum import represent
    >>> from sympy.physics.quantum.pauli import SigmaY
    >>> sy = SigmaY()
    >>> sy
    SigmaY()
    >>> represent(sy)
    Matrix([
    [0, -I],
    [I,  0]])
    """

    def __new__(cls, *args, **hints):
        return SigmaOpBase.__new__(cls, *args)

    def _eval_commutator_SigmaZ(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return 2 * I * SigmaX(self.name)

    def _eval_commutator_SigmaX(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return -2 * I * SigmaZ(self.name)

    def _eval_commutator_SigmaI(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaI(self, other, **hints):
        return 2 * self

    def _eval_anticommutator_SigmaX(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaZ(self, other, **hints):
        return S.Zero

    def _eval_adjoint(self):
        return self

    def _print_contents_latex(self, printer, *args):
        if self.use_name:
            return r'{\sigma_y^{(%s)}}' % str(self.name)
        else:
            return r'{\sigma_y}'

    def _print_contents(self, printer, *args):
        return 'SigmaY()'

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[0, -I], [I, 0]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')


class SigmaZ(SigmaOpBase):
    """Pauli sigma z operator

    Parameters
    ==========

    name : str
        An optional string that labels the operator. Pauli operators with
        different names commute.

    Examples
    ========

    >>> from sympy.physics.quantum import represent
    >>> from sympy.physics.quantum.pauli import SigmaZ
    >>> sz = SigmaZ()
    >>> sz ** 3
    SigmaZ()
    >>> represent(sz)
    Matrix([
    [1,  0],
    [0, -1]])
    """

    def __new__(cls, *args, **hints):
        return SigmaOpBase.__new__(cls, *args)

    def _eval_commutator_SigmaX(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return 2 * I * SigmaY(self.name)

    def _eval_commutator_SigmaY(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return -2 * I * SigmaX(self.name)

    def _eval_commutator_SigmaI(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaI(self, other, **hints):
        return 2 * self

    def _eval_anticommutator_SigmaX(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaY(self, other, **hints):
        return S.Zero

    def _eval_adjoint(self):
        return self

    def _print_contents_latex(self, printer, *args):
        if self.use_name:
            return r'{\sigma_z^{(%s)}}' % str(self.name)
        else:
            return r'{\sigma_z}'

    def _print_contents(self, printer, *args):
        return 'SigmaZ()'

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[1, 0], [0, -1]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')


class SigmaMinus(SigmaOpBase):
    """Pauli sigma minus operator

    Parameters
    ==========

    name : str
        An optional string that labels the operator. Pauli operators with
        different names commute.

    Examples
    ========

    >>> from sympy.physics.quantum import represent, Dagger
    >>> from sympy.physics.quantum.pauli import SigmaMinus
    >>> sm = SigmaMinus()
    >>> sm
    SigmaMinus()
    >>> Dagger(sm)
    SigmaPlus()
    >>> represent(sm)
    Matrix([
    [0, 0],
    [1, 0]])
    """

    def __new__(cls, *args, **hints):
        return SigmaOpBase.__new__(cls, *args)

    def _eval_commutator_SigmaI(self, other, **hints):
        return S.Zero

    def _eval_commutator_SigmaX(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return -SigmaZ(self.name)

    def _eval_commutator_SigmaY(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return I * SigmaZ(self.name)

    def _eval_commutator_SigmaZ(self, other, **hints):
        return 2 * self

    def _eval_commutator_SigmaMinus(self, other, **hints):
        return SigmaZ(self.name)

    def _eval_anticommutator_SigmaI(self, other, **hints):
        return 2 * self

    def _eval_anticommutator_SigmaZ(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaX(self, other, **hints):
        return S.One

    def _eval_anticommutator_SigmaY(self, other, **hints):
        return I * S.NegativeOne

    def _eval_anticommutator_SigmaPlus(self, other, **hints):
        return S.One

    def _eval_adjoint(self):
        return SigmaPlus(self.name)

    def _eval_power(self, e):
        if e.is_Integer and e.is_positive:
            return S.Zero

    def _print_contents_latex(self, printer, *args):
        if self.use_name:
            return r'{\sigma_-^{(%s)}}' % str(self.name)
        else:
            return r'{\sigma_-}'

    def _print_contents(self, printer, *args):
        return 'SigmaMinus()'

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[0, 0], [1, 0]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')


class SigmaPlus(SigmaOpBase):
    """Pauli sigma plus operator

    Parameters
    ==========

    name : str
        An optional string that labels the operator. Pauli operators with
        different names commute.

    Examples
    ========

    >>> from sympy.physics.quantum import represent, Dagger
    >>> from sympy.physics.quantum.pauli import SigmaPlus
    >>> sp = SigmaPlus()
    >>> sp
    SigmaPlus()
    >>> Dagger(sp)
    SigmaMinus()
    >>> represent(sp)
    Matrix([
    [0, 1],
    [0, 0]])
    """

    def __new__(cls, *args, **hints):
        return SigmaOpBase.__new__(cls, *args)

    def _eval_commutator_SigmaI(self, other, **hints):
        return S.Zero

    def _eval_commutator_SigmaX(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return SigmaZ(self.name)

    def _eval_commutator_SigmaY(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return I * SigmaZ(self.name)

    def _eval_commutator_SigmaZ(self, other, **hints):
        if self.name != other.name:
            return S.Zero
        else:
            return -2 * self

    def _eval_commutator_SigmaMinus(self, other, **hints):
        return SigmaZ(self.name)

    def _eval_anticommutator_SigmaI(self, other, **hints):
        return 2 * self

    def _eval_anticommutator_SigmaZ(self, other, **hints):
        return S.Zero

    def _eval_anticommutator_SigmaX(self, other, **hints):
        return S.One

    def _eval_anticommutator_SigmaY(self, other, **hints):
        return I

    def _eval_anticommutator_SigmaMinus(self, other, **hints):
        return S.One

    def _eval_adjoint(self):
        return SigmaMinus(self.name)

    def _eval_mul(self, other):
        return self * other

    def _eval_power(self, e):
        if e.is_Integer and e.is_positive:
            return S.Zero

    def _print_contents_latex(self, printer, *args):
        if self.use_name:
            return r'{\sigma_+^{(%s)}}' % str(self.name)
        else:
            return r'{\sigma_+}'

    def _print_contents(self, printer, *args):
        return 'SigmaPlus()'

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[0, 1], [0, 0]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')


class SigmaZKet(Ket):
    """Ket for a two-level system quantum system.

    Parameters
    ==========

    n : Number
        The state number (0 or 1).

    """

    def __new__(cls, n):
        if n not in (0, 1):
            raise ValueError("n must be 0 or 1")
        return Ket.__new__(cls, n)

    @property
    def n(self):
        return self.label[0]

    @classmethod
    def dual_class(self):
        return SigmaZBra

    @classmethod
    def _eval_hilbert_space(cls, label):
        return ComplexSpace(2)

    def _eval_innerproduct_SigmaZBra(self, bra, **hints):
        return KroneckerDelta(self.n, bra.n)

    def _apply_from_right_to_SigmaZ(self, op, **options):
        if self.n == 0:
            return self
        else:
            return S.NegativeOne * self

    def _apply_from_right_to_SigmaI(self, op, **options):
        return self

    def _apply_from_right_to_SigmaX(self, op, **options):
        return SigmaZKet(1) if self.n == 0 else SigmaZKet(0)

    def _apply_from_right_to_SigmaY(self, op, **options):
        return I * SigmaZKet(1) if self.n == 0 else (-I) * SigmaZKet(0)

    def _apply_from_right_to_SigmaMinus(self, op, **options):
        if self.n == 0:
            return SigmaZKet(1)
        else:
            return S.Zero

    def _apply_from_right_to_SigmaPlus(self, op, **options):
        if self.n == 0:
            return S.Zero
        else:
            return SigmaZKet(0)

    def _represent_default_basis(self, **options):
        format = options.get('format', 'sympy')
        if format == 'sympy':
            return Matrix([[1], [0]]) if self.n == 0 else Matrix([[0], [1]])
        else:
            raise NotImplementedError('Representation in format ' +
                                      format + ' not implemented.')


class SigmaZBra(Bra):
    """Bra for a two-level quantum system.

    Parameters
    ==========

    n : Number
        The state number (0 or 1).

    """

    def __new__(cls, n):
        if n not in (0, 1):
            raise ValueError("n must be 0 or 1")
        return Bra.__new__(cls, n)

    @property
    def n(self):
        return self.label[0]

    @classmethod
    def dual_class(self):
        return SigmaZKet


def _qsimplify_pauli_product(a, b):
    """
    Internal helper function for simplifying products of Pauli operators.
    """
    if not (isinstance(a, SigmaOpBase) and isinstance(b, SigmaOpBase)):
        return Mul(a, b)

    if a.name != b.name:
        # Pauli matrices with different labels commute; sort by name
        if a.name < b.name:
            return Mul(a, b)
        else:
            return Mul(b, a)

    elif isinstance(a, SigmaI):

        if isinstance(b, SigmaI):
            return SigmaI(a.name)

        if isinstance(b, SigmaX):
            return SigmaX(a.name)

        if isinstance(b, SigmaY):
            return SigmaY(a.name)

        if isinstance(b, SigmaZ):
            return SigmaZ(a.name)

        if isinstance(b, SigmaMinus):
            return SigmaMinus(a.name)

        if isinstance(b, SigmaPlus):
            return SigmaPlus(a.name)

    elif isinstance(a, SigmaX):

        if isinstance(b, SigmaI):
            return SigmaX(a.name)

        if isinstance(b, SigmaX):
            return SigmaI(a.name)

        if isinstance(b, SigmaY):
            return I * SigmaZ(a.name)

        if isinstance(b, SigmaZ):
            return -I * SigmaY(a.name)

        if isinstance(b, SigmaMinus):
            return (SigmaI(a.name) + SigmaZ(a.name)) / 2

        if isinstance(b, SigmaPlus):
            return (SigmaI(a.name) - SigmaZ(a.name)) / 2

    elif isinstance(a, SigmaY):

        if isinstance(b, SigmaI):
            return SigmaY(a.name)

        if isinstance(b, SigmaX):
            return -I * SigmaZ(a.name)

        if isinstance(b, SigmaY):
            return SigmaI(a.name)

        if isinstance(b, SigmaZ):
            return I * SigmaX(a.name)

        if isinstance(b, SigmaMinus):
            return -I * (SigmaI(a.name) + SigmaZ(a.name)) / 2

        if isinstance(b, SigmaPlus):
            return I * (SigmaI(a.name) - SigmaZ(a.name)) / 2

    elif isinstance(a, SigmaZ):

        if isinstance(b, SigmaI):
            return SigmaZ(a.name)

        if isinstance(b, SigmaX):
            return I * SigmaY(a.name)

        if isinstance(b, SigmaY):
            return -I * SigmaX(a.name)

        if isinstance(b, SigmaZ):
            return SigmaI(a.name)

        if isinstance(b, SigmaMinus):
            return -SigmaMinus(a.name)

        if isinstance(b, SigmaPlus):
            return SigmaPlus(a.name)

    elif isinstance(a, SigmaMinus):

        if isinstance(b, SigmaI):
            return SigmaMinus(a.name)

        if isinstance(b, SigmaX):
            return (SigmaI(a.name) - SigmaZ(a.name)) / 2

        if isinstance(b, SigmaY):
            return -I * (SigmaI(a.name) - SigmaZ(a.name)) / 2

        if isinstance(b, SigmaZ):
            # (SigmaX(a.name) - I * SigmaY(a.name))/2
            return SigmaMinus(b.name)

        if isinstance(b, SigmaMinus):
            return S.Zero

        if isinstance(b, SigmaPlus):
            return (SigmaI(a.name) - SigmaZ(a.name)) / 2

    elif isinstance(a, SigmaPlus):

        if isinstance(b, SigmaI):
            return SigmaPlus(a.name)

        if isinstance(b, SigmaX):
            return (S.SigmaI(a.name) + SigmaZ(a.name)) / 2

        if isinstance(b, SigmaY):
            return I * (SigmaI(a.name) + SigmaZ(a.name)) / 2

        if isinstance(b, SigmaZ):
            # -(SigmaX(a.name) + I * SigmaY(a.name))/2
            return -SigmaPlus(a.name)

        if isinstance(b, SigmaMinus):
            return (SigmaI(a.name) + SigmaZ(a.name)) / 2

        if isinstance(b, SigmaPlus):
            return S.Zero

    else:
        return a * b


def qsimplify_pauli(e, *args, **kwargs):
    """
    Simplify an expression that includes products of pauli operators.

    Parameters
    ==========

    e : expression
        An expression that contains products of Pauli operators that is
        to be simplified.

    Examples
    ========

    >>> from sympy.physics.quantum.pauli import SigmaX, SigmaY
    >>> from sympy.physics.quantum.pauli import qsimplify_pauli
    >>> sx, sy = SigmaX(), SigmaY()
    >>> sx * sy
    SigmaX()*SigmaY()
    >>> qsimplify_pauli(sx * sy)
    I*SigmaZ()
    """
    if isinstance(e, Operator):
        return e

    if isinstance(e, (Add, Pow, exp)):
        t = type(e)
        return t(*(qsimplify_pauli(arg) for arg in e.args))

    if isinstance(e, Mul):

        c, nc = e.args_cnc()

        nc_s = []
        while nc:
            curr = nc.pop(0)

            while (len(nc) and
                   isinstance(curr, SigmaOpBase) and
                   isinstance(nc[0], SigmaOpBase) and
                   curr.name == nc[0].name):

                x = nc.pop(0)
                y = _qsimplify_pauli_product(curr, x)
                c1, nc1 = y.args_cnc()
                curr = Mul(*nc1)
                c = c + c1

            nc_s.append(curr)

        return Mul(*c) * Mul(*nc_s)

    return e


def qcollect_pauli(e, ops=None, *args, **kwargs):
    """
    Collect like terms in an expression containing the non-commutaive pauli operators.

    Parameters
    ==========

    e : expression
        An expression that contains Pauli operators that is
        to be simplified.
    ops : Optional[list] = all_operators
        An optional list of operators to collect

    Examples
    ========

    >>> from sympy import symbols
    >>> from sympy.physics.quantum.pauli import SigmaX, SigmaY
    >>> from sympy.physics.quantum.pauli import qcollect_pauli
    >>> sx, sy = SigmaX(), SigmaY()
    >>> (a,b,c,d) = symbols('a:d')
    >>> a*sx + b*sx + c*sy + d*sy
    a*SigmaX() + b*SigmaX() +c*SigmaY() + d*SigmaY()
    >>> qcollect_pauli(a*sx + b*sx + c*sy + d*sy)
    (a+b)*SigmaX() + (c+d)*SigmaY()
    """
    if isinstance(e, (Operator, Symbol)):
        return e

    if not isinstance(e, Add):
        if isinstance(e, (Expr, Function)):
            args = []
            for arg in e.args:
                args.append(qcollect_pauli(arg, ops))
            return type(e)(*args)
        else:
            return e

    all_ops = [SigmaI(), SigmaX(), SigmaY(), SigmaZ(), SigmaPlus(), SigmaMinus()]
    if ops is None or len(ops) == 0:
        ops = all_ops

    for op in ops:
        if not op in all_ops:
            raise ValueError(f'Operators to collect must be from {all_ops}')

    coefs = [ [] for _ in range(len(ops))]
    args = []
    for arg in e.args:
        if isinstance(arg, Add):
            args.append(qcollect_pauli(arg, ops))
        elif isinstance(arg, Mul):
            if arg.args[-1] in ops:
                idx = ops.index(arg.args[-1])
                if len(arg.args[:-1]) > 1:
                    coefs[idx].append(Mul(*arg.args[:-1]))
                elif len(arg.args[:-1]):
                        coefs[idx].append(arg.args[:-1][0])
                else:
                    coefs[idx].append(S.One)
            else:
                args.append(arg)
        else:
            args.append(arg)

    for idx in range(len(ops)):
        if len(coefs[idx]) == 1:
            args.append(Mul(coefs[idx][0], ops[idx]))
        elif len(coefs[idx]):
            args.append(Mul(Add(*coefs[idx]), ops[idx]))

    return Add(*args)
