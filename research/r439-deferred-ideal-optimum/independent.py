#!/usr/bin/env python3
"""Backward coefficient-cone and Boolean truth-table audit, no verifier imports.
Apache-2.0. Substantial OpenAI Codex assistance; not independent human review.
"""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(value, label):
    if not value:
        raise RuntimeError(label)


def pullback(row, gates):
    """Apply a row functional backward through the circuit."""
    support = set(row)
    for d, s in reversed(gates):
        if d in support:
            support.symmetric_difference_update((s,))
    return support


def evaluate(support, source_rows):
    result = [0] * 9
    for k in support:
        for j in source_rows[k]:
            result[j] ^= 1
    return sum(b << j for j, b in enumerate(result))


def two_gate_matrix(a, b):
    labels = set(a + b)
    rows = {i: {i} for i in labels}
    for d, s in (a, b):
        rows[d] = rows[d] ^ rows[s]
    return rows


def audit():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    source = next(x for x in pins['files'] if x['usage'] == 'input')
    raw = (ROOT / source['path']).read_bytes()
    check(hashlib.sha256(raw).hexdigest() == source['sha256'], 'source pin')
    word = json.loads(gzip.decompress(raw))
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
    v = word['v']
    preparation, undo = [], []
    reading = False
    for frame, dest, sources in word['D']:
        if dest not in range(v, 2*v):
            continue
        if all(s in range(2*v, 2*v + word['R']) for s in sources):
            reading = True
        else:
            check(frame == 0 and len(sources) == 1 and sources[0] in range(v, 2*v), 'target gate')
            (undo if reading else preparation).append((dest-v, sources[0]-v))
    check(len(undo) == 306 and preparation == undo[::-1], 'circuit pin')
    # No forward row-state traversal is used to reconstruct these coefficients.
    initial = [evaluate(pullback((d,), preparation), word['scatter']) for d in range(v)]
    coefficients = [evaluate(pullback((s,), preparation + undo[:i]), word['scatter'])
                    for i, (_, s) in enumerate(undo)]
    check(initial == certificate['initial_rows'], 'backward initial rows')
    check(coefficients == certificate['increments'], 'backward gate coefficients')
    # Reconstruct noncommutation by literal multiplication of tiny matrices.
    deps = {(i, j) for i, a in enumerate(undo) for j, b in enumerate(undo[:i])
            if two_gate_matrix(a, b) != two_gate_matrix(b, a)}
    check(len(deps) == 850, 'matrix commutator count')
    check(all(tuple(x) in deps for x in certificate['essential_dependencies']), 'essential matrix commutators')
    lower = []
    weights = {}
    variables = {}
    total = 0
    for row in range(v):
        gates = [i for i, (d, _) in enumerate(undo) if d == row]
        assignments = 1 << len(gates)
        all_bits = (1 << assignments) - 1
        # A truth table is one integer whose bits enumerate all gate choices.
        variables[row] = {g: sum(((a >> k) & 1) << a for a in range(assignments))
                          for k, g in enumerate(gates)}
        columns = []
        for b in range(9):
            truth = all_bits if initial[row] >> b & 1 else 0
            for g in gates:
                if coefficients[g] >> b & 1:
                    truth ^= variables[row][g]
            columns.append(truth)
        ws = [sum((column >> a) & 1 for column in columns) for a in range(assignments)]
        weights[row] = ws
        lower.append(min(ws))
        total += assignments
        check(min(ws) == certificate['row_certificates'][row]['minimum'], 'independent row minimum')
        check(assignments == certificate['row_certificates'][row]['subsets'], 'independent row coverage')
    for row, gate, threshold in ((47,47,2),(68,93,2),(93,39,2)):
        check(all(w >= threshold or (variables[row][gate] >> a & 1)
                  for a,w in enumerate(weights[row])), 'saving implies gate')
    for row, gate, threshold in ((96,6,4),(6,36,2)):
        check(all(not (variables[row][gate] >> a & 1) or w >= threshold
                  for a,w in enumerate(weights[row])), 'gate forces cost')
    others = set(range(v)) - {24,28,47,96,68,93,6}
    # Rebuild the sum-of-groups lower bound, independently of the stored 94.
    result = sum(lower[d] for d in others) + lower[24] + lower[28] + 4 + 4
    check(result == 94 and total == 1386, 'global certificate arithmetic')
    chosen = {31,51,52}
    check(all(i not in chosen or j in chosen for i,j in deps), 'attaining ideal')
    first = [g for i,g in enumerate(undo) if i in chosen]
    rest = [g for i,g in enumerate(undo) if i not in chosen]
    for d in range(v):
        check(pullback((d,), first+rest) == pullback((d,), undo), 'commuted undo matrix')
    final = [evaluate(pullback((d,), preparation+first),word['scatter']) for d in range(v)]
    check(sum(x.bit_count() for x in final) == result, 'backward sharpness')
    # A relaxed cheaper assignment must fail the matrix-derived ideal condition.
    relaxed = chosen | {47}
    relaxed_rows = initial.copy()
    for g in relaxed:
        relaxed_rows[undo[g][0]] ^= coefficients[g]
    check(sum(x.bit_count() for x in relaxed_rows) == 93, 'relaxed control cost')
    check(any(i in relaxed and j not in relaxed for i,j in deps), 'reject relaxed control')
    print('PASS_INDEPENDENT_IDEAL_AUDIT backward_coefficients=417 row_subsets=1386 matrix_dependencies=850 minimum=94')


if __name__ == '__main__':
    audit()
