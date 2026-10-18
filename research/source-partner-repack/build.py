#!/usr/bin/env python3
"""Build PR2530's derivative with its own unchanged build.py, then substitute this package's call order and owner fill.

Only new/borrow-fill/ORDER.json (the shifted diagonal order) and new/borrow-fill/FILL.json.gz change. Words, providers,
plan inputs and every pipeline stage are PR2530's (research/source-partner-lifetimes). Windows are recomputed from the
order by the package's own vendor/build_parent.py; the owner witness is re-derived by its reconstruct.py (literal windows,
bins, prefixes and families) and lift_parent.py, exactly as PR2530's build does for its own order and fill.
"""
import argparse, hashlib, shutil, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / 'research/source-partner-lifetimes'
sys.path.insert(1, str(SRC))   # PR2530's own modules (generate.py) resolve from its directory
import importlib.util   # noqa: E402
_spec = importlib.util.spec_from_file_location('pr2530_build', SRC / 'build.py')
pr2530 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(pr2530)   # PR2530's build.py, unchanged
read, write, need, sha = pr2530.read, pr2530.write, pr2530.need, pr2530.sha
FILL = HERE / 'evidence/repack-fill.json.gz'
ORDER = HERE / 'evidence/repack-order.json'


def build(work):
    work = Path(work)
    p = pr2530.build(work)                      # PR2530 derivative with PR2530's fill (its own checks run)
    old = read(p / 'new/borrow-fill/FILL.json.gz'); new = read(FILL)
    need(old['columns'] == new['columns'] and old['dispatch_overrides'] == new['dispatch_overrides'], 'fill format')
    need(sorted(map(tuple, (r[:2] for r in old['rows']))) == sorted(map(tuple, (r[:2] for r in new['rows']))), 'same (call, helper) roles')
    old_order = read(p / 'new/borrow-fill/ORDER.json'); order = read(ORDER)
    need(sorted(map(tuple, old_order)) == sorted(map(tuple, order)), 'the order is a permutation of the same 666 calls')
    for r in range(74):   # every replica keeps its nine stages in order (the per-replica event projection is re-checked by actual_windows)
        need([s for s, rr in order if rr == r] == list(range(9)), 'stage order of replica %d' % r)
    need(order == sorted(order, key=lambda c: (4 * c[0] + c[1] + (4 if c[0] >= 1 else 0), c[0], c[1])), 'shifted diagonal order key')
    shutil.copy2(ORDER, p / 'new/borrow-fill/ORDER.json')
    shutil.copy2(FILL, p / 'new/borrow-fill/FILL.json.gz')
    for script, args in [('reconstruct.py', ['--out', work / 'repack-owners']), ('lift_parent.py', ['--owners', work / 'repack-owners', '--out', work / 'repack-parent-data'])]:
        subprocess.run([sys.executable, '-B', str(p / script), *map(str, args)], check=True)
    for n in ['PLAN.json', 'OWNERS.json.gz', 'DISPATCH.json', 'PROFILE.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz', 'SPEC.json']:
        shutil.copy2(work / 'repack-parent-data' / n, p / n)
    for n in ['PLAN.json', 'PROFILE.json', 'SPEC.json']:
        shutil.copy2(work / 'repack-parent-data' / n, p / 'new' / n)
    for name in ['SPEC.json', 'new/SPEC.json']:   # the same frozen outer settings as PR2530's build.py
        spec = read(p / name)
        need(spec['geometry']['replicas'] == 74 and spec['geometry']['charged_prefix_bits'] == 2048, 'geometry')
        spec['outer_refinement'] = dict(endpoint_digits=24, grid_digits=18, margin_digits=28, bootstrap_steps=12)
        spec['expected']['live'] = 66304
        write(p / name, spec)
    return p


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); a = ap.parse_args()
    print(build(a.work.resolve()))
