"""Exact common-right-factor batching. Apache-2.0; see NOTICE.md."""
from collections import Counter


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(word):
    return [(f, x, y, -s) for f, x, y, s in reversed(word)]


def product(factors, source, target, scratch):
    """Factors are in application order, so [B, A] means A B."""
    need(bool(factors), 'empty factor list')
    need(len(scratch) >= (len(factors)-1).bit_length(), 'insufficient scratch')
    need(len(set([source, target] + list(scratch))) == 2+len(scratch), 'aliased roles')
    if len(factors) == 1:
        return [(factors[0], source, target, 1)]
    mid = len(factors)//2
    z, *rest = scratch
    right = product(factors[:mid], source, z, rest)
    left = product(factors[mid:], z, target, rest)
    return right + left + inverse(right) + inverse(left)


def compile_batch(common, branches, mode='batch'):
    """Return (literal leaf word, dirty role count), reserving all output roles."""
    need(bool(common) and bool(branches) and all(branches), 'nonempty factors and outputs required')
    need(mode in ('batch', 'separate', 'grouped'), 'unknown comparator')
    k = len(branches)
    depth = max((len(common)-1).bit_length(), *((len(a)-1).bit_length() for a in branches))
    dirt = max(1+depth, max((len(common)+len(a)-1).bit_length() for a in branches))
    scratch = list(range(k+1, k+1+dirt))
    if mode == 'separate':
        return [op for i, a in enumerate(branches, 1)
                for op in product(common+a, 0, i, scratch)], dirt
    right = product(common, 0, scratch[0], scratch[1:])
    lefts = [product(a, scratch[0], i, scratch[1:]) for i, a in enumerate(branches, 1)]
    if mode == 'grouped':
        return [op for left in lefts for op in right+left+inverse(right)+inverse(left)], dirt
    # Distinct targets and read-only shared source make these left words commute.
    left = [op for word in lefts for op in word]
    return right + left + inverse(right) + inverse(left), dirt


def run(word, matrices, arrays, modulus=None):
    """Literal exact leaf interpreter; validate every alias before any mutation."""
    need(len({id(v) for v in arrays}) == len(arrays), 'aliased arrays')
    n = len(arrays[0])
    need(n > 0 and all(len(v) == n for v in arrays), 'array lengths')
    need(modulus is None or type(modulus) is int and modulus > 1, 'modulus')
    for f, x, y, sign in word:
        need(type(f) is int and f in matrices, 'unknown factor')
        need(type(x) is int and type(y) is int and 0 <= x < len(arrays) and 0 <= y < len(arrays) and x != y, 'leaf ports')
        need(type(sign) is int and sign in (-1, 1), 'leaf sign')
        a = matrices[f]
        need(len(a) == n and all(len(row) == n for row in a), 'matrix dimensions')
        need(all(a is not v and row is not v for v in arrays for row in a), 'mutable coefficient alias')
    for f, x, y, sign in word:
        for i, row in enumerate(matrices[f]):
            increment = sum(a*b for a, b in zip(row, arrays[x]))
            arrays[y][i] += sign*increment
            if modulus is not None:
                arrays[y][i] %= modulus


def leaf_count(n):
    need(type(n) is int and n > 0, 'positive factor count')
    p = 1 << (n.bit_length()-1)
    return p*(3*n-2*p)


def invoice(word, dimension, roles, factors):
    """Dense reference leaf invoice, including literal head travel in word slots.

    Data rows precede the read-only coefficient matrices on one tape. Each leaf
    starts and ends at word slot 0; the scalar accumulator is an arithmetic port.
    This deliberately slow layout makes source access and head returns explicit.
    """
    n = dimension
    counts = Counter(f for f, _, _, _ in word)
    moves = 0
    for f, x, y, _ in word:
        head = 0
        for i in range(n):
            for j in range(n):
                for pos in (roles*n + f*n*n + i*n+j, x*n+j):
                    moves += abs(pos-head)
                    head = pos
            pos = y*n+i
            moves += abs(pos-head)
            head = pos
        moves += head
    return dict(leaf_calls=len(word), calls_by_factor={str(f): counts[f] for f in range(factors)},
                coefficient_reads=len(word)*n*n, source_reads=len(word)*n*n,
                target_read_writes=len(word)*n, multiplications=len(word)*n*n,
                additions=len(word)*n*(n+1), negations=sum(s < 0 for _,_,_,s in word)*n,
                head_travel_word_slots=moves,
                preflight_array_length_checks=roles, preflight_role_alias_entries=roles,
                preflight_matrix_row_length_checks=len(word)*n,
                preflight_coefficient_alias_pairs=len(word)*roles*n,
                coefficient_storage_words=factors*n*n, data_storage_words=roles*n,
                instruction_records=len(word))
