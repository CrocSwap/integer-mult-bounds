# SPDX-License-Identifier: Apache-2.0
"""Exact fixtures for the written all-real-parameter D_n strict gap proof."""
import argparse
import ast
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pins():
    sources = json.loads((HERE/'SOURCES.json').read_text())['files']
    deps = json.loads((HERE/'DEPENDENCY.json').read_text())['files']
    result = {}
    for row, root in [(x,ROOT) for x in sources]+[(x,HERE) for x in deps]:
        p = root/row['path']
        need(p.stat().st_size < 2_000_000, 'source size bound')
        b = p.read_bytes()
        need(hashlib.sha256(b).hexdigest() == row['sha256'], 'source SHA256 mismatch')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == row['git_blob'], 'source blob mismatch')
        result[row['path']] = b
    return result


def roots(n):
    return [tuple(1 if k == i else sign if k == j else 0 for k in range(n))
            for i in range(n) for j in range(i+1,n) for sign in (1,-1)]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def rows(lines):
    return [sum(int(i == j or dot(a,b) == 0)<<j for j,b in enumerate(lines))
            for i,a in enumerate(lines)]


def support(lines, a):
    return sum(int(dot(x,a) != 0)<<i for i,x in enumerate(lines))


def rank(items):
    pivots = {}
    for value in items:
        while value:
            j = value.bit_length()-1
            if j not in pivots:
                pivots[j] = value
                break
            value ^= pivots[j]
    return len(pivots)


def price(matrix, left, right):
    return rank(row & right for i,row in enumerate(matrix) if left>>i & 1)


def unit(n,i):
    return [int(j == i) for j in range(n)]


def rectangle_formula(b, i):
    supp = [j for j,x in enumerate(b) if x]
    n = len(b)
    if not supp:
        return 0
    return n-2 if n % 2 and len(supp) == 1 and supp[0] != i else n-1


def family(n, a, lam, lines=None, matrix=None):
    lines = roots(n) if lines is None else lines
    matrix = rows(lines) if matrix is None else matrix
    b = [[F(i == j)-lam*a[i]*a[j] for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            need(b[i][j]+lam*a[i]*a[j] == (i == j), 'coordinate factorization')
    costs = [price(matrix,support(lines,unit(n,i)),support(lines,b[i])) for i in range(n)]
    for i in range(n):
        need(costs[i] == rectangle_formula(b[i],i), 'exact star rectangle formula')
    extra = 0 if lam == 0 else price(matrix,support(lines,a),support(lines,a))
    active = sum(x != 0 for x in a)
    genuine = bool(lam and active and all(any(v) for v in b))
    floor = n*(n-1) + (n-2 if n % 2 else n-1) if genuine else n*(n-1)
    need(sum(costs)+extra >= floor, 'strict family floor')
    equality = not lam or not active or (active == 1 and any(lam*x*x == 1 for x in a))
    need((sum(costs)+extra == n*(n-1)) == equality, 'baseline equality classification')
    return {'n':n,'a':list(map(str,a)),'lambda':str(lam),'costs':costs+[extra],
            'genuine':genuine,'total':sum(costs)+extra,'floor':floor}


def rectangles():
    count = 0
    principal = 0
    for n in range(3,7):
        lines = roots(n); matrix = rows(lines)
        for b in itertools.product((-1,0,1),repeat=n):
            if not any(b):
                continue
            mask = support(lines,b)
            p = price(matrix,mask,mask)
            floor = n if n % 2 and sum(x != 0 for x in b) >= 2 else n-1
            need(p >= floor,'principal support rank')
            principal += 1
            for i in range(n):
                actual = price(matrix,support(lines,unit(n,i)),mask)
                need(actual == rectangle_formula(b,i),'exhaustive rectangle fixture')
                count += 1
    return {'star_rectangles':count,'principal_supports':principal,'dimensions':[3,4,5,6]}


def fixtures():
    out = []
    for n in range(3,13):
        lines = roots(n); matrix = rows(lines)
        vectors = [[F(0)]*n, list(map(F,unit(n,0))), [F(1),F(1)]+[F(0)]*(n-2),
                   [F(1),F(2)]+[F(0)]*(n-2), [F(1)]*n,
                   [F((k%3)-1,k+1) for k in range(n)]]
        for a in vectors:
            for lam in map(F,[0,1,-1,2,F(1,2),F(1,4)]):
                out.append(family(n,a,lam,lines,matrix))
        sharp = family(n,[F(1),F(1)]+[F(0)]*(n-2),F(1),lines,matrix)
        need(sharp['total'] == sharp['floor'] and sharp['genuine'],'sharp genuine fixture')
    return out


def source_binding(blobs):
    tree = ast.parse(blobs['references/PR2518-search.py'])
    names = {'canon','lines','D','dot','sup_mask','one_extra_cells'}
    nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    need({n.name for n in nodes} == names,'source function coverage')
    env = {'F':F}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pinned PR2518 definitions>','exec'),env)
    cert = json.loads(blobs['references/PR2518-CERTIFICATE.json'])
    out = []
    cells = 0
    for n in (4,5):
        original = env['D'](n)
        need(original == [tuple(2*v for v in x) for x in roots(n)],'source D_n convention')
        old = cert['overcomplete_full']['D'+str(n)]
        a = list(map(F,old['min_witness']['dir'])); lam = F(old['min_witness']['lambda'])
        replay = family(n,a,lam)
        need(replay['total'] == old['min_cost'] == n*(n-1),'credited minimum replay')
        need(not replay['genuine'],'credited minimum is replacement')
        out.append(replay)
        for a in ([F(1),F(1)]+[F(0)]*(n-2), [F(1)]*n):
            for _,lam,terms in env['one_extra_cells'](original,[unit(n,i) for i in range(n)],a):
                matrix = rows(roots(n))
                source_cost = sum(price(matrix,left,right) for left,right in terms)
                need(source_cost == family(n,a,lam)['total'],'source support-cell binding')
                cells += 1
    return {'source_cells':cells,'credited_minima':out,'source_functions':sorted(names)}


def controls():
    # Pairing and full-line assumptions have observable effects.
    n = 5; lines = roots(n); matrix = rows(lines); a = [F(1),F(1),0,0,0]
    sharp = family(n,a,F(1))
    need(sharp['costs'] == [3,3,4,4,4,5],'sharp profile')
    need(sum(sharp['costs'][:-1]) < n*(n-1),'omitting extra term would break floor')
    singleton = family(n,list(map(F,unit(n,0))),F(1))
    need(singleton['total'] == 20 and not singleton['genuine'],'zero old term exclusion')
    x = support(lines,unit(n,0)); y = support(lines,unit(n,1))
    identity_rows = [1<<i for i in range(len(lines))]
    need(price(identity_rows,x,y) != price(matrix,x,y),'pairing mutation')
    punctured = [r for r in lines if r[0] == 0]
    need(price(rows(punctured),support(punctured,unit(n,0)),support(punctured,unit(n,1))) == 0,'puncture boundary')
    need(rectangle_formula(unit(5,1),0) == 3 and rectangle_formula(unit(4,1),0) == 3,'parity boundary')
    need([[int(i==j)-a[i]*a[j]+2*a[i]*a[j] for j in range(n)] for i in range(n)] != [unit(n,i) for i in range(n)],'wrong extra coefficient')
    return ['omit extra price','zero old term','identity pairing','puncture','parity','wrong extra coefficient']


def result():
    blobs = pins()
    return {'schema_version':1,'scope':'full D_n, dense B0, fixed standard coordinates, one extra rank-one update',
            'rectangle_checks':rectangles(),'fixtures':fixtures(),'source_binding':source_binding(blobs),
            'controls':controls(),'supplier_admitted':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--emit',type=Path);args=parser.parse_args()
    actual=result()
    if args.emit:
        with args.emit.open('x',encoding='utf8') as f:
            json.dump(actual,f,indent=2);f.write('\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        need(json.dumps(actual,sort_keys=True) == json.dumps(expected,sort_keys=True),'typed receipt mismatch')
    print('PASS_DN_ONE_EXTRA_GAP')


if __name__ == '__main__':
    main()
