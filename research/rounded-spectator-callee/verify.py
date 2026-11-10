#!/usr/bin/env python3
"""Check actual rounded row calls, zero return and the next diagonal."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
B = runpy.run_path(str(HERE / 'backend.py'))
W, N = B['WRAPPER'], B['NATIVE']
need = B['need']


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def exact_column(values, n, bits):
    """Apply the defining Gaussian pair matrix in physical coordinates."""
    out = [(F(a), F(b)) for a, b in values]
    for bit in bits:
        stride = 1 << (n - 1 - bit)
        changed = list(out)
        for index in range(len(out)):
            if index & stride:
                continue
            a, b = out[index]
            c, d = out[index | stride]
            changed[index] = ((a - b + c + d) / 2, (a + b - c + d) / 2)
            changed[index | stride] = ((a + b + c - d) / 2, (-a + b + c + d) / 2)
        out = changed
    return out


def squared_error(left, right):
    return max((F(a) - c) ** 2 + (F(b) - d) ** 2
               for (a, b), (c, d) in zip(left, right))


def case(n, selected, K, Q, seed, P=3, H=2, mode='dirty'):
    f = len(selected) // K
    g = P + (f + 1) // 2 + 1
    rng = random.Random(seed)
    cap = 1 << (H + g - 1)
    values = [(rng.randrange(-cap, cap + 1), rng.randrange(-cap, cap + 1))
              for _ in range(1 << n)]
    if mode == 'zero':
        values = [(0, 0)] * len(values)
    elif mode == 'basis':
        values = [(0, 0)] * len(values)
        values[seed % len(values)] = (1 << g, 0)
    before = list(values)
    output, receipt, p = B['execute'](values, n, selected, K, 1, Q, P, H, cycle=seed)
    need(values == before, 'Reference input is not overwritten')
    ideal = exact_column(values, n, selected[::K])
    source = W['wrapped']([(F(a), F(b)) for a, b in values], p)
    need(source == ideal, 'Exact predecessor equals the physical-coordinate formula')
    error = squared_error(output, ideal)
    need(error < F(2) ** (2 * (g - P)), 'Completed-call tolerance')
    post = W['diagonal'](output, n, 7)
    ideal_post = W['diagonal'](ideal, n, 7)
    need(squared_error(post, ideal_post) == error, 'Next unit-phase diagonal preserves error')
    if mode == 'zero':
        need(all(value == (0, 0) for value in output) and receipt['rounding_events'] == 0,
             'Literal zero fixed point')
    if mode == 'basis':
        need(error == 0, 'Exactly represented basis-column control')
    receipt.update(n=n, selected=list(selected), K=K, Q=Q, seed=seed, mode=mode,
                   error_squared_grid_units=str(error),
                   output_sha256=sha256(canonical(output).encode()).hexdigest())
    return receipt


def controls():
    # The published actual cross-row port loop must fail zero-bank return.
    x = [(-1, -1)] + [(0, 0)] * 7
    y = [(0, 0)] * 8
    original = list(x)
    for reverse in (False, True):
        x, y, _, _ = N['port'](x, y, 1, 2, reverse, N['signed_width'](0, 4, 1, 2, reverse))
    need(x == original and y == [(0, -1) if i in (0, 5) else (0, 0) for i in range(8)],
         'Actual cross-row counterexample retained')
    # Wrong axis moves a passive coordinate instead of the active coordinate.
    v = [(32, 0)] + [(0, 0)] * 7
    a, b = list(v), list(v)
    N['call'](a, 1, 0, 20)
    N['call'](b, 1, 2, 20)
    need(a != b, 'Wrong native axis rejected')
    # A coarse diagonal before inverse exposure gives the wrong address labels.
    n, selected = 7, [0]
    p = W['plan'](n, selected, 1, 1, 3)
    values = [(F(i + 1), F(1 - 2 * i)) for i in range(1 << n)]
    correct = W['diagonal'](W['wrapped'](values, p), n, 7)
    early = W['wrapped'](values, p, diagonal_too_early=True)
    need(correct != early, 'Early coarse diagonal rejected')
    for args in (([(True, 0)] * (1 << n), n, selected, 1, 1, 3, 3, 2),
                 ([(1 << 20, 0)] * (1 << n), n, selected, 1, 1, 3, 3, 2),
                 ([(0, 0)] * ((1 << n) - 1), n, selected, 1, 1, 3, 3, 2)):
        try:
            B['execute'](*args)
        except ValueError:
            pass
        else:
            raise ValueError('An invalid input was accepted')
    try:
        N['call']([(1, 0)] * 8, 1, 0, 2)
    except ValueError:
        pass
    else:
        raise ValueError('Insufficient signed width was accepted')
    return {'cross_row_residual': y, 'wrong_axis': True, 'early_diagonal': True,
            'invalid_inputs': 3, 'overflow': True}


def source_controls():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = [row['path'] for row in pins['files'] if row['usage'] == 'input']
    with tempfile.TemporaryDirectory(prefix='rounded-row-source-') as directory:
        root = Path(directory)
        package = root / 'research/rounded-spectator-callee'
        package.mkdir(parents=True)
        for name in ('backend.py', 'SOURCES.json'):
            (package / name).write_bytes((HERE / name).read_bytes())
        for name in inputs:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((B['ROOT'] / name).read_bytes())
        command = [sys.executable, '-I', *(['-O'] if sys.flags.optimize else []),
                   '-B', str(package / 'backend.py')]
        good = subprocess.run(command, capture_output=True, text=True, timeout=20)
        need(good.returncode == 0, 'Copied source control must load')
        for name in inputs:
            path = root / name
            original = path.read_bytes()
            path.write_bytes(b"raise RuntimeError('changed source executed')\n")
            bad = subprocess.run(command, capture_output=True, text=True, timeout=20)
            need(bad.returncode != 0 and 'Source mismatch: ' + name in bad.stderr
                 and 'RuntimeError' not in bad.stderr, 'Changed source rejected before execution')
            path.write_bytes(original)
    return len(inputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = []
    for selected in range(7):
        result.append(case(7, [selected], 1, 3, selected + 1))
        result.append(case(7, [selected], 1, 3, selected + 1, mode='basis'))
    for selected in ([0, 9], [6, 7], [2, 5]):
        for seed in (1, 4, 7):
            result.append(case(10, selected, 1, 3, seed))
    for selected in ([0, 1], [3, 4], [6, 7]):
        result.append(case(8, selected, 2, 3, 11))
    for selected in ([0, 1, 2], [5, 6, 7], [9, 10, 11]):
        result.append(case(12, selected, 3, 3, 13))
    result.append(case(15, [0, 7, 14], 1, 5, 17))
    result.append(case(7, [0], 1, 3, 3, mode='zero'))
    result.append(case(6, [4], 1, 1, 5))
    for precision, magnitude in ((0, 0), (0, 4), (4, 16), (31, 10)):
        result.append(case(7, [6], 1, 3, 19, P=precision, H=magnitude))
    need(sum(row['rounding_events'] for row in result) > 0, 'Actual rounding is exercised')
    receipt = {'schema_version': 1, 'fixtures': result, 'controls': controls(),
               'source_mutation_controls': source_controls(),
               'fixture_count': len(result),
               'padded_zeros_checked': sum(row['padded_coordinates_checked_zero'] for row in result),
               'butterflies': sum(row['butterflies'] for row in result)}
    receipt = json.loads(json.dumps(receipt))
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(receipt == json.loads((HERE / 'RESULT.json').read_text()), 'Stored result mismatch')
    print('PASS_ROUNDED_SPECTATOR_CALLEE', receipt['fixture_count'],
          'fixtures;', receipt['padded_zeros_checked'], 'exact padded zeros;',
          receipt['butterflies'], 'literal paid butterflies')


if __name__ == '__main__':
    main()
