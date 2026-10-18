"""Census library: fifth joint read-set exchange on the selected X4 word.

Standard library only. The frame/profile/exactness logic mirrors JointXF's
construction/jx/build_jx.py (research/gauge44-frames-x), which is also imported
by path (sha256-pinned) and used as an oracle on every candidate that its recipe
format can express. Apache-2.0.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from fractions import Fraction as Fr
from itertools import combinations
from pathlib import Path

V = 112
H = 9

PINS = {
    # sha256 of decompressed canonical word content
    'sw4_content': 'd232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59',
    'f741_content': 'e78047028c7dcd25fb1b6216c2b53eda76d2f91292b21d43f5d1903cc13a5c6c',
    'x4_content': '1e1d99ba7aab877d6b573c41f7030ee73de9a52fee51d0a822ddaae71251999f',
}
REL = {
    'sw4_word': 'research/complex-sw4-frame8-validation/platforms/linux/sw4/FULL-WORD.json.gz',
    'f741_word': 'research/complex-sw4-frame8-validation/platforms/linux/frames/FULL-WORD.json.gz',
    'replay_tar': 'research/community-frontier799-audit/integrated799-replay.tar.gz',
    'x4_member': 'native/jx/FULL-WORD.json.gz',
    'build_jx': 'research/gauge44-frames-x/construction/jx/build_jx.py',
    'recipe_x4': 'research/gauge44-frames-x/construction/jx/RECIPE-X4.json',
    'price_profile': 'research/gauge44-frames-x/independent/price_profile.py',
    'plan': 'research/gauge44-frames-x/data/PLAN.json',
    'sw4_recipe': 'research/gauge44-frames-x/construction/sw4/SW4-RECIPE-P6k4.json',
}
X4_PAIRS = {448: 235, 458: 58, 470: 26, 472: 267, 482: 18, 592: 427, 604: 443, 614: 50}
X4_INSTANCES = [(448, 472), (458, 592), (470, 604), (482, 614)]
SW4_H = {461, 581, 591, 603}


def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def csha(w): return sha_bytes(json.dumps(w, sort_keys=True, separators=(',', ':')).encode())


def basis(vs):
    piv = {}
    for a in vs:
        while a:
            b = a.bit_length() - 1
            if b in piv: a ^= piv[b]
            else: piv[b] = a; break
    for k in sorted(piv):
        for j in sorted(piv):
            if j > k and (piv[j] >> k) & 1: piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def contained(a, b): return basis(list(a) + list(b)) == tuple(b)
def registers(e): return e[1:3] if e[0] == 'add' else e[1:2]
def hyper(p): return basis([x for x in range(1, 1 << H) if bin(x & p).count('1') % 2 == 0])
FULL = basis([1 << i for i in range(H)])
def istarget(q): return V <= q < 2 * V


def load_build_jx(root):
    p = Path(root) / REL['build_jx']
    spec = importlib.util.spec_from_file_location('pinned_build_jx', p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- domain
def copy_pairs(w):
    """BRoute's sw4 copy-pair family (construction/sw4/NOTES.md): h an entering helper whose
    first B write is add(h, r, 1, 1) from a non-target r and whose only earlier B gates are
    target pre-reads add(t, h, c). Movable reads: target reads add(t, h|r, c) strictly after
    the copy gate and before the next write of h or r."""
    B = w['B']; ent = {int(q) for q in w['start_extra']}
    touch = defaultdict(list)
    for i, e in enumerate(B):
        for q in registers(e): touch[q].append(i)
    out = []
    for h in sorted(q for q in touch if q >= 2 * V):
        idx = touch[h]
        k = next((i for i in idx if B[i][1] == h), None)
        if k is None: continue
        e = B[k]
        if not (e[0] == 'add' and e[3] == 1 and e[4] == 1) or istarget(e[2]): continue
        r = e[2]; pre = [i for i in idx if i < k]
        if not all(B[i][0] == 'add' and B[i][2] == h and istarget(B[i][1]) for i in pre): continue
        if h not in ent: continue
        mv = []
        for i in range(k + 1, len(B)):
            g = B[i]
            if g[1] in (h, r): break
            if g[0] == 'add' and g[2] in (h, r) and istarget(g[1]): mv.append(i)
        out.append(dict(h=h, r=r, copy=k, pre=pre, movable=mv))
    return out


def pair_edits(w, p, subset):
    """sw4-rule edits (build_jx recipe format) for one copy pair over a subset of its movable reads.
    Returns (edits, problem) where problem is None or a reason the rule cannot be written."""
    B = w['B']; h, r = p['h'], p['r']
    rep, dele, ins = [], [], []
    before = (max(p['pre']) + 1) if p['pre'] else p['copy']
    for i in subset:
        e = B[i]; t, s, a, b = e[1], e[2], e[3], e[4]
        if s == h:
            pi = [j for j in p['pre'] if B[j][:5] == ['add', t, h, -a, b]]
            if len(pi) != 1: return None, ('h2r_without_unique_preread', i)
            rep.append(dict(h=h, i=i, old=e[:5], new=['add', t, r, a, b], why='h2r'))
            dele.append(dict(h=h, i=pi[0], old=B[pi[0]][:5], why='h2r delete pre-read'))
        else:
            rep.append(dict(h=h, i=i, old=e[:5], new=['add', t, h, a, b], why='r2h'))
            ins.append(dict(h=h, before=before, gate=['add', t, h, -a, b], why='r2h insert pre-read'))
    return dict(replace=rep, delete=dele, insert=ins), None


def domain(w_sw4):
    """Complete candidate domain after X4: unordered pairs {p1, p2} of sw4 copy pairs with movable
    reads, neither in X4's eight, whose movable-read target sets intersect; every (S1, S2) with S1,
    S2 nonempty subsets of the respective movable reads."""
    P = [p for p in copy_pairs(w_sw4) if p['movable']]
    B = w_sw4['B']
    T = {p['h']: frozenset(B[i][1] for i in p['movable']) for p in P}
    free = [p for p in P if p['h'] not in X4_PAIRS]
    pp = [(a, b) for i, a in enumerate(free) for b in free[i + 1:] if T[a['h']] & T[b['h']]]
    allpp = [(a['h'], b['h']) for i, a in enumerate(P) for b in P[i + 1:] if T[a['h']] & T[b['h']]]
    return P, T, pp, allpp


def subsets(xs):
    for k in range(1, len(xs) + 1):
        for c in combinations(xs, k): yield list(c)


# ---------------------------------------------------------------- builder
class Reject(Exception): pass


def symstate(gs):
    rows = {}
    for e in gs:
        for q in registers(e): rows.setdefault(q, {q: Fr(1)})
        if e[0] == 'add':
            t, s = e[1], e[2]; c = Fr(e[3], e[4]); d = rows[t]
            for k, x in list(rows[s].items()):
                a = d.get(k, 0) + c * x
                if a: d[k] = a
                else: d.pop(k, None)
        else:
            t = e[1]; c = Fr(e[2], e[3]); rows[t] = {k: c * x for k, x in rows[t].items()}
    return rows


class Builder:
    """build_jx.build semantics, plus one extra frame option for moved reads:
    keep[i] = True gives the replaced gate at original index i base = its stored frame
    (monotone repair, span(stored + operand frames)) instead of the plain join. Explicit frames
    (PR741's eight and X4's sixteen raises) keep build_jx's equality requirement."""

    def __init__(self, w):
        self.w = w; R = w['report']['R']; self.n = 2 * V + R
        END = [FULL] * V + [hyper(p) for p in w['ports']] + [FULL] * R
        for q, U in w['helper_final'].items(): END[int(q)] = basis(U)
        self.END = END
        cur = [(p,) for p in w['ports']] + [()] * (V + R)
        for q, U in w['start_extra'].items(): cur[int(q)] = basis(U)
        paid = Counter()
        for e in w['A']:
            for q in registers(e):
                U = basis(e[-1]); d = len(U) - len(cur[q])
                if d: paid[d] += 1
                cur[q] = U
        lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
        for q, U in zip(w['centers'], w['center_frames']):
            U = basis(U); served = {lev.get(e[1] - V, ()) for e in w['cut'] if e[2] == q}
            for T in sorted(served, key=lambda x: -len(x)):
                if T != U: paid[len(U) - len(T)] += 1
                U = T
        self.cur0, self.paid0 = cur, paid
        self.stored = [tuple(e[-1]) if e[-1] is not None else None for e in w['B']]
        self.S0 = symstate([e[:-1] for e in w['B']])

    def splice(self, edits):
        B = [list(e) for e in self.w['B']]; tag = set(); dele = set(); ins = {}
        for x in edits['replace']:
            i = x['i']
            if B[i][:-1] != x['old']: raise Reject(('replace old mismatch', i))
            if i in tag: raise Reject(('replace twice', i))
            B[i] = list(x['new']) + [B[i][-1]]; tag.add(i)
        for x in edits['delete']:
            i = x['i']
            if B[i][:-1] != x['old']: raise Reject(('delete old mismatch', i))
            if i in dele: raise Reject(('delete twice', i))
            dele.add(i)
        for x in edits['insert']: ins.setdefault(x['before'], []).append(list(x['gate']) + [None])
        NB = []
        for i, e in enumerate(B):
            for g in ins.get(i, []): NB.append(g)
            if i in dele: continue
            NB.append(e)
        return NB

    def exact(self, edits):
        """Fraction replay of the whole B segment against the input (frame-independent)."""
        b = symstate([e[:-1] for e in self.splice(edits)]); a = self.S0
        return sorted(q for q in set(a) | set(b) if a.get(q, {q: Fr(1)}) != b.get(q, {q: Fr(1)}))

    def build(self, edits, explicit, keep=frozenset(), want_word=False, check_exact=True, soft=None):
        soft = soft or {}
        w = self.w; B0 = w['B']
        B = [list(e) for e in B0]; tag = set(); dele = set(); ins = {}
        for x in edits['replace']:
            i = x['i']
            if B[i][:-1] != x['old']: raise Reject(('replace old mismatch', i))
            if i in tag: raise Reject(('replace twice', i))
            B[i] = list(x['new']) + [B[i][-1]]; tag.add(i)
        for x in edits['delete']:
            i = x['i']
            if B[i][:-1] != x['old']: raise Reject(('delete old mismatch', i))
            if i in dele: raise Reject(('delete twice', i))
            dele.add(i)
        for x in edits['insert']: ins.setdefault(x['before'], []).append(list(x['gate']) + [None])
        NB, nt, key = [], set(), []
        for i, e in enumerate(B):
            for g in ins.get(i, []): nt.add(len(NB)); NB.append(g); key.append(None)
            if i in dele: continue
            if i in tag: nt.add(len(NB))
            NB.append(e); key.append(i)
        END = self.END; cur = list(self.cur0); paid = Counter(self.paid0); used = set()
        for j, e in enumerate(NB):
            rs = registers(e); k = key[j]
            if k is not None and k in explicit: base = list(explicit[k]); used.add(k)
            elif k is not None and k in soft: base = list(soft[k])
            elif k is not None and k in keep and k in tag: base = list(self.stored[k])
            elif j in nt or e[-1] is None: base = []
            else: base = list(e[-1])
            F = basis(base + [x for q in rs for x in cur[q]])
            if k is not None and k in explicit and F != basis(explicit[k]): raise Reject(('explicit frame below join', k))
            for q in rs:
                if V <= q < 2 * V and not contained(F, END[q]): raise Reject(('cap', j, q))
                d = len(F) - len(cur[q])
                if d: paid[d] += 1
                cur[q] = F
            NB[j] = list(e[:-1]) + [list(F)]
        if used != set(explicit): raise Reject(('unused explicit frame', sorted(set(explicit) - used)))
        newearly = []
        for i, U in w['early_cleanup']:
            rs = registers(w['cleanup'][i]); F = basis(list(U) + [x for q in rs for x in cur[q]])
            for q in rs:
                if w['helper_final'].get(str(q)) is not None and not contained(F, END[q]): raise Reject(('tailend', i, q))
                d = len(F) - len(cur[q])
                if d: paid[d] += 1
                cur[q] = F
            newearly.append([i, list(F)])
        for q in range(self.n):
            if not contained(cur[q], END[q]): raise Reject(('end', q))
            d = len(END[q]) - len(cur[q])
            if d: paid[d] += 1
        if check_exact:
            b = symstate([e[:-1] for e in NB]); a = self.S0
            bad = sorted(q for q in set(a) | set(b) if a.get(q, {q: Fr(1)}) != b.get(q, {q: Fr(1)}))
            if bad: raise Reject(('exactness rows', bad))
        prof = {str(k): v for k, v in sorted(paid.items())}
        if not want_word: return prof, None
        o = copy.deepcopy(w); o['B'] = NB; o['early_cleanup'] = newearly
        o['report'] = dict(o['report']); o['report']['local_profile'] = prof
        return prof, o


def merge(*eds):
    return {k: [x for e in eds for x in e[k]] for k in ('replace', 'delete', 'insert')}


def explicit_of(rc):
    ex = {int(i): f for i, f in rc['frames_741']}
    for i, f in rc['raises']: ex[int(i)] = f
    return ex


# ---------------------------------------------------------------- pricing
EXTRA = {1: 1, 3: 1, 44: 1, 48: 2396}   # non-local part of the frozen X4 PLAN profile
CALLS = 72


def global_profile(local):
    g = Counter({int(k): CALLS * v for k, v in local.items()})
    for k, v in EXTRA.items(): g[k] += v
    return {str(k): v for k, v in sorted(g.items())}


def price(root, local, workdir, tag):
    """Exact price of a local profile with the pinned independent price_profile.py (two exact moment
    engines + the 47 strict outer constraints), run as `python -I -B` from the repository root."""
    import subprocess, sys, os
    root = Path(root).resolve(); workdir = Path(workdir)
    inp = workdir / ('profile-%s.json' % tag); out = workdir / ('price-%s.json' % tag)
    inp.write_text(json.dumps(dict(profile=global_profile(local)), sort_keys=True) + '\n')
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONOPTIMIZE', 'PYTHONPATH')}
    r = subprocess.run([sys.executable, '-I', '-B', str(root / REL['price_profile']), '--main', str(root),
                        '--profile', str(inp), '--output', str(out)], cwd=str(root), env=env,
                       capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError('price_profile failed: ' + r.stderr[-800:])
    d = json.loads(out.read_text())
    assert d['status'] == 'PASS_FROZEN_PROFILE_TWO_EXACT_ENGINE_AND_OUTER47_CROSSCHECK', d['status']
    nat = d['prices']['native']
    return dict(kappa=nat['outer_with_bit']['kappa'], kappa_decimal=nat['outer_with_bit']['kappa_decimal'],
                complex_b=nat['outer_with_bit']['complex_b'], binding=nat['outer_with_bit']['binding'],
                strict_outer=nat['outer_with_bit']['strict_constraints_passed'],
                conservative_kappa=d['prices']['conservative']['outer_with_bit']['kappa'])
