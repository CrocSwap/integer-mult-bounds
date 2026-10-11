"""Value of a pivot: the same R715 word with k of the 112 selected kernel pivots (evenly spread over the file order, donors kept only where used),
each priced through the full local chain (kernel build, target mixing, PR #443 cohort legality profile) and the exact whole-residual hosting
re-solve (hosting_model.py, CP-SAT) with the exact two-engine endpoint.  k = 0 is infeasible: the width-8 slots of the 240 copies cannot hold
the 7,865 residuals of the eleven stages, so narrow residuals are required, not just helpful.
needs: ortools; the C++ cohort legality binary of PR #443's parent run (parent/bin/legality).
usage: scan_pivots.py REPO_RESEARCH_DIR LEGALITY_BIN WORKDIR OUT.json [k ...]
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
import sys, os, json, subprocess
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kernel_cap as KC, hosting_model as HM
R, LEG, work, out = sys.argv[1:5]; ks = [int(x) for x in sys.argv[5:]] or [0, 56, 70, 84, 98, 112]
ROOT = os.path.dirname(HERE); SIB = R + '/e8-r715-eleven-stage-whole'; BITC = R + '/e8-r740-replica32/parent436/code/bit'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0')
def run(c):
    r = subprocess.run([str(x) for x in c], env=env, capture_output=True, text=True); assert r.returncode == 0, (c[:3], r.stderr[-500:]); return r.stdout
def local_profile(U, kw, d):
    os.makedirs(d + '/cout', exist_ok=True); U.save_word(kw, d + '/kernel.json.gz')
    run([sys.executable, '-B', SIB + '/code/mix_target.py', d + '/kernel.json.gz', d + '/word-mixed.json'])
    run([sys.executable, '-B', BITC + '/export_records.py', d + '/word-mixed.json', d + '/records'])
    run([sys.executable, '-B', BITC + '/regression/stage_cohort.py', d + '/records', d + '/records', d + '/cin', d + '/cout'])
    run([LEG, d + '/cin', d + '/cout', d + '/cout/legality.json'])
    return {int(r): z for r, z in json.load(open(d + '/cout/legality.json'))['paid_histogram']}
U = KC.setup(R); w, ret, mv = KC.primitive_retimed(U, SIB + '/data/word-r715.json.gz'); G = KC.Geo(U, ret)
full = json.load(open(ROOT + '/data/kernel-selection.json')); rows = []
cases = [('R715 greedy kernel (PR #443 search, 84 mixed-rank pivots)', json.load(open(SIB + '/data/kernel-selection.json'))['entries'])]
for k in ks: cases.append(('%d rank-1 pivots' % k, ([full[(j * len(full)) // k] for j in range(k)] if k < len(full) else full) if k else []))
for name, sel in cases:
    chk = KC.check_selection(G, sel); kw, iso, info = KC.build_kernel(U, ret, sel)
    wd = KC.width_rule_check(U, kw, sel); loc = local_profile(U, kw, work + '/scan_%d_%d' % (len(sel), chk['entrance_rank']))
    row = dict(case=name, pivots=len(sel), entrance_rank=chk['entrance_rank'], widths=wd, local_profile={str(r): z for r, z in sorted(loc.items())})
    try:
        res = HM.solve(loc, {int(a): b for a, b in wd.items()}, tl=120); c, W = HM.price(R, res)
        row.update(status=res['status'], c='%d/%d' % (c.numerator, c.denominator), c_decimal=float(c), remainder={str(a): b for a, b in sorted(res['remainder'].items())})
    except AssertionError as e:
        row.update(status='INFEASIBLE', c=None)
    rows.append(row); print(json.dumps(row), flush=True)
base = next(r for r in rows if r['case'].startswith('R715 greedy'))
for r in rows:
    r['gain_over_r715_percent'] = None if r['c'] is None else float((Q(r['c']) / Q(base['c']) - 1) * 100)
json.dump(rows, open(out, 'w'), indent=1)
