#!/usr/bin/env python3
"""Independent set-valued finite F2 verification of the R480 Q-node2 recipe.

No search, primary verifier, exporter, or predecessor checker is imported.
The full-column check is finite linear algebra, not a proof of the conditional
multiplication theorem. Prepared for ToikY with substantial OpenAI Codex
assistance; Apache-2.0. Native record vocabulary follows Dylan Crow's PR249/
PR266 exporter, and signed-prefix convention follows the retained PR503 checker.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
SOURCE_SHA256 = '92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c'
WIRES = [17, 25, 32, 43, 52, 58, 64, 77, 82, 90, 99, 104]
OBJECT = {'phase': 'A', 'slice_start_inclusive': 2250,
          'slice_end_exclusive': 2302, 'frame': 484,
          'registers_in_matrix_order': WIRES}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def rows_after(gates, labels):
    """Each row is a set of independently named input variables."""
    rows = {i: {i} for i in labels}
    for _, d, sources in gates:
        for s in sources:
            rows[d] = rows[d].symmetric_difference(rows[s])
    return [sorted(rows[i]) for i in labels]


def check_local(old, new, advertised):
    for event in new:
        need(type(event) is list and len(event) == 3, 'recipe event shape')
        f, d, ss = event
        need(type(f) is int and f == 484, 'recipe common frame')
        need(type(d) is int and d in WIRES, 'recipe destination')
        need(type(ss) is list and len(ss) == 1, 'one source per recipe gate')
        need(type(ss[0]) is int and ss[0] in WIRES and ss[0] != d,
             'recipe source or alias')
    old_rows, new_rows = rows_after(old, WIRES), rows_after(new, WIRES)
    need(old_rows == new_rows, 'twelve arbitrary-input rows changed')
    masks = [sum(1 << WIRES.index(s) for s in r) for r in new_rows]
    need(type(advertised) is list and all(type(x) is int for x in advertised)
         and masks == advertised, 'advertised local matrix differs')
    need(rows_after(new + list(reversed(new)), WIRES) == [[s] for s in WIRES],
         'literal reverse does not restore all input rows')
    # A scalar truth-table implementation, distinct from the symbolic sets.
    def execute(gates, assignment):
        state = {s: (assignment >> i) & 1 for i, s in enumerate(WIRES)}
        for _, d, ss in gates:
            for s in ss:
                state[d] ^= state[s]
        return state
    for assignment in range(1 << len(WIRES)):
        want = execute(old, assignment)
        actual = execute(new, assignment)
        need(actual == want, f'Boolean assignment mismatch {assignment}')
        for _, d, ss in reversed(new):
            for s in ss:
                actual[d] ^= actual[s]
        need(actual == {s: (assignment >> i) & 1 for i, s in enumerate(WIRES)},
             f'Boolean inverse mismatch {assignment}')
    return masks


def basis(vectors):
    """Exact canonical rational row space; no producer rank routine."""
    result = []
    for vector in vectors:
        row = [Fraction(x) for x in vector]
        for pivot, b in result:
            scale = row[pivot]
            row = [x - scale*y for x, y in zip(row, b)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is None:
            continue
        scale = row[pivot]
        row = [x/scale for x in row]
        result = [(p, [x-b[pivot]*y for x, y in zip(b, row)]) for p, b in result]
        result.append((pivot, row))
        result.sort(key=lambda item: item[0])
    return tuple(tuple(row) for _, row in result)


def frame_spaces(word):
    return [basis(word['lines'][i] for i in frame) for frame in word['frames']]


def native_records(word, spaces):
    """Build and validate explicit MOVE/ADD/COPY/ERASE records independently."""
    n, v = 720, 120
    need(word['v'] == v and word['R'] == 480 and word['h'] == 8,
         'R480 dimensions')
    need(len(word['start']) == len(word['final']) == n, 'frame endpoint count')
    frames = list(word['start'])
    paths = [[f] for f in frames]
    records = []
    nested = {}
    def move(register, frame):
        old = frames[register]
        if old == frame:
            return
        pair = old, frame
        if pair not in nested:
            nested[pair] = (len(spaces[old]) < len(spaces[frame]) and
                            basis(spaces[old] + spaces[frame]) == spaces[frame])
        need(nested[pair], f'non-nested frame movement {register}: {old}->{frame}')
        records.append((0, register, old, frame,
                        len(spaces[frame])-len(spaces[old]), 0))
        frames[register] = frame
        paths[register].append(frame)
    def phase(name, tag):
        for f, d, ss in word[name]:
            need(type(f) is int and 0 <= f < len(spaces), 'frame range')
            operands = [d] + ss
            need(all(type(r) is int and 0 <= r < n for r in operands)
                 and len(set(operands)) == len(operands), 'word register or alias')
            if d < v or d >= 2*v:
                need(not any(v <= s < 2*v for s in ss), 'target feeds restored bank')
            if name == 'D':
                need(f == 0 and v <= d < 2*v and all(s >= 2*v for s in ss),
                     'dirty compensation interface')
            if name == 'A':
                need(not v <= d < 2*v, 'phase A writes target')
            if name == 'B':
                need(v <= d < 2*v, 'phase B does not write target')
            for r in operands:
                move(r, f)
            for s in ss:
                records.append((1, d, s, 1, f, tag))
    phase('D', 1)
    phase('A', 2)
    need(all(frames[r] == 0 for r in range(v, 2*v)), 'scatter target not at zero')
    for k, centre in enumerate(word['ret']):
        need(centre >= 2*v and len(spaces[frames[centre]]) == 8,
             'retained centre is not full-frame helper')
        frame = frames[centre]
        records.append((2, centre, n, frame, 0, len(spaces[frame])))
        for t, row in enumerate(word['scatter']):
            if k in row:
                records.append((1, v+t, n, 1, 0, 3))
        records.append((3, centre, n, frame, 0, 0))
    phase('B', 4)
    phase('C', 5)
    for r in range(n):
        move(r, word['final'][r])
    need(frames == word['final'], 'final frame mismatch')
    need(word['C'] == [[1, d, ss[:]] for _, d, ss in reversed(word['A'])],
         'cleanup is not the literal full-frame reverse')
    return records, paths


def replay(records, reverse=False, positive=False, zero_input=None):
    """All 720 independent columns; fresh copy is a snapshot, erase closes it.

    Reverse is the signed inverse's F2 reduction: reverse order, exchange COPY
    and ERASE, retain ADD destination/source (its integer coefficient is -1).
    Positive bounds drop coefficient signs and count all intermediate rows.
    """
    n = 720
    state = [1 if positive else {r} for r in range(n)]
    state.append(0 if positive else set())
    if zero_input is not None:
        state[zero_input] = 0 if positive else set()
    opened = None
    maximum = 1
    adds = copies = 0
    for rec in reversed(records) if reverse else records:
        op, a, b, c, frame, phase = rec
        if reverse and op in (2, 3):
            op = 5-op
        if op == 0:
            continue
        if op == 1:
            need(c == 1 and a != b and 0 <= a < n and 0 <= b <= n,
                 'malformed ADD')
            need(b != n or opened is not None, 'read closed copy')
            need(a != opened, 'copied original centre mutated')
            state[a] = state[a] + state[b] if positive else state[a] ^ state[b]
            if positive:
                maximum = max(maximum, state[a])
            adds += 1
        elif op == 2:
            need(opened is None and b == n and 0 <= a < n, 'copy lifecycle')
            state[n] = state[a] if positive else state[a].copy()
            opened = a
            copies += 1
        elif op == 3:
            need(opened == a and b == n and state[n] == state[a],
                 'erase source binding or copy modified')
            state[n] = 0 if positive else set()
            opened = None
        else:
            raise ValueError('unknown native opcode')
    need(opened is None and not state[n], 'unclosed private copy')
    if positive:
        return {'max_row_l1_upper': str(maximum), 'bits': maximum.bit_length(),
                'adds': adds, 'copies': copies}
    want = [{r} for r in range(n)]
    for t in range(120):
        want[120+t].add(t)
    need(state[:n] == want, 'whole-word 720-column endpoint mismatch')
    return digest([sorted(s) for s in state])


def fails(call, name):
    try:
        call()
    except (ValueError, KeyError, IndexError):
        return name
    raise ValueError('negative control unexpectedly accepted: ' + name)


def run(recipe_path=None, records_dir=None):
    raw = SOURCE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'source SHA256 mismatch')
    old = json.loads(gzip.decompress(raw))
    recipe = json.loads(Path(recipe_path or HERE / 'RECIPE.json').read_text())
    need(recipe['object'] == OBJECT, 'recipe object differs from claimed scope')
    new_gates = recipe['replacement_A_events']
    need(len(new_gates) == 43, 'frozen recipe gate count')
    local = old['A'][2250:2302]
    masks = check_local(local, new_gates, recipe['fixed_output_f2_rows'])
    new = copy.deepcopy(old)
    new['A'][2250:2302] = copy.deepcopy(new_gates)
    new['C'] = [[1, d, ss[:]] for _, d, ss in reversed(new['A'])]
    spaces = frame_spaces(old)
    before, old_paths = native_records(old, spaces)
    after, new_paths = native_records(new, spaces)
    need(old_paths == new_paths, 'one or more register frame paths changed')
    receipts = {}
    for name, records in [('original', before), ('replacement', after)]:
        endpoints = [replay(records, reverse=rev) for rev in (False, True)]
        need(endpoints[0] == endpoints[1], 'inverse F2 endpoint differs')
        positive = [replay(records, reverse=rev, positive=True) for rev in (False, True)]
        forward, backward = [int(p['max_row_l1_upper']) for p in positive]
        payload = 64 * forward**3 * backward**2
        receipts[name] = {'endpoint_sha256': endpoints[0],
                          'native_records': len(records),
                          'native_records_sha256': hashlib.sha256(b''.join(
                              struct.pack('<6i', *r) for r in records)).hexdigest(),
                          'positive_forward': positive[0], 'positive_reverse': positive[1],
                          'five_stage_payload_upper': str(payload),
                          'five_stage_payload_bits': payload.bit_length(),
                          'five_stage_payload_below_2pow104': payload < 2**104}
        if records_dir is not None:
            exported = Path(records_dir) / name / 'records/249-records.bin'
            data = exported.read_bytes()
            need(len(data) % 24 == 0, 'native record stream alignment')
            parsed = list(struct.iter_unpack('<6i', data))
            need(parsed == records, 'native exporter differs from independent records')
    need(receipts['original']['positive_forward']['adds'] -
         receipts['replacement']['positive_forward']['adds'] == 18,
         'complete-word saving differs from eighteen')
    # Every one-gate deletion must change the finite twelve-input map.
    want = rows_after(local, WIRES)
    for i in range(len(new_gates)):
        need(rows_after(new_gates[:i] + new_gates[i+1:], WIRES) != want,
             f'vacuous local deletion control {i}')
    controls = ['all_43_single_gate_deletions']
    swapped = want[:]
    swapped[0], swapped[1] = swapped[1], swapped[0]
    need(swapped != want, 'vacuous output permutation control')
    controls.append('swapped_output_rows')
    controls.append(fails(lambda: replay(after, zero_input=240), 'arbitrary_dirty_helper_assumed_zero'))
    controls.append(fails(lambda: replay(after, zero_input=WIRES[0]), 'arbitrary_source_assumed_zero'))
    controls.append(fails(lambda: replay(after, zero_input=120), 'arbitrary_target_assumed_zero'))
    for phase, name in [(1, 'missing_dirt_compensation_ADD'), (5, 'missing_cleanup_ADD')]:
        i = next(i for i, e in enumerate(after) if e[0] == 1 and e[5] == phase)
        controls.append(fails(lambda i=i: replay(after[:i] + after[i+1:]), name))
    wrong = copy.deepcopy(new)
    wrong['A'][2250][0] = 0
    controls.append(fails(lambda: native_records(wrong, spaces), 'wrong_local_frame'))
    i = next(i for i, e in enumerate(after) if e[0] == 3)
    controls.append(fails(lambda: replay(after[:i] + after[i+1:]), 'missing_private_ERASE'))
    return {'status': 'PASS_INDEPENDENT_R480_QNODE2', 'source_sha256': SOURCE_SHA256,
            'columns_checked': 720, 'arbitrary_dirty_helpers': 480,
            'arbitrary_targets': 120, 'local_Boolean_assignments': 4096,
            'local_rows': masks, 'register_frame_paths_checked': 720,
            'frame_paths_sha256': digest(old_paths), 'local_word_xor_saving': 18,
            'original': receipts['original'], 'replacement': receipts['replacement'],
            'controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', type=Path)
    parser.add_argument('--records-dir', type=Path,
                        help='optional root containing original/replacement/records exports')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = run(args.recipe, args.records_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('PASS_INDEPENDENT_R480_QNODE2 columns=720 Boolean=4096 '
              'frame_paths=720 saved=18 finite_F2_only')


if __name__ == '__main__':
    main()
