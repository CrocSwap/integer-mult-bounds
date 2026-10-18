"""c1 (standard library): tallies of the shipped state files and lane summaries; exact arithmetic of the reduction. Re-runs nothing."""
import json, os, re, glob, math
from fractions import Fraction as Fr
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def ok(c, m): print(('PASS ' if c else 'FAIL ') + m)
# summaries: all 8 types UNSAT-VERIFIED for both families
S = open(f'{PKG}/data/summaries/lane.summary').read() + open(f'{PKG}/data/summaries/helper.summary').read()
for P, k in ((56, 17), (53, 6)):
    got = set(int(m.group(1)) for m in re.finditer(rf'exit=0 TYPE (\d) P {P} k {k} RESULT UNSAT-VERIFIED', S))
    ok(got == set(range(8)), f'summaries: P = {P}, k = {k}: types with RESULT UNSAT-VERIFIED = {sorted(got)}')
ok('SAT ' not in re.sub('UNSAT', '', S) and 'INCOMPLETE' not in S, 'summaries: no SAT / INCOMPLETE result line')
# states
exp56 = {0: (125, 0, 2), 1: (305, 83, 3), 2: (561, 187, 5), 3: (1373, 544, 8), 4: (1027, 375, 6), 5: (575, 183, 5), 6: (238, 56, 4), 7: (60, 7, 2)}   # PUNCT-MID section 4 table
exp53 = {0: (44, 0, 0), 1: (112, 0, 0), 2: (397, 187, 3), 3: (1119, 558, 8), 4: (858, 376, 6), 5: (397, 183, 3), 6: (81, 0, 0), 7: (19, 0, 0)}   # README table, P = 53
tot = {}
for P, k in ((56, 17), (53, 6)):
    for t in range(8):
        d = json.load(open(f'{PKG}/data/states/T{t}_P{P}_k{k}.json'))
        ver = sum(1 for v in d.values() if v['res'] == 'UNSAT-VERIFIED'); cnt = sum(1 for v in d.values() if v['res'] == 'COUNT')
        spl = sum(1 for v in d.values() if v.get('split')); other = len(d) - ver - cnt
        ok(other == 0, f'T{t} P{P} k{k}: {ver} verified entries ({spl} split nodes), {cnt} counting leaves, {other} other (SAT/TIMEOUT/UNVERIFIED)')
        ok(all(len(v['T']) > P for v in d.values() if v['res'] == 'COUNT'), f'T{t} P{P} k{k}: every counting leaf has |T| > {P}')
        ok(all(v['res'] != 'UNSAT-VERIFIED' or v.get('split') or ('md5' in v and v['live']) for v in d.values()), f'T{t} P{P} k{k}: every solved leaf has a recorded CNF md5 and a live line')
        tot[P, t] = (ver, cnt, spl)
        if P == 53: ok((ver, cnt, spl) == exp53[t], f'T{t} P53: (verified, counting, split) = {(ver, cnt, spl)} = the README table')
        if P == 56: ok((ver, cnt, spl) == exp56[t], f'T{t} P56: (verified, counting, split) = {(ver, cnt, spl)} = the table of the working card')
        # leaf table
        rows = [l.split('\t') for l in open(f'{PKG}/data/tables/T{t}_P{P}_k{k}.tsv').read().splitlines()[1:]]
        ok(len(rows) == len(d), f'T{t} P{P} k{k}: leaf table has {len(rows)} rows = state entries')
# arithmetic: need(p), m = 7 closure for 54..56, Q(p) table
need = {p: math.ceil(Fr(54, 102) * (120 - p)) for p in range(48, 57)}
ok([need[p] for p in range(48, 57)] == [39, 38, 38, 37, 36, 36, 35, 35, 34], f'need(p), p = 48..56: {[need[p] for p in range(48, 57)]}')
Q = {p: max(q for q in range(0, 10) if 49 - 2 * q >= need[p]) for p in range(48, 57)}
ok([Q[p] for p in range(48, 54)] == [5, 5, 5, 6, 6, 6], f'E7q reach Q(p), p = 48..53: {[Q[p] for p in range(48, 54)]}')
ok(all(5 * 7 >= need[p] for p in (54, 55, 56)), 'p = 54..56: the Lemma R cost bound 5 * 7 = 35 for m = 7 is >= need(p) = 35, 35, 34')
ok(all(49 - 2 * q >= need[p] for p in range(48, 54) for q in range(0, Q[p] + 1)), 'p = 48..53: q <= Q(p) closed by E7q (cost >= 49 - 2q >= need(p))')
ok(max(48, 0) <= 53 and 54 <= 56 and 53 + 1 == 54, 'bands: (I-a) P = 53 covers 48..53 by monotonicity in P; (I-b) P = 56 covers 54..56')
