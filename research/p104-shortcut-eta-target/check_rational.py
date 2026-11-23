#!/usr/bin/env python3
"""Compare the old and five-shortcut 1291-output maps exactly over Q.

Each rational DAG row is converted to an integer linear circuit with a known
positive denominator and an absolute coefficient bound. For 64 inputs at a
time, signed integer digits in a base larger than the worst possible
cross-multiplied coefficient encode all basis vectors simultaneously. A zero
packed integer implies every signed coefficient is zero by reduction modulo
the base, so this is an exact identity, not a random or modular test.
"""
from argparse import ArgumentParser
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys
import time

ap = ArgumentParser()
ap.add_argument('runtime', type=Path)
ap.add_argument('--preflight', action='store_true')
ap.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'rational-identity-receipt.json')
args = ap.parse_args()
runtime = args.runtime.resolve()
sys.path.insert(0, str(runtime))
from upstream import install
install()
from strong_complex import digest, load_changed, WORD, SHORTCUT_WORD
from sparse_helpers import rebuild

started = datetime.now(timezone.utc)
clock = time.monotonic()
new, layout = load_changed(runtime / 'inputs')
from verify_split_helpers import read, reconstruct
parent, _ = rebuild()
old, _ = reconstruct(parent, read('BANK-FACTORS.json.gz'))
assert digest(old) == WORD == '38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb'
assert digest(new) == SHORTCUT_WORD == 'ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35'
assert all(old[k] == new[k] for k in ('initial', 'final', 'frames', 'first_output'))
n = len(new['initial'])
assert n == len(new['final']) == 1291
first = new['first_output']
inputs = [~i for i in range(n)]
outputs = [first + i for i in range(n)]

def build(graph):
    order = graph['schedule']
    rows = {k: row for k, row in graph['forms']}
    moves = {k: (a, b) for k, a, b in graph['moves']}
    assert len(rows) == len(order) and len(set(order)) == len(order)
    assert set(order) == set(rows) == set(moves) | set(outputs)
    chart = dict(zip(inputs, graph['initial'], strict=True))
    denom = dict.fromkeys(inputs, 1)
    mass = dict.fromkeys(inputs, 1)
    code = []
    terms = 0
    for k in order:
        a, b = moves[k] if k in moves else (graph['final'][k - first],) * 2
        assert all(chart[s] == a for s, _ in rows[k]), ('donor chart', k)
        scaled = [(s, Fraction(c) / denom[s]) for s, c in rows[k]]
        d = lcm(*(v.denominator for _, v in scaled))
        weights = [(s, v.numerator * (d // v.denominator)) for s, v in scaled]
        divisor = gcd(d, *(abs(v) for _, v in weights))
        d //= divisor
        weights = [(s, v // divisor) for s, v in weights]
        denom[k] = d
        mass[k] = sum(abs(v) * mass[s] for s, v in weights)
        chart[k] = b
        code.append((k, weights))
        terms += len(weights)
    return {'code': code, 'denom': denom, 'mass': mass, 'rows': rows, 'moves': moves, 'terms': terms}

before = build(old)
after = build(new)
assert len(before['moves']) == 5674 and len(after['moves']) == 5669
limit = max(after['denom'][o] * before['mass'][o] + before['denom'][o] * after['mass'][o] for o in outputs)
bits = max(1, limit.bit_length() + 1)
common = set(before['rows']) & set(after['rows'])
def normalized(row):
    return tuple((s, Fraction(c)) for s, c in row)

modified_rows = sorted(k for k in common if normalized(before['rows'][k]) != normalized(after['rows'][k]))
old_only = sorted(set(before['moves']) - set(after['moves']))
new_only = sorted(set(after['moves']) - set(before['moves']))
changed_moves = sorted(k for k in set(before['moves']) & set(after['moves']) if before['moves'][k] != after['moves'][k])
report = {'started_at': started.isoformat(), 'old_graph_sha256': digest(old), 'new_graph_sha256': digest(new),
          'roles': n, 'old_moves': len(before['moves']), 'new_moves': len(after['moves']),
          'old_form_terms': before['terms'], 'new_form_terms': after['terms'],
          'changed_common_rows': len(modified_rows), 'removed_move_labels': old_only,
          'new_move_labels': new_only, 'changed_move_labels': changed_moves,
          'digit_bits': bits, 'coefficient_bound_bits': limit.bit_length(),
          'runtime': str(runtime), 'word_file_sha256': sha256((runtime / 'w5669_shortcut5.json.gz').read_bytes()).hexdigest()}
if args.preflight:
    report['preflight_only'] = True
    print(json.dumps(report, sort_keys=True), flush=True)
    raise SystemExit(0)

def evaluate(prog, start, stop):
    values = dict.fromkeys(inputs, 0)
    for i in range(start, stop):
        values[~i] = 1 << (bits * (i - start))
    for k, weights in prog['code']:
        values[k] = sum(values[s] * v for s, v in weights)
    return values

blocks = 0
for start in range(0, n, 64):
    stop = min(n, start + 64)
    a, b = evaluate(before, start, stop), evaluate(after, start, stop)
    for o in outputs:
        if a[o] * after['denom'][o] != b[o] * before['denom'][o]:
            raise ArithmeticError(f'exact rational output {o}, block {start}')
    blocks += 1

# Increase one real output coefficient by one, choosing a donor that is
# nonzero on an actual basis block. No source file is altered.
found = None
for start in range(0, n, 64):
    stop = min(n, start + 64)
    b = evaluate(after, start, stop)
    for output in outputs:
        source = next((s for s, _ in after['rows'][output] if b[s]), None)
        if source is not None:
            found = output, source, start, stop, b
            break
    if found:
        break
assert found is not None
output, source, start, stop, b = found
a = evaluate(before, start, stop)
changed_num = b[output] * after['denom'][source] + b[source] * after['denom'][output]
assert changed_num * before['denom'][output] != a[output] * after['denom'][output] * after['denom'][source]
report.update({'preflight_only': False, 'input_blocks': blocks, 'matrix_entries': n * n,
               'all_exact_outputs_match': True, 'modified_output_negative_control_rejected': True,
               'negative_control_output': output, 'negative_control_donor': source,
               'negative_control_input_block': [start, stop],
               'finished_at': datetime.now(timezone.utc).isoformat(),
               'elapsed_seconds': round(time.monotonic() - clock, 6),
               'scope': 'Full rational forward map equality; all-column phase, compilation, ownership, physical cost and signed outer recovery remain separate obligations.'})
out = args.output.resolve()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print('PASS_RATIONAL_1291_OUTPUT_IDENTITY', json.dumps(report, sort_keys=True), flush=True)
