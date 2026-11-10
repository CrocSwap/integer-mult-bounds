"""Word model, exact replays and sparse exact linear algebra for the relay-hub package.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
Event semantics follow the retained native verifiers (Ali Romman, CubeJerry; Apache-2.0):
registers have a frame (subspace of F_2^9) that public registers only climb and private registers only
descend; ADD/COPY/SCALE act at the common frame of their registers; INIT/CLEAR bound private lifetimes.
Standard library only; every failure raises ValueError (so it stays active under python -O).
"""
import gzip
import hashlib
import json
import math
from fractions import Fraction as Q


def need(cond, what):
    if not cond:
        raise ValueError(what)


# ------------------------------------------------------------------------------------------ word
def load(path):
    return json.loads(gzip.decompress(open(path, 'rb').read()))


def payload_sha(word):
    body = {k: v for k, v in word.items() if k != 'verifier_profile'}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in out}
    return frozenset(out)


class Frames:
    def __init__(self, word):
        self.sets = [span(b) for b in word['frames']]
        self.mask = [sum(1 << x for x in s) for s in self.sets]
        self.dim = [len(s).bit_length() - 1 for s in self.sets]
        self.zero = next(i for i, d in enumerate(self.dim) if d == 0)
        self.full = next(i for i, d in enumerate(self.dim) if d == 9)

    def sub(self, a, b):          # frame a is contained in frame b
        return self.mask[a] & ~self.mask[b] == 0

    def proper(self, a, b):
        return a != b and self.sub(a, b) and self.mask[a] != self.mask[b]


def regs(e):
    """Registers an event touches (MOVE included)."""
    return [e[1]] if e[0] in ('SCALE', 'INIT', 'CLEAR', 'MOVE') else [e[1], e[2]]


def event_frame(e):
    return e[2] if e[0] in ('INIT', 'CLEAR') else e[-1]


def coeff(e):
    return Q(e[2]) if e[0] == 'SCALE' else Q(e[3])


def check_legal(word, program=None):
    """Frame legality of a program on the word's registers; returns census counters."""
    F = Frames(word)
    prog = word['program'] if program is None else program
    pub = word['public']
    cur = {r: word['initial'][r] for r in range(pub)}
    census = {'public_rise': 0, 'private_fall': 0, 'adds': 0, 'lifetimes': 0}
    for e in prog:
        o = e[0]
        if o == 'MOVE':
            r, a, b, own = e[1], e[2], e[3], e[4]
            need(cur.get(r) == a, ('move source frame', e))
            need(own == (r >= pub), ('owned flag', e))
            if own:
                need(F.proper(b, a), ('private move must descend', e))
                census['private_fall'] += 1
            else:
                need(F.proper(a, b), ('public move must climb', e))
                census['public_rise'] += 1
            cur[r] = b
        elif o == 'INIT':
            need(e[1] >= pub and cur.get(e[1]) is None, ('INIT of a live or public register', e))
            cur[e[1]] = e[2]
            census['lifetimes'] += 1
        elif o == 'CLEAR':
            need(e[1] >= pub and cur.get(e[1]) == e[2], ('CLEAR frame', e))
            cur[e[1]] = None
        else:
            need(o in ('ADD', 'COPY', 'SCALE'), ('unknown event', e))
            rs = regs(e)
            need(len(set(rs)) == len(rs), ('aliased registers', e))
            for r in rs:
                need(cur.get(r) == e[-1], ('co-rest violated', e))
            census['adds'] += 1
    for r in range(pub):
        need(cur[r] == word['final'][r], ('final frame', r))
    need(all(v is None for r, v in cur.items() if r >= pub), 'a private register is alive at the end')
    return census


# --------------------------------------------------------------------------------- exact replay
def replay(word, program, symbolic_cut=None):
    """Rows of the public registers as dicts {input: Fraction}; owned rows start empty, INIT/CLEAR empty them.

    symbolic_cut(e) -> True makes a private MOVE replace its register's row by a fresh symbol ('z', k); the
    old row is appended to the list returned as second value.  Returns (rows, cut_sources)."""
    pub = word['public']
    n = pub + word['owned_fields']
    rows = [{r: Q(1)} if r < pub else {} for r in range(n)]
    cut_sources = []
    for e in program:
        o = e[0]
        if o == 'MOVE':
            if e[1] >= pub and symbolic_cut is not None and symbolic_cut(e):
                cut_sources.append(rows[e[1]])
                rows[e[1]] = {('z', len(cut_sources) - 1): Q(1)}
        elif o in ('INIT', 'CLEAR'):
            rows[e[1]] = {}
        elif o == 'SCALE':
            c = coeff(e)
            rows[e[1]] = {k: c * v for k, v in rows[e[1]].items()}
        elif o == 'COPY':
            c = coeff(e)
            rows[e[1]] = {k: c * v for k, v in rows[e[2]].items()}
        else:
            c = coeff(e)
            d = rows[e[1]]
            for k, v in rows[e[2]].items():
                x = d.get(k, 0) + c * v
                if x:
                    d[k] = x
                else:
                    d.pop(k, None)
    return rows[:pub], cut_sources


def endpoint_matrix(word):
    """A = I + sum E(Y_r, X_r) as sparse rows."""
    pub = word['public']
    A = [{r: Q(1)} for r in range(pub)]
    for r in word['live']:
        A[r + 112][r] = Q(1)
    return A


def mul(A, B):
    out = []
    for ra in A:
        d = {}
        for k, a in ra.items():
            for j, b in B[k].items():
                x = d.get(j, 0) + a * b
                if x:
                    d[j] = x
                else:
                    d.pop(j, None)
        out.append(d)
    return out


def identity(n):
    return [{r: Q(1)} for r in range(n)]


def rank_exact(rows, ncols):
    """Exact rank over Q of a sparse matrix given as list of dict rows (Fractions)."""
    piv = {}
    rk = 0
    for row in rows:
        v = dict(row)
        while v:
            c = min(v)
            if c in piv:
                p = piv[c]
                f = v[c] / p[c]
                for k, x in p.items():
                    y = v.get(k, 0) - f * x
                    if y:
                        v[k] = y
                    else:
                        v.pop(k, None)
            else:
                piv[c] = v
                rk += 1
                break
    return rk


def is_dyadic_unit(q):
    n = abs(q.numerator)
    d = q.denominator
    return n & (n - 1) == 0 and d & (d - 1) == 0


def is_dyadic(q):
    return q.denominator & (q.denominator - 1) == 0


# ----------------------------------------------------------------- elementary events of a matrix
def elementary(G, idx):
    """G: rows {reg:{col:Fraction}} supported on the registers idx; returns events ('A',d,s,c) / ('S',d,None,c)
    whose ordered application (state <- E state) realises G, by Euclid on dyadic entries (G in GL(Z[1/2]))."""
    n = len(idx)
    pos = {r: i for i, r in enumerate(idx)}
    rows = [{pos[k]: v for k, v in G[r].items()} for r in idx]
    colrows = [set() for _ in range(n)]
    for i, d in enumerate(rows):
        for j in d:
            colrows[j].add(i)
    ops = []

    def addrow(a, b, c):
        ops.append(('A', a, b, c))
        ra = rows[a]
        for k, v in rows[b].items():
            x = ra.get(k, 0) + c * v
            if x:
                ra[k] = x
                colrows[k].add(a)
            else:
                ra.pop(k, None)
                colrows[k].discard(a)

    def scale(a, c):
        ops.append(('S', a, None, c))
        rows[a] = {k: v * c for k, v in rows[a].items()}

    done = [False] * n
    piv = [None] * n
    remaining = set(range(n))
    while remaining:
        col = min(remaining, key=lambda c: sum(1 for r in colrows[c] if not done[r]))
        remaining.discard(col)
        while True:
            cand = [r for r in colrows[col] if not done[r]]
            need(cand, 'singular gauge matrix')
            un = [r for r in cand if is_dyadic_unit(rows[r][col])]
            if un:
                p = min(un, key=lambda r: len(rows[r]))
                break
            cand.sort(key=lambda r: abs(rows[r][col]))
            need(len(cand) >= 2, 'non-unit pivot: matrix is not in GL(Z[1/2])')
            a, b = cand[0], cand[1]
            q = rows[b][col] / rows[a][col]
            t = Q(2) ** math.floor(math.log2(abs(q))) * (1 if q > 0 else -1)
            addrow(b, a, -t)
        x = rows[p][col]
        if x != 1:
            scale(p, 1 / x)
        for r in list(colrows[col]):
            if r != p:
                addrow(r, p, -rows[r][col])
        done[p] = True
        piv[col] = p
    need(all(len(rows[piv[c]]) == 1 for c in range(n)), 'elimination did not reach a monomial matrix')
    loc = list(piv)
    at = {loc[c]: c for c in range(n)}
    for c in range(n):
        r = loc[c]
        if r == c:
            continue
        other = at[c]
        addrow(c, r, Q(1))
        addrow(r, c, Q(-1))
        addrow(c, r, Q(1))
        scale(r, Q(-1))
        loc[c] = c
        loc[other] = r
        at[r] = other
        at[c] = c
    ev = []
    for k, d, s, c in reversed(ops):
        ev.append(('A', idx[d], idx[s], -c) if k == 'A' else ('S', idx[d], None, 1 / c))
    return ev


def to_word_events(ev, frame):
    out = []
    for k, d, s, c in ev:
        out.append(['ADD', d, s, str(c), frame] if k == 'A' else ['SCALE', d, str(c), frame])
    return out
