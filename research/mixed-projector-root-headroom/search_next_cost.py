"""Screen the next root cost level with a bounded integer search.

All prices and solver bounds here are floating discovery evidence.
The registered exact proof does not execute this optional search.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, vstack
from functools import reduce
from itertools import combinations
import argparse

from verify import read_inputs

def admissible(masks):
    if any(not a & b for a,b in combinations(masks,2)):
        return False
    for a,b,c in combinations(masks,3):
        if (a|b|c).bit_count()<4:
            return False
        if a&b == a&c == b&c and (a&b).bit_count()==1:
            return False
    return all(reduce(int.__or__, group).bit_count()>=6 for group in combinations(masks,5))

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
local=read_inputs()['research/mixed-root-source-composition/RESULT.json']['local']
PAID={int(r):n for r,n in local['paid'].items()}
HELPERS={int(r):n for r,n in local['helpers'].items()}

K=.00328554
T=1-K
BOUND=200
sizes=np.arange(1,BOUND)
cost=np.zeros(BOUND)
for n in range(2,BOUND):
    cost[n]=min(cost[a]+cost[n-a] for a in range(1,n))+2*(8*n)**T+1-2*(8*n+1)**T
deficit=(sum(c*r**T for r,c in PAID.items())-sum(c*r**T for r,c in HELPERS.items()))/104
rows=[]
for extra in range(64):
    masks=[3,5,11,21,extra]
    if extra.bit_count()!=4 or not admissible(masks):continue
    support=np.array([[(mask>>j)&1 for j in range(6)] for mask in masks])
    n=len(sizes);nv=5*n+6
    objective=np.zeros(nv)
    for i,mask in enumerate(masks):
        objective[i*n:(i+1)*n]=sizes*deficit+cost[1:]+(mask.bit_count()-2)*(8*sizes)**T
    objective[-6:]=-1
    equality=np.zeros((5,nv))
    for i in range(5):equality[i,i*n:(i+1)*n]=1
    constraints=[];bounds=[]
    total=np.zeros((1,nv));total[0,:5*n]=np.tile(sizes,5)
    constraints.append(csr_matrix(total));bounds.append(BOUND-1)
    grid=np.arange(BOUND)
    slopes=8*T*(1+8*grid)**(-K)
    intercepts=(1+8*grid)**T-slopes*grid
    for j in range(6):
        degree=np.zeros(nv)
        for i in range(5):degree[i*n:(i+1)*n]=support[i,j]*sizes
        tangents=-slopes[:,None]*degree[None,:]
        tangents[:,5*n+j]=1
        constraints.append(csr_matrix(tangents));bounds.extend(intercepts)
    result=milp(objective,integrality=np.r_[np.ones(5*n),np.zeros(6)],bounds=Bounds(np.zeros(nv),np.full(nv,np.inf)),
                constraints=[LinearConstraint(vstack(constraints,format='csc'),np.full(len(bounds),-np.inf),np.array(bounds)),
                             LinearConstraint(csr_matrix(equality),np.ones(5),np.ones(5))],
                options={'time_limit':20.,'mip_rel_gap':1e-9})
    record={'masks':masks,'status':result.status,'incumbent_margin_float':-result.fun-2,
            'weights':(result.x[:5*n].reshape(5,n)@sizes).tolist(),
            'mip_dual_bound':result.mip_dual_bound,'message':result.message}
    rows.append(record)
    print('MASK',extra,record['incumbent_margin_float'],record['weights'],flush=True)
args.output.write_text(json.dumps({'saving':K,'tail_start':BOUND,'scope':'Floating integer solve; time limits are not exclusions. No rational dual certificate.','records':rows},indent=2)+'\n')
