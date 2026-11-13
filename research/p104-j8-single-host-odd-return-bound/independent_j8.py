"""Check one physical central phase fibre and its fixed-wrapper rank gate."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from functools import reduce
from itertools import product
from operator import xor
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
PINS = {
    '7113-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    '7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    'upstream_application.py': 'd98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184',
    '7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
}


def timeout(signum, frame):
    print(dumps({'status': 'unresolved_timeout', 'cases_completed': 0, 'cap_seconds': 30}))
    exit(124)


def parity_polynomial(terms):
    out = {}
    for axes, coefficient in terms:
        support = [1 << j for j in range(145) if axes & (1 << j)]
        for j, a in enumerate(support):
            out[(a,)] = (out.get((a,), 0) + coefficient) % 4
            for b in support[j + 1:]:
                out[a, b] = (out.get((a, b), 0) - 2 * coefficient) % 4
    return {indices: value for indices, value in out.items() if value}


def rank(matrix):
    rows = [list(map(Q, row)) for row in matrix]
    pivots = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(pivots, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pivots], rows[pivot] = rows[pivot], rows[pivots]
        top = rows[pivots]
        for row in rows[pivots + 1:]:
            multiplier = row[col] / top[col]
            for j in range(col, len(row)):
                row[j] -= multiplier * top[j]
        pivots += 1
    return pivots


def evaluate(terms, walsh_bits):
    return sum(weight * ((mask & walsh_bits).bit_count() % 2) for mask, weight in terms) % 4


def phase_sign(terms, walsh_slices):
    exponent = sum(evaluate(terms, bits) for bits in walsh_slices) % 4
    assert exponent in (0, 2)
    return 1 if exponent == 0 else -1


def difference(plus, minus):
    return [[a - b for a, b in zip(top, bottom)] for top, bottom in zip(plus, minus)]


def determinant3(m):
    a, b, c = m
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    data = {name: (ROOT / name).read_bytes() for name in PINS}
    assert {name: sha256(value).hexdigest() for name, value in data.items()} == PINS
    payload = decompress(data['7481-WORD.json.gz'])
    assert sha256(payload).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(payload)
    caller = loads(data['7113-CALLER.json'])
    events = caller['events']
    stage, port, central, rail = 8, 15, 81, 68
    idle_clock, host_clock = 1339, 1423
    idle, host = events[idle_clock], events[host_clock]
    assert caller['ambient_rank'] == 145 and caller['stages'] == 17
    assert caller['types']['B']['ports'][0] == port and word['ports'][port] == central
    assert port not in word['hosted']['Dports']
    assert idle == ['B', 'IDLE_ODD', rail, [stage], -1]
    assert host == ['J', stage, [8, 0, 18, 26], [36, 37, '-1', '1/2']]
    x = word['live'][port]
    y = x + 112
    assert word['frames'][word['initial'][x]] == [central]
    assert word['frames'][word['initial'][y]] == []
    assert word['frames'][word['final'][x]] == [1 << j for j in range(9)]
    end_y = word['frames'][word['final'][y]]
    assert len(end_y) == 8 and all(not ((central & a).bit_count() % 2) for a in end_y)
    for index, event in enumerate(events):
        if event[0] == 'J':
            assert rail not in event[3][:2]
        elif event[0] == 'B' and index != idle_clock:
            operands = 2 if event[1] in ('ADD', 'SWAP', 'QUERY') else 1
            assert rail not in event[2:2 + operands]
    # Independently reconstruct input/output phase exponents as in the
    # pinned physical application: X carries all current axes; Y omits q.
    before = [(1 << j, 1) for j in range(9 + 8 * (stage - 1))]
    body = [1 << j for j in range(9 + 8 * (stage - 1), 9 + 8 * stage)]
    after = before + [(axis, 1) for axis in body]
    y_before, y_after = before + [(central, -1)], after + [(central, -1)]
    contact_terms = [[dst + [(axis, -weight) for axis, weight in src]
                      for src in (before, y_before)] for dst in (after, y_after)]
    expected = [[[(axis, 1) for axis in body] + ([(central, 1)] if r < s else
                  [(central, -1)] if s < r else []) for s in range(2)] for r in range(2)]
    assert [[parity_polynomial(t) for t in row] for row in contact_terms] == [
        [parity_polynomial(t) for t in row] for row in expected]
    axes = [central] + body
    gram = [[(a & b).bit_count() % 2 for b in axes] for a in axes]
    assert gram == [[int(i == j) for j in range(9)] for i in range(9)]
    assert len({reduce(xor, (a for a, bit in zip(axes, flags) if bit), 0)
                for flags in product((0, 1), repeat=9)}) == 512
    child = run_path(str(ROOT / '7113-signed-child.py'))
    C = child['C']
    assert [[sum(C[r][j][k] * (1, 1)[j] for j in range(2)) for k in range(2)]
            for r in range(2)] == [[2, 0], [2, 0]]
    assert [[sum(C[r][j][k] * (1, -1)[j] for j in range(2)) for k in range(2)]
            for r in range(2)] == [[0, 2], [0, -2]]
    alpha, beta = map(Q, host[3][2:])
    assert [Q(word['hosted'][name]) for name in ('alpha', 'beta')] == [alpha, beta]
    coefficient = [[Q(1), alpha], [beta, 1 + alpha * beta]]
    # At width two, use the all-positive body and either zero or two
    # negative Walsh bits along q. They give q=+1 or q=-1, respectively.
    # Pick a central bit whose dot product with q is one. The two width
    # slices are independent and all body Walsh bits remain zero.
    central_selector = central & -central
    sector_bits = ((0, 0), (central_selector, central_selector))
    sectors = []
    central_exponents = []
    for walsh_bits in sector_bits:
        central_exponent = sum(evaluate([(central, 1)], bits) for bits in walsh_bits) % 4
        central_exponents.append(central_exponent)
        contact_phases = [[phase_sign(terms, walsh_bits) for terms in row] for row in contact_terms]
        host_matrix = [[coefficient[r][s] * contact_phases[r][s] for s in range(2)] for r in range(2)]
        old = [row + [Q(0)] for row in host_matrix]
        old.append([Q(0), Q(0), Q(1) if central_exponent == 0 else Q(-1)])
        sectors.append(old)
    assert central_exponents == [0, 2]
    changed = difference(*sectors)
    host_difference = [row[:2] for row in changed[:2]]
    assert rank(host_difference) == 2 and rank(changed) == 3 and determinant3(changed) == 4
    assert rank([row[:2] for row in changed[:2]]) == 2
    receipt = {
        'status': 'PASS_INDEPENDENT_J8_FIXED_FIBRE_RANK', 'pins': PINS,
        'case': {'port': port, 'stage': stage, 'rail': rail, 'host_roles': host[3][:2],
                 'idle_event': idle_clock, 'host_event': host_clock, 'cap_seconds': 30},
        'cases_completed': 1, 'native_roles': [x, y], 'physical_axes': axes,
        'axis_gram': gram, 'physical_width_one_span': 512,
        'sector_pair': [1, -1], 'sector_witness_width': 2, 'sector_walsh_slices': sector_bits,
        'shared_nonzero_body': 1,
        'host_odd_rank': rank(host_difference), 'required_odd_rank': rank(changed),
        'required_odd_difference': changed, 'required_odd_determinant': determinant3(changed),
        'single_removed_rail_control_rank': rank(host_difference),
        'wrapper_contract': 'arbitrary linear ingress and egress with sector-identical matrices on the paired body fibre and only sector-identical bypass contributions',
    }
    alarm(0)
    print(dumps(receipt, indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
