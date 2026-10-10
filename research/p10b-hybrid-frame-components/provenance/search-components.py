"""Fixed-endpoint, exact paid-histogram simulated annealing.

PR340 method credit: Rohan Arun, Anthropic Claude assistance, pinned head
695e703731491f81aa22d51b2def850afd7519c0. Its discovery script was not supplied.
This independent implementation uses PR320's exact frame primitives and frozen
W3 greedy assignment, then permits uphill/neutral moves and depth-two closure.
OpenAI Codex assistance; inherited Apache-2.0 credits retained.
"""
import sys, pathlib, json, random, math, time, hashlib, pickle
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
INPUT=pathlib.Path('/private/tmp/p10b-hybrid023-w3-fresh-20261010/joint-final/final/data.pkl')
SEED=ROOT/'transfer-combined-selection.json'
REF=pathlib.Path('/private/tmp/p10-crossgroup-t300-v3/vendor/pr320/discovery/descent2_search.py')
seednum=int(sys.argv[1]) if len(sys.argv)>1 else 340
seconds=int(sys.argv[2]) if len(sys.argv)>2 else 600
sys.argv=[str(REF),str(INPUT),str(ROOT/'unused.json'),'0']
source=REF.read_text();prefix=source[:source.index('for it in range(PASSES):')]
saved_file=__file__;__file__=str(REF)
exec(compile(prefix,str(REF),'exec'),globals())
__file__=saved_file
assert hashlib.sha256(D['records']).hexdigest()=='a9965c931289d5afcab3c128b349cc2510369ad1bfce246a4c86b3858bb615f6'
original_ids=set(B)
seed=json.loads(SEED.read_text())
assert seed['input_raw_sha256']==hashlib.sha256(D['records']).hexdigest()
for entry in seed['entries']:
    setframe(entry['record'],register(entry['new_basis']))
seedH=hist();seedL=sum(LN[d]*c for d,c in seedH.items())
# Reuse only upstream frame bases as candidate spaces, never gate indices.
pr=json.loads((ROOT/'pr340-695e-selection.json').read_text())
for entry in pr['entries']:register(entry['new_basis'])
upstream_frames={register(e['new_basis']) for e in pr['entries']}
registered=sorted(B)
bydim=defaultdict(list)
for f in registered:bydim[dimf[f]].append(f)
# Sparse exact integer products make rejection of unrelated global frames cheap.
sparse={}
def sparsify(rows):return tuple(tuple((j,x) for j,x in enumerate(row) if x) for row in rows)
def sp(f):
    if f not in sparse:sparse[f]=(sparsify(B[f]),sparsify(A[f]))
    return sparse[f]
cc.clear()
def sub(f1,f2):
    if f1==f2:return True
    key=(f1,f2)
    if key in cc:return cc[key]
    if dimf[f1]>dimf[f2]:r=False
    else:
        b,a=sp(f1)[0],A[f2]
        r=all(sum(x*row[j] for j,x in br)==0 for row in a for br in b)
    cc[key]=r;return r
# Exact signed source support is independent of the evolving frame assignment.
columns=[{i:1} if i<v else {} for i in range(n)];center=None;needs={}
for k in range(N):
    op,a,b,c,f,z=old[6*k:6*k+6]
    if op==0:continue
    if op==2:center=a;continue
    if op==3:center=None;continue
    source=center if b==n else b;ca=columns[a]
    for s,x in columns[source].items():
        y=ca.get(s,0)+c*x
        if y:ca[s]=y
        else:del ca[s]
    if k in fixed:continue
    need=set()
    if not(v<=a<2*v):need.update(ca)
    if not(v<=b<2*v) and b!=n:need.update(columns[b])
    needs[k]=frozenset(need)
del columns
print('seed',len(selected),'phi',seedL-L0,'needs',len(needs),'%.1fs'%(time.time()-t0),flush=True)
interval_cache={};candidate_cache={};stats=Counter();rng=random.Random(seednum)
def candidates(k):
    slots=gate_slots[k];prev=tuple(prevf(r,p) for r,p in slots);nxt=tuple(nextf(r,p) for r,p in slots)
    key=(prev,nxt,needs[k])
    if key in candidate_cache:return candidate_cache[key]
    if max(dimf[f] for f in prev)==min(dimf[f] for f in nxt):
        result=(gate_frame[k],);candidate_cache[key]=result;return result
    J=join(prev);M=meet(nxt)
    if not sub(J,M):raise AssertionError(('interval',k))
    J=join([J,spanframe(needs[k])])
    if not sub(J,M):raise AssertionError(('span interval',k))
    ik=(J,M,prev,nxt)
    if ik not in interval_cache:
        pool={J,M,gate_frame[k]}
        for r,p in slots:
            pool.update(chain[r]);pool.add(initial[r]);pool.add(final[r])
        pool.update(upstream_frames)
        pool={f for f in pool if sub(J,f) and sub(f,M)}
        local={J,M,gate_frame[k],*prev,*nxt}
        for depth in range(2):
            current=sorted(local)
            if len(current)>16:current=sorted({J,M,gate_frame[k],*prev,*nxt})
            additions=set()
            for i,a in enumerate(current):
                for b in current[:i]:
                    additions.add(join([a,b]));additions.add(meet([a,b]))
            local.update(additions)
        pool.update(f for f in local if sub(J,f) and sub(f,M))
        interval_cache[ik]=tuple(sorted(pool))
    result=interval_cache[ik];assert gate_frame[k] in result or all(sub(J,gate_frame[k]) and sub(gate_frame[k],M) for _ in [0])
    if gate_frame[k] not in result:result=(*result,gate_frame[k])
    candidate_cache[key]=result
    return result
def variable(k):
    slots=gate_slots[k]
    return max(dimf[prevf(r,p)] for r,p in slots)<min(dimf[nextf(r,p)] for r,p in slots)
active=[k for k in gates if k not in fixed and k>=275000 and variable(k)]
print('initial active',len(active),flush=True)
best=dict(selected);bestL=seedL;curL=seedL;start=time.monotonic();last=start;epoch=0
def restore(assignment):
    for k in list(selected):setframe(k,old[6*k+4])
    for k,g in assignment.items():setframe(k,g)
def snapshot(label):
    H=hist();L=sum(LN[d]*c for d,c in H.items());delta=Counter(H);delta.subtract(H0)
    entries=[]
    for k in sorted(selected):
        op,a,b,c,f,z=old[6*k:6*k+6];g=selected[k]
        if sub(f,g) and sub(g,f):continue
        entries.append(dict(record=k,scalar=[a,b,c,z],category=D['cats'][z],old_dimension=dimf[f],old_basis_sha256=hashlib.sha256(json.dumps([list(r) for r in B[f]],separators=(',',':')).encode()).hexdigest(),new_basis=[list(map(int,r)) for r in B[g]],new_dimension=dimf[g],constructed=g not in original_ids))
    result=dict(source_record_count=N,selected_gate_count=len(entries),local_delta={str(d):c for d,c in sorted(delta.items()) if c},removed_calls=sum(H0.values())-sum(H.values()),dL_local=L-L0,moves=dict(stats),new_frames=len({e['new_basis'].__repr__() for e in entries if e['constructed']}),entries=entries,seed_phi_delta=seedL-L0,search_seed=seednum,elapsed=time.monotonic()-start)
    path=ROOT/('component-search-'+str(seednum)+'-'+label+'.json');path.write_text(json.dumps(result,indent=1)+'\n')
    print('snapshot',label,len(entries),'delta',result['local_delta'],'phi',result['dL_local'],'extra',L-seedL,flush=True)
def harvest_components():
    global best,bestL
    dirty={k for k in set(selected)|set(best) if gate_frame[k]!=best.get(k,old[6*k+4])}
    parent={k:k for k in dirty}
    def root(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    for k in dirty:
        for r,p in gate_slots[k]:
            for q in (p-1,p+1):
                if 0<=q<len(owner[r]) and owner[r][q] in dirty:
                    a,b=root(k),root(owner[r][q]);parent[a]=b
    groups=defaultdict(list)
    for k in dirty:groups[root(k)].append(k)
    improve=0
    def oldfr(r,p):
        if p<0:return initial[r]
        if p>=len(chain[r]):return final[r]
        k=owner[r][p]
        return chain[r][p] if k not in dirty else best.get(k,old[6*k+4])
    def nowfr(r,p):return initial[r] if p<0 else final[r] if p>=len(chain[r]) else chain[r][p]
    accepted=[]
    for ks in groups.values():
        edges={(r,q,q+1) for k in ks for r,p in gate_slots[k] for q in (p-1,p)}
        change=sum(cost(nowfr(r,p),nowfr(r,q))-cost(oldfr(r,p),oldfr(r,q)) for r,p,q in edges)
        if change<-1e-9:accepted.append((ks,change))
    for ks,change in accepted:
        for k in ks:
            if gate_frame[k]==old[6*k+4]:best.pop(k,None)
            else:best[k]=gate_frame[k]
        bestL+=change;improve+=change;stats['improving_components']+=1
    return improve
while time.monotonic()-start<seconds:
    epoch+=1;elapsed=time.monotonic()-start
    # Reheating restarts from best, with deterministic multi-temperature cycles.
    cycle=(epoch-1)%30
    if cycle==0:
        restore(best);curL=bestL
    T=(0.9*(0.025/0.9)**(cycle/29))
    if epoch%5==1:active=[k for k in gates if k not in fixed and k>=275000 and variable(k)]
    rng.shuffle(active)
    accepted=0
    for k in active:
        if not variable(k):continue
        opts=candidates(k)
        if len(opts)<2:continue
        slots=gate_slots[k];cur=gate_frame[k];g=rng.choice(opts)
        if g==cur or not nondeg(g):continue
        delta=gate_eval(slots,g)-gate_eval(slots,cur)
        if delta<=1e-12 or rng.random()<math.exp(-delta/T):
            setframe(k,g);curL+=delta;accepted+=1
            stats['down' if delta<-1e-9 else 'up' if delta>1e-9 else 'neutral']+=1
            if curL<bestL-1e-8:
                bestL=curL;best=dict(selected);stats['best_updates']+=1
        if time.monotonic()-last>=20:
            print('tick',epoch,'best',round(bestL-seedL,6),'current',round(curL-seedL,6),'intervals',len(interval_cache),'sec',round(time.monotonic()-start,1),flush=True);last=time.monotonic()
        if time.monotonic()-start>=seconds:break
    component_gain=harvest_components()
    if component_gain:print('component improvement',epoch,component_gain,'best',bestL-seedL,flush=True)
    if time.monotonic()-last>=15 or epoch==1:
        print('epoch',epoch,'T',round(T,4),'active',len(active),'accept',accepted,'current',round(curL-seedL,6),'best',round(bestL-seedL,6),'intervals',len(interval_cache),'frames',len(B),'sec',round(time.monotonic()-start,1),flush=True);last=time.monotonic()
        current=dict(selected);restore(best);snapshot('best');restore(current)
restore(best)
H=hist();actualL=sum(LN[d]*c for d,c in H.items());assert abs(actualL-bestL)<1e-6
assert sum(d*c for d,c in H.items())==sum(d*c for d,c in H0.items())
for i in initial:
    last=initial[i]
    for f in chain[i]+[final[i]]:assert sub(last,f);last=f
for k,g in selected.items():assert nondeg(g) and spanok(g,needs[k])
snapshot('final')
print('PASS_SEARCH_EXACT_NESTING_SPANS_FIXED_ENDPOINTS',json.dumps(dict(stats)),flush=True)
