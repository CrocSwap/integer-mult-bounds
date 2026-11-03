#!/usr/bin/env python3
"""Finite integer-only classification of one frozen280-row demand system.

Nick Petalas/6425, ToikY/6455 and PR1422/support lineage retain their credit.
New finite certificate: ToikY with OpenAI Codex assistance. Apache-2.0.
No source executable, LP, floating arithmetic or optional dependency is used.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
from itertools import combinations_with_replacement
import json
from math import comb
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
MANIFEST_SHA = 'c326b2a83adb02af94954c3904ee6e59822bf5fd274c847851abdcb63c1b9c64'
DIM, NROWS, OUTSIDE = 14, 280, 8
CAPS = {'seconds': 180, 'total_profiles': 30000000, 'profiles_per_target': 200000}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticated():
    raw_manifest = (HERE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(raw_manifest).hexdigest() == MANIFEST_SHA, 'source manifest SHA256')
    pins = decode(raw_manifest)['files']
    require(set(pins) == {'MATRIX-6425.json', 'REAL-RESULT-6455.json', 'README-6455.md'}, 'three exact source files')
    raw = {}
    for name, pin in pins.items():
        value = (HERE / 'sources' / name).read_bytes()
        require(len(value) == pin['bytes'], 'source byte length: ' + name)
        require(hashlib.sha256(value).hexdigest() == pin['sha256'], 'source SHA256: ' + name)
        require(hashlib.sha1(b'blob ' + str(len(value)).encode() + b'\0' + value).hexdigest() == pin['git_blob'], 'source Git blob: ' + name)
        raw[name] = value
    return decode(raw['MATRIX-6425.json']), decode(raw['REAL-RESULT-6455.json'])


def mask_value(text):
    require(type(text) is str, 'hex support string')
    mask = int(text, 16)
    require(0 < mask < (1 << DIM) and text == hex(mask), 'canonical nonempty14-bit support')
    return mask


def rational(text):
    require(type(text) is str, 'canonical Fraction string')
    value = F(text)
    require(str(value) == text, 'canonical Fraction representation')
    return value


def bits(mask):
    return [k for k in range(DIM) if mask & (1 << k)]


def order(mask):
    return mask.bit_count(), mask


def dot(mask, x):
    return sum(x[k] for k in bits(mask))


def matrix_rows(obj):
    require(type(obj.get('kernel_rows')) is int and obj['kernel_rows'] == NROWS, '280 original rows')
    require(type(obj.get('alphabet')) is list and len(obj['alphabet']) == DIM, '14 source variables')
    require(type(obj.get('kernel')) is list and len(obj['kernel']) == NROWS, 'literal source kernel')
    rows = {}
    for entry in obj['kernel']:
        require(type(entry) is list and len(entry) == 3, 'source kernel row schema')
        mask = mask_value(entry[0])
        require(mask not in rows, 'unique source support')
        demand = entry[1]
        require(type(demand) is int and 1 <= demand <= OUTSIDE, 'source demand1..8')
        require(type(entry[2]) is str and entry[2] == hex(int(entry[2], 16)) and int(entry[2], 16) > 0, 'source witness identifier')
        rows[mask] = demand
    return rows


def real_separator(target, x, rows):
    require(target in rows and len(x) == DIM and all(value >= 0 for value in x), 'nonnegative real point')
    require(all(dot(mask, x) >= demand for mask, demand in rows.items() if mask != target), 'point misses another original row')
    require(dot(target, x) < rows[target], 'point must strictly violate target')


def integer_separator(target, x, rows):
    require(type(x) is list and len(x) == DIM and all(type(value) is int and value >= 0 for value in x), 'literal nonnegative INTEGER witness')
    real_separator(target, x, rows)


def validate_old_deletions(parent, retained, rows):
    deleted = []
    require(type(parent['deletions']) is list and len(parent['deletions']) == 43, '43 legacy real deletions')
    for record in parent['deletions']:
        target = mask_value(record['target'])
        require(target in rows and target not in retained and target not in deleted, 'legacy deletion partition')
        coverage, demand, seen = [F(0)] * DIM, F(0), set()
        require(type(record['multipliers']) is list and record['multipliers'], 'nonempty legacy multiplier list')
        for raw_donor, raw_weight in record['multipliers']:
            donor, weight = mask_value(raw_donor), rational(raw_weight)
            require(donor in retained and donor not in seen and donor != target and donor & target == donor and weight >= 0, 'proper-subset nonnegative legacy donor')
            seen.add(donor)
            demand += weight * rows[donor]
            for k in bits(donor):
                coverage[k] += weight
        require(all(v <= int(bool(target & (1 << k))) for k, v in enumerate(coverage)) and demand >= rows[target], 'legacy Farkas combination')
        deleted.append(target)
    require(set(deleted) | retained == set(rows), 'complete prior real partition')
    return sorted(deleted)


def parent_data(parent, rows):
    require(type(parent.get('dimension')) is int and parent['dimension'] == DIM and type(parent.get('source_rows')) is int and parent['source_rows'] == NROWS, 'parent dimensions')
    require(type(parent.get('retained')) is list and len(parent['retained']) == 237, '237 legacy real retained rows')
    sequence = [mask_value(text) for text in parent['retained']]
    retained = set(sequence)
    require(len(retained) == 237 and retained <= set(rows), 'unique legacy retained masks')
    deleted = validate_old_deletions(parent, retained, rows)
    require(type(parent['separators']) is list and len(parent['separators']) == 237, 'all237 legacy separators')
    integral, all_points = {}, {}
    for record in parent['separators']:
        target = mask_value(record['target'])
        require(target in retained and target not in all_points and type(record['x']) is list, 'legacy separator target')
        x = [rational(text) for text in record['x']]
        real_separator(target, x, rows)
        all_points[target] = x
        if all(value.denominator == 1 for value in x):
            point = [int(value) for value in x]
            integer_separator(target, point, rows)
            integral[target] = point
    require(set(all_points) == retained and len(integral) == 134, '134 actual prior integral points')
    unresolved = sorted(retained - set(integral), key=order)
    require(len(unresolved) == 103, '103 integer-only questions beyond predecessor')
    return deleted, integral, unresolved


class Budget:
    def __init__(self):
        self.started = time.monotonic()
        self.profiles = 0

    def check(self):
        require(time.monotonic() - self.started <= CAPS['seconds'], 'UNKNOWN: finite classification time cap')
        require(self.profiles <= CAPS['total_profiles'], 'UNKNOWN: finite classification profile cap')

    def tick(self):
        self.profiles += 1
        require(self.profiles <= CAPS['total_profiles'], 'UNKNOWN: finite classification profile cap')
        if self.profiles % 1024 == 0:
            self.check()


def obstruction_shape(record, rows):
    target = mask_value(record['target'])
    coordinates, bound = bits(target), rows[target] - 1
    expected = comb(len(coordinates) + bound, len(coordinates))
    require(record['coordinates'] == coordinates and record['budget'] == bound, 'obstruction domain')
    require(type(record['expected_profiles']) is int and record['expected_profiles'] == expected and type(record['checked_profiles']) is int and record['checked_profiles'] == expected, 'complete weak-composition count')
    total, seen = 0, set()
    for raw_mask, count in record['miss_histogram']:
        premise = mask_value(raw_mask)
        require(premise in rows and premise != target and premise & target == premise and premise not in seen, 'obstruction premise must be a proper source subset')
        require(type(count) is int and count > 0, 'positive miss count')
        seen.add(premise)
        total += count
    require(total == expected, 'miss histogram covers complete domain')


def classify(target, rows, budget):
    coordinates, bound = bits(target), rows[target] - 1
    expected = comb(len(coordinates) + bound, len(coordinates))
    require(expected <= CAPS['profiles_per_target'], 'UNKNOWN: target domain cap')
    proper = [(mask, rows[mask], tuple(int(bool(mask & (1 << k))) for k in range(DIM)))
              for mask in sorted(rows) if mask != target and mask & target == mask]
    histogram, checked = Counter(), 0
    transcript = hashlib.sha256(b'p112-miss/v1\0' + target.to_bytes(2, 'big') + bytes((bound,)))
    budget.check()
    for total in range(bound + 1):
        for allocation in combinations_with_replacement(coordinates, total):
            budget.tick()
            checked += 1
            missing = next((mask for mask, demand, members in proper if total < demand or sum(members[k] for k in allocation) < demand), None)
            if missing is None:
                x = [OUTSIDE] * DIM
                for k in coordinates:
                    x[k] = 0
                for k in allocation:
                    x[k] += 1
                integer_separator(target, x, rows)
                return x, None, checked
            histogram[missing] += 1
            transcript.update(bytes((total,)) + bytes(allocation) + missing.to_bytes(2, 'big'))
    require(checked == expected, 'actual complete weak-composition enumeration')
    record = {'target': hex(target), 'coordinates': coordinates, 'budget': bound,
              'expected_profiles': expected, 'checked_profiles': checked,
              'miss_histogram': [[hex(mask), count] for mask, count in sorted(histogram.items())],
              'profile_sha256': transcript.hexdigest()}
    obstruction_shape(record, rows)
    budget.check()
    return None, record, checked


def generate(rows, parent):
    legacy, integral, unresolved = parent_data(parent, rows)
    witnesses = {mask: {'target': hex(mask), 'x': x, 'origin': 'prior-integral'} for mask, x in integral.items()}
    obstructions, statistics, budget = [], [], Budget()
    for target in unresolved:
        x, obstruction, checked = classify(target, rows, budget)
        statistics.append([hex(target), checked, 'witness' if x is not None else 'exhausted'])
        if x is not None:
            witnesses[target] = {'target': hex(target), 'x': x, 'origin': 'new-integer'}
        else:
            obstructions.append(obstruction)
    removed = {mask_value(record['target']) for record in obstructions}
    retained = set(witnesses)
    require(not(retained & set(legacy) or retained & removed or set(legacy) & removed), 'disjoint complete classification')
    require(retained | set(legacy) | removed == set(rows), 'all280 original rows classified')
    require(134 <= len(retained) <= 237 and len(witnesses) - 134 + len(obstructions) == 103, 'new-only classification counts')
    for target, witness in witnesses.items():
        integer_separator(target, witness['x'], rows)
    for record in obstructions:
        obstruction_shape(record, rows)
    budget.check()
    return legacy, witnesses, sorted(obstructions, key=lambda record: int(record['target'], 16)), statistics, budget


def rejects(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('invalid proof object accepted')


def controls(rows, witnesses, obstructions):
    triangle = {3: 1, 5: 1, 6: 1, 7: 2}
    x, obstruction, _checked = classify(7, triangle, Budget())
    require(x is None and obstruction['checked_profiles'] == 4, 'triangle integer-only obstruction')
    fractional = [F(0)] * DIM
    fractional[:3] = [F(1, 2)] * 3
    real_separator(7, fractional, triangle)
    integer_error = rejects(lambda: integer_separator(7, fractional, triangle))
    boundary = {1: 1, 3: 2}
    x, obstruction2, _checked = classify(3, boundary, Budget())
    require(obstruction2 is None and dot(3, x) == 1, 'inclusive d-1 boundary witness')
    corrupted = dict(obstruction)
    corrupted['checked_profiles'] -= 1
    count_error = rejects(lambda: obstruction_shape(corrupted, triangle))
    corrupted = dict(obstruction)
    corrupted['miss_histogram'] = [['0x7', 4]]
    circular_error = rejects(lambda: obstruction_shape(corrupted, triangle))
    target = min(witnesses)
    changed = list(witnesses[target]['x'])
    changed[bits(target)[0]] += rows[target]
    strict_error = rejects(lambda: integer_separator(target, changed, rows))
    return {'triangle_real_integer_gap': {'target': '0x7', 'checked_profiles': 4,
                                          'fractional_point': ['1/2', '1/2', '1/2'], 'integer_domain_rejection': integer_error},
            'inclusive_budget_boundary': {'target': '0x3', 'witness_first_two_coordinates': x[:2]},
            'incomplete_count_rejection': count_error, 'self_premise_rejection': circular_error,
            'actual_witness_loses_strict_violation': {'target': hex(target), 'observed_error': strict_error},
            'full_source_obstructions': len(obstructions)}


def run():
    source_matrix, parent = authenticated()
    rows = matrix_rows(source_matrix)
    legacy, witnesses, obstructions, statistics, budget = generate(rows, parent)
    retained = sorted(witnesses)
    return {'schema_version': 1, 'source_manifest_sha256': MANIFEST_SHA,
            'dimension': DIM, 'source_rows': len(rows), 'retained': list(map(hex, retained)),
            'reused_real_deletions': list(map(hex, legacy)),
            'witnesses': [witnesses[mask] for mask in retained], 'obstructions': obstructions,
            'counts': {'retained': len(retained), 'reused_real_deletions': len(legacy),
                       'reused_integral_witnesses': 134, 'new_integer_witnesses': len(retained) - 134,
                       'new_integer_only_deletions': len(obstructions)},
            'search_statistics': {'new_targets': 103, 'profiles_checked': budget.profiles, 'per_target': statistics},
            'declared_caps': CAPS, 'controls': controls(rows, witnesses, obstructions),
            'exhaustion_encoding': 'CWR coordinates ascending; total0..budget. SHA256 starts with p112-miss/v1 NUL,target two-byte big-endian,budget byte; each miss is total byte,allocation bytes,first-missed mask two-byte big-endian. Histogram/count/digest alone are not a proof: full negative domains are enumerated.',
            'limits': ['Only103previously unresolved integer labels are newly classified;43real deletion certificates and134actual integral separators are validated and reused as predecessor evidence.',
                       'Unique minimum subset of the original280named rows on unrestricted nonnegative INTEGER variables; not a minimum arbitrary inequality description, facet theorem or support-alphabet extension.',
                       'Equivalence can be conjoined with the same additional constraints, but indispensability/minimum need not survive added budget constraints that exclude these witnesses.',
                       'Original clique census, caps, real280-row source equivalence, coefficients/decoder, COPY floor, native/physical/outer admission and kappa remain separate.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(canonical(result))
    else:
        path = HERE / 'RESULT.json'
        require(path.is_file(), 'retained RESULT.json required')
        observed = decode(path.read_bytes())
        require(type(observed) is dict and type(observed.get('schema_version')) is int and observed['schema_version'] == 1, 'typed integer certificate receipt')
        require(canonical(observed) == canonical(result), 'strict retained complete integer certificate')
        print('PASS_P112_INTEGER_DEMAND_KERNEL')


if __name__ == '__main__':
    main()
