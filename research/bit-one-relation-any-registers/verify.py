"""Finite controls for the arbitrary-register one-relation proof. Apache-2.0."""
import hashlib,itertools,json,sys
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def need(x,m):
    if not x:raise ValueError(m)
def mat(x,y,n):return tuple(y if x>>i&1 else 0 for i in range(n))
def mm(a,b):
    out=[]
    for row in a:
        z=0
        for i in range(len(a)):
            if row>>i&1:z^=b[i]
        out.append(z)
    return tuple(out)
def mx(a,b):return tuple(x^y for x,y in zip(a,b))
def cyclic(pattern,n):
    reach=list(pattern)
    for k in range(n):
        for i in range(n):
            if reach[i]>>k&1:reach[i]|=reach[k]
    return any(reach[i]>>i&1 for i in range(n))
def formal(ops,n,d):
    zero=(0,)*d;eye=tuple(1<<i for i in range(n));none=(0,)*n;out={zero:eye}
    for a,p in ops:
        nxt={}
        for b,q in out.items():
            for shift,m in ((zero,mx(eye,p)),(a,p)):
                addr=tuple(x+y for x,y in zip(b,shift));nxt[addr]=mx(nxt.get(addr,none),mm(q,m))
        out={a:p for a,p in nxt.items() if any(p)}
    return out
def diagonal(out):return all(all(not(row&~(1<<i)) for i,row in enumerate(p)) for p in out.values())
def run():
    for f in json.loads((H/'SOURCES.json').read_text())['files']:
        if f['usage']=='input':need(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],'source')
    reports=[];conjugations=0
    for n in range(1,6):
        groups=defaultdict(list);count=0
        for x,y in itertools.product(range(1,1<<n),repeat=2):
            if not((x&y).bit_count()%2):continue
            p=mat(x,y,n);need(mm(p,p)==p,'idempotent');pat=tuple(row&~(1<<i) for i,row in enumerate(p));groups[pat].append((x,y,p));count+=1
        cycles=0
        for pat,entries in groups.items():
            if cyclic(pat,n):need(len(entries)==1,'cyclic pattern not unique');cycles+=1
            else:need(all((x&y).bit_count()==1 for x,y,p in entries),'acyclic diagonal weight')
            for x,y,p in entries:
                for k in range(n):
                    e=mat(1<<k,1<<k,n)
                    # Form the Laurent conjugate D_N(z) E D_N(z^-1) directly.
                    eye=tuple(1<<i for i in range(n));a={0:mx(eye,p),1:p};b={0:mx(eye,p),-1:p};out={}
                    for i,aa in a.items():
                        for j,bb in b.items():out[i+j]=mx(out.get(i+j,(0,)*n),mm(mm(aa,e),bb))
                    out={t:m for t,m in out.items() if any(m)}
                    commute=mm(p,e)==mm(e,p)
                    need(diagonal(out)==commute,'diagonal-conjugate equivalence')
                    if commute:need(out=={0:e},'constant diagonal conjugate')
                    conjugations+=1
        need(count==((1<<n)-1)*(1<<(n-1)),'complete projector count')
        reports.append(dict(registers=n,projectors=count,patterns=len(groups),cyclic_patterns=cycles))
    fixtures=[];frames=[(1,0,0),(0,1,0),(-1,-1,0)];outside=(0,0,1)
    for x,y in ((7,7),(7,15),(15,7)):
        p=mat(x,y,4)
        for k in range(4):
            e=mat(1<<k,1<<k,4)
            for gap in range(4):
                ops=[(a,p) for a in frames];ops.insert(gap,(outside,e));out=formal(ops,4,3)
                want=gap in (0,3) or mm(p,e)==mm(e,p)
                need(diagonal(out)==want,'one-relation placement fixture')
                fixtures.append([x,y,k,gap,want])
    # Torsion countercontrol: same nonzero rational frame twice is not a diagonal identity.
    p=mat(7,7,4);out=formal([((1,),p),((1,),p)],4,1);need(not diagonal(out),'torsion-free control')
    folded={}
    for a,m in out.items():folded[a[0]%2]=mx(folded.get(a[0]%2,(0,)*4),m)
    need(folded=={0:tuple(1<<i for i in range(4))},'unsafe torsion specialization passes')
    return dict(status='PASS_ONE_RELATION_ANY_REGISTERS',projector_censuses=reports,laurent_conjugation_checks=conjugations,rank_one_frame_relation_fixtures=fixtures,torsion_countercontrol=True,scope='Written arbitrary-W lemma; finite checks only W1..5 and declared fixtures',no_new_kappa=True)
if __name__=='__main__':
    x=run();p=H/'CERTIFICATE.json'
    if '--write' in sys.argv:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(x==json.loads(p.read_text()),'receipt')
    print(x['status'],'censuses='+str(x['projector_censuses']),'conjugations='+str(x['laurent_conjugation_checks']))
