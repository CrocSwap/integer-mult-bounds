"""Bind PR117's actual routing/scalars to its DAG, then replay audited frame code."""
from pathlib import Path
from collections import Counter
from itertools import combinations
import gzip,hashlib,importlib.util,json,random,time

HERE=Path(__file__).resolve().parent;ROOT=HERE/'pr117-public/tree'
def load(name):return json.loads(gzip.decompress((ROOT/'certificates'/name).read_bytes()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=time.time()
dag=load('deferred-product-complex-dag.json.gz')
raw=load('deferred-product-complex-word.json.gz')
cfpath=ROOT/'scripts/deferred_product/complex_frames.py'
spec=importlib.util.spec_from_file_location('reviewed_pr117_frames',cfpath)
cf=importlib.util.module_from_spec(spec);spec.loader.exec_module(cf)
cf.ALLOW_ALTERNATING=True
w=cf.Word(raw);h=w.h;v=w.v;R=w.R
assert (h,v,R)==(24,2024,28705)
flat=dag['args'];assert len(raw['args'])==v+1+len(flat)//2
for k in range(len(flat)//2):assert raw['args'][v+1+k]==flat[2*k:2*k+2]
trip=list(combinations(range(h),3))
expected=Counter((T,n,1) for T,n in zip(trip,dag['D']))
stars=[(a,b,i) for a,b in combinations(range(h),2) for i in range(h) if i not in (a,b)]
expected.update((tuple(sorted(S)),n,-1) for S,n in zip(stars,dag['P']))
assert Counter(w.pieces)==expected
assert Counter((name,n,i) for name,n,i in raw['retained'])==Counter(
    ('A_'+str(i),n,i) for i,n in enumerate(dag['A']))
assert len(w.gates)==len(w.nodes)
assert sorted(n for n,_,_ in w.gates)==sorted(w.nodes)
assert len(w.src)==v and len(set(w.src.values()))==v
assert set(w.pout)==set(range(len(w.pieces)))
assert set(w.rout)=={('A_'+str(i),) for i in range(h)}
assert len(set(w.rout.values()))==h
point=[sum(1<<j for j,T in enumerate(trip) if i in T) for i in range(h)]
full=(1<<v)-1
for T,n in zip(trip,dag['D']):
    assert w.nodes[n]['sup']==full&~(point[T[0]]|point[T[1]]|point[T[2]])
for (a,b,i),n in zip(stars,dag['P']):assert w.nodes[n]['sup']==point[a]&point[b]&~point[i]
for i,n in enumerate(dag['A']):assert w.nodes[n]['sup']==full&~point[i]
assert [j-1+(j==0)-(j==2) for j in range(4)]==[0,0,0,2]

# Exact fresh source transfer through every physical carrier gate. Supports
# are integer bit vectors because every source contribution at a DAG gate is1.
fresh=[0]*R
for T,slot in w.src.items():fresh[slot]=1<<w.tid[T]
for n,ins,outs in w.gates:
    assert outs and outs[0]==ins[0]
    assert len(set(ins))==len(ins) and len(set(outs))==len(outs)
    assert all(0<=slot<R for slot in ins+outs)
    args=w.nodes[n]['args']
    if args:
        assert len(ins)==2
        assert Counter(fresh[s] for s in ins)==Counter(w.nodes[a]['sup'] for a in args)
        assert not fresh[ins[0]]&fresh[ins[1]]
        fresh[ins[0]]|=fresh[ins[1]]
    else:assert len(ins)==1 and fresh[ins[0]]==w.nodes[n]['sup']
    for s in outs[1:]:
        assert fresh[s]==0
        fresh[s]=fresh[outs[0]]
    assert all(fresh[s]==w.nodes[n]['sup'] for s in outs)
for i,(_,n,_) in enumerate(w.pieces):assert fresh[w.pout[i]]==w.nodes[n]['sup']
for i,n in enumerate(dag['A']):assert fresh[w.rout[('A_'+str(i),)]]==w.nodes[n]['sup']
print('PASS exact actual carrier routing and every target/center coefficient',flush=True)

# Literal signed integer replay. y stores42 times the actual target; every
# scalar update is exact. Algebraically the same word is old-read subtraction,
# V insertion, new-read addition and exact inverse cleanup.
def mix(a,inverse):
    for n,ins,outs in (reversed(w.gates) if inverse else w.gates):
        if inverse:
            for s in reversed(outs[1:]):a[s]-=a[outs[0]]
            if len(ins)==2:a[ins[0]]-=a[ins[1]]
        else:
            if len(ins)==2:a[ins[0]]+=a[ins[1]]
            for s in outs[1:]:a[s]+=a[outs[0]]
def scatter(a,y,sgn):
    av=[a[w.rout[('A_'+str(i),)]] for i in range(h)]
    total=2*sum(av)
    for j,T in enumerate(trip):y[j]+=sgn*(total-21*sum(av[i] for i in T))
    for i,(T,n,c) in enumerate(w.pieces):y[w.tid[T]]+=sgn*21*c*a[w.pout[i]]
def inject(a,x,sgn):
    for T,s in w.src.items():a[s]+=sgn*x[w.tid[T]]
rng=random.Random(117)
for trial in range(4):
    x=[rng.randrange(-10**12,10**12) for _ in range(v)]
    old=[rng.randrange(-10**12,10**12) for _ in range(R)]
    y0=[rng.randrange(-10**12,10**12) for _ in range(v)]
    for sign in (1,-1):
        a=old[:];y=[42*z for z in y0]
        if sign==1:
            mix(a,False);scatter(a,y,-1);mix(a,True)
            inject(a,x,1);mix(a,False);scatter(a,y,1);mix(a,True);inject(a,x,-1)
        else: # literal reverse word with every scalar gate inverted
            inject(a,x,1);mix(a,False);scatter(a,y,-1);mix(a,True)
            inject(a,x,-1);mix(a,False);scatter(a,y,1);mix(a,True)
        assert a==old and y==[42*(u+sign*z) for u,z in zip(y0,x)]
print('PASS eight signed arbitrary-dirty exact integer replay cases',flush=True)

alternating={};old_check=cf.residual_ok
def checked(Rb):
    ok=old_check(Rb)
    if Rb and cf.nondegenerate(Rb) and not any(x.bit_count()&1 for x in cf.vecs(Rb)):
        basis=cf.vecs(Rb);assert len(basis)==2
        values=[0,basis[0],basis[1],basis[0]^basis[1]]
        weights=[x.bit_count()%4 for x in values]
        assert all(q in (0,2) for q in weights)
        S=sum(1 if q==0 else -1 for q in weights)
        assert S in (-2,2)
        alternating[tuple(basis)]=dict(weights=weights,gauss_sum=S)
    return ok
cf.residual_ok=checked
events,initial,final,bad,ok=cf.forward(w)
breaks,end=cf.reflect(w,events,initial,final)
paid,cls=cf.paid_histogram(w,events)
assert not bad and ok and breaks==0 and end
assert dict(paid)=={int(r):n for r,n in raw['child_list']['rows'].items()}
assert cls['aux']==R*h and cls['data']==2*v*(h-1) and cls['center']==h*(h-1)

# An outer exterior is attached after this whole inner forward word, where
# every original auxiliary is already at its FULL active-factor frame.
assert final[2*v:]==[w.FULL]*R
assert initial[2*v:]==[w.ZERO]*R
out=dict(status='PASS exact routing/scalar binding, signed dirty replay, full frame ledger and alternating phases',
    commit='cbb05ce504d571546d9b7794c186a613c659c3bf',R=R,
    dag_sha256=sha(ROOT/'certificates/deferred-product-complex-dag.json.gz'),
    word_sha256=sha(ROOT/'certificates/deferred-product-complex-word.json.gz'),frame_checker_sha256=sha(cfpath),
    every_carrier_fresh_support_exact=True,every_piece_target_coefficient_exact=True,all_centers_exact=True,
    all_source_scalar_identity_exact=True,literal_forward_and_inverse_signed_words=True,
    signed_dirty_trials=8,all_signed_dirty_trials_pass=True,events=len(events),moves=sum(e[0]=='move' for e in events),
    frame_violations=len(bad),stage_two_breaks=breaks,stage_two_endpoints_ok=end,
    every_auxiliary_source_zero_frame=True,every_auxiliary_pre_exterior_full_frame=True,
    histogram_matches_word=True,alternating_checked_occurrences=dict(cf.ALTERNATING),
    distinct_alternating_planes=len(alternating),all_actual_alternating_Gauss_sums_valid=True,
    alternating_gauss_sign_counts=dict(Counter(r['gauss_sum'] for r in alternating.values())),
    elapsed_seconds=time.time()-start,
    scope='All-source fresh support transfer is exact; arbitrary-dirty identity follows the inverse-word proof, with eight finite signed cases as checks')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2),flush=True)
