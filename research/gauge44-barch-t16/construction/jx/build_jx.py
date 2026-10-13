#!/usr/bin/env python3
"""build_jx.py --input WORD --recipe RECIPE.json --out OUT.json.gz [--control NAME] [--no-pin]

Stdlib-only builder: joint read-set exchange (copy pairs, BRoute sw4 rule) + explicit B frame raises on P6k4sw4.
Steps:
 1. input content sha256 must equal recipe.input_content_sha256.
 2. explicit B edits: replace (old gate asserted), delete (old gate asserted), insert (before an original index).
 3. frames: replaced/inserted gates take the plain join of their operands' current frames; gates listed in
    frames_741 / raises take base = the listed frame and the resulting frame must EQUAL it (explicit frames);
    every other gate keeps span(stored frame + operand frames) (monotone repair). Early cleanup likewise.
 4. legality: target frames inside u_t^perp at every gate; tails inside helper_final; every end frame contains the
    final frame; the explicit frame must contain the join (enforced by equality in 3).
 5. exactness: the rational linear map of the whole B segment is identical to the input's (Fraction replay).
 6. paid profile recomputed (A + centre levels + B + tails + ends) and written to report.local_profile.
Output: canonical json (sort_keys, compact) gzip mtime=0. Exit 0 and prints output sha; exit 2 with the first
rejection (site) on failure. --control applies a named mutation from recipe.controls (expected to be rejected
or to give a pinned sha)."""
import argparse, gzip, json, hashlib, sys, copy
from fractions import Fraction as Fr
from collections import Counter

V, H = 112, 9

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
def hyper(p): return basis([x for x in range(1, 1 << H) if (x & p).bit_count() % 2 == 0])
FULL = basis([1 << i for i in range(H)])
def csha(w): return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

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

def build(w, rc, control=None):
    w = copy.deepcopy(w); B0 = w['B']
    edits = copy.deepcopy(rc['edits']); explicit = {int(i): f for i, f in rc['frames_741']}
    for i, f in rc['raises']:
        if int(i) in explicit: raise Reject(('duplicate frame', i))
        explicit[int(i)] = f
    if control:
        c = rc['controls'][control]['mutation']
        if c['kind'] == 'drop_insert': edits['insert'] = [x for k, x in enumerate(edits['insert']) if k != c['k']]
        elif c['kind'] == 'flip_insert_sign': edits['insert'][c['k']]['gate'][3] *= -1
        elif c['kind'] == 'frame': explicit[c['i']] = c['frame']
        elif c['kind'] == 'drop_edits': edits = dict(replace=[], delete=[], insert=[])
        elif c['kind'] == 'drop_raises': explicit = {int(i): f for i, f in rc['frames_741']}
        elif c['kind'] == 'only_edits_of':
            hs = set(c['h'])
            edits = {k: [x for x in v if x['h'] in hs] for k, v in edits.items()}
            explicit = {i: f for i, f in explicit.items() if i in {int(j) for j, _ in rc['frames_741']} or i in set(c['raises'])}
        elif c['kind'] == 'empty': edits = dict(replace=[], delete=[], insert=[]); explicit = {}
        else: raise SystemExit('unknown control')
    B = [list(e) for e in B0]; tag = set(); dele = set(); ins = {}
    for x in edits['replace']:
        i = x['i']
        if B[i][:-1] != x['old']: raise Reject(('replace old mismatch', i))
        B[i] = list(x['new']) + [B[i][-1]]; tag.add(i)
    for x in edits['delete']:
        i = x['i']
        if B[i][:-1] != x['old']: raise Reject(('delete old mismatch', i))
        dele.add(i)
    for x in edits['insert']: ins.setdefault(x['before'], []).append(list(x['gate']) + [None])
    NB, nt, key = [], set(), []
    for i, e in enumerate(B):
        for g in ins.get(i, []): nt.add(len(NB)); NB.append(g); key.append(None)
        if i in dele: continue
        if i in tag: nt.add(len(NB))
        NB.append(e); key.append(i)
    # frames + paid
    R = w['report']['R']; n = 2 * V + R
    END = [FULL] * V + [hyper(p) for p in w['ports']] + [FULL] * R
    for q, U in w['helper_final'].items(): END[int(q)] = basis(U)
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
    used = set()
    for j, e in enumerate(NB):
        rs = registers(e); k = key[j]
        if k is not None and k in explicit: base = list(explicit[k]); used.add(k)
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
    for q in range(n):
        if not contained(cur[q], END[q]): raise Reject(('end', q))
        d = len(END[q]) - len(cur[q])
        if d: paid[d] += 1
    # exactness of the B segment
    a, b = symstate([e[:-1] for e in B0]), symstate([e[:-1] for e in NB])
    bad = sorted(q for q in set(a) | set(b) if a.get(q, {q: Fr(1)}) != b.get(q, {q: Fr(1)}))
    if bad: raise Reject(('exactness rows', bad))
    w['B'] = NB; w['early_cleanup'] = newearly
    w['report'] = dict(w['report']); w['report']['local_profile'] = {str(k): v for k, v in sorted(paid.items())}
    return w

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--input', required=True); ap.add_argument('--recipe', required=True)
    ap.add_argument('--out'); ap.add_argument('--control'); ap.add_argument('--no-pin', action='store_true')
    a = ap.parse_args()
    w = json.loads(gzip.decompress(open(a.input, 'rb').read())); rc = json.load(open(a.recipe))
    if csha(w) != rc['input_content_sha256']: print('REJECT input pin'); sys.exit(2)
    pin = rc['controls'][a.control].get('rejection_expected') if a.control else None
    try: o = build(w, rc, a.control)
    except Reject as r:
        got = json.loads(json.dumps(r.args[0])); print('REJECT', json.dumps(got))
        if pin is not None:
            print('CONTROL', 'PINNED' if got == pin else 'PIN MISMATCH %s' % json.dumps(pin)); sys.exit(0 if got == pin else 4)
        sys.exit(2)
    if pin is not None and not a.no_pin: print('CONTROL NOT REJECTED, pinned', json.dumps(pin)); sys.exit(4)
    s = csha(o)
    exp = rc['controls'][a.control].get('expected_sha') if a.control else rc['expected']['output_content_sha256']
    print('OK', s, o['report']['local_profile'])
    if a.out: open(a.out, 'wb').write(gzip.compress(json.dumps(o, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    if not a.no_pin and exp and s != exp: print('REJECT output pin', exp); sys.exit(3)

if __name__ == '__main__': main()
