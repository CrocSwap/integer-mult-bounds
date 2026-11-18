"""Exact rational values of every node of a banked circuit (standard library only)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import schedule, axpy, Q


def exact_values(net, order=None):
    """node -> {input r: Fraction}; inputs are the public roles at their initial charts."""
    order = order or schedule(net); V = {}
    for k in order:
        v = {}
        for d, c in net.forms[k].items():
            if d < 0: axpy(v, {~d: Q(1)}, c)
            else: axpy(v, V[d], c)
        V[k] = v
    return V
