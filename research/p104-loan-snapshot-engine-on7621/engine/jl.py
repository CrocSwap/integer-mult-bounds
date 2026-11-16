# JOINTEDIT library: tag-sequence model of a word (non-MOVE events in order, each with a chart tag).
# A public register's path = clean([initial] + tags of its ops in order + [final]); MOVEs are regenerated from it.
# Joint edit = slide ops inside exact commutation windows + retag, so the main skips a stop; partners pay hop changes.
import sys, gzip, json, math, bisect, os
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
from collections import defaultdict
import pricekit as pk  # vendored in this directory
KAPPA = 0.0036576
def f(r): return r ** (1 - KAPPA) if r > 0 else 0.0
def spanmask(b):
    S = {0}
    for v in b: S |= {x ^ v for x in S}
    m = 0
    for x in S: m |= 1 << x
    return m
C_PATH = os.path.join(HERE, 'data', '7113_CALLER.json')  # Rohan Arun's signed #7113 caller, vendored as data
_CI = None
def kappa(W):
    global _CI
    if _CI is None: _CI = pk.caller_invoice(pk.load(C_PATH))
    pr = pk.price(pk.invoice(_CI, pk.native_from_word(W)), 30)
    return pr
class Word:
    def __init__(s, W):
        s.W = W; n = W['public']; s.n = n
        s.sp = [spanmask(b) for b in W['frames']]; s.dim = [len(b) for b in W['frames']]
        live = set(W['live']); H = W['hosted']
        s.mains = live | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
        s.ev = [e for e in W['program'] if e[0] != 'MOVE']          # E-order
        s.key = [float(i) for i in range(len(s.ev))]
        s.tag = [None] * len(s.ev)
        s.ops = defaultdict(list)      # public reg -> E idx (ADD/COPY/SCALE)
        s.touch = defaultdict(list)    # any reg -> E idx incl INIT/CLEAR
        for i, e in enumerate(s.ev):
            op = e[0]
            if op in ('ADD', 'COPY'):
                s.tag[i] = e[4]; regs = (e[1], e[2])
            elif op == 'SCALE':
                s.tag[i] = e[3]; regs = (e[1],)
            else:
                s.tag[i] = e[2]; regs = (e[1],)
            for r in regs:
                s.touch[r].append(i)
                if r < n and op != 'INIT' and op != 'CLEAR': s.ops[r].append(i)
    def legal(s, a, b): return (s.sp[a] & ~s.sp[b]) == 0 and s.sp[a] != s.sp[b]
    def path(s, r, override=None):
        """override: dict E idx -> (key, tag) for moved/retagged ops (may include ops of other regs)."""
        L = s.ops[r]
        if override:
            items = []
            for i in L:
                k, t = override.get(i, (s.key[i], s.tag[i])); items.append((k, t))
            items.sort()
            tags = [t for _, t in items]
        else:
            tags = [s.tag[i] for i in L]
        q = [s.W['initial'][r]] + tags + [s.W['final'][r]]
        o = [q[0]]
        for c in q[1:]:
            if c != o[-1]: o.append(c)
        return o
    def cost(s, o):
        t = 0.0
        for a, b in zip(o, o[1:]):
            if not s.legal(a, b): return None
            t += f(abs(s.dim[b] - s.dim[a]))
        return t
    def conflicts(s, i, x):
        """does event x fail to commute with ADD event i?"""
        e = s.ev[i]; d, src = e[1], e[2]; y = s.ev[x]; op = y[0]
        if op in ('INIT', 'CLEAR', 'SCALE'): return y[1] in (d, src)
        # ADD/COPY y: dst y1, src y2
        if op == 'COPY' and y[1] in (d, src): return True
        if y[2] == d: return True          # reads d
        if y[1] == src: return True        # writes src
        return False
    def window(s, i):
        e = s.ev[i]
        if e[0] != 'ADD': return (i, i)
        d, src = e[1], e[2]
        cand = sorted(set(s.touch[d]) | set(s.touch[src]))
        j = bisect.bisect_left(cand, i)
        lo = -1
        for x in reversed(cand[:j]):
            if s.conflicts(i, x): lo = x; break
        hi = len(s.ev)
        for x in cand[j + 1:]:
            if s.conflicts(i, x): hi = x; break
        return (lo, hi)
    def rebuild(s, override):
        """new word: apply override {E idx: (key, tag)}; regenerate MOVEs of affected public regs only."""
        W = s.W; n = s.n
        aff = set()
        for i in override:
            e = s.ev[i]
            for r in ((e[1], e[2]) if e[0] in ('ADD', 'COPY') else (e[1],)):
                assert r < n, 'owned touched'; aff.add(r)
        # new E order
        keys = [override[i][0] if i in override else s.key[i] for i in range(len(s.ev))]
        # attach old MOVEs (unaffected regs) to the next non-MOVE event in old order
        prog = W['program']; att = defaultdict(list); tail = []; k = 0; pend = []
        for e in prog:
            if e[0] == 'MOVE':
                if e[1] in aff: continue
                pend.append(e)
            else:
                if pend and k not in override: att[k].extend(pend); pend = []
                k += 1
        tail = pend
        order = sorted(range(len(s.ev)), key=lambda i: (keys[i], i))
        evs = []
        for i in order:
            e = list(s.ev[i])
            if i in override:
                t = override[i][1]
                if e[0] in ('ADD', 'COPY'): e[4] = t
                elif e[0] == 'SCALE': e[3] = t
            evs.append((i, e))
        # MOVE insertion for affected regs: before first op at each new chart
        ins = defaultdict(list); endm = []
        for r in aff:
            o = s.path(r, override)
            opsr = sorted(s.ops[r], key=lambda i: (keys[i], i))
            first = {}
            for i in opsr:
                t = override[i][1] if i in override else s.tag[i]
                first.setdefault(t, i)
            for a, b in zip(o, o[1:]):
                if b in first: ins[first[b]].append(['MOVE', r, a, b, False])
                else: endm.append(['MOVE', r, a, b, False])
        newp = []
        for i, e in evs:
            newp.extend(att.get(i, []))   # NOTE: unaffected MOVEs keep their old successor event
            newp.extend(ins.get(i, []))
            newp.append(e)
        newp.extend(tail); newp.extend(endm)
        W2 = dict(W); W2['program'] = newp
        return W2
