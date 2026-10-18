#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-pinned exhaustive retiming boundary and exact A-frame optimization."""
import argparse
import contextlib
import copy
import gzip
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import tempfile
import types

P = Path(__file__).resolve().parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def authenticate(path, expected, raw=None):
    require(hashlib.sha256(path.read_bytes() if raw is None else raw).hexdigest() == expected,
            'source SHA256 mismatch: ' + path.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    pins = json.loads((P / 'PINS.json').read_text())
    for name, pin in pins.items():
        authenticate(P / name, pin['sha256'])
    pm = load('preload_move', P / 'vendor/preload_move.py')
    load('exact_root', P / 'vendor/root.py')
    common = load('common', P / 'common.py')
    frames = load('frames', P / 'frames.py')
    barrier = load('barrier', P / 'barrier.py')
    opt = load('optimizer', P / 'optimize.py')
    auditor = load('retiming_auditor', P / 'vendor/audit_local.py')
    records, controls = {}, {}
    with tempfile.TemporaryDirectory(prefix='normal45-retiming-') as tmp:
        work = Path(tmp)
        def audit(word, name):
            barrier.explicit_invoice(word)
            path = work / (name + '.json.gz')
            path.write_bytes(gzip.compress(json.dumps(word, separators=(',', ':')).encode(), mtime=0))
            with contextlib.redirect_stdout(io.StringIO()):
                receipt = auditor.run(path, work / (name + '.json'))
            require(receipt['orientations'] == {'forward': 'PASS', 'dual': 'PASS'}, 'both orientations')
            require(receipt['independent_inputs'] == 632 and receipt['zero_buffers'] == 86,
                    'full inherited local interface')
        def rejects(name, action):
            try:
                action()
            except (ValueError, RuntimeError, AssertionError):
                controls[name] = 'rejected'
            else:
                raise ValueError('negative control accepted: ' + name)
        src = 'data/WORD-base.json.gz'
        rejects('corrupt-source', lambda: authenticate(P / src, pins[src]['sha256'], (P / src).read_bytes() + b'!'))
        # Independent enumeration of all subspaces in dimensions 0..3.
        for d, expected in enumerate((1, 2, 5, 16)):
            hi = tuple(1 << i for i in range(d))
            actual = opt.interval((), pm.basis(hi))
            require(len(actual) == expected, 'complete subspace lattice control')
            require(len({barrier.span(tuple(x)) for x in actual}) == expected, 'distinct complete subspaces')
        controls['subspace-counts-0-through-3'] = '1,2,5,16'
        for tag in ('base', 'extra'):
            word = json.loads(gzip.decompress((P / f'data/WORD-{tag}.json.gz').read_bytes()))
            require(word['report']['local_profile'] == common.PROFILE, 'pinned baseline profile')
            audit(word, tag + '-baseline')
            baseline_word, baseline_dp = opt.optimize(copy.deepcopy(word))
            require(baseline_word['report']['local_profile'] == common.PROFILE, 'baseline optimum')
            fixed_rest = tuple(common.PROFILE.get(str(r), 0) - baseline_dp['optimized_variable_profile'][r - 1]
                               for r in range(1, 10))
            require(all(x >= 0 for x in fixed_rest), 'nonnegative fixed remainder')
            cases = []
            for obj in common.OBJECTS:
                target, source, original, first, boundary = obj
                receipt, representatives = barrier.census(word, *obj)
                optimized = []
                for rep in representatives:
                    row = rep['row']
                    for order in itertools.permutations(sorted(row)):
                        child = common.retime(word, original, rep['cut'], row, order)
                        child, proof = opt.optimize(child)
                        require(child['report']['local_profile'] == common.PROFILE, 'no lower profile in domain')
                        require(tuple(common.PROFILE.get(str(r), 0) - proof['optimized_variable_profile'][r - 1]
                                      for r in range(1, 10)) == fixed_rest, 'complete objective accounting')
                        child['cleanup'] = common.cleanup(child)
                        name = f'{tag}-{source}-{rep["cut"]}-' + '-'.join(map(str, order))
                        audit(child, name)
                        optimized.append({'cut': rep['cut'], 'source_order': list(order),
                                          'row': {str(r): str(a) for r, a in sorted(row.items())},
                                          'local_profile': child['report']['local_profile'], 'dp': proof})
                        # At the nontrivial two-source boundary test algebra, cleanup and the ledger separately.
                        if rep['cut'] == boundary and len(row) == 2 and order == tuple(sorted(row)):
                            bad = copy.deepcopy(child)
                            bad['A'][rep['cut']][3] *= -1
                            bad['cleanup'] = common.cleanup(bad)
                            rejects(name + '-wrong-sign', lambda: audit(bad, name + '-wrong-sign'))
                            bad = copy.deepcopy(child)
                            bad['cleanup'] = word['cleanup']
                            rejects(name + '-stale-cleanup', lambda: audit(bad, name + '-stale-cleanup'))
                            bad = copy.deepcopy(child)
                            bad['report']['local_profile']['1'] -= 1
                            rejects(name + '-missing-charge', lambda: audit(bad, name + '-missing-charge'))
                # Earliest preceding cut is impossible even when replacement source order is reversed.
                cut = boundary - 1
                row = {source: common.Q(1)}
                for g in reversed(word['A'][cut:original]):
                    row = common.scalar_pull(row, g)
                for order in (tuple(sorted(row)), tuple(sorted(row, reverse=True))):
                    bad = common.retime(word, original, cut, row, order)
                    rejects(f'{tag}-{source}-early-{order}', lambda: frames.solve(bad))
                # Removing all centre ceilings removes this obstruction (not a valid supplier).
                low, high = barrier.boundaries(word, original, relax_centres=True)
                require(all(low[cut][target] <= high[cut][r] for r in row), 'relaxed-centre positive control')
                controls[f'{tag}-{source}-relaxed-centres'] = 'admissible to the relaxed barrier only'
                receipt['representatives'] = optimized
                receipt['earlier_multitarget'] = barrier.earlier_transport(word, target, source, original, first)
                cases.append(receipt)
                print(tag, source, receipt['cuts'], 'cuts;', len(optimized), 'exact frame optima', flush=True)
            records[tag] = cases
        result = {'status': 'PASS_NORMAL45_SINGLE_SHEAR_RETIMING_BOUNDARY',
                  'providers': records, 'controls': controls,
                  'cost_interval': [str(opt.B_LO), str(opt.B_HI)],
                  'cost_scale': opt.SCALE,
                  'local_profile': common.PROFILE,
                  'scope': 'One terminal A shear at a time; arbitrary source-addition order and all non-prelude A frames. Prelude, remaining scalar order, B, restore, entrances, endpoints and inventory fixed. No new supplier or kappa.'}
        rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
        if args.write_result:
            (P / 'RESULT.json').write_text(rendered)
        else:
            require(json.loads((P / 'RESULT.json').read_text()) == json.loads(rendered), 'committed deterministic result')
        print(result['status'], 'controls', len(controls), flush=True)


if __name__ == '__main__':
    main()
