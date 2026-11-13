"""Independent dense forward check of one exact #7481 late receiver bank."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
ROLE, EARLY, CUT, LATE = 749, 32222, 35152, 35155
GRID = 1125 * 2**25
COMPRESSED = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PAYLOAD = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'


def timeout(signum, frame):
    print(dumps({'status': 'unresolved_timeout', 'cases_completed': 0, 'cap_seconds': 30}))
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
    assert tape[EARLY:EARLY + 4] == [['MOVE', ROLE, 3, 260, False], ['ADD', 1540, ROLE, '-1', 260],
                                    ['ADD', 210, 526, '2', 3], ['ADD', ROLE, 990, '1', 260]]
    assert tape[35142] == ['SCALE', ROLE, '4', 260]
    assert tape[35143:CUT] == [['INIT', 1541, 599]] + [
        event for role in (1347, 1346, 1344, 1343)
        for event in (['MOVE', role, 3, 599, False], ['ADD', 1541, role, '-1', 599])]
    assert tape[CUT:LATE] == [['MOVE', 1541, 599, 260, True], ['ADD', ROLE, 1541, '1', 260],
                              ['ADD', 1540, ROLE, '1/4', 260]]
    assert tape[LATE] == ['ADD', 1540, 1393, '-1/4', 260]
    public = word['public']
    zero = [0] * public
    rows = [zero] * (public + word['owned_fields'])
    for index in range(public):
        row = zero.copy()
        row[index] = GRID
        rows[index] = row
    charts = word['initial'] + [None] * word['owned_fields']
    early_role = None
    source, destination = {}, {}
    for clock, (op, dst, *args) in enumerate(tape[:LATE]):
        if clock == EARLY:
            early_role = rows[ROLE]
        if clock == CUT:
            source = {role: row for role, row in enumerate(rows) if charts[role] == 599 and role != 1541}
            destination = {role: row for role, row in enumerate(rows)
                           if charts[role] == 260 and role not in (ROLE, 1540)}
        if op == 'INIT':
            assert charts[dst] is None and not any(rows[dst])
            charts[dst] = args[0]
        elif op == 'CLEAR':
            assert charts[dst] == args[0]
            charts[dst] = None
            rows[dst] = zero
        elif op == 'MOVE':
            assert charts[dst] == args[0] and args[2] == (dst >= public)
            charts[dst] = args[1]
        elif op == 'SCALE':
            assert charts[dst] == args[1]
            rows[dst] = scaled(rows[dst], Q(args[0]))
        else:
            src, coefficient, chart = args
            assert op in ('ADD', 'COPY') and charts[src] == charts[dst] == chart
            if op == 'COPY':
                assert not any(rows[dst])
                rows[dst] = scaled(rows[src], Q(coefficient))
            else:
                increment = scaled(rows[src], Q(coefficient))
                rows[dst] = [a + b for a, b in zip(rows[dst], increment)]
    assert set(source) == {1343, 1344, 1346, 1347}
    assert set(destination) == {226, 988, 990, 1345, 1393, 1506, 1514}
    assert early_role is not None
    assert rows[ROLE] == [GRID if j == ROLE else 0 for j in range(public)]
    assert all(rows[1540][j] == -early_role[j] + Q(rows[ROLE][j], 4) for j in range(public))
    return source, destination, {ROLE: rows[ROLE], 1540: rows[1540]}, early_role


def sparse(row):
    return {j: Q(value) / GRID for j, value in enumerate(row) if value}


def subtract(row, other, scale):
    for key, value in other.items():
        coefficient = row.get(key, Q(0)) - scale * value
        if coefficient:
            row[key] = coefficient
        else:
            row.pop(key, None)


def reduce_row(row, basis):
    result = row.copy()
    for pivot, vector in sorted(basis.items()):
        if pivot in result:
            subtract(result, vector, result[pivot])
    return result


def echelon(rows):
    basis = {}
    for row in rows:
        remaining = reduce_row(row, basis)
        if remaining:
            pivot = min(remaining)
            basis[pivot] = {k: v / remaining[pivot] for k, v in remaining.items()}
    return basis


def dot(row, probe):
    return sum((value * probe.get(j, Q(0)) for j, value in row.items()), Q(0))


def dual_probe(free, basis):
    assert free not in basis
    probe = {free: Q(1)}
    for pivot, row in sorted(basis.items(), reverse=True):
        value = -dot(row, probe)
        if value:
            probe[pivot] = value
    return probe


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    compressed = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(compressed).hexdigest() == COMPRESSED
    raw = decompress(compressed)
    assert sha256(raw).hexdigest() == PAYLOAD
    source, destination, targets, early = replay(loads(raw))
    source = {role: sparse(row) for role, row in source.items()}
    destination = {role: sparse(row) for role, row in destination.items()}
    targets = {role: sparse(row) for role, row in targets.items()}
    early = sparse(early)
    bank = list(destination.values())
    required = list(targets.values())
    basis = echelon(bank)
    residuals = [reduce_row(row, basis) for row in required]
    quotient_rank = len(echelon(residuals))
    probe_pair = []
    if quotient_rank == 2:
        first = min(residuals[0])
        probe1 = dual_probe(first, basis)
        second_basis = echelon(bank + required[:1])
        second = min(reduce_row(required[1], second_basis))
        probe2 = dual_probe(second, second_basis)
        probe_pair = [probe1, probe2]
        assert all(not dot(row, probe) for row in bank for probe in probe_pair)
        assert dot(required[0], probe1) and not dot(required[0], probe2) and dot(required[1], probe2)
    source_basis = echelon([early, *source.values()])
    source_target_residual = reduce_row(required[0], source_basis)
    source_probe = dual_probe(min(source_target_residual), source_basis) if source_target_residual else {}
    if source_probe:
        assert all(not dot(row, source_probe) for row in [early, *source.values()])
        assert dot(required[0], source_probe)
    receipt = {
        'status': 'EXACT_RECEIVER_QUOTIENT_EXCLUSION' if quotient_rank == 2 else 'RECEIVER_QUOTIENT_GATE_SURVIVES',
        'case': {'role': ROLE, 'early': EARLY, 'cut': CUT, 'late': LATE, 'runner_cap_seconds': 30},
        'cases_completed': 1, 'compressed_sha256': COMPRESSED, 'payload_sha256': PAYLOAD,
        'source_donors': list(source), 'receiver_donors': list(destination),
        'receiver_rank': len(basis), 'receiver_union_rank': len(echelon(bank + required)),
        'receiver_quotient_rank': quotient_rank, 'receiver_probes': probe_pair,
        'receiver_probe_target_values': [[dot(row, probe) for row in required] for probe in probe_pair],
        'source_span_rank': len(source_basis), 'source_target_representable': not source_target_residual,
        'source_target_probe': source_probe,
        'source_probe_target_value': dot(required[0], source_probe),
    }
    alarm(0)
    print(dumps(receipt, indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
