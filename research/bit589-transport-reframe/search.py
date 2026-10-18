"""Exhaustive search: one commuting relocation of a phase-A or phase-B summand or gate of PR589's word, then the
exact frame optimum over all frame assignments.

Move classes (D and C are never changed; C is the literal reverse of the z-destination gates and is accounted for
implicitly, see reframe.py):
  summand   take one source s out of a gate t += {..., s, ...} as its own gate t += s and insert it at any position of
            the same section reachable by crossing only gates it commutes with (single-source gates: the whole gate
            moves). The positions next to its own remainder are the in-place splits of a multi-source gate.
  gate      move a whole multi-source gate the same way.
  xsummand, xgate   the same moves continued across the scatter into the other section; allowed only when the moved
            gate commutes with the scatter (it writes neither a target nor a retained total and reads no target),
            which keeps H1-H5 syntactically (A writes only z registers, B z-gates write z from z).
Two XOR gates commute iff neither writes a register the other reads. A position matters only through the order of
the gates on the moved operands (and the section), so one representative per slot between consecutive gates that touch
the moved operands is evaluated; positions in one slot give identical register sequences and hence identical optima.

Usage: search.py WORD.json.gz C_NUMERATOR/C_DENOMINATOR [--jobs N] [--out FILE]
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import json
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reframe as R


def commute(a, b):
    return a[1] not in b[2] and b[1] not in a[2]


def touches(g, regs):
    return g[1] in regs or any(s in regs for s in g[2])


def slots(L2, o, p0):
    """insertion indices into L2 for gate o, one per slot, starting from its legal original index p0"""
    regs = {o[1], *o[2]}
    out = [p0]
    p = p0
    while p > 0 and commute(o, L2[p - 1]):
        p -= 1
        if touches(L2[p], regs):
            out.append(p)
    p = p0
    while p < len(L2) and commute(o, L2[p]):
        p += 1
        if touches(L2[p - 1], regs):
            out.append(p)
    return out


def candidates(word, regs=None):
    """(kind, section, index, source or None, insertion index) for every relocation slot except the identity;
    with regs, only moves out of gates that touch one of those registers"""
    out = []
    for sec in 'AB':
        L = getattr(word, sec)
        for i, (f, t, ss) in enumerate(L):
            if regs is not None and t not in regs and not any(x in regs for x in ss):
                continue
            for s in ss:
                o = (f, t, (s,))
                if len(ss) > 1:
                    L2 = L[:i] + [(f, t, tuple(x for x in ss if x != s))] + L[i + 1:]
                else:
                    L2 = L[:i] + L[i + 1:]
                for p in slots(L2, o, i):
                    if len(ss) == 1 and p == i:
                        continue  # identity
                    out.append(('summand', sec, i, s, p))
            if len(ss) > 1:
                o = (f, t, ss)
                L2 = L[:i] + L[i + 1:]
                for p in slots(L2, o, i):
                    if p != i:
                        out.append(('gate', sec, i, None, p))
    return out


def crosses_scatter(word, o):
    """o commutes with the scatter (targets ^= retained totals) and may sit in either phase under H3: it writes
    neither a target nor a retained total, and reads no target"""
    V = word.V
    t, ss = o[1], o[2]
    return not (V <= t < 2 * V) and t not in word.pin and not any(V <= s < 2 * V for s in ss)


def cross_candidates(word, regs=None):
    """relocations that cross the scatter: (kind, section, index, source or None, destination section, index),
    one per slot of the destination section reachable through commuting gates (the scatter counts as a boundary)"""
    out = []
    for sec in 'AB':
        L, M = (word.A, word.B) if sec == 'A' else (word.B, word.A)
        for i, (f, t, ss) in enumerate(L):
            if regs is not None and t not in regs and not any(x in regs for x in ss):
                continue
            variants = [('xsummand', s, (f, t, (s,)),
                         L[:i] + ([(f, t, tuple(x for x in ss if x != s))] if len(ss) > 1 else []) + L[i + 1:])
                        for s in ss]
            if len(ss) > 1:
                variants.append(('xgate', None, (f, t, ss), L[:i] + L[i + 1:]))
            for kind, s, o, L2 in variants:
                if not crosses_scatter(word, o):
                    continue
                regs_o = {o[1], *o[2]}
                if sec == 'A':  # walk forward to the end of A, then into B from its start
                    p = i
                    while p < len(L2) and commute(o, L2[p]):
                        p += 1
                    if p < len(L2):
                        continue
                    q = 0
                    out.append((kind, sec, i, s, 'B', q))
                    while q < len(M) and commute(o, M[q]):
                        q += 1
                        if touches(M[q - 1], regs_o):
                            out.append((kind, sec, i, s, 'B', q))
                else:  # walk backward to the start of B, then into A from its end
                    p = i
                    while p > 0 and commute(o, L2[p - 1]):
                        p -= 1
                    if p > 0:
                        continue
                    q = len(M)
                    out.append((kind, sec, i, s, 'A', q))
                    while q > 0 and commute(o, M[q - 1]):
                        q -= 1
                        if touches(M[q], regs_o):
                            out.append((kind, sec, i, s, 'A', q))
    return out


def apply(word, cand):
    if cand[0] in ('xsummand', 'xgate'):
        kind, sec, i, s, dst, q = cand
        L, M = (word.A, word.B) if sec == 'A' else (word.B, word.A)
        f, t, ss = L[i]
        if kind == 'xsummand':
            o = (f, t, (s,))
            L2 = L[:i] + ([(f, t, tuple(x for x in ss if x != s))] if len(ss) > 1 else []) + L[i + 1:]
        else:
            o = (f, t, ss)
            L2 = L[:i] + L[i + 1:]
        M2 = M[:q] + [o] + M[q:]
        return (L2, M2) if sec == 'A' else (M2, L2)
    kind, sec, i, s, p = cand
    L = getattr(word, sec)
    f, t, ss = L[i]
    if kind == 'summand':
        o = (f, t, (s,))
        L2 = L[:i] + ([(f, t, tuple(x for x in ss if x != s))] if len(ss) > 1 else []) + L[i + 1:]
    else:
        o = (f, t, ss)
        L2 = L[:i] + L[i + 1:]
    L2 = L2[:p] + [o] + L2[p:]
    return (L2, word.B) if sec == 'A' else (word.A, L2)


_W = None


def _init(path, z):
    global _W, _Z
    _W = R.Word(R.load(path))
    _Z = z


def _eval(batch):
    res = []
    for cand in batch:
        A, B = apply(_W, cand)
        o = R.optimum(_W, A, B, _Z)
        res.append((cand, None if o is None else (o['cost'], o['profile'], o['free'], o['components'],
                                                   o['enumerated'])))
    return res


def main():
    path = sys.argv[1]
    c = Fraction(sys.argv[2])
    z = float(c)
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else os.cpu_count()
    outp = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    t0 = time.time()
    word = R.Word(R.load(path))
    base = R.optimum(word, word.A, word.B, z)
    assert base['profile'] == R.fixed_profile(word, word.A, word.B), 'base word is not frame-optimal in this model'
    cands = candidates(word) + cross_candidates(word)
    batches = [cands[k:k + 64] for k in range(0, len(cands), 64)]
    results = []
    with Pool(jobs, initializer=_init, initargs=(path, z)) as pool:
        for part in pool.imap(_eval, batches):
            results.extend(part)
    legal = [(cand, r) for cand, r in results if r is not None]
    deltas = sorted(((r[0] - base['cost'], cand, r[1]) for cand, r in legal), key=lambda x: (x[0], x[1]))
    improving = [d for d in deltas if d[0] < -1e-9]
    same = [d for d in deltas if abs(d[0]) <= 1e-9]
    kinds = {}
    for cand, r in results:
        k = (cand[0], cand[1])
        e = kinds.setdefault('%s/%s' % k, dict(candidates=0, legal=0, improving=0, same_cost=0))
        e['candidates'] += 1
        if r is not None:
            e['legal'] += 1
            d = r[0] - base['cost']
            e['improving'] += d < -1e-9
            e['same_cost'] += abs(d) <= 1e-9
    report = dict(
        word=os.path.basename(path), c=str(c), base_profile=base['profile'], base_cost=base['cost'],
        base_free_gates=base['free'], base_components=base['components'],
        candidates=len(cands), legal=len(legal), illegal=len(cands) - len(legal),
        improving=len(improving), same_cost=len(same), by_kind=kinds,
        best=[dict(delta=d, move=list(cand), profile=prof) for d, cand, prof in deltas[:20]],
        smallest_nonzero_loss=min((d for d, _, _ in deltas if d > 1e-9), default=None),
        seconds=round(time.time() - t0, 1))
    if '--detail' in sys.argv:
        report['detail'] = [dict(kind=cand[0], sec=cand[1], i=cand[2], s=cand[3],
                                 dst=cand[4] if len(cand) == 6 else cand[1], p=cand[-1],
                                 profile=None if r is None else r[1]) for cand, r in results]
    js = json.dumps(report, indent=1, default=str)
    if outp:
        open(outp, 'w').write(js + '\n')
    print(js)


if __name__ == '__main__':
    main()
