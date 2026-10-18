"""Replay the clean-ancilla register check.

Quick mode (about one minute) compiles the engine, checks that its dirty mode
reproduces the merged PR #1882 digest byte for byte, reruns the n=2 and n=3
clean searches with positive and failure controls, and runs the symbolic,
physical-realization and clean-only controls.  ``--full`` adds the clean
six-call positive control, the complete n=3, s=4 symbolic comparison and the
n=4 exhaustive clean search (about 2.5 hours).

Terminal lines are streamed through SHA-256 rather than stored, because the
clean n=4 and s=6 runs emit tens of gigabytes.

Usage: python3 -B research/bit-clean-ancilla-registers/verify.py
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

DIRTY_EXPECTED = ROOT.parent / 'bit-dirty-auxiliary-registers' / 'EXPECTED.json'

# name, (n, W, s), flags, keep all lines in memory
QUICK = [
    ('dirty_n3_w2_s5_regression', (3, 2, 5), [], False),
    ('clean_n2_w2_s5', (2, 2, 5), ['clean'], True),
    ('clean_n3_w2_s4', (3, 2, 4), ['clean'], True),
    ('clean_n3_w2_s5', (3, 2, 5), ['clean'], True),
    ('clean_n3_w1_s3_positive', (3, 1, 3), ['clean'], False),
    ('clean_n3_w2_s5_rank2_control', (3, 2, 5), ['clean', 'rank2-control'], False),
]
FULL = [
    ('clean_n3_w2_s6_positive', (3, 2, 6), ['clean'], False),
    ('clean_n4_w2_s5', (4, 2, 5), ['clean'], False),
]
SAMPLE_EVERY = 1000


def run_engine(binary, args, flags, keep):
    """Run the engine, streaming its terminal lines through SHA-256."""
    read_fd, write_fd = os.pipe()
    command = [str(binary), *map(str, args), f'/dev/fd/{write_fd}', *flags]
    start = time.time()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            pass_fds=(write_fd,), text=True)
    os.close(write_fd)
    h, lines, sample, count, flagged = sha256(), [], [], 0, 0
    with os.fdopen(read_fd, 'rb') as stream:
        for raw in stream:
            h.update(raw)
            line = raw.decode().rstrip('\n')
            flagged += line.startswith('1 ')
            if keep:
                lines.append(line)
            elif count % SAMPLE_EVERY == 0:
                sample.append(line)
            count += 1
    out, err = proc.communicate()
    if proc.returncode:
        raise RuntimeError(f'engine failed: {command}\n{err}')
    summary = json.loads(out)
    assert summary['diagonal_terminals'] == count, (summary, count)
    assert summary['candidates'] == flagged, (summary, flagged)
    summary['terminals_sha256'] = h.hexdigest()
    summary['seconds'] = round(time.time() - start, 1)
    return summary, (lines if keep else sample)


def check_run(name, summary, expected):
    if name not in expected['runs']:
        # Only while first recording a new run; replays require every entry.
        assert os.environ.get('CLEAN_ANCILLA_RECORDING') == '1', f'{name} missing from EXPECTED.json'
        return
    for key, value in expected['runs'][name].items():
        assert summary[key] == value, (name, key, summary[key], value)


def rejects(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except AssertionError:
        return True
    return False


def checker_controls(lines5):
    """Tampered engine output must be rejected by the Python checks."""
    first = next(line for line in lines5 if line.startswith('0 '))
    flag, word, r, reps = controls.parse_terminal(first)
    dropped = [line for line in lines5 if line != first]
    altered = reps[:]
    altered[0] ^= 1 << (len(word) - 1)
    rewritten = ' '.join(['0', *map(str, word), '|',
                          *(map(str, r) if r else ['0']), '|', *map(str, altered)])
    flagged = '1' + first[1:]
    # a dirty-only line (three representatives) is not a clean terminal record
    padded = first + ' 0'
    out = {
        'dropped_terminal_rejected': rejects(controls.compare_symbolic, dropped, 3, 2, 5, [tuple(word)]),
        'altered_representative_rejected': rejects(controls.realize_terminals, [rewritten], 3, 2, 1),
        'false_candidate_flag_rejected': rejects(controls.realize_terminals, [flagged], 3, 2, 1),
        'wrong_arity_rejected': rejects(controls.realize_terminals, [padded], 3, 2, 1),
    }
    assert all(out.values()), out
    return out


def replay(directory, full):
    expected = json.loads((ROOT / 'EXPECTED.json').read_text())
    dirty_expected = json.loads(DIRTY_EXPECTED.read_text())['runs']['n3_w2_s5']
    compiler = os.environ.get('CXX', 'c++')
    binary = directory / 'engine'
    subprocess.run([compiler, '-O3', '-std=c++17', str(ROOT / 'engine.cpp'), '-o', str(binary)],
                   check=True)
    runs, lines = {}, {}
    for name, args, flags, keep in QUICK + (FULL if full else []):
        summary, kept = run_engine(binary, args, flags, keep)
        check_run(name, summary, expected)
        runs[name], lines[name] = summary, kept

    # The dirty mode is the merged PR #1882 engine, byte for byte on output.
    regression = runs['dirty_n3_w2_s5_regression']
    for key, value in dirty_expected.items():
        assert regression[key] == value, ('PR1882 regression', key)
    assert regression['clean_only_terminals'] == 0

    # Semantic expectations, stated independently of the recorded digests.
    shapes = {q[0]: q[1] for q in QUICK + FULL}
    for name in ('clean_n2_w2_s5', 'clean_n3_w2_s4', 'clean_n3_w2_s5') + \
            (('clean_n4_w2_s5',) if full else ()):
        n, w, s = shapes[name]
        assert runs[name]['words'] == len(controls.projectors(n)) ** s
        assert runs[name]['candidates'] == 0
    assert runs['clean_n2_w2_s5']['clean_only_terminals'] == 0  # no auxiliary
    assert runs['clean_n3_w2_s5']['clean_only_terminals'] > 0   # relaxation is used
    assert runs['clean_n3_w2_s5']['diagonal_terminals'] > regression['diagonal_terminals']
    assert runs['clean_n3_w1_s3_positive']['candidates'] > 0
    assert runs['clean_n3_w2_s5_rank2_control']['candidates'] > 0
    if full:
        assert runs['clean_n3_w2_s6_positive']['candidates'] > 0
        assert runs['clean_n4_w2_s5']['clean_only_terminals'] > 0

    result = {'runs': runs,
              'pr1882_formal_controls': controls.dirty.check_formal_controls(),
              'clean_only_control': controls.clean_only_control()}
    lines5 = lines['clean_n3_w2_s5']
    result['realized_terminals_n3_s5'] = controls.realize_terminals(lines5[::5000], 3, 2, 300)
    result['realized_clean_only_n3_s5'] = controls.realize_terminals(
        lines5[1::997], 3, 2, 300, require_clean_only=True)
    assert result['realized_terminals_n3_s5'] == 300
    assert result['realized_clean_only_n3_s5'] == 300
    if full:
        sample4 = lines['clean_n4_w2_s5']
        result['realized_clean_only_n4_s5'] = controls.realize_terminals(
            sample4, 4, 2, 300, require_clean_only=True)
        assert result['realized_clean_only_n4_s5'] == 300

    result['symbolic_words_n2_s5'] = controls.compare_symbolic(
        lines['clean_n2_w2_s5'], 2, 2, 5, list(product(range(6), repeat=5)))
    sample = [word for index, word in enumerate(product(range(28), repeat=5)) if index % 5000 == 0]
    sample += sorted({tuple(controls.parse_terminal(line)[1]) for line in lines5[::20000]})
    result['symbolic_words_n3_s5_sample'] = controls.compare_symbolic(lines5, 3, 2, 5, sample)
    words4 = list(product(range(28), repeat=4))
    result['symbolic_words_n3_s4'] = controls.compare_symbolic(
        lines['clean_n3_w2_s4'], 3, 2, 4, words4 if full else words4[::31])
    result['checker_controls'] = checker_controls(lines5)
    result['mode'] = 'full' if full else 'quick'
    result['environment'] = {'python': platform.python_version(), 'platform': platform.platform(),
                             'compiler': compiler}
    result['status'] = 'PASS_CLEAN_ANCILLA_SIX_CALLS'
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
