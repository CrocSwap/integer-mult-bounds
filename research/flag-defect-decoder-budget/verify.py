"""Independent finite tests for the defect budget and the complete ADD word.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from itertools import product
from collections import Counter
import hashlib
import json
import random
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
M = runpy.run_path(str(ROOT/'model.py'))
check, rank, audit = M['require'], M['rank'], M['audit']


def image_rank(matrix):
    rows = [sum(x << j for j, x in enumerate(row)) for row in matrix]
    space = {0}
    for row in rows:
        space |= {x ^ row for x in space}
    size = len(space)
    check(size & (size-1) == 0, 'image is not a binary subspace')
    return size.bit_length()-1


def scalar(ports, allowed, p):
    edges = [(i, j) for i in range(len(ports)) for j in range(len(ports))
             if i != j and (ports[i], ports[j]) in allowed]
    best, witness = len(ports)+1, None
    for values in product(range(p), repeat=len(edges)):
        a = [[int(i == j) for j in ports] for i in ports]
        for (i, j), x in zip(edges, values):
            a[i][j] = x
        r = rank(a, p)
        if r < best:
            best, witness = r, a
    return best, witness


def bound_and_attainer(levels, allowed, p):
    coordinates = [(i, t) for i, layer in enumerate(levels) for t in layer]
    attainer = [[0]*len(coordinates) for _ in coordinates]
    bound = 0
    for t in sorted({t for _, t in coordinates}):
        indices = [j for j, x in enumerate(coordinates) if x[1] == t]
        ports = [coordinates[j][0] for j in indices]
        minimum, a = scalar(ports, allowed, p)
        bound += minimum
        for i, row in enumerate(indices):
            for j, col in enumerate(indices):
                attainer[row][col] = a[i][j]
    r, e, _ = audit(attainer, levels, allowed, p)
    check((r, e) == (bound, 0), 'layer attainer fails')
    return bound


def fitting(levels, allowed, values):
    coords = [(i, t) for i, layer in enumerate(levels) for t in layer]
    a = [[int(i == j) for j in range(len(coords))] for i in range(len(coords))]
    values = iter(values)
    for i, (port, _) in enumerate(coords):
        for j, (source, _) in enumerate(coords):
            if (port, source) in allowed:
                a[i][j] = next(values)
    return a


def binary_census(counts):
    levels = ((0,), (0, 1), (0, 1))
    edges = [(i, j) for i in range(3) for j in range(3) if i != j]
    for mask in range(64):
        allowed = frozenset(e for i, e in enumerate(edges) if mask >> i & 1)
        bound = bound_and_attainer(levels, allowed, 2)
        free = sum(len(levels[i])*len(levels[j]) for i, j in allowed)
        compatible_min = 6
        for values in product(range(2), repeat=free):
            a = fitting(levels, allowed, values)
            r, e, defect = audit(a, levels, allowed, 2)
            check(r == image_rank(a) and e == image_rank(defect), 'independent image rank')
            check(r+e >= bound, 'defect inequality fails')
            if e == 0:
                compatible_min = min(compatible_min, r)
                counts['compatible_unequal_matrices'] += 1
            counts['all_unequal_matrices'] += 1
        check(compatible_min == bound, 'unequal minimum fails')
    check(counts['all_unequal_matrices'] == 180625, 'incomplete unequal census')


def chart_c5(matrix, charts):
    invs = []
    for a in charts:
        # Every nonzero determinant over F2 is one.
        invs.append([[a[1][1], a[0][1]], [a[1][0], a[0][0]]])
    out = [[0]*10 for _ in range(10)]
    for i, j, r, c in product(range(5), range(5), range(2), range(2)):
        out[2*i+r][2*j+c] = sum(invs[i][r][u]*matrix[2*i+u][2*j+v]*charts[j][v][c]
                                  for u in range(2) for v in range(2)) % 2
    return out


def run():
    counts = Counter()
    origin = json.loads((ROOT/'ORIGIN.json').read_text())
    data = (ROOT/origin['local']).read_bytes()
    check(hashlib.sha256(data).hexdigest() == origin['sha256'], 'source pin')
    check(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == origin['git_blob'], 'source Git blob')
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        (dest/'inputs').mkdir()
        for name in ('model.py', 'verify.py', 'ORIGIN.json'):
            shutil.copyfile(ROOT/name, dest/name)
        (dest/origin['local']).write_bytes(data+b'\n')
        mutated = runpy.run_path(str(dest/'verify.py'))
        try:
            mutated['run']()
        except ValueError as error:
            check(str(error) == 'source pin', 'wrong source rejection')
            counts['source_corruptions'] += 1
        else:
            raise ValueError('changed retained source accepted')
    binary_census(counts)
    rng = random.Random(20261103)
    gap_profiles = [((0, 3), (1,), (0, 2)), ((-2,), (0, 1), (3, 4)), ((0,), (0, 2, 4), (1, 2))]
    edges = [(i, j) for i in range(3) for j in range(3) if i != j]
    for p, levels, mask in product((2, 3, 5), gap_profiles, (0, 13, 37, 63)):
        allowed = frozenset(e for i, e in enumerate(edges) if mask >> i & 1)
        bound = bound_and_attainer(levels, allowed, p)
        for _ in range(8):
            free = sum(len(levels[i])*len(levels[j]) for i, j in allowed)
            a = fitting(levels, allowed, (rng.randrange(p) for _ in range(free)))
            r, e, _ = audit(a, levels, allowed, p)
            check(r+e >= bound, 'gapped/field defect inequality')
            counts['gapped_field_cases'] += 1
    sharp = []
    for p, n, copies in product((2, 3, 5), (5, 7, 9, 11), (1, 2, 3)):
        a, allowed = M['cycle'](n, copies)
        # Change each odd port's basis by swapping the two edge coordinates.
        order = [2*copies*i+2*c+(1-b if i % 2 else b)
                 for i in range(n) for c in range(copies) for b in range(2)]
        changed = [[a[i][j] for j in order] for i in order]
        levels = (tuple(range(2*copies)),)*n
        r, e, defect = audit(changed, levels, allowed, p)
        check((r, e) == (n*copies, copies), 'sharp all-field defect')
        check(sum(x != 0 for row in defect for x in row) == copies, 'defect is not the claimed matching')
        counts['sharp_family_cases'] += 1
        sharp.append([p, n, copies, r, e])
    a, allowed = M['cycle'](5, 1)
    bases = []
    for values in product(range(2), repeat=4):
        b = [list(values[:2]), list(values[2:])]
        if rank(b, 2) == 2:
            bases.append(b)
    hist = Counter()
    for charts in product(bases, repeat=5):
        r, e, defect = audit(chart_c5(a, charts), ((0, 1),)*5, allowed, 2)
        check(r == 5 and e >= 1 and e == image_rank(defect), 'C5 all-basis lower bound')
        hist[e] += 1
    check(sum(hist.values()) == 6**5 and min(hist) == 1, 'incomplete GL2 census')
    counts['C5_local_basis_tuples'] = sum(hist.values())
    word_invoices = []
    for n, copies, dirty in product((5, 7, 11), (1, 2), (False, True)):
        a, _ = M['cycle'](n, copies)
        size = len(a)
        operations = M['word'](n, copies, dirty)
        expected_ops = (8 if dirty else 6)*n*copies
        check(len(operations) == expected_ops, 'wrong full ADD bill')
        vectors = [[int(i == j) for i in range(2*size+1)] for j in range(2*size+int(dirty))]
        vectors += [[sign*7]*(2*size)+([sign*7] if dirty else [0]) for sign in (-1, 1)]
        vectors += [[rng.randrange(-7, 8) for _ in range(2*size)]+([rng.randrange(-7, 8)] if dirty else [0]) for _ in range(8)]
        for values in vectors:
            actual, maximum = M['execute'](values, operations)
            expected = values[:size] + [values[size+i]+sum(a[i][j]*values[j] for j in range(size))
                                       for i in range(size)] + values[-1:]
            check(actual == expected, 'literal word endpoint/source/scratch')
            check(maximum <= 3*max(map(abs, values)), 'prefix range exceeds 3H')
            counts['complete_word_inputs'] += 1
        positive = [7]*(2*size)+([7] if dirty else [0])
        check(M['execute'](positive, operations)[1] == 21, 'range bound not attained')
        for j in range(min(len(operations), 16)):
            bad = operations[:j]+operations[j+1:]
            check(any(M['execute'](v, bad)[0] != M['execute'](v, operations)[0] for v in vectors), 'omitted operation survived')
            counts['omitted_operations'] += 1
        word_invoices.append(dict(n=n,copies=copies,dirty=dirty,adds=expected_ops,reads=2*expected_ops,writes=expected_ops,scratch_fields=1))
    invalid = [lambda: M['cycle'](4,1), lambda: M['cycle'](3,1), lambda: M['cycle'](5,0),
               lambda: M['word'](5,1,1), lambda: audit([[1]],((0,0),),frozenset(),2),
               lambda: audit([[0]],((0,),),frozenset(),2), lambda: audit([[1]],((0,),),frozenset(),4),
               lambda: audit([[1,1],[0,1]],((0,),(0,)),frozenset(),2),
               lambda: audit([[1]],((0,),),frozenset({(0,0)}),2),
               lambda: audit([[2]],((0,),),frozenset(),2)]
    for f in invalid:
        try:
            f()
        except ValueError:
            counts['invalid_inputs'] += 1
        else:
            raise ValueError('invalid input accepted')
    hashes = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
              for name in ('PROOF.md','model.py','verify.py','ORIGIN.json')}
    return dict(status='PASS_FLAG_DEFECT_DECODER_BUDGET',counts=dict(counts),sharp_family=sharp,
                C5_defect_histogram={str(k):v for k,v in sorted(hist.items())},word_invoices=word_invoices,
                source_hashes=hashes,scope='All-field written theorem and finite checks; no native invoice or kappa.')


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (ROOT/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        check(not sys.argv[1:],'unknown command option')
        check(result == json.loads((ROOT/'RESULT.json').read_text()),'receipt differs')
    print(json.dumps(result,sort_keys=True))
