#!/usr/bin/env python3
"""Exact checks for the chain-root caller on the merged G20 conjugation word.
Python 3.12, standard library only.  Expected marker: PASS_CHAIN_ROOT_ON_G20_WORD

 1 retained bytes against retained/SOURCE-PINS.json
 2 caller: rebuild, reduce, reverse; forward and transpose engines over F2[q,D^+-1]/(q^2-1),
   true inverse over Z[q,D^+-1]/(q^2-1), and forward*reversed = identity
 3 local word: own scalar and physical replay at address moduli 101 and 10201, forward and adjoint,
   all 685 columns; exact rational port lemma giving the LOCAL form
 4 literal 18-call stream: per-call checks, query descriptors, a second pass recounting the invoice
 5 two rational-interval engines: crossing, tested margin, tails, uniform guards
 6 fees, compiler cutoffs, cover list, five ordinary levels
 7 the alternative ambient-134 finite comparison
 8 controls
All failures raise ValueError, so -O changes nothing.
"""
import gzip, hashlib, json, sys
from collections import Counter
from decimal import Decimal as Dec, getcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chainroot  # noqa: E402

G = HERE / 'retained/g20'
V = 111
RAW_LO, RAW_HI = Q('.00380058610514'), Q('.00380058610515')
TESTED = Q('.00380058610513'); UNIFORM = Q('.00380058610512'); COVER = Q(1, 10**14)
RHO = Q(1, 100); RESERVE = Q(1, 2**48); TENSOR = 2048; CUT, FLOOR = 13, 14; U_TAIL = Q(1, 5)
GRID = 10**15; CMAX = Q('.0039'); AMBIENT = 134; LEVELS = 5


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def rd(name):
    b = (G / name).read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)


def pins():
    rows = json.loads((HERE / 'retained/SOURCE-PINS.json').read_text())
    for r in rows:
        b = (HERE / r['local']).read_bytes()
        need(len(b) == r['bytes'] and hashlib.sha256(b).hexdigest() == r['sha256'], ('sha256', r['local']))
        need(hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() == r['git_blob'], ('blob', r['local']))
    return len(rows)


# ------------------------------------------------------------------------------ 2 caller
def to_binary(c):
    ev = []
    for e in c['events']:
        if e[0] in ('LAMBDA', 'SCALE'):
            if e[0] == 'SCALE':
                need(abs(Q(e[2])) == 1, 'unit scale')
            continue
        if e[0] == 'ADD':
            x = Q(e[3]); need(x.denominator == 1, 'integral coefficient')
            if int(x) % 2:
                ev.append(e[:3])
        elif e[0] == 'QUERY':
            ev.append(e[:3])
        else:
            need(e[0] in ('SWAP', 'LOCAL', 'IDLE_ONE'), 'opcode')
            ev.append(e)
    diag = [{'q': d[0] % 2, 'stages': [s for s, x in enumerate(d[2:], 1) if x]} for d in c['diagonal']]
    return {'roles': c['roles'], 'stages': c['stages'], 'events': ev, 'diagonal': diag}


def reversed_caller(b):
    return dict(b, events=[e[:] for e in reversed(b['events'])])


def f2_forward(w, sign=1):
    """Rows over F2[q,D^+-1]/(q^2-1).  sign=-1 reads each LOCAL and IDLE_ONE as its true inverse."""
    n, wd = w['roles'], w['stages'] + 1; zero = (0,) * wd
    rows = [[{zero} if i == j else set() for j in range(n)] for i in range(n)]

    def sh(row, ss=(), q=0):
        out = []
        for cell in row:
            cc = set()
            for key in cell:
                k = list(key); k[0] ^= q
                for s in ss: k[s] += sign
                cc ^= {tuple(k)}
            out.append(cc)
        return out
    seen = []
    for e in w['events']:
        op = e[0]
        if op == 'ADD': rows[e[1]] = [x ^ y for x, y in zip(rows[e[1]], rows[e[2]])]
        elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
        elif op == 'QUERY': rows[e[1]] = [x ^ y for x, y in zip(rows[e[1]], sh(rows[e[2]], q=1))]
        elif op == 'LOCAL':
            _, s, src, dst = e; seen.append(s)
            rows[dst] = [x ^ y for x, y in zip(rows[dst], sh(rows[src], q=1))]
            rows[src], rows[dst] = sh(rows[src], [s]), sh(rows[dst], [s])
        elif op == 'IDLE_ONE': rows[e[1]] = sh(rows[e[1]], e[2])
        else: raise ValueError('opcode ' + op)
    need(sorted(seen) == list(range(1, wd)), 'every native stage once')
    for i, d in enumerate(w['diagonal']):
        key = (d['q'],) + tuple(sign * int(s in d['stages']) for s in range(1, wd))
        for j in range(n):
            need(rows[i][j] == ({key} if i == j else set()), ('F2 forward', i, j))
    return n * n


def f2_transpose(w):
    """Second engine: pull each output functional back through the events."""
    n, wd = w['roles'], w['stages']; zero = (0,) * (wd + 1); done = 0

    def sh(a, ss=(), q=0):
        out = set()
        for key in a:
            k = list(key); k[0] ^= q
            for s in ss: k[s] += 1
            out ^= {tuple(k)}
        return out
    for o in range(n):
        f = [set() for _ in range(n)]; f[o] = {zero}
        for e in reversed(w['events']):
            op = e[0]
            if op == 'ADD': f[e[2]] = f[e[2]] ^ f[e[1]]
            elif op == 'SWAP': f[e[1]], f[e[2]] = f[e[2]], f[e[1]]
            elif op == 'QUERY': f[e[2]] = f[e[2]] ^ sh(f[e[1]], q=1)
            elif op == 'LOCAL':
                _, s, a, b = e
                f[a] = sh(f[a], [s]) ^ sh(f[b], [s], 1); f[b] = sh(f[b], [s])
            elif op == 'IDLE_ONE': f[e[1]] = sh(f[e[1]], e[2])
            else: raise ValueError('opcode ' + op)
        d = w['diagonal'][o]; key = (d['q'],) + tuple(int(s in d['stages']) for s in range(1, wd + 1))
        for i in range(n):
            need(f[i] == ({key} if i == o else set()), ('F2 transpose', o, i))
            done += 1
    return done


def main_fixture(w, m):
    """Evaluate the caller on paired addresses: q swaps the head pair, D_s swaps the seven pairs of block s."""
    n, S = w['roles'], w['stages']; pt = tuple(pow(3, i + 1, m) for i in range(2 + 14 * S))

    def head(x): return (x[1], x[0]) + x[2:]

    def block(x, s):
        a = 2 + 14 * (s - 1); return x[:a] + tuple(x[a + 7:a + 14]) + tuple(x[a:a + 7]) + x[a + 14:]

    def blocks(x, ss):
        for s in ss: x = block(x, s)
        return x
    rows = [{pt: 1 << i} for i in range(n)]

    def mv(c, f):
        o = {}
        for k, v in c.items():
            y = f(k); z = o.get(y, 0) ^ v
            if z: o[y] = z
            else: o.pop(y, None)
        return o

    def xor(a, b):
        o = dict(a)
        for k, v in b.items():
            z = o.get(k, 0) ^ v
            if z: o[k] = z
            else: o.pop(k, None)
        return o
    for e in w['events']:
        op = e[0]
        if op == 'ADD': rows[e[1]] = xor(rows[e[1]], rows[e[2]])
        elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
        elif op == 'QUERY': rows[e[1]] = xor(rows[e[1]], mv(rows[e[2]], head))
        elif op == 'LOCAL':
            _, s, a, b = e; rows[b] = xor(rows[b], mv(rows[a], head)); rows[a] = mv(rows[a], lambda x, s=s: block(x, s)); rows[b] = mv(rows[b], lambda x, s=s: block(x, s))
        else: rows[e[1]] = mv(rows[e[1]], lambda x, ss=e[2]: blocks(x, ss))
    for i, d in enumerate(w['diagonal']):
        y = blocks(head(pt) if d['q'] else pt, d['stages']); need(rows[i] == {y: 1 << i}, ('main fixture', i))
    return n


def z_inverse(c):
    """The integral caller's true inverse, event by event, over Z[q,D^+-1]/(q^2-1)."""
    n, wd = c['roles'], c['stages'] + 1; zero = (0,) * wd
    rows = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]

    def sh(row, ss=(), q=0, sgn=-1):
        out = []
        for cell in row:
            d = {}
            for k, v in cell.items():
                k = list(k); k[0] ^= q
                for s in ss: k[s] += sgn
                d[tuple(k)] = v
            out.append(d)
        return out

    def acc(a, b, m):
        for k, v in b.items():
            a[k] = a.get(k, 0) + m * v
            if not a[k]: del a[k]
    for e in reversed(c['events']):
        op = e[0]
        if op == 'ADD':
            for a, b in zip(rows[e[1]], rows[e[2]]): acc(a, b, -int(Q(e[3])))
        elif op == 'SCALE':
            m = int(Q(e[2])); rows[e[1]] = [{k: v * m for k, v in cell.items()} for cell in rows[e[1]]]
        elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
        elif op == 'QUERY':
            for a, b in zip(rows[e[1]], sh(rows[e[2]], q=1)): acc(a, b, -1)
        elif op == 'LOCAL':
            _, s, src, dst = e
            rows[src], rows[dst] = sh(rows[src], [s]), sh(rows[dst], [s])
            for a, b in zip(rows[dst], sh(rows[src], q=1)): acc(a, b, -1)
        elif op == 'IDLE_ONE': rows[e[1]] = sh(rows[e[1]], e[2])
        else: need(op == 'LAMBDA', 'opcode')
    for i, d in enumerate(c['diagonal']):
        key = (d[0] % 2,) + tuple(-d[1 + s] for s in range(1, wd))
        for j in range(n):
            need(rows[i][j] == ({key: 1} if i == j else {}), ('Z inverse', i, j))
    return n * n


# ------------------------------------------------------------------------------ 3 local word
class Geo:
    def __init__(self, frames):
        self.f = frames; self.dim = {int(k): v['dim'] for k, v in frames.items()}; self.cache = {}; self.pq = {}

    def proj(self, fid):
        """Exact orthogonal projector onto the B span of a frame."""
        if fid in self.pq: return self.pq[fid]
        b = [[Q(x) for x in row] for row in self.f[str(fid)]['B']]
        if not b:
            out = [[Q(0)] * 8 for _ in range(8)]
        else:
            k = len(b); gram = [[sum(x * y for x, y in zip(r, s)) for s in b] + [Q(int(i == j)) for j in range(k)] for i, r in enumerate(b)]
            for j in range(k):
                p = next(i for i in range(j, k) if gram[i][j]); gram[j], gram[p] = gram[p], gram[j]
                v = gram[j][j]; gram[j] = [x / v for x in gram[j]]
                for i in range(k):
                    if i != j and gram[i][j]:
                        v = gram[i][j]; gram[i] = [x - v * y for x, y in zip(gram[i], gram[j])]
            inv = [r[k:] for r in gram]
            out = [[sum(b[a][i] * inv[a][c] * b[c][j] for a in range(k) for c in range(k)) for j in range(8)] for i in range(8)]
        self.pq[fid] = out
        return out

    def pm(self, fid, m):
        key = (fid, m)
        if key not in self.cache:
            self.cache[key] = tuple(tuple(x.numerator * pow(x.denominator, -1, m) % m for x in r) for r in self.proj(fid))
        return self.cache[key]

    def resid(self, s, t, m):
        key = (s, t, m)
        if key not in self.cache:
            a, b = self.pm(s, m), self.pm(t, m)
            self.cache[key] = tuple(tuple((x - y) % m for x, y in zip(r, q)) for r, q in zip(a, b))
        return self.cache[key]

    def nested(self, s, t, k):
        lo, hi = (s, t) if self.dim[s] < self.dim[t] else (t, s)
        need(0 < k < 8 and self.dim[hi] - self.dim[lo] == k, 'proper residual rank')
        need(all(sum(Q(x) * Q(y) for x, y in zip(a, b)) == 0 for a in self.f[str(lo)]['B'] for b in self.f[str(hi)]['A']), 'nested frames')


def move(p, x, m):
    """Paired-address reflection: the antisymmetric part goes through I-2P, the symmetric part is fixed."""
    z = [sum(a * (x[j] - x[15 - j]) for j, a in enumerate(r)) % m for r in p]; o = list(x)
    for i in range(8):
        o[i] = (o[i] - z[i]) % m; o[15 - i] = (o[15 - i] + z[i]) % m
    return tuple(o)


def expected_rows(w):
    own = set(w['owned']); n = len(w['start'])
    return [0 if i in own else (1 << i) ^ ((1 << (i - V)) if V <= i < 2 * V else 0) for i in range(n)]


def local_scalar(w, geo):
    own = set(w['owned']); st = w['start'][:]; rows = [1 << i for i in range(len(st))]; paid = Counter(); peak = 1; norm = [1] * len(st)
    for e in w['records']:
        op, d = e[:2]
        if op == 'ERASE': need(d in own, 'only owned erasure'); rows[d] = norm[d] = 0; st[d] = e[2]
        elif op == 'INIT': need(d in own and rows[d] == 0, 'zero init'); st[d] = e[2]
        elif op == 'ADD':
            s, f = e[2:]; need(d != s and st[d] == st[s] == f, 'common frame ADD'); rows[d] ^= rows[s]; norm[d] += norm[s]; peak = max(peak, norm[d])
        elif op in ('Q', 'ZERO_Q'):
            s, t, k = e[2:]; need(st[d] == s, 'current frame'); geo.nested(s, t, k); st[d] = t
            if op == 'Q': paid[k] += 1
            else: need(rows[d] == 0, 'free move on zero only')
        else: raise ValueError('local opcode')
    need(st == w['final'], 'final frames'); need(rows == expected_rows(w), 'all 685 scalar columns')
    return paid, peak.bit_length()


def local_physical(w, geo, m):
    own = set(w['owned']); pt = tuple(v % m for v in (1, 2, 4, 8, 16, 32, 64, 128, 3, 5, 7, 11, 13, 17, 19, 23))
    fields = [{pt: 1 << i} for i in range(len(w['start']))]; st = w['start'][:]
    for e in w['records']:
        op, d = e[:2]
        if op == 'ERASE': fields[d] = {}; st[d] = e[2]
        elif op == 'INIT': st[d] = e[2]
        elif op == 'ADD':
            for x, v in fields[e[2]].items():
                z = fields[d].get(x, 0) ^ v
                if z: fields[d][x] = z
                else: fields[d].pop(x, None)
        else:
            s, t = e[2:4]; st[d] = t
            if op == 'Q':
                r = geo.resid(s, t, m); fields[d] = {move(r, x, m): v for x, v in fields[d].items()}
    exp = expected_rows(w)
    for o, row in enumerate(exp):
        want = {}
        for i in range(len(exp)):
            if row >> i & 1:
                y = move(geo.pm(w['final'][o], m), move(geo.pm(w['start'][i], m), pt, m), m); want[y] = want.get(y, 0) ^ (1 << i)
        need(fields[o] == {k: v for k, v in want.items() if v}, ('physical column', o))
    return len(exp)


def local_adjoint(w, geo, m):
    own = set(w['owned']); n = len(w['start']); pt = tuple(v % m for v in (1, 3, 9, 27, 2, 6, 18, 54, 5, 15, 45, 34, 7, 21, 63, 88))
    fields = [{pt: 1 << i} for i in range(n)]
    for e in reversed(w['records']):
        op, d = e[:2]
        if op == 'ADD':
            for x, v in fields[d].items():
                z = fields[e[2]].get(x, 0) ^ v
                if z: fields[e[2]][x] = z
                else: fields[e[2]].pop(x, None)
        elif op in ('ERASE', 'INIT', 'ZERO_Q'):
            fields[d] = {}
        else:
            r = geo.resid(e[2], e[3], m); fields[d] = {move(r, x, m): v for x, v in fields[d].items()}
    exp = expected_rows(w)
    for i in range(n):
        want = {}
        for o in range(n):
            if exp[o] >> i & 1:
                y = move(geo.pm(w['start'][i], m), move(geo.pm(w['final'][o], m), pt, m), m); want[y] = want.get(y, 0) ^ (1 << o)
        need(fields[i] == {k: v for k, v in want.items() if v}, ('adjoint column', i))
    return n


def port_lemma(w, geo):
    """On each port P(entry X)=I, P(exit Y)=0, P(exit X)+P(entry Y)=I, P(exit X)P(entry Y)=0.
    So with q=T(exit X), D=T(entry Y): X'=Dx and Y'=D(y+qx), the LOCAL form, in both orientations."""
    I = [[Q(int(i == j)) for j in range(8)] for i in range(8)]; lines = []
    for p in range(V):
        a, b, c, d = w['start'][p], w['final'][p], w['start'][p + V], w['final'][p + V]
        need((geo.dim[a], geo.dim[b], geo.dim[c], geo.dim[d]) == (8, 1, 7, 0), 'port dimensions')
        Pa, Pb, Pc, Pd = map(geo.proj, (a, b, c, d))
        need(Pa == I, 'entry X full'); need(all(not x for r in Pd for x in r), 'exit Y empty')
        need([[x + y for x, y in zip(r, s)] for r, s in zip(Pb, Pc)] == I, 'complementary head and body')
        need(all(sum(Pb[i][k] * Pc[k][j] for k in range(8)) == 0 for i in range(8) for j in range(8)), 'orthogonal head and body')
        lines.append(b)
    return lines


# ------------------------------------------------------------------------------ 4 literal stream
def emit_stream(w, frames, c, corrupt=None):
    own = w['owned']; ownset = set(own); ret = [r for r in range(2 * V, len(w['start'])) if r not in ownset]
    need(len(ret) == 415 and len(own) == 48, 'helper and owned counts')
    m = c['roles'] * V; N = m + 18 * 415; W = list(range(N, N + 48)); center = W[0]; ow = dict(zip(own, W)); ho = {r: i for i, r in enumerate(ret)}
    val = [1 << i for i in range(N + 48)]; norm = [1] * (N + 48); ver = [0] * (N + 48); epo = [0] * (N + 48)
    pref = hashlib.sha256(); desc = hashlib.sha256(); ops = Counter(); paid = Counter(); peak = 1; nev = 0; lines = []; episodes = 0; ndesc = 0; targets = []

    def emit(e):
        nonlocal nev
        b = (json.dumps(e, separators=(',', ':')) + '\n').encode(); pref.update(b); lines.append(b); nev += 1; ops[e[0]] += 1

    def clear(d, why):
        need(d in W, 'only owned erasure'); val[d] = norm[d] = 0; ver[d] += 1; epo[d] += 1; emit(['OWNED_CLEAR', d, why])

    def add(d, s, why):
        nonlocal peak
        need(d != s, 'distinct'); val[d] ^= val[s]; norm[d] += norm[s]; peak = max(peak, norm[d]); ver[d] += 1; emit(['ADD', d, s, why])

    def query(d, k, detail):
        nonlocal ndesc
        need(k > 0, 'positive rank')
        desc.update(json.dumps([nev, pref.hexdigest(), d, ver[d], epo[d], k, detail, hashlib.sha256(val[d].to_bytes((N + 55) // 8, 'little')).hexdigest()], separators=(',', ':')).encode() + b'\n')
        ndesc += 1; paid[k] += 1; ver[d] += 1; emit(['QUERY', d, k, detail])
    for d in W: clear(d, 'ENTRY_DIRTY')
    idx = 0
    for e in c['events']:
        op = e[0]
        if op == 'ADD':
            for p in range(V): add(e[1] * V + p, e[2] * V + p, 'BANK')
        elif op == 'SWAP':
            for p in range(V):
                a, b = e[1] * V + p, e[2] * V + p; add(a, b, 'SWAP'); add(b, a, 'SWAP'); add(a, b, 'SWAP')
        elif op == 'QUERY':
            for p in range(V):
                src, dst = e[2] * V + p, e[1] * V + p; need(val[center] == 0, 'clean thin scratch'); v = ver[src]
                add(center, src, ['THIN', p]); query(center, 1, ['THIN', p]); add(dst, center, ['THIN', p]); need(ver[src] == v, 'immutable thin source'); clear(center, ['THIN', p]); episodes += 1
        elif op == 'IDLE_ONE':
            for p in range(V): query(e[1] * V + p, 7 * len(e[2]), ['IDLE_ONE', e[2], p])
        elif op == 'LOCAL':
            _, stage, src, dst = e; base = m + 415 * idx; idx += 1

            def owner(r):
                if r in ow: return ow[r]
                if r < V: return src * V + r
                if r < 2 * V: return dst * V + r - V
                return base + ho[r]
            for bank in (src, dst):
                for p in range(V): emit(['PAID_PORT_ROUTE', stage, bank * V + p, p, 'ENTRY'])
            sx = [val[owner(i)] for i in range(V)]; sy = [val[owner(V + i)] for i in range(V)]; before = {r: val[owner(r)] for r in ret}
            st = w['start'][:]; lp = Counter(); live = set()
            for ix, r in enumerate(w['records']):
                t, d = r[:2]; gd = owner(d)
                if corrupt == 'skip_record' and idx == 1 and ix == 4000: continue
                if t == 'ERASE':
                    clear(gd, ['LOCAL', stage, ix]); st[d] = r[2]
                    if gd in live: live.discard(gd); episodes += 1
                elif t == 'INIT':
                    need(val[gd] == 0, 'zero init'); st[d] = r[2]; emit(['OWNED_ZERO_HEADER', gd, r[2], stage])
                elif t == 'ADD':
                    s, f = r[2:]; need(st[d] == st[s] == f, 'common frame')
                    if gd in W: live.add(gd)
                    add(gd, owner(s), ['LOCAL', stage, f, ix])
                else:
                    a, b, k = r[2:]; need(st[d] == a, 'current frame'); st[d] = b
                    if t == 'Q': query(gd, k, ['LOCAL', stage, a, b, ix]); lp[k] += 1
                    else: need(val[gd] == 0, 'zero only free frame'); emit(['WHOLE_ZERO_FRAME', gd, a, b, k, stage])
            need(not live and st == w['final'], 'no live owned state at return')
            need(all(val[owner(i)] == sx[i] and val[owner(V + i)] == sy[i] ^ sx[i] for i in range(V)), 'all main inputs')
            need(all(val[owner(r)] == before[r] for r in ret) and all(val[x] == 0 for x in W), 'helpers and owned return')
            for bank in (src, dst):
                for p in range(V): emit(['PAID_PORT_ROUTE', stage, bank * V + p, p, 'RETURN'])
            for r in ret:
                targets.append([base + ho[r], abs(frames[str(w['start'][r])]['dim'] - frames[str(w['final'][r])]['dim']), 'HELPER'])
        else: raise ValueError('opcode ' + op)
    for d in W: clear(d, 'EXIT')
    need(val == [1 << i for i in range(N)] + [0] * 48, 'identity on all raw inputs, all dirty owned columns annihilated')
    for r, d in enumerate(c['diagonal']):
        for p in range(V): targets.append([r * V + p, d['q'] + 7 * len(d['stages']), 'MAIN'])
    return dict(lines=lines, paid=paid, ops=ops, events=nev, stream_sha256=pref.hexdigest(), descriptor_sha256=desc.hexdigest(), descriptors=ndesc,
                majorant_bits=peak.bit_length(), episodes=episodes, targets=targets, originals=N, owned=48)


def second_pass(s):
    """Recount the bill from emitted lines alone."""
    n, own = s['originals'], s['owned']; val = [1 << i for i in range(n + own)]; ok = [True] * (n + own); paid = Counter(); ops = Counter()
    for b in s['lines']:
        e = json.loads(b); op, d = e[:2]; ops[op] += 1
        if op == 'ADD': val[d] ^= val[e[2]]
        elif op == 'OWNED_CLEAR': need(n <= d < n + own, 'owned only'); val[d] = 0
        elif op == 'QUERY': need(0 <= d < n + own and e[2] > 0, 'query'); paid[e[2]] += 1
        else: need(op in ('PAID_PORT_ROUTE', 'OWNED_ZERO_HEADER', 'WHOLE_ZERO_FRAME'), 'event')
    need(val == [1 << i for i in range(n)] + [0] * own, 'second pass endpoint')
    need(paid == s['paid'] and ops == s['ops'], 'second pass bill')
    t = Counter(x[1] for x in s['targets']); need(len({x[0] for x in s['targets']}) == n == sum(t.values()), 'one target per independent input')
    return t, paid


# ------------------------------------------------------------------------------ 5 interval engines
G1 = 10**100


def down(x): return Q((x * G1).__floor__(), G1)
def up(x): return Q(-((-x * G1).__floor__()), G1)


def atanh2(z, terms=90):
    z = Q(z); a = abs(z); s = Q(0); zz = z * z; p = z
    for n in range(terms):
        s += p / (2 * n + 1); p = up(p * zz) if z > 0 else down(p * zz)
    rem = 2 * a**(2 * terms + 1) / (1 - zz)
    return down(2 * s - rem), up(2 * s + rem)


LN2 = atanh2(Q(1, 3))
_ln = {}


def ln_i(r):
    if r not in _ln:
        k = r.bit_length(); lo, hi = atanh2((Q(r, 2**k) - 1) / (Q(r, 2**k) + 1))
        _ln[r] = (k * LN2[0] + lo, k * LN2[1] + hi)
    return _ln[r]


def exp_pos(y, rnd):
    k = 40; x = rnd(y / 2**k); s = Q(1); p = Q(1)
    for n in range(1, 24):
        p = rnd(p * x / n); s += p
    s += (2 * abs(p) * abs(x) if rnd is up else -2 * abs(p) * abs(x))
    for _ in range(k): s = rnd(s * s)
    return s


_pw = {}


def pw1(r, s):
    """Engine one: outward rational enclosure of r^s for s>=0."""
    if r == 1: return Q(1), Q(1)
    if (r, s) not in _pw:
        a, b = ln_i(r); need(s >= 0, 'exponent'); _pw[r, s] = (exp_pos(s * a, down), exp_pos(s * b, up))
    return _pw[r, s]


def pw2(r, s):
    """Engine two: Decimal ln/exp at 130 digits, widened by 1e-110."""
    if r == 1: return Q(1), Q(1)
    getcontext().prec = 130
    v = ((Dec(s.numerator) / Dec(s.denominator)) * Dec(r).ln()).exp(); e = Q(1, 10**110); x = Q(v)
    return x - e, x + e


def mom(h, s, pw):
    lo = hi = Q(0)
    for r, n in h.items():
        a, b = pw(r, s); lo += n * a; hi += n * b
    return lo, hi


def margin(T, P, c, pw):
    a, b = mom(T, 1 - c, pw), mom(P, 1 - c, pw); return a[0] - b[1], a[1] - b[0]


def ratio(a, b): return a[0] / b[1], a[1] / b[0]


def tails(T, P, pw, tested=TESTED, cut=CUT, floor=FLOOR, u=U_TAIL):
    t = 1 - tested; Tt = mom(T, t, pw); n = sum(T.values())
    alpha = ratio(mom(P, t, pw), Tt)
    pu = mom(P, t + u, pw); cu = pw(cut, u); gamma = ratio(pu, (cu[0] * Tt[0], cu[1] * Tt[1]))
    cc = pw(cut, tested); delta = (Q(n * floor) / (cc[1] * Tt[1]), Q(n * floor) / (cc[0] * Tt[0]))
    return alpha, gamma, delta


def strict_grid(x, den): return Q(-((-x.numerator * den) // x.denominator) - 1, den)


def cutoffs(tested, uniform, v):
    t, z = 1 - tested, 1 - uniform; z0 = (t + z) / 2; gap = z0 - t; h = Q(1, 64)
    rhs = gap * (5 + 8 * h) * v + 1 + 8 * v * (1 - z0); h0 = (rhs / (h * gap)).__floor__() + 1; h1 = (h0 * (1 - z0) / (z - z0)).__floor__() + 1
    need(h0 >= 8 * v and h0 * h * gap > rhs and h1 * (z - z0) > h0 * (1 - z0), 'strict cutoffs')
    return h0, h1


# ------------------------------------------------------------------------------ 7 alternative finite comparison
def ambient_cap(T, P, c, tested, A0, gap=Q(1, 10**10), v=768, cut=15, floor=16, u=Q(1, 5)):
    """The ambient-cap reading: ambient A0^v with separated paid cut^v and target floor^v."""
    t = 1 - tested; Tt = mom(T, t, pw1); a = ratio(mom(P, t, pw1), Tt); cu = pw1(cut, u); fu = pw1(floor, u)
    g = ratio(mom(P, t + u, pw1), (cu[0] * Tt[0], cu[1] * Tt[1])); lt = mom(T, t - u, pw1); l = ratio((fu[0] * lt[0], fu[1] * lt[1]), Tt)
    aa, gg, ll = (up(x[1]) for x in (a, g, l)); norm = 1 / (1 + v * (1 - aa)) + 2 * gg**v + ll**v; need(norm < 1, 'paid plus discarded below one')
    d = 2
    while not cut**d < floor**(d - 1): d += 1
    theta = Q(d - 1, d); need(2 * cut**(v * d) <= A0**(v * (d - 1)), 'shifted exit comparison')
    la = ln_i(A0)
    # eta = t*A0^(-v*C), base = A0^(v*C), compared through exact logarithm enclosures
    lnb = (v * tested * la[0], v * tested * la[1]); lnt = (-(1 - t) - (1 - t)**2, -(1 - t))
    lnth = (-sum(Q(1, d)**k / k for k in range(1, 200)) - Q(2, d**200), -sum(Q(1, d)**k / k for k in range(1, 200)))
    p = 1
    while not (p * lnth[1] < lnt[0] - lnb[1] and lnb[1] < p * LN2[0]): p += 1
    lo, hi = 1, 2
    st = gap.denominator
    while not (st * hi + 1)**p < 2**hi: lo, hi = hi, hi * 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if (st * mid + 1)**p < 2**mid: hi = mid
        else: lo = mid
    ops = Counter(e[0] for e in c['events']); F = 18; m = c['roles']; thin = ops['QUERY']; idles = ops['IDLE_ONE']
    basis = V * 8 * (ops['ADD'] + 3 * ops['SWAP']); visible = F * 10**7 + basis + 256 * V * (F + thin + m)
    route_count = 4 * (sum(P.values()) + sum(T.values())) + 8 * V * F + 8 * V * idles; routes = 8 * (10 * A0 * A0 + 10 * A0) * route_count
    need(visible + routes < 10**12, 'ordinary work funded')
    bank = F * 48 + 2 * V * m * len(c['events']) + 16 * V * (F + thin + m); need(bank < 10**7, 'owned bank')
    return dict(owned_bank=bank, ambient=A0, power=v, cutoff=cut, floor=floor, theta=str(theta), log_power=p, grid_index=hi, H=st * hi, norm_upper=float(norm), route_count=route_count, routes=routes, visible=visible, total=routes + visible)


# ------------------------------------------------------------------------------ main
def main():
    OUT = {}; OUT['retained_inputs'] = pins()
    frames = rd('FRAMES.json')['frames']; w = rd('WORD.json.gz'); geo = Geo(frames)
    cw = chainroot.build([1] * 9, [1] * 9); bw = to_binary(cw); rw = reversed_caller(bw)
    ops = Counter(e[0] for e in bw['events'])
    need(dict(ops) == {'ADD': 240, 'SWAP': 393, 'LOCAL': 18, 'IDLE_ONE': 16, 'QUERY': 3}, 'caller census')
    need(set(ops) <= {'ADD', 'SWAP', 'LOCAL', 'IDLE_ONE', 'QUERY'}, 'no address-dependent scalar in the binary caller')
    OUT['caller'] = dict(events=dict(sorted(ops.items())), roles=bw['roles'], stages=bw['stages'],
                         forward_sha256=hashlib.sha256(json.dumps(bw, separators=(',', ':')).encode()).hexdigest(),
                         reversed_sha256=hashlib.sha256(json.dumps(rw, separators=(',', ':')).encode()).hexdigest())
    OUT['coefficients'] = dict(reversed_literal_inverse_F2=f2_forward(rw, -1), reversed_renamed_F2=f2_forward(rw, 1), reversed_transpose_F2=f2_transpose(rw),
                               true_inverse_Z=z_inverse(cw), unreversed_F2=f2_forward(bw, 1), unreversed_transpose_F2=f2_transpose(bw))
    # product of the two callers: forward then literal inverse is the identity with no diagonal
    OUT['coefficients']['forward_then_inverse_identity'] = _compose_identity(bw, rw)
    OUT['main_fixture'] = {str(m): main_fixture(bw, m) for m in (101, 10201)}; OUT['main_fixture_reversed'] = {str(m): main_fixture(rw, m) for m in (101, 10201)}
    # local word
    paid0, local_bits = local_scalar(w, geo)
    need(dict(paid0) == {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}, 'local paid histogram')
    port_lemma(w, geo)
    OUT['local'] = dict(paid=dict(sorted(paid0.items())), majorant_bits=local_bits, physical_columns={str(m): local_physical(w, geo, m) for m in (101, 10201)},
                        adjoint_columns={str(m): local_adjoint(w, geo, m) for m in (101, 10201)}, port_lemma_ports=V)
    # stream, both callers
    s = emit_stream(w, frames, bw); T, P = second_pass(s)
    u = emit_stream(w, frames, rw); Tu, Pu = second_pass(u); need(Tu == T and Pu == P, 'orientation does not change the bill')
    mass = sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items()); need(mass == 753, 'rank surplus')
    need(sum(T.values()) == 9690 and sum(P.values()) == 53337, 'field and job counts'); need(s['majorant_bits'] < 1024 and u['majorant_bits'] < 1024, 'majorant envelope')
    OUT['invoice'] = dict(targets={str(k): v for k, v in sorted(T.items())}, paid={str(k): v for k, v in sorted(P.items())}, rank_surplus=mass, fields=sum(T.values()), jobs=sum(P.values()))
    OUT['stream'] = {k: s[k] for k in ('events', 'stream_sha256', 'descriptor_sha256', 'descriptors', 'majorant_bits', 'episodes')}; OUT['stream']['ops'] = dict(sorted(s['ops'].items()))
    OUT['stream_reversed'] = {k: u[k] for k in ('events', 'stream_sha256', 'majorant_bits')}
    # crossing
    for pw in (pw1, pw2):
        need(margin(T, P, RAW_LO, pw)[0] > 0 and margin(T, P, RAW_HI, pw)[1] < 0, 'crossing bracket')
        need(margin(T, P, TESTED, pw)[0] > 0, 'tested margin')
        a, g, d = tails(T, P, pw)
        need(a[1] < 1 - RESERVE and g[1] < Q(31, 32) and d[1] < Q(19, 20), 'charged tails')
        b, _, _ = tails(T, P, pw, tested=RAW_HI); need(b[1] > 1 - Q(1, 10**9), 'alpha is genuinely close to one')
    OUT['crossing'] = [str(float(RAW_LO)), str(float(RAW_HI))]
    a, g, d = tails(T, P, pw1)
    OUT['tails'] = dict(cutoff=CUT, floor=FLOOR, gamma=float(g[1]), delta=float(d[1]), one_minus_alpha_lower=float(1 - a[1]))
    v = TENSOR; need(1 / (1 + v * RESERVE) + Q(4, 2**(v // 32)) < 1 and Q(31, 32)**128 < Q(1, 16) and Q(19, 20)**128 < Q(1, 16), 'tensor contraction')
    need(CUT**64 < FLOOR**63 and 1 < CUT < FLOOR < max(T) < 256 and AMBIENT < 256, 'separation and ambient')
    need(2 * CUT**(v * 64) <= max(T)**(v * 63), 'shifted exit comparison at the largest target')
    need(all(CUT**k < FLOOR**(k - 1) for k in range(36, 257)) and not CUT**35 < FLOOR**34, 'separation holds from exponent 36')
    # the 17/18 parameters of the predecessor do not apply to this smaller field count
    _, _, d17 = tails(T, P, pw1, cut=17, floor=18); need(d17[0] > 1, 'old floor rejected'); OUT['tails']['delta_at_17_18_lower'] = float(d17[0])
    H0, H1 = cutoffs(TESTED, UNIFORM, v); OUT['compiler'] = dict(H0=H0, H1=H1, v=v, ambient_guard=AMBIENT)
    # fees, with all paid-job dimension work at the conservative ambient
    n, M, own = s['originals'], s['descriptors'], s['owned']; o = s['ops']; mt = rd('MATCHER.json')
    scans = o['ADD'] + o['OWNED_CLEAR'] + o['OWNED_ZERO_HEADER'] + o['WHOLE_ZERO_FRAME'] + 2 * own; park = 4 * (n + own) * M
    routes = o['PAID_PORT_ROUTE'] + 2 * n + 2 * M; matcher = mt['global_occurrences'] * mt['paired_address_coefficient_terms_per_call'] + mt['new_target_coefficient_terms']
    base = scans + park + routes + s['events'] + M * (32 * AMBIENT**2 + 8 * AMBIENT**3) + matcher
    need(base < 2**64 and own == 48, 'finite fee'); OUT['fees'] = dict(scans=scans, parking=park, routes=routes, records=s['events'], matcher_terms=matcher, base=base, owned_per_instance=own, majorant_bits=s['majorant_bits'])
    OUT['cover'] = cover_list(w, geo, bw, frames)
    # levels from the merged completed backend
    b0 = Q(rd('ORDINARY-RESULT.json')['admitted']); need(b0 == Q('.003507719059749'), 'merged backend value')
    C1 = UNIFORM - COVER; need(Q(2**60) * COVER > 256, 'cover gap'); b = b0; levels = []
    for j in range(1, LEVELS + 1):
        x = (1 - RHO) * C1 + RHO * b; y = strict_grid(x, GRID); need(b < y < x < C1 < RHO < 1 - x, 'level gaps'); levels.append(dict(level=j, backend=str(float(b)), admitted=f'{float(y):.15f}', exact=str(y))); b = y
    ADMITTED = b; OUT['levels'] = levels; OUT['admitted'] = str(ADMITTED); OUT['admitted_decimal'] = f'{float(ADMITTED):.15f}'
    # uniform guards and strict-margin monotonicity on the whole approach interval
    for pw in (pw1, pw2):
        lowt = mom(T, 1 - CMAX, pw); cu = pw(CUT, U_TAIL); pp = mom(P, 1 - b0 + U_TAIL, pw)
        need(pp[1] / (cu[0] * lowt[0]) < Q(31, 32), 'uniform gamma'); need(Q(sum(T.values()) * FLOOR) / (pw(CUT, b0)[0] * lowt[0]) < Q(19, 20), 'uniform delta')
    tl = [sum(k * x for k, x in T.items() if k >= a) - sum(k * x for k, x in P.items() if k >= a) for a in range(1, 129)]
    need(min(tl) >= 0 and tl[0] == 753, 'rank-mass tails'); need(margin(T, P, b0, pw1)[0] > 0 and margin(T, P, CMAX, pw1)[1] < 0, 'crossing inside interval')
    # controls on prices
    # the credit for the empty field: without its 111 rank-1 targets the caller does not beat the merged backend
    TE = {k: x for k, x in T.items() if k != 1}; need(T[1] == 111, 'empty-field targets')
    for pw in (pw1, pw2):
        need(margin(TE, P, Q('.0032366'), pw)[0] > 0 and margin(TE, P, Q('.0032367'), pw)[1] < 0 and margin(TE, P, b0, pw)[1] < 0, 'crossing without the empty-field credit')
    OUT['without_empty_field_credit'] = dict(crossing=['.0032366', '.0032367'], rank_surplus=mass - 111, below_merged_backend=True)
    Tt = {int(k): x for k, x in rd('INVOICE.json')['targets'].items()}; Pt = {int(k): x for k, x in rd('INVOICE.json')['paid'].items()}
    need(margin(Tt, Pt, Q('.00350771905979'), pw1)[0] > 0 and margin(Tt, Pt, Q('.00350771905983'), pw1)[1] < 0, 'merged tree invoice control')
    need(margin(Tt, Pt, RAW_LO, pw1)[1] < 0, 'merged tree invoice cannot fund the saving')
    Pn = Counter({1: 1386, 2: 1253, 3: 62, 4: 47, 5: 9, 6: 104, 7: 10}); Tn = Counter({2: 1, 4: 25, 6: 1, 8: 410}); Pc = Counter(P); Tc = Counter(T)
    for r, x in paid0.items(): Pc[r] -= 18 * x
    Tc[8] -= 18 * 413; Tc[4] -= 18 * 2
    for r, x in Pn.items(): Pc[r] += 18 * x
    for r, x in Tn.items(): Tc[r] += 18 * x
    Pc = {k: x for k, x in Pc.items() if x}; Tc = {k: x for k, x in Tc.items() if x}
    need(margin(Tc, Pc, Q('.0038525393934'), pw1)[0] > 0 and margin(Tc, Pc, Q('.0038525393935'), pw1)[1] < 0, 'same caller on the other histogram control')
    need(margin(T, P, Q('.0038006'), pw1)[1] < 0, 'pin above the crossing rejected')
    OUT['ambient_cap_comparison'] = ambient_cap(T, P, bw, Q('.00380058'), 134)
    OUT['ambient_cap_comparison_127'] = ambient_cap(T, P, bw, Q('.00380058'), 127)
    OUT['controls'] = controls(w, frames, geo, bw, cw, T, P)
    OUT['status'] = 'PASS_CHAIN_ROOT_ON_G20_WORD'
    OUT['assumptions'] = ['native_all_columns', 'ROW_spectators', 'owned_erasure', 'mixed_target_compiler', 'ordinary_backend', 'precision_fixed_tape', 'analytic_recovery']
    OUT['scope'] = 'Conditional ordinary BIT component on the merged G20 word; no overall kappa.'
    target = HERE / 'RESULT.json'; text = json.dumps(OUT, indent=1, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        target.write_text(text)
        (HERE / 'GLOBAL.jsonl.gz').write_bytes(gzip.compress(b''.join(s['lines']), mtime=0))
    else:
        need(target.read_text() == text, 'committed result reproduced exactly')
        need(hashlib.sha256(gzip.decompress((HERE / 'GLOBAL.jsonl.gz').read_bytes())).hexdigest() == s['stream_sha256'], 'committed stream')
    print(OUT['status']); print(json.dumps({k: OUT[k] for k in ('admitted_decimal', 'crossing', 'invoice', 'tails', 'fees', 'ambient_cap_comparison')}, default=str))


def _compose_identity(bw, rw):
    """Forward word then the reversed word read as literal inverses must be the identity."""
    n, wd = bw['roles'], bw['stages'] + 1; zero = (0,) * wd
    rows = [[{zero} if i == j else set() for j in range(n)] for i in range(n)]

    def sh(row, ss=(), q=0, sgn=1):
        out = []
        for cell in row:
            cc = set()
            for key in cell:
                k = list(key); k[0] ^= q
                for s in ss: k[s] += sgn
                cc ^= {tuple(k)}
            out.append(cc)
        return out
    for sgn, evs in ((1, bw['events']), (-1, rw['events'])):
        for e in evs:
            op = e[0]
            if op == 'ADD': rows[e[1]] = [x ^ y for x, y in zip(rows[e[1]], rows[e[2]])]
            elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
            elif op == 'QUERY': rows[e[1]] = [x ^ y for x, y in zip(rows[e[1]], sh(rows[e[2]], q=1))]
            elif op == 'LOCAL':
                _, s, a, b = e
                rows[b] = [x ^ y for x, y in zip(rows[b], sh(rows[a], q=1))]; rows[a], rows[b] = sh(rows[a], [s], sgn=sgn), sh(rows[b], [s], sgn=sgn)
            else: rows[e[1]] = sh(rows[e[1]], e[2], sgn=sgn)
    for i in range(n):
        for j in range(n):
            need(rows[i][j] == ({zero} if i == j else set()), ('composition', i, j))
    return n * n


def cover_list(w, geo, rw, frames):
    """Everything a delayed-cover prime must avoid for this caller, before the prime is chosen."""
    used = set(w['start']) | set(w['final'])
    for e in w['records']:
        if e[0] in ('ERASE', 'INIT'): used.add(e[2])
        elif e[0] == 'ADD': used.add(e[3])
        else: used |= {e[2], e[3]}
    used.discard(None); den = set(); dets = set()
    for f in used:
        for row in geo.proj(f):
            for x in row: den.add(x.denominator)
        A = frames[str(f)]['A']; B = frames[str(f)]['B']
        g = [[sum(Q(x) * Q(y) for x, y in zip(r, s)) for s in B] for r in B]
        dets.add(abs(_det(g)) if g else Q(1))
        m = [[Q(x) for x in r] for r in A + B]; need(len(m) == 8, 'frame spans a coordinate space'); dets.add(abs(_det(m)))
    mt = rd('MATCHER.json')
    for key in ('forward', 'inverse', 'new_target_forward', 'new_target_inverse'):
        m = [[Q(x) for x in r] for r in mt[key]]; dets.add(abs(_det(m)))
        for r in m:
            for x in r: den.add(x.denominator)
    need(all(d for d in dets), 'nonzero witnesses')
    primes = set()
    for x in list(den) + [d.numerator for d in dets] + [d.denominator for d in dets]:
        x = int(x); p = 2
        while x > 1 and p * p <= x:
            while x % p == 0: primes.add(p); x //= p
            p += 1
        if x > 1: primes.add(x)
    ops = Counter(e[0] for e in rw['events'])
    jobs = dict(thin_line_jobs=ops['QUERY'] * V, idle_blocks=ops['IDLE_ONE'] * V, main_targets=rw['roles'] * V, native_frames=len(used), distinct_idle_sets=len({tuple(e[2]) for e in rw['events'] if e[0] == 'IDLE_ONE'}))
    return dict(jobs, avoid_primes=sorted(primes), max_prime=max(primes), note='Idle and main-target projectors are the port lines plus disjoint coordinate stage blocks, so they add no denominator beyond these frames. The prime is chosen above 2^60*N^5 only after this finite list and every compiled matcher are fixed.')


def _det(m):
    a = [[Q(x) for x in r] for r in m]; n = len(a); d = Q(1)
    if n != len(a[0]): raise ValueError('square')
    for j in range(n):
        k = next((i for i in range(j, n) if a[i][j]), None)
        if k is None: return Q(0)
        if k != j: a[j], a[k] = a[k], a[j]; d = -d
        d *= a[j][j]; a[j] = [x / a[j][j] for x in a[j]]
        for i in range(j + 1, n):
            if a[i][j]:
                v = a[i][j]; a[i] = [x - v * y for x, y in zip(a[i], a[j])]
    return d


def controls(w, frames, geo, rw, cw, T, P):
    neg = {}

    def reject(label, fn):
        try: fn()
        except (ValueError, KeyError) as e: neg[label] = str(e)[:60]; return
        raise ValueError('control accepted: ' + label)

    def cp(x): return json.loads(json.dumps(x))
    for op in ('LOCAL', 'QUERY', 'IDLE_ONE'):
        bad = cp(rw); del bad['events'][next(i for i, e in enumerate(bad['events']) if e[0] == op)]
        reject('drop_' + op + '_forward', lambda b=bad: f2_forward(b)); reject('drop_' + op + '_transpose', lambda b=bad: f2_transpose(b))
    bad = cp(rw); i = next(i for i, e in enumerate(bad['events']) if e[0] == 'IDLE_ONE'); bad['events'][i][2] = bad['events'][i][2][:-1]
    reject('shrunk_idle', lambda: f2_forward(bad))
    bad2 = cp(rw); bad2['events'].insert(len(bad2['events']) // 2, ['ADD', 3, 5]); reject('stray_xor', lambda: f2_forward(bad2))
    # a stage repeated twice is not an involution in the free ring
    bad3 = cp(rw); j = next(i for i, e in enumerate(bad3['events']) if e[0] == 'IDLE_ONE'); bad3['events'].insert(j, ['IDLE_ONE', bad3['events'][j][1], bad3['events'][j][2]]); reject('no_free_involution', lambda: f2_forward(bad3))
    # word mutations
    for label, mut in (('drop_native_add', lambda r: r.__delitem__(next(i for i, e in enumerate(r) if e[0] == 'ADD'))),
                       ('wrong_query_rank', lambda r: r.__setitem__(next(i for i, e in enumerate(r) if e[0] == 'Q'), (lambda e: [e[0], e[1], e[2], e[3], e[4] % 7 + 1])(next(e for e in r if e[0] == 'Q')))),
                       ('drop_owned_erase', lambda r: r.__delitem__(next(i for i, e in enumerate(r) if e[0] == 'ERASE' and i > 200)))):
        ww = cp(w); mut(ww['records']); reject(label, lambda x=ww: local_scalar(x, geo))
    ww = cp(w); ix = next(i for i, e in enumerate(ww['records']) if e[0] == 'Q'); ww['records'][ix] = ['ZERO_Q'] + ww['records'][ix][1:]; reject('free_move_on_data', lambda: local_scalar(ww, geo))
    # physical: a query dropped from the address replay only
    ww2 = cp(w); ix = len(ww2['records']) // 2
    while ww2['records'][ix][0] != 'Q' or ww2['records'][ix][1] >= 2 * V: ix += 1
    a = ww2['records'][ix]; ww2['records'][ix] = ['Q', a[1], a[2], a[3], a[4]]; gg = Geo(frames); gg.cache[(a[2], a[3], 101)] = tuple(tuple(0 for _ in range(8)) for _ in range(8)); reject('physical_query_omitted', lambda: local_physical(ww2, gg, 101))
    ww3 = cp(w); ww3['final'][0], ww3['final'][1] = ww3['final'][1], ww3['final'][0]; reject('port_lines_exchanged', lambda: local_scalar(ww3, geo))
    ww4 = cp(w); ww4['start'][V], ww4['start'][V + 1] = ww4['start'][V + 1], ww4['start'][V]; reject('port_lemma_wrong_body', lambda: port_lemma(ww4, geo))
    bad4 = cp(rw); i4 = next(i for i, e in enumerate(bad4['events']) if e[0] == 'LOCAL'); e4 = bad4['events'][i4]; bad4['events'][i4] = ['LOCAL', e4[1], e4[3], e4[2]]; reject('local_roles_exchanged', lambda: f2_forward(bad4)); reject('local_roles_exchanged_fixture', lambda: main_fixture(bad4, 101))
    reject('stream_skip_record', lambda: emit_stream(w, frames, rw, corrupt='skip_record'))
    s = emit_stream(w, frames, rw)
    t = dict(s, paid=Counter(s['paid'])); t['paid'][1] -= 1; reject('bill_short_one_job', lambda: second_pass(t))
    t2 = dict(s, lines=[b for b in s['lines'] if json.loads(b)[0] != 'QUERY' or json.loads(b)[1] != 0]); reject('bill_drop_query', lambda: second_pass(t2))
    reject('pin_above_crossing', lambda: need(margin(T, P, Q('.0038006'), pw1)[0] > 0, 'unfunded'))
    return neg


if __name__ == '__main__':
    main()
