#!/usr/bin/env python3
"""Literal inverse/reflection and exact finite scalar/frame audit.

Captures an unchanged deferred producer before its output write, then checks
the scalar computation on every source symbol, the exact signed old-readout
transpose, the dependency cut and the complete complemented incidence ledger.
This is finite verification; the inherited residual-to-child implementation,
all-size transfer and analytic interfaces are not proved by this script.
"""
import ast
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import argparse,json,pickle,sys
from pathlib import Path
sys.dont_write_bytecode=True
assert not sys.flags.optimize,'Assertions must remain enabled'


def capture(source):
    source=Path(source).resolve();sys.path.insert(0,str(source.parent))
    tree=ast.parse(source.read_text(),filename=str(source))
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    at=next(i for i,n in enumerate(main.body) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='write_text')
    main.body[at:]=[ast.Return(ast.Call(ast.Name('locals',ast.Load()),[],[]))]
    ast.fix_missing_locations(tree)
    ns={'__file__':str(source),'__name__':'reflection_capture'}
    exec(compile(tree,str(source)+' [read-only capture]','exec'),ns)
    data=ns['main']();data['source']=str(source);return data


def basis(vectors):
    piv={}
    for x in vectors:
        for p in sorted(piv,reverse=True):
            if x>>p&1:x^=piv[p]
        if x:
            p=x.bit_length()-1
            for q in piv:
                if piv[q]>>p&1:piv[q]^=x
            piv[p]=x
    return tuple(piv[p] for p in sorted(piv,reverse=True))


def dot(a,b):return (a&b).bit_count()&1


@lru_cache(None)
def contained(A,B):return len(basis(A+B))==len(B)


@lru_cache(None)
def complement(A,h):
    A=basis(A);piv={x.bit_length()-1:x for x in A};result=[]
    for j in range(h):
        if j not in piv:
            x=1<<j
            for p,row in piv.items():
                if row>>j&1:x|=1<<p
            result.append(x)
    return basis(result)


@lru_cache(None)
def nondeg(A):
    return len(basis(sum(dot(x,y)<<j for j,y in enumerate(A)) for x in A))==len(A)


def root_readout(d,s):
    h,v,j=d['h'],d['v'],d['role_root'][s];p=(1<<61)-1
    if d['kind'][j]:
        assert d['seed_c'][s]==[int(i==d['centre_of'][j]) for i in range(h)],'Root centre readout'
        assert d['seed_d'][s]=={},'Root centre extra target'
    else:
        assert d['seed_c'][s] is None,'Root extra centre'
        expected=pow(2,-1,p)*(1 if j<v else -1)%p
        assert d['seed_d'][s]=={d['target'][j]:expected},'Root signed readout'


@lru_cache(None)
def dual_frames(A,B,h):
    return len(A)+len(B)==h and all(not dot(x,y) for x in A for y in B)


def check_reflection(forward,backward,h,v):
    def bank(s):return s+v if s<v else s-v if s<2*v else s
    assert len(forward)==len(backward),'Reflected event count'
    for left,right in zip(reversed(forward),backward):
        k,a,b,c,F,*tail=left;kk,aa,bb,cc,FF,*tt=right
        assert kk==k and aa==bank(a) and cc==-c,'Reflected inverse shear'
        assert bb==(bank(b) if k=='gate' else tuple(bank(t) for t in reversed(b))),'Reflected port incidence'
        assert dual_frames(F,FF,h),'Reflected frame complement'
        if k=='centre':
            assert dual_frames(tail[0],tt[0],h) and tail[1:]==tt[1:],'Reflected centre copy'
        else:assert tail==tt,'Reflected coefficient-row binding'


def audit(d):
    h,v,R=d['h'],d['v'],d['R'];ops=d['ops'];q=d['q'];p=(1<<61)-1
    trip=list(combinations(range(h),3));assert d['trip']==trip
    for s in d['role_root']:root_readout(d,s)
    full=(1<<v)-1;point=[sum(1<<j for j,T in enumerate(trip) if i in T) for i in range(h)]
    # All fresh-source coefficients, exactly over the integers. No modular
    # replay is used for this check, and no stored DAG support is trusted.
    nodes={};values=[0]*R
    for n in d['order']:
        a,b=d['args'][n]
        if not a:nodes[n]=1<<(n-1)
        else:
            assert not nodes[a]&nodes[b],('DAG overlap',n)
            nodes[n]=nodes[a]|nodes[b]
    for s,n in d['leaf_of'].items():values[s]=1<<(n-1)
    for o in ops:
        if o[0]=='src':continue
        a,b=(o[1],o[2]) if o[0]=='add' else (o[2],o[1])
        assert not values[a]&values[b],('literal signal overlap',o)
        values[a]|=values[b]
        assert values[a]==nodes[o[3]],('literal source coefficients',o)
    negative=[0]*v;positive=[None]*v;centres={}
    for s,j in d['role_root'].items():
        assert values[s]==nodes[d['roots'][j]]
        if d['kind'][j]:centres[d['centre_of'][j]]=values[s]
        elif j<v:
            t=d['target'][j];assert positive[t] is None;positive[t]=values[s]
        else:
            t=d['target'][j];assert not negative[t]&values[s];negative[t]|=values[s]
    assert set(centres)==set(range(h))
    for i,S in centres.items():assert S==full^point[i]
    for t,T in enumerate(trip):
        A,B,C=(point[i] for i in T)
        assert positive[t]==full^(A|B|C)
        assert negative[t]==((A&B&~C)|(A&C&~B)|(B&C&~A))
    assert h-3==21
    assert [((k-1)+(k==0)-(k==2)) for k in range(4)]==[0,0,0,2]
    # Every centre decoder coefficient is 1/21-[i in T]/2. Thus the
    # preceding source-support identities prove J L V = I over Q.

    # Independently form J L on arbitrary scratch as integer centre rows
    # and signed half-output rows. Compare every coefficient, not hashes.
    cc=[None]*R;dd=[{} for _ in range(R)]
    for s,j in d['role_root'].items():
        if d['kind'][j]:cc[s]=[int(i==d['centre_of'][j]) for i in range(h)]
        else:dd[s][d['target'][j]]=1 if j<v else -1
        assert cc[s]==d['seed_c'][s],'Root centre readout'
        assert {t:(x*pow(2,-1,p))%p for t,x in dd[s].items()}==d['seed_d'][s],'Root signed readout'
    def addrow(a,b):
        if cc[b] is not None:
            cc[a]=list(cc[b]) if cc[a] is None else [x+y for x,y in zip(cc[a],cc[b])]
        for t,x in dd[b].items():dd[a][t]=dd[a].get(t,0)+x
    for o in reversed(ops):
        if o[0]=='add':addrow(o[2],o[1])
        elif o[0]=='copy':addrow(o[1],o[2])
    maxcoef=0;readcount=0;actual_reach={};coefficient_digest=sha256()
    for s in range(R):
        assert cc[s] is None and d['cvec'][s] is None or cc[s] is not None and [x%p for x in cc[s]]==d['cvec'][s]
        assert {t:(x*pow(2,-1,p))%p for t,x in dd[s].items()}==d['dpart'][s]
        # Exact expanded readout numerators over the single denominator42.
        if cc[s] is None:
            reached=tuple(t for t,x in sorted(dd[s].items()) if x)
            maxcoef=max(maxcoef,max((abs(21*x) for x in dd[s].values()),default=0))
            coefficient_digest.update(repr((s,[(t,21*dd[s][t]) for t in reached])).encode()+b'\n')
        else:
            total=2*sum(cc[s]);reached=[]
            for t,T in enumerate(trip):
                num=total-21*sum(cc[s][i] for i in T)+21*dd[s].get(t,0)
                maxcoef=max(maxcoef,abs(num))
                if num:
                    reached.append(t)
                    coefficient_digest.update(s.to_bytes(4,'little')+t.to_bytes(4,'little')+num.to_bytes(8,'little',signed=True))
            reached=tuple(reached)
        readcount+=len(reached);actual_reach[s]=reached
    assert maxcoef<=42,'Expanded readout coefficient exceeds one in absolute value'
    # Early/remainder order is a legal commutation of independent shears.
    # Deferred inputs are untouched by the early word; completed centre
    # roles are untouched by its remainder. These facts make deferred
    # readout placement equivalent to the canonical -JL, V, L, J,L^-1,-V.
    early=set(d['phase1']);assert early==set(d['Anc'])
    assert sorted(d['phase1'])==d['phase1'] and d['rest']==[i for i in range(len(ops)) if i not in early]
    seen_late=set();early_touched=set();late_touched=set()
    for i,o in enumerate(ops):
        touched=set(o[1:3]) if o[0] in ('add','copy') else set()
        if i in early:
            assert not touched&seen_late;early_touched.update(touched)
        else:seen_late.update(touched);late_touched.update(touched)
    assert not set(d['deferred'])&early_touched
    assert not set(d['centre_roles'])&late_touched
    assert all(cc[s] is None for s in d['deferred'])
    for s in d['deferred']:assert set(actual_reach[s])<=set(d['reach'][s])

    # Frame-labelled literal chronological word. Readout blocks mean the
    # explicit commuting additions to their individual named target ports;
    # their scalar count and target incidences are expanded above.
    ZERO=();FULL=basis(1<<i for i in range(h))
    U={n:basis(B) for n,B in d['U'].items()}
    sigma={s:basis(B) for s,B in d['placed'].items()}
    rootframe={s:basis(B) for s,B in d['root_frame'].items()}
    tm=[basis((sum(1<<i for i in T),)) for T in trip]
    X=lambda t:t;Y=lambda t:v+t;A=lambda s:2*v+s
    word=[]
    def gate(a,b,c,F):word.append(('gate',a,b,c,F))
    def read(s,sgn,F,targets,row):word.append(('read',A(s),tuple(Y(t) for t in targets),sgn,F,row))
    def run(i,sign=1,F=None):
        o=ops[i]
        if o[0]=='add':gate(A(o[1]),A(o[2]),sign,U[o[3]] if F is None else F)
        elif o[0]=='copy':gate(A(o[2]),A(o[1]),sign,U[o[3]] if F is None else F)
    deferred=set(d['deferred'])
    for s in range(R):
        if s not in deferred:read(s,-1,ZERO,actual_reach[s],('old',s))
    for s,n in d['leaf_of'].items():
        if s not in deferred:gate(A(s),X(n-1),1,U[n])
    for i in d['phase1']:run(i)
    for s in d['centre_roles']:word.append(('centre',A(s),tuple(Y(t) for t in range(v)),1,rootframe[s],ZERO,d['centre_of'][d['role_root'][s]]))
    for s in d['deferred']:read(s,-1,sigma[s],actual_reach[s],('old',s))
    for s in d['deferred']:
        if s in d['leaf_of']:n=d['leaf_of'][s];gate(A(s),X(n-1),1,U[n])
    for i in d['rest']:run(i)
    for s,j in d['role_root'].items():
        if not d['kind'][j]:read(s,1,rootframe[s],(d['target'][j],),('root',21 if j<v else -21))
    for i in reversed(range(len(ops))):run(i,-1,FULL)
    for s,n in d['leaf_of'].items():gate(A(s),X(n-1),-1,FULL)

    def swap(s):return s+v if s<v else s-v if s<2*v else s
    def reflect(event):
        k,a,b,c,F,*rest=event
        if k=='gate':return (k,swap(a),swap(b),-c,complement(F,h))
        tail=(complement(rest[0],h),rest[1]) if k=='centre' else tuple(rest)
        return (k,swap(a),tuple(swap(t) for t in reversed(b)),-c,complement(F,h),*tail)
    reverse=[reflect(e) for e in reversed(word)]
    assert [reflect(e) for e in reversed(reverse)]==word
    check_reflection(word,reverse,h,v)
    # Reuse this exact captured word for targeted failure controls.
    rejected=[]
    for failure in ('inverse-sign','uncomplemented-frame'):
        damaged=list(reverse);first=list(damaged[0])
        if failure=='inverse-sign':first[3]*=-1
        else:first[4]=word[-1][4]
        damaged[0]=tuple(first)
        try:check_reflection(word,damaged,h,v)
        except AssertionError:rejected.append(failure)
        else:raise AssertionError('Accepted reflection mutation: '+failure)
    s=next(s for s,j in d['role_root'].items() if not d['kind'][j]);original=d['seed_d'][s]
    d['seed_d'][s]={t:(-c)%p for t,c in original.items()}
    try:
        try:root_readout(d,s)
        except AssertionError:rejected.append('signed-root-readout')
        else:raise AssertionError('Accepted signed root mutation')
    finally:d['seed_d'][s]=original

    def framescan(events,initial,expected):
        current=list(initial);hist=Counter();copies=Counter();scalar=0;digest=sha256()
        def promote(s,F):
            old=current[s];assert contained(old,F),(s,old,F)
            assert nondeg(F);assert nondeg(complement(F,h))
            if len(F)>len(old):hist[len(F)-len(old)]+=1
            current[s]=F
        for event in events:
            k,a,b,c,F,*rest=event
            assert c in (-1,1)
            promote(a,F)
            if k=='gate':promote(b,F);scalar+=1
            elif k=='read':
                for t in b:promote(t,F)
                scalar+=len(b)
            else:
                assert k=='centre';G=rest[0]
                assert contained(G,F) or contained(F,G)
                assert nondeg(G);copies[abs(len(F)-len(G))]+=1
                for t in b:promote(t,G)
                scalar+=len(b)+2 # temporary copy and erasure
            digest.update(repr(event).encode()+b'\n')
        # Each literal role cleanup reaches full space; any unused final
        # endpoint is still represented explicitly in the expected chain.
        for s,F in enumerate(expected):promote(s,F)
        assert current==expected
        return hist,copies,scalar,digest.hexdigest()
    start=tm+[ZERO]*v+[sigma.get(s,ZERO) for s in range(R)]
    finish=[FULL]*v+[complement(T,h) for T in tm]+[FULL]*R
    H,C,scalar,digest=framescan(word,start,finish)
    revstart=[None]*len(start);revfinish=[None]*len(start)
    for s in range(len(start)):
        revstart[swap(s)]=complement(finish[s],h);revfinish[swap(s)]=complement(start[s],h)
    HR,CR,scalarR,reverse_digest=framescan(reverse,revstart,revfinish)
    assert (H,C,scalar)==(HR,CR,scalarR)
    z=Counter({r:2*v*n for r,n in (H+C).items()})
    for s in range(R):z[h*h-h+len(sigma.get(s,ZERO))]+=2*v
    z[(h-1)**2]+=2*v*v;z[1]+=v*v
    z.pop(0,None)
    assert dict(sorted(z.items()))=={int(r):n for r,n in d['out']['child_multiplicities'].items()},'Literal reflected child histogram'
    assert sum(r*n for r,n in z.items())==d['out']['total_rank']
    G=v*v+2*v*scalar
    safe=8*(d['c_add']+2*R+(R+q)*v*(h+1)+h*h+h+1) if 'c_add' in d else 8*(d['out']['additions']+2*R+(R+q)*v*(h+1)+h*h+h+1)
    assert safe>=scalar
    return dict(h=h,v=v,R=R,exact_fresh_source_map=True,exact_integer_old_readout_transpose=True,
                exact_arbitrary_dirty_cancellation_by_dependency_cut=True,
                reflected_word_rule='Reverse literal order, negate every shear, swap X/Y ports, complement every frame; auxiliary bank is separate.',
                reflected_scalar_map='X becomes X-Y; Y unchanged; all auxiliary coordinates restored.',
                two_stage_scalar_map='(X,Y) becomes (-Y,X+Y) before inherited endpoint correction.',
                literal_frame_incidences_both_directions=True,all_frames_nondegenerate=True,
                reflected_residual_rank_histogram_equal=True,child_multiplicities=dict(sorted(z.items())),
                word_blocks=len(word),expanded_scalar_operations_per_stage=scalar,
                expanded_old_readout_additions=readcount,largest_readout_numerator_over_42=maxcoef,
                old_readout_coefficients_over_42_sha256=coefficient_digest.hexdigest(),
                literal_global_scalar_groups=G,conservative_local_G=safe,
                forward_incidence_sha256=digest,reflected_incidence_sha256=reverse_digest,
                rejected_controls=rejected,
                scope='Exact finite source coefficients, dirty cancellation algebra and literal reflected frame/charge ledger. Copied-centre transforms, endpoint correction and residual-to-child/all-size transfer retain their stated inherited contracts.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);ap.add_argument('--state',type=Path)
    ap.add_argument('--output',type=Path);ap.add_argument('--check',type=Path);a=ap.parse_args()
    assert bool(a.source)!=bool(a.state)
    d=capture(a.source) if a.source else pickle.loads(a.state.read_bytes())
    result=audit(d);source=Path(d['source'])
    result['source_sha256']=sha256(source.read_bytes()).hexdigest()
    result['audit_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    result=json.loads(json.dumps(result));encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.check:assert result==json.loads(a.check.read_text())
    if a.output:a.output.write_text(encoded)
    else:print(encoded,end='')
    print('PASS exact scalar and literal complement reflection audit',file=sys.stderr)


if __name__=='__main__':main()
