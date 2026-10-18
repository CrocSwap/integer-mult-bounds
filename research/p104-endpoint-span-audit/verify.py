#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Finite premises and exact profile screens for the endpoint-span proof.

Hiroki Kumazaki (kumagi), with substantial OpenAI Codex assistance.
Credited geometry: Arham Tahir's PR2675 verifier. Credited cost engine:
Douglas Colkitt, with Claude assistance. See PROOF.md for the universal step;
this finite replay is not an enumeration of correction networks.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SELECTED_A = Q(67018507072324140917, 40000000000000000000000)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def authenticated_sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    sources = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'],
             'source hash: ' + row['path'])
        sources[row['path']] = data
    return sources


def source_module(sources, path, name):
    # Execute the authenticated bytes themselves; never read a source-adjacent
    # bytecode cache. These pinned modules import only the standard library.
    module = ModuleType(name)
    module.__file__ = str(ROOT / path)
    exec(compile(sources[path], module.__file__, 'exec'), module.__dict__)
    return module


def endpoint_weights(jumps):
    need(bool(jumps) and all(type(x) is int and x > 0 for x in jumps)
         and sum(jumps) == 9, 'complete positive dimension history')
    previous = 0
    arrival = departure = 0
    for jump in jumps:
        current = previous + jump
        if current == 8:
            arrival = previous
        if previous == 1:
            departure = 9 - current
        previous = current
    return arrival, departure


def screen(histogram, histories):
    need(all(type(n) is int and n >= 0 for n in histogram.values()),
         'nonnegative integer lifetime counts')
    cuts = [0] * 9
    endpoints = [0, 0]
    local = Counter()
    for index, number in histogram.items():
        jumps, column = histories[index]
        for rank in jumps:
            local[rank] += number
        for i, value in enumerate(column):
            cuts[i] += number * value
        for i, value in enumerate(endpoint_weights(jumps)):
            endpoints[i] += number * value
    return cuts, endpoints, local


def upper_decimal(value):
    scale = 10**15
    numerator = -((-value.numerator * scale) // value.denominator)
    return f'{numerator // scale}.{numerator % scale:015d}'


def main():
    sources = authenticated_sources()
    assembly = json.loads(sources['research/community-frontier1094-audit/ASSEMBLY.json'])
    need(Q(assembly['complex_lower']) == SELECTED_A, 'selected saving binding')
    predecessor = source_module(sources, 'research/p104-coupled-profile-budget/verify.py',
                                'credited_geometry')
    cost = source_module(sources, 'research/complex-local-word-ceiling/ceiling.py',
                         'credited_cost')
    witness = json.loads(sources['research/p104-native-channel/inputs/LOWRANK-WITNESS.json'])
    fixture = json.loads(sources['research/p104-native-channel/inputs/P104-FIXTURE.json'])
    for event in witness['program']:
        need(event[0] in {'add', 'copy', 'zero', 'erase', 'transport'}, 'known instruction')
        if event[0] in {'add', 'copy'}:
            need(not event[1].startswith('X') and not event[2].startswith('Y'),
                 'immutable sources and unread targets')
        elif event[0] in {'zero', 'erase'}:
            need(not event[1].startswith(('X', 'Y')), 'no data-field creation or erasure')
    need(all(len(witness['final_frames'][f'X{s}']) == 9 for s in range(104))
         and all(witness['initial_frames'][f'Y{t}'] == [] for t in range(104)),
         'FULL source ends and ZERO target starts')
    finite = predecessor.geometry(witness, fixture)
    need(finite['departure_lines'] == finite['arrival_hyperplanes'] == 104,
         '104 endpoints on each side')
    histories = predecessor.histories()
    need(len(histories) == 256 and len({tuple(h) for h, _ in histories}) == 256,
         'all positive compositions of nine')
    for jumps, _ in histories:
        a, d = endpoint_weights(jumps)
        need(0 <= a <= 7 and 0 <= d <= 7, 'endpoint weight range')
        need(endpoint_weights(jumps[::-1]) == (d, a), 'annihilator reversal')
    controls = {(8, 1): (0, 0), (1, 8): (0, 0), (1, 1, 7): (0, 7),
                (7, 1, 1): (7, 0), (1, 1, 6, 1): (2, 7),
                (1, 6, 1, 1): (7, 2), (1, 7, 1): (1, 1),
                (1,) * 9: (7, 7)}
    for history, expected in controls.items():
        need(endpoint_weights(history) == expected, 'endpoint control ' + str(history))
    need(histories[129][0] == [1, 7, 1] and histories[255][0] == [1] * 9,
         'predecessor profile index binding')
    results = []
    for label, cheap, full, expected, should_pass in [
        ('historical_208', 137, 71, 634, False),
        ('adversarial_400', 329, 71, 826, False),
        ('necessary_screen_control_406', 335, 71, 832, True),
    ]:
        counts, endpoints, extra = screen({129: cheap, 255: full}, histories)
        lifetimes = cheap + full
        need(counts[:7] == [cheap + 64 * full] * 7 and counts[7:] == [lifetimes] * 2,
             'old capacity totals')
        need(all(c >= b for c, b in zip(counts, predecessor.RHS, strict=True)),
             'predecessor necessary rows')
        need(endpoints == [expected, expected], 'endpoint totals')
        need(all(x >= 832 for x in endpoints) == should_pass, 'new screen verdict')
        if label != 'historical_208':
            need(387 <= lifetimes <= 482 and lifetimes >= max(219, 234, 216, 250),
                 'reported count floors and investigation window')
        need(sum(r * n for r, n in extra.items()) == 9 * lifetimes <= 4344,
             'complete lifetime mass within ideal budget')
        local = Counter(predecessor.BASE)
        local.update(extra)
        lo, hi = cost.relax(local, 73, 832, 9, 56, SELECTED_A)
        need(0 < lo <= hi < 1, 'strict favorable selected-budget relaxation')
        results.append({'profile': label, 'lifetimes': lifetimes,
                        'cut_capacities': counts[:7], 'endpoint_counts': counts[7:],
                        'arrival_dimension': endpoints[0], 'departure_codimension': endpoints[1],
                        'endpoint_requirement': 832, 'new_rows_pass': should_pass,
                        'ideal_idle_mass': 4344 - 9 * lifetimes,
                        'relaxation_upper': upper_decimal(hi)})
    print(json.dumps({'finite_premises': finite, 'histories_checked': 256,
                      'profiles': results}, indent=2))
    print('PASS_P104_ENDPOINT_SPAN_AUDIT histories=256 rejected=400 control=406')


if __name__ == '__main__':
    main()
