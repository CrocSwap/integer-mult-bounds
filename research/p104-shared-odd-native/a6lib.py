"""Library of check_a6.py: exact Gaussian-dyadic checks of owned rises and of tensor width 2. Standard library only.

Code of this package. The mathematics read as text from CubeJerry #6914 (owned rises are one completed positive child between two
monomial adapters; width-f lift is the f-fold tensor power, so a global phase i^a becomes i^(a f)) and from unpaidmoon #6930
(a recorder phase integer is a width-1 residue; copy it onto a joint state and it fails; per-column execution matches).
The frame formula and gate conventions follow the retained native (Ali Romman, icekylinx, Dugongue, zxv and others) and are
re-implemented here from the formulas; the check is that this dense formula agrees with the recipes stored by the retained compiler
(different code path: tableau and zero-state, not a dense operator).
Apache-2.0.
"""
import gzip, json
from fractions import Fraction as Q
from collections import Counter

SIZE = 512


def need(ok, why):
    if not ok:
        raise ValueError(why)


def par(x):
    return x.bit_count() & 1


# ---------------------------------------------------------------- binary algebra
def span(basis):
    out = {0}
    for v in basis:
        need(type(v) is int and 0 < v < SIZE and v not in out, 'independent binary basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def extend(basis):
    """columns: the basis, then those unit vectors that enlarge the span (retained order)."""
    cols, sp = [], {0}
    for v in list(basis) + [1 << i for i in range(9)]:
        if v not in sp:
            cols.append(v)
            sp |= {x ^ v for x in sp}
    need(len(cols) == 9, 'complete basis extension')
    return cols


# ---------------------------------------------------------------- frames as circuits of table gates
# gate kinds (time order): ('D', tab) multiply by i^tab[address]; ('P', tab) address -> tab[address];
# ('C', q, s) Fourier axis q with sign s; ('G', k) global phase i^k.  A width-f gate acts on every column;
# only 'G' is not per column.
_frame_cache = {}


def frame_tables(basis):
    """(rank, forward permutation table, phase table) of the chart of the frame spanned by basis."""
    key = tuple(basis)
    if key in _frame_cache:
        return _frame_cache[key]
    r = len(basis)
    if r in (0, 9):
        out = (r, tuple(range(SIZE)), (0,) * SIZE)
    else:
        cols = extend(basis)
        fwd = [0] * SIZE
        for x in range(SIZE):
            v = 0
            for b in range(9):
                if (x >> b) & 1:
                    v ^= cols[b]
            fwd[x] = v
        bwd = [0] * SIZE
        for x, y in enumerate(fwd):
            bwd[y] = x
        icols = [bwd[1 << b] for b in range(9)]
        quad = [sum(((i == j) ^ par(icols[i] & icols[j])) << j for j in range(9)) for i in range(9)]
        lin = [(quad[i] >> i) & 1 for i in range(9)]
        ph = tuple(phase_at(quad, lin, x) for x in range(SIZE))
        out = (r, tuple(fwd), ph)
    _frame_cache[key] = out
    return out


def phase_at(quad, lin, x):
    s = sum(lin[i] for i in range(9) if (x >> i) & 1)
    for i in range(9):
        if (x >> i) & 1:
            s += 2 * par((quad[i] >> (i + 1)) & (x >> (i + 1)))
    return s % 4


def inv_tab(tab):
    out = [0] * len(tab)
    for x, y in enumerate(tab):
        out[y] = x
    return tuple(out)


def frame_circuit(basis):
    """T_U = D^-1 P^-1 F_r P D in time order (chart (P then D); retained: adjoint(chart) + fourier + chart)."""
    r, fwd, ph = frame_tables(basis)
    if r == 0:
        return []
    if r == 9:
        return [('C', 1 << i, 1) for i in range(9)]
    return ([('D', tuple((-p) % 4 for p in ph)), ('P', inv_tab(fwd))] + [('C', 1 << i, 1) for i in range(r)]
            + [('P', fwd), ('D', ph)])


def adjoint(circ):
    out = []
    for g in reversed(circ):
        if g[0] == 'D':
            out.append(('D', tuple((-p) % 4 for p in g[1])))
        elif g[0] == 'P':
            out.append(('P', inv_tab(g[1])))
        elif g[0] == 'C':
            out.append(('C', g[1], -g[2]))
        else:
            need(g[0] == 'G', 'gate kind')
            out.append(('G', (-g[1]) % 4))
    return out


def chart_change(frames, a, b):
    """T_b T_a^-1 in time order: T_a^-1 first."""
    return adjoint(frame_circuit(frames[a])) + frame_circuit(frames[b])


def monomial_tables(m):
    """own reading of a stored monomial record: address map, phase table, offset, global phase."""
    rows, quad, lin = m['matrix_rows'], m['quadratic_rows'], m['linear_Z4']
    need(len(rows) == len(quad) == len(lin) == 9, 'nine-axis monomial')
    fwd = tuple(sum(par(rows[i] & x) << i for i in range(9)) ^ m['offset'] for x in range(SIZE))
    ph = tuple(phase_at(quad, lin, x) for x in range(SIZE))
    need(len(set(fwd)) == SIZE, 'invertible address map')
    return fwd, ph


def monomial_circuit(m, f=1, mode='faithful'):
    """D, P(+offset), global phase.  mode: faithful i^(p f) | copied i^p | offby i^(p f + 1)."""
    fwd, ph = monomial_tables(m)
    p = m['phase']
    g = {'faithful': p * f, 'copied': p, 'offby': p * f + 1}[mode] % 4
    return [('D', ph), ('P', fwd), ('G', g)]


def recipe_circuit(rec, f=1, mode='faithful', sign=1, drop_left_phase=0):
    """right monomial, F_r on axes 0..r-1, left monomial (time order), as stored by lower_child."""
    r = rec['rank']
    if r == 0:
        need(rec['right'] is None, 'rank zero has no right factor')
        return monomial_circuit(rec['left'], f, mode)
    return monomial_circuit(rec['right'], f, mode) + [('C', 1 << i, sign) for i in range(r)] + monomial_circuit(rec['left'], f, mode)


# ---------------------------------------------------------------- sparse exact Gaussian execution, f columns
ROT = ((1, 0), (0, 1), (-1, 0), (0, -1))


def rot(a, b, k):
    k %= 4
    return ((a, b), (-b, a), (-a, -b), (b, -a))[k]


def run(circ, basis_addr, f=1):
    """apply circ to |basis_addr> over f 9-bit columns; returns (dict addr -> (re, im), den) reduced."""
    val, den = {basis_addr: (1, 0)}, 0
    mask = SIZE - 1
    for g in circ:
        t = g[0]
        out = {}
        if t == 'C':
            q, s = g[1], g[2]
            for col in range(f):
                out = {}
                qq = q << (9 * col)
                for ad, (a, b) in val.items():
                    for tgt, pr in ((ad, (a - s * b, b + s * a)), (ad ^ qq, (a + s * b, b - s * a))):
                        o = out.get(tgt)
                        out[tgt] = pr if o is None else (o[0] + pr[0], o[1] + pr[1])
                val = {k: v for k, v in out.items() if v != (0, 0)}
                den += 1
            continue
        if t == 'G':
            val = {ad: rot(a, b, g[1]) for ad, (a, b) in val.items()}
            continue
        tab = g[1]
        for ad, (a, b) in val.items():
            if t == 'D':
                k = 0
                for col in range(f):
                    k += tab[(ad >> (9 * col)) & mask]
                out[ad] = rot(a, b, k)
            else:
                need(t == 'P', 'gate kind')
                tgt = 0
                for col in range(f):
                    tgt |= tab[(ad >> (9 * col)) & mask] << (9 * col)
                need(tgt not in out, 'injective address map')
                out[tgt] = (a, b)
        val = out
    while den and all(not ((a | b) & 1) for a, b in val.values()):
        den -= 1
        val = {k: (a // 2, b // 2) for k, (a, b) in val.items()}
    return val, den


def gmul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def outer(col_x, col_y, f=2):
    """exact product state of two single-column outputs (dict, den) -> joint (dict, den)."""
    (dx, nx), (dy, ny) = col_x, col_y
    out = {}
    for ax, vx in dx.items():
        for ay, vy in dy.items():
            out[ax | (ay << 9)] = gmul(vx, vy)
    den = nx + ny
    while den and all(not ((a | b) & 1) for a, b in out.values()):
        den -= 1
        out = {k: (a // 2, b // 2) for k, (a, b) in out.items()}
    return out, den


# ---------------------------------------------------------------- adapter records (monomial -> S, CZ, XROW, NOT, I)
def record_list(m):
    rows, quad, lin = list(m['matrix_rows']), m['quadratic_rows'], m['linear_Z4']
    recs = []
    for i, v in enumerate(lin):
        need(0 <= v < 4 and v % 2 == (quad[i] >> i) & 1, 'unit quadratic phase convention')
        recs += [('S', i)] * v
    for i in range(9):
        for j in range(i + 1, 9):
            need(((quad[i] >> j) & 1) == ((quad[j] >> i) & 1), 'symmetric quadratic phase')
            if (quad[i] >> j) & 1:
                recs.append(('CZ', i, j))
    red, elim = rows, []
    for c in range(9):
        piv = next((r for r in range(c, 9) if (red[r] >> c) & 1), None)
        need(piv is not None, 'invertible address matrix')
        if piv != c:
            red[piv], red[c] = red[c], red[piv]
            elim += [('XROW', c, piv), ('XROW', piv, c), ('XROW', c, piv)]
        for r in range(9):
            if r != c and (red[r] >> c) & 1:
                red[r] ^= red[c]
                elim.append(('XROW', r, c))
    need(red == [1 << i for i in range(9)], 'eliminated to identity')
    recs += list(reversed(elim))
    recs += [('NOT', i) for i in range(9) if (m['offset'] >> i) & 1]
    recs += [('I',)] * m['phase']
    return recs


def record_action(recs, addr, f, ipf=True):
    """(address, phase mod 4) after executing the record list on f columns; 'I' is global: f times if ipf else once."""
    res, ph = addr, 0
    for r in recs:
        k = r[0]
        if k == 'I':
            ph += f if ipf else 1
            continue
        for col in range(f):
            o = 9 * col
            i = r[1] + o
            if k == 'NOT':
                res ^= 1 << i
            elif k == 'XROW':
                res ^= ((res >> (r[2] + o)) & 1) << i
            elif k == 'S':
                ph += (res >> i) & 1
            elif k == 'CZ':
                ph += 2 * ((res >> i) & 1) * ((res >> (r[2] + o)) & 1)
            else:
                raise ValueError('record kind')
    return res, ph % 4


# ---------------------------------------------------------------- word scan: owned lifetimes, rises
def load_word(path):
    return json.load(gzip.open(path, 'rt'))


def smooth(m, primes):
    m = abs(m)
    for p in primes:
        while m % p == 0:
            m //= p
    return m == 1


def scan(w, primes=(2,), descending_only=False):
    """exact chronological scan of owned lifetimes returns (rises, lifetimes, census)."""
    n = w['public']
    N = n + w['owned_fields']
    sp = [span(f) for f in w['frames']]
    dims = [len(f) for f in w['frames']]
    cur = list(w['initial']) + [None] * w['owned_fields']
    rows = [{r: Q(1)} for r in range(n)] + [{} for _ in range(w['owned_fields'])]
    live, lives, rises, paid = {}, [], [], Counter()
    dirty = peak = 0
    strict_rej = []
    hosted = w['hosted']
    groups = {'Y2': set(hosted['Y2']), 'X': set(w['live']), 'X2': set(hosted['X2'])}
    owned_reads = {k: [] for k in groups}
    for i, e in enumerate(w['program']):
        op, r = e[:2]
        need(isinstance(r, int) and 0 <= r < N, 'role')
        if op == 'INIT':
            need(r >= n and cur[r] is None and r not in live, 'exclusive owned birth (public alias rejected)')
            cur[r] = e[2]
            rows[r] = {}
            life = dict(role=r, begin=i, birth=e[2], rises=[], reads=[], writes=[], moves=[])
            live[r] = life
            lives.append(life)
            peak = max(peak, len(live))
        elif op == 'CLEAR':
            need(r in live and cur[r] == e[2], 'owned clear at the current chart')
            life = live.pop(r)
            life.update(end=i, dirty=bool(rows[r]))
            dirty += bool(rows[r])
            cur[r] = None
            rows[r] = {}
        elif op == 'MOVE':
            _, _, a, b, private = e
            need(cur[r] == a and bool(private) == (r in live), 'move owns its current field')
            up, down = sp[a] < sp[b], sp[b] < sp[a]
            need(up or down, 'strict nested move')
            need(private or up, 'public moves ascend')
            paid[abs(dims[a] - dims[b])] += 1
            if private:
                live[r]['moves'].append(i)
                if up:
                    live[r]['rises'].append(i)
                    rises.append(dict(event=i, role=r, start=a, end=b, rank=dims[b] - dims[a]))
                    if descending_only:
                        strict_rej.append(i)
            cur[r] = b
        else:
            need(op in ('ADD', 'COPY', 'SCALE'), 'opcode')
            fr = e[-1]
            need(cur[r] is not None and cur[r] == fr, 'scalar destination chart')
            q = Q(e[2] if op == 'SCALE' else e[3])
            need(q != 0 and smooth(q.denominator, primes), 'scalar alphabet')
            if r in live:
                live[r]['writes'].append(i)
            if op == 'SCALE':
                need(smooth(q.numerator, primes), 'unit SCALE')
                rows[r] = {k: v * q for k, v in rows[r].items()}
            else:
                s = e[2]
                need(s != r and 0 <= s < N and cur[s] == fr, 'scalar source chart, distinct field')
                if op == 'COPY':
                    need(r in live and not rows[r], 'COPY into an owned zero')
                if s in live:
                    live[s]['reads'].append(i)
                if r in live:
                    for k, g in groups.items():
                        if s in g:
                            owned_reads[k].append(i)
                for k, v in rows[s].items():
                    u = rows[r].get(k, Q(0)) + q * v
                    if u:
                        rows[r][k] = u
                    else:
                        rows[r].pop(k, None)
    need(not live and all(c is None for c in cur[n:]), 'every owned lifetime closes')
    need(cur[:n] == w['final'], 'public final charts')
    hist = Counter(x['rank'] for x in rises)
    before = [l['begin'] for l in lives if l['rises'] and any(j < l['rises'][0] for j in l['reads'])]
    between = [l['begin'] for l in lives if len(l['rises']) > 1 and
               any(l['rises'][0] < j < l['rises'][-1] for j in l['reads'] + l['writes'])]
    census = dict(events=len(w['program']), lifetimes=len(lives), peak=peak, dirty_clears=dirty,
                  rises=len(rises), rise_hist=dict(sorted(hist.items())), rise_mass=sum(x['rank'] for x in rises),
                  paid=dict(sorted(paid.items())), read_before_first_rise=len(before), contact_between_rises=len(between),
                  owned_reads={k: len(v) for k, v in owned_reads.items()}, owned_reads_total=sum(len(v) for v in owned_reads.values()),
                  strict_rejected=strict_rej)
    return rises, lives, census
