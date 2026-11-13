"""Dense signed forward replay and rational rowspace certificate for one #7481 cut."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
WORD = '7481-WORD.json.gz'
COMPRESSED = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PAYLOAD = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
ROLE, START, CUT, CHART = 1533, 38139, 42500, 1031
GRID = 1125 * 2**25


def timeout(signum, frame):
    print(dumps({'status': 'unresolved_timeout', 'cases': 0, 'cap_seconds': 30}))
    exit(124)


def scaled(row, coefficient):
    numerator, denominator = coefficient.as_integer_ratio()
    if denominator == 1:
        return [numerator * value for value in row]
    products = [numerator * value for value in row]
    return [value // denominator if not value % denominator else Q(value, denominator)
            for value in products]


def replay(word):
    tape = word['program']
    assert tape[START] == ['INIT', ROLE, 597]
    assert tape[42487] == ['MOVE', ROLE, 597, CHART, True]
    assert tape[CUT:CUT + 4] == [['MOVE', ROLE, CHART, 591, True],
                                ['SCALE', ROLE, '-1/2', 591],
                                ['ADD', 901, ROLE, '1', 591],
                                ['CLEAR', ROLE, 591]]
    assert tape[42495] == ['ADD', 1336, 1562, '1', CHART]
    public = word['public']
    count = public + word['owned_fields']
    zero = [0] * public
    rows = [zero] * count
    for index in range(public):
        row = zero.copy()
        row[index] = GRID
        rows[index] = row
    charts = word['initial'] + [None] * word['owned_fields']
    dirty = [Q(0)] * count
    guards = []
    dirty_clears = []
    outward = {}
    for clock, (op, dst, *args) in enumerate(tape[:CUT]):
        if op == 'INIT':
            assert charts[dst] is None and not any(rows[dst])
            if dirty[dst]:
                guards.append((clock, op, dst, dirty[dst]))
            charts[dst] = args[0]
            dirty[dst] = Q(clock == START)
        elif op == 'CLEAR':
            assert charts[dst] == args[0]
            if dirty[dst]:
                dirty_clears.append((clock, dst, args[0], dirty[dst]))
            charts[dst] = None
            rows[dst] = zero
            dirty[dst] = Q(0)
        elif op == 'MOVE':
            assert charts[dst] == args[0] and args[2] == (dst >= public)
            charts[dst] = args[1]
        elif op == 'SCALE':
            assert charts[dst] == args[1]
            coefficient = Q(args[0])
            rows[dst] = scaled(rows[dst], coefficient)
            if dirty[dst]:
                dirty[dst] *= coefficient
        else:
            src, coefficient, chart = args
            assert op in ('ADD', 'COPY') and charts[src] == charts[dst] == chart
            coefficient = Q(coefficient)
            if op == 'COPY':
                assert not any(rows[dst])
                if dirty[dst]:
                    guards.append((clock, op, dst, dirty[dst]))
                rows[dst] = scaled(rows[src], coefficient)
                dirty[dst] = coefficient * dirty[src]
            else:
                added = scaled(rows[src], coefficient)
                rows[dst] = [a + b for a, b in zip(rows[dst], added)]
                if dirty[src]:
                    dirty[dst] += coefficient * dirty[src]
            if clock == 42495:
                outward = {'clock': clock, 'destination': dst, 'old_row': rows[dst],
                           'extra_coefficient': str(dirty[dst])}
    return rows, charts, dirty, guards, dirty_clears, outward


def add_scaled(row, other, coefficient):
    for key, value in other.items():
        total = row.get(key, Q(0)) + coefficient * value
        if total:
            row[key] = total
        else:
            row.pop(key, None)


def reduce_row(row, basis):
    residual = row.copy()
    combination = {}
    for pivot, (basis_row, provenance) in sorted(basis.items()):
        if pivot in residual:
            factor = residual[pivot]
            add_scaled(residual, basis_row, -factor)
            add_scaled(combination, provenance, factor)
    return residual, combination


def echelon(rows):
    basis = {}
    for index, row in enumerate(rows):
        residual, combination = reduce_row(row, basis)
        if residual:
            pivot = min(residual)
            coefficient = residual[pivot]
            provenance = {index: Q(1)}
            add_scaled(provenance, combination, -1)
            basis[pivot] = ({k: v / coefficient for k, v in residual.items()},
                            {k: v / coefficient for k, v in provenance.items()})
    return basis


def dot(row, probe):
    return sum((value * probe.get(index, Q(0)) for index, value in row.items()), Q(0))


def separating_probe(residual, basis):
    free = min(residual)
    assert free not in basis
    probe = {free: Q(1)}
    for pivot, (row, _) in sorted(basis.items(), reverse=True):
        value = -dot(row, probe)
        if value:
            probe[pivot] = value
    return probe


def sparse_old(row):
    return {index: Q(value) / GRID for index, value in enumerate(row) if value}


def sparse_json(row):
    return {str(index): str(value) for index, value in sorted(row.items())}


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    compressed = (ROOT / WORD).read_bytes()
    assert sha256(compressed).hexdigest() == COMPRESSED
    raw = decompress(compressed)
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw)
    rows, charts, dirty, guards, dirty_clears, outward = replay(word)
    assert charts[ROLE] == CHART
    roles = [role for role, chart in enumerate(charts) if chart == CHART]
    public = word['public']
    extra = {public: Q(1)}
    original = {role: sparse_old(rows[role]) for role in roles}
    available = [original[role] | ({public: dirty[role]} if dirty[role] else {}) for role in roles]
    basis = echelon(available)
    outward['old_row'] = sparse_json(sparse_old(outward['old_row']))
    retained_add = {index: -value / 2 for index, value in original[ROLE].items()}
    targets = [('recover_extra', extra), ('retained_add_42502_term', retained_add)]
    targets.extend((f'restore_{role}', row) for role, row in original.items())
    certificates = {}
    solutions = {}
    for label, target in targets:
        residual, representation = reduce_row(target, basis)
        if residual:
            probe = separating_probe(residual, basis)
            actual = [dot(row, probe) for row in available]
            expected = dot(target, probe)
            assert not any(actual) and expected
            certificates[label] = {'public_and_extra_input_probe': sparse_json(probe),
                                   'source_values': list(map(str, actual)),
                                   'required_value': str(expected)}
        else:
            check = {}
            for index, coefficient in representation.items():
                add_scaled(check, available[index], coefficient)
            assert check == target
            solutions[label] = sparse_json({roles[i]: c for i, c in representation.items()})
    outside = {role: value for role, value in enumerate(dirty) if value and charts[role] != CHART}
    receipt = {
        'status': 'rationally_inconsistent' if certificates or outside or guards else 'rationally_feasible',
        'case': {'role': ROLE, 'cut': CUT, 'chart': CHART, 'cap_seconds': 30, 'cases_completed': 1},
        'word_sha256': COMPRESSED, 'payload_sha256': PAYLOAD,
        'role_order': roles, 'extra_input_column': public, 'source_rank': len(basis),
        'required_rank': len(echelon([target for _, target in targets])),
        'combined_rank': len(echelon(available + [target for _, target in targets])),
        'old_rows': {role: sparse_json(row) for role, row in original.items()},
        'extra_column': sparse_json({role: value for role, value in enumerate(dirty) if value}),
        'exterior_extra_column': sparse_json(outside),
        'prior_outward_add': outward,
        'later_outward_add': {'clock': 42502, 'old_source_term': sparse_json(retained_add),
                             'extra_coefficient': str(-dirty[ROLE] / 2)},
        'dirty_guard_failures': [[*event[:3], str(event[3])] for event in guards],
        'nonzero_owned_clears': [[*event[:3], str(event[3])] for event in dirty_clears],
        'separators': certificates,
        'representations': solutions,
    }
    alarm(0)
    print(dumps(receipt, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
