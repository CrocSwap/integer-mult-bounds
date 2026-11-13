#!/usr/bin/env python3
"""Read-only exact-source controls for the selected packed grid interface."""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha1,sha256
import gzip,json,sys,types
HERE=Path(__file__).resolve().parent
PIN='e54523517d0f03e58352e647c403a5af3e525a57'
def need(ok,label):
    if not ok:raise ValueError(label)
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def iphase(a,k):return mul(a,[(1,0),(0,1),(-1,0),(0,-1)][k%4])
def deposit(v,x,a):
    b=plus(v.get(x,(Q(0),Q(0))),a)
    if b!=(0,0):v[x]=b
    else:v.pop(x,None)
def axis(v,j):
    out={}
    for x,a in v.items():
        deposit(out,x,mul(a,(Q(1,2),Q(1,2))))
        deposit(out,x^(1<<j),mul(a,(Q(1,2),-Q(1,2))))
    return out
def column(x,j,f):return sum(((x>>(i*f+j))&1)<<i for i in range(9))
def replace(x,j,f,y):
    for i in range(9):
        bit=i*f+j;x=(x&~(1<<bit))|(((y>>i)&1)<<bit)
    return x
def monomial(v,record,f,c,inverse=False):
    out={};G=tuple(record['matrix_rows']);Gi=c.inv(G,9)
    for address,a in v.items():
        result=address;phase=0
        for j in range(f):
            y=column(address,j,f)
            x=c.mv(Gi,y^record['offset']) if inverse else y
            phase+=record['phase']+c.qvalue(tuple(record['quadratic_rows']),tuple(record['linear_Z4']),x,9)
            result=replace(result,j,f,x if inverse else c.mv(G,x)^record['offset'])
        deposit(out,result,iphase(a,-phase if inverse else phase))
    return out
def integral(v):return all(Q(a).denominator==1 for z in v.values() for a in z)
def main():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    need(sources['base_commit']==PIN,'canonical source pin')
    for source in sources['bundled_inputs']:
        name=Path(source['path'])
        need(not name.is_absolute() and '..' not in name.parts,'regular package-local source')
        file=HERE/name;need(file.is_file() and not file.is_symlink(),'ordinary retained source file')
        data=file.read_bytes()
        need(len(data)==source['bytes'] and sha256(data).hexdigest()==source['sha256'],'exact bundled SHA256')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==source['git_blob'],'exact bundled Git blob')
    p=HERE/'inputs';word_bytes=(p/'WORD.json.gz').read_bytes()
    need(sha256(word_bytes).hexdigest()=='2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883','exact selected native word')
    w=json.loads(gzip.decompress(word_bytes));need(w['program'][24472]==['MOVE',415,3,99,False],'actual selected MOVE')
    source=p/'clifford_exact.py';c=types.ModuleType('packed_grid_clifford');sys.modules[c.__name__]=c
    exec(compile(source.read_bytes(),str(source),'exec'),c.__dict__)
    record,compiled=c.lower_child(c.canonical_frame(9,tuple(w['frames'][3])).adjoint().then(c.canonical_frame(9,tuple(w['frames'][99]))))
    need(record['rank']==1 and record['right']['phase']==1 and record['left']['phase']==0,'source rank and absolute phases')
    need(sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='064d51e9c347dbcfd9e172e5b5cab75f96912e0eb9a6f9537d53540cf4780ca9','complete selected recipe')
    seed={0:(Q(1),Q(0)),3:(Q(1),Q(0))};f=2
    entrance=monomial(seed,record['right'],f,c,True)
    need(monomial(entrance,record['right'],f,c)==seed,'actual right inverse/source order')
    first=axis(seed,0);last=axis(first,1);final=monomial(last,record['left'],f,c)
    need(integral(entrance) and integral(final) and not integral(first),'actual whole-MOVE endpoint-only control')
    need(last=={1:(Q(1),Q(0)),2:(Q(1),Q(0))},'independent C tensor endpoint')
    scaled={x:(a*(1<<18),b*(1<<18)) for x,(a,b) in entrance.items()}
    stage=monomial(scaled,record['right'],f,c)
    for j in range(f):stage=axis(stage,j);need(integral(stage),'common-root reserve admits every prefix')
    stage=monomial(stage,record['left'],f,c);need(integral(stage),'complete guarded source endpoint')
    need(max(abs(q) for z in stage.values() for q in z)<1<<(40-1),'selected width signed headroom')
    # Finite corroboration of the closed-form inequalities; the proof uses
    # 178t < D/2, not extrapolation of this bounded scan.
    tested=0
    for D in range(1,5001):
        t=(D-1)//356
        need((D+1)//2+178*t<=D,'fractional width consequence')
        need((D+2)//2+161*t+1<=D+2,'magnitude width consequence');tested+=1
    bridge=[]
    for f,K,rho in [(1,2,0),(2,2,1),(3,3,1)]:
        u=2;z=u+9*f*K;a=z+1;selected=[u+(i*f+j)*K+rho for i in range(9) for j in range(f)]
        suffix=[k for k in range(u,a) if k not in selected];permutation=list(range(u))+selected+suffix
        need(sorted(permutation)==list(range(a)) and len(set(selected))==9*f,'complete spectator-preserving packing bijection')
        b_width=7;r=2;rows=3;P=rows*(1<<u);S=1<<(a-u-9*f)
        old=rows*(1<<a)*6*r*(b_width+1);packed=2*P*(1<<(9*f))*S*r*b_width
        need(Q(old,packed)==Q(3*(b_width+1),b_width),'complete physical payload ratio')
        need(old>packed,'header-only bridge rejected by exact cardinality')
        bridge.append(dict(f=f,K=K,rho=rho,address_bits=a,selected_positions=selected,old_bits=old,packed_bits=packed,ratio=str(Q(old,packed))))
    encode=lambda v:{str(x):list(map(str,z)) for x,z in sorted(v.items())}
    out=dict(status='PASS_SELECTED_MOVE_PACKED_GRID_INTERFACE',base=PIN,selected_word_sha256=sha256(word_bytes).hexdigest(),actual_event=24472,actual_move=w['program'][24472],recipe=record,recipe_sha256=sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest(),endpoint_only_control=dict(complete_native_entrance=encode(entrance),central_first_prefix=encode(first),complete_native_final=encode(final),entrance_integral=integral(entrance),final_integral=integral(final),prefix_integral=integral(first),interpretation='Rejects endpoint-only admission to this literal provider, not the selected guarded root pipeline.'),common_root_scaled_control=dict(root_axes=18,p=0,h=1,F=18,W=40,scale=1<<18,all_prefixes_integral=True),depth_inequality_cases=tested,packing_cases=bridge,scope='Source-bound numerical admission implication conditional on the existing complete-root Clifford/depth premise and a faithful paid packed ABI. No physical packing, whole MOVE, nonleaf tariff, all-column foundation discharge or new kappa.',source_files_verified=len(sources['bundled_inputs']))
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
