#!/usr/bin/env python3
"""Exact finite controls for the all-p written cut-normal-form theorem.

This verifier does not infer an all-p theorem from finite examples.
Prepared for Cinna Davis with OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse,ast,itertools,json,random
import model as M

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def source_controller():
    path=ROOT/'research/kappa-rebuild/bit/complex_controller_factor.py'
    tree=ast.parse(path.read_text());names={'plus','monomial_times','controller'}
    fs=[f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name in names]
    need({f.name for f in fs}==names,'Exact pure source-function inventory')
    ctx={'Q':Fraction}
    exec(compile(ast.Module(body=fs,type_ignores=[]),str(path),'exec'),ctx)
    return ctx['controller']


def mapped_events(events,slots):
    out=[]
    for e in events:
        if e[0]=='local':out.append(['LOCAL',*e[1:]])
        elif e[0]=='idle':
            j,ss=slots[e[1]];out.append(['IDLE',j,list(ss)])
        elif e[0]=='add':out.append(['ADD',*e[1:]])
        else:out.append(['SIGNED_SWAP',*e[1:]])
    return out


def source_numeric(coeff,p,values):
    n=2*p;a=[[0]*n for _ in range(n)]
    for exps,mat in coeff.items():
        scalar=1
        for stage,degree in enumerate(exps[1:]):scalar*=values.get(stage,1)**degree
        for i in range(n):
            for j in range(n):a[i][j]+=scalar*mat[i][j]
    return a


def projection_checks():
    constructor=source_controller();source_cases=0;projectors=0;nodes=0
    for p in range(1,8):
        events,slots=M.template(p)
        coefficients,written,_=constructor(p,(1<<len(slots))-1)
        need(mapped_events(events,slots)==written,'Every source event and idle window')
        values={s:s+2 for s in range(2*p+1)}
        need(M.evaluate(p,events,slots,values)==source_numeric(coefficients,p,values),
             'Independent interpreter agrees with source Laurent coefficients')
        source_cases+=1
        for stage in M.thick(p):
            j=M.vertex(p,stage)
            available=[i for i,(_,ss) in enumerate(slots) if stage in ss]
            need(len(available)==p-1,'Exactly one idle option at every other vertex')
            for bits in range(1<<(p-1)):
                chosen={i for k,i in enumerate(available) if bits>>k&1}
                mask=(1<<j)|sum(1<<slots[i][0] for i in chosen)
                want=M.projector(p,j,mask)
                need(M.multiply(want,want)==want,'Closed projector is idempotent')
                assignment=[(v,(stage,) if i in chosen else ()) for i,(v,_) in enumerate(slots)]
                # Degree <= p: p+1 nodes certify this one-variable polynomial.
                for value in range(p+1):
                    actual=M.evaluate(p,events,assignment,{stage:value})
                    expected=[[int(r==c)+(value-1)*(want[r//2][c//2] if r%2==c%2==0
                                else want[c//2][r//2] if r%2==c%2==1 else 0)
                               for c in range(2*p)] for r in range(2*p)]
                    need(actual==expected,'Actual single-stage projector in both blocks')
                    nodes+=1
                projectors+=1
    coeff,_,_=constructor(2,0,wrong_reverse_sign=True)
    events,slots=M.template(2)
    need(source_numeric(coeff,2,{})!=M.evaluate(2,events,[(j,()) for j,_ in slots],{}),
         'Wrong backward sign rejected against actual source')
    return {'source_words':source_cases,'stage_subsets':projectors,'integer_nodes':nodes,
            'wrong_backward_sign_rejected':True}


def binary_source_checks():
    path=ROOT/'research/kappa-rebuild/bit/mixed_productive_bit.py'
    tree=ast.parse(path.read_text())
    names={'shift','add','polynomial_coefficients','physical_controller'}
    fs=[f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name in names]
    need({f.name for f in fs}==names,'Exact pure binary function inventory')
    ctx={'need':need};exec(compile(ast.Module(body=fs,type_ignores=[]),str(path),'exec'),ctx)
    constructor=source_controller();cases=0
    for p in range(1,8):
        mask=(1<<(3*(p-1)))-1
        integer,_,_=constructor(p,mask)
        binary,_,_=ctx['physical_controller'](p,mask)
        reduced={}
        for exps,matrix in integer.items():
            key=sum((e%2)<<i for i,e in enumerate(exps))
            target=reduced.setdefault(key,[0]*(2*p))
            for i,row in enumerate(matrix):
                for j,v in enumerate(row):
                    need(v.denominator==1,'Integral source coefficients')
                    if v.numerator%2:target[i]^=1<<j
        reduced={k:v for k,v in reduced.items() if any(v)}
        need(reduced==binary,'Actual BIT source is the involutive characteristic-two specialization')
        cases+=1
    return {'binary_group_ring_source_words':cases,'quotient':'F2[(Z/2)^(2p+2)]'}


def commutator_checks():
    count=0
    for p in range(1,7):
        for j in range(p):
            for k in range(j,p):
                for s in range(1<<p):
                    if not s>>j&1:continue
                    a=M.core(p,j,s);x=M.projector(p,j,s)
                    for t in range(1<<p):
                        if not t>>k&1:continue
                        b=M.core(p,k,t);y=M.projector(p,k,t)
                        xy=M.multiply(x,y);yx=M.multiply(y,x)
                        actual=xy==yx
                        overlap=max(a[0],b[0])<=min(a[1],b[1])
                        need(actual==overlap,'Commutation iff core intervals intersect')
                        need(all((r-s)%2==0 for arow,brow in zip(xy,yx)
                                 for r,s in zip(arow,brow))==overlap,
                             'Same necessary core condition in characteristic two')
                        count+=1
    need(M.multiply(M.projector(2,0,1),M.projector(2,1,2))!=
         M.multiply(M.projector(2,1,2),M.projector(2,0,1)),
         'Removing all idles fails the diagonalization necessity')
    return {'exact_subset_pairs':count,'characteristic_two_subset_pairs':count,
            'unpaid_no_idle_diagonal_rejected':True}


def endpoint_checks():
    cases=0;canonical=0
    for p in range(1,9):
        events,slots=M.template(p);stages=M.thick(p)
        for seed in range(16):
            rng=random.Random(100*p+seed)
            masks=[rng.randrange(1<<p)|(1<<M.vertex(p,s)) for s in stages]
            values={s:rng.randint(2,9) for s in stages}
            assignment=[(i,tuple(s for s,mask in zip(stages,masks)
                               if s in available and mask>>i&1)) for i,available in slots]
            initial=[1]*p;terminal=[1]*p;d=[1]*p
            for s,mask in zip(stages,masks):
                j=M.vertex(p,s);d[j]*=values[s]
                for i in range(p):
                    if i!=j and mask>>i&1:
                        (initial if i>j else terminal)[i]*=values[s]
            # Closed recurrence from PROOF.md, independently evaluated on every input.
            q=Fraction(2)
            actual=M.evaluate(p,events,assignment,values,q=q)
            expected=[[0]*(2*p) for _ in range(2*p)]
            for col in range(2*p):
                aa=[];bb=[]
                for j in range(p):
                    aa.append(-q*d[j]*initial[j]*int(col==2*j+1)-d[j]*(aa[-1] if aa else 0))
                    bb.append((d[j]*initial[j]*int(col==2*j)+
                               (initial[j+1]*int(col==2*j+2) if j+1<p else 0))/q)
                for j in range(p):
                    expected[2*j][col]=sum((-1)**(k-j)*terminal[k]*bb[k] for k in range(j,p))
                    expected[2*j+1][col]=-(terminal[j]*aa[j]+(terminal[j-1]*aa[j-1] if j else 0))
            need(actual==expected,'General multistage recurrence at a non-involutive Q')
            cases+=1
        values={s:s+2 for s in stages}
        for cut in range(p):
            masks=M.canonical_masks(p,cut)
            assignment=[(i,tuple(s for s,mask in zip(stages,masks)
                               if s in available and mask>>i&1)) for i,available in slots]
            actual=M.evaluate(p,events,assignment,values)
            g=[math_product(values[s] for s,mask in zip(stages,masks) if mask>>i&1) for i in range(p)]
            l=[[int(i==k)+((-1)**(k-i) if i<k<=cut else 0) for k in range(p)] for i in range(p)]
            li=[[int(i==k)+int(k==i+1 and k<=cut) for k in range(p)] for i in range(p)]
            diagonal=[[g[i]*int(i==k) for k in range(p)] for i in range(p)]
            block=M.multiply(M.multiply(l,diagonal),li)
            want=[[block[i//2][k//2] if i%2==k%2==0 else block[k//2][i//2]
                   if i%2==k%2==1 else 0 for k in range(2*p)] for i in range(2*p)]
            need(actual==want,'Canonical cut has exact constant scalar normalizers')
            canonical+=1
    return {'multistage_recurrences':cases,'non_involutive_q':'2','canonical_cut_boundaries':canonical}


def math_product(xs):
    out=1
    for x in xs:out*=x
    return out


def cap_difference(old,new):
    ot,op=old;nt,np=new
    signed=Counter(nt)
    signed.subtract(np);signed.subtract(ot);signed.update(op)
    need(sum(r*m for r,m in signed.items())==0,'Deletion preserves total rank surplus')
    for k in range(1,max(signed,default=0)+1):
        need(sum(m*min(r,k) for r,m in signed.items())>=0,
             'Capped-rank dominance for every discrete concave price')


def domination_checks():
    families=0;removed=0;by_p={}
    for p in range(1,5):
        stages=M.thick(p)
        choices=[[s for s in range(1<<p) if s>>M.vertex(p,j)&1] for j in stages]
        cases=0
        for masks in itertools.product(*choices):
            intervals=[M.core(p,M.vertex(p,j),s) for j,s in zip(stages,masks)]
            lo=max(a for a,b in intervals);hi=min(b for a,b in intervals)
            if lo>hi:continue
            reduced=M.canonical_masks(p,lo)
            need(all(a&b==a for a,b in zip(reduced,masks)),'Cut only deletes idle factors')
            cap_difference(M.family_invoice(p,masks),M.family_invoice(p,reduced))
            removed+=sum((a^b).bit_count() for a,b in zip(masks,reduced))
            families+=1;cases+=1
        by_p[str(p)]=cases
    balanced_cases=0
    for p in range(1,33):
        best=M.family_invoice(p,M.canonical_masks(p,(p-1)//2))
        for cut in range(p):
            cap_difference(M.family_invoice(p,M.canonical_masks(p,cut)),best)
            balanced_cases+=1
    x=json.loads((ROOT/'research/joint-helper-lattice/RESULT.json').read_text())
    h={int(r):m for r,m in x['local_helpers'].items()}
    local={int(r):m for r,m in x['local_paid'].items()}
    t,paid=M.family_invoice(16,M.canonical_masks(16,7),helpers=h,paid_local=local)
    need(dict(t)=={int(r):m for r,m in x['targets'].items()},'Every selected target is priced')
    need(dict(paid)=={int(r):m for r,m in x['paid'].items()},'Every selected paid job is priced')
    need(sum(r*m for r,m in t.items())-sum(r*m for r,m in paid.items())==752,
         'Positive selected rank surplus')
    bit=json.loads((ROOT/'research/query-thinned-controllers/BIT-CONTROLLER.json').read_text())['invoice']
    bt,bp=M.family_invoice(16,M.canonical_masks(16,7),block=7,ports=111,helpers={8:439},
                          paid_local={1:1323,2:1342,3:79,4:44,5:102,6:11,7:19})
    need(dict(bt)=={int(r):m for r,m in bit['targets'].items()},'Full BIT target invoice')
    need(dict(bp)=={int(r):m for r,m in bit['paid'].items()},'Full BIT paid invoice')
    need(min(17,9)-min(16,9) < min(9,9)-min(8,9),
         'A direction-reversed concavity claim is rejected')
    return {'compatible_families':families,'by_pairs':by_p,'deleted_stage_factors':removed,
            'balanced_cut_comparisons':balanced_cases,
            'all_capped_rank_prices':True,'selected_p16_calls':sum(paid.values()),
            'selected_p16_targets':sum(t.values()),'selected_p16_surplus':752,
            'bit_p16_targets':sum(bt.values()),'bit_p16_calls':sum(bp.values()),
            'selected_full_native_and_outer_replay':False}


def run():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for r in pins['files']:
        if r['usage']=='input':
            need(sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],
                 'Authenticated live source '+r['path'])
    return {'status':'PASS_PARTIAL_IDLE_CUT_NORMAL_FORM_FINITE_CONTROLS',
            'theorem_scope':'All-p written necessity and concave-price domination; no new kappa',
            'projection':projection_checks(),'binary_source':binary_source_checks(),
            'commutators':commutator_checks(),
            'endpoint':endpoint_checks(),'dominance':domination_checks()}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=run();path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads(path.read_text()),'Fresh receipt equals committed result')
    print(json.dumps(result,sort_keys=True))
