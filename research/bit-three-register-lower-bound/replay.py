"""Regenerate the scalar catalogue and run both complete exact searches."""

from collections import Counter
from contextlib import nullcontext
from hashlib import sha256
from math import factorial, prod
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import os
import subprocess
import time

from catalogue import catalogue
from controls import CORE_WORDS, check_formal_controls

ROOT = Path(__file__).resolve().parent


def run(command, log):
    with log.open('w') as output:
        result = subprocess.run(list(map(str, command)), stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Command failed: {command}\n{log.read_text()[-4000:]}')


def read_results(path, words):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    by_case = {row['case']: row for row in rows}
    assert len(rows) == len(by_case) == len(words)
    assert set(by_case) == set(range(len(words)))
    for case, word in enumerate(words):
        expected_orders = factorial(8) // prod(factorial(count) for count in Counter(word).values())
        assert by_case[case]['words'] == expected_orders
        assert by_case[case].get('nonmonomial_diagonal', 0) == 0
    return by_case


def replay(directory):
    directory.mkdir(parents=True, exist_ok=True)
    expected = json.loads((ROOT / 'expected.json').read_text())
    words, census = catalogue()
    # JSON normalizes the dimension keys to strings, as in the small record.
    census = json.loads(json.dumps(census))
    assert all(census[key] == value for key, value in expected.items() if key in census)
    input_path = directory / 'catalogue.txt'
    input_path.write_text(str(len(words)) + '\n' + ''.join(
        ' '.join(map(str, (case, *word))) + '\n' for case, word in enumerate(words)))
    assert sha256(input_path.read_bytes()).hexdigest() == expected['catalogue_sha256']
    formal_controls = check_formal_controls()
    compiler = os.environ.get('CXX', 'c++')
    for name in ('rational', 'f101'):
        run([compiler, '-O3', '-std=c++17', ROOT / f'{name}.cpp', '-o', directory / name],
            directory / f'{name}-compile.log')

    control_input = directory / 'controls.txt'
    control_input.write_text('2\n' + ''.join(
        ' '.join(map(str, (case, *word))) + '\n' for case, word in enumerate(CORE_WORDS)))
    control_output = directory / 'controls.jsonl'
    run([directory / 'f101', control_input, control_output], directory / 'controls.log')
    controls = read_results(control_output, CORE_WORDS)
    assert controls[0]['robust'] > 0 and controls[1]['robust'] == 0

    first = directory / 'rational-results.jsonl'
    second = directory / 'f101-results.jsonl'
    candidates = directory / 'candidates.txt'
    run([directory / 'rational', '--batch', input_path, first, candidates], directory / 'rational.log')
    run([directory / 'f101', input_path, second], directory / 'f101.log')
    rational, finite = read_results(first, words), read_results(second, words)
    assert candidates.read_text() == ''
    for case in rational:
        assert all(rational[case][key] == finite[case][key] for key in ('words', 'terminals', 'robust'))
    counts = {'families': len(words), 'orders': sum(row['words'] for row in rational.values()),
              'diagonal_terminals': sum(row['terminals'] for row in rational.values()),
              'survivors': sum(row['robust'] for row in rational.values())}
    assert all(value == expected[key] for key, value in counts.items())
    return {**counts, 'all_per_case_counts_agree': True, 'formal_controls': formal_controls,
            'core_positive_accepted': True, 'core_rank_two_mutation_rejected': True,
            'catalogue_sha256': sha256(input_path.read_bytes()).hexdigest(),
            'source_sha256': {name: sha256((ROOT / name).read_bytes()).hexdigest()
                              for name in ('catalogue.py', 'rational.cpp', 'f101.cpp')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, help='Keep generated inputs, binaries, and per-case results here')
    args = parser.parse_args()
    context = nullcontext(args.work_dir.resolve()) if args.work_dir else TemporaryDirectory(prefix='bit-three-register-')
    start = time.monotonic()
    with context as directory:
        result = replay(Path(directory))
        result['seconds'] = time.monotonic() - start
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
