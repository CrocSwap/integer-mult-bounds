#!/usr/bin/env python3
"""Full equivalence and fault controls for packed omission replay; stdlib only.

Apache-2.0. Sagar Thakrar, with substantial OpenAI Codex assistance.
"""

import argparse
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import platform
import random
from statistics import median
import sys
from time import perf_counter
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('packed_omission', HERE / 'replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
require = replay.require


def reject(name, operation, message):
    try:
        operation()
    except ValueError as error:
        require(message in str(error), name + ': wrong rejection: ' + str(error))
    else:
        raise ValueError(name + ': corruption accepted')
    return name


def check():
    old = replay.load_checker(False)
    gates = old.expand(old.load_inputs()[0])
    count = 0
    trace = sha256()
    for k, actual in enumerate(replay.packed_replays(gates, old.N)):
        expected = old.replay(gates, k)
        require(actual == expected, 'full literal matrix mismatch: ' + str(k))
        trace.update(old.canonical([str(row) for row in actual]) + b'\n')
        count += 1
    require(count == 5563, 'full literal omission coverage')

    # All short words plus deterministic long words cross complete and short batches.
    rng = random.Random(92)
    edges = [(d, s, 0, 0) for d in range(3) for s in range(3) if d != s]
    words = [word for length in range(5) for word in product(edges, repeat=length)]
    words += [tuple(rng.choice(edges) for _ in range(length))
              for length in (15, 16, 17, 31, 32, 33, 63, 64, 65)]
    for word in words:
        expected = [old.replay(word, k)[:3] for k in range(len(word))]
        for size in (1, 2, 3, 16, 64):
            require(list(replay.packed_replays(word, 3, size)) == expected,
                    'short-word or batch-boundary mismatch')

    literal = replay.audit(False)
    packed = replay.audit(True)
    require(old.canonical(packed) == old.canonical(literal), 'full audit result mismatch')
    controls = []
    for bad in (0, -1, True):
        controls.append(reject('invalid batch ' + str(bad),
                               lambda bad=bad: list(replay.packed_replays([], 3, bad)),
                               'positive batch size'))

    def corrupt_row(gates, width):
        for k, rows in enumerate(replay.packed_replays(gates, width)):
            if k == 16:
                rows[-1] ^= 1 << (width - 1)
            yield rows

    def duplicate_lane(gates, width):
        first = None
        for k, rows in enumerate(replay.packed_replays(gates, width)):
            if k == 0:
                first = rows
            yield first if k == 16 else rows

    def extra_lane(gates, width):
        yield from replay.packed_replays(gates, width)
        yield [0] * width

    def missing_lane(gates, width):
        for k, rows in enumerate(replay.packed_replays(gates, width)):
            if k < len(gates) - 1:
                yield rows

    def missing_row(gates, width):
        for rows in replay.packed_replays(gates, width):
            yield rows[:-1]

    for name, generator, message in (
        ('alter high input bit in helper output', corrupt_row, 'literal omission delta disagrees at 16'),
        ('repeat first omission at next batch', duplicate_lane, 'literal omission delta disagrees at 16'),
        ('extra omission map', extra_lane, 'extra literal omission replay'),
        ('missing last partial-batch lane', missing_lane, 'missing literal omission replay'),
        ('missing helper output row', missing_row, 'literal omission row coverage'),
    ):
        checker = replay.load_checker()
        checker.packed_replays = generator
        controls.append(reject(name, checker.run, message))

    original_read = Path.read_bytes
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        relative = pin['path']
        target = replay.ROOT / relative

        def changed(path, target=target):
            raw = original_read(path)
            return raw + b'\n' if path == target else raw

        with patch.object(Path, 'read_bytes', changed):
            controls.append(reject('pin ' + relative, replay.load_checker, 'source pin mismatch'))

    result = {
        'status': 'PASS_PACKED_OMISSION_EQUIVALENCE',
        'base_commit': pins['base_commit'], 'seed': 92, 'batch_size': replay.BATCH_SIZE,
        'full_mutant_matrices': count, 'rows_per_matrix': old.N, 'columns_per_matrix': old.N,
        'literal_matrix_stream_sha256': trace.hexdigest(),
        'complete_certificate_equal': True,
        'predecessor_certificate_canonical_sha256': sha256(old.canonical(packed)).hexdigest(),
        'short_words': len(words), 'short_word_batch_sizes': [1, 2, 3, 16, 64],
        'predecessor_controls': packed['controls_rejected'], 'new_controls': controls,
        'scope': 'Finite PR1017 omission replay only; no new kappa or full theorem proof.',
    }
    return result


def benchmark():
    times = {'literal': [], 'packed': []}
    # Alternate order; every timed call hashes inputs and checks the entire certificate.
    for round_number in range(5):
        for name in (('literal', 'packed') if round_number % 2 == 0 else ('packed', 'literal')):
            started = perf_counter()
            replay.audit(name == 'packed')
            times[name].append(perf_counter() - started)
    return {'python': sys.version, 'platform': platform.platform(),
            'times_seconds': times, 'median_speedup': median(times['literal']) / median(times['packed']),
            'scope': 'Same-process complete audit, source checks and certificate comparison; no timing threshold.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', action='store_true')
    args = parser.parse_args()
    result = check()
    expected_path = HERE / 'RESULT.json'
    expected = json.loads(expected_path.read_text(encoding='utf-8'))
    require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            'equivalence receipt mismatch')
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.benchmark:
        print(json.dumps(benchmark(), indent=2, sort_keys=True))
