"""Compile actual commuting coordinate idle groups of the connected L18 root."""
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

root=Path(__file__).resolve().parent
package=root/"connected7002"
source=package/"root_L18.json"
assert sha256(source.read_bytes()).hexdigest()=="be4a2beed3a40de6d2c5dcc6e4f25f3c2a4375551b70e63fb0e9a03041db6a34"
spec=json.loads(source.read_bytes())
n=spec["n"]
X,Y=([list(map(F,row)) for row in spec[label]] for label in ("X","Y"))
stages=spec["stages"]
boundaries={max(stage["units"])+1:j for j,stage in enumerate(stages)}
masks=[set(stage["mask"]) for stage in stages]

def clean_role(role,unit):
    return not X[unit][role] and not Y[unit][role]

# At a stage boundary r is an actual idle summand when its coordinate
# projector kills the two HOST directions on both sides.
eligible={(role,j) for j,stage in enumerate(stages) for role in masks[j]
          if all(clean_role(role,u) for u in stage["units"])}
assert len(eligible)<=sum(len(mask)-2 for mask in masks)
groups=defaultdict(list)
for role,j in sorted(eligible):
    cut=max(stages[j]["units"])+1
    # Pull the idle to the earliest cut in the current untouched run.
    previous=max((u+1 for u in range(cut) if not clean_role(role,u)),default=0)
    assert all(clean_role(role,u) for u in range(previous,cut))
    groups[role,previous].append(j)

paid=Counter({8:sum(len(mask)-2 for mask in masks)-len(eligible)})
for labels in groups.values():
    paid[8*len(labels)]+=1
assert sum(r*c for r,c in paid.items())==8*sum(len(mask)-2 for mask in masks)

# Independent value replay. At each gap, compare the original stream and the
# relocated stream on every column, in both sign sectors and two unrelated
# positive variable settings. Universal equality follows from the per-crossing
# zero row/column checks, not from these finite evaluations.
def replay(sign,variables,grouped):
    A=[[F(i==j) for j in range(n)] for i in range(n)]
    def scale(role,c):
        A[role]=[c*v for v in A[role]]
    moved=defaultdict(list)
    if grouped:
        for (role,cut),labels in groups.items():
            factor=1
            for j in labels:
                factor*=variables[j]
            moved[cut].append((role,factor))
    for cut in range(len(X)+1):
        if cut in boundaries:
            j=boundaries[cut]
            for role in masks[j]:
                if not grouped or (role,j) not in eligible:
                    scale(role,variables[j])
        for role,amount in moved[cut]:
            scale(role,amount)
        if cut<len(X) and sign!=1:
            x,y=X[cut],Y[cut]
            row=[sum(y[i]*A[i][j] for i in range(n) if y[i]) for j in range(n)]
            for i,scalar in enumerate(x):
                if scalar:
                    A[i]=[v+(sign-1)*scalar*z for v,z in zip(A[i],row)]
    return A

for sign in (-1,1):
    for shift in (2,13):
        variables=[(j+shift)**2+1 for j in range(len(stages))]
        assert replay(sign,variables,False)==replay(sign,variables,True)

ps=importlib.util.spec_from_file_location("power",package/"idle_coalescing.py")
power=importlib.util.module_from_spec(ps)
ps.loader.exec_module(power)
power.K=F(1,200)
mass=sum(paid.values())
base_jobs=sum(len(mask)-2 for mask in masks)
saving_lo=base_jobs*power.power_bounds(8)[0]-sum(c*power.power_bounds(r)[1] for r,c in paid.items())
saving_hi=base_jobs*power.power_bounds(8)[1]-sum(c*power.power_bounds(r)[0] for r,c in paid.items())
assert saving_lo>0
with (root/"PR7002-CHRONOLOGICAL-IDLE-GROUPS.json").open("x") as f:
    json.dump({"stage_count":len(stages),"old_jobs":base_jobs,"new_jobs":mass,"paid_idle_rank_profile":paid,
               "commuting_groups":[{"role":role,"cut":cut,"stages":labels} for (role,cut),labels in sorted(groups.items())],
               "per_port_saving_at_005":[power.decimal(saving_lo),power.decimal(saving_hi,"ROUND_CEILING")],
               "scope":"Constructed commuting normalized root schedule, universal over stage variables. Grouped jobs require the retained whole-mask IDLE tariff and physical adapters. No native price reduction, outer admission or kappa claim."},f,indent=2)
print("old jobs",base_jobs,"grouped jobs",mass,"histogram",dict(sorted(paid.items())),
      "per-port savings",float(saving_lo),"104-port savings",float(104*saving_lo),flush=True)
