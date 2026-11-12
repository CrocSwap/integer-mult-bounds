"""Exact independent width-two five-parity sketch capacity check."""
from ast import Assign, Name, literal_eval, parse
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

CAP = 20
F = 2
M = 8 * F
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PREDECESSOR = '8401b466472bc1a7e5b1fc6c8ba21c5de056e4b9'
CLOCKS = (4646, 4660)
ROLES = (36, 37, 52, 53)
PINS = {
    'inputs/7113-SHA256.json': '064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078',
    'inputs/7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/PHYSICAL-BINDING.json': 'ade5f8cbb2e30677b1d48d23a1aa270b3d0b72e2504472ab9fdb71d124b075b5',
    'inputs/7397-PROOF.md': '1b5f670a1fd044b92905639b2cfb81eaf71c1dcdf63c114b73d2841919c58e32',
    'receipts/INDEPENDENT.json': '435620f25a7f15c2d67a0a511e6d7d699b0cfb307a0fd053c09d84dbe8ac1bbb',
    'receipts/LEAD.json': '95f89deb1952b9e72181dbfc58e72208a27b14ba014839ec19bf8505bb2f0f26',
}


def no_duplicates(items):
    obj = dict(items)
    assert len(obj) == len(items)
    return obj


def pin(root, path):
    raw = (root / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return loads(raw, object_pairs_hook=no_duplicates) if path.endswith('.json') else raw


def unit(j):
    return [Q(i == j) for i in range(4)]


def run_scalar(events, x, inverse=False):
    x = x.copy()
    for kind, op, role, *args in reversed(events) if inverse else events:
        assert kind == 'B'
        dst = ROLES.index(role)
        if op == 'ADD':
            src, weight = args
            x[dst] += Q(weight) * (-1 if inverse else 1) * x[ROLES.index(src)]
        else:
            assert op == 'SCALE'
            x[dst] *= Q(args[0]) ** (-1 if inverse else 1)
    return x


def stage(caller, previous):
    events = caller['events']
    a, b = CLOCKS
    assert len(events) == 4783 and all(events[i] == ['B', 'IDLE_ONE', 36, [17]] for i in CLOCKS)
    between = events[a+1:b]
    assert len(between) == 13
    forward = [run_scalar(between, unit(j)) for j in range(4)]
    backward = [run_scalar(between, unit(j), inverse=True) for j in range(4)]
    assert all(run_scalar(between, col) == unit(j) for j, col in enumerate(backward))
    assert forward[0][0] == backward[0][0] == 0
    columns = [[u + forward[j][0] * v for u, v in zip([Q(i == j == 0) for i in range(4)], backward[0], strict=True)]
               for j in range(4)]
    assert list(map(list, zip(*columns, strict=True))) == [[Q(x) for x in row] for row in previous['projector']]
    assert sum(columns[i][i] for i in range(4)) == 2
    return [[str(x) for x in row] for row in zip(*columns, strict=True)]


def pop_parity(x):
    return x.bit_count() & 1


def quadratic(x):
    w = x.bit_count()
    return ((w * (w-1)) // 2) & 1


def polar(x, y):
    return pop_parity(x & y) ^ (pop_parity(x) & pop_parity(y))


def rank2(rows):
    pivots = {}
    for r in rows:
        while r:
            p = r.bit_length()-1
            if p not in pivots:
                pivots[p] = r
                break
            r ^= pivots[p]
    return len(pivots)


def form_rows(basis):
    return [sum(polar(x, y) << j for j, y in enumerate(basis)) for x in basis]


def stop(*_):
    raise TimeoutError('R215 independent 20-second cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 2, 'pass exact #7416 research package root'
    root = Path(argv[1]).resolve()
    signal(SIGALRM, stop)
    alarm(CAP)
    source = {p: pin(root, p) for p in PINS}
    manifest = source['inputs/7113-SHA256.json']
    assert manifest['expected/ODD-TYPE-AB-CALLER.json'] == PINS['inputs/CALLER.json']
    assert manifest['expected/ODD-PHYSICAL-BINDING.json'] == PINS['inputs/PHYSICAL-BINDING.json']
    assert manifest['replay/supplier7112/short-caller/signed_child.py'] == PINS['inputs/7113-signed-child.py']
    previous, quote = [source['receipts/'+engine+'.json'] for engine in ('INDEPENDENT','LEAD')]
    for p in (previous, quote):
        assert (p['head'], p['caller'], tuple(p['clocks'])) == (HEAD, CALLER, CLOCKS)
    assert previous['selected_axes'] == list(range(137, 145)) and quote['selected_bits'] == 8
    binding = source['inputs/PHYSICAL-BINDING.json']
    assert binding['caller_sha256'] == PINS['inputs/CALLER.json'] and binding['occurrence_and_geometry']['ambient'] == 145
    projector = stage(source['inputs/CALLER.json'], previous)
    c = next(literal_eval(n.value) for n in parse(source['inputs/7113-signed-child.py']).body
             if isinstance(n, Assign) and isinstance(n.targets[0], Name) and n.targets[0].id == 'C')
    for sign, twice_eigen in ((1, (2, 0)), (-1, (0, 2))):
        for i in (0, 1):
            assert tuple(c[i][0][k]+sign*c[i][1][k] for k in (0, 1)) == tuple(sign**i*t for t in twice_eigen)
    affordability = Q(quote['rank16_affordability'][1])
    assert affordability == Q(previous['affordability_upper']) < Q('1.003')
    n = 1 << M
    standard = [1 << j for j in range(M)]
    assert all(polar(x, y) == quadratic(x ^ y) ^ quadratic(x) ^ quadratic(y) for x in standard for y in standard)
    assert rank2(form_rows(standard)) == M
    masks = [n-1, *[3 << (2*j) for j in range(4)]]
    kernel = [*masks[1:], *[(1 << 8) | (1 << i) for i in range(9, 16)]]
    assert rank2(masks) == 5 and rank2(kernel) == 11
    assert all(not pop_parity(m & v) for m in masks for v in kernel)
    assert rank2(form_rows(kernel)) == 6
    cases = [[0]*4 for _ in range(32)]
    for x in range(n):
        k = sum(pop_parity(x & mask) << j for j, mask in enumerate(masks))
        residue = x.bit_count() % 4
        assert residue == pop_parity(x) + 2*quadratic(x)
        cases[k][residue] += 1
    assert all(sum(row) == 1 << 11 for row in cases)
    peak = max(max(row) for row in cases)
    assert Q(peak,1<<11) == Q(9,16)
    max_bias = max(abs(Q(row[0]+row[1]-row[2]-row[3], 1<<11)) for row in cases)
    assert max_bias == Q(1,8)
    extremal = [k for k,row in enumerate(cases) if max(row) == peak]
    exact_control_min_displacement = 2*(n-sum(map(max,cases)))
    core = [1,0,0,0]
    for _ in range(16*F):
        core = [core[i]+core[(i-1)%4] for i in range(4)]
    core_fixed = Q(core[0], 1 << (16*F))
    assert core_fixed == Q(1,4)+Q(1,1<<17)
    required = Q(7,8)*n
    core_capacity = Q(3,4)
    volume_lower = required / (n*core_capacity)
    assert volume_lower == Q(7,6) > affordability
    alarm(0)
    print(dumps({'head':HEAD,'caller':CALLER,'pr7416':PREDECESSOR,'pins':PINS,'clocks':CLOCKS,
                 'local_projector':projector,'f':F,'bits':M,'addresses':n,'sketch_probes':masks,
                 'restricted_polar_rank':6,'coset_phase_counts':cases,'max_phase_fraction':'9/16',
                 'max_quadratic_bias':str(max_bias),'extremal_cosets':extremal,
                 'exact_control_min_displacement':exact_control_min_displacement,
                 'universal_required_displacement':str(required),'core_phase_counts':core,
                 'core_fixed_fraction':str(core_fixed),'core_capacity_fraction_upper':str(core_capacity),
                 'required_volume_lower':str(volume_lower),'affordability_upper':str(affordability),
                 'runner_cap_seconds':CAP},sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
