#!/usr/bin/env python3
"""Reproduce the pinned phase-alias defect and validate its one-line repair.

Uses only Python's standard library and Git. Fetch the source commit named in
SOURCE.json before running. No network access or tracked-file writes occur here.
"""
import argparse
import copy
import difflib
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GUARD = "    c.need(all(phases is not v for v in arrays),'phase array aliases mutable data')\n"
ANCHOR = "    arrays=[x,y]+scratch;c.need(len({id(v)for v in arrays})==len(arrays),'all ancestor arrays distinct')\n"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call(module, arrays, factors, phases, bits, direction, sign):
    stats = dict(leaves=0, scalar_steps=0)
    module.compose(arrays[0], arrays[1], factors, arrays[2:], phases,
                   F(1, 2), bits, direction, sign, stats)
    return stats['leaves']


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()


def aliases(module, factors_count):
    results = []
    depth = (factors_count - 1).bit_length()
    factors = [(False, (F(1, 4), F(0)), F(1))] * factors_count
    for index in range(2 + depth):
        arrays = [[(F(1), F(0))] * 2 for _ in range(2 + depth)]
        before = copy.deepcopy(arrays)
        try:
            call(module, arrays, factors, arrays[index], 8, 1, 1)
        except ValueError as error:
            message = str(error)
        else:
            message = 'accepted'
        results.append(dict(alias=index, message=message, unchanged=arrays == before, after=arrays))
    return results


def positive_checks(original, patched, model):
    rng = random.Random(67)
    units = [(F(1), F(0)), (F(0), F(1)), (F(-1), F(0)),
             (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]
    traces = hashlib.sha256()
    cases = leaves = 0
    for nf in (1, 2, 3, 5, 8):
        factors = [(i % 2 == 0, (F(1, 4), F((-1)**i, 8)), F(3 if i == 0 else 1))
                   for i in range(nf)]
        for length in (1, 2, 3, 5, 8):
            phases = [rng.choice(units) for _ in range(length)]
            for bits in (4, 8, 16):
                grid = 1 << bits
                integers = [[(rng.randrange(-2*grid, 2*grid+1), rng.randrange(-2*grid, 2*grid+1))
                             for _ in range(length)] for _ in range(2+(nf-1).bit_length())]
                values = [[(F(x, grid), F(y, grid)) for x, y in array] for array in integers]
                for direction in (-1, 1):
                    for sign in (-1, 1):
                        baseline, fixed, independent = copy.deepcopy(values), copy.deepcopy(values), copy.deepcopy(integers)
                        calls = call(original, baseline, factors, phases, bits, direction, sign)
                        need(call(patched, fixed, factors, phases, bits, direction, sign) == calls, 'changed leaf count')
                        need(model.execute(independent, factors, phases, bits, direction, sign) == calls, 'independent leaf count')
                        expected = [[(F(x, grid), F(y, grid)) for x, y in array] for array in independent]
                        need(fixed == baseline == expected, 'integer-grid differential mismatch')
                        need(fixed[0] == values[0] and fixed[2:] == values[2:], 'source/scratch restoration')
                        call(patched, fixed, factors, phases, bits, direction, -sign)
                        model.execute(independent, factors, phases, bits, direction, -sign)
                        need(fixed == values and independent == integers, 'exact inverse word')
                        traces.update(encode(baseline))
                        cases += 1
                        leaves += calls
    # Equal values are allowed; only identity aliasing is forbidden.
    arrays = [[(F(1), F(0))] * 2 for _ in range(2)]
    phases = arrays[0].copy()
    call(patched, arrays, [(False, (F(1, 4), F(0)), F(1))], phases, 8, 1, 1)
    need(phases == [(F(1), F(0))] * 2, 'read-only phases changed')
    return dict(cases=cases, forward_leaf_executions=leaves, inverse_cases=cases,
                distinct_equal_phase_control=True, output_digest=traces.hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    source = json.loads((HERE/'SOURCE.json').read_text())
    blobs = {}
    for name, expected in source['files'].items():
        result = subprocess.run(['git', 'show', source['commit']+':'+source['package']+'/'+name],
                                cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        need(result.returncode == 0, 'Missing pinned source; run the README fetch command first')
        need(hashlib.sha256(result.stdout).hexdigest() == expected, 'source hash mismatch: '+name)
        blobs[name] = result.stdout
    original_text = blobs['dirty.py'].decode()
    need(original_text.count(ANCHOR) == 1, 'unambiguous patch anchor')
    patched_text = original_text.replace(ANCHOR, ANCHOR+GUARD)
    path = source['package']+'/dirty.py'
    patch = ''.join(difflib.unified_diff(original_text.splitlines(True), patched_text.splitlines(True),
                                       fromfile='a/'+path, tofile='b/'+path))
    need(patch == (HERE/'phase-alias-guard.patch').read_text(), 'patch differs from tested repair')
    model = load('integer_audit_model', HERE/'integer_model.py')
    # Positive and negative half-grid ties differ under sign negation.
    need([model.nearest(F(n, 2)) for n in (-3, -1, 1, 3)] == [-1, 0, 1, 2], 'tie rule')
    with tempfile.TemporaryDirectory(prefix='cyclic-dirty-audit-') as temp:
        root = Path(temp)
        for directory in ('original', 'patched'):
            for name, content in blobs.items():
                target = root/directory/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
        application = subprocess.run(['git', 'apply', '-p3', str(HERE/'phase-alias-guard.patch')],
                                     cwd=root/'patched', capture_output=True, text=True)
        need(application.returncode == 0, 'patch application: '+application.stderr)
        need((root/'patched/dirty.py').read_text() == patched_text, 'applied patch content')
        original = load('original_dirty_audit', root/'original/dirty.py')
        patched = load('patched_dirty_audit', root/'patched/dirty.py')
        original_counterexamples = aliases(original, 1)
        need(original_counterexamples[0]['message'] == 'accepted', 'source alias no longer accepted')
        need(original_counterexamples[0]['after'][0][1] == (F(15, 16), F(0)), 'counterexample changed')
        need(original_counterexamples[1]['message'] == 'accepted' and not original_counterexamples[1]['unchanged'], 'target alias no longer accepted')
        # Independent exact family: source[1] becomes 1-b^2 when phases aliases source.
        family = []
        for b in (F(1, 8), F(1, 4), F(3, 8), F(1, 2)):
            for bits in (8, 16, 64):
                arrays = [[(F(1), F(0))]*2, [(F(0), F(0))]*2]
                call(original, arrays, [(False, (b, F(0)), F(1))], arrays[0], bits, 1, 1)
                expected = 1-b*b
                need(arrays[0][1] == (expected, F(0)), 'exact alias family')
                family.append(dict(b=str(b), bits=bits, source_second=str(expected)))
        rejected = []
        for nf in (1, 2, 3, 5, 8):
            for row in aliases(patched, nf):
                need(row['message'] == 'phase array aliases mutable data' and row['unchanged'], 'alias rejected after mutation or accepted')
                rejected.append(dict(factors=nf, alias=row['alias'], unchanged=True))
        positives = positive_checks(original, patched, model)
        # Deleting the new guard must re-expose the counterexample, not merely fail syntax.
        (root/'patched/dirty.py').write_text(patched_text.replace(GUARD, ''))
        mutant = load('missing_guard_audit', root/'patched/dirty.py')
        need(not aliases(mutant, 1)[0]['unchanged'], 'missing-guard control did not detect source damage')
        # Run the predecessor's instruction mutation suite against the patched code.
        (root/'patched/dirty.py').write_text(patched_text)
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'patched/dirty_controls.py'),
                                 '--out', str(root/'controls.json')], capture_output=True, text=True)
        need(result.returncode == 0, 'inherited controls failed: '+result.stderr)
        inherited = json.loads((root/'controls.json').read_text())
        need(len(inherited['controls']) == 8, 'inherited control count')
    report = dict(status='PASS_PHASE_ALIAS_REPAIR_AND_INTEGER_GRID_AUDIT', source_commit=source['commit'],
                  source_hashes=source['files'], original_counterexamples=original_counterexamples,
                  exact_source_alias_family=family, rejected_aliases=rejected,
                  positive=positives, missing_guard_control=True, inherited_controls=inherited,
                  scope='Read-only phase alias admission and finite exact restoration; no new kappa or all-length formal proof')
    if args.out:
        args.out.write_bytes(json.dumps(report, indent=2, default=str).encode()+b'\n')
    print(report['status'], positives['cases'], 'differential cases;', len(rejected), 'pre-mutation alias rejections')


if __name__ == '__main__':
    main()
