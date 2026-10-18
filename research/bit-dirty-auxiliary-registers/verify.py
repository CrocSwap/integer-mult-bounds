"""Replay the dirty-auxiliary register check.

Quick mode (about one minute) compiles the engine, reruns the n=2 and n=3
five-call searches with their positive and failure controls, and runs the
symbolic, physical-realization and formal-identity controls.  ``--full`` adds
the six-call positive control, the complete n=3, s=4 symbolic comparison and
the n=4 exhaustive search (about 80 minutes).

Usage: python3 -B research/bit-dirty-auxiliary-registers/verify.py
           [--full] [--work-dir DIR] [--record PATH]
"""

from hashlib import sha256
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import controls  # noqa: E402

QUICK = [
    ('n2_w2_s5', (2, 2, 5), False),
    ('n3_w2_s4', (3, 2, 4), False),
    ('n3_w2_s5', (3, 2, 5), False),
    ('n3_w1_s3_positive', (3, 1, 3), False),
    ('n3_w2_s5_rank2_control', (3, 2, 5), True),
]
FULL = [
    ('n3_w2_s6_positive', (3, 2, 6), False),
    ('n4_w2_s5', (4, 2, 5), False),
]


def digest(path):
    h = sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def run_engine(binary, directory, name, args, rank2):
    out = directory / f'{name}.txt'
    command = [str(binary), *map(str, args), str(out)] + (['rank2-control'] if rank2 else [])
    start = time.time()
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'engine failed: {command}\n{result.stderr}')
    summary = json.loads(result.stdout)
    summary['terminals_sha256'] = digest(out)
    summary['seconds'] = round(time.time() - start, 1)
    return summary, out


def check_run(name, summary, expected):
    if name not in expected['runs']:
        # Only while first recording a new run; replays require every entry.
        assert os.environ.get('DIRTY_AUX_RECORDING') == '1', f'{name} missing from EXPECTED.json'
        return
    want = expected['runs'][name]
    for key, value in want.items():
        assert summary[key] == value, (name, key, summary[key], value)


def rejects(function, *args):
    try:
        function(*args)
    except AssertionError:
        return True
    return False


def checker_controls(lines5):
    """Tampered engine output must be rejected by the Python checks."""
    flag, word, r, reps = controls.parse_terminal(lines5[0])
    dropped = [line for line in lines5 if line != lines5[0]]
    altered = reps[:]
    altered[0] ^= 1 << (len(word) - 1)
    rewritten = ' '.join(['0', *map(str, word), '|',
                          *(map(str, r) if r else ['0']), '|', *map(str, altered)])
    flagged = '1' + lines5[0][1:]
    out = {
        'dropped_terminal_rejected': rejects(controls.compare_symbolic, dropped, 3, 5, [tuple(word)]),
        'altered_representative_rejected': rejects(controls.realize_terminals, [rewritten], 3, 1),
        'false_candidate_flag_rejected': rejects(controls.realize_terminals, [flagged], 3, 1),
    }
    assert all(out.values()), out
    return out


def replay(directory, full):
    expected = json.loads((ROOT / 'EXPECTED.json').read_text())
    compiler = os.environ.get('CXX', 'c++')
    binary = directory / 'engine'
    subprocess.run([compiler, '-O3', '-std=c++17', str(ROOT / 'engine.cpp'), '-o', str(binary)],
                   check=True)
    runs, files = {}, {}
    for name, args, rank2 in QUICK + (FULL if full else []):
        summary, path = run_engine(binary, directory, name, args, rank2)
        check_run(name, summary, expected)
        runs[name], files[name] = summary, path

    # Semantic expectations, stated independently of the recorded digests.
    for name in ('n2_w2_s5', 'n3_w2_s4', 'n3_w2_s5') + (('n4_w2_s5',) if full else ()):
        n, w, s = dict((q[0], q[1]) for q in QUICK + FULL)[name]
        assert runs[name]['words'] == len(controls.projectors(n)) ** s
        assert runs[name]['candidates'] == 0
    assert runs['n3_w2_s5']['aux_touching_terminals'] > 0
    assert runs['n3_w1_s3_positive']['candidates'] > 0
    assert runs['n3_w2_s5_rank2_control']['candidates'] > 0
    if full:
        assert runs['n3_w2_s6_positive']['candidates'] > 0
        assert runs['n4_w2_s5']['aux_touching_terminals'] > 0

    result = {'runs': runs, 'formal_controls': controls.check_formal_controls()}
    lines5 = files['n3_w2_s5'].read_text().splitlines()
    result['realized_terminals_n3_s5'] = controls.realize_terminals(lines5[::50], 3, 300)
    assert result['realized_terminals_n3_s5'] == 300

    lines = files['n2_w2_s5'].read_text().splitlines()
    result['symbolic_words_n2_s5'] = controls.compare_symbolic(
        lines, 2, 5, list(product(range(6), repeat=5)))
    all5 = product(range(28), repeat=5)
    sample = [word for index, word in enumerate(all5) if index % 500 == 0]
    sample += sorted({tuple(controls.parse_terminal(line)[1]) for line in lines5[::20]})
    result['symbolic_words_n3_s5_sample'] = controls.compare_symbolic(lines5, 3, 5, sample)
    lines4 = files['n3_w2_s4'].read_text().splitlines()
    words4 = list(product(range(28), repeat=4))
    result['symbolic_words_n3_s4'] = controls.compare_symbolic(
        lines4, 3, 4, words4 if full else words4[::31])
    result['checker_controls'] = checker_controls(lines5)
    result['mode'] = 'full' if full else 'quick'
    result['environment'] = {'python': platform.python_version(), 'platform': platform.platform(),
                             'compiler': compiler}
    result['status'] = 'PASS_DIRTY_AUXILIARY_SIX_CALLS'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--work-dir', type=Path)
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    if args.work_dir:
        args.work_dir.mkdir(parents=True, exist_ok=True)
        result = replay(args.work_dir, args.full)
    else:
        with TemporaryDirectory() as tmp:
            result = replay(Path(tmp), args.full)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.record:
        args.record.write_text(text)
    print(text, end='')
    print(result['status'])


if __name__ == '__main__':
    main()
