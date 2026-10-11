"""Simulated annealing of the complex pair module at p = 10 against the base-compile proxy (base R / numerical root).
Moves re-split a node's support into two existing disjoint supports (sharing changes), keeping every root support.
Order: stable topological order (original positions as priority).  Evaluations ~8 s.  Writes the best module found."""
import sys, json, random, time, math, heapq
sys.path.insert(0,'/home/claude/cx')
import basecost
from itertools import combinations
M='/home/claude/cx/mods/'
P=10; n_in=36
start=json.load(open(sys.argv[1])); out=sys.argv[2]; budget=float(sys.argv[3]); seed=int(sys.argv[4])
rng=random.Random(seed)
def to_dag(mod):
    sup=[];recipe={};order={}
    for x,a in enumerate(mod['args']):
        if a is None: s=1<<x
        else: s=sup[a[0]]|sup[a[1]]
        sup.append(s)
        if a is not None and s not in recipe: recipe[s]=(sup[a[0]],sup[a[1]]); order[s]=x
        if a is None: order[s]=x
    roots=[sup[r] for r in mod['roots']]
    return recipe,order,roots
def reachable(recipe,roots):
    seen=set(); st=list(roots)
    while st:
        s=st.pop()
        if s in seen: continue
        seen.add(s)
        if s in recipe: st.extend(recipe[s])
    return seen
def export(recipe,order,roots):
    need=reachable(recipe,roots)
    inputs=[1<<i for i in range(n_in)]
    nodes=[s for s in need if s in recipe]
    # stable topological order by original position (new nodes get position of their first consumer - eps)
    indeg={s:0 for s in nodes}; users={}
    for s in nodes:
        for c in recipe[s]:
            if c in indeg: indeg[s]+=1; users.setdefault(c,[]).append(s)
    heap=[(order.get(s,1e9),s) for s in nodes if indeg[s]==0]; heapq.heapify(heap); topo=[]
    while heap:
        _,s=heapq.heappop(heap); topo.append(s)
        for u in users.get(s,[]):
            indeg[u]-=1
            if indeg[u]==0: heapq.heappush(heap,(order.get(u,1e9),u))
    assert len(topo)==len(nodes)
    idx={s:i for i,s in enumerate(inputs)}
    args=[None]*n_in
    for s in topo:
        a,b=recipe[s]; args.append([idx[a],idx[b]]); idx[s]=len(args)-1
    return dict(input_count=n_in,args=args,roots=[idx[r] for r in roots])
def evaluate(mod):
    json.dump(mod,open('/tmp/pm_try_%d.json'%seed,'w'))
    p,row=basecost.base(P,M+'tmod_v2_p10.json','/tmp/pm_try_%d.json'%seed,M+'bit_qmod_p10.json')
    return row['numerical_complex_root'], row['R']
recipe,order,roots=to_dag(start)
cur=export(recipe,order,roots); cur_root,cur_R=evaluate(cur); best=(cur_root,cur_R,cur)
print('start root %.6e R %d additions %d'%(cur_root,cur_R,len(cur['args'])-n_in),flush=True)
t0=time.time(); it=0; T=2e-7
while time.time()-t0<budget:
    it+=1
    need=reachable(recipe,roots); cand=[s for s in need if s in recipe and bin(s).count('1')>=3]
    S=rng.choice(cand)
    subs=[A for A in need if A!=S and (A&S)==A and (S^A) in need and A<(S^A)]
    alt=[A for A in subs if (A,S^A)!=recipe[S] and (S^A,A)!=recipe[S]]
    if not alt: continue
    A=rng.choice(alt)
    old=recipe[S]; recipe[S]=(A,S^A)
    if S in reachable(recipe,[A,S^A]):  # cycle guard (cannot happen: A,S^A strictly smaller) 
        recipe[S]=old; continue
    trial=export(recipe,order,roots)
    try: r,R=evaluate(trial)
    except Exception as e:
        recipe[S]=old; continue
    acc = r>=cur_root or rng.random()<math.exp((r-cur_root)/T)
    if acc:
        cur_root,cur_R=r,R
        if r>best[0]:
            best=(r,R,trial); json.dump(trial,open(out,'w'))
            print('it %d t %.0fs NEW BEST root %.6e R %d additions %d'%(it,time.time()-t0,r,R,len(trial['args'])-n_in),flush=True)
    else:
        recipe[S]=old
    T*=0.995
print('done its',it,'best root %.6e R %d'%(best[0],best[1]),flush=True)
