"""Independent retained-profile moment audit; no producer/verifier imports.
Inputs: raw native strict ASSEMBLY, nominated refinement SPEC and B.json.
Native complex_profile is read directly; live/dimension are bound to immutable parent SPEC. The supplied
600-digit rational is only a proposed point: acceptance derives moment bounds.
"""
import argparse,hashlib,json,math
from pathlib import Path
from fractions import Fraction as F

def require(condition,message):
    if not condition:raise ValueError(message)
def pointer(obj,p):
    if p=='':return obj
    require(p.startswith('/'),'JSON pointer must start /')
    for key in p[1:].split('/'):
        key=key.replace('~1','/').replace('~0','~');obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj
ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--assembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
args.spec=args.package/'refinement/new/SPEC.json';args.b_json=args.package/'refinement/outer/B.json';parent_spec=args.package/'parent/new/SPEC.json';claim_file=args.package/'refinement/outer/OUTER-CLAIM.json'
S=json.loads(args.spec.read_text());B=json.loads(args.b_json.read_text());A=json.loads(args.assembly.read_text());P=json.loads(parent_spec.read_text());C=json.loads(claim_file.read_text())
require(A['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY','actual native assembly status')
profile={int(k):v for k,v in S['expected']['global_profile'].items()};actual={int(k):v for k,v in A['complex_profile'].items()};W=S['expected']['live'];m=S['geometry']['dimension'];b=F(B['b']);endpoint=F(S['expected']['complex_lower']);gap=F(1,10**500)
require(all(type(v) is int and v>=0 for v in actual.values()),'native profile must contain exact nonnegative integers');require(type(W) is int and type(m) is int,'integral native geometry');require(actual==profile=={int(k):v for k,v in B['profile'].items()}=={int(k):v for k,v in P['expected']['global_profile'].items()},'native/parent/spec/B profile mismatch');require(P['expected']['live']==W==B['live'],'parent/spec/B live mismatch');require(P['geometry']['dimension']==m and (m,W)==(73,66304),'unexpected retained geometry');require(b==endpoint-gap,'wrong endpoint backoff');require(all(0<r<=m for r in profile),'rank outside source geometry')
q=b-gap;epsilon=1-2*gap;derived_kappa=F((epsilon*q*10**600).__floor__(),10**600)-F(1,10**550)
require(derived_kappa==F(C['rational'])==F(C['kappa']),'independent main-row rational/decimal mismatch')
G=10**650
ceildiv=lambda n,d:-((-n)//d)
def unitlog(x):
    z=(x-1)/(x+1);N=700;lo=hi=0
    zn,zd=z.numerator,z.denominator
    for j in range(N):
        num=2*pow(zn,2*j+1)*G;den=(2*j+1)*pow(zd,2*j+1)
        lo+=num//den;hi+=ceildiv(num,den)
    tail=2*z**(2*N+1)/((2*N+1)*(1-z*z))
    hi+=ceildiv(tail.numerator*G,tail.denominator)
    return lo,hi
l2=unitlog(F(2))
def logbounds(x):
    k=0
    while x>=2:x/=2;k+=1
    l,h=unitlog(x);return l+k*l2[0],h+k*l2[1]
logs={rank:logbounds(F(m,rank)) for rank in profile}
def exbounds(xlo,xhi):
    if not 0<=xlo<=xhi<G:raise ValueError('exponential range')
    low=high=G;termlo=termhi=G;N=200
    for j in range(1,N):
        termlo=termlo*xlo//(G*j);termhi=ceildiv(termhi*xhi,G*j)
        low+=termlo;high+=termhi
    termnext=ceildiv(termhi*xhi,G*N)
    high+=ceildiv(termnext*G*(N+1),G*(N+1)-xhi)
    return low,high
def moment(v,P):
    low=high=F(0)
    for rank,count in P.items():
        l,h=logs[rank];xl=v.numerator*l//v.denominator;xh=ceildiv(v.numerator*h,v.denominator)
        el,eh=exbounds(xl,xh);w=F(count*rank,m*W)
        low+=w*el/G;high+=w*eh/G
    return low,high
valid=moment(b,profile);require(valid[1]<1,'candidate native moment failed')
large=moment(endpoint+gap,profile);require(large[0]>1,'above-root control failed')
bad=dict(profile);bad[48]+=1;corrupt=moment(b,bad);require(corrupt[0]>1,'one-count rank48 mutation failed')
require(F(float(b))!=b,'floating corruption control failed')
require(json.loads(json.dumps({'n':10**600+1}))['n']==10**600+1,'large-integer roundtrip failed')
result={'status':'PASS_INDEPENDENT_ACTUAL_PROFILE_ENCLOSURE','kappa':str(derived_kappa),'scope':'Retained actual native ASSEMBLY profile bound to parent/refinement SPEC/B, independent directed fixed-point enclosures only. Driver owns full native/source/owner binding. No inference of complete all-size proof. Proposed600-digit endpoint not trusted as certified.','moment_at_b':[str(x) for x in valid],'margin':str(1-valid[1]),'above_root_moment':[str(x) for x in large],'one_count_mutation_moment':[str(x) for x in corrupt],'parameters':{'grid':str(G),'log_terms':700,'exp_terms':200},'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.spec,args.b_json,args.assembly,parent_spec,claim_file,Path(__file__)]}}
args.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
