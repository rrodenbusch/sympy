"""
    Collect non-commutative symbols

    Explanation
    ===========

    This function extends the sympy.core.radsimp.collect function to allow the
     collection of additive terms of an expression with respect non-commutative symbols.

    A non-commutative operator that provides an _eval_collect method will
    be collected first and removed from the list of symbols to be collected.
    Any remaining symbols will then be passed to the core collect function.

"""
from sympy import collect as core_collect
from sympy.physics.quantum import Operator
def collect(e, syms, *args, **kwargs):
    expr = e
    op_syms = list(filter(lambda x: isinstance(x, Operator) and hasattr(x,'_eval_collect'), syms))
    other_syms =  list(filter(lambda x: not isinstance(x, Operator) and hasattr(x, '_eval_collect'), syms))
    if len(op_syms):
        op_funcs = {}
        for sym in op_syms:
            func = sym._eval_collect
            func_syms = op_funcs.get(func,[])
            if sym not in func_syms:
                func_syms.append(sym)
                op_funcs[func] = func_syms
        for _func, _syms in op_funcs.items():
            expr = _func(expr, _syms, *args, **kwargs)
        if len(other_syms):
            return core_collect(e, other_syms, *args, **kwargs)
    return(expr)
