# SPDX-License-Identifier: Apache-2.0
"""accx.py + fastreplay.py, lossless.py, nativeplan.py: positive and negative controls (standard library only)."""
import copy
import random
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ok, check_data, base_word, word_7601, caller_path, KAPPA_7601  # noqa: E402
import accx  # noqa: E402
import fastreplay  # noqa: E402
import lossless  # noqa: E402
import nativeplan  # noqa: E402
import validate  # noqa: E402
import contextlib, gzip, io, json, tempfile  # noqa: E402,E401

check_data()
B = base_word(); W1 = word_7601(B)
quiet = []

# ---------------------------------------------------------------- accx
t = time.time(); r = accx.check(B, B, caller_path(), out=quiet.append, price=False)
ok(r['ok'] and 'ALL CHECKS PASS' in quiet, 'accx: #7546 vs itself ALL CHECKS PASS (%.1fs for the replay checks)' % (time.time() - t))
quiet.clear(); r = accx.check(B, W1, caller_path(), out=quiet.append)
ok(r['ok'] and str(r['kappa_new']['lo']).startswith(KAPPA_7601) and any(l.endswith('GAIN') for l in quiet),
   'accx: #7601 word vs #7546 ALL CHECKS PASS, kappa %s, GAIN' % KAPPA_7601)
bad = copy.deepcopy(B)
for i, e in enumerate(bad['program']):
    if i > 30000 and e[0] == 'ADD' and e[3] == '1':
        e[3] = '2'; break
quiet.clear()
try:
    accx.check(B, bad, caller_path(), out=quiet.append, price=False); failed = False
except accx.Fail:
    failed = True
ok(failed and any('row differs: YES' in l for l in quiet), 'accx NEG: one corrupted ADD coefficient (event %d) FAILS, exact re-check confirms' % i)
bad2 = copy.deepcopy(B)
j = next(k for k, e in enumerate(bad2['program']) if e[0] == 'MOVE' and not e[4] and k > 1000)
bad2['program'][j] = list(bad2['program'][j]); bad2['program'][j][2], bad2['program'][j][3] = bad2['program'][j][3], bad2['program'][j][2]
quiet.clear()
try:
    accx.check(B, bad2, caller_path(), out=quiet.append, price=False); failed = False
except accx.Fail:
    failed = True
ok(failed, 'accx NEG: one reversed public MOVE FAILS (replay frame check)')
F = fastreplay.FastReplay(B)
ok(F.ok and fastreplay.exact_rows(B, [5])[5] == {5: Q(1)}, 'fastreplay: #7546 replays clean; exact backward slice of helper 5 is its identity row')

# ---------------------------------------------------------------- validate (accx + lossless + the repository's invoice tools)
with tempfile.TemporaryDirectory() as d:
    for name, Wx, want in (('#7601', W1, 0), ('corrupted', bad, 1)):
        pth = Path(d) / 'w.json.gz'
        with gzip.open(pth, 'wt') as fh:
            json.dump(Wx, fh)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = validate.main([str(Path(__file__).resolve().parents[1] / 'data' / 'base-7546-word.json.gz'), str(pth)])
        txt = buf.getvalue()
        if want == 0:
            ok(rc == 0 and 'official   PASS' in txt and 'uniformly_better' in txt and 'crossing in (0.0036490213053, 0.0036490213054)' in txt,
               'validate: #7601 word OVERALL PASS; repository tools: uniformly_better, crossing in (0.0036490213053, 0.0036490213054)')
        else:
            ok(rc == 1 and 'accx       FAIL' in txt, 'validate NEG: corrupted word OVERALL FAIL (accx)')

# ---------------------------------------------------------------- lossless (law DUAL)
for name, Wx in (('#7546', B), ('#7601', W1)):
    loss, lam, occ = lossless.dual_scan(Wx)
    ok(not loss and not lam, 'lossless: %s has 0 lossy CLEARs and no relation left at the end' % name)
# negative: delete owned->public write-backs until a CLEAR becomes lossy
n = B['public']; wb = [k for k, e in enumerate(B['program']) if e[0] == 'ADD' and e[1] < n and e[2] >= n]
rng = random.Random(3); hit = None
for k in rng.sample(wb, 40):
    Wd = copy.deepcopy(B); del Wd['program'][k]
    loss = lossless.dual_scan(Wd)[0]
    if loss:
        hit = (k, loss); break
ok(hit is not None, 'lossless NEG: deleting the owned->public write-back at event %d makes %d CLEAR(s) lossy' % (hit[0], len(hit[1])))


def exact_scan(prog, n):
    """reference: Fraction state replay; a CLEAR of o is lossless iff row(o) is in the span of the other live rows."""
    rows = {r: {r: Q(1)} for r in range(n)}; out = []

    def rank(vs):
        piv = {}; rk = 0
        for v in vs:
            x = dict(v)
            while x:
                p = min(x)
                if p not in piv:
                    break
                c = x[p]
                for kk, y in piv[p].items():
                    nv = x.get(kk, 0) - c * y
                    if nv:
                        x[kk] = nv
                    else:
                        x.pop(kk, None)
            if x:
                p = min(x); c = x[p]; piv[p] = {kk: y / c for kk, y in x.items()}; rk += 1
        return rk
    for t_, e in enumerate(prog):
        if e[0] == 'INIT':
            rows[e[1]] = {}
        elif e[0] == 'CLEAR':
            o = e[1]; others = [v for r_, v in rows.items() if r_ != o]
            if rank(others) < rank(others + [rows[o]]):
                out.append(t_)
            del rows[o]
        elif e[0] == 'SCALE':
            rows[e[1]] = {kk: v * Q(e[2]) for kk, v in rows[e[1]].items()}
        else:
            R = rows[e[1]]
            for kk, v in list(rows[e[2]].items()):
                nv = R.get(kk, 0) + Q(e[3]) * v
                if nv:
                    R[kk] = nv
                else:
                    R.pop(kk, None)
    return out


rng = random.Random(11); agree = 0; nloss = 0; trials = 400
for _ in range(trials):
    n_, no = rng.randint(2, 4), rng.randint(1, 3); prog = []; live = []
    for _ in range(rng.randint(6, 24)):
        c = rng.random()
        free = [o for o in range(n_, n_ + no) if o not in live]
        if c < 0.15 and free:
            o = rng.choice(free); live.append(o); prog.append(['INIT', o, 0])
        elif c < 0.27 and live:
            o = rng.choice(live); live.remove(o); prog.append(['CLEAR', o, 0])
        elif c < 0.42 and live:      # park a public row in an owned register: o += a; a -= o
            o = rng.choice(live); a = rng.randrange(n_); prog += [['ADD', o, a, '1', 0], ['ADD', a, o, '-1', 0]]
        elif c < 0.52 and live:      # write back
            o = rng.choice(live); a = rng.randrange(n_); prog.append(['ADD', a, o, '1', 0])
        else:
            regs = list(range(n_)) + live; a, b = rng.choice(regs), rng.choice(regs)
            if a == b:
                prog.append(['SCALE', a, rng.choice(['2', '-1', '1/2']), 0])
            else:
                prog.append(['ADD', a, b, rng.choice(['1', '-1', '2', '1/2', '-3']), 0])
    for o in live:
        prog.append(['CLEAR', o, 0])
    Wt = dict(public=n_, owned_fields=no, program=prog)
    got = [t_ for t_, o, _ in lossless.dual_scan(Wt)[0]]; ref = exact_scan(prog, n_)
    agree += got == ref; nloss += bool(ref)
ok(agree == trials and 0 < nloss < trials, 'lossless: law DUAL agrees with exact Fraction ranks on %d/%d random programs (%d with a lossy CLEAR)'
   % (agree, trials, nloss))

# ---------------------------------------------------------------- nativeplan
plan = nativeplan.extract_plan(str(Path(__file__).resolve().parents[1] / 'data' / 'base-7546-word.json.gz'), log=lambda *a: None)
s = nativeplan.summary(plan)
ok(round(s['recost'], 6) == 9975.447669 and abs(nativeplan.recost_from_stays(plan) - s['recost']) < 1e-9,
   'nativeplan: #7546 helper layer re-costs to 9,975.447669 from routes alone (= from stays)')
ok(s['helpers'] == 1101 and s['stops'] == 3427 and s['basis_rank'] == 253 and s['blocks'] == 2682 and s['meetings'] == 36299,
   'nativeplan: 1,101 helpers, 3,427 interior stops, 2,682 requirement blocks, 36,299 meetings, state basis rank 253')
path = plan['word']
okr, m = nativeplan.reemit_check(plan, path)
ok(okr and m == 70714, 'nativeplan: all 70,714 helper-touching events re-emitted identically from the plan')
plan['events'][100]['q'] = '7'
okr2, _ = nativeplan.reemit_check(plan, path)
ok(not okr2, 'nativeplan NEG: one tampered plan coefficient breaks the re-emission check')
print('PASS_TOOLKIT_CHECKERS')
