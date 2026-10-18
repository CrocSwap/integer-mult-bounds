# SPDX-License-Identifier: Apache-2.0
"""Credited gauge and method-baseline comparisons, without stacking savings.

conorholds, with substantial OpenAI Codex assistance.
The frozen schedules are George Lydakis's composition of the credited
PR1263/PR1369 gauges; their original notice is retained in comparators/pr1979.
The published PR1119 cleanup routines credit Stephan Arrington.
"""
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path

from network import add_price, event, price, require, sha, splice, strict_json
from cleanup import operator

HERE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def power(exponent):
    require(type(exponent) is int, 'comparison integer exponent')
    return Q(2**exponent) if exponent >= 0 else Q(1, 2**-exponent)


def inputs(upstream=None):
    manifest = strict_json((HERE / 'COMPARISON-SOURCES.json').read_bytes())
    require(set(manifest['files']) == {'GAUGES.json', 'MENU.json', 'EXPECTED.json', 'NOTICE.md'},
            'comparison source inventory')
    result = {}
    for name, row in manifest['files'].items():
        raw = (HERE / 'comparators/pr1979' / name).read_bytes()
        require(sha(raw) == row['sha256'], 'comparison source hash: '+name)
        if upstream is not None:
            require(sha((upstream / row['upstream_path']).read_bytes()) == row['sha256'],
                    'live comparison source: '+name)
        if name.endswith('.json'):
            result[name] = strict_json(raw)
    return result, manifest


def reconstruct(word, programs, sources):
    """Apply the published static gauges, then its nineteen temporal schedules."""
    out = {}
    for orientation, events in programs.items():
        gauges = {int(h): k for h, k in sources['GAUGES.json'][orientation].items()}
        schedules = {int(h): {int(i): k for i, k in values.items()}
                     for h, values in sources['MENU.json'][orientation].items()}
        require(len(schedules) == 19 and not gauges.keys() & schedules.keys(), 'comparison fixed menu')
        helpers = gauges.keys() | schedules.keys()
        require(all(2*word['v'] <= h < 2*word['v']+word['R'] and word['start'][h] == 0
                    and word['final'][h] == 1 for h in helpers), 'comparison helper eligibility')
        require(not any(e[0] == 'residual_adapter' and e[2] in helpers for e in events),
                'comparison unwrapped helpers')
        require(not any(e[0] == 'scalar' and e[1][0] in ('copy', 'clear') and
                        any(['L', h] in e[1][1:] for h in helpers) for e in events),
                'comparison COPY/CLEAR exclusion')
        require(events[-1] == ['phase', 'done'], 'comparison final boundary')
        def scale(h, k, frame):
            q = power(k)
            return ['scalar', ['scale', ['L', h], q.numerator, q.denominator], frame]
        def shift(event, values):
            if event[0] == 'scalar' and event[1][0] == 'add':
                gate = event[1]
                k = sum(sign*values.get(r[1], 0) for sign, r in zip((1, -1), gate[1:3]) if r[0] == 'L')
                q = Q(gate[3], gate[4])*power(k)
                gate[3:5] = [q.numerator, q.denominator]
        static = copy.deepcopy(events)
        for event in static:
            shift(event, gauges)
        static[1:1] = [scale(h, gauges[h], word['start'][h]) for h in sorted(gauges)]
        static[-1:-1] = [scale(h, -gauges[h], word['final'][h]) for h in sorted(gauges)]
        for h, schedule in schedules.items():
            incident = {i for i, e in enumerate(static) if e[0] == 'scalar' and e[1][0] == 'add'
                        and ['L', h] in e[1][1:3]}
            require(set(schedule) == incident, 'comparison complete incident schedule')
        current = dict.fromkeys(schedules, 0)
        frames = list(word['start']); candidate = []; pulses = []
        for index, original in enumerate(static):
            event = copy.deepcopy(original)
            for h in sorted(schedules):
                if index in schedules[h]:
                    change = schedules[h][index]-current[h]
                    if change:
                        require(frames[h] == event[2], 'comparison actual transition frame')
                        pulses.append([index, h, change, event[2], len(candidate)])
                        candidate.append(scale(h, change, event[2]))
                    current[h] = schedules[h][index]
            shift(event, current)
            if index == len(static)-1:
                for h in sorted(schedules):
                    if current[h]:
                        require(frames[h] == word['final'][h], 'comparison restoration frame')
                        pulses.append([index, h, -current[h], frames[h], len(candidate)])
                        candidate.append(scale(h, -current[h], frames[h]))
            candidate.append(event)
            if event[0] == 'climb':
                require(frames[event[2]] == event[3], 'comparison original frame edge')
                frames[event[2]] = event[4]
        require(pulses == sources['EXPECTED.json']['orientations'][orientation]['inserted_scales'],
                'comparison published transition receipt')
        require([e for e in candidate if e[0] != 'scalar'] == [e for e in events if e[0] != 'scalar'],
                'comparison unchanged non-scalar events')
        out[orientation] = candidate
    return out


def copy_unit_count(events):
    total = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        gate = event[1]
        if gate[0] == 'add':
            q = Q(gate[3], gate[4])
            total += add_price(q)-2-2*int(abs(q) == 1)
        elif gate[0] == 'scale':
            q = Q(gate[2], gate[3]); a, b = abs(q.numerator), q.denominator
            require(a and not a & (a-1) and not b & (b-1), 'comparison dyadic scale')
            total += 2*(abs(a.bit_length()-b.bit_length())+int(q < 0))
        else:
            require(gate[0] in ('clear', 'copy'), 'comparison scalar opcode')
            total += 2
    return total


def compare(word, programs, candidate, upstream=None):
    sources, manifest = inputs(upstream)
    published = reconstruct(word, programs, sources)
    raw = (HERE / 'comparators/pr1979/PROGRAMS.json.gz').read_bytes()
    require(sha(raw) == manifest['programs_sha256'], 'comparison literal stream hash')
    require(published == strict_json(gzip.decompress(raw)), 'comparison literal reconstruction')
    result = {}
    for orientation, events in published.items():
        expected = sources['EXPECTED.json']['orientations'][orientation]['all19_invoice']['complex_primitives']
        published_count = copy_unit_count(events)
        require(published_count == expected, 'comparison published primitive invoice')
        result[orientation] = dict(published_real=published_count, candidate_real=copy_unit_count(candidate[orientation]),
                                   saving_real=published_count-copy_unit_count(candidate[orientation]),
                                   published_program_sha256=sha(canonical(events)))
    return dict(pr=1979, orientations=result, composed_with_candidate=False,
                scope='Same frozen word, both orientations, PR696 copy/unit tariff; no sum of overlapping savings.')


def method_baselines(word, programs, forest, cleanup, candidate, upstream=None):
    """A two-by-two panel/cleanup comparison, holding the rest of the word fixed."""
    published = strict_json((HERE / 'METHOD-BASELINES.json').read_bytes())
    if upstream is not None:
        for row in published['files']:
            require(sha((upstream / row['path']).read_bytes()) == row['sha256'],
                    'live PR1119 comparison source: '+row['path'])
    gates = strict_json((HERE / 'PR1119-CLEANUP.json').read_bytes())
    require(sha(canonical(gates)) == published['cleanup_payload_sha256'], 'PR1119 cleanup payload binding')
    require(operator(word, gates) == operator(word, word['cleanup']), 'PR1119 cleanup complete operator')
    best = published['trials'][published['selected_trial']]
    require(sum(map(price, gates)) == best['horner_real'] and
            copy_unit_count([event(g) for g in gates]) == best['copy_unit_real'], 'PR1119 cleanup invoice')
    result = {}
    for name, panel, restoration in [('forest_current_cleanup', forest, cleanup),
                                     ('forest_published_cleanup', forest, gates),
                                     ('nonforest_published_cleanup', candidate, gates)]:
        result[name] = {}
        for orientation, stream in splice(word, programs, panel, restoration).items():
            horner = sum(price(e[1]) if e[1][0] in ('add', 'scale') else 2
                         for e in stream if e[0] == 'scalar')
            result[name][orientation] = dict(horner_real=horner, copy_unit_real=copy_unit_count(stream),
                                            macros=sum(e[0] == 'scalar' for e in stream),
                                            program_sha256=sha(canonical(stream)))
    return dict(programs=result, published_cleanup_trial=published['selected_trial'],
                scope='Our PR1080 reimplementation; published PR1119 routines at dimension 704, seed 30, best of 17 trials. No method optimum or full legacy-verifier claim.')
