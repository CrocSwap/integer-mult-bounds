#!/usr/bin/env python3
"""Independent gate-frame check of a signed two-stage complex word (round6 layout), from the definitions.

Not derived from #97's round6_complex_literal_ledger.py or from frames.Checker: own F2 algebra, own labels, own
schedule. Sources: research/deferred-signed/PROOF.md (complex section), frames.py's docstring for the label
definition and the whole-residual condition, notes on copied centers.

Frames are F2-subspaces of F2^h with the dot product. A move U -> V of one role is legal iff U <= V and the residual
V cap U^perp is nondegenerate and nonalternating (has an odd-weight vector); its paid rank is dim V - dim U.
Forward stage-one schedule (one invocation), from PROOF.md "first subtracts AMz from y, restores z, injects Vx, adds
AM(z+Vx), and then restores z by M^-1 and -V", with copied centers:
  A  M at 0            B  readouts at 0: retained centers and pieces into targets (targets at 0)
  C  M^-1 at 0         D  V: source slot and X_t at <t>
  E  M at labels       F  copied centers: copy at its frame -> 0, scatter into targets at 0
  G  pieces at t^perp  H  M^-1 at F           I  -V at F           J  every role -> F
Stage two = reversed word, complemented frames, banks exchanged; checked for continuity.
Usage: cx_gate_check.py WORD.json [CLAIMED_RESULT.json] [--mutation NAME]
"""
import sys, json
from collections import Counter
from fractions import Fraction as Q

# ---------------------------------------------------------------- F2 algebra (bitmask vectors over h points)
def reduce_vec(basis, x):
    for p, b in basis:
        if x >> p & 1:
            x ^= b
    return x

def make_basis(vectors):
    basis = []                                        # list of (pivot bit, vector), pivots distinct
    for x in vectors:
        x = reduce_vec(basis, x)
        if x:
            p = x.bit_length() - 1
            basis = [(q, b ^ x if b >> p & 1 else b) for q, b in basis]
            basis.append((p, x))
    return tuple(sorted(basis))

def vecs(B):
    return [b for p, b in B]

def contains(V, U):
    return all(reduce_vec(V, u) == 0 for u in vecs(U))

def dot(a, b):
    return bin(a & b).count('1') & 1

def perp_within(V, U):
    """basis of V cap U^perp."""
    vs = vecs(V); us = vecs(U)
    rows = [(sum(dot(v, u) << j for j, u in enumerate(us)), 1 << i) for i, v in enumerate(vs)]
    kernel = []
    for col in range(len(us)):
        bit = 1 << col
        k = next((i for i, (a, _) in enumerate(rows) if a & bit), None)
        if k is None:
            continue
        a0, c0 = rows.pop(k)
        rows = [(a ^ a0, c ^ c0) if a & bit else (a, c) for a, c in rows]
    for a, c in rows:
        x = 0
        for i, v in enumerate(vs):
            if c >> i & 1:
                x ^= v
        kernel.append(x)
    return make_basis(kernel)

def nondegenerate(B):
    vs = vecs(B)
    gram = [sum(dot(a, b) << j for j, b in enumerate(vs)) for a in vs]
    return len(make_basis(gram)) == len(vs)

ALLOW_ALTERNATING = '--allow-alternating' in sys.argv     # notes/endpoint-gauge-complex.tex normal form
ALTERNATING = Counter()

def residual_ok(R):
    """Whole-residual child: nondegenerate; nonalternating unless --allow-alternating (round6's stricter rule)."""
    if not R:
        return True
    if not nondegenerate(R):
        return False
    if any(bin(x).count('1') & 1 for x in vecs(R)):
        return True
    ALTERNATING[len(R)] += 1
    return ALLOW_ALTERNATING


def _name(k):
    """retained-output name from a JSON key: '["E", 3]', "('E', 3)", 'E,3' or '*'."""
    import ast
    if isinstance(k, (list, tuple)):
        return tuple(k)
    for parse in (json.loads, ast.literal_eval):
        try:
            x = parse(k)
            return tuple(x) if isinstance(x, (list, tuple)) else (x,)
        except Exception:
            pass
    parts = k.split(',')
    return tuple(int(p) if p.strip().lstrip('-').isdigit() else p.strip() for p in parts)


class Word:
    def __init__(s, d):
        from itertools import combinations
        s.h = h = d['h']
        if 'roles' in d:                                   # port97 layout (foamy): node-indexed args, roles{}
            s.triples = [tuple(t) for t in combinations(range(h), 3)]
            args = d['args']
            sup = [0] * len(args)
            for i in range(len(s.triples)):
                assert args[i + 1] is None
                sup[i + 1] = 1 << i
            for n in range(len(s.triples) + 1, len(args)):
                if args[n] is None:
                    continue
                a, b = args[n]
                assert 0 < a < n and 0 < b < n and not sup[a] & sup[b], ('cancellation or order', n)
                sup[n] = sup[a] | sup[b]
            s.nodes = {int(n): dict(sup=sup[n], args=args[n]) for n in d['active']}
            ro = dict(d['roles'])
            if isinstance(ro['src'], list):
                ro['src'] = {','.join(map(str, S)): sl for S, sl in ro['src']}
            if isinstance(ro['rout'], list):
                ro['rout'] = {json.dumps([nm] if isinstance(nm, str) else list(nm)): sl for nm, sl in ro['rout']}
        else:
            s.triples = [tuple(t) for t in d['triples']]
            s.nodes = {int(n): x for n, x in d['nodes'].items()}
            ro = d
        s.tid = {t: i for i, t in enumerate(s.triples)}
        s.v = len(s.triples)
        s.pieces = [(tuple(S), n, coef) for S, n, coef in d['pieces']]
        s.retained = [(_name([e[0]] if isinstance(e[0], str) else e[0]), e[1]) for e in d['retained']]
        s.R = ro['size']
        s.gates = [(n, tuple(ins), tuple(outs)) for n, ins, outs in ro['gates']]
        s.src = {tuple(map(int, str(k).strip('()[] ').split(','))): v for k, v in ro['src'].items()}
        s.pout = {int(i): sl for i, sl in ro['pout'].items()} if isinstance(ro['pout'], dict) else dict(enumerate(ro['pout']))
        s.rout = {_name(k): sl for k, sl in ro['rout'].items()}
        for n in s.nodes:                                  # leaves: node i+1 is triple i
            if not s.nodes[n]['args']:
                assert s.nodes[n]['sup'] == 1 << (n - 1), ('leaf numbering', n)
        s.ZERO = make_basis([])
        s.FULL = make_basis([1 << i for i in range(h)])
        s.tvec = [sum(1 << p for p in t) for t in s.triples]
        s.line = [make_basis([x]) for x in s.tvec]
        s.hyper = [perp_within(s.FULL, L) for L in s.line]
        s._label = {}

    def label(s, n):
        """leaf <t>; several triples sharing a common pair -> span of indicators; else covered coordinates."""
        if n not in s._label:
            sup = s.nodes[n]['sup']
            idx = [i for i in range(s.v) if sup >> i & 1]
            if len(idx) == 1:
                B = make_basis([s.tvec[idx[0]]])
            else:
                common = set(s.triples[idx[0]]).intersection(*[s.triples[i] for i in idx[1:]])
                if len(common) >= 2:
                    B = make_basis([s.tvec[i] for i in idx])
                else:
                    cover = 0
                    for i in idx:
                        cover |= s.tvec[i]
                    B = make_basis([1 << p for p in range(s.h) if cover >> p & 1])
            s._label[n] = B
        return s._label[n]


def center_terms(w):
    """targets and coefficients of the retained readouts (PROOF.md: twice the centre scatter at S is
    2T - sum_{i in S} E_i if h-1 not in S, and (5-h)T + sum_{i<h-1, i not in S} E_i otherwise)."""
    h, v = w.h, w.v
    terms = {name: [] for name in w.rout}
    if ('*',) not in w.rout:
        # PR #104 all-disjoint centres A_i = G - T_i with G = sum_i A_i / 21: the scatter for target S is
        # G - (1/2) sum_{i in S} A_i, so every retained centre reads every target (coefficient 1/21 - [i in S]/2).
        for name in w.rout:
            terms[name] = [(v + j, 1) for j in range(v)]
        return terms
    for j, T in enumerate(w.triples):
        if h - 1 not in T:
            terms[('*',)].append((v + j, 2)); sel = T; sg = -1
        else:
            terms[('*',)].append((v + j, 5 - h)); sel = [i for i in range(h - 1) if i not in T]; sg = 1
        for i in sel:
            terms[('E', i)].append((v + j, sg))
    return terms


def forward(w, mutation=None, sample=()):
    h, v, R = w.h, w.v, w.R
    off = 2 * v
    cur = [w.line[t] for t in range(v)] + [w.ZERO] * (v + R)     # X at <t>, Y and aux at 0
    if mutation == 'merged-entrance':
        for q in sample:
            cur[off + q] = None                                         # source frame shifted below 0 (symbolic)
    initial = list(cur)
    events = []                                                         # ('move', reg, old, new) | ('add', a, b) | ('copy', reg, f, terms)
    bad = []
    cache = {}

    def move(reg, f, where):
        old = cur[reg]
        if old == f:
            return
        if old is None:
            bad.append((where, reg, 'shifted source must pass the background gate at 0'))
            cur[reg] = f
            return
        key = (old, f)
        if key not in cache:
            cache[key] = contains(f, old) and residual_ok(perp_within(f, old))
        if not cache[key]:
            bad.append((where, reg, len(old), len(f)))
        events.append(('move', reg, old, f))
        cur[reg] = f

    def add(a, b, where):
        if cur[a] != cur[b]:
            bad.append((where, 'unequal frames', a, b))
        events.append(('add', a, b))

    def mix(mode, inverse, where):
        for n, ins, outs in (reversed(w.gates) if inverse else w.gates):
            f = w.ZERO if mode == 'low' else w.FULL if mode == 'high' else w.label(n)
            for q in sorted(set(ins + outs)):
                move(off + q, f, where)
            if inverse:
                for q in reversed(outs[1:]):
                    add(off + q, off + outs[0], where)
                if len(ins) == 2:
                    add(off + ins[0], off + ins[1], where)
            else:
                if len(ins) == 2:
                    add(off + ins[0], off + ins[1], where)
                for q in outs[1:]:
                    add(off + q, off + outs[0], where)

    terms = center_terms(w)

    def centers(copied, where):
        for name, sl in sorted(w.rout.items()):
            reg = off + sl
            if copied:
                f = cur[reg]
                if not residual_ok(f):
                    bad.append((where, reg, 'copy transform residual'))
                for t, _ in terms[name]:
                    if cur[t] != w.ZERO:
                        bad.append((where, 'target not at 0 for copied centre', t))
                events.append(('copy', reg, f, tuple(t for t, _ in terms[name])))
            else:
                move(reg, w.ZERO, where)
                for t, _ in terms[name]:
                    add(t, reg, where)

    def pieces(high, where):
        for i, (S, n, cf) in enumerate(w.pieces):
            t = w.tid[S]
            f = w.hyper[t] if high else w.ZERO
            move(off + w.pout[i], f, where); move(v + t, f, where); add(v + t, off + w.pout[i], where)

    def sources(high, where):
        for T, sl in sorted(w.src.items()):
            t = w.tid[T]
            f = w.FULL if high else w.line[t]
            move(off + sl, f, where); move(t, f, where); add(off + sl, t, where)

    mix('low', False, 'A')
    centers(False, 'B'); pieces(False, 'B')
    mix('low', True, 'C')
    sources(False, 'D')
    mix('label', False, 'E')
    if mutation == 'centres-after-pieces':
        pieces(True, 'G'); centers(True, 'F')
    else:
        centers(True, 'F'); pieces(True, 'G')
    mix('high', True, 'H')
    sources(True, 'I')
    for s in range(R):
        move(off + s, w.FULL, 'J')
    final = list(cur)
    ok_final = final[:v] == [w.FULL] * v and final[v:off] == w.hyper and final[off:] == [w.FULL] * R
    return events, initial, final, bad, ok_final


def reflect(w, events, initial, final):
    """Stage two: reversed events, complemented frames, banks exchanged; continuity of every role."""
    v = w.v; off = 2 * v
    bank = lambda s: s + v if s < v else s - v if s < off else s
    rev = {}
    for s, f in enumerate(final):
        rev[bank(s)] = ('comp', f)
    breaks = 0
    for e in reversed(events):
        if e[0] == 'move':
            _, reg, old, new = e
            r = bank(reg)
            if rev[r] != ('comp', new):
                breaks += 1
            rev[r] = ('comp', old)
        elif e[0] == 'add':
            if rev[bank(e[1])] != rev[bank(e[2])]:
                breaks += 1
        else:
            _, reg, f, targets = e
            if rev[bank(reg)] != ('comp', f) or any(rev[bank(t)] != ('comp', w.ZERO) for t in targets):
                breaks += 1
    end = all(rev[bank(s)] == ('comp', initial[s]) for s in range(len(initial)) if initial[s] is not None)
    return breaks, end


def paid_histogram(w, events):
    v = w.v; off = 2 * v; h = w.h; m = h * h; N = v * v
    hist = Counter()
    cls = Counter()
    for e in events:
        if e[0] == 'move':
            r = len(e[3]) - len(e[2])
            hist[r] += 1
            cls['aux' if e[1] >= off else 'data'] += r
        elif e[0] == 'copy':
            hist[len(e[2])] += 1
            cls['center'] += len(e[2])
    paid = Counter({r: 2 * v * n for r, n in hist.items()})
    paid[m - h] += 2 * v * w.R
    paid[(h - 1) ** 2] += 2 * N
    paid[1] += N
    return paid, cls


def moment_report(paid, m, W):
    """Float sanity check (fsum) of sum_t t n_t/(mW) (m/t)^a at a few savings; the exact certificate is elsewhere."""
    from math import fsum, exp, log
    def mom(a):
        return fsum(t * n * exp(a * log(m / t)) for t, n in paid.items()) / (m * W)
    out = {}
    for a in (Q(258969, 2500000000), Q(258970, 2500000000), Q(36926111, 500000000000),
              Q(1037353, 10**10), Q(1037354, 10**10)):
        out[str(a)] = '%.15f' % mom(float(a))
    return out


def main():
    w = Word(json.load(open(sys.argv[1])))
    claimed = None
    args = [a for a in sys.argv[2:] if a != '--allow-alternating']
    mutation = None
    if '--mutation' in args:
        mutation = args[args.index('--mutation') + 1]
        args = [a for a in args if a not in ('--mutation', mutation)]
    if args:
        cj = json.load(open(args[0]))
        claimed = {int(k): v for k, v in (cj['full_histogram'] if 'full_histogram' in cj else cj['rows']).items()}
    sample = range(0, w.R, 101) if mutation == 'merged-entrance' else ()
    if mutation == 'degenerate-label':
        n0 = next(n for n, x in sorted(w.nodes.items()) if x['args'])
        w._label[n0] = make_basis([0b11, 0b1100])                  # alternating 2-plane: residual must fail
    if mutation == 'link-swap':
        g = [i for i, (n, ins, outs) in enumerate(w.gates) if len(ins) == 2]
        a, b = g[len(g) // 3], g[2 * len(g) // 3]
        (na, ia, oa), (nb, ib, ob) = w.gates[a], w.gates[b]
        w.gates[a], w.gates[b] = (nb, ia, oa), (na, ib, ob)        # a donor's slot meets a non-nested consumer frame
    events, initial, final, bad, ok_final = forward(w, mutation, sample)
    breaks, end = reflect(w, events, initial, final)
    paid, cls = paid_histogram(w, events)
    rank = sum(r * n for r, n in paid.items())
    v, h = w.v, w.h
    res = dict(h=h, roles=w.R, events=len(events), moves=sum(1 for e in events if e[0] == 'move'),
               violations=len(bad), first=[str(x) for x in bad[:3]], final_states_ok=ok_final,
               stage_two_breaks=breaks, stage_two_endpoints_ok=end,
               aux_rank=cls['aux'], aux_expected=w.R * h, data_rank=cls['data'], data_expected=2 * v * (h - 1),
               center_rank=cls['center'],
               center_expected=(h - 1) ** 2 + h if ('*',) in w.rout else len(w.rout) * (h - 1),
               recursive_rank=rank, maxchild=max(paid),
               histogram_matches_claim=(dict(paid) == claimed) if claimed is not None else None,
               histogram_diff=({r: (paid.get(r, 0), claimed.get(r, 0)) for r in set(paid) | set(claimed)
                                if paid.get(r, 0) != claimed.get(r, 0)} if claimed is not None else None),
               W=2 * v * v + 2 * v * w.R,
               moment_at=moment_report(paid, h * h, 2 * v * v + 2 * v * w.R),
               alternating_residuals_by_rank=dict(ALTERNATING), allow_alternating=ALLOW_ALTERNATING,
               mutation=mutation)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
