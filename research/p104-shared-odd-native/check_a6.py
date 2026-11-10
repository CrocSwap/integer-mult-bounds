#!/usr/bin/env python3
"""A6 check for a later package: owned rises at f = 1, and tensor width 2 (joint execution of the stored recipes).
python3 -I -B check_a6.py WORD.json.gz COMPILER_DIR PRIMES [--exh] [--ranks-width2 N]
  WORD.json.gz  the native word; COMPILER_DIR holds the retained clifford_exact.py (lower_child); PRIMES e.g. 2,3,5 (dyadic: 2)
Standard library only (plus a6lib.py next to this file).  Ends PASS_A6_CHECK or exits 1.

Part 1 (the argument of CubeJerry #6914; code of this package): scan every owned lifetime; list the owned rises and their rank histogram;
 for each distinct rise chart pair, all 512 exact Gaussian columns of T_b T_a^-1 (a dense frame formula, no recipe) against
 right monomial, F_r, left monomial (the recipe stored by the retained compiler); adapter record lists (S, CZ, XROW, NOT, I) at
 f = 1 (all 512 addresses) and f = 2, 3 (random addresses with spectators).
Part 2 (the argument of unpaidmoon #6930; code of this package): joint execution on TWO columns of the stored recipes of the rise charts
 (and of the first rank-1 MOVE of the word), faithful global phase i^(p f) against the exact tensor product (M|x>)(x)(M|y>);
 --exh runs all 512 x 512 input pairs on the first rank-1 MOVE, otherwise a stated sample.  The copied width-1 integer
 i^p must fail whenever the total stored phase is not 0 mod 4; an off-by-one phase and a flipped Fourier sign must fail always.
Failing controls: wrong phase, omitted CLEAR, public/owned alias, rank-zero MOVE, uncorrected adjoint child, global phase not
multiplied by f (records and joint run), wrong source frame.
"""
import sys, copy, random, importlib.util, time, hashlib
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a6lib import *

args = [a for a in sys.argv[1:] if not a.startswith('--')]
EXH = '--exh' in sys.argv
word_path, comp_dir, primes = args[0], args[1], tuple(int(p) for p in args[2].split(','))


def fail(msg):
    print('FAIL_A6_CHECK:', msg, file=sys.stderr)
    raise SystemExit(1)


def chk(ok, msg):
    if not ok:
        fail(msg)
    print('PASS', msg, flush=True)


spec = importlib.util.spec_from_file_location('retained_clifford', Path(comp_dir) / 'clifford_exact.py')
C = importlib.util.module_from_spec(spec)
sys.modules['retained_clifford'] = C
spec.loader.exec_module(C)

w = load_word(word_path)
print('word sha256', hashlib.sha256(Path(word_path).read_bytes()).hexdigest()[:16], flush=True)
rises, lives, cen = scan(w, primes, descending_only=True)
print('census', {k: v for k, v in cen.items() if k != 'strict_rejected'})
chk(cen['strict_rejected'] == [x['event'] for x in rises] and len(rises) > 0,
    '%d owned rises, rank histogram %s, mass %d; the descending-only rule rejects exactly these events' % (len(rises), cen['rise_hist'], cen['rise_mass']))

cache = {}


def chart(i):
    if i not in cache:
        cache[i] = C.canonical_frame(9, tuple(w['frames'][i]))
    return cache[i]


def lower(a, b):
    rec, _ = C.lower_child(chart(a).adjoint().then(chart(b)))
    return rec


maps = {}
for x in rises:
    k = (x['start'], x['end'])
    if k not in maps:
        maps[k] = lower(*k)
        chk(maps[k]['rank'] == x['rank'], 'rise %d->%d: one child of rank %d = frame dimension difference' % (k + (x['rank'],)))


def dense_bad(k, rec, sign=1, shift=0, src=None):
    a, b = k
    circ = chart_change(w['frames'], a if src is None else src, b)
    rc = copy.deepcopy(rec)
    rc['left']['phase'] = (rc['left']['phase'] + shift) % 4
    rcirc = recipe_circuit(rc, 1, 'faithful', sign=sign)
    return sum(run(circ, x) != run(rcirc, x) for x in range(SIZE))


bad = sum(dense_bad(k, r) for k, r in maps.items())
chk(bad == 0, 'f = 1: %d distinct rise maps x 512 exact Gaussian columns equal the stored two-adapter factorisation' % len(maps))

tot = pairmax = 0
for k, rec in maps.items():
    L, R = record_list(rec['left']), record_list(rec['right'])
    chk_len = len(L) <= 171 and len(R) <= 171 and len(L) + len(R) <= 342
    if not chk_len:
        fail('record bound at %s' % (k,))
    tot += len(L) + len(R)
    pairmax = max(pairmax, len(L) + len(R))
    for side, rl in (('left', L), ('right', R)):
        m = rec[side]
        fwd, ph = monomial_tables(m)
        for x in range(SIZE):
            if record_action(rl, x, 1) != (fwd[x], (ph[x] + m['phase']) % 4):
                fail('record action f=1 at %s' % (k,))
        rng = random.Random(k[0] * 7919 + k[1])
        for f in (2, 3):
            for _ in range(32):
                xs = [rng.randrange(SIZE) for _ in range(f)]
                sp = rng.randrange(1 << 11) << (9 * f)
                addr = sum(v << (9 * c) for c, v in enumerate(xs)) | sp
                want = (sp | sum(fwd[v] << (9 * c) for c, v in enumerate(xs)), (sum(ph[v] for v in xs) + f * m['phase']) % 4)
                if record_action(rl, addr, f) != want:
                    fail('record action width %d at %s' % (f, k))
chk(True, 'adapter records: %d in all (largest pair %d), allowance 1000 per rise = %d; exact at f = 1 (all addresses), f = 2, 3 (sampled, spectators)' % (tot, pairmax, 1000 * len(rises)))


# ---------------------------------------------------------------- width 2
def joint_bad(k_or_chart, rec, pairs, modes, src=None):
    a, b = k_or_chart
    circ = chart_change(w['frames'], a if src is None else src, b)
    cols = {}
    out = {m: 0 for m in modes}
    circs = {m: (recipe_circuit(rec, 2, 'faithful', sign=-1) if m == 'signflip' else recipe_circuit(rec, 2, m)) for m in modes}
    for x, y in pairs:
        for z in (x, y):
            if z not in cols:
                cols[z] = run(circ, z)
        want = outer(cols[x], cols[y])
        for m, c in circs.items():
            if run(c, x | (y << 9), 2) != want:
                out[m] += 1
    return out


def ptot(rec):
    return (rec['left']['phase'] + (rec['right']['phase'] if rec['right'] else 0)) % 4


rng = random.Random(6930)
cols = [0, 511] + [1 << i for i in range(9)] + [rng.randrange(SIZE) for _ in range(13)]
sample = [(x, y) for x in cols for y in cols]
copied_fail_expected = copied_fail_seen = 0
for k, rec in sorted(maps.items()):
    r = rec['rank']
    prs = sample if r <= 3 else rng.sample(sample, 64 if r <= 5 else 8)
    modes = ('faithful', 'copied', 'offby', 'signflip')
    res = joint_bad(k, rec, prs, modes)
    if res['faithful'] or res['offby'] != len(prs) or res['signflip'] != len(prs):
        fail('width 2 at rise map %s rank %d: %s of %d pairs' % (k, r, res, len(prs)))
    if ptot(rec):
        copied_fail_expected += 1
        copied_fail_seen += res['copied'] == len(prs)
    elif res['copied']:
        fail('copied phase failed with total phase 0 at %s' % (k,))
chk(copied_fail_seen == copied_fail_expected,
    'width 2, %d rise maps, sampled pairs: faithful i^(p f) = tensor product on every pair; copied integer fails on all pairs of the %d maps with total phase != 0 (and passes the %d with 0); off-by-one and flipped Fourier fail on all pairs' % (len(maps), copied_fail_expected, len(maps) - copied_fail_expected))

first = next(i for i, e in enumerate(w['program']) if e[0] == 'MOVE' and abs(len(w['frames'][e[2]]) - len(w['frames'][e[3]])) == 1)
ev = w['program'][first]
rec1 = lower(ev[2], ev[3])
print('first rank-1 MOVE: event %d %s, stored phases left %d right %d' % (first, ev, rec1['left']['phase'], rec1['right']['phase']))
allp = [(x, y) for x in range(SIZE) for y in range(SIZE)] if EXH else rng.sample([(x, y) for x in range(SIZE) for y in range(SIZE)], 4096)
res = joint_bad((ev[2], ev[3]), rec1, allp, ('faithful', 'copied', 'offby'))
chk(res['faithful'] == 0 and res['offby'] == len(allp) and (res['copied'] == len(allp) if ptot(rec1) else res['copied'] == 0),
    'first rank-1 MOVE (event %d): %d input pairs, faithful bad %d, copied-integer bad %d (total phase %d), off-by-one bad %d' % (first, len(allp), res['faithful'], res['copied'], ptot(rec1), res['offby']))
# width 1 cannot see the difference
c1 = chart_change(w['frames'], ev[2], ev[3])
b1 = sum(run(recipe_circuit(rec1, 1, 'copied'), x) != run(c1, x) for x in range(SIZE))
chk(b1 == 0, 'control: at f = 1 the copied integer is the faithful one, so a width-1 check cannot distinguish the readings')

# ---------------------------------------------------------------- failing controls (each must be rejected)
k0, r0 = sorted(maps.items())[0]
need_rej = {
    'wrong_phase_+1': dense_bad(k0, r0, shift=1) > 0,
    'wrong_phase_+2': dense_bad(k0, r0, shift=2) > 0,
    'uncorrected_adjoint_child': dense_bad(k0, r0, sign=-1) > 0,
    'wrong_source_frame': dense_bad(k0, r0, src=next(i for i in range(len(w['frames'])) if i != k0[0] and len(w['frames'][i]) == len(w['frames'][k0[0]]) and span(w['frames'][i]) != span(w['frames'][k0[0]]))) > 0,
}


def rejects(mut):
    m = copy.deepcopy(w)
    mut(m)
    try:
        scan(m, primes)
    except ValueError:
        return True
    return False


b0 = next(j for j, e in enumerate(w['program']) if e[0] == 'INIT')
need_rej['public_alias'] = rejects(lambda m: m['program'][b0].__setitem__(1, 0))
need_rej['omitted_clear'] = rejects(lambda m: m['program'].pop(next(j for j, e in enumerate(m['program']) if e[0] == 'CLEAR')))
need_rej['rank_zero_move'] = rejects(lambda m: m['program'][rises[0]['event']].__setitem__(3, rises[0]['start']))
mf = False
for k, rec in maps.items():
    for side in ('left', 'right'):
        mo = rec[side]
        if mo['phase'] % 4:
            rl = record_list(mo)
            fwd, ph = monomial_tables(mo)
            if record_action(rl, 5 | (7 << 9), 2, ipf=False) != (fwd[5] | (fwd[7] << 9), (ph[5] + ph[7] + 2 * mo['phase']) % 4):
                mf = True
need_rej['records_global_phase_not_times_f'] = mf
chk(all(need_rej.values()), 'failing controls all rejected: %s' % need_rej)
print('PASS_A6_CHECK')
