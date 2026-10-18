#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact audit by woklerx with substantial OpenAI Codex assistance."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, permutations
from math import isqrt
import json, hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok, message):
    if not ok: raise ValueError(message)
def source_check():
    for row in json.loads((HERE/'EXTERNAL-SOURCES.json').read_text()):
        b=(HERE/row['local']).read_bytes()
        require(hashlib.sha256(b).hexdigest()==row['sha256'],'external source bytes')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'external Git blob')
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'live source bytes')
source_check()

# Truth vectors pack the eight complete assignments into one byte.
inputs=[sum(((x>>r)&1)<<x for x in range(8)) for r in range(3)]
gates=[(t,(c,)) for t in range(3) for c in range(3) if c!=t]+[(t,tuple(c for c in range(3) if c!=t)) for t in range(3)]
def graph(word):
    values=inputs[:];last=list(range(3));edges=[]
    for j,g in enumerate(word):
        t,controls=g;v=3+j
        for role in [t,*controls]:edges.append((last[role],v,values[role]));last[role]=v
        term=255
        for c in controls:term &= values[c]
        values[t]^=term
    if sorted(values)!=sorted(inputs):return None
    rho=[values.index(x) for x in inputs]
    for r in range(3):edges.append((last[r],3+len(word)+r,values[r]))
    return edges,rho

def injective(edges,demands,outgoing):
    fixed=7^demands;seen={}
    for x in range(8):
        transcript=sum(((edges[e][2]>>x)&1)<<j for j,e in enumerate(outgoing))
        key=(x&fixed,transcript)
        if key in seen and (seen[key]&demands)!=(x&demands):return False
        seen[key]=x
    return True
words=valid=cuts=transcripts=0;depth_counts={};nonidentity=0
for depth in range(1,6):
    cnt=0
    for ids in product(range(9),repeat=depth):
        words+=1
        if not any(i>=6 for i in ids):continue
        word=[gates[i] for i in ids];g=graph(word)
        if g is None:continue
        valid+=1;cnt+=1;edges,rho=g;nonidentity+=rho!=[0,1,2]
        vertices=6+depth
        # Complement symmetry fixes source vertex zero to label 0; both classes are audited.
        for mask0 in range(1<<(vertices-1)):
            mask=mask0<<1
            for label in (0,1):
                demand=sum(1<<r for r in range(3) if ((mask>>r)&1)==label and ((mask>>(3+depth+rho[r]))&1)!=label)
                if not demand:continue
                outgoing=[i for i,(u,v,t) in enumerate(edges) if ((mask>>u)&1)==label and ((mask>>v)&1)!=label]
                require(len(outgoing)>=demand.bit_count(),'cut cardinality')
                require(injective(edges,demand,outgoing),'full transcript injectivity')
                cuts+=1;transcripts+=8
    depth_counts[str(depth)]=cnt
# Direct missing-wire control in the sharp identity topology.
edges=[(r,3+r,inputs[r]) for r in range(3)]
require(injective(edges,7,[0,1,2]) and not injective(edges,7,[1,2]),'omitted physical terminal wire')
# A Toffoli identity mutant passes zero and every basis input but not all dirty inputs.
target,ctrl=gates[6];false=inputs[:];false[target]^=inputs[ctrl[0]]&inputs[ctrl[1]]
require(all(all(((false[r]>>x)&1)==((inputs[r]>>x)&1) for r in range(3)) for x in [0,1,2,4]),'basis trap setup')
require(false!=inputs,'basis-only endpoint checker must reject')
# Complete finite upper triangular rank/diagonal calibration for the common-flag step.
mats=list(product([-1,0,1],repeat=3));matrix_pairs=0
for A,B in product(mats,repeat=2):
    x,y,z=[b-a for a,b in zip(A,B)]
    rank=2 if x*z else int(bool(x or y or z))
    require(rank>=int(x!=0)+int(z!=0),'common-flag rank charge');matrix_pairs+=1
receipt=json.loads(json.dumps({'status':'PASS_NONLINEAR_CUT_EXHAUSTIVE_AUDIT','enumerated_words':words,'nonlinear_permutation_words':valid,'by_depth':depth_counts,'nonidentity_permutation_words':nonidentity,'demanded_label_class_cuts':cuts,'complete_assignment_transcripts':transcripts,'upper_triangular_matrix_pairs':matrix_pairs,'controls':2,'no_new_kappa':True},sort_keys=True))
require(receipt==json.loads((HERE/'RESULT.json').read_text()),'committed audit receipt differs from recomputation')
print(json.dumps(receipt,sort_keys=True))
