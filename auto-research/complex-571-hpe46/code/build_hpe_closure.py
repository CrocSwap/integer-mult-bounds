"""Generalised hyperplane-ended helpers (closure form). Recipe-driven build for the package: the chosen helpers and the tail are recomputed from the word and must equal the recipe.
"""
"""Generalised hyperplane-ended helpers: end every entering helper whose cleanup can run below FULL.
T = closure (under non-commuting precedence) of the chosen helpers' cleanup gates; T runs right after B in a greedy minimal-frame order;
the chosen helpers end at their last tail frame (must have dim < 9); everything else climbs to FULL and the rest of the cleanup runs at FULL.
Usage: build_hpe2.py IN.json.gz OUT_DIR [max_candidates]"""
import sys,gzip,json,math,hashlib
from collections import Counter,defaultdict
from pathlib import Path
F='/private/tmp/claude-501/-Users-sreekanthnair-Documents-Projects-nlogn/a545f491-8755-42a6-8a72-750f99423436/scratchpad/frontier'
sys.path.insert(0,F+'/pr568/research/complex-multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk');import gk_common as C
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--recipe',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--nominate',type=Path);a=ap.parse_args()
w=json.loads(gzip.decompress(a.input.read_bytes()));out=a.out;V=112;R=w['report']['R'];N=2*V+R;P=w['ports']
assert 'early_cleanup' not in w
m=73.0;g=lambda r:r*math.log(m/r)if r>0 else 0
def regs(e):return[e[1]]+([e[2]]if e[0]=='add'else[])
def commute(x,y):
    if x[0]=='add'and y[0]=='add':return x[1]!=y[2]and y[1]!=x[2]
    return not set(regs(x))&set(regs(y))
B=lambda vs:tuple(C.basis(vs))
cur={r:(B([P[r]])if r<V else(B(w['start_extra'][str(r)])if r>=2*V and str(r)in w.get('start_extra',{})else()))for r in range(N)}
paidAB=Counter()
def climb(r,f):
    f=B(f)
    if cur[r]!=f:
        assert B(list(cur[r])+list(f))==f,('nonmonotone',r);paidAB[len(f)-len(cur[r])]+=1;cur[r]=f
# centres' served-level climbs (as in gk_word.profile) are part of the local profile; compute them the same way
lev={int(t):B(E)for t,E in w.get('target_levels',{}).items()}
for part in('A','B'):
    if part=='B':
        for r,f in zip(w['centers'],w['center_frames']):
            served=sorted({lev.get(e[1]-V,())for e in w['cut']if e[2]==r},key=lambda E:-len(E));o=B(f)
            for Lv in served:
                if Lv!=o:paidAB[len(o)-len(Lv)]+=1;o=Lv
    for e in w[part]:
        for r in regs(e):climb(r,e[-1])
last=dict(cur);entering={r for r in range(2*V,N)if str(r)in w.get('start_extra',{})}
cl=w['cleanup'];n=len(cl);cnt=Counter()
for e in cl:
    for r in regs(e):cnt[r]+=1
pred=[set()for _ in range(n)]
for i,e in enumerate(cl):
    for j in range(i):
        if not commute(cl[j],e):pred[i].add(j)
gates_of=defaultdict(list)
for i,e in enumerate(cl):
    for r in regs(e):gates_of[r].append(i)
def J(r):return len(B([x for q in {r}|{q for i in gates_of[r]for q in regs(cl[i])}for x in last[q]]))
cands=[h for h in range(2*V,N)if h in entering and J(h)<9]
MAXC=len(cands)
print('candidate entering helpers with partner-join dim < 9:',len(cands),'by #cleanup gates',Counter(cnt[h]for h in cands))
def closure(gs):
    T=set();stack=list(gs)
    while stack:
        i=stack.pop()
        if i in T:continue
        T.add(i);stack.extend(pred[i])
    return T
def schedule(T):
    """greedy minimal-frame order of T respecting precedence; returns (order, frames per gate, final frames)"""
    c=dict(last);indeg={i:len(pred[i]&T)for i in T};avail={i for i in T if indeg[i]==0};succ=defaultdict(list)
    for i in T:
        for j in pred[i]:
            if j in T:succ[j].append(i)
    order=[];fr={}
    while avail:
        i=min(avail,key=lambda i:(len(B([x for r in regs(cl[i])for x in c[r]])),i));avail.remove(i)
        f=B([x for r in regs(cl[i])for x in c[r]]);fr[i]=f
        for r in regs(cl[i]):c[r]=f
        order.append(i)
        for s in succ[i]:
            indeg[s]-=1
            if indeg[s]==0:avail.add(s)
    assert len(order)==len(T);return order,fr,c
# choose helpers greedily: add candidates one by one (by J then index), keep if it still ends below FULL and no chosen helper is spoiled
chosen=[]
for h in sorted(cands,key=lambda h:(J(h),h))[:MAXC]:
    trial=chosen+[h];T=closure([i for q in trial for i in gates_of[q]]);order,fr,c=schedule(T)
    if all(len(c[q])<9 for q in trial):chosen=trial
T=closure([i for q in chosen for i in gates_of[q]]);order,fr,c=schedule(T)
print('chosen hyperplane-ended helpers:',len(chosen),'| tail gates',len(T),'| registers touched by the tail',len({r for i in T for r in regs(cl[i])}))
# profile: A/B climbs + tail climbs + finals
paid=Counter(paidAB);c2=dict(last)
for i in order:
    f=fr[i]
    for r in regs(cl[i]):
        if c2[r]!=f:paid[len(f)-len(c2[r])]+=1;c2[r]=f
hf={h:list(c2[h])for h in chosen}
for r in range(N):
    fin=B(list(C.FULL))if(r<V or r>=2*V)else B(list(__import__('gk_word').perp(P[r-V])))if False else None
for r in range(N):
    if V<=r<2*V:
        import gk_word as G;G.V=112;fin=B(list(G.perp(P[r-V])))
    elif r in hf:continue
    else:fin=B(list(C.FULL))
    if c2[r]!=fin:paid[len(fin)-len(c2[r])]+=1
phi=lambda pr:sum(n*g(r)for r,n in pr.items())
ref=Counter({int(k):v for k,v in w['report']['local_profile'].items()})
print('input local profile',dict(sorted(ref.items())),'Phi',round(phi(ref),2))
print('new   local profile',dict(sorted(paid.items())),'Phi',round(phi(paid),2),'delta',round(phi(paid)-phi(ref),2))
inv=Counter({int(k):v for k,v in w['report']['width_inventory'].items()})
for h in chosen:e=len(w['start_extra'][str(h)]);inv[9-e]-=1;inv[len(hf[h])-e]+=1
print('width inventory',dict(sorted(inv.items())),'(hyperplane-ended:',len(chosen),')')
w['early_cleanup']=[[i,list(fr[i])]for i in order];w['helper_final']={str(h):v for h,v in sorted(hf.items())}
w['report']['local_profile']={str(r):c for r,c in sorted(paid.items())if c};w['report']['local_rank_mass']=sum(r*c for r,c in paid.items())
w['report']['width_inventory']={str(k):v for k,v in sorted(inv.items())if v}
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();digest=hashlib.sha256(raw).hexdigest()
rec=dict(helpers=sorted(chosen),early_cleanup=w['early_cleanup'],helper_final=w['helper_final'],output_content_sha256=digest)
if a.nominate:a.nominate.write_text(json.dumps(rec,indent=1)+'\n',newline='\n');raise SystemExit(0)
r=json.loads(a.recipe.read_bytes());assert r['helpers']==rec['helpers']and r['early_cleanup']==rec['early_cleanup']and r['helper_final']==rec['helper_final'],'recipe differs from the recomputed closure build'
assert r['output_content_sha256']==digest,digest
out.mkdir(parents=True,exist_ok=False);(out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
(out/'HPE-CONSTRUCTION.json').write_text(json.dumps(dict(status='PASS_HYPERPLANE_ENDED_HELPERS_CLOSURE',helpers=rec['helpers'],tail_gates=len(rec['early_cleanup']),local_profile=w['report']['local_profile']),indent=1)+'\n',newline='\n')
print('PASS',len(chosen),'hyperplane-ended helpers (closure form), tail gates',len(rec['early_cleanup']))
