"""Run every check of research/format-limits, a few at a time, and print PASS/FAIL per claim in a fixed order.

usage: run_all.py OUTPUT_DIR [JOBS]
Each check script runs in its own process with its output in OUTPUT_DIR/logs/<script>.log.  The run fails (exit 1) if
any script exits non-zero or prints a FAIL line.  OUTPUT_DIR/RECEIPT.json records per-script status, claim counts and
wall times, the Python version and the sha256 of MANIFEST.sha256.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parent
CHECKS = [  # (section, script)
    ('A', 'a1_ceiling_roots.py'), ('A', 'a2_ceiling_sup.py'), ('A', 'a3_axioms.py'), ('A', 'a4_gap.py'),
    ('A', 'a5_scope_multipliers.py'),
    ('B', 'b_census_anchors.py'),
    ('C', 'c1_sandwich_toy.py'), ('C', 'c2_port_gauge.py'), ('C', 'c3_complement_gate0.py'),
    ('C', 'c3_complement_taint.py'), ('C', 'c4_quotient.py'), ('C', 'c5_lambda.py'), ('C', 'c6_asym.py'),
    ('C', 'c7_descent_toy.py'), ('C', 'c7_descent_price.py'),
    ('D', 'd1_cover_numbers.py'), ('D', 'd2_coupled_count.py'), ('D', 'd3_carrier_ledger.py'),
    ('E', 'e1_run_census.py'), ('E', 'e2_helper_prices.py'),
]


def run(script, logdir):
    t = time.time()
    p = subprocess.run([sys.executable, '-B', str(HERE / script)], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    out = p.stdout + (('\n[stderr]\n' + p.stderr) if p.stderr.strip() else '')
    (logdir / (script + '.log')).write_text(out)
    return script, p.returncode, out, time.time() - t


def main():
    outdir = pathlib.Path(sys.argv[1]).resolve()
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    logdir = outdir / 'logs'
    logdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    results = {}
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = [ex.submit(run, s, logdir) for _, s in CHECKS]
        for f in cf.as_completed(futs):
            s, rc, out, dt = f.result()
            results[s] = (rc, out, dt)
            print('   finished %-26s rc=%d  %6.1fs' % (s, rc, dt), flush=True)
    failed, receipt = [], {'scripts': {}}
    for sec, s in CHECKS:
        rc, out, dt = results[s]
        lines = [ln for ln in out.splitlines() if ln.startswith(('PASS ', 'FAIL '))]
        npass = sum(ln.startswith('PASS ') for ln in lines)
        nfail = len(lines) - npass
        ok = rc == 0 and nfail == 0 and npass > 0
        print('== %s  %s  [%s, %.1fs]' % (sec, s, 'ok' if ok else 'FAILED', dt))
        for ln in out.splitlines():
            print('   ' + ln)
        receipt['scripts'][s] = dict(section=sec, returncode=rc, passed=npass, failed=nfail, seconds=round(dt, 1))
        if not ok:
            failed.append(s)
    total = sum(v['passed'] for v in receipt['scripts'].values())
    receipt.update(python=platform.python_version(), platform=platform.platform(), wall_seconds=round(time.time() - t0, 1),
                   claims_passed=total, failed_scripts=failed,
                   manifest_sha256=hashlib.sha256((PKG / 'MANIFEST.sha256').read_bytes()).hexdigest())
    (outdir / 'RECEIPT.json').write_text(json.dumps(receipt, indent=1) + '\n')
    print('== summary: %d claims PASS in %d scripts, %d scripts failed%s; wall %.0fs' % (
        total, len(CHECKS), len(failed), (': ' + ' '.join(failed)) if failed else '', time.time() - t0))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
