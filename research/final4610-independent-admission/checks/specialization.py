#!/usr/bin/env python3
"""Finite membership/census witness for the written same-premise P1 theorem.

Reads actual supplied file bytes. No Git reads, evaluator imports, native
simulation, or assumption that the new catalogue is a physical primitive.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import time

from . import source
def need(ok,why):
    if not ok: raise ValueError(why)

def span(basis):
    s={0}
    for v in basis:
        need(type(v) is int and 0<v<512,'binary9 basis vector')
        s|={x^v for x in tuple(s)}
    need(len(s)==2**len(basis),'independent basis')
    return frozenset(s)

def eliminate(rows):
    need(len(rows)==9 and all(type(x)is int and 0<=x<512 for x in rows),'binary9 rows')
    work=list(rows);ops=[]
    for j in range(9):
        piv=next((k for k in range(j,9) if (work[k]>>j)&1),None)
        need(piv is not None,'invertible affine matrix')
        if piv!=j:
            work[j],work[piv]=work[piv],work[j];ops.append(('swap',j,piv))
        for k in range(9):
            if k!=j and (work[k]>>j)&1:
                work[k]^=work[j];ops.append(('xor',k,j))
    need(work==[1<<j for j in range(9)],'row elimination identity')
    need(sum(op[0]=='swap' for op in ops)<=8 and sum(op[0]=='xor' for op in ops)<=72,'finite row-operation bound')
    return list(reversed(ops))

def mv(rows,x):
    return sum(((row&x).bit_count()&1)<<j for j,row in enumerate(rows))

def apply_ops(ops,x):
    for op,i,j in ops:
        a=(x>>i)&1;b=(x>>j)&1
        if op=='xor':x^=b<<i
        else:x^=((a^b)<<i)|((a^b)<<j)
    return x

def qvalue(m,x):
    alpha=m['linear_Z4'];Q=m['quadratic_rows']
    return (m['phase']+sum(alpha[i] for i in range(9) if (x>>i)&1)
            +2*sum(((Q[i]>>(i+1))&(x>>(i+1))).bit_count()%2
                   for i in range(9) if (x>>i)&1))%4

def monomial(m):
    need(set(m)=={'matrix_rows','offset','phase','linear_Z4','quadratic_rows'},'exact monomial grammar')
    A=m['matrix_rows'];ops=eliminate(A)
    b=m['offset'];a=m['phase'];alpha=m['linear_Z4'];Q=m['quadratic_rows']
    need(type(b)is int and 0<=b<512,'binary affine offset')
    need(type(a)is int and 0<=a<4,'absolute Z4 constant')
    need(len(alpha)==9 and all(type(x)is int and 0<=x<4 for x in alpha),'Z4 linear phase')
    need(len(Q)==9 and all(type(x)is int and 0<=x<512 for x in Q),'binary quadratic matrix')
    need(all(((Q[i]>>j)&1)==((Q[j]>>i)&1) for i in range(9) for j in range(9)),'symmetric quadratic matrix')
    need(all((alpha[i]&1)==((Q[i]>>i)&1) for i in range(9)),'Clifford diagonal parity')
    pairs=[(i,j) for i in range(9) for j in range(i+1,9) if (Q[i]>>j)&1]
    probes={0,511,341,170}|{1<<i for i in range(9)}|{(1<<i)|(1<<j) for i in range(9) for j in range(i+1,9)}
    for x in probes:
        need((apply_ops(ops,x)^b)==(mv(A,x)^b),'constructive affine decomposition')
        primitive_phase=(a+sum(alpha[i]*((x>>i)&1) for i in range(9))
                         +2*sum(((x>>i)&1)*((x>>j)&1) for i,j in pairs))%4
        need(qvalue(m,x)==primitive_phase,'exact phase polynomial decomposition')
    elementary=sum(3 if op[0]=='swap' else 1 for op in ops)+b.bit_count()+sum(alpha)+len(pairs)+a
    need(elementary<=171,'one monomial finite primitive-record bound')
    for f in (1,2,3,4):
        xs=[(j*73+341)%512 for j in range(f)]
        expected=sum(qvalue(m,x) for x in xs)%4
        lifted=(a*f+sum(qvalue(m,x)-a for x in xs))%4
        need(expected==lifted,'tensor absolute phase multiplicity')
    return elementary,len(ops),len(pairs)

def scalar_cost(g):
    need(g[0] in ('add','scale','copy','clear'),'retained scalar opcode')
    if g[0] in ('copy','clear'):return 2
    q=Fraction(g[3],g[4]) if g[0]=='add' else Fraction(g[2],g[3])
    n,d=abs(q.numerator),q.denominator
    need(n and not d&(d-1),'nonzero dyadic scalar')
    if g[0]=='scale':
        need(not n&(n-1),'dyadic unit scale')
        return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)

def program_schema(c,word):
    spaces=[span(b) for b in c['frames']]
    need(len(c['start'])==len(c['final'])==632,'exact arbitrary owner count')
    current={('L',r):c['start'][r] for r in range(632)};current['C',0]=0
    cost=0;profile=Counter();types=Counter()
    for e in word:
        typ=e[0];types[typ]+=1
        need(typ in ('scalar','climb','center','warp','adapter','phase'),'retained event grammar')
        if typ=='scalar':
            g,frame=e[1:];target=tuple(g[1]);need(target in current,'declared scalar owner')
            cost+=scalar_cost(g)
            if g[0]=='clear':
                need(target==('C',0),'no borrowed clear');current[target]=frame
            else:
                need(current[target]==frame,'scalar target frame')
                if g[0] in ('copy','add'):
                    source=tuple(g[2]);need(source in current and source!=target,'distinct actual owner slots')
                    need(current[source]==frame,'scalar source frame')
                    if g[0]=='copy':need(target==('C',0),'no borrowed overwrite')
        elif typ in ('climb','center'):
            if typ=='climb':
                _,_,r,a,b,rank=e;target=('L',r);need(spaces[a]<spaces[b],'nested borrowed transition')
            else:
                _,r,a,b,rank=e;target=('C',r)
                need(target==('C',0) and (spaces[a]<spaces[b] or spaces[b]<spaces[a]),'owned nested transition')
            need(target in current and current[target]==a,'paid current owner/frame')
            need(rank==abs(len(c['frames'][b])-len(c['frames'][a])) and 1<=rank<=9,'exact positive child rank')
            current[target]=b;profile[rank]+=1
        elif typ=='warp':
            _,r,op,a,b=e;target=tuple(r)
            need(target in current and current[target]==a,'warp owner/frame');current[target]=b
    need([current['L',r] for r in range(632)]==c['final'],'all final owner frames')
    need(next(e for e in reversed(word) if e[0]=='scalar' and e[1][1]==['C',0])[1][0]=='clear','final owned erase event')
    return {'scalar_allowance':cost,'profile':dict(sorted(profile.items())),'events':dict(types)}

def run():
    start=time.monotonic();pins=['docs/research/pr-intake-evidence/pr4359/PROOF-REVIEW.md', 'docs/research/pr-intake-evidence/pr4416/PROOF-REVIEW.md', 'docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md', 'notes/general-clifford-frames.tex', 'notes/compact-control-movement.tex', 'research/kappa-rebuild/transfer-audit/FINITE-TEMPLATE-CLOSURE.md', 'research/query-thinned-controllers/PROOF.md', 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz', 'research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz', 'research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json', 'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json', 'research/joint-helper-lattice/CONTROLLER.json', 'research/joint-helper-lattice/NATIVE.json.gz', 'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz', 'research/kappa-rebuild/complex/rebuild_native.py', 'research/kappa-function-composition/complex/prune_native.py', 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'research/kappa-round6-compiler-tightening-20261022/arithmetic.py']
    if 'notes/stopped-product-complex.tex' not in pins:pins.append('notes/stopped-product-complex.tex')
    for path in pins:source.raw(path)
    read=source.js
    word=read('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz');c=word['canonical'];native=read('research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json')
    ph=read('research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz');selected=read('research/joint-helper-lattice/NATIVE.json.gz')
    base=read('research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    payload=hashlib.sha256(gzip.decompress(source.raw('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'))).hexdigest()
    need(payload=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','final payload')
    need(native['actual_word_canonical_sha256']==ph['actual_word_canonical_sha256']==payload,'receipt word binding')
    monomials=[];families={}
    for family in ('actual_warp_classes','new_paid_pairs','changed_helper_boundaries'):
        families[family]=len(ph[family])
        for row in ph[family]:
            if 'G_columns' in row:eliminate(row['G_columns'])
            need(set(row['recipes'])=={'forward','backward'},'both orientations')
            for d,rec in row['recipes'].items():
                need(0<=rec['rank']<=9,'recipe child rank')
                if family=='actual_warp_classes':need(rec['rank']==0,'rankzero transported native warp')
                costs=[monomial(rec['left'])]
                if rec['rank']:costs.append(monomial(rec['right']))
                else:need(rec['right']is None,'rankzero single adapter')
                need(sum(z[0] for z in costs)<=342,'two adapter group below1000records')
                monomials.extend(costs)
    selected_monomials=0
    for row in selected['new_physical_edges_and_boundaries']:
        for rec in row['recipes'].values():
            monomial(rec['left']);selected_monomials+=1
            if rec['rank']:monomial(rec['right']);selected_monomials+=1
    summaries={}
    for d,w in word['programs'].items():
        summaries[d]=program_schema(c,w)
        need([e[1] for e in w if e[0]=='scalar']==[e[1] for e in base[d] if e[0]=='scalar'],'exact unchanged scalar opcode/coefficient chronology')
        selected_adapters=[e for e in base[d] if e[0]=='adapter' and e[1]in ('old_to_new','new_to_old') and e[2]<224]
        need([e for e in w if e[0]=='adapter']==selected_adapters,'exact inherited main entrance/exit charts')
        need(summaries[d]['scalar_allowance']==native['native'][d]['real_scalar_allowance'],'source primitive allowance')
        need(summaries[d]['profile']=={int(k):v for k,v in native['paid'].items()},'paid census binding')
    helper_profile=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];need(span(c['frames'][a])<span(c['frames'][b]),'arbitrary helper strict wholejob')
        helper_profile[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(dict(helper_profile)=={4:28,7:7,8:47,9:326},'helper census')
    counts=summaries['forward']['events'];paid=sum(summaries['forward']['profile'].values())
    groups=paid+2*408+counts['warp']+counts['adapter']
    need((paid,counts['warp'],counts['adapter'],groups)==(3298,240,448,4802),'complete raw route groups')
    local_scalar=max(x['scalar_allowance'] for x in summaries.values());routes=groups*1000
    need(local_scalar==158168 and routes==4802000 and local_scalar+routes<10**7,'retained local raw allowance')
    ctl=read('research/joint-helper-lattice/CONTROLLER.json');ar=read('research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json')
    raw=18*10**7+15*1792+32*112*(len(ctl['physical_events'])+sum(len(ctl['boundaries'][d+'_program']) for d in ('left','right')))
    need(raw==181098496 and raw<10**9 and raw==ar['nonrecursive']['raw_scalar_upper'],'complete raw controller charge')
    controls=[]
    import copy
    sample=ph['actual_warp_classes'][0]['recipes']['forward']['left']
    bad=copy.deepcopy(sample);bad['matrix_rows']=[0]*9
    tests=[('singular affine recipe',lambda:monomial(bad))]
    badphase=copy.deepcopy(sample);badphase['phase']=4;tests.append(('nonZ4 absolute phase',lambda:monomial(badphase)))
    badword=copy.deepcopy(word['programs']['forward']);e=next(e for e in badword if e[0]=='scalar' and e[1][0]=='clear');e[1][1]=['L',0]
    tests.append(('borrowed owner clear',lambda:program_schema(c,badword)))
    badrank=copy.deepcopy(word['programs']['forward']);next(e for e in badrank if e[0]=='climb')[5]+=1;tests.append(('unpaid rank change',lambda:program_schema(c,badrank)))
    tests.append(('non-dyadic scalar',lambda:scalar_cost(['add',['L',0],['L',1],1,3])))
    for name,fn in tests:
        try:fn()
        except ValueError:controls.append(name)
        else:raise ValueError('negative control accepted '+name)
    nonzero=next(m for family in ('actual_warp_classes','new_paid_pairs','changed_helper_boundaries') for row in ph[family] for rec in row['recipes'].values() for m in (rec['left'],rec.get('right')) if m and m['phase'])
    need((2*nonzero['phase'])%4!=nonzero['phase'],'phase multiplicity mutation discriminates');controls.append('unlifted absolute phase atf2')
    out={'status':'PASS_EXACT_CATALOGUE_SPECIALIZATION_SCHEMA_AND_RAW_FINITE_TARIFF',
         'candidate_payload':payload,'source_inputs':len(pins),'families':families,'new_monomials':len(monomials),
         'selected_monomials_same_schema':selected_monomials,'max_new_elementary_records_per_monomial':max(x[0] for x in monomials),
         'uniform_elementary_bound_one_monomial':171,'uniform_elementary_bound_two_adapters':342,
         'programs':summaries,'helper_profile':dict(helper_profile),'raw_route_groups':groups,
         'raw_local_scalar':local_scalar,'raw_local_routes':routes,'raw_local_total':local_scalar+routes,
         'raw_controller_upper':raw,'controls':controls,'seconds':time.monotonic()-start,
         'scope':'Written proof supplies all-f physical specialization under selected generic primitive hypotheses. Executable authenticates actual bytes and finite membership/census/decomposition. No exact recipe phase replay or full physical theorem is claimed by this checker.',
         'tape_tariff_unit':'finite retained primitive-record count; not a literal1000-tape-step claim',
         'expanded_compiler_counts':'fresh template counts and semantic constants required, not raw1e9 cap'}
    return out
