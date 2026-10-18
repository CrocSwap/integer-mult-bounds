"""Faithful S3 output transport: construction and six-state planner.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
All costs count emitted scalar ADD/NEG instructions, not multiplication time.
"""
from dataclasses import dataclass


G = ((-1, 0, -1, 1), (-1, 1, -1, 0), (0, -1, 1, -1),
     (0, 1, 1, 0), (1, -1, 0, -1), (1, 0, 0, 1))
E, S, T = 5, 3, 0


def mm(a, b):
    return tuple(sum(a[2*i+k] * b[2*k+j] for k in range(2))
                 for i in range(2) for j in range(2))


PRODUCT = tuple(tuple(G.index(mm(a, b)) for b in G) for a in G)
INVERSE = tuple(next(b for b in range(6) if PRODUCT[a][b] == E)
                for a in range(6))


def mul(a, b):
    return PRODUCT[a][b]


def add(dst, src, sign=1):
    return ("ADD", dst, src, sign)


def neg(dst):
    return ("NEG", dst, -1, -1)


# These literal two-register words are checked independently through radius four.
Q_WORDS = (
    (add(1, 0, -1), neg(0)),
    (add(0, 1), add(1, 0, -1), add(0, 1), add(0, 1)),
    (add(0, 1, -1), add(0, 1, -1), add(1, 0), add(0, 1, -1)),
    (add(0, 1), add(1, 0, -1), add(0, 1), neg(1)),
    (add(0, 1, -1), neg(1)),
    (),
)
Q_COST = tuple(map(len, Q_WORDS))


def q_word(g, rows):
    return [(kind, rows[d], rows[s] if kind == "ADD" else -1, sign)
            for kind, d, s, sign in Q_WORDS[g]]


def p_word(g, rows):
    """Left regular action P_g e_h=e_(gh), with charged cycle rotations."""
    pull = [mul(INVERSE[g], h) for h in range(6)]
    seen, word = set(), []
    for start in range(6):
        if start in seen:
            continue
        cycle, h = [], start
        while h not in seen:
            cycle.append(rows[h])
            seen.add(h)
            h = pull[h]
        for a, b in zip(cycle, cycle[1:]):
            # (a,b) <- (b,-a). Consecutive signs cancel on odd cycles.
            word.extend((add(a, b), add(b, a, -1), add(a, b)))
        if len(cycle) % 2 == 0:
            word.append(neg(cycle[-1]))
    return word


P_COST = tuple(len(p_word(g, list(range(6)))) for g in range(6))


def reader(v):
    """The intertwiner R(v) has column h equal to Q_h v."""
    return tuple(tuple(G[h][2*i] * v[0] + G[h][2*i+1] * v[1]
                       for h in range(6)) for i in range(2))


def admitted(r):
    if len(r) != 2 or any(len(row) != 6 for row in r):
        return False
    for g in (S, T):
        for i in range(2):
            for h in range(6):
                if r[i][mul(g, h)] != sum(G[g][2*i+j] * r[j][h]
                                         for j in range(2)):
                    return False
    return True


def gap(before, after, drift):
    delta = mul(after, INVERSE[before])
    return mul(delta, INVERSE[drift]), delta


def plan(drifts, cuts=(), pscale=1, qscale=1):
    """Exact minimum in the declared complete P/Q macro alphabet."""
    if any(type(g) is not int or not 0 <= g < 6 for g in drifts):
        raise ValueError("unknown group element")
    if pscale <= 0 or qscale <= 0:
        raise ValueError("frame prices must be positive")
    if any(type(c) is not int or not 0 <= c <= len(drifts) for c in cuts):
        raise ValueError("checkpoint outside the batch")
    cuts = set(cuts) | {len(drifts)}
    costs = {g: (pscale * P_COST[g] + qscale * Q_COST[g], (g,))
             for g in range(6) if 0 not in cuts or g == E}
    for j, drift in enumerate(drifts, 1):
        following = {}
        for after in range(6):
            if j in cuts and after != E:
                continue
            choices = []
            for before, (price, path) in costs.items():
                a, b = gap(before, after, drift)
                choices.append((price + pscale * P_COST[a] + qscale * Q_COST[b],
                                path + (after,)))
            following[after] = min(choices)
        costs = following
    return costs[E]


def distance_certificate(drifts):
    """Forward shortest distances, to be checked as dual feasible potentials."""
    rows = [[P_COST[g]+Q_COST[g] for g in range(6)]]
    for drift in drifts:
        following = []
        for after in range(6):
            choices = []
            for before in range(6):
                a, b = gap(before, after, drift)
                choices.append(rows[-1][before]+P_COST[a]+Q_COST[b])
            following.append(min(choices))
        rows.append(following)
    return rows


@dataclass(frozen=True)
class Node:
    drift: int
    v: tuple = (0, 0)
    children: tuple = ()


def vector(node):
    if not node.children:
        return node.v
    return tuple(sum(vector(c)[i] for c in node.children) for i in range(2))


def depth(node):
    return 0 if not node.children else 1 + max(map(depth, node.children))


def inverse_word(word):
    return [(kind, d, s, -sign if kind == "ADD" else sign)
            for kind, d, s, sign in reversed(word)]


def leaf_word(node, output, source):
    word = []
    for i, row in enumerate(reader(node.v)):
        for j, coefficient in enumerate(row):
            word.extend([add(output[i], source[j], 1 if coefficient > 0 else -1)]
                        * abs(coefficient))
    return word + p_word(node.drift, source)


def batch_word(children, output, work, scratch, optimized=True, cuts=()):
    drifts = tuple(c.drift for c in children)
    path = plan(drifts, cuts)[1] if optimized else (E,) * (len(children)+1)
    word = p_word(path[0], work) + q_word(path[0], output)
    boundaries = [len(word)]
    for i, child in enumerate(children):
        word.extend(node_word(child, output, work, scratch, optimized))
        a, b = gap(path[i], path[i+1], child.drift)
        word.extend(p_word(a, work))
        word.extend(q_word(b, output))
        boundaries.append(len(word))
    return word, path, boundaries


def echo_word(children, output, source, scratch, optimized=True, cuts=()):
    work = list(range(scratch, scratch+6))
    h, _, _ = batch_word(children, output, work, scratch+6, optimized, cuts)
    return ([add(w, x) for w, x in zip(work, source)] + h
            + [add(w, x, -1) for w, x in zip(work, source)] + inverse_word(h))


def node_word(node, output=(0, 1), source=tuple(range(2, 8)), scratch=8,
              optimized=True):
    if not node.children:
        return leaf_word(node, output, source)
    return (echo_word(node.children, output, source, scratch, optimized)
            + p_word(node.drift, source))


def cost_node(node, optimized=True):
    if not node.children:
        return sum(abs(x) for row in reader(node.v) for x in row) + P_COST[node.drift]
    return cost_echo(node.children, optimized) + P_COST[node.drift]


def cost_echo(children, optimized=True, cuts=()):
    drifts = tuple(c.drift for c in children)
    boundary = plan(drifts, cuts)[0] if optimized else sum(P_COST[g] for g in drifts)
    return 2 * sum(cost_node(c, optimized) for c in children) + 12 + 2 * boundary
