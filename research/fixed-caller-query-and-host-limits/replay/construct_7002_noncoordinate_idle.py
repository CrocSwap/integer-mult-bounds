"""Construct persistent noncoordinate idle projectors and replay their relocation."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import json

root=Path(__file__).resolve().parent
base=root/"construct_7002_chronological_idle_groups.py"
ns={"__file__":str(base)}
exec(base.read_text().split("def clean_role")[0],ns)
n,X,Y,stages,masks,boundaries=(ns[k] for k in ("n","X","Y","stages","masks","boundaries"))
def dot(a,b):
    return sum(x*y for x,y in zip(a,b) if x and y)

def nullspace(constraints,indices):
    width=len(indices)
    pivots={}
    for row in constraints:
        v=[row[i] for i in indices]
        for j in range(width):
            c=v[j]
            if not c:
                continue
            if j not in pivots:
                pivots[j]=[x/c for x in v]
                break
            v=[x-c*y for x,y in zip(v,pivots[j])]
    result=[]
    for free in range(width):
        if free in pivots:
            continue
        u=[F(i==free) for i in range(width)]
        for pivot,row in sorted(pivots.items(),reverse=True):
            u[pivot]=-dot(row,u)
        v=[F(0)]*n
        for i,x in zip(indices,u):
            v[i]=x
        result.append(v)
    return result

def paired(a,b):
    while a and b:
        pivot=next(((i,j,dot(v,u)) for i,v in enumerate(a) for j,u in enumerate(b) if dot(v,u)),None)
        if pivot is None:
            break
        i,j,c=pivot
        v=a.pop(i)
        u=[z/c for z in b.pop(j)]
        a=[[x-dot(u,w)*y for x,y in zip(w,v)] for w in a]
        b=[[x-dot(v,w)*y for x,y in zip(w,u)] for w in b]
        yield v,u

intervals=sorted(((i,j) for i in range(len(stages)) for j in range(i+1,len(stages))),
                 key=lambda t:(t[0]-t[1],t[0]))
chosen=[]
for i,j in intervals:
    support=sorted(set.intersection(*masks[i:j+1]))
    if not support:
        continue
    units=range(min(stages[i]["units"]),max(stages[j]["units"])+1)
    overlaps=[(v,u) for a,b,v,u in chosen if max(i,a)<=min(j,b)]
    vectors=nullspace([Y[k] for k in units]+[u for _,u in overlaps],support)
    duals=nullspace([X[k] for k in units]+[v for v,_ in overlaps],support)
    for v,u in paired(vectors,duals):
        assert dot(v,u)==1
        assert all(dot(v,Y[k])==dot(u,X[k])==0 for k in units)
        assert all(dot(v,old_u)==dot(u,old_v)==0 for old_v,old_u in overlaps)
        overlaps.append((v,u))
        chosen.append((i,j,v,u))
# Replay explicit projection products. At stage j remove grouped projectors
# from the diagonal dilation and issue their product at the first stage.
def replay(sign,weights,grouped):
    A=[[F(i==j) for j in range(n)] for i in range(n)]
    def correction(v,u,scale,input_rows):
        coeff=[dot(u,column) for column in zip(*input_rows)]
        for r,rv in enumerate(v):
            if rv:
                A[r]=[a+scale*rv*c for a,c in zip(A[r],coeff)]
    for cut in range(len(X)+1):
        if cut in boundaries:
            stage=boundaries[cut]
            before=[row[:] for row in A]
            d=weights[stage]
            for i in masks[stage]:
                A[i]=[d*x for x in before[i]]
            if grouped:
                for start,end,v,u in chosen:
                    if start<=stage<=end:
                        correction(v,u,1-d,before)
                for start,end,v,u in chosen:
                    if start==stage:
                        value=1
                        for j in range(start,end+1):
                            value*=weights[j]
                        correction(v,u,value-1,A)
        if cut<len(X) and sign!=1:
            correction(X[cut],Y[cut],sign-1,A)
    return A

for sign in (-1,1):
    for shift in (3,17):
        weights=[(j+shift)**2+1 for j in range(len(stages))]
        assert replay(sign,weights,False)==replay(sign,weights,True)
profile=Counter(8*(j-i+1) for i,j,_,_ in chosen)
base_jobs=sum(len(mask)-2 for mask in masks)
profile[8]=base_jobs-sum(r*c//8 for r,c in profile.items())
assert profile[8]>=0
assert sum(r*c for r,c in profile.items())==base_jobs*8
import importlib.util
ps=importlib.util.spec_from_file_location("power",root/"connected7002"/"idle_coalescing.py")
power=importlib.util.module_from_spec(ps)
ps.loader.exec_module(power)
power.K=F(1,200)
low=base_jobs*power.power_bounds(8)[0]-sum(c*power.power_bounds(r)[1] for r,c in profile.items())
high=base_jobs*power.power_bounds(8)[1]-sum(c*power.power_bounds(r)[0] for r,c in profile.items())
coordinate=json.loads((root/"PR7002-CHRONOLOGICAL-IDLE-GROUPS.json").read_text())
advantage=104*(low-F(coordinate["per_port_saving_at_005"][1]))
with (root/"PR7002-NONCOORDINATE-IDLE-WORD.json").open("x") as f:
    json.dump({"idle_rank_profile":profile,"base_jobs":base_jobs,"projectors":[[i,j,list(map(str,v)),list(map(str,u))] for i,j,v,u in chosen],
               "per_port_saved_interval":[power.decimal(low),power.decimal(high,"ROUND_CEILING")],
               "104_port_saving_over_coordinate_lower":power.decimal(advantage),
               "scope":"Exact normalized role-level relocation by orthogonal projectors, with all-column rational controls. Requires physical whole-idle composition, ordinary map costs, and the native HOST construction."},f,indent=2)
print("projectors",len(chosen),"profile",dict(profile),"old",base_jobs,"new",sum(profile.values()),
      "104 port extra savings over coordinate",float(advantage),flush=True)
