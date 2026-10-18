"""Exact rank-transport controls, including independent dense Clifford replay."""
if not __debug__:
    raise SystemExit('Run without -O: inherited Clifford checks require assertions.')

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from field import E, ZERO, ONE, OMEGA
from transport import require, point, audit, inverse_matrix, check_metrics
import model


def block(entries):
    return ('mix3', *(E.cast(x) for x in entries))


def controls():
    roots = (ONE, OMEGA, OMEGA*OMEGA)
    require(sum(roots, ZERO) == 0 and roots[1]*roots[2] == 1, 'Cyclotomic identity failed')
    fourier = tuple(roots[(r*c) % 3] for r in range(3) for c in range(3))
    grover = tuple(E(2-3*int(r == c))/3 for r in range(3) for c in range(3))
    diagonal = tuple(roots[r] if r == c else ZERO for r in range(3) for c in range(3))
    for matrix in (fourier, grover, diagonal):
        inv = inverse_matrix(matrix)
        for r in range(3):
            for c in range(3):
                require(sum((matrix[3*r+k]*inv[3*k+c] for k in range(3)), ZERO) == int(r == c),
                        'Exact scalar inverse failed')
    nine = []
    for axis in (1, 2, 4):
        nine.extend(('paid', r, axis) for r in range(3))
        nine.append(block(grover))
    nine = tuple(nine)
    eight = tuple(g for i, g in enumerate(nine) if i != 8)
    require(sum(g[0] == 'paid' for g in eight) == 8, 'Wrong eight-call control')
    cases = {'unitary-nine': nine, 'unitary-eight': eight}
    # U is genuinely non-real and exactly unitary over Q(omega).
    unitary = tuple(grover[3*r+c]*roots[c] for r in range(3) for c in range(3))
    scales = [(1, 2, 3), (2, 3, 1), (3, 1, 2), (1, 3, 2)]
    matrices = [tuple(unitary[3*r+c]*Q(scales[k][c], scales[k+1][r])
                      for r in range(3) for c in range(3)) for k in range(3)]
    metrics = [[Q(x*x) for x in s] for s in scales]
    check_metrics(matrices, metrics)
    gauged = []
    for k, axis in enumerate((1, 2, 4)):
        gauged.append(block(matrices[k]))
        gauged.extend(('paid', r, axis) for r in range(3))
    cases['diagonally-gauged-nine'] = tuple(gauged)
    cases['diagonally-gauged-eight'] = tuple(gauged[:-1])
    # An exact local gain >1 from a paid call; this is NOT an endpoint.
    cases['signed-excess'] = (('paid', 1, 1), block([1, 2, 0, 2, 1, 0, 0, 0, 1]), ('paid', 1, 1))
    # Potential 9 is necessary but not sufficient for a rank-three endpoint.
    cases['false-potential-nine'] = (('paid', 1, 1), block([1, Q(3, 2), 0, 1, 1, 0, 0, 0, 1]),
                                     ('paid', 1, 1), ('paid', 2, 1), ('paid', 2, 2), ('paid', 2, 4))
    # Amplifying correct coefficients does not complete the missing rank.
    deceptive = [block([1, 0, 10, 0, 1, 10, 0, 0, 1])]
    deceptive.extend(('paid', r, axis) for r in range(3)
                     for axis in ((1, 2) if r == 2 else (1, 2, 4)))
    cases['amplification-trap'] = tuple(deceptive)
    reports = {name: audit(word, independent=True) for name, word in cases.items()}
    for name in ('unitary-nine', 'diagonally-gauged-nine'):
        require(reports[name]['endpoint'] is not None and reports[name]['potential'] == '9', 'Positive control failed')
        require(reports[name]['paid_negative_mass'] == '0', 'Gauge-unitary positivity failed')
    for name in ('unitary-eight', 'diagonally-gauged-eight'):
        require(reports[name]['endpoint'] is None and Q(reports[name]['potential']) <= 8, 'Eight-call control failed')
        require(reports[name]['paid_negative_mass'] == '0', 'Eight-call positivity failed')
    excess = reports['signed-excess']
    require(excess['potential'] == '8/3' and excess['paid_steps'][-1]['delta'] == '5/3'
            and excess['paid_negative_mass'] == '1/3' and excess['endpoint'] is None,
            'Exact excess/negativity witness failed')
    require(reports['false-potential-nine']['potential'] == '9'
            and reports['false-potential-nine']['endpoint'] is None, 'Potential confused with an endpoint')
    require(reports['amplification-trap']['potential'] == '8'
            and reports['amplification-trap']['endpoint'] is None, 'Amplification trap failed')
    ring = model.Engine()
    rows = model.execute(ring, cases['amplification-trap'])
    total = good = Q(0)
    for row in rows:
        for key, value in row.items():
            if key & 3 == 2:
                mass = E.cast(value).norm()
                total += mass
                if model.fourier_rank(ring.groups[key >> 2]) == 3:
                    good += mass
    require(good/total == Q(200, 201), 'Wrong deceptive good-mass ratio')
    # A metric with a zero/negative entry is not a positivity certificate.
    rejected = []
    for label, ms, ds in (
        ('zero metric', matrices, [[Q(0)]*3]*(len(matrices)+1)),
        ('negative metric', matrices, [[-x for x in d] for d in metrics]),
        ('corrupt metric', matrices, [metrics[0], [1, 1, 1], *metrics[2:]]),
        ('shear declared unitary', [(E(1), E(1), ZERO, ZERO, ONE, ZERO, ZERO, ZERO, ONE)], [[1]*3, [1]*3]),
    ):
        try:
            check_metrics(ms, ds)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('False metric accepted: '+label)
    # Paid inverse signs and all seven paid directions are exercised directly.
    unary_checks = 0
    for value in range(1, 8):
        for free in range(18):
            word = (('paid', 0, value), ('free', 0, free), ('paid', 0, value))
            p = point(word, independent=True)
            require(p['negative'] == [0, 0, 0], 'Unary inverse/control failed')
            unary_checks += 1
    return {'status': 'PASS_SIGNED_RANK_TRANSPORT', 'cases': reports,
            'independent_named_prefixes': sum(r['prefixes'] for r in reports.values()),
            'dense_unary_inverse_controls': unary_checks, 'rejected_metrics': rejected,
            'amplification_trap_good_fraction': '200/201',
            'eight_call_necessary_paid_negative_mass': '1/2'}


def check_manifest():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    actual = {p.name for p in ROOT.iterdir() if p.is_file() and p.name != 'MANIFEST.json'}
    require(actual == set(manifest['files']), 'Source inventory mismatch')
    for name, wanted in manifest['files'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == wanted, 'Source integrity mismatch: '+name)
    origins = json.loads((ROOT/'ORIGINS.json').read_text())
    for name, wanted in origins['vendored_files'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == wanted, 'Vendored source mismatch: '+name)


if __name__ == '__main__':
    check_manifest()
    report = controls()
    require(report == json.loads((ROOT/'EXPECTED.json').read_text()), 'Expected result mismatch')
    print(json.dumps(report, sort_keys=True))
