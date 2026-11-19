"""Check both quadratic sectors of the four-qubit width-ten Gram matrix.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha1, sha256
import importlib.util
import json
from math import prod
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ORDER = 47_377_612_800


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_check(archive):
    pins = json.loads((ROOT/'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (ROOT/pin['retained']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
        require(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
                'source Git blob')
    path = ROOT/'retained/source7766'
    args = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
            '-B', str(path/'verify.py')]
    if archive:
        args += ['--ctbllib-archive', str(archive)]
    result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=60)
    require('PASS_CLIFFORD_FOUR_QUBIT_THRESHOLD' in result.stdout, 'unchanged source replay')
    return len(pins), load('source7766', path/'verify.py'), load('source7747', path/'retained/source7747/verify.py')


def gaussian(n, r):
    return prod(2**n-2**i for i in range(r))//prod(2**r-2**i for i in range(r))


def quadratic_tuple_orbits(n, length, minus):
    total = 0
    for r in range(min(length, 2*n)+1):
        for t in range(r % 2, r+1, 2):
            if r+t > 2*n:
                continue
            even, half = r-t, (r-t)//2
            gl = prod(2**even-2**i for i in range(even))
            sp = 2**(half*half)*prod(2**(2*i)-1 for i in range(1, half+1))
            alternating = gaussian(r, t)*gl//sp
            if r+t < 2*n:
                forms = 2**r
            else:
                zero_radical = ((2**(2*half)+(-1 if minus else 1)*2**half)//2
                                if half else int(not minus))
                forms = (2**t-1)*2**even+zero_radical
            total += gaussian(length, r)*alternating*forms
    return total


def small_group_orbits(source):
    records = []
    for n in (1, 2):
        for minus in (False, True):
            width, size = 2*n, 2**(2*n)
            q = [source.quadratic(x, n, minus) for x in range(size)]
            group = []

            def extend(columns, span):
                if len(columns) == width:
                    group.append(tuple(columns))
                    return
                index = len(columns)
                for v in range(1, size):
                    if v in span or q[v] != q[1 << index]:
                        continue
                    if any(source.omega(v, w, n) != source.omega(1 << index, 1 << j, n)
                           for j, w in enumerate(columns)):
                        continue
                    extend(columns+[v], span | {x ^ v for x in span})

            extend([], {0})
            expected_order = 2**(n*(n-1)+1)*(2**n+(1 if minus else -1))*prod(2**(2*i)-1 for i in range(1, n))
            require(len(group) == expected_order, 'complete small orthogonal group')
            fixed = []
            for columns in group:
                images = [source.apply(columns, x) for x in range(size)]
                require(len(set(images)) == size and all(q[x] == q[y] for x, y in enumerate(images)),
                        'literal small quadratic action')
                fixed.append(sum(x == y for x, y in enumerate(images)))
            moments = []
            for length in range(9):
                total = sum(f**length for f in fixed)
                value, remainder = divmod(total, len(group))
                require(remainder == 0 and value == quadratic_tuple_orbits(n, length, minus),
                        'independent small-group orbit formula')
                moments.append(value)
            records.append({'half_dimension': n, 'minus': minus, 'group_order': len(group),
                            'tuple_orbits_0_to8': moments})
    return records


def check_group(group, sdata, degrees, quotient_multiplicities):
    minus = group['kind'] == 'minus'
    index = 120 if minus else 136
    order = group['order']
    centralizers, fusion, rows = group['centralizers'], group['fusion_to_S8'], group['rows']
    require(order*index == ORDER and len(centralizers) == len(fusion) == len(rows), 'stabilizer size')
    require(fusion[0] == 1 and centralizers[0] == order, 'identity fusion')
    require(all(c > 0 and order % c == 0 for c in centralizers), 'stabilizer centralizers')
    sizes = [order//c for c in centralizers]
    require(sum(sizes) == order, 'stabilizer class-size sum')
    masses = [0]*81
    dims = []
    for size, target in zip(sizes, fusion, strict=True):
        require(1 <= target <= 81, 'fusion target')
        masses[target-1] += size
        point = sdata['columns'][target-1]
        fixed = 2+sum(point['values'][:2])
        require(fixed.bit_count() == 1, 'fixed-space power')
        dims.append(fixed.bit_length()-1)
    for mass, column in zip(masses, sdata['columns'], strict=True):
        actual, remainder = divmod(column['centralizer']*mass, order)
        expected = 1+column['values'][0 if minus else 1]
        require(remainder == 0 and actual == expected, 'quadratic-form fusion character')
    require(dims.count(8) == 1 and dims[0] == 8, 'identity fixed dimension')
    multiplicities, restriction_degrees = [], [0]*81
    for i, row in enumerate(rows):
        degree = row['degree']
        require(type(degree) is int and degree > 0 and len(row['sums_d1_to7']) == 7, 'stabilizer row')
        numerator = degree*(2**32-1)+sum(a*(2**(4*d)-1) for d, a in enumerate(row['sums_d1_to7'], 1))
        value, remainder = divmod(numerator, order)
        require(remainder == 0, 'nonintegral stabilizer multiplicity')
        value += i == 0
        require(value >= 0, 'negative stabilizer multiplicity')
        restriction = row['restriction']
        require([j for j, _ in restriction] == sorted({j for j, _ in restriction}), 'restriction row indices')
        require(all(1 <= j <= 81 and type(b) is int and b > 0 for j, b in restriction), 'restriction coefficients')
        require(sum(degrees[j-1]*b for j, b in restriction) == index*degree, 'induced dimension')
        require(sum(quotient_multiplicities[j-1]*b for j, b in restriction) == value,
                'independent quotient restriction multiplicity')
        for j, b in restriction:
            restriction_degrees[j-1] += degree*b
        multiplicities.append(value)
    require(restriction_degrees == degrees, 'all restricted quotient dimensions')
    require(sum(r['degree']**2 for r in rows) == order, 'stabilizer regular dimension')
    require(sum(r['degree']*m for r, m in zip(rows, multiplicities, strict=True)) == 2**32,
            'whole quotient restriction dimension')
    norm = quadratic_tuple_orbits(4, 8, minus)
    require(sum(m*m for m in multiplicities) == norm, 'independent quadratic tuple norm')
    require(sum(size*2**(8*d) for size, d in zip(sizes, dims, strict=True)) == order*norm,
            'class histogram tuple norm')
    require(multiplicities[0] == quadratic_tuple_orbits(4, 4, minus), 'four-tuple orbit count')
    require(multiplicities[1] == int(not minus), 'source Dickson multiplicity')
    missing = [{'row': i+1, 'degree': row['degree'], 'clifford_degree': index*row['degree']}
               for i, (row, m) in enumerate(zip(rows, multiplicities, strict=True)) if m == 0]
    loss = sum(row['clifford_degree']**2 for row in missing)
    return {'kind': group['kind'], 'index': index, 'order': order, 'multiplicities': multiplicities,
            'missing': missing, 'nullity': loss, 'tuple_norm': norm,
            'four_tuple_orbits': multiplicities[0], 'class_dimension_counts': dict(sorted(Counter(dims).items()))}


def collect(archive=None):
    count, source, old = source_check(archive)
    external = json.loads((ROOT/'EXTERNAL.json').read_text())
    raw = (ROOT/'STABILIZERS.json').read_bytes()
    require(sha256(raw).hexdigest() == external['derived_sha256'], 'derived stabilizer hash')
    data = json.loads(raw)
    if archive:
        extractor = load('exact_table_extractor', ROOT/'extract.py')
        require(extractor.extract(archive) == data, 'authenticated complete stabilizer extraction')
    sdata = json.loads((ROOT/'retained/source7770/CHARACTER-COLUMNS.json').read_text())
    projection = json.loads((ROOT/'retained/source7766/retained/source7747/PROJECTION.json').read_text())
    degrees, multiplicities = old.check_projection(projection)
    groups = [check_group(g, sdata, degrees, multiplicities) for g in data['groups']]
    require([g['kind'] for g in groups] == ['minus', 'plus'], 'both quadratic sectors')
    require([[m['row'] for m in g['missing']] for g in groups]
            == [[2, 4, 10, 14, 22, 28, 43], [4, 6, 14, 16, 21, 25, 44, 46]], 'full missing-row profile')
    require([g['nullity'] for g in groups] == [102154809600, 91765092608], 'sector nullities')
    for fault, reason in [('fusion', 'identity fusion'), ('sum', 'nonintegral stabilizer multiplicity')]:
        bad = json.loads(json.dumps(data['groups'][0]))
        if fault == 'fusion':
            bad['fusion_to_S8'][0] = 2
        else:
            bad['rows'][0]['sums_d1_to7'][0] += 1
        try:
            check_group(bad, sdata, degrees, multiplicities)
        except ValueError as error:
            require(str(error) == reason, 'wrong fault rejection')
        else:
            raise ValueError('stabilizer fault accepted')
    dimension = sum(g['index']**2*g['order'] for g in groups)
    nullity = sum(g['nullity'] for g in groups)
    require(dimension == 256*ORDER and nullity == 193919902208, 'complete central ideal')
    return {'source_files': count, 'groups': groups, 'small_group_checks': small_group_orbits(source),
            'projective_order': dimension, 'exact_nullity': nullity, 'exact_rank': dimension-nullity,
            'archive_validation_scope': data['archive_checks'], 'threshold': 'T(4)=13 unchanged'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ctbllib-archive', type=Path)
    args = parser.parse_args()
    result = collect(args.ctbllib_archive)
    require(json.loads(json.dumps(result)) == json.loads((ROOT/'RESULT.json').read_text()), 'saved result mismatch')
    if args.ctbllib_archive:
        print('PASS_AUTHENTICATED_STABILIZERS rows=127 inner_products=14650 restrictions=10287')
    print('PASS_CLIFFORD_WIDTH_TEN_NULLITY')
    print('Exact nullity 193919902208; exact rank 11934748974592; T(4)=13 unchanged')
    print('Minus: seven missing modules, nullity 102154809600; plus: eight, nullity 91765092608')
    print('All 127 multiplicities agree with quotient restrictions; complete regular dimension passes')
    print('Independent quadratic tuple norms 78491573017 and 84713186558; four complete small groups')


if __name__ == '__main__':
    main()
