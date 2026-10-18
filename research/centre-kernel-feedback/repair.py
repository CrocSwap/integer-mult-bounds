#!/usr/bin/env python3
"""Explicit source-preserving repair generator in a rational field-bank model.
Tekalign, substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok: raise ValueError(why)


def word():
    reference = json.loads(gzip.decompress((HERE/'pr2799-result.json.gz').read_bytes()))
    kernel = [{int(j): F(q) for j, q in row.items()}
              for row in reference['readouts']['Y']['noncoordinate_kernel_basis']]
    correction = {int(j): {int(k): F(q) for k, q in row.items()}
                  for j, row in json.loads((HERE/'CORRECTION.json').read_text()).items()}
    # The orientation at each chronological site is committed in the correction receipt.
    orientations = json.loads((HERE/'RESULT.json').read_text())['call_orientations']
    operations = []
    for group, exponent in [('P', 1), ('M', -1)]:
        for k in range(21):
            w, z = (group, k), ('Z', k)
            operations.extend([('add', w, z, F(1)), ('oracle', w, exponent), ('add', w, z, F(-1))])
    setup = len(operations)
    def weighted(dst, src, q):
        if q in (1, -1): operations.append(('add', dst, src, q))
        else:
            scratch = ('S', 0)
            operations.extend([('add', scratch, src, F(1)), ('scale', scratch, q),
                               ('add', dst, scratch, F(1)), ('scale', scratch, 1/q),
                               ('add', scratch, src, F(-1))])
    injections = []
    for j in range(1152):
        start = len(operations)
        for k, row in enumerate(kernel):
            if j in row: weighted(('E', j), ('Z', k), row[j])
        group = 'P' if orientations[j//8] == 'forward' else 'M'
        for k, q in correction.get(j, {}).items(): weighted(('E', j), (group, k), -q)
        injections.append((start, len(operations)))
    cleanup = len(operations)
    for group, exponent in [('M', -1), ('P', 1)]:
        for k in reversed(range(21)):
            w, z = (group, k), ('Z', k)
            operations.extend([('add', w, z, F(1)), ('oracle', w, -exponent), ('add', w, z, F(-1))])
    return operations, setup, cleanup, injections, kernel, correction, orientations


def verify(mutation=None):
    operations, setup, cleanup, injections, kernel, correction, orientations = word()
    if mutation == 'omit-cleanup': operations = operations[:cleanup]
    if mutation == 'wrong-oracle':
        operations = list(operations)
        j = next(i for i, op in enumerate(operations) if op[0] == 'oracle')
        operations[j] = ('oracle', operations[j][1], -operations[j][2])
    # Free Laurent module: each H^a Z_k is an independent formal term.
    # This checks the entire word for an arbitrary invertible linear H.
    state = {('Z', k): {('Z', k, 0): F(1)} for k in range(21)}
    state.update({('E', j): {('E', j, 0): F(1)} for j in range(1152)})
    state.update({(group, k): {} for group in ('P', 'M') for k in range(21)})
    state['S', 0] = {}
    original = {k: dict(v) for k, v in state.items()}
    def merge(left, right, q):
        out = dict(left)
        for k, value in right.items():
            new = out.get(k, 0)+q*value
            if new: out[k] = new
            else: out.pop(k, None)
        return out
    def shift(row, exponent):
        return {(role, k, a+exponent): q for (role, k, a), q in row.items()}
    counts = Counter()
    boundaries = {end for start, end in injections}
    for number, op in enumerate(operations):
        name, dst = op[:2];counts[name] += 1
        need(dst[0] != 'Z', 'read-only source at every prefix')
        if name == 'add': state[dst] = merge(state[dst], state[op[2]], op[3])
        elif name == 'scale': state[dst] = {k: q*op[2] for k, q in state[dst].items()}
        else:
            need(name == 'oracle', 'known repair op')
            state[dst] = shift(state[dst], op[2])
            counts['H' if op[2] == 1 else 'H_inverse'] += 1
        if number+1 in boundaries:
            need(not state['S', 0], 'scratch restored at every centre boundary')
    for j in range(1152):
        expected = dict(original['E', j])
        for k, row in enumerate(kernel):
            if j in row: expected = merge(expected, original['Z', k], row[j])
        exponent = 1 if orientations[j//8] == 'forward' else -1
        for k, q in correction.get(j, {}).items():
            dz = merge(shift(original['Z', k], exponent), original['Z', k], -1)
            expected = merge(expected, dz, -q)
        need(state['E', j] == expected, 'complete dirty injection map')
    need(all(state['Z', k] == original['Z', k] for k in range(21)), 'source restoration')
    need(all(not value for key, value in state.items() if key[0] in ('P', 'M', 'S')),
         'all clean work restored')
    result = dict(oracle_H=counts['H'], oracle_H_inverse=counts['H_inverse'],
                  signed_unit_adds=counts['add'], rational_scales=counts['scale'],
                  clean_work_fields=43, source_fields=21, total_instructions=len(operations),
                  formal_dirty_injection_targets=1152, source_written_at_any_prefix=False)
    need(result == json.loads((HERE/'RESULT.json').read_text())['expanded_repair_invoice'], 'expanded invoice')
    print('PASS_SOURCE_PRESERVING_KERNEL_REPAIR', json.dumps(result, sort_keys=True))


if __name__ == '__main__': verify()
