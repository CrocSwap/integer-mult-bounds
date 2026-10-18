#!/usr/bin/env python3
"""Reproduce the partial K/M obstruction and its fully paid control circuit.

Standard library only. No network, optimizer, or selected-frontier regeneration.
Douglas R. Colkitt with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location('partial_k_model', PACKAGE/'model.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
require = model.require


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value):
    return json.loads(json.dumps(value, sort_keys=True))


def check_pins(pins, root=ROOT):
    for path, digest in pins['files'].items():
        require(sha(root/path) == digest, 'source pin mismatch: '+path)


def run(name, script, arguments, work, expected_failure=False):
    # Inherited auditors use assertions. Explicitly start a fresh, non-optimized
    # interpreter, even when this orchestration runs under -I -O.
    command = [sys.executable, '-I', '-B', str(script), *map(str, arguments)]
    result = subprocess.run(command, capture_output=True, text=True)
    (work/(name+'.log')).write_text(result.stdout+result.stderr)
    if expected_failure:
        require(result.returncode != 0, 'negative control accepted: '+name)
        require('AssertionError' in result.stderr, 'control failed for an unrelated reason: '+name)
    else:
        require(result.returncode == 0, name+' failed: '+result.stderr[-2000:])
    return result


def audit_receipt(path):
    receipt = read(path/'SCALAR-FRAME-AUDIT.json')
    receipt.pop('seconds')
    widths = receipt.pop('widths')
    receipt['residual_width_histogram'] = dict(sorted(Counter(widths).items()))
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, help='new output directory; default temporary')
    ap.add_argument('--write', type=Path, help='write a new result instead of comparing EXPECTED.json')
    args = ap.parse_args()
    work = args.work.resolve() if args.work else Path(tempfile.mkdtemp(prefix='partial-k-bypass-'))/'replay'
    require(not work.exists(), 'use a new work directory')
    work.mkdir(parents=True)
    pins = read(PACKAGE/'SOURCE-PINS.json')
    check_pins(pins)
    bad_pins = copy.deepcopy(pins)
    bad_pins['files'][next(iter(bad_pins['files']))] = '0'*64
    try:
        check_pins(bad_pins)
    except ValueError:
        pass
    else:
        raise ValueError('corrupt source pin accepted')

    geometry = model.load_geometry(ROOT/'research/direct-delivery504-global/inputs/hamming')
    pairs = model.mixed_pairs(geometry)
    require(len(pairs) == 8 and pairs[24 % len(pairs)] == (0, 2), 'assignment object changed')
    cases = [model.case(geometry, pair, sign) for pair in pairs for sign in (-1, 1)]
    selected = [c for c in cases if c['pair'] == [0, 2]]
    searches = []
    for case in selected:
        for copies in (2, 3, 4):
            answer = model.search(case, copies)
            require(answer['status'] == ('FOUND' if copies == 4 else 'EXHAUSTED'), 'unexpected schedule status')
            searches.append(dict(sign=case['sign'], **answer))
    rebuilt_recipe = model.recipe(selected[0], searches[2]['schedule'])
    require(normalized(rebuilt_recipe) == read(PACKAGE/'RECIPE.json'), 'recipe differs from seeded search')
    relaxed = model.search(selected[0], 2, ordinary_guard=False)
    require(relaxed['status'] == 'FOUND', 'missing-consumer guard control stopped distinguishing the model')
    # Replay that relaxed schedule and record the first violation of the
    # actual ordinary-consumer caps; this is a geometric counterexample to
    # accepting the relaxed search as a complete circuit.
    state = [()]*4 + selected[0]['leaver_frames'] + [selected[0]['packet_frame']]*2
    violation = None
    for step, (event, source) in enumerate(relaxed['schedule']):
        target = selected[0]['operations'][event][0]
        frame = model.join(state[target], state[source])
        state[target] = state[source] = frame
        if source < 8 and not model.contained(frame, selected[0]['ordinary_labels']):
            violation = dict(step=step, event=event, leaver=source-4, frame=frame)
            break
    require(violation is not None, 'relaxed schedule unexpectedly satisfies ordinary caps')

    constructor = ROOT/'research/complex-k492-owner-repair/code/construct_k_triangle.py'
    auditor = ROOT/'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
    inputs = ROOT/'research/direct-delivery504-global/inputs/hamming'
    triangles = ROOT/'research/complex-k492-owner-repair/data/TRI-SCHEDULE.json'
    routing = ROOT/'research/direct-delivery504-global/inputs/data-base/split-centres/CANONICAL-WORD.json.gz'
    run('baseline-build', constructor, [inputs, work/'baseline', triangles], work)
    run('control-build', PACKAGE/'construct.py', [PACKAGE/'RECIPE.json', work/'control'], work)
    for name in ('baseline', 'control'):
        run(name+'-native-audit', auditor,
            ['--raw', work/name/'FULL-WORD.json.gz', '--routing', routing, '--out', work/(name+'-native')], work)
    base = audit_receipt(work/'baseline-native')
    control = audit_receipt(work/'control-native')
    require(base['helpers'] == control['helpers'] == 492, 'unpaid helper')
    require(base['residual_width_histogram'] == control['residual_width_histogram'] == {9: 492}, 'width inventory changed')
    delta = Counter({int(k): v for k, v in control['local_profile'].items()})
    delta.subtract({int(k): v for k, v in base['local_profile'].items()})
    delta = {rank: count for rank, count in sorted(delta.items()) if count}
    require(delta == {1: 10, 2: -6, 3: 2, 4: 2, 6: -2}, 'profile delta changed')
    more_spread = [6, 2, 2, 2, 0, 0, 0]
    less_spread = [4, 3, 1, 1, 1, 1, 1]
    prefix_pairs = [[sum(more_spread[:i]), sum(less_spread[:i])] for i in range(1, 8)]
    require(all(left >= right for left, right in prefix_pairs), 'majorization fails')
    require(prefix_pairs[-1][0] == prefix_pairs[-1][1], 'rank mass not conserved')
    proof_delta = Counter(less_spread)
    proof_delta.subtract(more_spread)
    require({k: 2*v for k, v in proof_delta.items() if k and v} == delta, 'majorization does not price the circuit')

    word = read(work/'control/FULL-WORD.json.gz')
    mutations = {}
    bad = copy.deepcopy(word)
    bad['cut'][0][3] *= 2
    mutations['wrong-source-coefficient'] = bad
    bad = copy.deepcopy(word)
    bad['cleanup'] = bad['cleanup'][1:]
    mutations['missing-dirty-restoration'] = bad
    bad = copy.deepcopy(word)
    bad['report']['local_profile']['1'] -= 1
    mutations['unpaid-source-access'] = bad
    bad = copy.deepcopy(word)
    bad['B'][0][-1] = []
    mutations['illegal-read-frame'] = bad
    controls = []
    for name, bad in mutations.items():
        path = work/(name+'.json')
        path.write_text(json.dumps(bad))
        failure = run(name, auditor, ['--raw', path, '--routing', routing, '--out', work/name], work, True)
        # Pin the diagnostic category, not Python/version-dependent line numbers.
        last = next(line for line in reversed(failure.stderr.splitlines()) if 'AssertionError' in line)
        controls.append(dict(name=name, rejected=True, diagnostic=last))
    result = dict(
        status='PASS_PARTIAL_K_BYPASS_FLOOR_AND_UNFAVORABLE_PAID_CONTROL',
        base_commit=pins['base_commit'], assignment_seed=24,
        exact_geometry_cases=cases, bounded_searches=searches,
        missing_ordinary_guard_control=dict(**relaxed, first_actual_violation=violation),
        baseline=base, paid_control=control, profile_delta=delta,
        majorization=dict(more_spread=more_spread, less_spread=less_spread, prefix_pairs=prefix_pairs,
                          conclusion='control moment strictly larger for every 0 < exponent < 1'),
        negative_controls=controls, corrupt_source_pin_rejected=True,
        scope='Fixed two-face bypass with unchanged ordinary M consumers and pure remaining packets. No general delivery lower bound, phase/global admission, new kappa, or formal multiplication proof.')
    payload = json.dumps(result, indent=2, sort_keys=True)+'\n'
    (work/'RESULT.json').write_text(payload)
    if args.write:
        args.write.write_text(payload)
    else:
        require(normalized(result) == read(PACKAGE/'EXPECTED.json'), 'receipt differs from EXPECTED.json')
    print(result['status'])
    print('16 exact geometric cases; 2/3 carriers exhausted for both seed-selected signs; 4 carriers attained.')
    print('Both 716-column native orientations pass; 4 circuit mutations rejected; no new kappa.')
    print('Evidence:', work)


if __name__ == '__main__':
    main()
