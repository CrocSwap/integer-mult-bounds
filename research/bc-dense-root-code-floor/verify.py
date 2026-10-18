#!/usr/bin/env python3
"""Source-bound B/C root-code floor; ywz65 with OpenAI Codex assistance."""
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import model as m

def source():
    manifest=json.loads((HERE/'SNAPSHOTS.json').read_text())
    for item in manifest['files']:
        raw=(HERE/item['snapshot']).read_bytes()
        m.require(hashlib.sha256(raw).hexdigest()==item['sha256'],'snapshot hash mismatch')
        m.require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'snapshot blob mismatch')
    tree=ast.parse((HERE/'snapshots/pr2272-search.py').read_text())
    names={'canon','lines','Bn','Cn','dot','rank2','b0_rows','supports','cost_from_supports'}
    nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
    m.require({x.name for x in nodes}==names,'source function binding')
    env={}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'pinned-PR2272-functions','exec'),env)
    return env

def price(rows,p,q):
    total=[]
    for a,b in zip(p,q):
        rs=[i for i,x in enumerate(a) if x];cs=[i for i,x in enumerate(b) if x]
        total.append(m.rank2(m.block(rows,rs,cs)))
    return total

def outer(p,q):
    return [[sum(a[i]*b[j] for a,b in zip(p,q)) for j in range(len(p[0]))] for i in range(len(p[0]))]

def experiment():
    old=source();positive=[];identical_rows=0;star_checks=0
    for n in range(1,17):
        for kind in ('B','C'):
            lines=m.roots(n,kind);rows=m.dense(lines)
            source_lines=list(map(tuple,old[kind+'n'](n)))
            m.require(len(set(source_lines))==len(lines) and set(lines)==set(source_lines),'predecessor root generator differs')
            permutation=[source_lines.index(r) for r in lines]
            source_rows=old['b0_rows'](source_lines)
            m.require(rows==m.block(source_rows,permutation,permutation),'predecessor pairing differs after explicit row permutation')
            for k in range(n,len(lines),2):
                m.require(rows[k]==rows[k+1],'opposite root signs have different dense rows')
                identical_rows+=1
            vectors=[[int(i==j) for j in range(n)] for i in range(n)]
            for x in vectors:
                for y in vectors:
                    m.verify_star(lines,rows,x,y);star_checks+=1
            expected=[n]*n
            supports=old['supports'](lines)
            m.require(old['cost_from_supports'](rows,supports,supports)==expected,'original coordinate decoder price')
            positive.append({'kind':kind,'n':n,'lines':len(lines),'term_ranks':expected,'cost':n*n})
    # Complete canonical rational support-cell cross checks, with left symmetry reduction.
    census=[]
    for n in range(1,7):
        lines=m.roots(n);rows=m.dense(lines);patterns=m.patterns(n)
        masks=[sum(1<<i for i in m.support(lines,x)) for x in patterns]
        counts=Counter()
        for x in m.orbit_representatives(n):
            selected=[rows[i] for i in m.support(lines,x)]
            for y,mask in zip(patterns,masks):
                rank=m.rank2([r&mask for r in selected]);m.require(rank>=n,'support-cell lower bound')
                counts[rank]+=1
        census.append({'n':n,'right_cells':len(patterns),'left_orbits':len(list(m.orbit_representatives(n))),
                       'ranks':{str(k):v for k,v in sorted(counts.items())}})
    # Coefficient fields are distinct from the binary rank field.
    finite_pairs=0
    for prime,n in ((3,2),(3,3),(5,2),(5,3),(7,2)):
        lines=m.roots(n);rows=m.dense(lines)
        vectors=[v for v in itertools.product(range(prime),repeat=n) if any(v)]
        for x in vectors:
            for y in vectors:m.verify_star(lines,rows,x,y,prime);finite_pairs+=1
    # Exact noncoordinate and overcomplete Gram factorizations, not support-only samples.
    decoder_tests=[]
    for n in range(2,7):
        for kind in ('B','C'):
            lines=m.roots(n,kind);rows=m.dense(lines)
            original=[[Q(r[j]) for r in lines] for j in range(n)]
            gram=outer(original,original)
            for a,b in itertools.permutations(range(n),2):
                p=[r[:] for r in original];q=[r[:] for r in original];scale=Q(3,2)
                p[b]=[x+scale*y for x,y in zip(p[b],p[a])]
                q[a]=[x-scale*y for x,y in zip(q[a],q[b])]
                m.require(outer(p,q)==gram,'noncoordinate factorization not exact')
                ranks=price(rows,p,q);m.require(min(ranks)>=n,'noncoordinate floor')
                # Split one nonzero rank-one contribution into two equal pieces.
                p.append(p[0][:]);q[0]=[x/2 for x in q[0]];q.append(q[0][:])
                m.require(outer(p,q)==gram,'overcomplete factorization not exact')
                extended=price(rows,p,q);m.require(min(extended)>=n and sum(extended)>=n*(n+1),'overcomplete floor')
                decoder_tests.append((n,kind,sum(ranks),sum(extended)))
    # Each named restriction is necessary for the local star argument.
    lines=m.roots(2);rows=m.dense(lines);x=(1,1);y=(1,-1)
    rs=m.support(lines,x);cs=m.support(lines,y)
    sparse=rows[:];sparse[2]&=~(1<<3);sparse[3]&=~(1<<2)
    m.require(m.rank2(m.block(rows,rs,cs))==2 and m.rank2(m.block(sparse,rs,cs))==1,'density counterexample')
    primitive=[tuple(z//2 for z in r) for r in lines]
    char2=m.support(primitive,(1,1),2)
    m.require(m.rank2(m.block(rows,char2,char2))==1,'characteristic2 counterexample')
    puncture=[0,1,2];survivors=[i for i in m.support(lines,(1,-1)) if i in puncture]
    m.require(m.rank2(m.block(rows,survivors,survivors))==1,'missing opposite root counterexample')
    m.require(m.rank2(m.block(rows,[0],[0]))==1,'outside-root-code singleton')
    coordinate=[[Q(r[j]) for r in lines] for j in range(2)]
    p=coordinate+[[Q(0)]*4];q=coordinate+[coordinate[0][:]]
    m.require(price(rows,p,q)==[2,2,0] and outer(p,q)==outer(coordinate,coordinate),'zero term counting control')
    m.require(price(rows,[coordinate[0]],[coordinate[0]])==[2] and outer([coordinate[0]],[coordinate[0]])[1][1]==0,
              'rank-deficient realization control')
    return {'positive_source_bound_decoders':positive,'opposite_sign_row_equalities':identical_rows,
            'ordered_coordinate_star_checks':star_checks,'rational_support_cells':census,
            'finite_coefficient_field_pairs':finite_pairs,'exact_sheared_and_split_decoders':len(decoder_tests),
            'decoder_table_sha256':hashlib.sha256(json.dumps(decoder_tests).encode()).hexdigest(),
            'controls':{'sparse_dense_counterexample_rank':1,'characteristic2_rank':1,'missing_partner_rank':1,
                        'outside_code_singleton_rank':1,'zero_term_ranks':[2,2,0],'inadmissible_rank_one_cost':2},
            'all_size_theorem':'For n>=1, coefficient char!=2, full B_n/C_n dense F2 pairing and root-code factors: cost>=n*t>=n^2; coordinate Gram attains n^2.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=experiment();text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(text,encoding='utf-8',newline='\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        m.require(json.dumps(expected,sort_keys=True)==json.dumps(result,sort_keys=True),'typed receipt mismatch')
    print('PASS_BC_DENSE_ROOT_CODE_FLOOR dimensions=16 characteristic_ne_2=1 controls=6')

if __name__=='__main__':main()
