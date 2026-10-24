#!/usr/bin/env python3
"""Exact replay for a scoped selected-port Gram-family obstruction.

All source, certificate and matrix dimensions are fixed and bounded. Enumeration
uses at most 107240 row multisets, 40320 coordinate permutations, 900 duals,
14400 reflection pairs, 8568 cubic tuples and 33350 signed 3-by-3 candidates. Fraction and Python list allocation is a managed-
runtime deviation; live storage is bounded by these finite domains. No solver,
network, repository checkout, recursion or third-party package is used.
"""
import argparse
from fractions import Fraction as F
import hashlib
from itertools import combinations_with_replacement, permutations, product
import json
from math import lcm, isqrt
from pathlib import Path

SOURCE_SHA256 = '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    require(bool(a) and bool(b) and len(a[0]) == len(b), 'matrix dimensions')
    bt = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in bt] for row in a]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def determinant(a):
    """Bareiss elimination with checked exact divisions and pivoting."""
    n = len(a)
    require(1 <= n <= 112 and all(len(row) == n for row in a), 'square matrix')
    m = [list(row) for row in a]
    previous, sign = 1, 1
    for k in range(n-1):
        pivot_row = next((i for i in range(k, n) if m[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            m[k], m[pivot_row] = m[pivot_row], m[k]
            sign = -sign
        pivot = m[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                value, remainder = divmod(m[i][j]*pivot-m[i][k]*m[k][j], previous)
                require(remainder == 0, 'Bareiss division is not exact')
                m[i][j] = value
            m[i][k] = 0
        previous = pivot
    return sign*m[-1][-1]


def inverse(a):
    n = len(a)
    require(1 <= n <= 8 and all(len(row) == n for row in a), 'inverse dimensions')
    m = [[F(x) for x in row] + [F(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        pivot_row = next((i for i in range(k, n) if m[i][k]), None)
        require(pivot_row is not None, 'matrix is singular')
        m[k], m[pivot_row] = m[pivot_row], m[k]
        pivot = m[k][k]
        m[k] = [x/pivot for x in m[k]]
        for i in range(n):
            if i != k:
                factor = m[i][k]
                m[i] = [x-factor*y for x, y in zip(m[i], m[k])]
    require([row[:n] for row in m] == eye(n), 'inverse elimination failure')
    return [row[n:] for row in m]


def is_power_two(x):
    return x > 0 and x & (x-1) == 0


def unit(q):
    q = abs(F(q))
    return is_power_two(q.numerator) and is_power_two(q.denominator)


def integral_scale(a):
    denominator = lcm(*(F(x).denominator for row in a for x in row))
    return [[int(F(x)*denominator) for x in row] for row in a], denominator


def check_inverse_pair(a, b, name):
    ai, ad = integral_scale(a)
    bi, bd = integral_scale(b)
    target = [[int(i == j)*ad*bd for j in range(len(a))] for i in range(len(a))]
    require(multiply(ai, bi) == target, name+' right inverse')
    require(multiply(bi, ai) == target, name+' left inverse')
    require(is_power_two(ad) and is_power_two(bd), name+' non-dyadic matrix')
    return {'dimension': len(a), 'matrix_denominator': ad, 'inverse_denominator': bd}


def load_columns(path):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'source SHA256 mismatch')
    source = json.loads(raw)
    require(len(source['R']) == 8 and len(source['ports']) == 112, 'source dimensions')
    rows = [[int(F(row.get(str(j), '0'))) for j in range(112)] for row in source['R']]
    require(all(F(row.get(str(j), '0')).denominator == 1
                for row in source['R'] for j in range(112)), 'nonintegral source')
    columns = list(zip(*rows))
    require(all(sum(x*x for x in c) == 4 for c in columns), 'source column norm')
    require(multiply(rows, columns) == [[56*x for x in row] for row in eye(8)], 'source Gram')
    return rows, columns


def gram(columns, selected):
    return [[sum(columns[p][i]*columns[p][j] for p in selected)
             for j in range(8)] for i in range(8)]


def verify_selection(rows, columns, selected):
    require(all(type(p) is int and 0 <= p < 112 for p in selected), 'selection range')
    require(len(selected) == len(set(selected)), 'duplicate selected port')
    require(0 < len(selected) < 112, 'selection size')
    g = gram(columns, selected)
    m52 = [[52*int(i == j)-g[i][j] for j in range(8)] for i in range(8)]
    m4 = [[4*int(i == j)-g[i][j] for j in range(8)] for i in range(8)]
    d52, d4 = determinant(m52), determinant(m4)
    require(unit(d52) and unit(d4), 'both determinants must be signed powers of two')
    t = [[-F(x, 4) for x in row] for row in m52]
    w = [[F(x, 4) for x in row] for row in m4]
    ti, wi = inverse(t), inverse(w)
    check_inverse_pair(t, ti, 'reduced ordinary')
    check_inverse_pair(w, wi, 'reduced corrected')
    k = [[F(x, 4) for x in c] for c in columns]
    selected_set = set(selected)
    e = [-1 if i in selected_set else 1 for i in range(112)]
    low_a = multiply(multiply(k, ti), rows)
    low_ai = multiply(multiply(k, wi), rows)
    a = [[low_a[i][j]+int(i == j)*e[i] for j in range(112)] for i in range(112)]
    ai = [[int(i == j)*e[i]-e[i]*low_ai[i][j]*e[j] for j in range(112)] for i in range(112)]
    full = check_inverse_pair(a, ai, 'full original-input response')
    ordinary = [i for i in range(112) if i not in selected_set]
    ru = [[row[i] for i in ordinary] for row in rows]
    ku = [k[i] for i in ordinary]
    kr = multiply(ku, ru)
    ktir = multiply(multiply(ku, ti), ru)
    h = [[int(i == j)-kr[i][j] for j in range(len(ordinary))] for i in range(len(ordinary))]
    hi = [[int(i == j)+ktir[i][j] for j in range(len(ordinary))] for i in range(len(ordinary))]
    ordinary_check = check_inverse_pair(h, hi, 'ordinary principal response')
    dt, dw = F(d52, 4**8), F(d4, 4**8)
    return {'selected': sorted(selected), 'selected_count': len(selected), 'gram': g,
            'gram_trace': sum(g[i][i] for i in range(8)),
            'det_52I_minus_G': d52, 'det_4I_minus_G': d4,
            'det_T': str(dt), 'det_W': str(dw),
            'det_A': str((-1)**len(selected)*dw/dt),
            'full_inverse_check': full, 'ordinary_inverse_check': ordinary_check}


def canonical_rows(q):
    return [v for v in product((-1,0,1),repeat=q)
            if 0 < sum(x*x for x in v) <= 3 and next(x for x in v if x) == 1]


def positive_definite(c):
    n=len(c)
    a=[[50*int(i==j)-13*c[i][j] for j in range(n)] for i in range(n)]
    return all(determinant([row[:k] for row in a[:k]])>0 for k in range(1,n+1))


def census(r):
    q=8-r
    rows=canonical_rows(q)
    scans=0
    accepted=[]
    for b in combinations_with_replacement(rows,r):
        scans+=1
        edges=sum(x*x for row in b for x in row)
        if edges<6 or edges%2 or any(sum(row[j]*row[j] for row in b)>3 for j in range(q)):
            continue
        c=[[sum(x*y for x,y in zip(bi,bj)) for bj in b] for bi in b]
        d=determinant([[3*c[i][j]-8*int(i==j) for j in range(r)] for i in range(r)])
        if not unit(d) or not positive_definite(c):
            continue
        accepted.append({'B':b,'edge_count':edges,'abstract_port_count':40-edges//2,'reduced_det':d})
    return {'r':r,'q':q,'projective_rows':len(rows),'scanned':scans,'accepted':accepted}


def signature(b):
    r,q=len(b),len(b[0])
    best=None
    for perm in permutations(range(r)):
        for signs in product((-1,1),repeat=r):
            columns=[]
            for j in range(q):
                col=tuple(signs[i]*b[perm[i]][j] for i in range(r))
                first=next((x for x in col if x),1)
                columns.append(col if first>0 else tuple(-x for x in col))
            candidate=tuple(sorted(columns))
            if best is None or candidate<best:
                best=candidate
    return best


def verify_family_census():
    scans=[census(r) for r in range(1,5)]
    classes={(s['r'],signature(c['B'])) for s in scans for c in s['accepted']}
    summary=[{'r':s['r'],'row_domain':s['projective_rows'],'scanned':s['scanned'],
              'accepted':len(s['accepted']),
              'classes':len({signature(c['B']) for c in s['accepted']})} for s in scans]
    require(sum(s['scanned'] for s in scans)==107240,'multiset census')
    require(sum(len(s['accepted']) for s in scans)==1233 and len(classes)==11,'family census')
    return classes,summary


def target_from_block(b, permutation):
    r,q=len(b),len(b[0])
    require(r+q==8 and sorted(permutation)==list(range(8)), 'target dimensions')
    c=multiply(b,list(zip(*b)))
    g=[[20*int(i==j) for j in range(8)] for i in range(8)]
    for i in range(r):
        for j in range(r):
            g[i][j]-=2*c[i][j]
        for j in range(q):
            g[i][r+j]=g[r+j][i]=-8*b[i][j]
    inv=[permutation.index(i) for i in range(8)]
    return [[g[inv[i]][inv[j]] for j in range(8)] for i in range(8)]


def normalized_generator(b):
    removed=sum(not any(row) for row in b)
    trimmed=[row+[0]*removed for row in b if any(row)]
    require(bool(trimmed),'nonzero generator')
    return len(trimmed),signature(trimmed)


def verify_box_cases(data,roots,classes):
    pairs=[(i,j) for i in range(8) for j in range(i,8)]
    require(data['root_vectors']==[list(r) for r in roots], 'root list source binding')
    require(list(map(tuple,data['coefficient_pairs']))==pairs,'coefficient convention')
    require(len(data['cases'])==900,'case count')
    records={};targets=set();gaps=[];generators=set();blocks={};placements={}
    for case in data['cases']:
        key=(case['orientation'],case['canonical_index'],case['placement'])
        require(key not in records,'duplicate case key')
        b=case['block'];permutation=tuple(case['permutation'])
        target=target_from_block(b,list(permutation))
        require(target==case['target'],'target formula')
        y=case['dual']
        require(len(y)==36 and all(type(v)is int for v in y),'integer dual')
        target_value=sum(d*target[i][j] for d,(i,j) in zip(y,pairs))
        values=[sum(d*v[i]*v[j] for d,(i,j) in zip(y,pairs)) for v in roots]
        bound=sum(max(0,v) for v in values)
        gap=target_value-bound
        require(target_value==case['target_value'] and bound==case['box_bound']
                and gap==case['gap'] and gap>0,'strict box separation')
        records[key]=True;targets.add(tuple(map(tuple,target)));gaps.append(gap)
        groupkey=key[:2]
        require(groupkey not in blocks or blocks[groupkey]==b,'changing block in placement list')
        blocks[groupkey]=b
        placements.setdefault(groupkey,{})[key[2]]=permutation
        if key[0]=='normal':
            generators.add(normalized_generator(b))
    expected={(o,c,p) for o in ('normal','transpose') for c in range(15) for p in range(30)}
    require(set(records)==expected and generators==classes,'family-to-certificate coverage')
    for c in range(15):
        require(blocks['transpose',c]==list(map(list,zip(*blocks['normal',c]))),'transpose binding')
    representatives=placements['normal',0]
    require(all(p==representatives for p in placements.values()),'placement indexing')
    require(len(targets)==584 and min(gaps)==4,'certificate census')
    return set(representatives.values()),{'cases':len(records),'distinct_targets':len(targets),
                  'minimum_gap':min(gaps),'maximum_gap':max(gaps)}


def verify_coordinate_coverage(columns,representatives):
    require(all(sum(x!=0 for x in v)==4 and all(x in (-1,0,1) for x in v)
                for v in columns),'source support/sign structure')
    supports={tuple(i for i,x in enumerate(v) if x) for v in columns}
    require(len(supports)==14,'source support count')
    require(all(sum(tuple(i for i,x in enumerate(v) if x)==s for v in columns)==8
                for s in supports),'complete projective signs')
    planes={tuple(x for x in range(8) if ((a&x).bit_count()%2)==b)
            for a in range(1,8) for b in range(2)}
    require(supports==planes,'binary affine-plane supports')
    all_permutations=set(permutations(range(8)))
    group={p for p in all_permutations if {tuple(sorted(p[i] for i in s))
                                          for s in supports}==supports}
    covered={tuple(h[p[i]] for i in range(8)) for p in representatives for h in group}
    require(len(group)==1344 and len(representatives)==30,'automorphism/coset census')
    require(covered==all_permutations,'all coordinate permutations covered')
    return {'supports':len(supports),'sign_patterns_per_support':8,
            'source_coordinate_automorphisms':len(group),'placement_cosets':len(representatives),
            'permutations_covered':len(covered)}


def projective_line(v):
    first=next(x for x in v if x)
    return tuple(x if first>0 else -x for x in v)


def verify_reflection_closure(roots):
    lines={projective_line(r) for r in roots}
    require(len(lines)==120,'projective root count')
    count=0
    for r in lines:
        for v in lines:
            dot=sum(x*y for x,y in zip(r,v))
            require(dot%2==0,'even inner product')
            require(projective_line(tuple(x-dot//2*y for x,y in zip(v,r))) in lines,
                    'root reflection closure')
            count+=1
    return {'projective_root_lines':len(lines),'reflection_pairs':count}


def polynomials():
    result=[];tested=0
    for s in range(0,53,4):
        for a in range(18):
            for b in range(17):
                for sign in (-1,1):
                    tested+=1
                    q,w=2**a,sign*2**b
                    if (q-w)%48:
                        continue
                    u=(q-w)//48-2928+56*s
                    d=64-16*s+4*u-w
                    disc=s*s*u*u-4*u**3-4*s**3*d-27*d*d+18*s*u*d
                    if min(u,d,disc,8112-104*s+u)<0:
                        continue
                    result.append((s,u,d,q,w,disc))
    return tested,result


def symmetric_signature(h):
    return min(tuple(signs[i]*signs[j]*h[perm[i]][perm[j]]
                     for i in range(3) for j in range(3))
               for perm in permutations(range(3)) for signs in product((-1,1),repeat=3))


def matrices(polys):
    classes=set();tested=0
    for s,u,d,_,_,_ in polys:
        for a in range(s//3+1):
            for b in range(a,(s-a)//2+1):
                c=s-a-b
                for x in range(isqrt(a*b)+1):
                    for y in range(isqrt(a*c)+1):
                        z2=a*b+a*c+b*c-u-x*x-y*y
                        if z2<0 or z2>b*c:
                            continue
                        z=isqrt(z2)
                        if z*z!=z2:
                            continue
                        for signed_z in ({z,-z} if z else {0}):
                            tested+=1
                            if a*b*c+2*x*y*signed_z-a*z2-b*y*y-c*x*x != d:
                                continue
                            h=[[a,x,y],[x,b,signed_z],[y,signed_z,c]]
                            classes.add(symmetric_signature(h))
    return tested,classes

def verify_three_cases(data,roots,classes,representatives):
    require(data['root_vectors']==list(map(list,roots)),'three-block source roots')
    pairs=[(i,j) for i in range(8) for j in range(i,8)]
    require(data['coefficient_pairs']==list(map(list,pairs)),'three-block coefficient convention')
    counts={'root_pair_congruence':0,'box_separator':0}
    keys=set();blocks={};placements={};gaps=[]
    require(len(data['cases'])==720,'three-block case count')
    for case in data['cases']:
        key=(case['index'],case['placement']);p=case['permutation'];g=case['target']
        require(key not in keys and sorted(p)==list(range(8)),'three-block key/permutation')
        keys.add(key)
        unplaced=[[g[p[i]][p[j]] for j in range(8)] for i in range(8)]
        h=[row[:3] for row in unplaced[:3]]
        require(all(unplaced[i][j]==(h[i][j] if i<3 and j<3 else 20*int(i==j))
                    for i in range(8) for j in range(8)),'three-block formula')
        require(key[0] not in blocks or blocks[key[0]]==h,'changing three-coordinate block')
        blocks[key[0]]=h;placements.setdefault(key[0],set()).add(tuple(p))
        if case['kind']=='root_pair_congruence':
            i,j=case['root_pair']
            require(0<=i<120 and 0<=j<120,'root-pair index')
            s,r=roots[i],roots[j]
            value=sum(s[a]*g[a][b]*r[b] for a in range(8) for b in range(8))
            require(case['modulus']==4 and value==case['target_value']
                    and value%4==case['target_residue']!=0,'root-pair congruence exclusion')
        elif case['kind']=='box_separator':
            y=case['dual']
            require(len(y)==36 and all(type(x)is int for x in y),'three-block integer dual')
            value=sum(d*g[i][j] for d,(i,j) in zip(y,pairs))
            bound=sum(max(0,sum(d*r[i]*r[j] for d,(i,j) in zip(y,pairs))) for r in roots)
            require(value==case['target_value'] and bound==case['box_bound']
                    and value-bound==case['gap']>0,'three-block box exclusion')
            gaps.append(value-bound)
        else:
            raise ValueError('unknown three-block certificate kind')
        counts[case['kind']]+=1
    require(keys=={(i,p) for i in range(24) for p in range(30)},'all three-block cases')
    require({symmetric_signature(h) for h in blocks.values()}==classes,'three-block catalogue binding')
    require(all(p==representatives for p in placements.values()),'three-block placement coverage')
    return {'cases':len(keys),'certificate_kinds':counts,
            'minimum_box_gap':min(gaps),'maximum_box_gap':max(gaps)}


def verify_three_catalogue():
    parameter_tests,polys=polynomials()
    matrix_tests,classes=matrices(polys)
    require(parameter_tests==8568 and len(polys)==20,'polynomial catalogue')
    require(matrix_tests==33350 and len(classes)==24,'integral matrix catalogue')
    return classes,{'parameter_tuples':parameter_tests,'admissible_polynomials':len(polys),
                    'signed_matrix_candidates':matrix_tests,'classes':len(classes)}


def replay():
    base=Path(__file__).parent
    rows,columns=load_columns(base/'SOURCE-INTERFACE.json')
    roots=list(map(tuple,columns))+[tuple(2*int(i==j) for j in range(8)) for i in range(8)]
    classes,census_summary=verify_family_census()
    data=json.loads((base/'BOX-CERTIFICATES.json').read_text())
    representatives,box=verify_box_cases(data,roots,classes)
    coordinates=verify_coordinate_coverage(columns,representatives)
    reflections=verify_reflection_closure(roots)
    three_classes,three_census=verify_three_catalogue()
    three=verify_three_cases(json.loads((base/'THREE-BLOCK-CERTIFICATES.json').read_text()),
                             roots,three_classes,representatives)
    selection=[1,3,4,17,18,19,20,23,24,26,27,29,35,36,38,39,40,42,45,
               60,63,66,69,74,75,77,78,84,86,88,97,99,104,105,107,108,109,111]
    baseline=verify_selection(rows,columns,selection)
    require(baseline['gram']==target_from_block([[1,1,0,0,0,0],[0,0,1,1,0,0]],
                                               list(range(8))),'sharp 38-port family membership')
    require(baseline['det_T']==str(2**24) and baseline['det_W']==str(2**12)
            and baseline['det_A']=='1/4096','predecessor calibration')
    selected39=[3,5,6,7,10,11,17,18,20,21,28,29,36,37,38,39,40,43,50,51,52,57,62,63,64,65,66,67,69,77,78,79,81,95,96,99,103,104,106]
    sharp=verify_selection(rows,columns,selected39)
    h=[[16,-8,-8],[-8,20,0],[-8,0,20]]
    target=[[h[i][j] if i<3 and j<3 else 20*int(i==j) for j in range(8)] for i in range(8)]
    require(sharp['gram']==target and sharp['det_52I_minus_G']==2**40
            and sharp['det_4I_minus_G']==2**30,'sharp 39-port witness')
    return {'family_census':census_summary,'generator_classes':len(classes),
            'box_separation':box,'coordinate_coverage':coordinates,
            'reflection_closure':reflections,'predecessor_calibration':baseline,
            'three_block_census':three_census,'three_block_exclusions':three,'sharp_39_port_witness':sharp,
            'input_sha256':{name:hashlib.sha256((base/name).read_bytes()).hexdigest()
                            for name in ('SOURCE-INTERFACE.json','BOX-CERTIFICATES.json','THREE-BLOCK-CERTIFICATES.json')},
            'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    result=replay()
    receipt=Path(__file__).with_name('REPLAY.json')
    if args.write_receipt:
        receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(json.loads(receipt.read_text())==result,'receipt mismatch')
    print('PASS: '+str(result['generator_classes'])+' generator classes; '+
          str(result['box_separation']['cases'])+' exact separators; sharp three-block minimum 39; S38 calibration')


if __name__=='__main__':
    main()
