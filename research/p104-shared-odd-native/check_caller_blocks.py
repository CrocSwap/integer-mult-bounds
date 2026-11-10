#!/usr/bin/env python3
"""Check of the joint caller with type A constant blocks resynthesized (method and blocks: CubeJerry #6912; code: this package).

usage: check_caller_blocks.py OLD_CALLER NEW_CALLER A6912_BEFORE A6912_AFTER [WORD ...]
  OLD_CALLER   the shipped joint caller (#6932 data/caller.json, sha 54badc10...)
  NEW_CALLER   the rewritten joint caller (gen_joint_caller.py output)
  A6912_*      #6912's data/caller-before.json (sha c403bb58...) and caller-after.json (sha e83221e5...), read as data
  WORD:S       optional word .json.gz files with their declared certificate S (225 or 1125): invoice (T, P, S, kappa) and the raw readings are recomputed for each
Exit code 0 only if every check passes and every failing control fails.  Standard library only."""
import copy, gzip, hashlib, json, os, sys, math
from collections import Counter
from decimal import Decimal as Dec, getcontext
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jclib as L
from jclib import need

getcontext().prec = 50
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
PINS = {'before': 'c403bb58f732de8356ed7fef3717649b209ba9d37eb4b8000eec9d876dc7142f',
        'after': 'e83221e5de1cd75b92bbbc40057f07e406af9551bd511bae659fa7173d6d5332',
        'old': '54badc10f975dd320bcc95c727c42fe2d7a7528f9a43a58c9fd323dd06dc38a0'}
SAVING = 32 * 40 * 96 * (2492 - 1194)


def stream(C, ty):
    return [e for e in C['events'] if e[0] in (ty, 'J')]


def a_equal_6912(C, bf):
    """type A stream of the joint caller equals #6912's source caller event for event (J read as HOST2)"""
    A = [e for e in C['events'] if e[0] in ('A', 'J')]
    need(len(A) == len(bf['events']), 'A stream length')
    for a, b in zip(A, bf['events']):
        if a[0] == 'J':
            need(b[0] == 'HOST2' and b[1] == a[1] and list(b[2:]) == list(a[2]), 'J anchor vs HOST2 %r %r' % (a, b))
        else:
            need(list(a[1:]) == list(b), 'A event %r vs %r' % (a, b))
    need(C['types']['A']['diagonal'] == bf['diagonal'] and bf['n'] == 40 == C['types']['A']['roles'] and bf['stages'] == C['stages'] and bf['ambient_rank'] == C['ambient_rank']
         and Counter(str(bf[k]) for k in ('alpha2', 'beta2')) == Counter(str(C['types']['A'][k]) for k in ('alpha2', 'beta2')), 'A metadata / diagonal')
    return len(A)


def verify_rewrite(old, new, replay_points=0, full=True):
    """all structural checks that a rewrite of type A constant blocks is exact; raises ValueError on any failure"""
    L.check_disjoint(old); L.check_disjoint(new)
    need({k: v for k, v in old.items() if k != 'events'} == {k: v for k, v in new.items() if k != 'events'}, 'caller metadata (types, diagonals, ports, pairs) unchanged')
    # B events and every nonconstant / joint event: same sequence
    need([e for e in old['events'] if e[0] == 'B'] == [e for e in new['events'] if e[0] == 'B'], 'type B events unchanged and in order')
    na = lambda C: [e for e in C['events'] if e[0] == 'J' or (e[0] == 'A' and e[1] not in L.CONST)]
    need(na(old) == na(new), 'nonconstant A events and joint contacts unchanged and in order')
    so, co = L.slots(old['events'], 'A'); sn, cn = L.slots(new['events'], 'A')
    need(len(so) == len(sn), 'same slot structure')
    changed = ent = 0
    for k, (a, b) in enumerate(zip(so, sn)):
        ba = [old['events'][i] for i in a]; bb = [new['events'][i] for i in b]
        if ba == bb:
            continue
        L.alphabet_ok(bb)
        Ma, Mb = L.block_matrix(ba, 'A'), L.block_matrix(bb, 'A')
        need(Ma == Mb, 'block %d matrix differs' % k)
        changed += 1; ent += 40 * 40
    return changed, ent


def replay_check(old, new, points):
    for qv, D in points:
        Ro = L.replay_matrix(old, qv, D); Rn = L.replay_matrix(new, qv, D)
        need(Ro == Rn, 'full 78x78 caller matrix differs at a point')
        if pow(qv, 4, L.PM) == 1:
            need(L.target_bad(new, Rn, qv, D) == 0, 'caller does not reach the block-diagonal target')
    return len(points)


def prefix_mass(C, ty):
    """largest l1 row sum on any prefix inside a constant block (rows start from identity at each anchor)"""
    n, off = L.NR[ty], L.OFF[ty]; best = 0; mx = 0
    for b in L.old_blocks(C, ty):
        rows = {off + i: [int(i == j) for j in range(n)] for i in range(n)}
        for e in b:
            L.apply_const(rows, e); best = max(best, max(sum(abs(x) for x in r) for r in rows.values())); mx = max(mx, max(abs(x) for r in rows.values() for x in r))
    return best, mx


def height_bits(C, ty):
    """log2 of the product of (1+|a|) over the ADD events of the type (the constant-gate factor of #6912's height bound)"""
    return sum(math.log2(1 + abs(float(L.Q(e[4])))) for e in C['events'] if e[0] == ty and e[1] == 'ADD')


def invoice(J, W):
    d = [len(b) for b in W['frames']]; n = len(W['initial']); live = set(W['live']); h = W['hosted']
    main = live | {r + 112 for r in live} | set(h['X2']) | set(h['Y2'])
    hel = Counter(d[W['final'][r]] - d[W['initial'][r]] for r in range(n) if r not in main)
    paid = Counter(abs(d[e[3]] - d[e[2]]) for e in W['program'] if e[0] == 'MOVE')
    T = Counter(); P = Counter()
    for r, v in hel.items(): T[r] += 18 * v
    for r, v in paid.items(): P[r] += 18 * v
    for ty in 'AB':
        cnt = len(J['types'][ty]['ports'])
        for e in J['events']:
            if e[0] == ty and e[1] == 'QUERY': P[1] += cnt
            elif e[0] == ty and e[1] == 'IDLE_ONE': P[8 * len(e[3])] += cnt
        for t in J['types'][ty]['diagonal']: T[int(t[0] % 2) + 8 * sum(t[2:])] += cnt
    S = sum(r * (T[r] - P[r]) for r in set(T) | set(P))
    rs = set(T) | set(P)
    mom = lambda k: sum((Dec(T[r]) - Dec(P[r])) * (Dec(r).ln() * (1 - k)).exp() for r in rs)
    lo, hi = Dec('0.003'), Dec('0.0045')
    for _ in range(160):
        m = (lo + hi) / 2
        if mom(m) > 0: lo = m
        else: hi = m
    return T, P, S, lo


def controls(old, new, bf):
    """every mutation must be rejected by verify_rewrite (structural) and, where it changes the operator, by the full replay"""
    out = []
    idxA = [i for i, e in enumerate(new['events']) if e[0] == 'A' and e[1] in L.CONST]
    chg = []
    so, _ = L.slots(old['events'], 'A'); sn, _ = L.slots(new['events'], 'A')
    for a, b in zip(sn, so):
        if [new['events'][i] for i in a] != [old['events'][i] for i in b]: chg.append(a)
    blk = chg[3]; addi = next(i for i in blk if new['events'][i][1] == 'ADD'); swpi = next(i for i in blk if new['events'][i][1] == 'SWAP')
    scl = next((i for a in chg for i in a if new['events'][i][1] == 'SCALE'), None)

    def mut(f):
        m = copy.deepcopy(new); f(m); return m

    def sign(m): m['events'][addi][4] = str(-int(m['events'][addi][4]))
    def dele(m): del m['events'][swpi]
    def sc(m): m['events'][scl][2] = (m['events'][scl][2] + 1) % 40
    def delscale(m): del m['events'][scl]
    def lam(m):
        i = next(i for i, e in enumerate(m['events']) if e[0] == 'A' and e[1] == 'LAMBDA'); m['events'][i][3] *= -1
    def across(m):          # move the last gate of a changed block past the next joint contact
        last = blk[-1]; e = m['events'].pop(last); j = next(i for i in range(last, len(m['events'])) if m['events'][i][0] == 'J'); m['events'].insert(j + 1, e)
    def foreign(m): m['events'][addi][3] = 45
    def pair(m):            # endpoint-preserving ADD(4)/ADD(-4) outside the alphabet
        e = m['events'][addi]; m['events'].insert(addi + 1, ['A', 'ADD', e[2], e[3], '4']); m['events'].insert(addi + 2, ['A', 'ADD', e[2], e[3], '-4'])
    def exch(m):
        a, b = chg[1], chg[2]; ea = [m['events'][i] for i in a]; eb = [m['events'][i] for i in b]
        for i, e in zip(a[:min(len(a), len(eb))], eb): m['events'][i] = e
        # keep lengths: only valid when equal; else truncated copy still differs in matrix
    def delB(m): del m['events'][next(i for i, e in enumerate(m['events']) if e[0] == 'B' and e[1] == 'ADD')]
    def anchor(m):
        j = next(e for e in m['events'] if e[0] == 'J'); j[2] = [j[2][0], j[2][1], j[2][3], j[2][2]]
    def swapjs(m):
        js = [e for e in m['events'] if e[0] == 'J']; js[0][1], js[1][1] = js[1][1], js[0][1]
    def stale(m):           # new A block copied from the wrong slot (previous slot of the same length is not the same matrix)
        a, b = chg[5], chg[6]
        for i, j in zip(a, b): m['events'][i] = copy.deepcopy(m['events'][j])
    pt = [L.random_points()[1]]
    for name, f, replay_must in (('flipped ADD sign in a changed block', sign, True), ('deleted SWAP in a changed block', dele, True),
                                 ('SCALE moved to another role', sc, True), ('deleted SCALE', delscale, True), ('flipped LAMBDA anchor', lam, True),
                                 ('last gate of a block moved past the next J contact', across, True), ('ADD reaching a type B role', foreign, False),
                                 ('ADD(4)+ADD(-4) pair (same operator, outside alphabet)', pair, False), ('block copied over another block', stale, True),
                                 ('deleted B event', delB, True), ('J contact roles exchanged', anchor, True), ('two J stages exchanged', swapjs, True)):
        m = mut(f)
        try:
            verify_rewrite(old, m); rej_struct = False
        except (ValueError, StopIteration, IndexError): rej_struct = True
        try:
            replay_check(old, m, pt); rej_rep = False
        except (ValueError, IndexError): rej_rep = True
        out.append((name, rej_struct, rej_rep, replay_must))
    return out


def main():
    po, pn, pb, pa = sys.argv[1:5]; words = [(x.split(':')[0], int(x.split(':')[1])) for x in sys.argv[5:]]
    print('pins: old caller', sha(po) == PINS['old'], '#6912 before', sha(pb) == PINS['before'], '#6912 after', sha(pa) == PINS['after'])
    need(sha(po) == PINS['old'] and sha(pb) == PINS['before'] and sha(pa) == PINS['after'], 'source pins')
    old, new, bf, af = (json.load(open(p)) for p in (po, pn, pb, pa))
    # (1) event identity
    n = a_equal_6912(old, bf)
    print('PASS 1: type A stream of the joint caller equals #6912 source caller event for event: %d events, J = HOST2, diagonal and metadata equal' % n)
    cA, cB = Counter(e[1] for e in old['events'] if e[0] == 'A'), Counter(e[1] for e in old['events'] if e[0] == 'B')
    bsc = sorted({e[3] for e in old['events'] if e[0] == 'B' and e[1] == 'SCALE'}); badd = sorted({e[4] for e in old['events'] if e[0] == 'B' and e[1] == 'ADD'}, key=lambda s: abs(L.Q(s)))
    need(any(L.Q(x).denominator != 1 for x in bsc) and len(bsc) > 1, 'type B has non-integer constant gates')
    print('PASS 1b: type B (38 roles, 8 ports, %d events with the 18 contacts) is NOT #6912\'s source: HOST (not HOST2), SCALE values %s, ADD values beyond integers (%s ...); no block transfer, integer elimination does not apply' % (sum(1 for e in old['events'] if e[0] in ('B', 'J')), bsc, badd[-4:]))
    # (2) rewrite
    ch, ent = verify_rewrite(old, new)
    blocks, anchors = L.from_6912(af, 'A')
    a_equal_6912(new, af)
    print('PASS 2a: %d changed A blocks, %d exact 40x40 matrices equal (%d scalar entries); B events, J contacts, LAMBDA/IDLE/QUERY unchanged and in order; metadata, diagonals, ports unchanged; alphabet |ADD|<=2, SCALE -1; new A stream = #6912 caller-after' % (ch, ch, ent))
    pts = L.random_points()
    k = replay_check(old, new, pts)
    print('PASS 2b: full 78x78 caller matrix of old and new identical at %d points (4 central characters q^4=1, where the target holds, + 4 random q, equality only, random D_1..D_18, mod %d); new caller reaches the block-diagonal target (0 bad entries)' % (k, L.PM))
    ev = Counter(e[0] + ':' + str(e[1]) for e in new['events']); eo = Counter(e[0] + ':' + str(e[1]) for e in old['events'])
    need(len(old['events']) - len(new['events']) == 1298 and ev['B:ADD'] == eo['B:ADD'] and all(ev[x] == eo[x] for x in eo if not x.startswith('A:') or x.split(':')[1] not in L.CONST), 'event counts')
    print('PASS 2c: events %d -> %d (A %d -> %d, B %d, J %d); LAMBDA A/B %d/%d unchanged; IDLE_ONE %d/%d, QUERY %d/%d unchanged' % (len(old['events']), len(new['events']), sum(e[0] == 'A' for e in old['events']), sum(e[0] == 'A' for e in new['events']),
          sum(e[0] == 'B' for e in new['events']), sum(e[0] == 'J' for e in new['events']), ev['A:LAMBDA'], ev['B:LAMBDA'], ev['A:IDLE_ONE'], ev['B:IDLE_ONE'], ev['A:QUERY'], ev['B:QUERY']))
    # (4) ordinary-pass side quantities
    for ty in 'A':
        po_, mo = prefix_mass(old, ty); pn_, mn = prefix_mass(new, ty)
        print('INFO 4: type A constant-block max prefix l1 row sum %d -> %d, max entry %d -> %d; log2 prod(1+|a|) over A ADDs %.1f -> %.1f; max |ADD| %d -> %d' % (po_, pn_, mo, mn, height_bits(old, ty), height_bits(new, ty),
              max(abs(int(L.Q(e[4]))) for e in old['events'] if e[0] == 'A' and e[1] == 'ADD'), max(abs(int(L.Q(e[4]))) for e in new['events'] if e[0] == 'A' and e[1] == 'ADD')))
        need(pn_ <= po_ and mn <= mo, 'constant-block mass did not grow')
    cbits = lambda C: (max(abs(L.Q(e[4] if e[1] == 'ADD' else e[3])).numerator.bit_length() for e in C['events'] if e[0] in 'AB' and e[1] in ('ADD', 'SCALE')),
                       max(L.Q(e[4] if e[1] == 'ADD' else e[3]).denominator.bit_length() for e in C['events'] if e[0] in 'AB' and e[1] in ('ADD', 'SCALE')))
    need(cbits(old) == cbits(new) == (9, 8), 'caller coefficient bits (numerator, denominator) 9 / 8 unchanged')
    print('PASS 4a: caller coefficient bits (num, den) = %s old and new (the 256 and 1/128 gates are type B)' % (cbits(new),))
    # invoice and raw per word
    for wp, Sc in words:
        W = json.load(gzip.open(wp, 'rt'))
        To, Po, So, ko = invoice(old, W); Tn, Pn, Sn, kn = invoice(new, W)
        need(To == Tn and Po == Pn and So == Sn and ko == kn, 'invoice changed')
        ro, rn = L.raw_all(old, W, Sc), L.raw_all(new, W, Sc)
        need(ro['literal'] - rn['literal'] == SAVING and all(ro[x] - rn[x] == SAVING for x in ('literal', 'actual', 'upper', 'recharge', 'per_input', 'per_input_recharge')), 'raw saving is the same exact amount in every reading')
        print('PASS 3: %s | events %d public %d | T,P,S=%d kappa=%.13f unchanged' % (os.path.basename(wp), len(W['program']), rn['public'], Sn, kn))
        for key in ('literal', 'actual', 'upper', 'recharge', 'per_input', 'per_input_recharge'):
            print('   raw %-19s %13s -> %13s   (<1e9: %s -> %s)' % (key, format(ro[key], ','), format(rn[key], ','), ro[key] < 10 ** 9, rn[key] < 10 ** 9))
        print('   LAMBDA jobs %d, debit %s; per-input scale %s' % (rn['lambda_jobs'], format(rn['debit'], ','), format(rn['per_in'], ',')))
    print('saving per reading = 32*40*96*(2492-1194) = %s' % format(SAVING, ','))
    # failing controls
    res = controls(old, new, bf)
    for name, rs_, rr_, must in res: print('   control %-58s structural-reject %-5s replay-reject %s' % (name, rs_, rr_))
    need(all(rs_ for _, rs_, _, _ in res) and all(rr_ for _, _, rr_, must in res if must), 'a control was accepted')
    # control for the first claim: a perturbed source must break the identity
    bad = copy.deepcopy(bf); bad['events'][0][3] = '1'
    try: a_equal_6912(old, bad); raise SystemExit('FAIL control: perturbed #6912 source accepted')
    except ValueError: print('   control perturbed #6912 source event: identity rejected')
    print('PASS_CALLER_BLOCKS_JOINT')


if __name__ == '__main__':
    main()
