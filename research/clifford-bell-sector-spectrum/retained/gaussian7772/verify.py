"""Check the sharp four-qubit width-thirteen stability contract.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y):
    return x[0]+y[0], x[1]+y[1]


def mul(x, y):
    return x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]


def conj(x):
    return x[0], -x[1]


def power(x, n):
    value = ONE
    for _ in range(n):
        value = mul(value, x)
    return value


def product(a, b):
    n = len(a)
    return [[sum_pair(mul(a[i][k], b[k][j]) for k in range(n)) for j in range(n)] for i in range(n)]


def sum_pair(values):
    result = ZERO
    for x in values:
        result = add(result, x)
    return result


def minus_scalar(a, value):
    return [[add(x, (-value, F(0))) if i == j else x for j, x in enumerate(row)]
            for i, row in enumerate(a)]


def serialize(x):
    return [x.numerator, x.denominator]


def one_qubit():
    unit = [[ONE, ZERO], [ZERO, ONE]]
    x = [[ZERO, ONE], [ONE, ZERO]]
    z = [[ONE, ZERO], [ZERO, (-F(1), F(0))]]
    phase = [[ONE, ZERO], [ZERO, (F(0), F(1))]]
    h = [[(F(1, 2), F(1, 2)), (F(1, 2), F(1, 2))],
         [(F(1, 2), F(1, 2)), (-F(1, 2), -F(1, 2))]]
    phases = [ONE, (F(0), F(1)), (-F(1), F(0)), (F(0), -F(1))]

    def canonical(a):
        return max(tuple(tuple(mul(v, t) for v in row) for row in a) for t in phases)

    start = canonical(unit)
    elements, seen = [start], {start}
    for a in elements:
        for g in (phase, h):
            b = canonical(product(g, a))
            if b not in seen:
                seen.add(b)
                elements.append(b)
    require(len(elements) == 24, 'complete one-qubit projective group')
    for a in elements:
        adjoint = [[conj(a[j][i]) for j in range(2)] for i in range(2)]
        require(product(adjoint, a) == unit, 'literal one-qubit unitary')
        for b in elements:
            require(canonical(product(a, b)) in seen, 'projective group closure')
    paulies = [unit, x, z, product(x, z)]
    characters = Counter()
    for a in elements:
        total = ZERO
        for p in paulies:
            b = product(p, a)
            trace = add(b[0][0], b[1][1])
            total = add(total, mul(power(trace, 13), conj(trace)))
        require(total[1] == 0 and total[0].denominator == 1, 'literal quotient trace')
        characters[total[0]/4] += 1
    require(characters == {F(4096): 4, F(-64): 12, F(1): 8}, 'actual S3 quotient character')
    multiples = [(4096-3*64+2)//6, (4096+3*64+2)//6, (2*4096-2)//6]
    require(multiples == [651, 715, 1365], 'literal S3 multiplicities')
    eigenvalues = [F(6*m, 4096*d) for m, d in zip(multiples, (1, 1, 2), strict=True)]
    dimensions = [4, 4, 16]
    gram = []
    for a in elements:
        row = []
        for b in elements:
            inner = sum_pair(mul(conj(u), v) for ar, br in zip(a, b, strict=True)
                             for u, v in zip(ar, br, strict=True))
            row.append(power((inner[0]/2, inner[1]/2), 13))
        gram.append(row)
    require(all(gram[i][j] == conj(gram[j][i]) for i in range(24) for j in range(24)),
            'literal Gram adjoint')
    require(all(gram[i][i] == ONE for i in range(24)), 'literal Gram diagonal')
    shifted = [minus_scalar(gram, e) for e in eigenvalues]
    annihilator = product(product(shifted[0], shifted[1]), shifted[2])
    require(all(x == ZERO for row in annihilator for x in row), 'literal cubic annihilator')
    moment = sum(mul(v, conj(v))[0] for row in gram for v in row)
    require(sum(d*e for d, e in zip(dimensions, eigenvalues, strict=True)) == 24,
            'small spectral trace')
    require(sum(d*e*e for d, e in zip(dimensions, eigenvalues, strict=True)) == moment,
            'small spectral second moment')
    require(len(set(eigenvalues)) == 3 and sum(dimensions) == 24, 'small complete spectrum')
    # Distinct roots and the three trace equations determine the full multiplicities.
    for factor in (4, F(1, 2), 2**13):
        require(sum(d*e*factor for d, e in zip(dimensions, eigenvalues, strict=True)) != 24,
                'wrong group, representation or column normalization accepted')
    return {'projective_elements': 24, 'closure_products': 576,
            'quotient_character_counts': [[int(k), v] for k, v in sorted(characters.items())],
            'multiplicities': multiples, 'eigenvalues': [serialize(e) for e in eigenvalues],
            'eigenspace_dimensions': dimensions, 'gram_second_moment': serialize(moment),
            'literal_cubic_annihilator': True, 'normalization_controls': 3}


def collect():
    pins = json.loads((ROOT/'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (ROOT/pin['retained']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'] and
                sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
                'source pin')
    source = ROOT/'retained/source7766'
    args = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []), '-B', str(source/'verify.py')]
    run = subprocess.run(args, capture_output=True, text=True, check=True, timeout=60)
    require('PASS_CLIFFORD_FOUR_QUBIT_THRESHOLD' in run.stdout, 'unchanged source replay')
    spec = importlib.util.spec_from_file_location('source7766', source/'verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = json.loads((source/'retained/source7747/PROJECTION.json').read_text())
    multiples, norm = module.odd_multiplicities(data, 6)
    saved = json.loads((source/'RESULT.json').read_text())['threshold']['width13_multiplicities']
    require(multiples == saved and all(m > 0 for m in multiples), 'source width-thirteen multiplicities')
    order = sum(data['element_counts'])
    size = 256*order
    levels = defaultdict(list)
    rows = []
    for i, (row, m) in enumerate(zip(data['rows'], multiples, strict=True), 1):
        degree = row[0]
        eigenvalue = F(order*m, 2**48*degree)
        require(eigenvalue == F(size*m, 16**13*(16*degree)), 'actual Gram normalization')
        block = (16*degree)**2
        rows.append({'row': i, 'quotient_degree': degree, 'multiplicity': m,
                     'clifford_degree': 16*degree, 'regular_dimension': block,
                     'eigenvalue': serialize(eigenvalue)})
        levels[eigenvalue].append(i)
    require(len(rows) == 81 and len(levels) == 52, 'complete distinct spectrum')
    lo, hi = min(levels), max(levels)
    require(levels[lo] == [1] and levels[hi] == [2], 'sharp endpoint rows')
    require(lo == F(470624175, 4294967296) and hi == F(7841980575, 1073741824), 'sharp endpoints')
    require(hi/lo == F(101244, 1519), 'Gram condition number')
    require(sum(r['regular_dimension'] for r in rows) == size, 'complete regular dimension')
    require(sum(r['regular_dimension']*F(*r['eigenvalue']) for r in rows) == size, 'full spectral trace')
    spectral_moment = sum(r['regular_dimension']*F(*r['eigenvalue'])**2 for r in rows)
    # Each symplectic element with fixed dimension d has 2^(8-d) nonzero Pauli lifts.
    direct_moment = size*sum(F(c*2**(12*d), 2**96) for d, c in enumerate(data['element_counts']))
    require(spectral_moment == direct_moment == F(256*order**2*norm, 2**96),
            'independent complete trace second moment')
    for r in rows:
        e = F(*r['eigenvalue'])
        require(lo <= e <= hi, 'endpoint inequality')
        require(r['regular_dimension'] > 0, 'nonempty endpoint witness')
    for factor in (4, 16, F(1, 16)):
        require(sum(r['regular_dimension']*F(*r['eigenvalue'])*factor for r in rows) != size,
                'full spectral normalization control')
    require(F(1, 1)/lo < F(3021, 1000)**2 and hi/lo < F(8165, 1000)**2,
            'rigorous decimal recovery bounds')
    return {'source_files': len(pins), 'projective_order': size, 'width': 13, 'rows': rows,
            'distinct_levels': [{'eigenvalue': serialize(e), 'rows': ids,
                                 'eigenspace_dimension': sum(rows[i-1]['regular_dimension'] for i in ids)}
                                for e, ids in sorted(levels.items())],
            'minimum': serialize(lo), 'maximum': serialize(hi),
            'minimum_dimension': 256, 'maximum_dimension': 313600,
            'gram_condition': serialize(hi/lo), 'inverse_squared_norm': serialize(1/lo),
            'second_moment': serialize(spectral_moment), 'one_qubit_calibration': one_qubit()}


def main():
    actual = collect()
    require(actual == json.loads((ROOT/'RESULT.json').read_text()), 'saved result mismatch')
    print('PASS_CLIFFORD_THRESHOLD_CONDITIONING')
    print('81 blocks, 52 distinct eigenvalues; complete rank 12128668876800')
    print('Sharp minimum 470624175/4294967296; sharp maximum 7841980575/1073741824')
    print('Gram condition 101244/1519; normalized tensor-map condition < 8.165; recovery norm < 3.021')
    print('Complete 24-element one-qubit Gram calibration, cubic annihilator and exact moments pass')


if __name__ == '__main__':
    main()
