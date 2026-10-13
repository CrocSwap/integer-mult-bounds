#!/usr/bin/env python3
"""Check the frame-522 replacement independently of the search program.

Exact finite circuit evidence, not a formal multiplication proof.
Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
START, STOP, FRAME = 361, 404, 522
PINNED_PATHS = {
    SOURCE, CHECKER, EXPORTER, 'certificates/checkpoints/frontier799.json',
    'research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py',
    'research/e8-bit-carrier-skeleton/portable-include/bits/stdc++.h',
    *('research/e8-bit-carrier-skeleton/code/bit/checkers/' + name
      for name in ('legality_h.cpp', 'columns_h.cpp', 'columns_k.cpp', 'json.hpp')),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_pins():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    require(set(pins['sha256']) == PINNED_PATHS, 'incomplete source pin inventory')
    for path, expected in pins['sha256'].items():
        require(digest(ROOT / path) == expected, 'source pin mismatch: ' + path)
    return pins


def load_checker():
    spec = importlib.util.spec_from_file_location('pinned_r439_checker', ROOT / CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_operations(operations, registers, inputs, xor=False):
    values = dict(zip(registers, inputs))
    for destination, source in operations:
        require(destination in values and source in values and destination != source,
                'invalid block operand')
        if xor:
            values[destination] ^= values[source]
        else:
            values[destination] += values[source]
    return [values[r] for r in registers]


def columns(operations, registers):
    # Scalar execution on each unit input, separate from search.py's row matrices.
    return [run_operations(operations, registers,
                           [int(i == j) for i in range(len(registers))])
            for j in range(len(registers))]


def check_operations(operations, registers, expected):
    require(columns(operations, registers) == expected, 'integer block map mismatch')


def cleanup(word):
    v = word['v']
    full = next(i for i, f in enumerate(word['frames']) if len(f) == v)
    return [[full, d, list(srcs)] for _, d, srcs in
            reversed(word['A'] + word['B']) if not v <= d < 2 * v]


def frame_paths(word):
    paths = [[f] for f in word['start']]
    for section in 'DABC':
        for frame, destination, sources in word[section]:
            for register in [destination, *sources]:
                if paths[register][-1] != frame:
                    paths[register].append(frame)
    for register, frame in enumerate(word['final']):
        if paths[register][-1] != frame:
            paths[register].append(frame)
    return paths


def build_word(base, candidate):
    old = base['B'][START:STOP]
    registers = sorted({r for _, d, ss in old for r in [d, *ss]})
    require(all(f == FRAME and len(ss) == 1 for f, _, ss in old), 'base block shape')
    require(candidate['slice'] == [START, STOP] and candidate['frame'] == FRAME,
            'candidate location mismatch')
    require(candidate['registers'] == registers, 'candidate registers mismatch')
    require(candidate['source_sha256'] == digest(ROOT / SOURCE), 'candidate source mismatch')
    require(candidate['format'] == 'r439-block522-positive-factor-v1', 'candidate format')
    require(candidate['seed'] == 17 and candidate['trials'] == 12000, 'search domain changed')
    require(sum(candidate['gate_count_histogram'].values()) ==
            candidate['successful_identity_factorizations'] <= candidate['trials'],
            'search coverage counts inconsistent')
    old_ops = [(d, ss[0]) for _, d, ss in old]
    operations = candidate['operations']
    require(len(operations) == candidate['candidate_additions'] < len(old_ops),
            'candidate count is not a strict improvement')
    require(candidate['baseline_additions'] == len(old_ops), 'baseline count mismatch')
    expected = columns(old_ops, registers)
    check_operations(operations, registers, expected)
    word = copy.deepcopy(base)
    word['B'][START:STOP] = [[FRAME, d, [s]] for d, s in operations]
    word['C'] = cleanup(word)
    require(frame_paths(word) == frame_paths(base), 'register frame path changed')
    return word, registers, old_ops, expected


def write_word(word, path):
    raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(raw, mtime=0))


def export(word_path, directory):
    result = subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORTER),
                             str(word_path), str(directory)], capture_output=True, text=True)
    require(result.returncode == 0, 'pinned exporter failed: ' + result.stderr)
    data = (directory / '249-records.bin').read_bytes()
    require(len(data) % 24 == 0, 'record stream alignment')
    return list(struct.iter_unpack('<6i', data))


def audit_records(records, n, v):
    profile = Counter()
    scalar = []
    values = [1 << r for r in range(n)] + [0]
    opened = None
    copies = adds = moves = 0
    for op, a, b, c, f, z in records:
        require(0 <= a <= n, 'record destination range')
        if op == 0:
            moves += 1
            require(f >= 0, 'negative move rank')
            if f:
                profile[f] += 1
        elif op == 1:
            require(0 <= b <= n and a != b, 'record ADD operands')
            require(a < n and (b < n or opened is not None), 'inactive temporary')
            require(opened is None or a != opened, 'copied source mutated')
            if c % 2:
                values[a] ^= values[b]
            scalar.append(('add', a, b, abs(c)))
            adds += 1
        elif op == 2:
            require(opened is None and a < n and b == n, 'COPY lifecycle')
            opened = a
            values[n] = values[a]
            profile[z] += 1
            copies += 1
            scalar.append(('copy', n, a, 0))
        elif op == 3:
            require(opened == a and b == n, 'ERASE lifecycle')
            opened = None
            values[n] = 0
            scalar.append(('erase', n, a, 0))
        else:
            raise ValueError('unknown opcode')
    require(opened is None and copies == 9, 'copy count/closure')
    expected = [(1 << r) ^ ((1 << (r-v)) if v <= r < 2*v else 0)
                for r in range(n)] + [0]
    require(values == expected, 'exported all-column endpoint mismatch')
    bounds = []
    for reverse in (False, True):
        norms = [1] * (n+1)
        maximum = 1
        open_center = None
        for op, dst, src, coefficient in (reversed(scalar) if reverse else scalar):
            if reverse and op != 'add':
                op = 'erase' if op == 'copy' else 'copy'
            if op == 'add':
                norms[dst] += coefficient * norms[src]
                maximum = max(maximum, norms[dst])
            elif op == 'copy':
                require(open_center is None, 'positive COPY lifecycle')
                norms[dst] = norms[src]
                open_center = src
            else:
                require(open_center == src, 'positive ERASE lifecycle')
                norms[dst] = 0
                open_center = None
        require(open_center is None, 'positive copy closure')
        bounds.append(maximum)
    payload = 64 * bounds[0]**3 * bounds[1]**2
    require(payload < 2**104, 'native payload cap exceeded')
    return {'records': len(records), 'additions': adds, 'moves': moves,
            'copies': copies, 'columns': n,
            'paid_profile': {str(k): x for k, x in sorted(profile.items())},
            'rank_mass': sum(k*x for k, x in profile.items()),
            'forward_positive_bound': bounds[0], 'reverse_positive_bound': bounds[1],
            'payload_upper': str(payload), 'payload_bits': payload.bit_length()}


def controls(base, word, candidate, registers, expected, records):
    rejected = []

    def reject(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    ops = candidate['operations']
    reject('omitted_ADD', lambda: check_operations(ops[1:], registers, expected))
    reject('reversed_block', lambda: check_operations(list(reversed(ops)), registers, expected))
    switched = copy.deepcopy(ops)
    switched[0] = list(reversed(switched[0]))
    reject('reversed_operands', lambda: check_operations(switched, registers, expected))
    reordered = [ops[1], ops[0], *ops[2:]]
    reject('noncommuting_reorder', lambda: check_operations(reordered, registers, expected))
    doubled = [*ops, ops[0], ops[0]]
    require(run_operations(doubled, registers, [1 << i for i in range(12)], True)
            == run_operations(ops, registers, [1 << i for i in range(12)], True),
            'even-multiplicity control must preserve the F2 map')
    reject('F2_invisible_double_ADD', lambda: check_operations(doubled, registers, expected))
    reject('self_ADD', lambda: check_operations([[registers[0], registers[0]], *ops],
                                               registers, expected))
    reject('foreign_register', lambda: check_operations([[registers[0], 660], *ops],
                                                       registers, expected))
    bad = copy.deepcopy(word)
    bad['C'] = base['C']
    reject('stale_cleanup', lambda: require(bad['C'] == cleanup(bad), 'cleanup mismatch'))
    bad_frame = copy.deepcopy(word)
    bad_frame['B'][START][0] = 0
    reject('wrong_frame', lambda: require(frame_paths(bad_frame) == frame_paths(base),
                                         'register frame path changed'))
    copy_index = next(i for i, r in enumerate(records) if r[0] == 2)
    modified = list(records)
    center, temp = records[copy_index][1:3]
    modified.insert(copy_index+1, (1, center, temp, 1, 0, 3))
    reject('mutated_copied_source', lambda: audit_records(modified, 661, 111))
    omitted = [r for r in records if r[0] != 3]
    reject('omitted_ERASE', lambda: audit_records(omitted, 661, 111))
    return rejected


def verify(output):
    pins = check_pins()
    base = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    candidate = json.loads((HERE / 'CANDIDATE.json').read_text())
    word, registers, old_ops, expected = build_word(base, candidate)
    # Exhaustive table includes every local arbitrary-dirt assignment.
    for bits in range(1 << len(registers)):
        inputs = [(bits >> i) & 1 for i in range(len(registers))]
        require(run_operations(old_ops, registers, inputs, True)
                == run_operations(candidate['operations'], registers, inputs, True),
                'Boolean truth table mismatch')
    checker = load_checker()
    reports, record_sets = {}, {}
    output.mkdir(parents=True, exist_ok=False)
    for name, current in [('baseline', base), ('candidate', word)]:
        path = output / (name + '.json.gz')
        write_word(current, path)
        audited, labels, full, hypotheses, conclusions, _ = checker.check(current)
        require(all(hypotheses.values()) and all(conclusions.values()), 'H1-H5 interface failed')
        require(full['columns'] == 661 and len(audited.punct) == 9, 'interface dimensions')
        require([t['rank'] for t in full['totals']] == [7]*9, 'COPY ranks changed')
        records = export(path, output / (name + '-records'))
        record_sets[name] = records
        reports[name] = audit_records(records, 661, 111)
        (output / (name + '-interface.json')).write_text(json.dumps({
            'hypotheses': hypotheses, 'conclusions': conclusions,
            'columns': full['columns'], 'copy_ranks': [7]*9,
            'labels': labels}, sort_keys=True, indent=2) + '\n')
    old, new = reports['baseline'], reports['candidate']
    for key in ('paid_profile', 'rank_mass', 'moves', 'copies', 'columns'):
        require(old[key] == new[key], 'changed complete invoice field: ' + key)
    require(old['additions'] - new['additions'] == 2*(43-len(candidate['operations'])),
            'complete ADD savings do not include cleanup')
    require(new['forward_positive_bound'] <= old['forward_positive_bound'],
            'forward bound grew despite positive-map preservation')
    reverse_old = columns(list(reversed(old_ops)), registers)
    reverse_new = columns(list(reversed(candidate['operations'])), registers)
    reverses = {'entrywise_dominated': all(a <= b for r, s in zip(reverse_new, reverse_old)
                                          for a, b in zip(r, s)),
                'old_entry_sum': sum(map(sum, reverse_old)),
                'new_entry_sum': sum(map(sum, reverse_new))}
    require(reverses['new_entry_sum'] == candidate['reverse_matrix_entry_sum'],
            'candidate reverse metric mismatch')
    result = {'status': 'PASS_R439_BLOCK522_FACTOR', 'base_commit': pins['base_commit'],
              'source_word_sha256': digest(ROOT / SOURCE),
              'candidate_sha256': digest(HERE / 'CANDIDATE.json'),
              'block_frame': FRAME, 'block_columns': len(registers),
              'boolean_inputs': 1 << len(registers), 'integer_columns': expected,
              'all_register_frame_paths_identical': True,
              'H1_H5_and_conclusions': True, 'reverse_block': reverses,
              'baseline': old, 'candidate': new,
              'controls_rejected': controls(base, word, candidate, registers, expected,
                                            record_sets['candidate']),
              'new_kappa_claimed': False}
    (output / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh directory; default temporary')
    parser.add_argument('--write-expected', action='store_true', help='explicit receipt regeneration')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='r439-block522-') as temp:
        result = verify(args.output or Path(temp) / 'replay')
    expected = HERE / 'EXPECTED.json'
    if args.write_expected:
        expected.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(result == json.loads(expected.read_text()), 'committed receipt mismatch')
    print('PASS_R439_BLOCK522_FACTOR gates=43->33 ADDs=%d->%d columns=661 controls=%d '
          'rank_mass=%d no_new_kappa' % (result['baseline']['additions'],
          result['candidate']['additions'], len(result['controls_rejected']),
          result['candidate']['rank_mass']))


if __name__ == '__main__':
    main()
