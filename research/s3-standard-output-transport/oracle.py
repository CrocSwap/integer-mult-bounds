"""Independent permutation/difference-coordinate oracle and literal row replay.

No imports from the construction. S3 is derived by permuting three coordinates;
the two outputs are coordinate differences (z1-z0, z2-z0).
Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import permutations, product
from functools import lru_cache


def require(ok, message):
    if not ok:
        raise ValueError(message)


PERMS = tuple(permutations(range(3)))


def difference_matrix(p):
    z = ((0, 0), (1, 0), (0, 1))
    return tuple(z[p[i]][j] - z[p[0]][j] for i in (1, 2) for j in (0, 1))


MATS = tuple(sorted(map(difference_matrix, PERMS)))
PERM_FOR = tuple(next(p for p in PERMS if difference_matrix(p) == a) for a in MATS)
ONE = MATS.index((1, 0, 0, 1))


@lru_cache(maxsize=None)
def compose(a, b):
    # Pull permutations: applying a after b reads b[a[i]].
    pa, pb = PERM_FOR[a], PERM_FOR[b]
    return PERM_FOR.index(tuple(pb[pa[i]] for i in range(3)))


INV = tuple(next(b for b in range(6) if compose(a, b) == ONE) for a in range(6))


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def row_add(a, b, sign):
    return [x + sign*y for x, y in zip(a, b)]


def run(word, n):
    """Exact all-input linear map, all prefixes, and literal access invoice."""
    rows = identity(n)
    adds = negs = travel = cursor = 0
    peak = 1
    for op in word:
        require(len(op) == 4, "invalid instruction shape")
        kind, d, s, sign = op
        require(type(d) is int and 0 <= d < n, "invalid destination")
        if kind == "ADD":
            require(type(s) is int and 0 <= s < n and s != d and sign in (-1, 1),
                    "invalid or aliased ADD")
            rows[d] = row_add(rows[d], rows[s], sign)
            adds += 1
            travel += abs(cursor-s) + abs(s-d)
        else:
            require(kind == "NEG" and s == -1 and sign == -1, "invalid NEG")
            rows[d] = [-x for x in rows[d]]
            negs += 1
            travel += abs(cursor-d)
        cursor = d
        peak = max(peak, sum(map(abs, rows[d])))
    return rows, {"ADD": adds, "NEG": negs, "instructions": adds+negs,
                  "data_reads": 2*adds+negs, "data_writes": adds+negs,
                  "descriptor_fields": 4*(adds+negs),
                  "address_travel": travel+abs(cursor), "prefix_l1_peak": peak,
                  "registers": n}


def regular(g):
    p = [[0]*6 for _ in range(6)]
    for col in range(6):
        p[compose(g, col)][col] = 1
    return p


def intertwiner(v):
    z = (0, v[0], v[1])
    return [[z[p[i]] - z[p[0]] for p in PERM_FOR] for i in (1, 2)]


def linear_product(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def expected(n, v, drift=None, inverse=False):
    out = identity(n)
    r = intertwiner(v)
    if drift is not None:
        p = regular(INV[drift] if inverse else drift)
        for i in range(6):
            out[2+i][2:8] = p[i]
        if inverse:
            r = linear_product(r, p)
    for i in range(2):
        out[i][2:8] = [-x for x in r[i]] if inverse else r[i]
    return out


def primitive_frame_minima():
    """Exhaust all distinct GL2(Z) endpoints through radius four, no cutoff."""
    initial = ((1, 0), (0, 1))
    dist, layer = {initial: 0}, {initial}
    layers = [1]
    for d in range(1, 5):
        following = set()
        for state in layer:
            for target in (0, 1):
                for sign in (-1, 1):
                    row = tuple(x+sign*y for x, y in zip(state[target], state[1-target]))
                    rows = list(state)
                    rows[target] = row
                    following.add(tuple(rows))
                rows = list(state)
                rows[target] = tuple(-x for x in rows[target])
                following.add(tuple(rows))
        layer = following - dist.keys()
        for state in layer:
            dist[state] = d
        layers.append(len(layer))
    costs = []
    for q in MATS:
        state = (q[:2], q[2:])
        require(state in dist, "frame not reached at radius four")
        costs.append(dist[state])
    return costs, layers


def raw_schedule_minima(drifts, pcost, qcost, cuts=()):
    """Enumerate unaligned entrance and interior frame pairs, force only exits.

Each child's independent response is carried through chronological output
operations. No planner alignment test or transition formula is used. There are
36**k words for k children after the two terminal frame choices are forced.
"""
    k = len(drifts)
    minima = {(a, b): None for a in range(1, 4) for b in range(1, 3)}
    accepted = 0
    # Tags (left output action, right workspace action) denote Q_l R P_p.
    # An explicit 2x6 equality decides whether each tag is the desired R.
    r = intertwiner((1, 0))
    admissible_tag = {}
    for left in range(6):
        qm = [list(MATS[left][:2]), list(MATS[left][2:])]
        for right in range(6):
            actual = linear_product(linear_product(qm, r), regular(right))
            admissible_tag[left, right] = actual == r
    for choices in product(range(36), repeat=k):
        work = output = ONE
        tags = []
        wp = qp = 0
        for j, choice in enumerate(choices):
            a, b = divmod(choice, 6)
            work = compose(a, work)
            output = compose(b, output)
            tags = [(compose(b, left), right) for left, right in tags]
            wp += pcost[a]
            qp += qcost[b]
            if j in cuts and (work != ONE or output != ONE):
                break
            tags.append((ONE, work))
            work = compose(drifts[j], work)
        if len(tags) != k:
            continue
        a, b = INV[work], INV[output]
        wp += pcost[a]
        qp += qcost[b]
        tags = [(compose(b, left), right) for left, right in tags]
        if not all(admissible_tag[tag] for tag in tags):
            continue
        accepted += 1
        for scales in minima:
            bill = scales[0]*wp + scales[1]*qp
            if minima[scales] is None or bill < minima[scales]:
                minima[scales] = bill
    return minima, 36**k, accepted


def certify_boundary(drifts, pcost, qcost, rows, path, claimed):
    """Check a lower-bound potential and a matching path, without optimization.

Transitions are constructed by enumerating actual frame pairs and multiplying
permutations chronologically. No construction gap formula is imported.
"""
    require(len(rows) == len(drifts)+1 and len(path) == len(rows), "dual shape")
    require(all(len(row) == 6 and all(type(v) is int for v in row) for row in rows),
            "dual potentials must be integer six-vectors")
    require(all(type(t) is int and 0 <= t < 6 for t in path), "primal phase")
    require(path[-1] == ONE, "primal endpoint")
    checks = 0
    for t in range(6):
        require(rows[0][t] <= pcost[t]+qcost[t], "dual entrance exceeds legal price")
        checks += 1
    primal = pcost[path[0]]+qcost[path[0]]
    for j, drift in enumerate(drifts):
        path_edges = []
        for before, a, b in product(range(6), repeat=3):
            workspace_after = compose(a, compose(drift, before))
            output_after = compose(b, before)
            if workspace_after != output_after:
                continue
            after = workspace_after
            price = pcost[a]+qcost[b]
            require(rows[j+1][after] <= rows[j][before]+price,
                    "invalid dual transition inequality")
            checks += 1
            if before == path[j] and after == path[j+1]:
                path_edges.append(price)
        require(len(path_edges) == 1, "primal gap is not uniquely realized")
        primal += path_edges[0]
    require(rows[-1][ONE] == claimed == primal, "primal/dual gap")
    return {"lower_bound": rows[-1][ONE], "primal_cost": primal,
            "checked_inequalities": checks, "potentials": rows}
