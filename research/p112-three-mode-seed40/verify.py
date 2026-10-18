#!/usr/bin/env python3
"""Exact three-mode P112 COPY obstruction; README supplies the quantified proof.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
Geometry: Mihir Srivastava / PR845 following PR717. Question: PR1473.
No pending theorem is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, permutations, product
import json
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
TRIPLE = (2, 4, 5)  # lexicographic triple number 40 (zero based)
ALL = (1 << 112) - 1
GEOMETRY = 'research/p112-single-lift/geometry.py'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def bm(indices):
    return sum(1 << i for i in indices)


def canonical(vector):
    divisor = gcd(*vector)
    if not divisor:
        return None
    vector = tuple(x // divisor for x in vector)
    return vector if next(x for x in vector if x) > 0 else tuple(-x for x in vector)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def check_sources():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    rows = sources['files']
    paths = [row['path'] for row in rows]
    require(len(paths) == len(set(paths)), 'duplicate source pins')
    require({row['path'] for row in rows if row['usage'] == 'input'} == {
        GEOMETRY, 'research/p112-single-lift/PROOF.md',
        'research/complex-decoder-field-extension-seed44/PROOF.md'},
        'incomplete live source inventory')
    for row in rows:
        if row['usage'] != 'input':
            continue
        p = ROOT / row['path']
        require(p.resolve().is_relative_to(ROOT.resolve()), 'external source path')
        data = p.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob: ' + row['path'])
    return sources


def geometry():
    spec = importlib.util.spec_from_file_location('pinned_p112_geometry', ROOT / GEOMETRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw = module.build()
    module.check_geometry(raw)
    order = sorted(range(112), key=lambda i: max(tuple(raw['roots'][i]), tuple(-x for x in raw['roots'][i])))
    roots, x, labels, duals = [], [], [], []
    for i in order:
        root = raw['roots'][i]
        sign = 1 if tuple(root) > tuple(-z for z in root) else -1
        roots.append(tuple(sign*z for z in root))
        x.append(tuple(sign*z for z in raw['X'][i]))
        labels.append(raw['labels'][i])
        duals.append(raw['duals'][i])
    b = [[(duals[i] & labels[j]).bit_count() % 2 for j in range(112)] for i in range(112)]
    require(len(set(roots)) == 112 and len(set(labels)) == 112, 'duplicate root/label')
    for i in range(112):
        for j in range(112):
            require(dot(roots[i], roots[j]) % 4 == 0, 'nonintegral Gram')
            gram = dot(roots[i], roots[j]) // 4
            require(dot(x[i], x[j]) == 2*gram, 'XX^T != 2G')
            require(b[i][j] == (1+gram) % 2, 'binary pairing binding')
    return module, roots, x, labels, duals, b


def support_strata(x):
    rows = [tuple(row[j] for j in TRIPLE) for row in x]
    normals = sorted({canonical(r) for r in rows} - {None})
    coeffs = {canonical(cross(a,b)) for a,b in combinations(normals, 2)} - {None}
    # Representatives of every rank-one zero flat and the generic zero flat.
    for normal in normals:
        found = next((a for a in product(range(-4,5), repeat=3)
                      if any(a) and dot(a,normal) == 0
                      and all(dot(a,n) != 0 for n in normals if n != normal)), None)
        require(found is not None, 'no rank-one flat representative')
        coeffs.add(canonical(found))
    found = next((a for a in product(range(1,6), repeat=3)
                  if all(dot(a,n) != 0 for n in normals)), None)
    require(found is not None, 'no generic representative')
    coeffs.add(canonical(found))
    supports = {}
    for a in sorted(coeffs):
        mask = bm(i for i,r in enumerate(rows) if dot(r,a))
        supports.setdefault(mask, a)
    require(len(normals) == 13 and len(supports) == 39, 'arrangement coverage')
    return normals, [(a,s) for s,a in sorted(supports.items(), key=lambda item: item[1])]


def transports(x, b):
    tetrads = {bm(j for j,v in enumerate(r) if v) for r in x}
    root_lookup = {max(r,tuple(-v for v in r)): i for i,r in enumerate(x)}
    require(len(root_lookup) == 112 and len(tetrads) == 14, 'frame-coordinate root coverage')
    found = {}
    for perm in permutations(range(8)):
        destination = tuple(sorted(perm[k] for k in TRIPLE))
        if destination in found:
            continue
        if not all(bm(perm[j] for j in bits(t)) in tetrads for t in tetrads):
            continue
        mapping, signs = [], []
        for row in x:
            new = [0]*8
            for j in range(8):
                new[perm[j]] = row[j]
            new = tuple(new)
            key = max(new,tuple(-v for v in new))
            require(key in root_lookup, 'transport does not preserve root lines')
            i = root_lookup[key]
            mapping.append(i)
            signs.append(1 if new == x[i] else -1)
        require(len(set(mapping)) == 112, 'transport is not a bijection')
        require(all(b[i][j] == b[mapping[i]][mapping[j]] for i in range(112) for j in range(112)),
                'transport changed binary pairing')
        found[destination] = {'destination': list(destination), 'permutation': list(perm),
                              'line_map_sha256': hashlib.sha256(json.dumps([mapping, signs]).encode()).hexdigest()}
        if len(found) == 56:
            break
    require(set(found) == set(combinations(range(8),3)), 'incomplete triple transport')
    return [found[k] for k in sorted(found)]


# Exact Gaussian-rational fixture arithmetic. Examples check conventions;
# the arrangement/rank proof, not sampling, gives the complex quantifier.
Z, O, I = (0,0), (1,0), (0,1)


def ga(a,b): return (a[0]+b[0], a[1]+b[1])
def gn(a): return (-a[0],-a[1])
def gm(a,b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
def gc(a): return (a[0],-a[1])


def gd(a,b):
    norm = b[0]*b[0]+b[1]*b[1]
    require(norm != 0, 'singular Gaussian division')
    z = gm(a,gc(b))
    out = (Fraction(z[0],norm), Fraction(z[1],norm))
    return tuple(v.numerator if v.denominator == 1 else v for v in out)


def identity(n): return [[O if i==j else Z for j in range(n)] for i in range(n)]
def transpose(m): return list(map(list,zip(*m)))


def mm(a,b):
    out=[]
    for row in a:
        outrow=[]
        for col in zip(*b):
            value=Z
            for v,w in zip(row,col): value=ga(value,gm(v,w))
            outrow.append(value)
        out.append(outrow)
    return out


def inverse(m):
    n=len(m)
    rows=[list(r)+e for r,e in zip(m,identity(n))]
    for k in range(n):
        pivot=next((i for i in range(k,n) if rows[i][k] != Z),None)
        require(pivot is not None,'singular mixing')
        rows[k],rows[pivot]=rows[pivot],rows[k]
        v=rows[k][k]
        rows[k]=[gd(z,v) for z in rows[k]]
        for i in range(n):
            if i!=k:
                v=rows[i][k]
                rows[i]=[ga(z,gn(gm(v,w))) for z,w in zip(rows[i],rows[k])]
    return [r[n:] for r in rows]


def free_support(left,right,b):
    require(left.bit_count()>=2 and right.bit_count()>=2,'fixture support premise')
    require(all(not b[i][j] for i in bits(left) for j in bits(right)),'nonfree fixture')


def fixtures(x,b,pairrank,exceptions):
    e=exceptions[0]
    U=set(e['erasure']); V=set(e['anchors'])
    a=e['coefficient']
    w=[sum(row[TRIPLE[j]]*a[j] for j in range(3)) for row in x]
    u=[(w[i],0) if i in U else Z for i in range(112)]
    v=[O if i in V else Z for i in range(112)]
    cancel=identity(4)
    for k in range(3): cancel[k][0]=(a[k],0)
    cancel[3][0]=(-1,0)
    complex_m=identity(4)
    for i,j,c in [(0,1,I),(1,2,(Fraction(1,2),0)),(2,3,(1,-1)),(3,0,(2,1)),(0,2,(-1,1))]:
        shear=identity(4);shear[i][j]=c;complex_m=mm(complex_m,shear)
    swap=identity(4);swap[0],swap[2]=swap[2],swap[0]
    cases=[('identity',u,v,identity(4)),('exceptional_cancellation',u,v,cancel),
           ('nonreal_dense',u,v,complex_m),('permuted',u,v,swap),
           ('transpose_nonreal',v,u,transpose(complex_m)),
           ('small_rectangle',[O if i in sorted(U)[:2] else Z for i in range(112)],v,complex_m)]
    receipts=[]; controls=[]; saved={}
    for name,left,right,m in cases:
        us=bm(i for i,z in enumerate(left) if z!=Z);vs=bm(i for i,z in enumerate(right) if z!=Z)
        free_support(us,vs,b)
        A=[[(row[k],0) for k in TRIPLE]+[left[i]] for i,row in enumerate(x)]
        C=[[(row[k],0) for k in TRIPLE]+[right[i]] for i,row in enumerate(x)]
        n=transpose(inverse(m));D=mm(A,m);T=mm(C,n)
        target=mm(A,transpose(C));actual=mm(D,transpose(T))
        require(actual==target,'fixture factor identity')
        ranks=[pairrank(bm(i for i in range(112) if D[i][j]!=Z),
                        bm(i for i in range(112) if T[i][j]!=Z)) for j in range(4)]
        active=[any(m[k][j]!=Z for k in range(3)) and any(n[k][j]!=Z for k in range(3)) for j in range(4)]
        require(sum(active)>=3 and all(not active[j] or ranks[j]>=8 for j in range(4)),
                'fixture contradicts active-term bound')
        receipts.append({'name':name,'support_sizes':[us.bit_count(),vs.bit_count()],
                         'replacement_ranks':ranks,'active_projected_products':sum(active),
                         'whole_copy_sum':40+sum(ranks),'entries_checked':112*112})
        saved[name]=(A,C,m,D,T,target)
    require(receipts[0]['replacement_ranks']==[8,8,8,0],'identity attainment')
    A,C,m,D,T,target=saved['exceptional_cancellation']
    omitted=mm([r[:3] for r in D],transpose([r[:3] for r in T]))
    fail=next(((i,j) for i in range(112) for j in range(112) if b[i][j] and omitted[i][j]!=target[i][j]),None)
    require(fail is not None,'omitted compensation control did not fail')
    controls.append({'name':'omit_compensation','constrained_entry':list(fail)})
    wrong=mm(D,transpose(mm(C,inverse(m))))
    fail=next(((i,j) for i in range(112) for j in range(112) if b[i][j] and wrong[i][j]!=target[i][j]),None)
    require(fail is not None,'wrong inverse-transpose control did not fail')
    controls.append({'name':'wrong_inverse_transpose','constrained_entry':list(fail)})
    A,C,m,D,T,target=saved['nonreal_dense']
    wrong=mm(D,[[gc(v) for v in r] for r in transpose(T)])
    fail=next(((i,j) for i in range(112) for j in range(112) if b[i][j] and wrong[i][j]!=target[i][j]),None)
    require(fail is not None,'Hermitian control did not fail')
    controls.append({'name':'Hermitian_in_place_of_transpose','constrained_entry':list(fail)})
    singular=identity(4);singular[3]=singular[0][:]
    try: inverse(singular)
    except ValueError: controls.append({'name':'singular_mixing'})
    else: raise ValueError('singular matrix accepted')
    badcol=next(j for j in range(112) if any(b[i][j] for i in U))
    try: free_support(bm(U),bm(V | {badcol}),b)
    except ValueError: controls.append({'name':'nonfree_correction','added_column':badcol})
    else: raise ValueError('nonfree correction accepted')
    return receipts,controls


def compute():
    sources=check_sources()
    g,roots,x,labels,duals,b=geometry()
    normals,strata=support_strata(x)
    row_bits=[bm(j for j,v in enumerate(row) if v) for row in b]
    chars=sorted({bm(i for i in range(112) if (duals[i]&q).bit_count()%2) for q in range(512)})
    require(len(chars)==512 and len(g.binary_basis(row_bits))==9,'character coverage')
    require(all(row in chars for row in row_bits),'character space binding')
    odd=[ALL ^ row for row in row_bits]
    def rank(mask): return len(g.binary_basis(labels[i] for i in bits(mask)))
    def pairrank(left,right):
        lb=g.binary_basis(duals[i] for i in bits(left))
        rb=g.binary_basis(labels[j] for j in bits(right))
        return len(g.binary_basis(sum(((v&w).bit_count()%2)<<k for k,w in enumerate(rb)) for v in lb))
    coordinate_supports=[bm(i for i,row in enumerate(x) if row[k]) for k in range(8)]
    coordinate_costs=[pairrank(s,s) for s in coordinate_supports]
    require(coordinate_costs==[8]*8,'unchanged coordinate COPY costs')
    hist=Counter();exceptions=[];digest=hashlib.sha256();nonempty=0
    for index,(coefficient,support) in enumerate(strata):
        for c in chars:
            cut=support & c
            if not cut: continue
            nonempty+=1
            neighbors=ALL
            for i in bits(cut): neighbors &= odd[i]
            count=neighbors.bit_count();hist[count]+=1
            digest.update(f'{index}:{cut:x}:{neighbors:x}\n'.encode())
            require(count<=2,'a cut has three common odd neighbors')
            if count==2:
                anchors=list(bits(neighbors));erasure=odd[anchors[0]] & odd[anchors[1]]
                require(cut==erasure and cut.bit_count()==24,'exception is not the maximal 24-row cut')
                require(rank(support)==9 and rank(support ^ cut)==8,'exceptional span dimensions')
                require(all(pairrank(support ^ cut,t)==8 for _,t in strata),'exceptional pairing floor')
                exceptions.append({'stratum':index,'coefficient':list(coefficient),'character':hex(c),
                                   'erasure':list(bits(cut)),'anchors':anchors,
                                   'span_before':9,'span_after':8,'all_39_pairing_ranks':8})
    require(len(exceptions)==4 and nonempty==19926,'exception/cut census')
    table=[[pairrank(s,t) for _,t in strata] for _,s in strata]
    require(all(v>=8 for row in table for v in row),'original pairing floor')
    controls=[{'name':'reject_three_mode_span_preservation','counterexamples':len(exceptions)}]
    axis=bm(i for i,row in enumerate(x) if row[TRIPLE[0]])
    beta=next(j for j in range(112) if rank(axis & ~odd[j])<rank(axis))
    require(rank(axis)==8 and rank(axis & ~odd[beta])==7,'one-anchor boundary')
    controls.append({'name':'one_anchor_span_loss','anchor':beta,'before':8,'after':7})
    maps=transports(x,b)
    bad=list(range(8));bad[0],bad[1]=bad[1],bad[0]
    tetrads={bm(j for j,v in enumerate(r) if v) for r in x}
    require(any(bm(bad[j] for j in bits(t)) not in tetrads for t in tetrads),'bad transport control')
    controls.append({'name':'nonautomorphism_coordinate_swap'})
    fixture_rows,fixture_controls=fixtures(x,b,pairrank,exceptions)
    controls.extend(fixture_controls)
    return {'schema_version':1,'kind':'scoped-three-mode-copy-obstruction',
            'base_commit':sources['base_commit'],'seed':40,'representative_triple':list(TRIPLE),
            'root_order':'sorted lexicographically larger doubled E8 line representatives; frame removed',
            'geometry_sha256':hashlib.sha256(json.dumps({'roots':roots,'X':x,'B':row_bits},sort_keys=True).encode()).hexdigest(),
            'normal_directions':[list(n) for n in normals],
            'strata':[{'coefficient':list(a),'support':hex(s),'size':s.bit_count(),'span':rank(s)} for a,s in strata],
            'cut_census':{'characters':512,'strata':39,'nonempty':nonempty,
                          'common_odd_neighbor_counts':{str(k):v for k,v in sorted(hist.items())},
                          'ordered_sha256':digest.hexdigest()},
            'exceptions':exceptions,'unmodified_pairing_table':table,
            'coordinate_copy_costs':coordinate_costs,
            'triple_transports':maps,'fixtures':fixture_rows,'controls':controls,
            'claim':{'all_coordinate_triples':56,'replacement_terms':4,
                     'active_terms_at_least':3,'rank_of_each_active_term_at_least':8,
                     'sharp_whole_copy_sum':64,'power_bill':'at least 8*8^q for 0<q<=1',
                     'scope':'One nonzero B-free rank-one correction, both supports of size at least two; GL(4,C) on three coordinate modes; separate COPY billing.'}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path,help='write a regenerated certificate explicitly')
    parser.add_argument('--check',type=Path,default=PACKAGE/'CERTIFICATE.json')
    args=parser.parse_args()
    result=compute()
    if args.write:
        args.write.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(json.loads(args.check.read_text())==result,'certificate mismatch')
    print('PASS_P112_THREE_MODE_COPY strata=39 cuts=19926 exceptions=4 triples=56 COPY=64 controls='+str(len(result['controls'])))


if __name__=='__main__':
    main()
