"""Receiver-window machinery from my #4567 (window extraction from the #4470 constructor, endpoint census, exact
nested-subspace search). Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0."""
from collections import Counter, defaultdict
from fractions import Fraction as Fr
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
C = Fr(60403, 20000000)
GATES = tuple((i, j, s) for i in range(3) for j in range(3) if i != j for s in (-1, 1))
IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


# ---------------------------------------------------------------- integer endpoint census
def act(m, g):
    i, j, s = g
    out = list(m)
    for k in range(3):
        out[3 * i + k] += s * m[3 * j + k]
    return tuple(out)


def target(ca, cb):
    return act(act(IDENTITY, (0, 2, ca)), (1, 2, cb))


def words_of_length(n):
    layer = [(IDENTITY, ())]
    for _ in range(n):
        layer = [(act(m, g), w + (g,)) for m, w in layer for g in GATES]
    return layer


@lru_cache(None)
def matches(ca, cb, max_len):
    T = target(ca, cb)
    found, visited = [], 0
    for n in range(min(max_len, 4) + 1):
        layer = words_of_length(n)
        visited += len(layer)
        found += [w for m, w in layer if m == T]
    if max_len >= 5:
        # Meet in the middle: word = p + q with M(q) M(p) = T, i.e. M(p) = M(q)^-1 T.
        pre = {n: defaultdict(list) for n in (2, 3)}
        for n in (2, 3):
            for m, w in words_of_length(n):
                pre[n][m].append(w)
        for n in range(5, max_len + 1):
            lp, lq = (2, 3) if n == 5 else (3, 3)
            for _, q in words_of_length(lq):
                # M(q) = E_qk ... E_q1, so M(q)^-1 T = E_q1^-1 ... E_qk^-1 T: apply inverses from the last gate.
                inv = T
                for (i, j, s) in reversed(q):
                    inv = act(inv, (i, j, -s))
                for p in pre[lp].get(inv, ()):
                    found.append(p + q)
            visited += 12 ** n
    return tuple(found), visited


# ---------------------------------------------------------------- binary frames
@lru_cache(None)
def span(basis):
    vals = {0}
    for v in basis:
        vals |= {x ^ v for x in vals}
    return frozenset(vals)


def dim(sp):
    return len(sp).bit_length() - 1


@lru_cache(None)
def ssum(a, b):
    basis = []
    for v in list(a) + list(b):
        for bv in basis:
            v = min(v, v ^ bv)
        if v:
            basis.append(v)
    return span(tuple(sorted(basis)))


def relaxed(starts, ends, word):
    if not all(a <= b for a, b in zip(starts, ends)):
        return set()
    cur, lower = list(starts), []
    for i, j, _ in word:
        f = ssum(cur[i], cur[j])
        lower.append(f)
        cur[i] = cur[j] = f
    cur, upper = list(ends), [None] * len(word)
    for k in range(len(word) - 1, -1, -1):
        i, j, _ = word[k]
        f = cur[i] & cur[j]
        upper[k] = f
        cur[i] = cur[j] = f
    if not all(a <= b for a, b in zip(lower, upper)):
        return set()
    bounds = [(dim(a), dim(b)) for a, b in zip(lower, upper)]
    s0, e0 = tuple(dim(x) for x in starts), tuple(dim(x) for x in ends)
    out = set()

    def visit(k, state, hist):
        if k == len(word):
            h = list(hist)
            for a, b in zip(state, e0):
                if b > a:
                    h[b - a] += 1
            need(sum(r * n for r, n in enumerate(h)) == sum(e0) - sum(s0), "rank mass")
            out.add(tuple(h))
            return
        i, j, _ = word[k]
        lo, hi = bounds[k]
        for dd in range(max(lo, state[i], state[j]), min(hi, e0[i], e0[j]) + 1):
            h, st = list(hist), list(state)
            for r in (i, j):
                if dd > st[r]:
                    h[dd - st[r]] += 1
                st[r] = dd
            visit(k + 1, tuple(st), tuple(h))

    visit(0, s0, (0,) * 10)
    return out


# ---------------------------------------------------------------- certified rank prices r^(1-C)
def ln_bounds(y, terms=80):
    y = Fr(y)
    e = 0
    while y >= 2:
        y /= 2
        e += 1

    def core(v):
        z = (v - 1) / (v + 1)
        s, p = Fr(0), z
        for k in range(terms):
            s += 2 * p / (2 * k + 1)
            p *= z * z
        return s, s + 2 * p / ((2 * terms + 1) * (1 - z * z))

    a, b = core(y)
    c, d = core(Fr(2))
    return a + e * c, b + e * d


def prices():
    out = {1: (Fr(1), Fr(1))}
    for r in range(2, 10):
        lo, hi = ln_bounds(r)
        xs = (C * lo, C * hi)

        def expm(x, terms=30):  # exp(-x) for 0 < x < 1/100: alternating series bounds
            t, s = Fr(1), Fr(1)
            for n in range(1, terms):
                t *= -x / n
                s += t
            return s - abs(t * x / terms), s + abs(t * x / terms)

        out[r] = (r * expm(xs[1])[0], r * expm(xs[0])[1])
    return out


PRICE = prices()


def gain_upper(old, new):
    """Upper bound on cost(old) - cost(new) with certified prices; exact 0 for identical profiles."""
    if old == new:
        return Fr(0)
    tot = Fr(0)
    for r in range(1, 10):
        n = old[r] - new[r]
        if n:
            tot += n * (PRICE[r][1] if n > 0 else PRICE[r][0])
    return tot


# ---------------------------------------------------------------- windows from the canonical constructor
def construct():
    with tempfile.TemporaryDirectory(prefix="ext-ceiling-cache-") as cache:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
                "c,p,b,o,n=native_joint.construct();print(json.dumps({'c':c,'p':p['forward']}))")
        run = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
                              str(ROOT / "research/joint-helper-lattice")], capture_output=True, check=True, timeout=120)
    data = json.loads(run.stdout)
    return data["c"], data["p"]


def extract_windows(c, program):
    word = [e for e in program if e[0] != "climb"]
    frames = c["frames"]
    state = list(c["start"])
    phase, out = None, []

    def roles(e):
        g = e[1]
        return g[1:3] if g[0] in ("add", "copy") else g[1:2]

    for pos, e in enumerate(word):
        if e[0] == "phase":
            phase = e[1]
        if phase in ("B", "cleanup_tail") and pos + 1 < len(word):
            f = word[pos + 1]
            if e[0] == f[0] == "scalar" and e[1][0] == f[1][0] == "add" and all(r[0] == "L" for r in roles(e) + roles(f)):
                a, x, b, y = e[1][1][1], e[1][2][1], f[1][1][1], f[1][2][1]
                ca, cb = Fr(*e[1][3:]), Fr(*f[1][3:])
                if x == y and len({a, b, x}) == 3 and ca in (-1, 1) and cb in (-1, 1):
                    owners = (a, b, x)
                    starts = [span(tuple(frames[state[r]])) for r in owners]
                    ends = []
                    for r in owners:
                        t = c["final"][r]
                        for later in word[pos + 2:]:
                            if later[0] == "scalar" and ["L", r] in roles(later):
                                t = later[2]
                                break
                            if later[0] == "warp" and later[1] == ["L", r]:
                                t = later[3]
                                break
                        ends.append(span(tuple(frames[t])))
                    actual = [span(tuple(frames[e[2]])), span(tuple(frames[f[2]]))]
                    out.append({"index": pos, "phase": phase, "roles": list(owners), "coefficients": [int(ca), int(cb)],
                                "starts": starts, "ends": ends, "frames": actual})
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L":
                    state[r[1]] = e[2]
        elif e[0] == "warp":
            state[e[1][1]] = e[4]
    return out


def actual_profile(starts, ends, frames):
    word = ((0, 2, 0), (1, 2, 0))
    st, h = list(starts), [0] * 10
    for (i, j, _), f in zip(word, frames):
        for r in (i, j):
            need(st[r] <= f, "actual frame monotone")
            if dim(f) > dim(st[r]):
                h[dim(f) - dim(st[r])] += 1
            st[r] = f
    for a, b in zip(st, ends):
        need(a <= b, "actual exit monotone")
        if dim(b) > dim(a):
            h[dim(b) - dim(a)] += 1
    return tuple(h)


def extract_nonadjacent(c, program):
    """Pairs a += ca x ... b += cb x (unit ca, cb) in phases B/cleanup_tail separated by >= 1 operation, none of which
    touches a, b or x (so the pair can be rewritten in place). Starts are taken at the first shear, exits after the second."""
    word = [e for e in program if e[0] != "climb"]
    frames = c["frames"]

    def roles(e):
        g = e[1]
        return g[1:3] if g[0] in ("add", "copy") else g[1:2]

    def touches(e, fields):
        if e[0] == "scalar":
            return any(r[0] == "L" and r[1] in fields for r in roles(e))
        return e[0] == "warp" and e[1][0] == "L" and e[1][1] in fields

    state, phase, states = list(c["start"]), None, []
    for e in word:
        if e[0] == "phase":
            phase = e[1]
        states.append((phase, list(state)))
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L":
                    state[r[1]] = e[2]
        elif e[0] == "warp":
            state[e[1][1]] = e[4]
    out = []
    for pos, e in enumerate(word):
        ph, st = states[pos]
        if ph not in ("B", "cleanup_tail") or e[0] != "scalar" or e[1][0] != "add" or not all(r[0] == "L" for r in roles(e)):
            continue
        a, x, ca = e[1][1][1], e[1][2][1], Fr(*e[1][3:])
        if ca not in (-1, 1):
            continue
        for q in range(pos + 1, len(word)):
            f = word[q]
            if f[0] == "phase":
                break
            if (f[0] == "scalar" and f[1][0] == "add" and all(r[0] == "L" for r in roles(f)) and f[1][2][1] == x
                    and f[1][1][1] not in (a, x) and Fr(*f[1][3:]) in (-1, 1) and q > pos + 1):
                b = f[1][1][1]
                if not any(touches(word[k], {a, b, x}) for k in range(pos + 1, q)):
                    owners = (a, b, x)
                    ends = []
                    for r in owners:
                        t = c["final"][r]
                        for later in word[q + 1:]:
                            if later[0] == "scalar" and ["L", r] in roles(later):
                                t = later[2]
                                break
                            if later[0] == "warp" and later[1] == ["L", r]:
                                t = later[3]
                                break
                        ends.append(span(tuple(frames[t])))
                    out.append({"index": pos, "partner": q, "coefficients": [int(ca), int(Fr(*f[1][3:]))],
                                "starts": [span(tuple(frames[st[r]])) for r in owners], "ends": ends,
                                "frames": [span(tuple(frames[e[2]])), span(tuple(frames[f[2]]))]})
            if touches(f, {a, x}):
                break
    return out


def subspaces_between(L, U, k):
    """Every subspace F with L <= F <= U and dim F = k."""
    if not L <= U or not dim(L) <= k <= dim(U):
        return []
    found, seen, stack = set(), {L}, [L]
    while stack:
        cur = stack.pop()
        if dim(cur) == k:
            found.add(cur)
            continue
        for vec in U:
            if vec not in cur:
                nxt = ssum(cur, span((vec,)))
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
    return list(found)


def geometric_best_gain(starts, ends, old, word):
    """Exact search over actual nested subspaces (joint incidence enforced) for one word; None if infeasible."""
    cur, upper = list(ends), [None] * len(word)
    for k in range(len(word) - 1, -1, -1):
        i, j, _ = word[k]
        f = cur[i] & cur[j]
        upper[k] = f
        cur[i] = cur[j] = f
    best = [None]

    def rec(k, state, hist):
        if k == len(word):
            h = list(hist)
            for r in range(3):
                if not state[r] <= ends[r]:
                    return
                g = dim(ends[r]) - dim(state[r])
                if g:
                    h[g] += 1
            gain = gain_upper(old, tuple(h))
            if best[0] is None or gain > best[0]:
                best[0] = gain
            return
        i, j, _ = word[k]
        L, U = ssum(state[i], state[j]), upper[k]
        for dd in range(dim(L), dim(U) + 1):
            for F in subspaces_between(L, U, dd):
                h, st = list(hist), list(state)
                for r in (i, j):
                    g = dim(F) - dim(st[r])
                    if g:
                        h[g] += 1
                    st[r] = F
                rec(k + 1, tuple(st), tuple(h))

    rec(0, tuple(starts), (0,) * 10)
    return best[0]


def single_contact_retiming(c, program):
    """For every two-operand scalar contact in the whole word (all phases), compare the incumbent contact dimension with
    every admissible dimension between the operands' current-frame sum and their next-contact (exit) intersection.
    Any dimension in that range is realisable by a nested subspace, so this is exact for single-contact retiming."""
    word = [e for e in program if e[0] != "climb"]
    frames = c["frames"]

    def roles(e):
        g = e[1]
        return g[1:3] if g[0] in ("add", "copy") else g[1:2]

    exit_after, cur = [None] * len(word), {}
    for k in range(len(word) - 1, -1, -1):
        e = word[k]
        exit_after[k] = dict(cur)
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L":
                    cur[r[1]] = e[2]
        elif e[0] == "warp" and e[1][0] == "L":
            cur[e[1][1]] = e[3]

    def cost(h):
        return sum(n * PRICE[r][1] for r, n in enumerate(h) if n and r)

    state, phase, tally = list(c["start"]), None, Counter()
    for k, e in enumerate(word):
        if e[0] == "phase":
            phase = e[1]
        if e[0] == "scalar" and len(roles(e)) == 2 and all(r[0] == "L" for r in roles(e)):
            i, j = roles(e)[0][1], roles(e)[1][1]
            Si, Sj = span(tuple(frames[state[i]])), span(tuple(frames[state[j]]))
            Ei = span(tuple(frames[exit_after[k].get(i, c["final"][i])]))
            Ej = span(tuple(frames[exit_after[k].get(j, c["final"][j])]))
            F0 = span(tuple(frames[e[2]]))
            L, U = ssum(Si, Sj), Ei & Ej
            need(L <= F0 <= U, "incumbent contact inside its bounds")

            def prof(dd):
                h = [0] * 10
                for lo_, hi_ in ((dim(Si), dd), (dd, dim(Ei)), (dim(Sj), dd), (dd, dim(Ej))):
                    if hi_ > lo_:
                        h[hi_ - lo_] += 1
                return tuple(h)

            incumbent = cost(prof(dim(F0)))
            need(all(cost(prof(dd)) >= incumbent for dd in range(dim(L), dim(U) + 1)), f"single-contact optimum at {k}")
            tally[phase] += 1
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L":
                    state[r[1]] = e[2]
        elif e[0] == "warp":
            state[e[1][1]] = e[4]
    return dict(tally)


def two_contact_retiming(c, program):
    """Joint retiming of two consecutive contacts k1 < k2 of one field r (other operands p at k1, q at k2, p != q):
    F1 >= S_r + S_p, F1 <= E_p, F1 <= F2, F2 >= F1 + S_q, F2 <= E_r & E_q. First a dimension relaxation; where it is
    positive, an exact search over actual nested subspaces. Returns tallies; any exact gain fails the check."""
    word = [e for e in program if e[0] != "climb"]
    frames = c["frames"]

    def roles(e):
        g = e[1]
        return g[1:3] if g[0] in ("add", "copy") else g[1:2]

    def fr(i):
        return span(tuple(frames[i]))

    def is2(e):
        return e[0] == "scalar" and len(roles(e)) == 2 and all(r[0] == "L" for r in roles(e))

    state, before = list(c["start"]), []
    for e in word:
        before.append(list(state))
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L":
                    state[r[1]] = e[2]
        elif e[0] == "warp":
            state[e[1][1]] = e[4]
    nexttouch, cur = [None] * len(word), {}
    for k in range(len(word) - 1, -1, -1):
        e = word[k]
        nexttouch[k] = dict(cur)
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L":
                    cur[r[1]] = k
        elif e[0] == "warp" and e[1][0] == "L":
            cur[e[1][1]] = k

    def exit_frame(field, k):
        t = nexttouch[k].get(field)
        if t is None:
            return fr(c["final"][field])
        return fr(word[t][2]) if word[t][0] == "scalar" else fr(word[t][3])

    def cost(h):
        return sum(n * PRICE[r][1] for r, n in enumerate(h) if n and r)

    tally = Counter()
    for k1, e1 in enumerate(word):
        if not is2(e1):
            continue
        f1 = [r[1] for r in roles(e1)]
        for r in f1:
            k2 = nexttouch[k1].get(r)
            if k2 is None or not is2(word[k2]):
                continue
            p = [x for x in f1 if x != r][0]
            q = [x[1] for x in roles(word[k2]) if x[1] != r][0]
            if q == p:
                continue
            Sr, Sp, Sq = fr(before[k1][r]), fr(before[k1][p]), fr(before[k2][q])
            Ep, Er, Eq = exit_frame(p, k1), exit_frame(r, k2), exit_frame(q, k2)

            def prof(d1, d2):
                h = [0] * 10
                for lo_, hi_ in ((dim(Sr), d1), (d1, d2), (d2, dim(Er)), (dim(Sp), d1), (d1, dim(Ep)), (dim(Sq), d2), (d2, dim(Eq))):
                    if hi_ > lo_:
                        h[hi_ - lo_] += 1
                return tuple(h)

            base = cost(prof(dim(fr(e1[2])), dim(fr(word[k2][2]))))
            L1, U2 = ssum(Sr, Sp), Er & Eq
            U1 = Ep & U2
            need(L1 <= U1, "incumbent bounds consistent")
            relaxed_best = min(cost(prof(d1, d2)) for d1 in range(dim(L1), dim(U1) + 1)
                               for d2 in range(max(d1, dim(ssum(L1, Sq))), dim(U2) + 1))
            if relaxed_best >= base:
                tally["zero_by_relaxation"] += 1
                continue
            exact = None
            for d1 in range(dim(L1), dim(U1) + 1):
                for F1 in subspaces_between(L1, U1, d1):
                    L2 = ssum(F1, Sq)
                    for d2 in range(dim(L2), dim(U2) + 1):
                        if subspaces_between(L2, U2, d2):
                            cc = cost(prof(d1, d2))
                            exact = cc if exact is None or cc < exact else exact
            need(exact is None or exact >= base, f"two-contact retiming gain at {k1},{k2}")
            tally["zero_by_exact_geometry"] += 1
    return dict(tally)


def matches_alphabet(ca, cb, coefs, max_len):
    """All words of length <= max_len over shears y_i += c y_j (c in coefs) with the window endpoint (meet in middle)."""
    gates = tuple((i, j, c) for i in range(3) for j in range(3) if i != j for c in coefs)

    def layer(n):
        out = [(IDENTITY, ())]
        for _ in range(n):
            out = [(act(m, g), w + (g,)) for m, w in out for g in gates]
        return out

    half = max_len // 2
    pre = defaultdict(list)
    for n in range(half + 1):
        for m, w in layer(n):
            pre[n, m].append(w)
    T, found = target(ca, cb), []
    for total in range(max_len + 1):
        lp = min(half, total)
        lq = total - lp
        for _, q in layer(lq):
            inv = T
            for (i, j, c) in reversed(q):
                inv = act(inv, (i, j, -c))
            found += [p + q for p in pre.get((lp, inv), ())]
    return found

