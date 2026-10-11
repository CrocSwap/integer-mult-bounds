# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
"""Exact physical simulation of an emitted local program on C^(2^9) registers (Gaussian-dyadic, int64 with overflow guard).

Transitions are executed with the SERIALIZED child recipes (CLIFFORD-RECIPES.json, decoded here), data adapters with the serialized
endpoint monomials, entering-helper wrappers with the serialized RESIDUAL-ADAPTERS monomials.  Expected values are computed from
DEFINITIONS only (canonical frames, the port gate C_q, the Fourier gate), never from recipes.
"""
import sys
import numpy as np
from gd import GD, circ_of, monomial_circ, recipe_circ, fourier_circ, basis_batch, N
from pathlib import Path
VENDOR = str(Path(__file__).resolve().parents[3] / 'split-centres-global/vendor')   # the vendored clifford_exact of PR #433/#442 (definitions of T_F and C_q only)
sys.path.insert(0, VENDOR)
import clifford_exact as ce        # used ONLY for the definitions canonical_frame / cgate (label family and port gate)

n9 = 9


class Model:
    def __init__(self, d):
        self.c = c = d['c']; self.v = c['v']; self.R = c['R']; self.n = 2 * c['v'] + c['R']
        self.frames = [tuple(f) for f in c['frames']]
        self.children = {(r['old'], r['new']): recipe_circ(r) for r in d['rec']['children']}
        self.src_ad = {}; self.tgt_ad = {}
        for a in d['rec']['endpoint_adapters']:
            (self.src_ad if a['role'] == 'source' else self.tgt_ad)[a['port']] = (a['frame'], monomial_circ(a['left']) if a['rank'] == 0 else None)
        self.wraps = {int(f): (monomial_circ(w['right']), monomial_circ(w['left']), w['rank']) for f, w in d['wraps'].items()}
        self._T = {}
    # ---- definitions ---------------------------------------------------------------------------------------------
    def T(self, f):
        if f not in self._T: self._T[f] = circ_of(ce.canonical_frame(n9, self.frames[f]))
        return self._T[f]
    def def_transition(self, g, a, b):          # T_b T_a^-1
        return g.apply_circ(self.T(a), inverse=True).apply_circ(self.T(b))
    def Cq(self, i): return circ_of(ce.cgate(n9, self.c['ports'][i]))
    # ---- serialized operators ------------------------------------------------------------------------------------
    def rec_transition(self, g, a, b):
        return g.apply_circ(self.children[(a, b)])


def run(model, events, init, mode='recipe', regs=None, stop=None):
    """apply `events` physically to state `init` (dict reg -> GD, missing = 0).  regs: optional set of registers to simulate
    (events touching other registers are an error unless their operands are all zero).  Returns the state."""
    st = {x: y.copy() for x, y in init.items()}; k = next(iter(st.values())).k()
    if mode == 'recipe': trans = model.rec_transition
    elif mode == 'def': trans = model.def_transition
    else:                                   # mutants only: a transition without a serialized recipe is executed as T_b T_a^-1
        trans = lambda g, a, b: model.rec_transition(g, a, b) if (a, b) in model.children else model.def_transition(g, a, b)
    def get(x): return st.get(x)
    for idx, e in enumerate(events):
        if stop is not None and idx >= stop: break
        tag = e[0]
        if tag == 'phase': continue
        if tag == 'scalar':
            op = e[1]; t = tuple(op[1]); kind = op[0]
            if kind == 'clear': st.pop(t, None)
            elif kind == 'copy':
                s = get(tuple(op[2])); st.pop(t, None)
                if s is not None: st[t] = s.copy()
            elif kind == 'scale':
                if t in st: st[t].scale(op[2], op[3]) if op[3] > 0 else st[t].scale(-op[2], -op[3])
            else:
                s = get(tuple(op[2]))
                if s is None: continue
                num, den = op[3], op[4]
                if den < 0: num, den = -num, -den
                if t not in st: st[t] = GD.zeros(k)
                st[t].add_scaled(s, num, den)
        elif tag == 'climb':
            _, part, r, a, b, rk = e
            if ('L', r) in st: trans(st[('L', r)], a, b)
        elif tag == 'center':
            _, kk, a, b, rk = e
            if ('C', kk) in st: trans(st[('C', kk)], a, b)
        elif tag == 'adapter':
            _, way, r, f = e; x = st.get(('L', r))
            if way == 'old_to_new':
                if r < model.v:
                    fr, circ = model.src_ad[r]; assert fr == f
                    if x is not None: x.apply_circ(circ)
                else: assert f == 0, ('unexpected non-identity entry adapter', r, f)
            else:
                if model.v <= r < 2 * model.v:
                    fr, circ = model.tgt_ad[r - model.v]; assert fr == f
                    if x is not None: x.apply_circ(circ, inverse=True)
                else: assert f == 1, ('unexpected non-identity exit adapter', r, f)
        elif tag == 'residual_adapter':
            _, side, r, f = e; x = st.get(('L', r))
            Rc, Lc, w = model.wraps[f]
            if x is not None: x.apply_circ(Rc if side == 'pre' else Lc, inverse=True)
        else: raise ValueError(e)
    return st


def expected(model, init, back):
    """intended transform from DEFINITIONS: data shear in the old representation, helpers C_[w] (x) I"""
    v, n, c = model.v, model.n, model.c
    F = fourier_circ(range(9)); k = next(iter(init.values())).k()
    out = {}
    def g(r): return init.get(('L', r))
    def add(r, x):
        if x is None: return
        if r in out: out[r].add_scaled(x, 1, 1)
        else: out[r] = x
    for i in range(v):
        Cq = model.Cq(i); hs, ht = g(i), g(v + i)
        xs = hs.copy().apply_circ(Cq, inverse=True) if hs is not None else None          # logical source C_q^-1 h_s
        if not back:
            add(i, xs.copy().apply_circ(F) if xs is not None else None)
            yt = ht.copy() if ht is not None else None
            if xs is not None:
                yt = yt if yt is not None else GD.zeros(k); yt.add_scaled(xs, 1, 1)
            if yt is not None: add(v + i, yt.apply_circ(Cq, inverse=True).apply_circ(F))
        else:
            z = xs.copy() if xs is not None else None
            if ht is not None:
                z = z if z is not None else GD.zeros(k); z.add_scaled(ht, -1, 1)
            if z is not None: add(i, z.apply_circ(F))
            if ht is not None: add(v + i, ht.copy().apply_circ(Cq, inverse=True).apply_circ(F))
    for r in range(2 * v, n):
        h = g(r)
        if h is None: continue
        w = 9 - len(model.frames[c['start'][r]])
        add(r, h.copy().apply_circ(fourier_circ(range(w))))
    return out


def compare(model, got, exp):
    bad = []
    for r in range(model.n):
        a = got.get(('L', r)); b = exp.get(r)
        if a is None and b is None: continue
        if a is None: a = GD.zeros(b.k())
        if b is None: b = GD.zeros(a.k())
        if not a.equals(b): bad.append(r)
    leftovers = [x for x, y in got.items() if x[0] == 'C' and not y.is_zero()]
    return bad, leftovers
