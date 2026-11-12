"""Check one original-address stage-17 residual entry and the fixed scalar interval."""
from ast import Assign, Name, literal_eval, parse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

CAP = 20
CLOCKS = (4646, 4660)
ROLES = (36, 37, 52, 53)
AXES = tuple(range(137, 145))
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS = {
    'inputs/7113-SHA256.json': '064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078',
    'inputs/7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/PHYSICAL-BINDING.json': 'ade5f8cbb2e30677b1d48d23a1aa270b3d0b72e2504472ab9fdb71d124b075b5',
    'inputs/R173-INDEPENDENT.json': 'd53dfc746467daff3bddf25fd7d2ce11d2d984f0bd71c14d18277c6a0dad7b32',
    'receipts/7416-LEAD.json': '95f89deb1952b9e72181dbfc58e72208a27b14ba014839ec19bf8505bb2f0f26',
}


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), 'duplicate JSON key'
    return values


def source(root, path):
    data = (root / path).read_bytes()
    assert sha256(data).hexdigest() == PINS[path], f'wrong input hash: {path}'
    return loads(data, object_pairs_hook=unique) if path.endswith('.json') else data


def gaussian_product(left, right):
    a, b = left
    c, d = right
    return a*c - b*d, a*d + b*c


def address_entry(child):
    numerator = next(literal_eval(node.value) for node in parse(child).body
                     if isinstance(node, Assign) and isinstance(node.targets[0], Name)
                     and node.targets[0].id == 'C')
    gate = tuple(tuple(tuple(Q(x, 2) for x in entry) for entry in row) for row in numerator)
    a = (Q(1, 2), Q(1, 2))
    assert all(gate[r][s] == (a if r == s else gaussian_product(a, (0, -1)))
               for r in (0, 1) for s in (0, 1))
    # Probe one original-address neighbour, x=0 and y=1. The diagonal
    # product on eight bits also fixes the scalar in the all-width formula.
    result, diagonal = (Q(1), Q(0)), (Q(1), Q(0))
    for bit in range(len(AXES)):
        result = gaussian_product(result, gate[(1 >> bit) & 1][0])
        diagonal = gaussian_product(diagonal, a)
    assert diagonal == (Q(1, 16), Q(0)) and result == (Q(0), Q(-1, 16))
    # E uses only the identity and the full eight-bit complement.
    assert 1 not in (0, (1 << len(AXES)) - 1)
    return result


def apply(events, column, inverse=False):
    for _, op, dest, *args in reversed(events) if inverse else events:
        i = ROLES.index(dest)
        if op == 'ADD':
            src, coefficient = args
            column[i] += (-1 if inverse else 1) * Q(coefficient) * column[ROLES.index(src)]
        else:
            coefficient, = args
            column[i] *= Q(coefficient) ** (-1 if inverse else 1)
    return column


def multiply(left, right):
    return [[sum(a*b for a,b in zip(row, column, strict=True))
             for column in zip(*right, strict=True)] for row in left]


def frame_trace(caller, inherited):
    start, stop = CLOCKS
    tape = caller['events']
    assert len(tape) == 4783 and caller['ambient_rank'] == 145
    assert all(tape[clock] == ['B', 'IDLE_ONE', 36, [17]] for clock in CLOCKS)
    middle = tape[start + 1:stop]
    counts = Counter()
    for kind, op, dest, *args in middle:
        assert kind == 'B' and op in ('ADD', 'SCALE') and dest in ROLES
        if op == 'ADD':
            assert args[0] in ROLES and args[0] != dest
        else:
            assert Q(args[0])
        counts[op] += 1
    assert len(middle) == 13 and counts == {'ADD': 11, 'SCALE': 2}
    identity = [[Q(i == j) for j in range(len(ROLES))] for i in range(len(ROLES))]
    m, mi = [list(map(list, zip(*(apply(middle, x.copy(), inverse) for x in identity), strict=True)))
             for inverse in (False, True)]
    assert multiply(m, mi) == multiply(mi, m) == identity
    assert m[0][0] == mi[0][0] == 0
    e = [[Q(i == j == 0) for j in range(len(ROLES))] for i in range(len(ROLES))]
    f = multiply(multiply(mi, e), m)
    assert not any(any(row) for product in (multiply(e, f), multiply(f, e)) for row in product)
    p = [[a+b for a,b in zip(x,y,strict=True)] for x,y in zip(e,f,strict=True)]
    assert multiply(p, p) == p and sum(p[i][i] for i in range(len(ROLES))) == 2
    assert p == [[Q(x) for x in row] for row in inherited['projector']]
    return middle, counts, p


def stop(*_):
    raise TimeoutError('20-second fixed stage-17 original-address gate cap')


def main(root):
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    signal(SIGALRM, stop)
    alarm(CAP)
    manifest = source(root, 'inputs/7113-SHA256.json')
    for bundled, original in [('CALLER.json', 'expected/ODD-TYPE-AB-CALLER.json'),
                              ('PHYSICAL-BINDING.json', 'expected/ODD-PHYSICAL-BINDING.json'),
                              ('7113-signed-child.py', 'replay/supplier7112/short-caller/signed_child.py')]:
        assert manifest[original] == PINS[f'inputs/{bundled}']
    caller = source(root, 'inputs/CALLER.json')
    binding = source(root, 'inputs/PHYSICAL-BINDING.json')
    child = source(root, 'inputs/7113-signed-child.py')
    inherited = source(root, 'inputs/R173-INDEPENDENT.json')
    price = source(root, 'receipts/7416-LEAD.json')
    assert (inherited['benchmark'], inherited['caller'], inherited['clocks']) == (HEAD, CALLER, list(CLOCKS))
    assert (price['head'], price['caller'], price['clocks']) == (HEAD, CALLER, list(CLOCKS))
    assert binding['caller_sha256'] == PINS['inputs/CALLER.json']
    assert binding['occurrence_and_geometry']['ambient'] == 145
    assert inherited['stage'] == 17 and inherited['physical_stage_axes'] == list(AXES)
    assert inherited['ports'] == caller['types']['B']['ports'] == [15, 17, 27, 34, 35, 42, 47, 55]
    middle, counts, p = frame_trace(caller, inherited)
    result = address_entry(child)
    gross = price['affine_chart_raw_gain']
    assert Q(gross[1]) < Q('-126.39')
    assert Q(price['rank16_affordability'][1]) < Q('1.003')
    alarm(0)
    print(dumps({'head': HEAD, 'caller': CALLER, 'pins': PINS, 'clocks': CLOCKS,
                 'inherited_axis_ids': AXES, 'window': middle, 'role_scalar_counts': counts,
                 'literal_address_basis_bridge_in_window': False,
                 'normalized_role_projector': [[str(x) for x in row] for row in p],
                 'normalized_residual_lanes': 2, 'width': 1, 'address_pair': [1, 0],
                 'residual_entry': [str(x) for x in result],
                 'all_width_hamming_neighbour': '-i * 2^(-4f)',
                 'coordinate_only_minimum_old_lane_volumes': 2,
                 'two_lane_raw_interval_from_7416': gross, 'runner_cap_seconds': CAP}, sort_keys=True, indent=2))


if __name__ == '__main__':
    assert len(argv) == 2, 'pass the package root with bundled pinned inputs'
    main(Path(argv[1]).resolve())
