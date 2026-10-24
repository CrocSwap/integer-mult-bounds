#!/usr/bin/env python3
"""One macro-observation bank-level span, not a physical caller emitter.

Block-scalar coefficients are deliberately distinguished from arbitrary
port-by-port owner controls. A negative result here does not close the
larger permitted physical grammar.
"""
import contextlib
import hashlib
import io
import json
from fractions import Fraction as F
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
dependency=HERE.parent/'pr4948-mixed-thin-gate/check.py'
need_hash='fe7db972d7ae238b21f8a453c21243360d131d728a76b91a469dacf447629582'
if hashlib.sha256(dependency.read_bytes()).hexdigest()!=need_hash:
    raise ValueError('Frozen mixed derivation changed')
with contextlib.redirect_stdout(io.StringIO()): env=runpy.run_path(str(dependency))
a,q,qi,c,e,d,f=[env[k] for k in ('a','q','qi','c','e','d','f')]
need=env['need']

def observations(c1,c3):
    rows=[[a.one if i==j else {} for j in range(4)] for i in range(4)]
    obs=[]; cuts=[]
    def snap(label):
        cuts.append(label)
        for i,row in enumerate(rows): obs.append((label+':'+str(i),list(row)))
    def plus(i,j,z): rows[i]=[a.add(x,a.mul(z,y)) for x,y in zip(rows[i],rows[j])]
    def left(i,z): rows[i]=[a.mul(z,x) for x in rows[i]]
    def thin(pair,before,after,label):
        response=[a.mul(before,x) for x in rows[2*pair]]
        obs.append((label,response))
        rows[2*pair+1]=[a.add(x,a.mul(after,y)) for x,y in zip(rows[2*pair+1],response)]
    def full(pair,C,D):
        plus(2*pair,2*pair+1,a.neg(a.mul(q,C)))
        left(2*pair,D);left(2*pair+1,D)
    def bridge(dst,src,sgn):
        plus(2*dst,2*src,a.one if sgn==1 else a.neg(a.one))
        plus(2*src+1,2*dst+1,a.neg(a.one) if sgn==1 else a.one)
    rows[0][2]=a.neg(a.one);rows[3][1]=a.one
    snap('cut0_after_right_boundary')
    thin(0,qi,c1,'paid_response0_Qinv_x')
    snap('cut1_after_thin0')
    full(0,c1,d);snap('cut2_after_FULL1')
    left(2,d);left(3,d);snap('cut3_after_IDLE')
    bridge(0,1,1)
    thin(0,a.mul(qi,c1),a.one,'paid_response2_Qinv_C1_x')
    snap('cut4_after_bridge_plus_and_thin2')
    bridge(0,1,-1);snap('cut5_after_bridge_minus')
    full(1,c3,f);snap('cut6_after_FULL3')
    thin(1,a.mul(qi,c3),a.one,'paid_response4_Qinv_C3_x')
    snap('cut7_after_thin4')
    bridge(1,0,1)
    for pair in range(2):
        x,y=2*pair,2*pair+1
        rows[x],rows[y]=rows[y],[a.neg(z) for z in rows[x]]
    plus(0,2,a.one);plus(3,1,a.neg(a.one))
    snap('cut8_after_final_standard_boundary')
    return obs,cuts,rows

def vector(row):
    return {(i,w,ds):v for i,p in enumerate(row) for (w,ds),v in p.items() if v}
def axpy(x,z,y):
    out=dict(x)
    for k,v in y.items():
        out[k]=out.get(k,F(0))+z*v
        if not out[k]:del out[k]
    return out
def scale(x,z):return {k:z*v for k,v in x.items() if z*v}

controls=[(),(2,),(3,),(2,3),(3,2),(2,3,2),(3,2,3)]
def span(obs,targets):
    basis={};generators=[]
    for label,row in obs:
        for control in controls:
            z=a.term(control,(0,0))
            v=vector([a.mul(z,p) for p in row])
            index=len(generators);generators.append({'observation':label,'left_word':list(control)})
            coef={index:F(1)}
            while v:
                pivot=min(v)
                if pivot not in basis:
                    inv=1/v[pivot];basis[pivot]=(scale(v,inv),scale(coef,inv));break
                b,bc=basis[pivot];factor=v[pivot]
                v=axpy(v,-factor,b);coef=axpy(coef,-factor,bc)
    answers=[]
    for target in targets:
        v=vector(target);coef={}
        while v:
            pivot=min(v)
            if pivot not in basis:break
            b,bc=basis[pivot];factor=v[pivot]
            v=axpy(v,-factor,b);coef=axpy(coef,factor,bc)
        answers.append({'attained':not v,
            'recipe':[{**generators[i],'coefficient':str(z)} for i,z in sorted(coef.items())] if not v else None,
            'first_residual_monomial':{'source':min(v)[0],'word':list(min(v)[1]),'D_powers':list(min(v)[2]),'coefficient':str(v[min(v)])} if v else None})
    return {'basis_dimension':len(basis),'generator_count':len(generators),'answers':answers}

targets=[a.mul(d,qi),a.mul(d,q),a.mul(f,d,qi),a.mul(f,d,q)]
targetrows=[[targets[i] if i==j else {} for j in range(4)] for i in range(4)]
obs,cuts,rows=observations(c,e)
need(rows==env['rows'],'Exact frozen mixed endpoint')
actual=span(obs,targetrows)
plain,_,_=observations(a.one,a.one)
control=span(plain,targetrows)
need(all(x['attained'] for x in control['answers']),'Uncoded recoverability control')
out={'status':'BANK_LEVEL_SPAN_ONLY_PENDING_PORT_LEVEL_GATE',
     'cuts':cuts,'paid_response_count':3,'saved_bank_fields':len(obs),
     'controls':controls,'actual':actual,'uncoded_control':control,
     'copy_upper_ledger':{'independent_original_main_fields':448,'saved_dependent_fields':len(obs)*112,
       'COPY':len(obs)*112,'owned_zero_initializations':len(obs)*112,
       'required_final_zero_resets':len(obs)*112,'extra_Gaussian_calls':0,
       'qualification':'An all-snapshot upper inventory, not a cleanup certificate. Snapshots must be erased from still-available sources or an admitted final free representation.'},
     'helpers':'Both invocations retain408 autonomous helper jobs each, untouched by this bank-level observation model.',
     'scope':'Scalar coefficients on whole112-port banks plus reduced C1/C3 words length<=3. Arbitrary per-port scalar controls are not yet represented.',
     'physical_emission':False,'new_kappa':None,
     'dependency_sha256':need_hash}
print(json.dumps(out,indent=2,sort_keys=True))
