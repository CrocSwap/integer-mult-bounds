#!/usr/bin/env python3
"""Check the exact local interface for arbitrary line-encoded records."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PREVIOUS = HERE.parent/'row-capture-native-review-20261020'
HELPER = PREVIOUS/'check.py'
HELPER_PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != HELPER_PIN:
    raise ValueError('Independent review helper pin')
spec = importlib.util.spec_from_file_location('independent_row_review', HELPER)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
review.read(HELPER, HELPER_PIN)
need, read, frozen = review.need, review.read, review.frozen
P = review.P
SOURCE = review.NATIVE


def trace(word):
    current = list(word['start'])
    profile, used = Counter(), set()
    for i, event in enumerate(word['events']):
        if i == word['stage_ranges']['late_query'][0]:
            need(all(current[p] == 1 for p in range(112)) and
                 all(current[112+p] == 1 for p in P), 'Complete common-FULL query cut')
        if event[0] == 'native':
            _, field, before, after, rank, key = event
            need(0 <= field < 224 and current[field] == before, 'Native field and input frame')
            need(word['native_recipes'][key]['rank'] == rank, 'Native occurrence rank')
            current[field] = after
            profile[rank] += 1
            used.add(key)
        else:
            need(event[0] == 'scalar', 'Event opcode')
            _, scalar, frame = event
            op, target, origin, _ = scalar
            need(0 <= target < 224 and current[target] == frame, 'Scalar target frame')
            if op == 'add':
                need(0 <= origin < 224 and current[origin] == frame and target != origin,
                     'Scalar source frame')
            else:
                need(op == 'scale' and origin is None, 'Scale grammar')
    need(current == word['final'], 'Exact complete final frames')
    need(used == set(word['native_recipes']), 'Every stored native recipe is used')
    return profile


def check_word(word, old, e, ce):
    need(word['frames'] == old['frames'] and word['final'] == old['final'],
         'Exact inherited frame geometry and output declarations')
    expected_start = list(old['start'])
    for p in P:
        expected_start[112+p] = old['start'][p]
        need(len(word['frames'][expected_start[112+p]]) == 1,
             'Selected canonical line frame')
    need(word['start'] == expected_start, 'Only selected input frames change')
    start, end = old['stage_ranges']['retained_core']
    kept = old['events'][start:end]
    start, end = old['stage_ranges']['late_query']
    query = old['events'][start:end]
    progress = [['native', 112+p, old['start'][p], 1, 8, 'capture-line:'+str(p)] for p in P]
    need(word['events'] == kept+progress+query, 'Exact complete local reuse order')
    need(word['retained_original_event_indices'] == old['retained_original_event_indices'],
         'Same retained raw events')
    need(word['stage_ranges'] == {
        'precode': [0, 0], 'retained_core': [0, 2390],
        'selected_line_progress': [2390, 2406], 'late_query': [2406, 2654]},
        'Exact reuse stage boundaries')
    selected = {112+p for p in P}
    for event in kept:
        if event[0] == 'scalar':
            need(event[1][1] not in selected and
                 (event[1][0] != 'add' or event[1][2] not in selected),
                 'Retained core does not access selected records')
        else:
            need(event[1] not in selected, 'Retained native core does not access selected records')
    inherited = set(old['native_recipes'])-{'capture-full'}
    fresh = {'capture-line:'+str(p) for p in P}
    need(set(word['native_recipes']) == inherited|fresh, 'Exact native recipe set')
    for key in inherited:
        need(word['native_recipes'][key] == old['native_recipes'][key],
             'Byte-equal inherited native recipe')
    need(word['output_views'] == old['output_views'], 'All96 exact outgoing views')
    source_views = {r['port']: r for r in old['input_views']}
    inputs = [{**r, 'field': r['port']} for r in old['input_views']]
    inputs += [{**source_views[p], 'role': 'selected_target', 'field': 112+p,
                'source_entry_port': p} for p in P]
    need(word['input_views'] == inputs, 'Copied source adapters bound to actual target fields')
    need(len({r['field'] for r in inputs}) == 128, 'Distinct charged input view fields')
    count = trace(word)
    need(count == {1: 1392, 2: 64, 3: 48, 8: 16}, 'Complete reuse native profile')
    scalars = [event[1] for event in word['events'] if event[0] == 'scalar']
    expected = review.unit(640)
    for p in range(112):
        review.add(expected[112+p], ce[p] if p in P else e[p])
    columns = review.reverse(scalars, 640)
    need(columns == review.transpose(expected, 640), 'All640 arbitrary input columns')
    for p in P:
        need(columns[112+p] == {112+p: F(1)}, 'Independent selected record preserved exactly')
    actual, bound = review.prefix(scalars, 640)
    need(actual == expected and actual[224:] == review.unit(640)[224:],
         'Separate forward map and arbitrary outside fields')
    need(bound == {'row_one_norm': '112', 'binary_height': 1}, 'Complete local content bounds')
    need(review.price(scalars) == 9880, 'Complete reuse scalar invoice')
    need(review.price([e[1] for e in kept if e[0] == 'scalar']) == 6456 and
         review.price([e[1] for e in query if e[0] == 'scalar']) == 3424, 'Both scalar stages')
    bad = dict(word)
    bad['start'] = list(word['start'])
    bad['start'][112+P[0]] = 0
    try:
        trace(bad)
    except ValueError:
        pass
    else:
        raise ValueError('Wrong selected I-frame control')
    need(review.reverse([e[1] for e in kept if e[0] == 'scalar'], 640) != columns,
         'Omitted late-query control')
    return {
        'input_columns': 640, 'arbitrary_selected_records': 16, 'unchanged_arbitrary_roles': 416,
        'events': len(word['events']), 'native_profile': dict(sorted(count.items())),
        'native_children': sum(count.values()), 'native_mass': sum(k*v for k, v in count.items()),
        'real_scalar_primitives': 9880, 'retained_scalar_primitives': 6456,
        'late_query_scalar_primitives': 3424, 'input_views': 128, 'output_views': 96,
        'native_side_maps_upper_bound': 3040, 'new_fields': 0, 'private_fields': 0,
        'odd_scans': 0, 'growth': bound, 'inherited_distinct_recipes': len(inherited),
        'fresh_distinct_recipes': len(fresh),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    frozen(PREVIOUS, 'FREEZE.json',
           '488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532')
    frozen(SOURCE, 'LINE-ENTRY-REUSE-FREEZE.json',
           'a8e212f9cd3cc7ac4a020737ba4889c04a7ae6124877cf770b9555f6f3e54f60')
    original = json.loads(read(SOURCE/'run-normal/PRODUCTIVE-CAPTURE.json.gz',
                               '7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2', True))
    payload = json.loads(read(SOURCE/'reuse-normal/LINE-ENTRY-REUSE.json.gz',
                              'efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110', True))
    need(payload['source_decompressed_sha256'] ==
         '7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2',
         'Exact formation source')
    need(payload['schema'] == 'productive-sixteen-line-entry-reuse-v1', 'Reuse schema')
    need(payload['selected_ports'] == P and payload['ports'] == original['ports'] and
         payload['ordinary_ports'] == original['ordinary_ports'], 'Actual ordered ports')
    need(payload['response'] == original['response'] and
         payload['selected_query_response'] == original['captured_response'],
         'Same local reader response')
    need(set(payload['providers']) == {'base', 'extra'} and
         payload['providers']['base'] == payload['providers']['extra'], 'Both exact providers')
    e, ce = review.rows(payload['response']), review.rows(payload['selected_query_response'])
    reports = {name: check_word(word, original['providers'][name], e, ce)
               for name, word in payload['providers'].items()}
    phase = review.inherit()
    word = payload['providers']['base']
    full = [('C', 1 << j, 1) for j in range(9)]
    checks = []
    for p in P:
        frame = word['start'][112+p]
        native = phase.recipe(word['native_recipes']['capture-line:'+str(p)])
        result = phase.compare(phase.canonical(word['frames'][frame])+native,
                               full, 'Exact selected line progress '+str(p), 512)
        checks.append({'port': p, 'frame': frame, **result})
    first = P[0]
    frame = word['start'][112+first]
    bad = phase.canonical(word['frames'][frame])+phase.recipe(
        word['native_recipes']['capture-line:'+str(first)])+phase.compile_circuit([['phase', 1]])
    need(phase.run(bad, 0) != phase.run(full, 0), 'Wrong global phase control')
    raw = json.loads(read(review.RAW/'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
                          'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4', True))
    inverse = review.rows(raw['model']['response_inverse'])
    need(review.mul(e, inverse) == review.unit(112) and
         review.mul(inverse, e) == review.unit(112), 'Actual invertible response')
    report = {
        'status': 'PASS_INDEPENDENT_LOCAL_LINE_ENTRY_REUSE',
        'literal_words': reports, 'fresh_phase_checks': checks,
        'exact_response_inverse_orders': True,
        'negative_controls': ['wrong selected I input frame', 'omitted late query', 'wrong global phase'],
        'reader_scope': 'The required update for a stored reader L is L E. Since E is invertible, equality with W E on all inputs requires L=W. No routed reader change is priced here.',
        'scope': 'Complete local arbitrary-record reuse with the same reader, exact physical phases, and local invoice. No routed past-reader query, full caller, recursive host, or supplier claim.',
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [('REVIEW.json', report), ('INPUTS.json', review.INPUTS)]:
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
