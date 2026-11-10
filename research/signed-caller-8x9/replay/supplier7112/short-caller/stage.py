"""Exact necessary screen for shared direct summands of grouped P104 idles."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
import hashlib,json,sys
from pathlib import Path

EXPECTED="3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e"

def dot(x,y):
    return sum(v*y.get(k,0) for k,v in x.items())

def linear(x,y,s):
    z=x.copy()
    for k,v in y.items():
        t=z.get(k,0)+s*v
        if t:z[k]=t
        else:z.pop(k,None)
    return z

def scale(x,s):
    return {k:v*s for k,v in x.items() if v*s}

def intersection(left,right):
    basis={}
    shared=[]
    for i,v in enumerate(left+right):
        coeff={i:F(1)}
        for k,(w,c) in basis.items():
            if k in v:
                s=v[k]
                v,coeff=linear(v,w,-s),linear(coeff,c,-s)
        if v:
            k=min(v);s=1/v[k]
            basis[k]=scale(v,s),scale(coeff,s)
        else:
            z={}
            for j,c in coeff.items():
                if j<len(left):z=linear(z,left[j],c)
            if z: shared.append(z)
    return shared

def act_x(p,x):
    z={}
    for a,b in p:z=linear(z,a,dot(b,x))
    return z

def act_y(y,p):
    z={}
    for a,b in p:z=linear(z,b,dot(y,a))
    return z

def colrank(vectors):
    basis={}
    for v in vectors:
        for k,w in basis.items():
            if k in v:v=linear(v,w,-v[k])
        if v:
            k=min(v);basis[k]=scale(v,1/v[k])
    return list(basis.values())

def rows_of(p,n):
    rows=[{} for _ in range(n)]
    for x,y in p:
        for i,v in x.items():rows[i]=linear(rows[i],y,v)
    return rows

def trans(M):
    n=len(M); out=[{} for _ in range(n)]
    for i,v in enumerate(M):
        for j,c in v.items():out[j][i]=c
    return out

def prod(A,B):
    rows=[]
    for row in A:
        v={}
        for i,c in row.items():v=linear(v,B[i],c)
        rows.append(v)
    return rows

def one_type(c,kind,return_images=False,return_hosts=False,phase=1,return_cuts=False):
    t=c["types"][kind]; n=t["roles"]; off=t["offset"]
    rows,cols=([{i:F(1)} for i in range(n)] for _ in range(2))
    def add(r,s,c):
        r-=off;s-=off
        rows[r]=linear(rows[r],rows[s],c)
        cols[s]=linear(cols[s],cols[r],-c)
    factors=[]
    cuts=[(-1,tuple(rows),tuple(cols))]
    for k,e in enumerate(c["events"]):
        tag=e[0]
        if tag=="J":
            if kind=="A":
                x,y,u,v=e[2]; add(y,x,F(1));add(u,v,F(t["alpha2"])); rr=(x,y,u,v)
            else:
                x,y,a,b=e[3][:4];add(x,y,F(a)*phase);add(y,x,F(b)*phase);rr=(x,y)
            p=[(cols[r-off],rows[r-off]) for r in rr]
            factors.append(("J",tuple(e[1:2]),[k],p))
            cuts.append((k,tuple(rows),tuple(cols)))
        elif tag==kind:
            op,r,*a=e[1:];j=r-off
            if op=="IDLE_ONE":
                st=tuple(a[0]);p=(cols[j],rows[j])
                if factors and factors[-1][:2]==("I",st) and all(not dot(y,p[0]) and not dot(p[1],x) for x,y in factors[-1][3]):
                    factors[-1][2].append(k);factors[-1][3].append(p)
                else:factors.append(("I",st,[k],[p]))
            elif op=="ADD":add(r,a[0],F(a[1]))
            elif op=="QUERY":
                add(r,a[0],F(phase)**a[1]);cuts.append((k,tuple(rows),tuple(cols)))
            elif op=="SWAP":
                jj=a[0]-off;rows[j],rows[jj]=rows[jj],rows[j];cols[j],cols[jj]=cols[jj],cols[j]
            elif op=="SCALE":
                q=F(a[0]);rows[j]=scale(rows[j],q);cols[j]=scale(cols[j],1/q)
            else:assert op=="LAMBDA"
    assert rows==cols==[{i:F(phase)} for i in range(n)]
    assert all(all(dot(y,x)==(i==j) for j,(x,_) in enumerate(p) for i,(_,y) in enumerate(p))
               for _,_,_,p in factors)
    if return_cuts:
        return cuts
    if return_hosts:
        return {st[0]:p for kind,st,_,p in factors if kind=="J"}
    groups={}; residuals={}; summ={}; image_pairs={}
    for stage in range(1,19):
        joint=[p for typ,st,_,p in factors if typ=="J" and stage in st]
        assert len(joint)==1
        idles=[p for typ,st,_,p in factors if typ=="I" and stage in st]
        vectors=[z for group in idles for z in group]
        n_j=len(joint[0])
        n_i=len(vectors)
        paid=rows_of(vectors,n)
        total=rows_of(vectors+joint[0],n)
        expected=[{i:F(1)} if d[stage+1] else {} for i,d in enumerate(t["diagonal"])]
        assert total==expected and n_i==sum(map(bool,expected))-n_j
        c_rank=colrank(trans(paid))
        r_rank=colrank(paid)
        assert len(c_rank)==len(r_rank)==n_i
        projection=prod(paid,paid)==paid
        summ[stage]={"target_rank":sum(map(bool,expected)), "joint_rank":n_j,
                     "idle_rank":len(r_rank),"paid_idles":n_i,"residual_is_projector":projection}
        groups[stage]=(c_rank,r_rank)
        residuals[stage]=paid
    if return_images:
        return {j:pair[0] for j,pair in groups.items()}
    cont={}
    for (a,(ax,ay)),(b,(bx,by)) in combinations(groups.items(),2):
        x=intersection(ax,bx)
        y=intersection(ay,by)
        covered=[p for typ,st,_,proj in factors if typ=="I" and a in st and b in st for p in proj]
        assert all(act_x([(i,j) for i,j in covered],u)==u for u,_ in covered)
        bound=sum(bool(dot(i,j)) for i in x for j in y)
        pair_rank=len(colrank([{j:dot(u,v) for j,v in enumerate(y) if dot(u,v)} for u in x]))
        cont[str((a,b))]=[len(x),len(y),bound,prod(residuals[a],residuals[b])==prod(residuals[b],residuals[a]),len(covered),pair_rank]
        assert len(x)==len(covered) and len(colrank([u for u,_ in covered]+x))==len(x)
        image_pairs[a,b]=x
    chains=(tuple(range(1,10)),tuple(range(18,9,-1)))
    assert all(not image_pairs[a,b] for a in chains[0] for b in chains[1])
    fixed,minimum=Counter(),Counter()
    idle_masks=[(st,len(p)) for typ,st,_,p in factors if typ=="I"]
    for mask,n_idle in idle_masks:
        fixed[8*len(mask)]+=n_idle
    budget=[]
    for chain in chains:
        for pos,i in enumerate(chain):
            later=chain[pos+1:]
            common=[image_pairs[tuple(sorted((i,j)))] for j in later]
            w=len(common[0]) if common else 0
            assert all(len(v)==len(colrank(common[0]+v))==w for v in common)
            n_idle=summ[i]["idle_rank"]
            assert w<=n_idle
            remaining=len(later)+1
            minimum[8]+=n_idle-w
            if w:
                minimum[8*remaining]+=w
                minimum[8*(remaining-1)]-=w
            budget.append(dict(stage=i,idle_rank=n_idle,extendable_rank=w,remaining=remaining))
    assert dict(+minimum)==dict(+fixed) and not -minimum
    return {"stages":summ,"shared_stage_directions":cont,"marginal_lower_bound":budget,
            "frozen_paid_rank_histogram":dict(+fixed),"lower_bound_paid_rank_histogram":dict(+minimum)}

def main():
    path=Path(sys.argv[1]); data=path.read_bytes(); assert hashlib.sha256(data).hexdigest()==EXPECTED
    c=json.loads(data)
    out={"caller_sha256":EXPECTED,"specialization":"q=+1", "controls":{},
         "types":{k:one_type(c,k) for k in ("A","B")}}
    x={0:F(1),1:F(1)};y={0:F(1),1:F(-1)};p=({0:F(1)},{1:F(1)})
    a=[{0:F(1)},{1:F(1)}]
    b=[x,y]
    assert len(intersection(a,b))==2 and all(not dot(w,p[0]) or not dot(w,p[1]) for w in a)
    assert intersection([x],[y])==[] and len(intersection([x],[scale(x,F(2))]))==1
    out["controls"]={"equal_planes_with_distinct_generators":"pass","disjoint_lines":"pass","scaled_equal_lines":"pass"}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
