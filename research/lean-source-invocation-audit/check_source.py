#!/usr/bin/env python3
"""Offline source binding and independent normalized replay for PR442.

Checks the actual forward invocation, owners, frame annotations and private
temporary. It binds every generated Lean event to the original binary records.
This Python parser/replay is not kernel verified. Physical chart realization
and the source's written coordinate-isometry interface remain separate.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parent
PIN = '4e16d001d505d4f21dd2bcfc44591f9be4c279bd'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def literal_events(path, expected, receipt):
    """Read literal data, with no execution of the generator or Lean source."""
    source = path.read_text()
    matches = list(re.finditer(
        r'^def chunk(\d+) : List Event := \[(.*?)\]', source, re.M | re.S))
    projection = receipt['lean_event_projection']
    count, size = projection['chunk_count'], projection['chunk_size']
    require([int(m.group(1)) for m in matches] == list(range(count)),
            'Lean chunks are missing, repeated or reordered')
    events = []
    for number, match in enumerate(matches):
        body = match.group(2)
        fields = list(re.finditer(r'⟨(\d+),(\d+),(\d+),(true|false)⟩', body))
        residue = re.sub(r'⟨\d+,\d+,\d+,(?:true|false)⟩', '', body)
        require(not residue.replace(',', '').strip(), 'Unexpected nonliteral Lean event data')
        wanted_length = size if number + 1 < count else projection['last_chunk_size']
        require(len(fields) == wanted_length, 'Lean chunk length differs')
        events.extend([[int(m.group(1)), int(m.group(2)), int(m.group(3)),
                        m.group(4) == 'true'] for m in fields])
    chunks = re.search(r'^def chunks : List \(List Event\) := \[(.*?)\]',
                       source, re.M | re.S)
    require(chunks is not None and
            chunks.group(1).replace(' ', '').replace('\n', '').split(',') ==
            ['chunk' + str(i) for i in range(count)],
            'Lean evaluator chunk list differs')
    require(events == [[e[0], e[1], e[2], bool(e[3] & 1)] for e in expected],
            'Lean event projection differs from the actual source word')
    return len(events)


def scalar_replay(events, states, frames):
    """All 987 independent columns at once; no upstream replay code imported."""
    live = 987
    require(states['n'] == live and states['v'] == 120 and states['R'] == 747 and
            states['h'] == 8, 'Source word dimensions differ')
    current = [states['initial'][str(i)] for i in range(live)] + [-1]
    rows = [1 << i for i in range(live)] + [0]
    center = None
    copies = erases = 0
    for position, event in enumerate(events):
        op = event[0]
        context = ' at event ' + str(position)
        if op == 0:
            _, role, old, new, rank, reverse = event
            require(0 <= role < live and reverse == 0 and current[role] == old,
                    'MOVE state mismatch' + context)
            require(frames[str(new)]['dim'] - frames[str(old)]['dim'] == rank >= 0,
                    'MOVE rank mismatch' + context)
            require(center != role, 'Open center moved' + context)
            current[role] = new
        elif op == 1:
            _, destination, source, coefficient, frame, reverse = event
            require(0 <= destination < live and 0 <= source <= live and
                    destination != source and reverse == 0,
                    'Invalid ADD operand' + context)
            require(current[destination] == current[source] == frame,
                    'ADD frame mismatch' + context)
            require(center != destination and (source != live or center is not None),
                    'ADD violates private-center lifetime' + context)
            if coefficient & 1:
                rows[destination] ^= rows[source]
        elif op == 2:
            _, source, temporary, old, new, rank, reverse = event
            require(0 <= source < live and temporary == live and reverse == 0 and
                    center is None and rows[temporary] == 0 and current[source] == old,
                    'COPY precondition mismatch' + context)
            require(abs(frames[str(old)]['dim'] - frames[str(new)]['dim']) == rank == 8,
                    'COPY rank mismatch' + context)
            center = source
            current[temporary] = new
            rows[temporary] = rows[source]
            copies += 1
        elif op == 3:
            _, source, temporary, old, new, rank, reverse = event
            require(0 <= source < live and temporary == live and reverse == 0 and
                    rank == 0 and center == source and current[source] == old and
                    current[temporary] == new and rows[temporary] == rows[source],
                    'ERASE precondition mismatch' + context)
            center = None
            current[temporary] = -1
            rows[temporary] = 0
            erases += 1
        else:
            raise ValueError('Unknown opcode' + context)
    expected = [(1 << i) ^ ((1 << (i - 120)) if 120 <= i < 240 else 0)
                for i in range(live)] + [0]
    require(rows == expected, 'Normalized all-column endpoint differs')
    require(current[:live] == [states['final'][str(i)] for i in range(live)] and
            center is None and rows[live] == 0 and copies == erases == 9,
            'Final frame or scratch-lifetime mismatch')
    return {'independent_columns_checked': live, 'copy_erase_episodes': copies,
            'temporary_final_value': rows[live]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--hosted-template', required=True, type=Path)
    parser.add_argument('--parent-template', required=True, type=Path)
    parser.add_argument('--states', required=True, type=Path)
    parser.add_argument('--frames', required=True, type=Path)
    parser.add_argument('--records', required=True, type=Path)
    parser.add_argument('--receipt', type=Path, default=ROOT / 'invocation-source.json')
    parser.add_argument('--lean-source', type=Path, default=ROOT / 'SourceWord.lean')
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_bytes())
    require(receipt['source_commit'] == PIN and receipt['source_pr'] == 442,
            'Unexpected pinned source revision')
    for relative, expected in receipt['source_files_sha256'].items():
        require(digest((args.source_root / relative).read_bytes()) == expected,
                'Pinned source hash mismatch: ' + relative)
    data = {}
    for key in ['hosted_template', 'parent_template', 'states', 'frames', 'records']:
        raw = getattr(args, key).read_bytes()
        if key.endswith('template'):
            # Raw JSON is authoritative; gzip headers/encoders may differ.
            raw = gzip.decompress(raw)
            require(digest(raw) == receipt['inputs'][key]['json_sha256'],
                    'Raw template hash mismatch: ' + key)
        else:
            require(digest(raw) == receipt['inputs'][key]['sha256'], 'Input hash mismatch: ' + key)
        data[key] = raw if key == 'records' else json.loads(raw)
    hosted, parent = data['hosted_template'], data['parent_template']
    states, frames = data['states'], data['frames']['frames']
    require(len(data['records']) % 24 == 0, 'Binary record size mismatch')
    rebuilt = []
    for op, x, y, c, f, z in struct.iter_unpack('<6i', data['records']):
        if op in (0, 1):
            rebuilt.append([op, x, y, c, f, 0])
        elif op == 2:
            rank = abs(frames[str(c)]['dim'] - frames[str(f)]['dim'])
            require(z == rank, 'Binary COPY charge differs from emitted rank')
            rebuilt.append([op, x, y, c, f, rank, 0])
        elif op == 3:
            rebuilt.append([op, x, y, c, f, z, 0])
        else:
            raise ValueError('Unknown binary record opcode')
    require(rebuilt == hosted['local_programs']['forward'] == parent['local_programs']['forward'],
            'Literal forward instructions differ from source records or parent')
    require(len(rebuilt) == receipt['event_count'] == 19002 and
            {str(k): v for k, v in Counter(e[0] for e in rebuilt).items()} == receipt['event_counts'],
            'Instruction counts differ')
    require(digest(json.dumps(rebuilt, separators=(',', ':')).encode()) ==
            receipt['forward_program_sha256'], 'Literal forward program hash differs')

    selected = receipt['selected_call']
    require(selected == {'stage': 2, 'replica': 0, 'pair': 0, 'orientation': 'forward'},
            'Selected invocation differs')
    calls = []
    for template in [hosted, parent]:
        candidates = [c for c in template['calls'] if c['stage'] == 2 and c['replica'] == 0]
        require(len(candidates) == 1, 'Selected call is missing or duplicated')
        call = candidates[0]
        require(all(call[key] == value for key, value in selected.items()) and
                len(call['owners']) == 987, 'Selected call descriptor differs')
        calls.append(call)
    new, old = calls
    for helper in receipt['selected_helpers']:
        register = helper['register']
        require(register == helper['helper'] + 240 and helper['helper'] in (0, 3),
                'Selected helper/register differs')
        require(new['owners'][register] == helper['hosted_owner'] and
                old['owners'][register] == helper['parent_owner'], 'Selected owner differs')
        require(states['initial'][str(register)] == helper['initial_frame'] == 0 and
                states['final'][str(register)] == helper['final_frame'] == 1 and
                helper['initial_dimension'] == 0 and helper['final_dimension'] == 8,
                'Selected helper frame endpoints differ')
    require([h['helper'] for h in receipt['selected_helpers']] == [0, 3],
            'Both selected helpers are required')
    require(frames['0'] == receipt['selected_frame0'] ==
            {'A': [[int(i == j) for j in range(8)] for i in range(8)], 'B': [], 'dim': 0} and
            frames['1'] == receipt['selected_frame1'] ==
            {'A': [], 'B': [[2 * int(i == j) for j in range(8)] for i in range(8)], 'dim': 8},
            'Selected zero/full frame bases differ')
    require(receipt['parent_absent_families'] == [507, 508], 'Retained family pair differs')
    for family in [507, 508]:
        require(all(owner[0] != family for owner in old['owners']),
                'Parent invocation touches retained family ' + str(family))
        require([[i, owner] for i, owner in enumerate(new['owners']) if owner[0] == family] ==
                receipt['hosted_family_rows'][str(family)], 'Hosted retained-family owner set differs')
    require(sum(owner[1][0] == 'hosted' for owner in new['owners'][240:]) ==
            receipt['hosted_helpers_count'] == 747 and
            len({owner[0] for owner in new['owners'][240:] if owner[1][0] == 'hosted'}) ==
            receipt['hosted_helper_families_count'] == 317, 'Stage hosting totals differ')
    replay = scalar_replay(rebuilt, states, frames)
    count = literal_events(args.lean_source, rebuilt, receipt)
    print(json.dumps({'status': 'PASS_SOURCE_INVOCATION_BINDING', 'source_commit': PIN,
                      'literal_lean_events_checked': count,
                      'forward_program_sha256': receipt['forward_program_sha256'],
                      'selected_helpers': [0, 3], 'retained_families': [507, 508],
                      **replay,
                      'scope': 'Python source binding and normalized replay; no physical chart proof.'},
                     sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError, TypeError, EOFError, struct.error) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
