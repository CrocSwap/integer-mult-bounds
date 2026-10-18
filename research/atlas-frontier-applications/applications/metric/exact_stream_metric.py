# SPDX-License-Identifier: Apache-2.0
"""Exact eight-stream metric certificate for the source-bound T114 R408 instance.
No native primitive or unconditional integer-multiplication claim is made.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,sys
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True

def need(p,message):
    if not p:raise AssertionError(message)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def atomic_new(p,obj):
    import os
    p=Path(p);need(not p.exists(),'refuse overwrite '+str(p));lock=p.with_suffix(p.suffix+'.lock')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
    try:p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    finally:lock.unlink()
def mm(A,B):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
def mv(A,v):return [sum(a*b for a,b in zip(row,v))for row in A]
def transpose(A):return list(map(list,zip(*A)))
def eye(n):return [[int(i==j)for j in range(n)]for i in range(n)]
def solve(A,b):
    n=len(A);C=[[Q(x)for x in row]+[Q(b[i])]for i,row in enumerate(A)]
    for k in range(n):
        pivot=next((i for i in range(k,n)if C[i][k]),None);need(pivot is not None,'singular exact system')
        C[k],C[pivot]=C[pivot],C[k];a=C[k][k];C[k]=[x/a for x in C[k]]
        for i in range(n):
            if i!=k:
                a=C[i][k];C[i]=[x-a*y for x,y in zip(C[i],C[k])]
    return [row[-1]for row in C]

EXPECTED_PAIRS=[0,0,0,1,1,2,2,3,3]
EXPECTED_BACK={1,3,5,7}
EXPECTED_BRIDGES=[(1,0,1),(1,0,-1),(2,1,1),(2,1,-1),(3,2,1),(3,2,-1),(2,3,1),(1,2,1),(0,1,1)]

def derive(recipe):
    P=eye(8);prefix=[];stages=[];bridges=[]
    for e in recipe:
        kind=e['kind'];need(kind in ('local','bridge','terminal'),'unknown source recipe event')
        if kind=='local':
            s=e['stage'];need(s==len(stages) and 0<=s<9,'stage order')
            need(e['pair']==EXPECTED_PAIRS[s] and bool(e['reverse'])==(s in EXPECTED_BACK),'actual local orientation/pair')
            x=2*e['pair'];y=x+1;t,source=(x,y) if e['reverse'] else(y,x)
            P[t]=[a+b for a,b in zip(P[t],P[source])];stages.append(s)
        elif kind=='bridge':
            source,t=e['src'],e['dst'];need(0<=source<4 and 0<=t<4 and source!=t and e['coefficient']in(-1,1),'within-owner unit bridge')
            bridges.append((source,t,e['coefficient']))
            for side in (0,1):P[2*t+side]=[a+b for a,b in zip(P[2*t+side],P[2*source+side])]
        else:need(e['pairs']==4 and len(stages)==9 and len(bridges)==9,'terminal four signed exchanges')
        prefix.append(copy.deepcopy(P))
    need(stages==list(range(9)) and bridges==EXPECTED_BRIDGES,'exact source nine-call/nine-bridge recipe')
    need(len(recipe)==19 and recipe[-1]['kind']=='terminal','terminal after full source recipe')
    need(all(x<=y for A in prefix for row,final in zip(A,P) for x,y in zip(row,final)),'every positive prefix bounded by full P')
    return P,prefix

def check_witness(recipe,w):
    P,prefix=derive(recipe);need(w['P']==P,'forged majorant')
    u=list(map(Q,w['u']));v=list(map(Q,w['v']));R=Q(w['R']);C=Q(w['C']);bits=w['boundary_bits']
    need(len(u)==len(v)==8 and all(x>0 for x in u+v),'positive exact Schur weights')
    need(R>0 and C>0 and isinstance(bits,int)and bits>=0,'positive bound and bit count')
    need(all(x<=R*y for x,y in zip(mv(P,v),u)),'Schur row certificate')
    need(all(x<=C*y for x,y in zip(mv(transpose(P),u),v)),'Schur column certificate')
    need(R*C<=2**(2*bits),'understated boundary bits')
    group=2**1296
    for j in range(1,37):group*=2**(2*j)-1
    stock=group*896;blockbits=(stock.bit_length()+1)//2
    need(w['group_order']==str(group)and w['block_stock_bits']==stock.bit_length()and w['block_l2_bits']==blockbits,'wrong owner ambient conversion')
    need(w['local_bits']==70 and w['retained_local_reserve']==128,'actual source native prefix')
    actual=70+37+bits+blockbits+1+4;reserve=128+37+bits+blockbits+1+4
    need(w['actual_prefix']==actual and w['reserve_prefix']==reserve,'prefix arithmetic')
    need(w['charged_payload']==2048 and reserve<2048,'payload reserve')
    return dict(boundary_bits=bits,norm_bound_squared=str(R*C),block_l2_bits=blockbits,actual_prefix=actual,reserve_prefix=reserve,charged_payload=2048,paid_payload_change=0,prefix_count=len(prefix))

def make_witness(recipe):
    P,_=derive(recipe);B=mm(transpose(P),P);seed=solve([[100*int(i==j)-B[i][j]for j in range(8)]for i in range(8)],[1]*8)
    v=[Q(int(x*1000))for x in seed];u=[Q((int(x)+9)//10)for x in mv(P,v)]
    group=2**1296
    for j in range(1,37):group*=2**(2*j)-1
    blockbits=((group*896).bit_length()+1)//2
    return dict(P=P,u=list(map(str,u)),v=list(map(str,v)),R='10',C='10',boundary_bits=4,group_order=str(group),block_stock_bits=(group*896).bit_length(),block_l2_bits=blockbits,local_bits=70,retained_local_reserve=128,actual_prefix=70+37+4+blockbits+1+4,reserve_prefix=128+37+4+blockbits+1+4,charged_payload=2048)

def controls(recipe,w,legacy,programs):
    tests=[]
    def reject(name,r,ww):
        try:check_witness(r,ww)
        except (AssertionError,KeyError,ValueError,IndexError):tests.append(name);return
        raise AssertionError('negative control accepted '+name)
    x=copy.deepcopy(w);x['P'][0][0]+=1;reject('forged_majorant',recipe,x)
    x=copy.deepcopy(w);x['v'][0]='-1';reject('negative_metric_weight',recipe,x)
    x=copy.deepcopy(w);x['boundary_bits']=3;reject('understated_three_bit_boundary',recipe,x)
    x=copy.deepcopy(w);x['block_l2_bits']=10;reject('omit_full_group_conversion',recipe,x)
    x=copy.deepcopy(w);x['actual_prefix']-=1;reject('understated_prefix_sum',recipe,x)
    r=copy.deepcopy(recipe);r[0]['reverse']=True;reject('wrong_actual_orientation',r,w)
    r=copy.deepcopy(recipe);del r[2];reject('missing_bridge',r,w)
    r=copy.deepcopy(recipe);r[2]['dst']=4;reject('bridge_crosses_owner_partition',r,w)
    ev=copy.deepcopy(programs['forward']);ev.append(['scalar',['add',['L',112],['L',224],1,1]])
    try:legacy.replay_endpoint(ev,112,408,False)
    except AssertionError:tests.append('forged_dirty_helper_to_data_response')
    else:raise AssertionError('dirty response control accepted')
    return tests

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();manifest=read(a.manifest)
    need(not a.out.exists(),'fresh output required');a.out.mkdir()
    inputs=manifest['inputs'];required={'hosted','legacy_checker'}|{pid+'/'+name for pid in('extra','gauge44')for name in('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','INDEPENDENT-LOCAL-REPLAY.json','LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json')}
    need(set(inputs)==required,'complete exact source role inventory')
    def guards():
        for key,z in inputs.items():need(sha(z['path'])==z['sha256'],'source guard '+key)
    guards();d=read(inputs['hosted']['path']);spec=importlib.util.spec_from_file_location('atlas_frozen_blocknorm',inputs['legacy_checker']['path']);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    dirs={pid:Path(inputs[pid+'/CANONICAL-WORD.json.gz']['path']).parent for pid in('extra','gauge44')}
    inherited=legacy.certify(d,dirs);need(inherited['replicas']==114 and inherited['local_actual_prefix_bits']==70,'actual T114/native binding')
    w=make_witness(d['recipe']);result=check_witness(d['recipe'],w)
    programs=read(inputs['extra/LOCAL-PROGRAMS.json.gz']['path']);negative=controls(d['recipe'],w,legacy,programs);guards()
    result.update(status='PASS_EXACT_T114_EIGHT_STREAM_BOUND',source_manifest_sha256=sha(a.manifest),inherited_blocknorm_status=inherited['status'],inherited_actual_prefix=inherited['actual_prefix_bits'],inherited_reserve_prefix=inherited['required_reserve_bits'],negative_controls_rejected=negative,scope='Actual source-bound R408 T114 endpoint/owner premise replay plus an exact stream-norm certificate. Retained native phase/normalization and all-size contracts remain. No paid payload or kappa gain is asserted.')
    atomic_new(a.out/'WITNESS.json',w);atomic_new(a.out/'RESULT.json',result);print(json.dumps(result,sort_keys=True),flush=True)
if __name__=='__main__':main()
