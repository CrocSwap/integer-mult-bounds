#!/usr/bin/env python3
"""Exact grid of the complete selected #5413 caller: body ceil(9 lambda/2)+6, controller level exactly 73 bits.

Standard library only; about three minutes.  Inputs pinned by SHA256 in SOURCES.json, all on main: the #5413 capsule
(NEUTRAL-BACKWARD-v16c body, NEUTRAL-CALLER-v16c controller), the #5402 PROVIDER.json and provider WORD.json.gz, the
coded-native-caller NORMALIZERS.json port wrappers, the eight-relation WORD.json.gz (canonical frames and the native
warp table) and the repository Clifford compiler clifford_exact.py.  Successor of research/selected-word-exact-grid.

Model (PR2772 / PR2813 / selected-word-exact-grid): public inputs are arbitrary arrays on 2^-f Z[i]; a value is
sum_s c_s U_s V_s(0) with exact rational c_s and dyadic Gaussian Clifford U_s; a Clifford of Fourier rank r has
reduced denominator exactly 2^ceil(r/2).

Part A, body.  The only runtime local direction is backward (18 calls). Execute the body with PROVIDER_5402 expanded
by its schedule; monomials, Gaussians and warps stay symbols (adjacent inverse warps cancel; each y-field monomial of
the 240-map block is followed by its exact inverse with only ADDs in between, so the pair is the identity and is
omitted). Checks: no odd denominator, 17 owned fields zero at exit, maximum v2 = 6 attained by a single-occurrence
rank-9 helper term (body guard ceil(9 lambda/2)+6), main-data terms v2 <= 4, helper terms local rank <= 9.

Part B, controller.  Per port p let A_x = (backward_input_X wrapper, then Delta_{I_x}^-1), A_y likewise, and
Q_p = A_y then A_x^-1.  Q_p has Fourier rank 1 and Q_p^2 rank 0, and the body's final X row is x_p - y_p on all
112 ports, so the body computes X = Phi (x - Q_p y): Q_p is the controller's Q.  The controller is replayed in the
exact Laurent ring of check_wholecaller_v1 (32 banks, integer coefficients). Global data live on 145 axes: central
axis 0 plus eight private axes per LOCAL stage; a component Q^q prod_{t in T} D_t has 8|T| private Fourier rank.
  * calls before the last: |T| <= 16, so every term needs <= 4 + ceil((128+9)/2) = 73 (main) or <= 11 (helper);
  * last call (stage 32, pair 15): original bank 31 enters x as Q^2 D_T and y as Q D_T with |T| = 17. Its x- and
    y-paths merge (Phi_y = Phi_x Q_p) on Phi_x Q^2 with coefficient c_x + c_y; every in-word cut is evaluated with
    exact nine-plane ranks (warps via the native table), plus the t-field cut after the paid C8 job and the cache cuts;
  * after the last call the controller only applies integer ADD/SCALE/SWAP and monomials; 224 targets have rank 145.
Result: the maximum over every cut is 73, attained by the rank-145 targets: one controller level needs exactly 73
extra fractional bits.
Usage: python3 -I -B verify.py [--write]
"""
import argparse, collections, gzip, hashlib, importlib.util, json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CAP = ROOT / 'research' / 'coupled-helper-neutral-completion' / 'capsule' / 'workspace'
BODY = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'caller' / 'NEUTRAL-BACKWARD-v16c.json'
CALLER = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'caller' / 'NEUTRAL-CALLER-v16c.json'
PROV = CAP / 'swarm-provider-audit-sol-high-20261024' / 'repository' / 'research' / 'native-rank8-helper-provider'
NORM = CAP / 'swarm-provider-audit-sol-high-20261024' / 'agents' / 'budget' / 'inputs' / 'NORMALIZERS.json'
EIGHT = ROOT / 'research' / 'eight-owned-relations' / 'WORD.json.gz'
CLIFFORD = ROOT / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
N9 = 9


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


def v2(n):
    n = abs(n)
    return (n & -n).bit_length() - 1


def ceil2(r):
    return (r + 1) // 2


class Ops:
    """Nine-axis Clifford helpers: charts, monomial words, native warps, port maps A and Q."""

    def __init__(self, ce, canonical, normalizers):
        self.ce, self.c = ce, canonical
        self.charts, self.kc = {}, {}
        self.warp = {w['op']: w['G_columns'] for w in canonical['warps']}
        self.A = {}
        for p in range(112):
            wr = normalizers['ports'][p]['compiled_wrappers']
            self.A[p] = self.mono(wr['backward_input_X']['word']).then(self.chart(canonical['start'][p]).adjoint())
            self.A[p + 112] = self.mono(wr['backward_input_Y']['word']).then(self.chart(canonical['start'][p + 112]).adjoint())
        self.Q = {p: self.A[p + 112].then(self.A[p].adjoint()) for p in range(112)}

    def rank(self, op):
        return self.ce.rank([x for x, z, p in op.tab[N9:]])

    def chart(self, f):
        if f not in self.charts:
            self.charts[f] = self.ce.canonical_frame(N9, self.c['frames'][f])
        return self.charts[f]

    def mono(self, word):
        ce = self.ce; op = ce.ident(N9)
        for e in word:
            if e[0] == 'D':
                op = op.then(ce.diag(N9, e[1], e[2]))
            elif e[0] == 'P':
                op = op.then(ce.perm(N9, e[1]))
            elif e[0] == 'X':
                op = op.then(ce.xgate(N9, e[1]))
            elif e[0] == 'phase':
                op = op.then(ce.Op(N9, ce.identity(N9), [('phase', e[1])]))
            else:
                require(False, 'unknown monomial primitive')
        return op

    def K(self, sym):
        """Logical native warp operator (as in kappa-round3-warp's frame-bound warp admission)."""
        if sym not in self.kc:
            ce = self.ce
            G = ce.transpose(tuple(self.warp[abs(sym)]), N9); gi = ce.inv(G, N9); tr = ce.transpose(gi, N9)
            quad = tuple((1 << i) ^ sum(ce.parity(a & b) << j for j, b in enumerate(tr)) for i, a in enumerate(tr))
            k = ce.perm(N9, G).then(ce.diag(N9, quad))
            self.kc[sym] = k if sym > 0 else k.adjoint()
        return self.kc[sym]

    def qpow(self, p, q):
        op = self.ce.ident(N9)
        for _ in range(q % 4):
            op = op.then(self.Q[p])
        return op


class Body:
    def __init__(self, body, prov, word, canonical):
        drop = {i for i, o in enumerate(body['operations']) if o['op'] == 'MONOMIAL' and 'purpose' not in o
                and 'whole_job_boundary' not in o and o['field'][0] == 'y'}
        self.ops = [o for i, o in enumerate(body['operations']) if i not in drop]
        self.dropped = len(drop)
        self.body, self.prov, self.word, self.c = body, prov, word, canonical
        self.bind = body['physical_field_bindings']
        self.rows = {i: {(i, ()): F(1)} for i in range(body['physical_field_count'])}
        self.sym = 0; self.S = 0; self.odd = 0; self.cls = {}; self.frames = {}; self.inword = False
        self.groups = []      # in-word: (frame, port, warp word, c_x, c_y)
        self.helper_witness = None; self.cache = {}

    def newsym(self, tag):
        self.sym += 1
        return (tag, self.sym)

    def apply(self, f, s):
        out = {}
        for (inp, wd), q in self.rows[f].items():
            nw = wd[:-1] if s[0] == 'W' and wd and wd[-1] == ('W', -s[1]) else wd + (s,)
            v = out.get((inp, nw), 0) + q
            if v:
                out[(inp, nw)] = v
            else:
                out.pop((inp, nw), None)
        self.rows[f] = out

    def stat(self, where, f):
        r = self.rows[f]
        if not r:
            return
        occ = collections.Counter(inp for inp, wd in r)
        by = collections.defaultdict(lambda: [F(0), F(0)])
        for (inp, wd), q in r.items():
            e = v2(q.denominator)
            if q.denominator >> e != 1:
                self.odd += 1
            self.S = max(self.S, e)
            cl = 'main' if inp < 224 else 'helper' if inp < 632 else 'owned'
            self.cls[cl] = max(self.cls.get(cl, 0), e)
            if self.inword and self.frames.get(f) is not None:
                if inp < 224:
                    by[(inp % 112, tuple(s for s in wd if s[0] == 'W'), tuple(s for s in wd if s[0] not in ('W', 'Nin')))][inp >= 112] += q
                elif inp < 632 and e == 6 and occ[inp] == 1 and self.helper_witness is None:
                    rank = Body.ops_ref.rank(Body.ops_ref.chart(self.c['start'][inp]).adjoint().then(Body.ops_ref.chart(self.frames[f])))
                    if rank == 9:
                        self.helper_witness = [str(where), f, inp, str(q)]
        for (p, ww, other), (cx, cy) in by.items():
            self.groups.append((self.frames[f], p, ww, cx, cy))

    def add(self, dst, src, q, where):
        d = self.rows[dst]
        for k, v in self.rows[src].items():
            nv = d.get(k, 0) + q * v
            if nv:
                d[k] = nv
            else:
                d.pop(k, None)
        self.stat(where, dst)

    def scale(self, f, q, where):
        if where == 'cache_scalar':
            m = next(m for m in self.prov['mode_boundaries'] if m['cache_slot'] == f)
            self.cache[f] = (m['frame'], dict(self.rows[f]), q)
        self.rows[f] = {k: q * v for k, v in self.rows[f].items()}
        self.stat(where, f)

    @staticmethod
    def role(r):
        if isinstance(r, int):
            return r
        return r[1] if r[0] == 'L' else 632 + r[1]

    def provider(self):
        p = self.prov
        for f in range(224):
            self.apply(f, self.newsym('Nin'))
        for m in p['mode_boundaries']:
            self.apply(m['owner'], self.newsym('K')); self.scale(m['owner'], F(2), 'mode_scalar')
        for ins in p['input_basis_program']:
            if ins[0] == 'add':
                self.add(ins[1], ins[2], F(ins[3]), 'input_basis')
            else:
                self.scale(ins[1], F(ins[2]), 'input_basis')
        self.inword = True
        self.frames = {i: self.c['start'][i] for i in range(632)}
        for t, e in enumerate(self.word['word']):
            k = e[0]
            if k == 'warp':
                self.apply(self.role(e[1]), ('W', e[2]))
                if e[1][0] == 'L':
                    self.frames[e[1][1]] = e[4]
            elif k == 'climb':
                self.frames[e[2]] = e[4]
            elif k == 'scalar':
                g = e[1]; d_ = self.role(g[1])
                if g[1][0] == 'L' and e[2] is not None:
                    self.frames[g[1][1]] = e[2]
                if g[0] == 'clear':
                    self.rows[d_] = {}
                elif g[0] == 'copy':
                    self.rows[d_] = dict(self.rows[self.role(g[2])]); self.stat(('word', t), d_)
                elif g[0] == 'add':
                    self.add(d_, self.role(g[2]), F(g[3], g[4]), ('word', t))
                elif g[0] == 'scale':
                    self.scale(d_, F(g[2], g[3]), ('word', t))
                else:
                    require(False, 'unknown provider scalar')
            elif k == 'zero_retag':
                require(not self.rows[self.role(e[1])], 'provider zero retag on a zero row')
            else:
                require(k in ('center', 'adapter', 'phase'), 'unknown provider event')
        self.inword = False
        for ins in p['output_basis_program']:
            if ins[0] == 'add':
                self.add(ins[1], ins[2], F(ins[3]), 'output_basis')
            else:
                self.scale(ins[1], F(ins[2]), 'output_basis')
        for m in p['mode_boundaries']:
            cs, o = m['cache_slot'], m['owner']
            self.scale(cs, F(m['cache_scalar']), 'cache_scalar'); self.apply(cs, self.newsym('N'))
            require(not self.rows[o], 'mode owner zero before the cache SWAP')
            self.rows[cs], self.rows[o] = self.rows[o], {}
        for f in range(224):
            self.apply(f, self.newsym('Nout'))

    def run(self):
        b = self.bind
        for n, o in enumerate(self.ops):
            k = o['op']
            if k == 'MONOMIAL':
                self.apply(b[o['field']], self.newsym('M'))
            elif k == 'GAUSSIAN':
                self.apply(b[o['field']], self.newsym('G'))
            elif k == 'ADD':
                self.add(b[o['dst']], b[o['src']], F(o['coefficient']), ('body', n))
            elif k == 'CLEAR':
                self.rows[b[o['field']]] = {}
            elif k == 'ZERO_RETAG':
                require(not self.rows[b[o['field']]], 'body zero retag on a zero row')
            elif k == 'SWAP':
                x, y = (b[f] for f in o['fields']); self.rows[x], self.rows[y] = self.rows[y], self.rows[x]
            elif k == 'PROVIDER_5402':
                self.provider()
            else:
                require(False, 'unknown body operation ' + k)
        owned = [b[f] for f in b if f[0] in 'ct']
        require(len(owned) == 17 and all(not self.rows[f] for f in owned), 'all 17 owned fields zero at exit')


def monomial_block_is_identity(body, ops):
    idx = [i for i, o in enumerate(body['operations']) if o['op'] == 'MONOMIAL' and 'purpose' not in o and 'whole_job_boundary' not in o]
    require(len(idx) == 240, '240-map monomial block')
    first = {body['operations'][i]['field']: body['operations'][i] for i in idx[:120]}
    second = {body['operations'][i]['field']: body['operations'][i] for i in idx[120:]}
    between = {body['operations'][i]['op'] for i in range(idx[119] + 1, idx[120])}
    require(set(first) == set(second) and between == {'ADD'}, 'block structure: maps, ADDs, maps')
    ident = ops.ce.ident(N9)
    for f in first:
        m = ops.mono(first[f]['word']).then(ops.mono(second[f]['word']))
        require(m.tab == ident.tab and m.zero_state() == ident.zero_state(), 'second map inverts the first: ' + f)
    return {f: (ops.mono(first[f]['word']), ops.mono(second[f]['word'])) for f in first}


def laurent(controller):
    """check_wholecaller_v1 semantics; returns the x/y components before every LOCAL and the endpoint check."""
    def add(a, b, c=1):
        out = dict(a)
        for k, v in b.items():
            out[k] = out.get(k, F(0)) + c * v
            if not out[k]:
                del out[k]
        return out

    def mul(a, q=0, stages=()):
        out = {}
        for (j, e), c in a.items():
            z = list(e); z[0] += q
            for s in stages:
                z[s + 1] += 1
            out[j, tuple(z)] = c
        return out

    def scalar(rows, prog):
        r = [dict(x) for x in rows]
        for op in prog:
            if op[0] == 'ADD':
                r[op[1]] = add(r[op[1]], r[op[2]], F(op[3]))
            elif op[0] == 'SCALE':
                r[op[1]] = {k: F(op[2]) * v for k, v in r[op[1]].items()}
            elif op[0] == 'SWAP':
                r[op[1]], r[op[2]] = r[op[2]], r[op[1]]
            else:
                require(False, 'boundary program primitive')
        return r
    w = controller
    zero = (0,) * 34
    r = scalar([{(j, zero): F(1)} for j in range(32)], w['boundaries']['right_program'])
    calls = []
    for e in w['physical_events']:
        kind = e[0]
        if kind in ('LOCAL', 'QUERY_SHEAR'):
            _, s, p, back = e; x, y = 2 * p, 2 * p + 1
            if kind == 'LOCAL':
                calls.append((s, p, dict(r[x]), dict(r[y])))
            if back:
                r[x] = add(r[x], mul(r[y], q=1), -1)
            else:
                r[y] = add(r[y], mul(r[x], q=-1))
            if kind == 'LOCAL':
                r[x] = mul(r[x], stages=[s]); r[y] = mul(r[y], stages=[s])
        elif kind == 'IDLE':
            for j in (2 * e[1], 2 * e[1] + 1):
                r[j] = mul(r[j], stages=e[2])
        elif kind == 'ADD':
            r[e[1]] = add(r[e[1]], r[e[2]], F(e[3]))
        elif kind == 'Q_POWER':
            r[e[1]] = mul(r[e[1]], q=e[2])
        elif kind == 'SIGNED_SWAP':
            a, b = e[1:]; r[a] = add(r[a], r[b]); r[b] = add(r[b], r[a], -1); r[a] = add(r[a], r[b])
        elif kind == 'SWAP':
            a, b = e[1:]; r[a], r[b] = r[b], r[a]
        else:
            require(False, 'unknown controller event')
    r = scalar(r, w['boundaries']['left_program'])
    require(r == [{(j, tuple(d)): F(1)} for j, d in enumerate(w['diagonal'])], 'Laurent endpoint is the diagonal')
    return calls


def build():
    pinned_inputs()
    spec = importlib.util.spec_from_file_location('selected_caller_clifford_exact', CLIFFORD)
    ce = importlib.util.module_from_spec(spec); spec.loader.exec_module(ce)
    body = json.loads(BODY.read_text(encoding='utf-8'))
    caller = json.loads(CALLER.read_text(encoding='utf-8'))
    require(caller['local_backward_sha256'] == hashlib.sha256(BODY.read_bytes()).hexdigest(), 'controller binds this body')
    require(caller['runtime_local_directions'] == {'backward': 18, 'forward_macro_calls': 0}, 'only backward bodies run')
    prov = json.loads((PROV / 'PROVIDER.json').read_text(encoding='utf-8'))
    word = json.loads(gzip.decompress((PROV / 'WORD.json.gz').read_bytes()))
    require(word['direction'] == 'backward', 'backward provider word')
    canonical = json.loads(gzip.decompress(EIGHT.read_bytes()))['canonical']
    ops = Ops(ce, canonical, json.loads(NORM.read_text(encoding='utf-8')))
    require(all(ops.rank(ops.Q[p]) == 1 and ops.rank(ops.qpow(p, 2)) == 0 for p in range(112)), 'Q_p: rank 1, Q_p^2 rank 0')
    blocks = monomial_block_is_identity(body, ops)

    # Part A
    Body.ops_ref = ops
    B = Body(body, prov, word, canonical)
    B.run()
    require(B.dropped == 224, 'the 224 y-field block maps are identity pairs')
    require(B.odd == 0, 'every coefficient of the complete body is dyadic')
    require(B.S == 6 and B.helper_witness is not None, 'body maximum v2 = 6 with a single-occurrence rank-9 helper term')
    require(B.cls['main'] == 4 and B.cls['helper'] == 6, 'class maxima: main 4, helper 6')
    for p in range(112):
        cx = [q for (inp, wd), q in B.rows[p].items() if inp == p]
        cy = [q for (inp, wd), q in B.rows[p].items() if inp == p + 112]
        require(cx == [F(1)] and cy == [F(-1)], 'final X row is x_p - y_p')

    # Part B
    calls = laurent(caller['controller'])
    require(len(calls) == 18, 'eighteen LOCAL calls')
    early = 0
    for s, p, rx, ry in calls[:-1]:
        for (j, ez), c in list(rx.items()) + list(ry.items()):
            require(c.denominator == 1, 'integer controller coefficients')
            t = sum(ez[1:])
            early = max(early, 4 + ceil2(8 * t + 9))
    require(early == 73, 'calls before the last need at most 73')
    s, p, rx, ry = calls[-1]
    require((s, p) == (32, 15), 'last call is stage 32, pair 15')
    comp_x = {j: (ez[0], sum(ez[1:]), c) for (j, ez), c in rx.items()}
    comp_y = {j: (ez[0], sum(ez[1:]), c) for (j, ez), c in ry.items()}
    require(len(comp_x) == len(rx) and len(comp_y) == len(ry), 'one monomial per original bank')
    require(comp_x[31][:2] == (2, 17) and comp_y[31][:2] == (1, 17), 'bank 31 enters x as Q^2 and y as Q, 17 stages')
    best = (-1,)

    def rank9(q, inp, ww, fr):
        op = ops.qpow(inp % 112, q).then(ops.A[inp])
        for sym in ww:
            op = op.then(ops.K(sym[1]))
        return ops.rank(op.then(ops.chart(fr)))
    cache9 = {}
    for fr, port, ww, cx, cy in B.groups:
        for j in set(comp_x) | set(comp_y):
            terms = []
            if j in comp_x and j in comp_y and comp_x[j][0] == comp_y[j][0] + 1 and comp_x[j][1] == comp_y[j][1]:
                terms.append((comp_x[j][0], comp_x[j][1], comp_x[j][2] * cx + comp_y[j][2] * cy, port))
            else:
                if j in comp_x:
                    terms.append((comp_x[j][0], comp_x[j][1], comp_x[j][2] * cx, port))
                if j in comp_y:
                    terms.append((comp_y[j][0], comp_y[j][1], comp_y[j][2] * cy, port + 112))
            for q, t, c, inp in terms:
                if not c:
                    continue
                key = (q % 4, inp, ww, fr)
                if key not in cache9:
                    cache9[key] = rank9(q, inp, ww, fr)
                g = v2(c.denominator) + ceil2(8 * t + cache9[key])
                if g > best[0]:
                    best = (g, str(c), 8 * t + cache9[key], j, inp, fr, [list(x) for x in ww])
    # t-field cut after the paid C8 job (y data enter t through the block maps)
    C8 = ce.ident(N9)
    for i in range(8):
        C8 = C8.then(ce.cgate(N9, 1 << i))
    route = {(o['field'], o['purpose']): ops.mono(o['word']) for o in body['operations'] if o['op'] == 'MONOMIAL' and o.get('purpose', '').startswith('D8paidjob')}
    tbest = 0
    for o in body['operations']:
        if o['op'] == 'ADD' and o['dst'].startswith('t'):
            yfield = o['src']; jport = int(yfield[1:]); tf = o['dst']
            op = ops.qpow(jport, comp_y[31][0]).then(blocks[yfield][0]).then(blocks[tf][1])
            op = op.then(route[(tf, 'D8paidjobinputaxisroute')]).then(C8).then(route[(tf, 'D8paidjoboutputaxisroute')])
            tbest = max(tbest, v2(F(o['coefficient']).denominator) + ceil2(8 * 17 + ops.rank(op)))
    # cache cuts
    cbest = 0
    for slot, (fr, row, sc) in B.cache.items():
        by = collections.defaultdict(lambda: [F(0), F(0)])
        for (inp, wd), q in row.items():
            if inp < 224:
                by[(inp % 112, tuple(s for s in wd if s[0] == 'W'))][inp >= 112] += q * F(sc)
        for (port, ww), (cx, cy) in by.items():
            c = comp_x[31][2] * cx + comp_y[31][2] * cy
            if c:
                cbest = max(cbest, v2(c.denominator) + ceil2(8 * 17 + rank9(2, port, ww, fr)))
    final_rank = max((1 if d[0] else 0) + 8 * sum(d[1:]) for d in caller['controller']['diagonal'])
    targets = ceil2(final_rank)
    require(caller['productive_profile']['145'] == 224 and final_rank == 145 and targets == 73, '224 rank-145 targets need 73')
    require(best[0] == 73 and tbest <= 73 and cbest <= 73, 'last call: every cut needs at most 73')
    guard = max(early, best[0], tbest, cbest, targets, 6 + ceil2(9))
    require(guard == 73, 'controller-level guard is exactly 73')
    return dict(body=dict(max_v2=B.S, helper_witness=B.helper_witness, class_max_v2=B.cls, odd_denominators=0,
                          identity_monomial_pairs=B.dropped, final_X_rows='x_p - y_p on all 112 ports',
                          guard='ceil(9 lambda/2) + 6 (attained)'),
                controller=dict(early_calls_bound=early, last_call=dict(stage=32, pair=15, in_word_max=best[0],
                                in_word_witness=best[1:], t_cut_max=tbest, cache_cut_max=cbest,
                                bank31=dict(x=[comp_x[31][0], comp_x[31][1]], y=[comp_y[31][0], comp_y[31][1]])),
                                rank145_targets=224, target_requirement=targets, guard=guard))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT.json equals the rebuild')
    print('PASS_SELECTED_CALLER_BODY_6_CONTROLLER_EXACTLY_73')


if __name__ == '__main__':
    main()
