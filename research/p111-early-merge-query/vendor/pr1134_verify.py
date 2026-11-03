#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the frozen-U8 P111 gather obstruction with exact arithmetic.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
This finite check does not prove the full multiplication theorem.
"""
import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = frozenset(range(512))
DEN = 1 << 160


def need(condition, label):
    if not condition:
        raise ValueError(label)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def basis(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for higher in pivots:
            if higher > bit and (pivots[higher] >> bit) & 1:
                pivots[higher] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


@lru_cache(None)
def span(frame):
    values = {0}
    for vector in frame:
        values |= {x ^ vector for x in values}
    return frozenset(values)


def operands(event):
    need(event[0] in ('add', 'scale'), 'unknown scalar operation')
    return event[1:3] if event[0] == 'add' else event[1:2]


def add_row(target, coefficient, source):
    for column, value in source.items():
        result = target.get(column, Q(0)) + coefficient * value
        if result:
            target[column] = result
        else:
            target.pop(column, None)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def rebuild(pins):
    for path, expected in pins['files'].items():
        need(digest((ROOT / path).read_bytes()) == expected, 'source pin: ' + path)
    source = pins['word']
    with tempfile.TemporaryDirectory(prefix='shared-carrier-host-') as directory:
        directory = Path(directory)
        with tarfile.open(ROOT / source['archive'], 'r:gz') as archive:
            member = archive.extractfile(source['member'])
            need(member is not None, 'X4 archive member')
            packed = member.read()
        need(digest(gzip.decompress(packed)) == source['x4_sha256'], 'raw X4 content pin')
        base = directory / 'X4.json.gz'
        output = directory / 'U8.json.gz'
        base.write_bytes(packed)
        command = [sys.executable, '-I', '-B', str(ROOT / source['builder']),
                   str(base), str(ROOT / source['recipe']), str(output)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        raw = gzip.decompress(output.read_bytes())
    need(digest(raw) == source['u8_sha256'], 'raw U8 content pin')
    return json.loads(raw)


def replay(word):
    v, h, helpers = (word['report'][key] for key in ('v', 'h', 'R'))
    need((v, h, helpers) == (112, 9, 504), 'U8 geometry')
    n = 2 * v + helpers
    ports = word['ports']
    full = basis(range(1, 512))
    end = [full] * v + [basis(x for x in range(512) if not dot_bits(x, p))
                       for p in ports] + [full] * helpers
    for role, frame in word['helper_final'].items():
        end[int(role)] = basis(frame)
    start = [(p,) for p in ports] + [()] * (v + helpers)
    for role, frame in word['start_extra'].items():
        need(2 * v <= int(role) < n, 'helper entrance role')
        start[int(role)] = basis(frame)
    current = start.copy()
    by_role = [Counter() for _ in range(n)]
    paid = Counter()
    rows = [{i: Q(1)} if i < v else {} for i in range(n)]
    need(all(role >= v for event in word['precondition'] for role in operands(event)),
         'precondition has a clean source response')

    def climb(role, frame):
        frame = basis(frame)
        need(span(current[role]) <= span(frame), 'nonmonotone source word')
        rank = len(frame) - len(current[role])
        if rank:
            paid[rank] += 1
            by_role[role][rank] += 1
        current[role] = frame

    for event in word['A']:
        for role in operands(event):
            climb(role, event[-1])
        if event[0] == 'add':
            _, target, source, numerator, denominator, _ = event
            need(target != source, 'self add')
            add_row(rows[target], Q(numerator, denominator), rows[source])
        else:
            _, target, numerator, denominator, _ = event
            scalar = Q(numerator, denominator)
            need(scalar != 0, 'zero scale')
            rows[target] = {i: scalar * value for i, value in rows[target].items()}
    at_cut = current.copy()
    for row, frame in zip(rows, at_cut):
        need(all(ports[i] in span(frame) for i in row), 'clean row outside its frame')
    levels = {int(t): basis(frame) for t, frame in word['target_levels'].items()}
    need(all(current[v + t] == levels.get(t, ()) for t in range(v)), 'target COPY levels')
    future = [[span(frame)] for frame in end]
    for centre, frame in zip(word['centers'], word['center_frames']):
        frame = basis(frame)
        need(current[centre] == frame, 'retained centre frame')
        future[centre].append(span(frame))
        served = {levels.get(e[1] - v, ()) for e in word['cut'] if e[2] == centre}
        for target in sorted(served, key=lambda item: -len(item)):
            need(span(target) <= span(frame), 'COPY path')
            if target != frame:
                paid[len(frame) - len(target)] += 1
            frame = target
    for event in word['cut']:
        future[event[1]].append(span(levels.get(event[1] - v, ())))
    early_ids = {index for index, _ in word['early_cleanup']}
    need(len(early_ids) == len(word['early_cleanup']), 'duplicate early cleanup')
    tail = [word['cleanup'][index][:-1] + [frame]
            for index, frame in word['early_cleanup']]
    for event in word['B'] + tail:
        for role in operands(event):
            future[role].append(span(basis(event[-1])))
            climb(role, event[-1])
    for role, frame in enumerate(end):
        climb(role, frame)
    for index, event in enumerate(word['cleanup']):
        if index not in early_ids:
            need(all(span(end[r]) == FULL for r in operands(event)), 'full cleanup end')
    expected = {int(rank): count for rank, count in word['report']['local_profile'].items()}
    need(dict(paid) == expected, 'paid local profile')
    widths = Counter(len(end[r]) - len(start[r]) for r in range(2 * v, n))
    need(dict(widths) == {int(r): c for r, c in word['report']['width_inventory'].items()},
         'helper widths')
    intersections = [frozenset.intersection(*frames) for frames in future]
    return rows, at_cut, intersections, by_role, paid, widths


def dot_bits(left, right):
    return (left & right).bit_count() % 2


def unique_expression(rows, roles, beta, query):
    pivots = {}
    for role in roles:
        row = {i: value for i, value in rows[role].items() if i != beta}
        combination = {role: Q(1)}
        for column, (pivot, expansion) in sorted(pivots.items()):
            scalar = row.get(column, Q(0))
            if scalar:
                add_row(row, -scalar, pivot)
                add_row(combination, -scalar, expansion)
        need(bool(row), 'eligible rows are dependent')
        column = min(row)
        scalar = row[column]
        pivots[column] = ({i: value / scalar for i, value in row.items()},
                          {i: value / scalar for i, value in combination.items()})
    residual = dict(query)
    result = {}
    for column, (pivot, expansion) in sorted(pivots.items()):
        scalar = residual.get(column, Q(0))
        if scalar:
            add_row(residual, -scalar, pivot)
            add_row(result, scalar, expansion)
    need(not residual, 'query not in eligible span')
    need(expands(rows, result, beta, query), 'query expression')
    return result


def expands(rows, expression, beta, query):
    actual = {}
    for role, scalar in expression.items():
        add_row(actual, scalar, rows[role])
    actual.pop(beta, None)
    return actual == query


def down(value):
    return Q(value.numerator * DEN // value.denominator, DEN)


def up(value):
    return -down(-value)


@lru_cache(None)
def price(rank, exponent):
    # The proof gives the two positive-series remainder bounds.
    value = Q(73, rank)
    power = 0
    while value >= 2:
        value /= 2
        power += 1

    def log_series(z):
        lower = 2 * sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(24)), Q(0))
        return lower, lower + 2 * z ** 49 / (49 * (1 - z * z))

    lower, upper = log_series((value - 1) / (value + 1))
    ln2_lower, ln2_upper = log_series(Q(1, 3))
    lower = down(exponent * (lower + power * ln2_lower))
    upper = up(exponent * (upper + power * ln2_upper))
    need(0 <= lower <= upper < 1, 'exponential interval domain')

    def exp_series(x):
        term = total = Q(1)
        for j in range(1, 13):
            term *= x / j
            total += term
        return total, term * x / 13 / (1 - x / 14)

    lo, _ = exp_series(lower)
    hi, tail = exp_series(upper)
    return down(rank * lo), up(rank * (hi + tail))


def moment(profile, idle_mass, exponent):
    need(idle_mass >= 0, 'negative residual owner mass')
    values = [Q(0), Q(0)]
    for rank, count in profile.items():
        need(count >= 0, 'negative recursive-child count')
        interval = price(rank, exponent)
        for side in (0, 1):
            values[side] += 9 * count * interval[side]
    idle = price(48, exponent)
    return tuple((values[side] + Q(idle_mass, 48) * idle[side]) / (73 * 888)
                 for side in (0, 1))


def show(value):
    with localcontext() as context:
        context.prec = 42
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Write the exact finite certificate here.')
    args = parser.parse_args()
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    word = rebuild(pins)
    print('PASS source pins and fresh raw U8 reconstruction', flush=True)
    rows, frames, future, by_role, local, widths = replay(word)
    claim = json.loads((ROOT / 'research/complex-t37-owners/CLAIM.json').read_text())
    exponent = Q(claim['complex_lower'])
    for rank, count in local.items():
        need(claim['profile'][str(rank)] == 333 * count + claim['idle'].get(str(rank), 0),
             'T37 local-to-global profile')
    helper_mass = sum(rank * count for rank, count in widths.items())
    capacity = 111 * (6 * 8 + 4 * (16 + 32 + 48))
    idle_before = capacity - 9 * helper_mass
    need(idle_before == 13950, 'P111 residual volume')
    ports, roots = word['ports'], word['root_lines']
    need(len(set(ports)) == 112 and len(roots) == 112, 'distinct port geometry')
    need(all(dot(r, r) == 4 for r in roots), 'root scale')
    need(all(dot_bits(ports[i], ports[j]) == (Q(dot(roots[i], roots[j]), 2) + 1) % 2
             for i in range(112) for j in range(112)), 'root-to-label pairing')
    mixed_ports = ports.copy()
    mixed_ports[0], mixed_ports[1] = mixed_ports[1], mixed_ports[0]
    need(any(dot_bits(mixed_ports[i], mixed_ports[j]) != (Q(dot(roots[i], roots[j]), 2) + 1) % 2
             for i in range(112) for j in range(112)), 'mixed label chart control')
    print('PASS clean A rows, all frame paths, data traces, and owner mass', flush=True)
    records = []
    controls = Counter(mixed_label_chart_rejected=1)
    for beta in range(112):
        hyperplane = frozenset(x for x in FULL if not dot_bits(x, ports[beta]))
        query = {i: Q(dot(roots[beta], roots[i]), 2) for i in range(112) if i != beta}
        query = {i: value for i, value in query.items() if value}
        need(len(query) == 52 and span(basis(ports[i] for i in query)) == hyperplane,
             'query spans its hyperplane')
        roles = [r for r, frame in enumerate(frames)
                 if span(frame) <= hyperplane and any(i != beta for i in rows[r])]
        expression = unique_expression(rows, roles, beta, query)
        required = sorted(expression)
        need(all((future[r] & hyperplane) == span(frames[r]) for r in required),
             'required row can advance within the query hyperplane')
        need(not any(span(frame) <= hyperplane <= future[r] for r, frame in enumerate(frames)),
             'an old register can reach the query hyperplane')
        need(all(not (span(frames[r]) <= span(frames[s]) or span(frames[s]) <= span(frames[r]))
                 for r, s in itertools.combinations(required, 2)), 'required frames form an antichain')
        transport = Counter(8 - len(frames[r]) for r in required)
        removed = by_role[beta] + by_role[112 + beta]
        need(sum(r * c for r, c in removed.items()) == 16, 'removed data mass')
        favorable = local.copy()
        favorable.subtract(removed)
        favorable[8] -= 1
        favorable[7] += 1
        free_query = moment(favorable, idle_before, exponent)
        need(free_query[1] < 1, 'free-query control is not favorable')
        controls['free_query_would_pass'] += 1
        favorable.update(transport)
        mass = sum(r * c for r, c in transport.items())
        interval = moment(favorable, idle_before - 9 * mass, exponent)
        need(interval[0] > 1, 'optimistic gather could meet the historical exponent')
        altered = dict(expression)
        altered[required[0]] += 1
        need(not expands(rows, altered, beta, query), 'wrong coefficient control')
        controls['wrong_query_coefficient_rejected'] += 1
        first, second = required[:2]
        need(not span(frames[first]) <= span(frames[second]), 'coalesced carrier control')
        controls['two_required_reads_cannot_share_one_monotone_path'] += 1
        need(not hyperplane <= future[first], 'old-row-to-H control')
        controls['old_row_advance_to_query_frame_rejected'] += 1
        records.append(dict(beta=beta,port=ports[beta],eligible_rows=len(roles),
                            required_rows=len(required),coefficients={str(r): str(expression[r]) for r in required},
                            required_frames={str(r): list(frames[r]) for r in required},
                            transport_profile=dict(sorted(transport.items())),transport_mass=mass,
                            removed_data_profile=dict(sorted(removed.items())),
                            optimistic_profile=dict(sorted(favorable.items())),
                            idle_mass=idle_before - 9 * mass,
                            moment_lower=str(interval[0]),moment_upper=str(interval[1])))
    spec = importlib.util.spec_from_file_location('retained_intervals', ROOT / pins['interval_engine'])
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    for rank in (1, 2, 3, 4, 5, 6, 7, 8, 48):
        lo, hi = engine.log(Q(73, rank))
        lower, upper = engine.exp(exponent * lo, exponent * hi)
        ours = price(rank, exponent)
        need(ours[0] <= rank * lower <= rank * upper <= ours[1], 'independent power enclosure')
    best = min(records, key=lambda row: Q(row['moment_lower']))
    cases = Counter((r['eligible_rows'], r['required_rows'], tuple(r['transport_profile'].items())) for r in records)
    certificate = dict(status='PASS_SCOPED_FROZEN_U8_GATHER_OBSTRUCTION',base_commit=pins['base_commit'],
                       source_word_sha256=pins['word']['u8_sha256'],historical_complex_b=str(exponent),
                       domain='All 112 punctures, exact rational rows, no random seed',
                       local_profile=dict(sorted(local.items())),helper_widths=dict(sorted(widths.items())),
                       p111_owner_capacity_per_replica=capacity,old_helper_mass_per_call=helper_mass,
                       best_beta=best['beta'],best_moment_lower=best['moment_lower'],
                       best_moment_upper=best['moment_upper'],controls=dict(controls),records=records)
    if args.out:
        args.out.write_text(json.dumps(certificate, indent=2) + '\n')
    print('PASS all 112 unique row expressions, fixed frames, and antichains')
    print('PASS carrier classes ' + str(dict(cases)))
    print('PASS exact moments and independent power enclosures')
    print('PASS controls ' + str(dict(controls)))
    print('best beta =', best['beta'])
    print('best moment lower =', show(Q(best['moment_lower'])))
    print('best moment upper =', show(Q(best['moment_upper'])))
    print(certificate['status'])


if __name__ == '__main__':
    main()
