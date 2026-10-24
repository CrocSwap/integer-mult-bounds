#!/usr/bin/env python3
"""Dimension-independent exact native phase audit for an all-fresh controller.

Uses the original nine-axis native supplier, with fresh eight-axis blocks.
No helper is hosted in a main idle field. Source all-column semantics remain
a written premise; this checks each finite raw contact and endpoint phase.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
NATIVE = HERE/'dependencies/tensor-strictification/native_inventory.py'


def need(test, why):
    if not test:
        raise AssertionError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def norm(terms):
    out = Counter()
    for axis, value in terms:
        out[axis] += value
    return tuple(sorted((axis, value % 4) for axis, value in out.items() if axis and value % 4))


def act(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length()-1]
        value ^= low
    return result


@lru_cache(None)
def polynomial(terms, dimension):
    linear = [0]*dimension
    quadratic = [0]*dimension
    for axis, value in terms:
        support = [i for i in range(dimension) if axis >> i & 1]
        for i in support:
            linear[i] = (linear[i]+value) % 4
            if value % 2:
                for j in support:
                    if i < j:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def contact(old, new, route, dimension):
    moved = norm((act(route, axis), value) for axis, value in old)
    left, right = polynomial(moved, dimension), polynomial(new, dimension)
    need(left[1] == right[1], 'Actual native contact has identical quadratic part')
    delta = tuple((a-b) % 4 for a, b in zip(right[0], left[0]))
    need(all(value in (0, 2) for value in delta), 'Even linear phase is a physical translation')
    shift = sum((value//2) << i for i, value in enumerate(delta))
    need(polynomial(norm(list(moved)+[(shift, 2)]), dimension) == right, 'Full native forward phase')
    inverse_shift = act(route, shift)
    inverse = norm([(act(route, axis), value) for axis, value in new]+[(inverse_shift, 2)])
    need(polynomial(inverse, dimension) == polynomial(old, dimension), 'Full inverse contact phase')
    return {'translation': shift, 'inverse_translation': inverse_shift}


def scalar_invoice(case, native_scalar):
    word = case['right_program']+case['left_program']
    counts = Counter(row[0] for row in word)
    need(all(Q(row[-1]) in (1, -1) for row in word if row[0] in ('ADD', 'SCALE')),
         'Literal boundary word has only unit coefficients')
    adds = counts['ADD']+3*counts['SWAP']
    negs = counts['SCALE']+counts['SWAP']
    bridges = sum(row[0] == 'ADD' for row in case['physical_events'])
    swaps = sum(row[0] == 'SIGNED_SWAP' for row in case['physical_events'])
    return native_scalar+112*(8*(adds+bridges+3*swaps)+2*negs)


def run(source_root, p=7, keep=232127, output_dir=None):
    root = Path(source_root).resolve()
    base = root/'research/kappa-rebuild'
    need((p, keep) == (7, 232127), 'This source-bound native admission is p7 keep232127')
    inventory = load(NATIVE, 'checked_native_inventory')
    native_gate = inventory.run(root)
    factor = load(HERE/'factor_receipt.py', 'fixed_p7_factor')
    case, factor_pins = factor.run(root)
    replay_path = base/'transfer-audit/p3_native_audit.py'
    need(sha256(replay_path.read_bytes()).hexdigest() == '5504a55a50546418d10c522984438cdeedb44993f7c1dab7bd4aa1ae0515d902',
         'Exact independent Laurent replay source')
    audit = load(replay_path, 'independent_laurent_replay')
    audit.replay(case)
    corrupted = json.loads(json.dumps(case))
    next(row for row in corrupted['physical_events'] if row[0] == 'LOCAL' and row[3])[3] = False
    wrong_orientation_rejected = False
    try:
        audit.replay(corrupted)
    except AssertionError:
        wrong_orientation_rejected = True
    need(wrong_orientation_rejected, 'A wrong native reverse orientation fails the exact whole Laurent word')
    phase_path = root/'research/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    if not phase_path.exists():
        phase_path = root/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    need(sha256(phase_path.read_bytes()).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
         'Exact original native port phase source')
    phases = read(phase_path)
    dimension = 9+16*p
    axes = tuple(1 << i for i in range(dimension))
    def completed(stage):
        return norm((axis, 1) for axis in axes[:9+8*stage])
    def stage_frame(stage, q):
        return norm([(axis, 1) for axis in axes[:9]]+[(q, -1)] if stage == 0
                    else [(axis, 1) for axis in axes[9+8*(stage-1):9+8*stage]])
    contacts = []
    stages = [row for row in case['physical_events'] if row[0] == 'LOCAL']
    need([row[1] for row in stages] == list(range(2*p+1)), 'Exact chronological stage sequence')
    for _, stage, pair, backward in stages:
        sign = -1 if backward else 1
        spectator = norm((axis, 1) for axis in axes[9:9+8*stage])
        for port, recipe in enumerate(phases['recipes']):
            q = recipe['q']
            basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
            need(all((b & q).bit_count() % 2 == 0 for b in basis), 'Actual owner basis is orthogonal to q')
            need(all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(basis)
                     for j, b in enumerate(basis)), 'Actual eight-vector basis is orthonormal')
            swaps = [] if stage == 0 else [b ^ axes[9+8*(stage-1)+i] for i, b in enumerate(basis)]
            route = tuple(e ^ act(swaps, sum(((e & v).bit_count() % 2) << i for i, v in enumerate(swaps)))
                          for e in axes)
            need(all(act(route, route[i]) == axes[i] for i in range(dimension)), 'Full dimension route is an involution')
            need(all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(route)
                     for j, b in enumerate(route)), 'Full dimension route is orthogonal')
            need(act(route, q) == q, 'Actual q is fixed')
            raw_x = norm([(q, 1)]) if stage == 0 else completed(stage-1)
            raw_y = () if stage == 0 else norm(list(raw_x)+[(q, -1)])
            local_x0 = norm(list(spectator)+[(q, sign)])
            local_y0 = spectator
            local_x1 = norm(list(spectator)+[(axis, sign) for axis in axes[:9]])
            local_y1 = norm(list(local_x1)+[(q, -sign)])
            out_x = completed(stage)
            out_y = norm(list(out_x)+[(q, -1)])
            maps = {name: contact(old, new, route, dimension) for name, old, new in (
                ('entry_X', raw_x, local_x0), ('entry_Y', raw_y, local_y0),
                ('exit_X', local_x1, out_x), ('exit_Y', local_y1, out_y))}
            delta = stage_frame(stage, q)
            for incoming, outgoing in ((raw_x, out_x), (raw_y, out_y)):
                need(polynomial(norm(list(outgoing)+[(a, -c) for a, c in incoming]), dimension)
                     == polynomial(delta, dimension), 'Raw diagonal operator is exactly D_s')
            cross = norm(list(out_y if sign == 1 else out_x)+
                         [(a, -c) for a, c in (raw_x if sign == 1 else raw_y)])
            need(polynomial(cross, dimension) == polynomial(norm(list(delta)+[(q, -sign)]), dimension),
                 'Raw cross operator is exactly D_s Q^(-sign)')
            contacts.append({'stage': stage, 'pair': pair, 'port': port, 'backward': backward,
                             'route': route, 'maps': maps})
    endpoints = []
    target_main = Counter()
    omitted_endpoint_phase_rejected = 0
    for role, term in enumerate(case['exact_diagonal_monomials']):
        qp, selected = term[0], term[1:]
        need(qp in (-1, 1) and set(selected) <= {0, 1}, 'Actual endpoint exponent alphabet')
        for port, recipe in enumerate(phases['recipes']):
            q = recipe['q']
            physical = norm([(q, qp)]+[entry for stage, yes in enumerate(selected) if yes for entry in stage_frame(stage, q)])
            positive = list(axes[:9]) if selected[0] else [q]
            positive += [axis for stage in range(1, len(selected)) if selected[stage]
                         for axis in axes[9+8*(stage-1):9+8*stage]]
            shift = q if qp == -1 else 0
            need(inventory.independent_axes(positive), 'Actual endpoint target axes independent')
            need(len(positive) == 1+8*sum(selected), 'Exact productive endpoint rank')
            need(polynomial(norm(list(physical)+[(shift, 2)]), dimension)
                 == polynomial(norm((axis, 1) for axis in positive), dimension), 'Complete endpoint phase normalization')
            if shift:
                need(polynomial(physical, dimension) != polynomial(norm((axis, 1) for axis in positive), dimension),
                     'Omitting the endpoint translation fails')
                omitted_endpoint_phase_rejected += 1
            endpoints.append({'role': role, 'port': port, 'rank': len(positive), 'axes': positive, 'translation': shift})
            target_main[len(positive)] += 1
    recorded = Counter((row['pair'], tuple(row['stages'])) for row in case['retained_idle_windows'])
    literal = Counter((row[1], tuple(row[2])) for row in case['physical_events'] if row[0] == 'IDLE')
    need(recorded == literal, 'Bijection of every paid whole idle and every literal controller IDLE')
    need(all(row['rank'] == 8*len(row['stages']) for row in case['retained_idle_windows']),
         'Every paid window rank matches the literal stage count')
    idle = Counter()
    idle_records = []
    for window in case['retained_idle_windows']:
        selected = window['stages']
        need(case['physical_events'].count(['IDLE', window['pair'], selected]) == 1,
             'Each full idle is attached to its original literal pair and event')
        for port, recipe in enumerate(phases['recipes']):
            q = recipe['q']
            if 0 in selected:
                need(selected == list(range(len(selected))) and len(selected) >= 2, 'Initial window contiguous from stage0')
                positive = recipe['idle_children'][0]['orthogonal_axes'][:]
                positive += [axis for stage in selected[2:] for axis in axes[9+8*(stage-1):9+8*stage]]
                shift = recipe['idle_children'][0]['translation_after']
            else:
                positive = [axis for stage in selected for axis in axes[9+8*(stage-1):9+8*stage]]
                shift = 0
            desired = norm(entry for stage in selected for entry in stage_frame(stage, q))
            actual = norm([(axis, 1) for axis in positive]+[(shift, 2)])
            need(inventory.independent_axes(positive) and len(positive) == window['rank'], 'Exact whole idle rank')
            need(polynomial(actual, dimension) == polynomial(desired, dimension), 'Exact complete whole idle phase')
            idle[len(positive)] += 2
            idle_records.append({'window': window['index'], 'pair': window['pair'], 'stages': selected,
                                 'port': port, 'owners': [f'X{window["pair"]}:{port}', f'Y{window["pair"]}:{port}'],
                                 'axes': positive, 'translation': shift})
    receipt = read(base/'complex/full-identity-certificates/RESULT.json')['providers']['THREE-base']
    target_helpers = Counter({int(k): v*(2*p+1) for k, v in receipt['helper_boundary']['widths'].items()})
    targets = target_main+target_helpers
    paid = Counter({int(k): v*(2*p+1) for k, v in receipt['unsplit_replays']['forward']['paid_profile'].items()})
    paid.update(idle)
    scalar = scalar_invoice(case, sum(receipt['split_replays']['backward' if row[3] else 'forward']
                                      ['independent_native_replay']['conservative_real_scalar_primitive_allowance'] for row in stages))
    artifact = {'contacts': contacts, 'endpoints': endpoints, 'whole_idles': idle_records, 'formal': case}
    artifact_json = json.dumps(artifact, sort_keys=True, separators=(',', ':')).encode()
    artifact_bytes = gzip.compress(artifact_json, compresslevel=9, mtime=0)
    if output_dir is not None:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        (output/'NATIVE-GEOMETRY.json.gz').write_bytes(artifact_bytes)
    result = {'status': 'PASS_EXACT_LAURENT_ALL_MAIN_CONTACTS_ENDPOINTS_AND_FULL_IDLE_PHASES',
              'p': p, 'keep': keep, 'dimension': dimension, 'contacts': 4*len(contacts),
              'main_fields': 224*p, 'fresh_helper_fields': 408*(2*p+1),
              'targets': dict(sorted(targets.items())), 'paid': dict(sorted(paid.items())),
              'native_scalar_allowance': scalar, 'scalar_allowance': scalar,
              'productive_fields': sum(targets.values()), 'paid_calls': sum(paid.values()), 'whole_idle_profile': dict(sorted(idle.items())),
              'rank_margin': sum(k*v for k, v in targets.items())-sum(k*v for k, v in paid.items()),
              'artifact_sha256': sha256(artifact_json).hexdigest(),
              'artifact_hash_encoding': 'Uncompressed UTF-8 JSON, sort_keys=True, separators=(comma,colon)',
              'native_source_gate': native_gate['status'],
              'negative_controls': {'wrong_native_orientation_rejected': wrong_orientation_rejected,
                                    'omitted_endpoint_translation_rejected': omitted_endpoint_phase_rejected},
              'source_sha256': {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
                                for path in (phase_path, base/'transfer-audit/p3_native_audit.py',
                                             base/'complex/full-identity-certificates/RESULT.json')},
              'limits': 'Finite exact physical controller admission; inherited all-column local word, tensor strictification, new full-word precision/stock and outer transfer remain written proof obligations.'}
    result['source_sha256'].update(native_gate['source_sha256'])
    result['source_sha256'].update(factor_pins)
    result['factor_receipt_sha256'] = factor.RECEIPT_SHA256
    result['schema'] = 'source-bound-p7-all-fresh-complete-native-controller/1'
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=HERE/'source')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    result = run(args.source_root, output_dir=args.output_dir)
    if args.output_dir:
        (args.output_dir/'NATIVE.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','contacts','dimension','productive_fields','paid_calls','targets','paid','native_scalar_allowance')}, sort_keys=True))
