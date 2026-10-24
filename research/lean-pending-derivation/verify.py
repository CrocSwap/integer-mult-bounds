#!/usr/bin/env python3
"""Build and audit the schedule-derived pending ranges for PR540's selected invocation.

Prerequisite: PR540's project is built, e.g.
  (cd research/lean-multi-host-source && lake build PhysicalSourceConnection)

Steps:
  1. generate_pending_schedule.py --check (literal schedule matches the pinned inputs);
  2. compile PendingScheduleData, PendingDerivation and PendingBinding with Lean 4.21
     against PR540's build (LEAN_PATH from `lake env`), with no change to PR540's files;
  3. require the axiom audit to list only propext, Quot.sound and Classical.choice;
  4. run the six mutation controls (each must fail by `decide`).

usage: verify.py [--lake LAKE]
Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
"""
import argparse, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent / 'lean-multi-host-source'
MODULES = ['PendingScheduleData', 'PendingDerivation', 'PendingBinding']
EXPECTED_THEOREMS = {
    'PendingDerivation.idle_ranks_and_nesting', 'PendingDerivation.hosted_windows',
    'PendingDerivation.target_derived', 'PendingDerivation.target_in_derived_pending',
    'PendingBinding.pendingTag_derived', 'PendingBinding.pending_eq_derived',
    'PendingBinding.selected_invocation_completion_derived',
}
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f'FAIL: {" ".join(map(str, cmd))}\n{r.stdout}{r.stderr}')
    return r.stdout


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--lake', default='lake'); a = ap.parse_args()
    print(run([sys.executable, '-I', '-B', HERE / 'generate_pending_schedule.py', '--check']).strip())
    toolchain = (HERE / 'lean-toolchain').read_text().strip()
    assert toolchain == (PROJECT / 'lean-toolchain').read_text().strip() == 'leanprover/lean4:v4.21.0'
    base = run([a.lake, 'env', 'printenv', 'LEAN_PATH'], cwd=PROJECT).strip()
    lean = run([a.lake, 'env', 'which', 'lean'], cwd=PROJECT).strip()
    assert (PROJECT / '.lake/build/lib/lean/PhysicalSourceConnection.olean').exists(), \
        'build PR540 first: lake build PhysicalSourceConnection'
    audit = {}
    with tempfile.TemporaryDirectory() as tmp:
        path = f'{tmp}{os.pathsep}{base}'
        env = dict(os.environ, LEAN_PATH=path)
        for m in MODULES:
            out = run([lean, f'--root={HERE}', '-o', f'{tmp}/{m}.olean', HERE / f'{m}.lean'], env=env)
            for line in out.splitlines():
                mt = re.search(r"'([\w.]+)' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])", line)
                if mt:
                    audit[mt[1]] = sorted(x.strip() for x in (mt[3] or '').split(',') if x.strip())
            print(f'compiled {m}')
        assert set(audit) == EXPECTED_THEOREMS, sorted(set(audit) ^ EXPECTED_THEOREMS)
        assert all(set(v) <= ALLOWED for v in audit.values()), audit
        for k in sorted(audit):
            print(f'  {k}: {audit[k] or "no axioms"}')
        print(run([sys.executable, '-I', '-B', HERE / 'pending_controls.py', lean, path]).strip())
    print('PASS_PR540_PENDING_RANGES_DERIVED_IN_LEAN')


if __name__ == '__main__':
    main()
