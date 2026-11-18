#!/usr/bin/env python3
"""Construct every current native scalar table and bind its exact local tokens."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def source_groups(operation):
    for row in json.loads((ROOT / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((REPO / row['path']).read_bytes()).hexdigest() == row['sha256'], 'retained input hash')
    for row in json.loads((ROOT / 'VENDORED.json').read_text())['files']:
        raw = (ROOT / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'candidate source hash')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'candidate source blob')
    raw = gzip.decompress((ROOT / 'source/WORD.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == json.loads((ROOT / 'source/GRID.json').read_text())['decompressed_sha256'], 'exact candidate word')
    word = json.loads(raw)
    charts = word['initial'] + [None] * word['owned_fields']
    groups = defaultdict(list)
    for pc, event in enumerate(word['program']):
        op, r = event[:2]
        need(0 <= r < len(charts), 'field index')
        if op == 'INIT':
            need(r >= word['public'] and charts[r] is None, 'fresh owned lifetime')
            charts[r] = event[2]
        elif op == 'CLEAR':
            need(r >= word['public'] and charts[r] == event[2], 'owned return chart')
            charts[r] = None
        elif op == 'MOVE':
            need(charts[r] == event[2] and event[4] == (r >= word['public']), 'paid source chart and owner class')
            charts[r] = event[3]
        elif op == 'SCALE':
            need(charts[r] is not None and charts[r] == event[3], 'live SCALE chart')
        elif op == 'ADD':
            need(r != event[2] and charts[r] is not None and charts[r] == charts[event[2]] == event[4], 'distinct cocharted ADD fields')
        else:
            raise ValueError('unexpected current native opcode')
        if op == operation:
            q = Q(event[2] if op == 'SCALE' else event[3])
            groups[q].append(('local', pc, tuple(event)))
    need(charts[:word['public']] == word['final'] and all(c is None for c in charts[word['public']:]), 'complete final chart metadata')
    expected = {'ADD': (139227, 2196), 'SCALE': (4149, 74)}[operation]
    need((sum(map(len, groups.values())), len(groups)) == expected, 'complete coefficient and occurrence census')
    reverse_census = Counter(Q(e[2] if operation == 'SCALE' else e[3])
                            for e in reversed(word['program']) if e[0] == operation)
    need(reverse_census == Counter({q: len(tokens) for q, tokens in groups.items()}), 'separate reverse raw coefficient census')
    return groups, sha256(raw).hexdigest()


def check_graph(table, public_ports):
    n = len(table)
    for row in table:
        op = row[0]
        need(op in ('branch', 'write', 'move', 'goto', 'halt', 'reject'), 'literal opcode')
        if op in ('branch', 'write', 'move'):
            need(0 <= row[1] < public_ports + 2, 'two private banks and exact public port count')
        if op == 'move':
            need(row[2] in (-1, 1), 'unit physical moves')
        elif op == 'goto':
            need(0 <= row[1] < n, 'goto target')
        elif op == 'branch':
            need(all(0 <= target < n for _, target in row[2]) and 0 <= row[3] < n, 'branch targets')
        elif op == 'write':
            need(row[2] in range(7), 'retained symbol alphabet')


def load_compiler(operation):
    slug = 'compact-rounded-add' if operation == 'ADD' else 'current-rounded-scalar-tables'
    sys.path.insert(0, str(REPO / 'research' / slug))
    if operation == 'ADD':
        from tables import compile_compact, cost_bound
        from source_binding import vendor
        physical = vendor('catalogue_compact_fixture', 'vendor/physical_fixture.py')
        return compile_compact, cost_bound, physical
    from tables import compile_rounded
    import physical
    def compile_scale(q):
        return compile_rounded('SCALE', q)
    def scale_cost(receipt, extent, records, old_backing):
        return 512 * (extent + 1) + 64 * receipt['denominator_twos'] * records + 7 * old_backing
    return compile_scale, scale_cost, physical


def execute_case(physical, cost, table, receipt, operation, q, target, source, width, work=None):
    out = physical.execute(table, operation, target, source, width, work, count_rows=True)
    a, b = q.numerator, q.denominator
    expected = tuple((x if operation == 'ADD' else 0) + (a * y + b // 2) // b
                     for x, y in zip(target, source if operation == 'ADD' else target))
    fits = all(-(1 << (width - 1)) <= x < (1 << (width - 1)) for x in expected)
    need((out['error'] is None) == fits, 'exact signed output range iff')
    if fits:
        need(out['output'] == expected, 'independent integer rounding oracle')
    else:
        reason = 'compact rounded ADD format/range' if operation == 'ADD' else 'rounded signed output overflow'
        need(out['error'] == reason, 'expected range rejection')
    charged = out['actions'] + out['table_rows'] + 64
    bound = cost(receipt, len(target) * (width + 1), len(target), out['old_backing'])
    need(charged <= bound, 'complete physical/control bound')
    return {'width': width, 'target': list(target), 'source': list(source) if operation == 'ADD' else None,
            'fits': fits, 'output': list(expected) if fits else None,
            'charged': charged, 'bound': bound, 'old_dirty': out['old_backing']}, out['work']


def calculate(operation):
    groups, source_hash = source_groups(operation)
    compile_table, cost, physical = load_compiler(operation)
    catalogue, covered = [], set()
    for index, q in enumerate(sorted(groups)):
        table, receipt = compile_table(q)
        need(receipt['coefficient'] == str(q), 'compiler coefficient binding')
        d = (q.denominator & -q.denominator).bit_length() - 1
        need(receipt['denominator_twos'] == d, 'compiler dyadic denominator binding')
        if operation == 'ADD':
            length = max(abs(q.numerator).bit_length(), q.denominator.bit_length())
            need(receipt['coefficient_bits'] == length and receipt['extra_width'] == length + 2,
                 'compact numerator width binding')
        check_graph(table, 2 if operation == 'ADD' else 1)
        tokens = groups[q]
        registry = {token: table for token in tokens}
        need(len(registry) == len(tokens), 'unique exact local tokens')
        for token, actual in registry.items():
            need(token[1] not in covered and actual is table, 'one correctly bound service per source event')
            covered.add(token[1])
        first = tokens[0]
        need(('local', first[1], ('SCALE' if operation == 'ADD' else 'ADD',)) not in registry, 'wrong raw event rejected')
        a, b = q.numerator, q.denominator
        width = max(abs(a), b + 1, 1).bit_length() + 3
        target = (-a, a) if operation == 'ADD' else (b - 1, -b - 1)
        source = (b - 1, -b - 1) if operation == 'ADD' else ()
        positive, work = execute_case(physical, cost, registry[first], receipt, operation, q, target, source, width)
        need(positive['fits'], 'signed nonzero coefficient witness fits')
        cases = [positive]
        if operation == 'ADD' and a:
            width = max(2, b.bit_length() + 2)
            upper = (1 << (width - 1)) - 1
            late, work = execute_case(physical, cost, registry[first], receipt, operation, q,
                                      (0, 0, upper, 0), (0, 0, b if a > 0 else -b, 0), width, work)
            need(not late['fits'], 'late overflow rejects every nonzero ADD coefficient')
            cases.append(late)
        tiny, work = execute_case(physical, cost, registry[first], receipt, operation, q,
                                  (0, -1), (-1, -1) if operation == 'ADD' else (), 1, work)
        cases.append(tiny)
        catalogue.append({'coefficient': str(q), 'occurrences': len(tokens),
                          'first_clock': tokens[0][1], 'last_clock': tokens[-1][1],
                          'tokens_sha256': digest(tokens), 'table_sha256': digest(table),
                          'construction': receipt, 'literal_cases': cases})
        if (index + 1) % 100 == 0:
            print(operation + ' tables checked ' + str(index + 1) + '/' + str(len(groups)), file=sys.stderr, flush=True)
    need(len(covered) == sum(map(len, groups.values())), 'all exact occurrences covered')
    all_tokens = sorted(token for tokens in groups.values() for token in tokens)
    if operation == 'ADD':
        extent_charge = sum(r['occurrences'] * 512 * (r['construction']['coefficient_bits'] + 8) for r in catalogue)
        component_charge = sum(r['occurrences'] * 512 * (r['construction']['coefficient_bits'] + 8)
                               * (r['construction']['extra_width'] + 1) for r in catalogue)
    else:
        extent_charge = 512 * len(covered)
        component_charge = sum(r['occurrences'] * 64 * r['construction']['denominator_twos'] for r in catalogue)
    costs = json.loads((ROOT / 'COST.json').read_text())
    need(costs[operation] == {'S_plus_one': extent_charge, 'R': component_charge}, 'source-weighted physical bill')
    need(costs['TOTAL'] == {k: costs['ADD'][k] + costs['SCALE'][k] for k in ('S_plus_one', 'R')}, 'combined physical bill')
    need(Q(-1, 2) in groups, 'actual half-coefficient control')
    wrong, wrong_receipt = compile_table(Q(-1))
    try:
        execute_case(physical, cost, wrong, wrong_receipt, operation, Q(-1, 2),
                     (0, 0) if operation == 'ADD' else (1, -1),
                     (1, -1) if operation == 'ADD' else (), 4)
    except ValueError as exc:
        need(str(exc) == 'independent integer rounding oracle', 'wrong-table control has a semantic cause')
    else:
        raise ValueError('wrong coefficient table accepted')
    malformed = list(wrong)
    at = next(i for i, row in enumerate(malformed) if row[0] == 'move')
    malformed[at] = ('move', malformed[at][1], 2)
    try:
        check_graph(malformed, 2 if operation == 'ADD' else 1)
    except ValueError as exc:
        need(str(exc) == 'unit physical moves', 'wrong-move control has the expected cause')
    else:
        raise ValueError('nonunit move accepted')
    return {'operation': operation, 'source_word_sha256': source_hash,
            'occurrences': len(covered), 'coefficients': len(catalogue),
            'registry_sha256': digest(all_tokens),
            'total_table_rows': sum(row['construction']['rows'] for row in catalogue),
            'total_table_states': sum(row['construction']['states'] for row in catalogue),
            'maximum_table_rows': max(row['construction']['rows'] for row in catalogue),
            'literal_cases': sum(len(row['literal_cases']) for row in catalogue),
            'successful_cases': sum(case['fits'] for row in catalogue for case in row['literal_cases']),
            'range_rejections': sum(not case['fits'] for row in catalogue for case in row['literal_cases']),
            'controls': ['wrong raw event token rejected in every group',
                         'wrong coefficient table rejected by integer oracle',
                         'nonunit physical move rejected'],
            'catalogue': catalogue}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('ADD', 'SCALE'))
    parser.add_argument('--write', action='store_true', help='Write the initial exact catalogue receipt.')
    args = parser.parse_args()
    result = calculate(args.operation)
    path = ROOT / ('CATALOGUE-' + args.operation + '.json')
    if args.write:
        need(not path.exists(), 'do not overwrite an existing checked catalogue')
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads(path.read_text()), 'complete catalogue receipt')
    print('PASS_CURRENT_NATIVE_ROUNDED_CATALOGUE ' + json.dumps({k: v for k, v in result.items() if k != 'catalogue'}, sort_keys=True))


if __name__ == '__main__':
    main()
