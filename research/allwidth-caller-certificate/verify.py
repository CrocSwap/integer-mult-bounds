"""All-width certificate for the complete selected #5413 caller, in the group algebra of its native operators.

Lifting lemma (PROOF.md).  Let G be a finite group of exact matrices (here: the dyadic Clifford group on nine or
145 binary axes, absolute phase included) and let a = sum_g c_g g be an element of C[G] with fixed coefficients.
Then  sum_g c_g g^{(x) f} = 0  for every positive column multiplicity f  <=>  a = 0 in C[G].
The map g -> g^{(x) f} is a group homomorphism, so any identity between products of group elements, and any
identity of C[G], transfers to every width.  Conversely an element that is not zero in C[G] fails at some width
(Burnside).  A certificate is therefore a census of exact group elements: canonical tableau plus the action on the
basis state |0>, which fixes the absolute phase.  Scalar coefficients stay outside the tensor power; the central
scalars i^k I are group elements, not coefficients.

What this file certifies for the selected caller (PR #5413, selected at the pinned base):
  A. Port binding (896 group identities, both orientations, exact phase).  For every port p the physical paths of
     the body are x->X = D, y->Y = D, y->X = D C_0 and the query operator Q_p = A_y A_x^-1 = C_0, where D is the
     positive rank-eight Gaussian on axes 1..8 and C_0 the positive central Gaussian on axis 0.  The backward
     orientation uses the entrywise-conjugate frame semantics; without the conjugation the element is -conj(C_0).
  B. Body endpoint (free-word replay of NEUTRAL-BACKWARD-v16c with the #5402 provider expanded): every surviving
     term of the main endpoint carries only the port wrappers; every warp cancelled; the 400 autonomous helper
     rows are wrapper pairs; owned fields zero.  Free-word identities are identities of C[G] for every assignment.
  C. Controller: the exact Laurent replay of check_wholecaller_v1 in free commuting variables Q, D_s; the plan's
     18 stage planes are pairwise disjoint and disjoint from the central axis, so the realization Q = C_0,
     D_s = fourier(stage axes) is abelian; C_0^2 = X_0 and C_0^-1 X_0 = C_0 exactly, so the 16 negative diagonal
     exponents are corrected by the central translation inside the group.
  D. Controls of the lemma on small matrices: the Reynolds-type trap C_0 = (1+i)/2 I + (1-i)/2 X_0 and the scalar
     trap i*I = (iI) hold at width 1 and fail at width 2 while the census rejects them; exponent two and reversed
     factors behave as the census predicts.
No new kappa.  The physical half of native_all_columns (tape realization of g^{(x) f} with spectators and adapters
at the retained tariff) is not addressed here.
"""
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CAP = ROOT / 'research' / 'coupled-helper-neutral-completion' / 'capsule' / 'workspace'
BODY = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'caller' / 'NEUTRAL-BACKWARD-v16c.json'
CALLER = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'caller' / 'NEUTRAL-CALLER-v16c.json'
PLAN = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'challenge' / 'WHOLECALLER-PLAN-v1.json'
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


def load_clifford():
    spec = importlib.util.spec_from_file_location('allwidth_clifford_exact', CLIFFORD)
    ce = importlib.util.module_from_spec(spec); spec.loader.exec_module(ce)
    return ce


def elem(op):
    """Exact group element: Pauli tableau (Clifford up to phase) and the image of |0> (fixes the phase)."""
    vec, den = op.zero_state()
    return op.tab, tuple(vec), den


class Ops:
    """Nine-axis Clifford helpers: charts (plain or entrywise conjugate), monomial words, native warps."""

    def __init__(self, ce, canonical, normalizers):
        self.ce, self.c, self.nz = ce, canonical, normalizers
        self.charts, self.kc = {}, {}
        self.warp = {w['op']: w['G_columns'] for w in canonical['warps']}
        self.I = ce.ident(N9)
        self.C0 = ce.cgate(N9, 1, 1)
        self.C0inv = ce.cgate(N9, 1, -1)
        self.X0 = ce.xgate(N9, 1)
        self.D = ce.fourier(N9, range(1, 9))

    def phase(self, k):
        return self.ce.Op(N9, self.ce.identity(N9), [('phase', k % 4)])

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
                op = op.then(self.phase(e[1]))
            else:
                require(False, 'unknown monomial primitive')
        return op

    def conj(self, op):
        """Entrywise complex conjugate of an exact circuit (the backward native semantics)."""
        ce = self.ce; r = ce.ident(N9)
        for g in op.circuit:
            if g[0] == 'P':
                part = ce.perm(N9, g[1])
            elif g[0] == 'X':
                part = ce.xgate(N9, g[1])
            elif g[0] == 'C':
                part = ce.cgate(N9, g[1], -g[2])
            elif g[0] == 'D':
                part = ce.diag(N9, g[1], tuple(-x % 4 for x in g[2]))
            else:
                part = self.phase(-g[1])
            r = r.then(part)
        return r

    def chart(self, f, cj=False):
        if (f, cj) not in self.charts:
            op = self.ce.canonical_frame(N9, self.c['frames'][f])
            self.charts[(f, cj)] = self.conj(op) if cj else op
        return self.charts[(f, cj)]

    def K(self, sym):
        if sym not in self.kc:
            ce = self.ce
            G = ce.transpose(tuple(self.warp[abs(sym)]), N9); gi = ce.inv(G, N9); tr = ce.transpose(gi, N9)
            quad = tuple((1 << i) ^ sum(ce.parity(a & b) << j for j, b in enumerate(tr)) for i, a in enumerate(tr))
            k = ce.perm(N9, G).then(ce.diag(N9, quad))
            self.kc[sym] = k if sym > 0 else k.adjoint()
        return self.kc[sym]

    def paths(self, p, backward):
        """Physical path operators of port p through the body, with the port wrappers of NORMALIZERS.json.

        A_role = input wrapper, then inverse canonical chart of the role's entrance frame;
        O_role = canonical chart of the role's exit frame, then output wrapper.  The body's logical endpoint is
        X = x - y, Y = y, so x->X = A_x O_x, y->Y = A_y O_y, y->X = A_y O_x and the query operator is Q = A_y A_x^-1.
        """
        wr = self.nz['ports'][p]['compiled_wrappers']; pre = 'backward_' if backward else ''; cj = backward
        Ax = self.mono(wr[pre + 'input_X']['word']).then(self.chart(self.c['start'][p], cj).adjoint())
        Ay = self.mono(wr[pre + 'input_Y']['word']).then(self.chart(self.c['start'][p + 112], cj).adjoint())
        Ox = self.chart(self.c['final'][p], cj).then(self.mono(wr[pre + 'output_X']['word']))
        Oy = self.chart(self.c['final'][p + 112], cj).then(self.mono(wr[pre + 'output_Y']['word']))
        return {'Q': Ay.then(Ax.adjoint()), 'x->X': Ax.then(Ox), 'y->Y': Ay.then(Oy), 'y->X': Ay.then(Ox)}


def port_bindings(ops):
    """A: 112 ports x 2 orientations x 4 paths are the controller's abelian symbols, with exact absolute phase."""
    want = {'Q': elem(ops.C0), 'x->X': elem(ops.D), 'y->Y': elem(ops.D), 'y->X': elem(ops.D.then(ops.C0))}
    count = 0
    for backward in (False, True):
        for p in range(112):
            got = ops.paths(p, backward)
            for name, op in got.items():
                require(elem(op) == want[name], 'port %d %s path %s is not the controller symbol' % (p, 'backward' if backward else 'forward', name))
                count += 1
    # The orientation convention matters: reading the backward wrappers against plain (unconjugated) charts gives a
    # different group element on every port (on port 0: -C_0^-1 times Z_1 Z_2, phase -1), so a census that mixed the
    # two conventions would wrongly reject the binding.  Only the conjugate reading is the backward semantics.
    mixed = 0
    for p in range(112):
        wr = ops.nz['ports'][p]['compiled_wrappers']
        Ax = ops.mono(wr['backward_input_X']['word']).then(ops.chart(ops.c['start'][p]).adjoint())
        Ay = ops.mono(wr['backward_input_Y']['word']).then(ops.chart(ops.c['start'][p + 112]).adjoint())
        mixed += elem(Ay.then(Ax.adjoint())) != want['Q']
    require(mixed == 112, 'the mixed-convention reading is a different element on every port')
    return dict(group_identities=count, symbols=dict(Q='C_0 (positive central Gaussian, axis 0)',
                D='fourier on axes 1..8 (positive rank-eight Gaussian)'),
                backward_semantics='entrywise conjugate charts and operators (PR5376 PROVIDER.md); the mixed reading differs from C_0 on all 112 ports')


class Body:
    """Free-word replay of the runtime body (NEUTRAL-BACKWARD-v16c with PROVIDER_5402 expanded by its schedule).

    Rows are keyed by (input field, word of symbols).  Native warps are the symbols ('W', op) with adjacent
    inverse cancellation; wrappers, monomials and Gaussians are fresh symbols, so no term through a different
    operator path ever merges.  A free-word endpoint is an identity of C[G] under every assignment of group
    elements to symbols, hence an identity at every column width.
    """

    def __init__(self, body, prov, word, canonical):
        self.ops_list = body['operations']
        self.body, self.prov, self.word, self.c = body, prov, word, canonical
        self.bind = body['physical_field_bindings']
        self.rows = {i: {(i, ()): F(1)} for i in range(body['physical_field_count'])}
        self.sym = 0; self.meaning = {}

    def newsym(self, tag, meaning=None):
        self.sym += 1
        self.meaning[(tag, self.sym)] = meaning
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

    def add(self, dst, src, q):
        d = self.rows[dst]
        for k, v in self.rows[src].items():
            nv = d.get(k, 0) + q * v
            if nv:
                d[k] = nv
            else:
                d.pop(k, None)

    def scale(self, f, q):
        self.rows[f] = {k: q * v for k, v in self.rows[f].items()}

    @staticmethod
    def role(r):
        if isinstance(r, int):
            return r
        return r[1] if r[0] == 'L' else 632 + r[1]

    def provider(self):
        p = self.prov
        for f in range(224):
            self.apply(f, self.newsym('Nin', f))
        for m in p['mode_boundaries']:
            self.apply(m['owner'], self.newsym('K', m['owner'])); self.scale(m['owner'], F(2))
        for ins in p['input_basis_program']:
            if ins[0] == 'add':
                self.add(ins[1], ins[2], F(ins[3]))
            else:
                self.scale(ins[1], F(ins[2]))
        self.frames = {i: self.c['start'][i] for i in range(632)}
        for e in self.word['word']:
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
                    self.rows[d_] = dict(self.rows[self.role(g[2])])
                elif g[0] == 'add':
                    self.add(d_, self.role(g[2]), F(g[3], g[4]))
                elif g[0] == 'scale':
                    self.scale(d_, F(g[2], g[3]))
                else:
                    require(False, 'unknown provider scalar')
            elif k == 'zero_retag':
                require(not self.rows[self.role(e[1])], 'provider zero retag on a zero row')
            else:
                require(k in ('climb', 'center', 'adapter', 'phase'), 'unknown provider event')
        for ins in p['output_basis_program']:
            if ins[0] == 'add':
                self.add(ins[1], ins[2], F(ins[3]))
            else:
                self.scale(ins[1], F(ins[2]))
        for m in p['mode_boundaries']:
            cs, o = m['cache_slot'], m['owner']
            self.scale(cs, F(m['cache_scalar'])); self.apply(cs, self.newsym('N', o))
            require(not self.rows[o], 'mode owner zero before the cache SWAP')
            self.rows[cs], self.rows[o] = self.rows[o], {}
        for f in range(224):
            self.apply(f, self.newsym('Nout', f))

    def run(self):
        b = self.bind
        for o in self.ops_list:
            k = o['op']
            if k == 'MONOMIAL':
                self.apply(b[o['field']], self.newsym('M', o['word']))
            elif k == 'GAUSSIAN':
                self.apply(b[o['field']], self.newsym('G', o['operator']))
            elif k == 'ADD':
                self.add(b[o['dst']], b[o['src']], F(o['coefficient']))
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


def body_endpoint(B, ops):
    """B: the main endpoint carries only the port wrappers, every warp cancelled; helpers are autonomous."""
    warps_left = sum(1 for f in range(649) for (inp, wd) in B.rows[f] for s in wd if s[0] == 'W')
    require(warps_left == 0, 'every native warp cancels in the free group at the endpoint')
    block_maps = 0

    def strip_block(wd):
        """The body's y-field block is a monomial, ADDs, and the exact inverse monomial: an identity element."""
        nonlocal block_maps
        ms = [s for s in wd if s[0] == 'M']
        if ms:
            m = ops.I
            for s in ms:
                m = m.then(ops.mono(B.meaning[s]))
            require(elem(m) == elem(ops.I), 'block monomials on a main row compose to the identity element')
            block_maps += len(ms)
        return tuple(s for s in wd if s[0] != 'M')
    for p in range(112):
        X = B.rows[p]; Y = B.rows[p + 112]
        require(len(X) == 2 and len(Y) == 1, 'main rows X: two terms, Y: one term')
        for (inp, wd), q in X.items():
            wd = strip_block(wd); tags = tuple(s[0] for s in wd)
            require(tags == ('Nin', 'Nout') and B.meaning[wd[1]] == p, 'X term is wrapped by the port wrappers only')
            if inp == p:
                require(q == 1 and B.meaning[wd[0]] == p, 'x_p term: coefficient 1, x input wrapper')
            else:
                require(inp == p + 112 and q == -1 and B.meaning[wd[0]] == p + 112, 'y_p term: coefficient -1, y input wrapper')
        (inp, wd), q = next(iter(Y.items())); wd = strip_block(wd)
        require(inp == p + 112 and q == 1 and tuple(s[0] for s in wd) == ('Nin', 'Nout')
                and B.meaning[wd[0]] == p + 112 and B.meaning[wd[1]] == p + 112, 'Y row is the wrapped y_p')
    # the 400 autonomous helpers return as their own input under an alias pair of monomials (an exact group
    # element pair, inverse to each other); the 8 mode owners return the paid rank-8 Gaussian of h_mode - Z y with
    # fixed +-1/2 entries over 56 y inputs (the restored coupled outputs, counted as paid+productive by #5413).
    autonomous = 0; alias_pairs_identity = 0; modes = 0; mode_terms = 0
    mode_owners = set(B.prov['mode_owners'])
    for h in range(224, 632):
        r = B.rows[h]
        if h in mode_owners:
            modes += 1; mode_terms += len(r)
            # H = D (h - Z y): own input with coefficient 1 and 56 y inputs with +-1/2 (Z = diag M^T diag / 2), one C8.
            require(len(r) == 57 and sum(1 for (inp, wd) in r if inp == h) == 1, 'mode output: own input plus 56 y inputs')
            for (inp, wd), q in r.items():
                require((q == 1 if inp == h else 112 <= inp < 224 and abs(q) == F(1, 2)) and [s[0] for s in wd].count('G') == 1,
                        'mode output: one paid Gaussian of h_mode - Z y with +-1/2 entries')
            continue
        require(len(r) == 1, 'autonomous helper returns one term')
        (inp, wd), q = next(iter(r.items()))
        require(inp == h and q == 1 and tuple(s[0] for s in wd) == ('M', 'M'), 'helper returns itself under two monomials')
        m = ops.mono(B.meaning[wd[0]]).then(ops.mono(B.meaning[wd[1]]))
        require(ops.ce.rank([x for x, z, ph in m.tab[N9:]]) == 0, 'helper alias pair is a monomial (rank 0) element')
        require(elem(m) != elem(ops.I), 'helper alias pairs are nontrivial (signed) monomials')
        if m.tab == ops.I.tab:
            alias_pairs_identity += 1          # identity tableau: a pure central phase i^k
        autonomous += 1
    require(autonomous == 400 and modes == 8, '400 autonomous helpers, 8 modes')
    # the paid climbs of every persistent role telescope to the recorded exit frame (frame changes are inert in rows)
    require(all(B.frames[i] == B.c['final'][i] for i in range(632)), 'every persistent role ends in its recorded exit frame')
    return dict(warps_cancelled=True, main_rows='X_p = Nout_x(Nin_x x_p - Nin_y y_p), Y_p = Nout_y Nin_y y_p on all 112 ports',
                block_monomials_identity=block_maps, exit_frames_recorded=632,
                autonomous_helpers=400, helper_alias_pairs_pure_phase=alias_pairs_identity,
                helper_alias_pairs_with_address_action=400 - alias_pairs_identity, mode_outputs=8, mode_terms=mode_terms,
                distinct_warp_symbols=len({abs(e[2]) for e in B.word['word'] if e[0] == 'warp'}), owned_zero=17)


def laurent(controller):
    """check_wholecaller_v1 semantics: 32 banks, free commuting Laurent variables Q and D_1..D_33."""
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
    stages = set(); qpow = []
    for e in w['physical_events']:
        kind = e[0]
        if kind in ('LOCAL', 'QUERY_SHEAR'):
            _, s, p, back = e; x, y = 2 * p, 2 * p + 1
            if back:
                r[x] = add(r[x], mul(r[y], q=1), -1)
            else:
                r[y] = add(r[y], mul(r[x], q=-1))
            if kind == 'LOCAL':
                stages.add(s); r[x] = mul(r[x], stages=[s]); r[y] = mul(r[y], stages=[s])
        elif kind == 'IDLE':
            for j in (2 * e[1], 2 * e[1] + 1):
                r[j] = mul(r[j], stages=e[2])
        elif kind == 'ADD':
            r[e[1]] = add(r[e[1]], r[e[2]], F(e[3]))
        elif kind == 'Q_POWER':
            qpow.append(e[2]); r[e[1]] = mul(r[e[1]], q=e[2])
        elif kind == 'SIGNED_SWAP':
            a, b = e[1:]; r[a] = add(r[a], r[b]); r[b] = add(r[b], r[a], -1); r[a] = add(r[a], r[b])
        elif kind == 'SWAP':
            a, b = e[1:]; r[a], r[b] = r[b], r[a]
        else:
            require(False, 'unknown controller event')
    r = scalar(r, w['boundaries']['left_program'])
    require(r == [{(j, tuple(d)): F(1)} for j, d in enumerate(w['diagonal'])], 'Laurent endpoint is the diagonal')
    return stages, qpow


def controller_realization(ops, caller, plan):
    """C: the Laurent identity holds in free commuting variables; its realization on the plan's axes is abelian."""
    w = caller['controller']
    stages, qpow = laurent(w)
    require(len(stages) == 18, 'eighteen LOCAL stages')
    planes = {s['stage']: s['local_axes'] for s in plan['stage_embeddings']}
    require(set(planes) == stages and plan['ambient_axes'] == 145, 'plan embeds exactly the eighteen stages on 145 axes')
    private = []
    for s, axes in planes.items():
        require(axes[0] == 0 and len(axes) == 9 and all(1 <= a <= 144 for a in axes[1:]), 'stage plane: central axis 0 plus eight private axes')
        private.extend(axes[1:])
    require(len(private) == 144 and len(set(private)) == 144, 'the 18 private planes are pairwise disjoint')
    # exact group identities used by the plan's phase proof (nine-axis model; they are statements about C_0 and X_0 alone)
    require(elem(ops.C0.then(ops.C0)) == elem(ops.X0), 'C_0^2 = X_0 with absolute coefficient +1')
    require(elem(ops.C0inv.then(ops.X0)) == elem(ops.C0), 'C_0^-1 X_0 = C_0 exactly')
    require(elem(ops.C0.then(ops.D)) == elem(ops.D.then(ops.C0)), 'C_0 and D commute as exact elements (disjoint axes)')
    require(all(q in (-2, 2) for q in qpow), 'Q_POWER events are even central translations X_0^{+-1}')
    neg = sum(1 for d in w['diagonal'] if d[0] == -1)
    require(neg == 16 and all(d[0] in (-1, 1) and all(x in (0, 1) for x in d[1:]) for d in w['diagonal']), 'diagonal: Q^{+-1} times distinct D factors; 16 negative exponents')
    require(all(m['central_X_after_LEFT'] == (m['q_exponent'] == -1) for m in plan['main_targets']), 'negative Q corrected by the central X in the plan')
    return dict(laurent_endpoint='diagonal, exterior coefficient +1, no finite-order quotient', stages=18,
                private_axes_disjoint=True, central_axis=0, q_power_exponents=sorted(set(qpow)),
                negative_q_banks=neg, group_identities=['C_0^2 = X_0', 'C_0^-1 X_0 = C_0', '[C_0, D] = 0'])


# --- D: controls of the lifting lemma on dense matrices over Q(i), width 1 and 2 ---------------------------------
class Qi:
    """Gaussian rationals a + b i with exact Fractions."""
    __slots__ = ('a', 'b')

    def __init__(self, a, b=0):
        self.a, self.b = F(a), F(b)

    def __add__(self, o):
        return Qi(self.a + o.a, self.b + o.b)

    def __mul__(self, o):
        return Qi(self.a * o.a - self.b * o.b, self.a * o.b + self.b * o.a)

    def __eq__(self, o):
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __repr__(self):
        return '%s%+si' % (self.a, self.b)


def mat(rows):
    return [[x if isinstance(x, Qi) else Qi(x) for x in r] for r in rows]


def mmul(A, B):
    n = len(A)
    return [[sum((A[i][k] * B[k][j] for k in range(n)), Qi(0)) for j in range(n)] for i in range(n)]


def kron(A, B):
    return [[A[i // len(B)][j // len(B)] * B[i % len(B)][j % len(B)] for j in range(len(A) * len(B))] for i in range(len(A) * len(B))]


def tpow(A, f):
    out = A
    for _ in range(f - 1):
        out = kron(out, A)
    return out


def msum(terms, f):
    """sum_g c_g g^{(x) f} for terms (c, g) with scalar c in Q(i); the scalar stays outside the tensor power."""
    n = len(terms[0][1]) ** f
    out = [[Qi(0)] * n for _ in range(n)]
    for c, g in terms:
        G = tpow(g, f)
        out = [[out[i][j] + c * G[i][j] for j in range(n)] for i in range(n)]
    return out


def zero(M):
    return all(x == Qi(0) for r in M for x in r)


def lemma_controls():
    half = F(1, 2)
    I = mat([[1, 0], [0, 1]]); X = mat([[0, 1], [1, 0]]); iI = mat([[Qi(0, 1), 0], [0, Qi(0, 1)]])
    C = mat([[Qi(half, half), Qi(half, -half)], [Qi(half, -half), Qi(half, half)]])       # (1+i)/2 I + (1-i)/2 X
    out = {}
    # (1) Reynolds-type trap: a linear relation between three distinct group elements.  Width 1: zero; width 2: not.
    rey = [(Qi(1), C), (Qi(-half, -half), I), (Qi(-half, half), X)]
    out['reynolds_trap'] = dict(distinct_elements=3, width1_zero=zero(msum(rey, 1)), width2_zero=zero(msum(rey, 2)))
    require(out['reynolds_trap']['width1_zero'] and not out['reynolds_trap']['width2_zero'], 'Reynolds trap: width 1 passes, width 2 fails')
    # (2) scalar trap: the scalar i times I against the group element iI.  Width 1: equal; width 2: (iI)^(x)2 = -I.
    sc = [(Qi(0, 1), I), (Qi(-1), iI)]
    out['scalar_phase_trap'] = dict(distinct_elements=2, width1_zero=zero(msum(sc, 1)), width2_zero=zero(msum(sc, 2)))
    require(out['scalar_phase_trap']['width1_zero'] and not out['scalar_phase_trap']['width2_zero'], 'scalar phase trap: width 1 passes, width 2 fails')
    # (3) exponent two: C^2 = X is one group element written two ways; it holds at every width (checked 1..3).
    e2 = [(Qi(1), mmul(C, C)), (Qi(-1), X)]
    out['exponent_two'] = dict(same_element=mmul(C, C) == X, widths_zero=[zero(msum(e2, f)) for f in (1, 2, 3)])
    require(out['exponent_two']['same_element'] and all(out['exponent_two']['widths_zero']), 'exponent two is a group identity')
    # (4) reversed noncommuting factors: S X against X S differ as elements and already at width 1.
    S = mat([[1, 0], [0, Qi(0, 1)]])
    rv = [(Qi(1), mmul(S, X)), (Qi(-1), mmul(X, S))]
    out['reversed_factors'] = dict(same_element=mmul(S, X) == mmul(X, S), width1_zero=zero(msum(rv, 1)))
    require(not out['reversed_factors']['same_element'] and not out['reversed_factors']['width1_zero'], 'reversed factors differ')
    return out


def build():
    pinned_inputs()
    ce = load_clifford()
    body = json.loads(BODY.read_text(encoding='utf-8'))
    caller = json.loads(CALLER.read_text(encoding='utf-8'))
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    require(caller['local_backward_sha256'] == hashlib.sha256(BODY.read_bytes()).hexdigest(), 'controller binds this body')
    require(caller['runtime_local_directions'] == {'backward': 18, 'forward_macro_calls': 0}, 'only backward bodies run')
    require(plan['bindings']['B_sha256'] == caller['local_backward_sha256'], 'plan binds the same body')
    prov = json.loads((PROV / 'PROVIDER.json').read_text(encoding='utf-8'))
    word = json.loads(gzip.decompress((PROV / 'WORD.json.gz').read_bytes()))
    require(word['direction'] == 'backward', 'backward provider word')
    canonical = json.loads(gzip.decompress(EIGHT.read_bytes()))['canonical']
    normalizers = json.loads(NORM.read_text(encoding='utf-8'))
    require(normalizers['source_payload_sha256'] == prov['source_payload_sha256'], 'normalizers and provider share the source payload')
    ops = Ops(ce, canonical, normalizers)
    A = port_bindings(ops)
    B = Body(body, prov, word, canonical); B.run()
    Bres = body_endpoint(B, ops)
    C = controller_realization(ops, caller, plan)
    D = lemma_controls()
    return dict(lemma='sum_g c_g g^{(x)f} = 0 for all f >= 1  <=>  sum_g c_g g = 0 in C[G]; group identities lift by g -> g^{(x)f}',
                port_bindings=A, body_endpoint=Bres, controller=C, lemma_controls=D,
                conclusion='The complete #5413 caller identity is a composition of (i) a free-word identity of the body, (ii) 896 exact group identities binding the ports to C_0 and D, (iii) a free commutative Laurent identity realized by commuting exact elements on disjoint axes. Each lifts to every positive column multiplicity; the algebraic half of native_all_columns holds for this caller. The physical half is not addressed.')


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
    print('PASS_ALLWIDTH_CALLER_CERTIFICATE_896_PORT_IDENTITIES_FREE_BODY_ABELIAN_CONTROLLER')


if __name__ == '__main__':
    main()
