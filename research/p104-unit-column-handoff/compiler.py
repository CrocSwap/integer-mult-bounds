"""Unit-column dyadic basis completion, prepared for @CubeJerry.

Substantial OpenAI Codex assistance. Apache-2.0.
The dual-pair contract and tariff are Ali Romman's #5611/#5602 work;
this source-specific column-pivot specialization uses classical shears.
"""
from fractions import Fraction as Q


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic(q):
    return q.denominator & (q.denominator - 1) == 0


def unit(q):
    n = abs(q.numerator)
    return n > 0 and n & (n - 1) == 0 and dyadic(q)


def compile_basis(a, b, pivot, frame):
    """Emit R with a R=e_p^T and R e_p=b, provided b_p is a unit.

    The operation order is T, D, C, hence R=C D T. This accepts arbitrary
    dirty inputs and uses only the roles occurring in the two given vectors.
    It is not a global scalar-circuit optimizer.
    """
    require(type(pivot) is int and pivot >= 0, 'Valid pivot')
    require(type(frame) is int and frame >= 0, 'Valid frame')
    require(all(type(k) is int and k >= 0 for k in a.keys() | b.keys()), 'Valid roles')
    a, b = {k: Q(v) for k, v in a.items() if v}, {k: Q(v) for k, v in b.items() if v}
    require(all(dyadic(v) for v in list(a.values()) + list(b.values())), 'Dyadic coefficients')
    require(sum(a.get(k, 0) * v for k, v in b.items()) == 1, 'Dual pairing')
    q = b.get(pivot, Q(0))
    require(unit(q), 'Unit column pivot')
    events = [['ADD', pivot, k, str(-v), frame] for k, v in sorted(a.items()) if k != pivot]
    if q != 1:
        events.append(['SCALE', pivot, str(q), frame])
    events += [['ADD', k, pivot, str(v/q), frame] for k, v in sorted(b.items()) if k != pivot]
    # This is the local caller's existing cap, not a new magnitude assumption.
    require(all(abs(Q(e[-2])) + 1 < 2**16 for e in events + inverse(events)), 'Fixed scalar growth bound')
    return events


def inverse(events):
    answer = []
    for event in reversed(events):
        copied = event[:]
        q = Q(copied[-2])
        copied[-2] = str(1/q if copied[0] == 'SCALE' else -q)
        answer.append(copied)
    return answer


def allowance(events):
    total = 0
    for event in events:
        q = Q(event[-2]); n, d = abs(q.numerator), q.denominator
        require(q and dyadic(q), 'Priced nonzero dyadic coefficient')
        if event[0] == 'ADD':
            total += 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)
        else:
            require(event[0] == 'SCALE' and unit(q), 'Priced unit SCALE')
            total += 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
    return total


def compile_preconditioned(a, b, pivot, frame, left, right):
    """Use S=I+e_left e_right^T, then return S^-1 R' for (aS^-1,Sb).

    The chosen roles are existing nonpivot roles. The caller supplies their
    common chart. This is one specified preconditioner, not an optimizer.
    """
    require(type(left) is int and type(right) is int and min(left, right) >= 0,
            'Valid preconditioner roles')
    require(left != right and pivot not in (left, right), 'Nonpivot preconditioner')
    require(left in a.keys() | b.keys() and right in a.keys() | b.keys(),
            'Existing preconditioner roles')
    a, b = {k: Q(v) for k,v in a.items()}, {k: Q(v) for k,v in b.items()}
    aa, bb = dict(a), dict(b)
    aa[right] = aa.get(right,Q(0)) - aa.get(left,Q(0))
    bb[left] = bb.get(left,Q(0)) + bb.get(right,Q(0))
    events = compile_basis(aa,bb,pivot,frame) + [['ADD',left,right,'-1',frame]]
    require(all(abs(Q(e[-2])) + 1 < 2**16 for e in events + inverse(events)),
            'Fixed scalar growth bound')
    return events
