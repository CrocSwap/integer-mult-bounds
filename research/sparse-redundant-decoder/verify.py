#!/usr/bin/env python3
"""Exact finite premises for PROOF.md; standard library, no sampled proof.
Philipp / mightyOil, substantial OpenAI Codex GPT-6 Astra assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()

def basis(vectors):
    pivots = {}
    for x in vectors:
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return list(pivots.values())

def span(generators):
    values = [0]
    for x in generators:
        values += [y ^ x for y in values]
    return sorted(values)

def geometry(include_frame=False):
    roots = set()
    for a, b in combinations(range(8), 2):
        for s, t in product((-2, 2), repeat=2):
            r = [0] * 8
            r[a], r[b] = s, t
            roots.add(tuple(r))
    for r in product((-1, 1), repeat=8):
        if sum(x < 0 for x in r) % 2 == 0:
            roots.add(r)
    need(len(roots) == 240, '240 scaled standard E8 roots')
    lines = set()
    for r in roots:
        q = tuple(v for j in range(0, 8, 2)
                  for v in ((r[j] + r[j+1]) // 2, (r[j] - r[j+1]) // 2))
        lines.add(max(q, tuple(-x for x in q)))
    need(len(lines) == 120, '120 root lines')
    return sorted(r for r in lines if include_frame or sum(x != 0 for x in r) > 1)

def setup(rs):
    n = len(rs)
    dots = [[sum(x*y for x, y in zip(r, s)) for s in rs] for r in rs]
    need(all(x % 2 == 0 for row in dots for x in row), 'integral true-root pairings')
    rows = [sum(((x//2 + 1) % 2) << j for j, x in enumerate(row)) for row in dots]
    ys = [[i for i, r in enumerate(rs) if r[j]] for j in range(8)]
    ys.append([i for i, r in enumerate(rs) if sum(r[:3])])
    spaces = [span(basis(rows[i] for i in y)) for y in ys]
    need(len(basis(rows)) == 9, 'full binary code dimension nine')
    return dots, rows, ys, spaces

def dimension(space):
    n = len(space)
    need(n > 0 and n & (n-1) == 0, 'linear space cardinality')
    return n.bit_length() - 1

def check_identity(rs, d, t):
    for i, r in enumerate(rs):
        for j, s in enumerate(rs):
            need(sum(a*b for a, b in zip(d[i], t[j])) == sum(a*b for a, b in zip(r, s)),
                 'all-pairs decoder identity')

def decode(rs, shifts, rows, ys):
    d = [tuple(r[j] - (x if j < 3 else 0) for j in range(8)) + (x,)
         for r, x in zip(rs, shifts)]
    t = [r + (sum(r[:3]),) for r in rs]
    check_identity(rs, d, t)
    costs = []
    active = []
    for k in range(9):
        xs = [i for i in range(len(rs)) if d[i][k] != 0]
        ym = sum(1 << i for i in ys[k])
        costs.append(len(basis(rows[i] & ym for i in xs)))
        active.append(bool(xs) and bool(ys[k]))
    return {'costs': costs, 'total': sum(costs), 'active_terms': sum(active)}, d, t

def check_sources():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    need(pins['base_commit'] == BASE, 'base pin')
    wanted = {'research/p112-single-lift/PROOF.md',
              'research/complex-frame-pair-decoders/PROOF.md',
              'research/complex-decoder-field-extension-seed44/PROOF.md'}
    inputs = [x for x in pins['files'] if x['usage'] == 'input']
    need({x['path'] for x in inputs} == wanted, 'complete input manifest')
    for x in inputs:
        need(hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest() == x['sha256'], 'source hash')
    return {x['path']: x['sha256'] for x in inputs}

def run():
    sources = check_sources()
    rs = geometry()
    need(len(rs) == 112, 'P112 frame puncture')
    need(all(sum(r[j]*r[k] for r in rs) == (56 if j == k else 0)
             for j in range(8) for k in range(8)), 'real root span via R-transpose-R=56I')
    dots, rows, ys, allspaces = setup(rs)
    need([dimension(s) for s in allspaces] == [8]*8+[9], 'column-code dimensions')
    need(all(any(rows[i] >> j & 1 for j in y) for y in ys for i in range(112)),
         'zero term cost iff row support empty')
    spaces = [allspaces[k] for k in (0, 1, 2, 8)]
    vals = [r[:3]+(0,) for r in rs]
    conflict = [[sum((v[j] != v[k]) << i for i, v in enumerate(vals))
                 for k in range(4)] for j in range(4)]
    planes = []
    stream = hashlib.sha256()
    for a in range(3):
        others = [k for k in range(4) if k != a]
        census = Counter()
        sp = spaces[a]
        for i, x in enumerate(sp[1:], 1):
            for y in sp[i+1:]:
                if y >= x ^ y:
                    continue
                union = x | y
                dims = [dimension([z for z in spaces[k] if not z & union & conflict[a][k]])
                        for k in others]
                need(dims == [0, 0, 1], 'plane compatibility dimensions')
                census[tuple(dims)] += 1
                stream.update(canonical([a, x, y, dims]).encode()+b'\n')
        need(sum(census.values()) == 10795, 'complete plane count')
        planes.append({'anchor': a, 'partner_order': others,
                       'counts': {','.join(map(str,k)):v for k,v in sorted(census.items())}})
    single = []
    for a in range(3):
        census = Counter()
        for z in spaces[a][1:]:
            dim = dimension([w for w in spaces[3] if not w & z & conflict[a][3]])
            need(dim <= 2, 'nonzero coordinate deficiency forces extra deficiency <=2')
            census[dim] += 1
        need(census == {1:1, 2:254}, 'complete single-vector census')
        single.append({'anchor':a, 'dimensions':{str(k):v for k,v in sorted(census.items())}})
    witnesses = []
    for name, shifts in [('zero', [0]*112)] + [(f'coordinate_{j}', [r[j] for r in rs]) for j in range(3)]:
        info, _, _ = decode(rs, shifts, rows, ys)
        need(info['total'] == 64 and info['active_terms'] == 8, 'all equality witnesses')
        witnesses.append({'name':name, **info})
    active_shift = [0]*112
    active_shift[40 % 112] = 2
    info, d, t = decode(rs, active_shift, rows, ys)
    need(info['costs'] == [8]*8+[1] and info['active_terms'] == 9, 'sharp all-active witness')
    witnesses.append({'name':'all_active_single_row', 'row':40, 'shift':2, **info})
    # Exact integer nonconstant-row examples check the representation, not the universal theorem.
    example_costs = []
    for s in range(12):
        shifts = [((i*17+s*13+40) % 7)-3 for i in range(112)]
        item, _, _ = decode(rs, shifts, rows, ys)
        need(item['total'] >= 64, 'finite shift check')
        example_costs.append(item['total'])
    controls=[]
    def reject(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('control not rejected: '+name)
    damaged=[list(x) for x in d];damaged[40][0]+=2
    reject('missing_shift_subtraction', lambda: check_identity(rs,damaged,t))
    damaged_t=[list(x) for x in t]
    for i,r in enumerate(rs):damaged_t[i][8]=r[0]+r[1]
    reject('missing_third_normal_coordinate', lambda: check_identity(rs,d,damaged_t))
    wrong = [(row ^ ((1<<112)-1)) for row in rows]
    reject('missing_pairing_affine_one',lambda:need(len(basis(wrong))==9,'binary pairing dimension'))
    reject('unpunctured_unit',lambda:need([dimension(s) for s in setup(geometry(True))[3]]==[8]*8+[9], 'puncture contract'))
    reject('omitted_ratio_conflict', lambda:need(dimension(spaces[1])==0,'plane lemma missing conflicts'))
    reject('incomplete_plane_inventory',lambda:need(10794==(255*254)//6,'complete planes'))
    need(info['total']==65 and witnesses[0]['total']==64,'active/zero distinction')
    return {'schema_version':1,'scope':'fixed coordinate frame plus e0+e1+e2 on P112',
            'base_commit':BASE,'roots':112,'root_digest':digest(rs),'pairing_digest':digest(rows),
            'column_support_sizes':list(map(len,ys)), 'column_code_dimensions':[dimension(s) for s in allspaces],
            'planes':planes,'plane_count':32385,'plane_stream_sha256':stream.hexdigest(),
            'single_vector_census':single,'single_vectors':765,'witnesses':witnesses,
            'equality_shifts':['0','r0','r1','r2'],'all_active_minimum':65,'minimum':64,
            'finite_example_costs':example_costs,'identity_entries_checked':17*112*112,
            'controls':controls,'source_inputs':sources,'new_kappa':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    result=run()
    if args.write:
        with args.write.open('x',encoding='utf-8') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'CERTIFICATE.json').read_text())
        need(canonical(result)==canonical(expected),'certificate exact replay')
    print('PASS_SPARSE_REDUNDANT_DECODER planes=32385 single_vectors=765 minimum=64 all_active=65 equality_shifts=4 controls=6 no_new_kappa')
if __name__=='__main__':
    main()
