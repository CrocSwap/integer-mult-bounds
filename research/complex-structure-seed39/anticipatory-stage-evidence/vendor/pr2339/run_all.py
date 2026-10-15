#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the independent word check and the model pricing of the extended T74 borrow words; print one PASS line.

Steps (each child runs as `python3 -I -B`, and its last stdout line must be its PASS line):
  0. (optional, --build) build_ext.py --controls, the construction with its own oracle, PR2269's auditor and
     PR2226 Gaussian products.  Needs numpy on PYTHONPATH (--numpy-site DIR).  The pinned words/ and witness/
     files must come out byte-identical (determinism); otherwise the run fails.
  1. check_ext.py --out: independent check of BORROW-WORD-80{base,extra} (no PR or construction code).
  2. price_ext.py sources, price_ext.py controls: the pricing harness re-reads its PR constants from git and
     runs its positive/negative controls.
  3. price-input-ext80.json is written from the profiles RECOUNTED by check_ext.py (not from the word reports),
     then priced: price_ext.py price price-input-ext80.json --digits 40 --conservative --out
     price_ext.ext80.receipt.json.  Models F (favourable), C (calibrated on PR2269's realized refill),
     C8 (calibrated on the T8 PR2260 refill) and P (pessimistic).  These are MODEL prices of an idle refill
     that has NOT been constructed: not a supplier, not a kappa claim.
  4. Cross-checks here: the priced local profiles equal the recount; every model's composed global profile
     249 P_gauge44 + 417 P_extra + idle has mass m W - D = 4816512; a plain float bisection of
     mu(a) = sum_r n_r (r/m)^(1-a) / W = 1 agrees with each certified b to 1e-12.
  5. Runner negative controls: a price input whose width sum breaks mass = 1856 + widths, and a check_ext
     receipt whose recount differs from the priced profile, must both be rejected.

Credit: PR2226 (Cinna Davis / @1337isnot1337, with OpenAI Codex) anticipatory dirty borrowing; PR2269
(Jeremy Kothe / jeremykothe2) T74 borrow43 words, fill and b; PR2260 (Dugongue) T8 44-high supplier and fill;
PR2312 reference claim only.  Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B run_all.py [--out] [--build --numpy-site DIR]
Final line: PASS_T74_LOW_ALIAS_RUN_ALL ... or FAIL_T74_LOW_ALIAS_RUN_ALL ...
"""

import sys

if sys.flags.optimize:
    sys.stdout.write('refusing to run under python -O\nFAIL_T74_LOW_ALIAS_RUN_ALL\n')
    sys.exit(2)

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PASS_LINE = 'PASS_T74_LOW_ALIAS_RUN_ALL'
FAIL_LINE = 'FAIL_T74_LOW_ALIAS_RUN_ALL'
PRICE_INPUT = 'price-input-ext80.json'
PRICE_RECEIPT = 'price_ext.ext80.receipt.json'
CHECK_RECEIPT = 'check_ext.receipt.json'
PINNED_OUTPUTS = {  # same pins as check_ext.LOCAL_PINS (sha256)
    'words/BORROW-WORD-80base.json.gz': '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493',
    'words/BORROW-WORD-80extra.json.gz': '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5',
    'witness/witness_80_base.json': '9380f74c032b0616d5b13e8ef94b6d9f80cac36239e329357e7d5fcab5283ad0',
    'witness/witness_80_extra.json': '6737072dcca47c6e6526bd62a41585dd09026549550c9e62eb53e64b265a6709',
}
T74 = dict(m=73, W=66304, D=23680, calls={'gauge44': 249, 'extra': 417})


def run(argv, env=None, timeout=1800):
    t0 = time.time()
    got = subprocess.run([sys.executable, '-I', '-B'] + argv, cwd=HERE, capture_output=True, text=True,
                         env=env, timeout=timeout)
    lines = got.stdout.strip().splitlines()
    return got.returncode, lines, got.stderr, round(time.time() - t0, 1)


def sha(path):
    with open(os.path.join(HERE, path), 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def step(name, argv, token, failures, log, env=None):
    rc, lines, err, dt = run(argv, env=env)
    last = lines[-1] if lines else ''
    ok = rc == 0 and last.startswith(token)
    log[name] = dict(argv=argv, rc=rc, last_line=last, seconds=dt)
    print('[%s] %s (rc=%d, %.1f s): %s' % (name, 'PASS' if ok else 'FAIL', rc, dt, last), flush=True)
    if not ok:
        failures.append('%s:%d:%s' % (name, rc, last[:80]))
        for ln in (lines[-15:] + err.strip().splitlines()[-10:]):
            print('    | ' + ln)
    return ok, lines


def float_root(H, m, W):
    """Plain float bisection of mu(a) = sum n_r (r/m)^(1-a) / W = 1 (cross-check only, not certified)."""
    mu = lambda a: sum(n * math.exp((1 - a) * math.log(r / m)) for r, n in H.items()) / W
    lo, hi = 0.0, 0.01
    assert mu(lo) < 1 < mu(hi)
    for _ in range(200):
        mid = (lo + hi) / 2
        if mu(mid) < 1:
            lo = mid
        else:
            hi = mid
    return lo


def crosscheck(pr, recount):
    """Priced profiles == recount; composed global mass == m W - D; float root == certified b (1e-12)."""
    out, bad = [], []
    if pr['local_profiles'] != dict((p, recount[p]['profile']) for p in ('gauge44', 'extra')):
        bad.append('crosscheck:priced profiles != recount')
    total = T74['m'] * T74['W'] - T74['D']
    for row in pr['models']:
        H = {}
        for p, c in T74['calls'].items():
            for r, n in recount[p]['profile'].items():
                H[int(r)] = H.get(int(r), 0) + c * n
        for r, n in row['idle'].items():
            H[int(r)] = H.get(int(r), 0) + n
        mass = sum(r * n for r, n in H.items())
        froot = float_root(H, T74['m'], T74['W'])
        good = mass == total and abs(froot - float(row['b'])) < 1e-12
        out.append(dict(model=row['model'], b=row['b'], b_conservative=row.get('b_conservative'),
                        gain_vs_pr2269=row['gain_vs_pr2269'], gain_vs_pr2269_pct=row['gain_vs_pr2269_pct'],
                        gain_vs_pr2312=row['gain_vs_pr2312'], gain_vs_pr2312_pct=row['gain_vs_pr2312_pct'],
                        idle=row['idle'], global_mass=mass, float_root=repr(froot), crosscheck_ok=good,
                        bit_bound=row['bit_bound']))
        if not good:
            bad.append('crosscheck:%s mass=%d float=%r' % (row['model'], mass, froot))
    return out, bad


FETCH_URL = 'https://github.com/CrocSwap/integer-mult-bounds'
FETCH_PRS = {2269: 'b479fc5567bc09ab9185bffe89b62594f36d74e5', 2226: 'dacaf3d81f1936bb55b8454b1244e5d014272754',
             2260: 'fde6b107e26a14da5bac5b66913c914708ea6901'}


def fetch_missing():
    repo = os.path.dirname(os.path.dirname(HERE))
    for pr, commit in sorted(FETCH_PRS.items()):
        have = subprocess.run(['git', '-C', repo, 'cat-file', '-t', commit], capture_output=True, text=True)
        if have.returncode == 0 and have.stdout.strip() == 'commit':
            continue
        print('fetching refs/pull/%d/head (commit %s absent)' % (pr, commit[:8]), flush=True)
        got = subprocess.run(['git', '-C', repo, 'fetch', '--no-tags', '--quiet', FETCH_URL, 'refs/pull/%d/head' % pr],
                             capture_output=True, text=True)
        if got.returncode != 0:
            print('fetch of #%d failed: %s' % (pr, got.stderr.strip()))


def main():
    ap = argparse.ArgumentParser(description='Run check_ext.py and the model pricing; print one PASS line')
    ap.add_argument('--out', action='store_true', help='write run_all.receipt.json next to this script')
    ap.add_argument('--build', action='store_true', help='first re-run build_ext.py --controls (needs numpy)')
    ap.add_argument('--numpy-site', default=None, help='directory to put on PYTHONPATH for build_ext.py')
    ap.add_argument('--fetch', action='store_true',
                    help='fetch refs/pull/{2269,2226,2260}/head from %s if their pinned commits are absent '
                         '(every input blob is still verified against its pin)' % FETCH_URL)
    args = ap.parse_args()
    if args.fetch:
        fetch_missing()
    t0 = time.time()
    failures, log = [], {}
    summary = {}
    try:
        if args.build:
            before = dict((p, sha(p)) for p in PINNED_OUTPUTS)
            env = dict(os.environ)
            if args.numpy_site:
                env['PYTHONPATH'] = args.numpy_site
            # build_ext.py imports replay_core/vendor modules from its own directory, so it is run without -I
            t1 = time.time()
            got = subprocess.run([sys.executable, '-B', 'build_ext.py', '--controls'], cwd=HERE, capture_output=True,
                                 text=True, env=env, timeout=3600)
            lines = got.stdout.strip().splitlines()
            ok = got.returncode == 0 and any('PASS_T74_LOW_ALIAS_EXTENSION' in ln for ln in lines[-5:])
            after = dict((p, sha(p)) for p in PINNED_OUTPUTS)
            same = after == before == PINNED_OUTPUTS
            log['build'] = dict(rc=got.returncode, last_line=lines[-1] if lines else '', deterministic=same,
                                seconds=round(time.time() - t1, 1))
            print('[build] %s (rc=%d): outputs byte-identical to pins: %s' % ('PASS' if ok else 'FAIL', got.returncode,
                                                                              same), flush=True)
            if not (ok and same):
                failures.append('build:%d:deterministic=%s' % (got.returncode, same))
        else:
            mism = [p for p in PINNED_OUTPUTS if sha(p) != PINNED_OUTPUTS[p]]
            if mism:
                failures.append('pins:%s' % ','.join(mism))
        ok1, _ = step('check_ext', ['check_ext.py', '--out'], 'PASS_T74_LOW_ALIAS_WORDS_INDEPENDENT', failures, log)
        ok2, _ = step('price_sources', ['price_ext.py', 'sources'], 'PASS_T74_EXT_PRICE_HARNESS', failures, log)
        ok3, _ = step('price_controls', ['price_ext.py', 'controls'], 'PASS_T74_EXT_PRICE_HARNESS', failures, log)
        if ok1:
            with open(os.path.join(HERE, CHECK_RECEIPT)) as fh:
                rec = json.load(fh)
            recount = rec['recounted']
            spec = {'family': 'T74',
                    'label': 'CONSTRUCTED BORROW-WORD-80{base,extra} (48 high + 32 low aliases); local profiles recounted '
                             'by check_ext.py; idle refill MODELLED (owner fill not rebuilt)',
                    'providers': dict((p, dict(profile=recount[p]['profile'], helpers=recount[p]['helpers'],
                                               helper_width_sum=recount[p]['helper_width_sum'])) for p in ('gauge44', 'extra'))}
            with open(os.path.join(HERE, PRICE_INPUT), 'w') as fh:
                json.dump(spec, fh, indent=1, sort_keys=True)
                fh.write('\n')
            ok4, lines = step('price_ext80', ['price_ext.py', 'price', PRICE_INPUT, '--digits', '40', '--conservative',
                                              '--out', PRICE_RECEIPT],
                              'PASS_T74_EXT_PRICE_HARNESS', failures, log)
            if ok4:
                for ln in lines:
                    if ln.startswith('  ') and ('b_40' in ln or 'idle mass' in ln or 'x249' in ln or 'x417' in ln):
                        print(ln)
                with open(os.path.join(HERE, PRICE_RECEIPT)) as fh:
                    pr = json.load(fh)['price']
                xc, bad_xc = crosscheck(pr, recount)
                failures.extend(bad_xc)
                summary = dict(extra_freed_mass=pr['extra_freed_mass'], idle_mass=pr['idle_mass'], models=xc)
                print('[crosscheck] %s: priced profiles = recount; global mass = %d for every model; float roots agree '
                      'with certified b to 1e-12' % ('FAIL' if bad_xc else 'PASS', T74['m'] * T74['W'] - T74['D']),
                      flush=True)
            # runner negative controls
            nc = []
            with tempfile.TemporaryDirectory() as td:
                bad = json.loads(json.dumps(spec))
                bad['providers']['extra']['helper_width_sum'] += 1
                path = os.path.join(td, 'bad.json')
                with open(path, 'w') as fh:
                    json.dump(bad, fh)
                rc, lines, _, _ = run(['price_ext.py', 'price', path, '--digits', '12'])
                nc.append(dict(control='price input with helper_width_sum + 1 (breaks mass = 1856 + widths)',
                               rejected=rc != 0 and lines[-1].startswith('FAIL') and
                               any('local.identity' in ln for ln in lines)))
            if ok4:
                moved = json.loads(json.dumps(recount))
                moved['gauge44']['profile']['1'] -= 1
                moved['gauge44']['profile']['2'] += 1
                _, bad_xc = crosscheck(pr, moved)
                nc.append(dict(control='crosscheck with a recount that moves one rank-1 child to rank 2',
                               rejected=bool(bad_xc), by=bad_xc[:2]))
            for c in nc:
                print('[runner control] %-80s %s' % (c['control'], 'REJECTED-OK' if c['rejected'] else 'NOT-OK'))
                if not c['rejected']:
                    failures.append('runner_control:%s' % c['control'][:40])
            log['runner_controls'] = nc
    except Exception as e:  # noqa: BLE001 - report any runner error as a failure line
        failures.append('runner:%s' % e)
    elapsed = round(time.time() - t0, 1)
    if failures:
        line = '%s failures=%s' % (FAIL_LINE, ';'.join(failures))
    else:
        models = ','.join('%s:%s' % (x['model'], x['b'][:14]) for x in summary['models'])
        line = '%s check=PASS price=PASS crosscheck=PASS runner_controls=%d E=%d b_40[%s]' % (
            PASS_LINE, len(log['runner_controls']), summary['extra_freed_mass'], models)
    if args.out:
        with open(os.path.join(HERE, 'run_all.receipt.json'), 'w') as fh:
            json.dump(dict(runner='run_all.py', python=sys.version.split()[0], steps=log, pricing=summary,
                           note='Model prices of a modelled idle refill; no owner fill was rebuilt; no kappa claim.',
                           elapsed_s=elapsed, result=line), fh, indent=1, sort_keys=True)
            fh.write('\n')
    print('elapsed %.1f s' % elapsed)
    print(line)
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
