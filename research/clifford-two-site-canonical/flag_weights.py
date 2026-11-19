"""Invert the width-13 central Gram on all marked Lagrangians, including exterior marks."""
from array import array
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations
import json
from math import lcm

from predecessor import pointed as P
from compile_row import UPPER, apply, compose, pairing, shear

IDENTITY = P.IDENTITY
BASE = P.BASE


@cache
def spaces():
    bases, masks, _ = P.quotient()
    return bases, masks, {mask: i for i, mask in enumerate(masks)}


@cache
def parabolic_generators():
    generators = [shear(1 << k) for k in range(len(UPPER))]
    for i in range(4):
        for j in range(4):
            if i != j:
                columns = list(IDENTITY)
                columns[i] ^= 1 << j
                columns[j+4] ^= 1 << (i+4)
                generators.append(tuple(columns))
    return tuple(generators)


@cache
def mark_transports():
    # Maps (Z, arbitrary mark) to one of the three fixed flags.
    maps = {}
    for root in (0, 1, 16):
        queue = [root]
        maps[root] = (root, IDENTITY)
        for v in queue:
            for g in parabolic_generators():
                w = apply(g, v)
                if w not in maps:
                    maps[w] = root, compose(maps[v][1], g)
                    queue.append(w)
    P.require(len(maps) == 256, "three parabolic mark orbits")
    return maps


@cache
def actions(columns):
    bases, _, index = spaces()
    vec = bytes(apply(columns, v) for v in range(256))
    lag = array('H', (index[P.point_set(tuple(vec[b] for b in B))] for B in bases))
    return vec, lag


@cache
def orbits(root):
    """Stabilizer orbits on pairs (variable Lagrangian, unrestricted mark)."""
    _, masks, _ = spaces()
    gens = [actions(g) for g in parabolic_generators() if apply(g, root) == root]
    labels = bytearray([255]) * (len(masks) * 256)
    reps = []
    for seed in range(len(labels)):
        if labels[seed] != 255:
            continue
        idx = len(reps)
        P.require(idx < 255, "orbit labels fit the inventory")
        reps.append(divmod(seed, 256))
        labels[seed] = idx
        queue = array('I', [seed])
        for state in queue:
            space, mark = divmod(state, 256)
            for vec, lag in gens:
                dest = (lag[space] << 8) | vec[mark]
                if labels[dest] == 255:
                    queue.append(dest)
                    labels[dest] = idx
    return labels, reps


@cache
def class_actions():
    moves = [actions(tuple(b ^ (a if pairing(a, b) else 0) for b in IDENTITY)) for a in range(256)]
    planes = [(a, b, a ^ b) for a, b in combinations(range(1, 256), 2)
              if b < (a ^ b) and not pairing(a,b)]
    P.require(len(planes) == 5355, "isotropic two-plane census")
    return moves, planes


@cache
def class_rows(root):
    labels, reps = orbits(root)
    moves, planes = class_actions()
    rows = []
    for L, v in reps:
        tr = Counter(labels[(lag[L] << 8) | vec[v]] for vec, lag in moves[1:])
        alt = Counter()
        for a, b, c in planes:
            av, al = moves[a]
            bv, bl = moves[b]
            cv, cl = moves[c]
            alt[labels[(cl[bl[al[L]]] << 8) | cv[bv[av[v]]]]] += 1
        rows.append((tr, alt))
    return rows


@cache
def character_levels():
    """Joint class-sum eigenvalues and Gram scalars on the three permutation modules."""
    table = json.loads((P.HERE/'predecessor/source/CLASS-ALGEBRA.json').read_bytes())
    classes = table['classes']
    indices = [next(i for i, c in enumerate(classes) if c['size'] == size)
               for size in (255, 5355)]
    bases, masks, _ = spaces()
    fixed = []
    for c in classes:
        previous = None
        for s in c['representatives']:
            vec = [apply(s, v) for v in range(256)]
            fixed_marks = sum(1 << v for v in range(256) if vec[v] == v)
            counts = [0, 0, 0]
            for basis, mask in zip(bases, masks, strict=True):
                if all((mask >> vec[b]) & 1 for b in basis):
                    inside = (mask & fixed_marks).bit_count()
                    counts[0] += 1
                    counts[1] += inside-1
                    counts[2] += fixed_marks.bit_count()-inside
            P.require(previous in (None, counts), "fixed flags across rational packet")
            previous = counts
        fixed.append(previous)
    levels = {}
    dims = [0, 0, 0]
    for row in table['characters']:
        norm, rem = divmod(sum(c['size'] * x*x for c, x in zip(classes, row)), P.ORDER)
        P.require(norm and not rem, "character packet norm")
        mult = [Fraction(sum(c['size'] * x * m[i] for c, x, m in zip(classes, row, fixed)),
                         P.ORDER * norm) for i in range(3)]
        P.require(all(n.denominator == 1 and n >= 0 for n in mult), "flag character multiplicity")
        for i, n in enumerate(mult):
            dims[i] += row[0] * n
        if not any(mult):
            continue
        pair = tuple(Fraction(classes[i]['size'] * row[i], row[0]) for i in indices)
        P.require(all(x.denominator == 1 for x in pair), "integral class-sum spectrum")
        scalar = Fraction(sum(c['size'] * x * (-64)**c['fixed'] for c, x in zip(classes, row)),
                          row[0] * 16**12)
        key = tuple(map(int, pair))
        P.require(scalar > 0 and key not in levels, "separating central class sums")
        levels[key] = scalar
    P.require(dims == [2295,34425,550800] and len(levels) == 31, "marked module dimensions")
    return levels


@cache
def separating_operator():
    levels = character_levels()
    # Both class operators have integer eigenvalues; a scale above the entire
    # transvection interval prevents collisions in their integer linear combination.
    scale = 511
    values = {a + scale*b: val for (a,b), val in levels.items()}
    P.require(len(values) == len(levels), "central interpolation nodes")
    return scale, values


def newton_values(nodes, values):
    coeff = list(values)
    for width in range(1,len(nodes)):
        for i in range(len(nodes)-1,width-1,-1):
            coeff[i] = (coeff[i]-coeff[i-1]) / (nodes[i]-nodes[i-width])
    return coeff


def rhs(j):
    return Fraction(1, 4**13) * Fraction(-1,32)**j


@cache
def class_matrix(root):
    scale, _ = separating_operator()
    result = []
    for tr, alt in class_rows(root):
        counts = tr.copy()
        counts.update({k: scale*v for k,v in alt.items()})
        result.append(tuple(counts.items()))
    return result


def apply_gram(root, vector, reciprocal):
    _, levels = separating_operator()
    nodes = sorted(levels)
    coeff = newton_values(nodes, [1/levels[k] if reciprocal else levels[k] for k in nodes])
    den = lcm(*(c.denominator for c in coeff))
    ci = [int(c*den) for c in coeff]
    input_den = lcm(*(x.denominator for x in vector))
    src = [int(x*input_den) for x in vector]
    state = [ci[-1]*v for v in src]
    matrix = class_matrix(root)
    for j in reversed(range(len(nodes)-1)):
        state = [sum(w*state[k] for k,w in row) - nodes[j]*state[i] + ci[j]*src[i]
                 for i,row in enumerate(matrix)]
    return tuple(Fraction(x, den*input_den) for x in state)


@cache
def solution(root):
    _, reps = orbits(root)
    _, masks, _ = spaces()
    raw = tuple(rhs(P.distance(BASE, masks[i])) if v == root else Fraction(0) for i,v in reps)
    return apply_gram(root, raw, True)


def weight(L, u, X, w):
    """Value at (X,w) of the inverse of h(distance(Z,X)) [u=w], with L=Z."""
    P.require(L == BASE, "left Lagrangian must be the reference Z in the supplied bases")
    _, _, index = spaces()
    root, g = mark_transports()[u]
    vec, lag = actions(g)
    idx = orbits(root)[0][(lag[index[X]] << 8) | vec[w]]
    return solution(root)[idx]
