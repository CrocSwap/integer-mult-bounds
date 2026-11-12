"""Replay the pinned signed-factor scope and check the actual D8-gauged witness."""
from fractions import Fraction as Q
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE / 'closure'


def check_pins():
    pins = {}
    for line in (PACKAGE / 'PINS.txt').read_text().splitlines():
        digest, path = line.split()
        assert path not in pins and sha256((PACKAGE / path).read_bytes()).hexdigest() == digest, path
        pins[path] = digest
    assert set(pins) == {f.relative_to(PACKAGE).as_posix() for f in ROOT.rglob('*') if f.is_file()}


def checked(script, expected, args=(), timeout=30, isolated=True):
    flags = ['-I', '-B'] if isolated else ['-E', '-B']
    proc = run([executable, *flags, str(ROOT / script), *map(str, args)],
               capture_output=True, check=True, timeout=timeout)
    assert not proc.stderr, script
    actual = loads(proc.stdout)
    stored = loads((ROOT / expected).read_bytes())
    if 'seconds' in actual:
        assert 0 <= actual.pop('seconds') < 60
        assert 0 <= stored.pop('seconds') < 60
    else:
        assert proc.stdout == (ROOT / expected).read_bytes(), script
    assert actual == stored, script
    return actual


def matrix(columns):
    return [[Q(x) for x in c] for c in columns]


def unit(size, j):
    return [Q(i == j) for i in range(size)]


def dot(left, right):
    return sum(a*b for a,b in zip(left, right, strict=True) if a and b)


def apply(factors, column):
    for image, covector in reversed(factors):
        assert any(image) and any(covector) and dot(image, covector) == 0
        val = dot(covector, column)
        column = [x + val * y for x, y in zip(column, image, strict=True)]
    return column


def compare_profiles(unit_target, literal, independent, witness):
    size = 36
    flipped = [*range(9, 18), *range(27, 36)]
    assert independent['gauge_negative_roles'] == flipped
    e = [(-1 if i in flipped else 1) for i in range(size)]
    target = matrix(literal['target_columns'])
    assert len(target) == size
    assert literal['rank'] == independent['rank'] == witness['rank'] == 19
    assert independent['minor_determinant'] == '524288'
    assert len(literal['changed_entries']) == independent['unit_target_changes'] == 153
    assert independent['first_unit_target_change'] == [27, 1, '4']
    assert literal['mutant_basis'] == independent['changed_body_scale_rejected_basis'] == 0
    for j, d in enumerate(matrix(independent['displacement_columns'])):
        assert [x+u for x,u in zip(d, unit(size,j), strict=True)] == target[j]
    factors = [(list(map(Q, u)), list(map(Q, v))) for u, v in witness['factors']]
    assert len(factors) == 19
    gauged = [([s*x for s,x in zip(e,u,strict=True)], [s*x for s,x in zip(e,v,strict=True)]) for u,v in factors]
    assert target != unit_target
    for j in range(size):
        assert apply(factors, unit(size,j)) == unit_target[j]
        assert apply(gauged, unit(size,j)) == target[j]
        assert [e[i]*value*e[j] for i,value in enumerate(unit_target[j])] == target[j]
    assert apply(factors, unit(size,1)) != target[1]


def price():
    low, high = map(Q, loads((ROOT/'lead/inputs/R194.json').read_bytes())['price'])
    assert Q('50.33412118538') < low < high < Q('50.33412118539')
    paid = 16 + 19 - 2
    assert paid == 33
    all_direct_upper = 17*(high+96)-paid*96
    assert all_direct_upper == Q('-1700799849621348281604535419004036353191280335045953/2500000000000000000000000000000000000000000000000')
    assert all_direct_upper < Q('-680.3199')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3,12)
    check_pins()
    lead208 = checked('lead/dependency.py','lead/RESULT.json')
    ind208 = checked('independent/replay.py','independent/RESULT.json',(ROOT/'lead',))
    assert lead208['minimum_support'] == len(ind208['least_support']) == 19
    assert lead208['chosen'] == ind208['least_support'] and ind208['literal_rank'] == 18
    frozen208 = ROOT/'lead/RESULT.json'
    short208 = checked('construct/run.py','construct/RESULT.json',
                      (frozen208,sha256(frozen208.read_bytes()).hexdigest()),timeout=62,isolated=False)
    assert short208['rank'] == 18 and short208['involution'] and short208['minimum_transvections'] == 19
    lead209 = checked('round209/lead/plane_gate.py','round209/lead/RESULT.json')
    ind209 = checked('round209/independent/replay.py','round209/independent/RESULT.json',
                     (ROOT/'independent/replay.py', ROOT/'lead'))
    assert lead209['target_columns'] == ind209['target_columns']
    assert lead209['rank'] == ind209['displacement_rank'] == 19
    unit_target = matrix(lead209['target_columns'])
    for j,col in enumerate(unit_target):
        assert col[:18] == [Q(-1 if i == j else 0) for i in range(18)]
        if j >= 18:
            diagonal = unit(36,j)[18:]
            if j in (18,19):
                diagonal[0] += 2 if j==18 else -2
                diagonal[1] += 2 if j==18 else -2
            assert col[18:] == diagonal
    assert sum(bool(x) for c in unit_target[:18] for x in c[18:]) == 306
    assert ind209['blocks'][2]['displacement_rank'] == 1
    frozen209 = ROOT/'round209/lead/RESULT.json'
    short209 = checked('round209/construction/run.py','round209/construction/RESULT.json',
                      (frozen209,sha256(frozen209.read_bytes()).hexdigest()),timeout=62)
    assert short209['minimum_transvections'] == short209['cross_plane_factors'] == 19
    assert short209['nondyadic_factors'] == 0
    lead210 = checked('round210/lead/body_gate.py','round210/lead/RESULT.json',timeout=35)
    ind210 = checked('round210/independent/replay.py','round210/independent/RESULT.json',
                     (ROOT/'lead',ROOT/'round209/independent/RESULT.json'),timeout=35)
    compare_profiles(unit_target, lead210, ind210, short209)
    price()
    print('PASS_SIGNED_FACTOR_CIRCUITS: minimum 19, 20-to-19 witness, 19 crossings, exact D8 gauge and negative direct-host price')


if __name__ == '__main__':
    main()
