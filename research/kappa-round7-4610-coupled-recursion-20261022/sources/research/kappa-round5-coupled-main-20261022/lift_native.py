"""A source-bound 120-channel unimodular extension of native clean-J.

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
No independent Gaussian main-job or improved kappa claim is made.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def mm(a, b):
    out = []
    for row in a:
        d = {}
        for k, c in row.items():
            for j, v in b[k].items():
                d[j] = d.get(j, Q(0))+c*v
        out.append({j:v for j,v in d.items() if v})
    return out


def matrices(geo):
    R = geo['R']
    B = [{k:row.get(i,Q(0))/2 for k,row in enumerate(R) if row.get(i,0)} for i in range(112)]
    C = [{i:v/2 for i,v in row.items()} for row in R]
    S = [dict(row) for row in geo['J']]
    for i in range(112):
        S[i].update({112+k:-v for k,v in B[i].items()})
    S += [{**row,112+k:Q(1)} for k,row in enumerate(C)]
    inv = [{i:Q(1),**{112+k:v for k,v in B[i].items()}} for i in range(112)]
    inv += [{**{i:-v for i,v in row.items()},112+k:Q(-13)} for k,row in enumerate(C)]
    I = [{i:Q(1)} for i in range(120)]
    assert mm(S,inv)==mm(inv,S)==I
    return B,C,S,inv


def add(dst,src,q,frame):
    return ['scalar',['add',['L',dst],['L',src],q.numerator,q.denominator],frame]


def adapter(main,aux,B,C,frame,inverse=False):
    out = [['phase','unimodular_lift_inverse' if inverse else 'unimodular_lift']]
    def lower(sign):
        for k,row in enumerate(C):
            for i,q in sorted(row.items()):out.append(add(aux[k],main[i],sign*q,frame))
    def upper(sign):
        for i,row in enumerate(B):
            for k,q in sorted(row.items()):out.append(add(main[i],aux[k],sign*q,frame))
    if inverse:upper(1);lower(-1)
    else:lower(1);upper(-1)
    return out


def construct(c,base,B,C,Z,W):
    source = list(range(112))+Z
    target = list(range(112,224))+W
    extended,wrapped = {},{}
    for d,program in base.items():
        pre = [['phase','lift_cross_zero']]
        post = [['phase','lift_cross_full']]
        if d=='forward':
            for i,row in enumerate(B):
                for k,q in sorted(row.items()):pre.append(add(112+i,Z[k],-q,0))
            for k,row in enumerate(C):
                for i,q in sorted(row.items()):post.append(add(W[k],i,q,1))
                post.append(add(W[k],Z[k],Q(1),1))
        else:
            for k,row in enumerate(C):
                for i,q in sorted(row.items()):pre.append(add(Z[k],112+i,-q,0))
                pre.append(add(Z[k],W[k],Q(-1),0))
            for i,row in enumerate(B):
                for k,q in sorted(row.items()):post.append(add(i,W[k],q,1))
        extended[d] = pre+deepcopy(program)+post
        inv = d=='backward'
        wrapped[d] = adapter(list(range(112,224)),W,B,C,0,inv)+extended[d]+adapter(list(range(112)),Z,B,C,1,inv)
    return source,target,extended,wrapped


def expected(V,role,source,target,S,inverse,d,wrapped):
    if role[0]!='L':return {}
    i=role[1]
    if i not in source and i not in target:return V.identity(role)
    out={}
    in_source=i in source
    k=(source if in_source else target).index(i)
    if not wrapped:
        V.add(out,V.identity(role),Q(1))
        if (d=='forward' and not in_source) or (d=='backward' and in_source):
            other=source if d=='forward' else target
            for j,q in S[k].items():V.add(out,V.identity(('L',other[j])),q if d=='forward' else -q)
    else:
        M=inverse if d=='backward' else S
        own=source if in_source else target
        for j,q in M[k].items():V.add(out,V.identity(('L',own[j])),q)
        if (d=='forward' and not in_source) or (d=='backward' and in_source):
            other=source if d=='forward' else target
            for j,q in M[k].items():V.add(out,V.identity(('L',other[j])),q if d=='forward' else -q)
    return out


def replay(V,N,c,program,wanted,d):
    rows={('L',r):V.identity(('L',r)) for r in range(632)}
    current=c['start'][:]
    spaces=[V.span(f) for f in c['frames']]
    profile=Counter();scalar=0;maxl1=Q(1)
    for i,e in enumerate(program):
        kind=e[0]
        if kind=='scalar':
            g,f=e[1:];r=g[1][1]
            assert g[1][0]=='L' and current[r]==f
            scalar+=N.primitive_allowance(g)
            if g[0]=='add':
                s=g[2][1];assert g[2][0]=='L' and current[s]==f and r!=s
                V.add(rows['L',r],rows['L',s],Q(g[3],g[4]))
            else:
                assert g[0]=='scale';q=Q(g[2],g[3]);rows['L',r]={k:q*v for k,v in rows['L',r].items()}
            maxl1=max(maxl1,sum(map(abs,rows['L',r].values()),Q(0)))
        elif kind=='warp':
            _,r,op,a,b=e;r=r[1];assert current[r]==a
            rows['L',r]=V.warp(rows['L',r],op,d=='backward');current[r]=b
        elif kind=='climb':
            _,part,r,a,b,rank=e;assert current[r]==a and spaces[a]<spaces[b]
            assert rank==len(c['frames'][b])-len(c['frames'][a]);current[r]=b;profile[rank]+=1
        else:assert kind in ['phase','adapter','residual_adapter']
    assert current==c['final']
    assert all(rows['L',r]==wanted(('L',r)) for r in range(632))
    return dict(paid_profile=dict(sorted(profile.items())),paid_rank_mass=sum(k*v for k,v in profile.items()),
                scalar_allowance=scalar,max_formal_row_l1=str(maxl1),arbitrary_inputs=632,
                scalar_contact_frames_checked=True,owned_fields=0)


def main():
    began=time.monotonic()
    N=load(ROOT/'research/kappa-rebuild/complex/rebuild_native.py','lift_rebuild')
    # Authenticate the exact used input set. The legacy receipt's packet path
    # is absent in this sparse checkout; this source-identical retained packet
    # has the SHA recorded by the legacy verifier, without restoring old files.
    assert N.digest(N.P_PATH)==N.P_SHA and N.digest(N.BASE/'RESULT.json')==N.RECEIPT_SHA
    P=load(N.P_PATH,'lift_prune')
    assert N.digest(P.CHECKER)==P.CHECKER_SHA
    V=load(P.CHECKER,'lift_retained_verifier')
    packet=ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/certificate.json.gz'
    assert N.digest(packet)=='a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7'
    receipt=read(N.BASE/'RESULT.json')
    for filename,pin in receipt['providers']['THREE-base']['artifacts'].items():assert N.digest(N.BASE/filename)==pin
    geo=N.geometry(packet)
    tag='THREE-base';c=read(N.BASE/(tag+'-CANONICAL.json.gz'));base=read(N.BASE/(tag+'-NATIVE-WORD.json.gz'))
    cold=[r for r in range(224,632) if c['start'][r]==0 and c['final'][r]==1]
    assert len(cold)==213
    Z,W=cold[:8],cold[8:16]
    B,C,S,inv=matrices(geo)
    source,target,extended,wrapped=construct(c,base,B,C,Z,W)
    checks={}
    oldexpected=V.expected
    for name,words in [('extended',extended),('wrapped',wrapped)]:
        checks[name]={}
        for d,program in words.items():
            oracle=lambda role:expected(V,role,source,target,S,inv,d,name=='wrapped')
            rec=replay(V,N,c,program,oracle,d)
            # Retain the separately implemented source-bound operation interpreter,
            # supplying only the explicitly changed endpoint oracle in memory.
            V.expected=lambda role,R,back,clean:oracle(role)
            try:rec['retained_operation_replay']=V.replay(program,c,[],d=='backward',False)
            finally:V.expected=oldexpected
            checks[name][d]=rec
            print('PASS_NATIVE_LIFT',name,d,rec['scalar_allowance'],flush=True)
    profiles=[v[d]['paid_profile'] for v in checks.values() for d in v]
    assert all(p==profiles[0] for p in profiles)
    helper=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,632) if r not in Z+W)
    paid=profiles[0];paidmass=sum(int(k)*v for k,v in paid.items());hmass=sum(k*v for k,v in helper.items())
    assert 112*16+16*9+hmass==paidmass
    payload=dict(canonical=c,source_roles=source,target_roles=target,extended=extended,wrapped=wrapped)
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode();(HERE/'LIFTED-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    pins={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'research/kappa-rebuild/complex/rebuild_native.py',Path(P.__file__),Path(V.__file__),packet,N.BASE/'RESULT.json',N.BASE/(tag+'-CANONICAL.json.gz'),N.BASE/(tag+'-NATIVE-WORD.json.gz')]}
    result=dict(status='PASS_EXACT_NATIVE_120_CHANNEL_DYADIC_LIFT',new_kappa=False,source_sha256=pins,
                source_auxiliaries=Z,target_auxiliaries=W,remaining_independent_helpers=dict(helper),remaining_helper_mass=hmass,
                paid=paid,paid_rank_mass=paidmass,checks=checks,
                matrix_identities=dict(CB='14I8',J='I-BC',S='U(-B)L(C)',S_inverse='L(-C)U(B)',detS=1,
                                       detJ='(-13)^8, not a dyadic unit',both_120_by_120_products_verified=True),
                optimistic_main_mass_unconverted=112*16+16*9,optimistic_local_deficit_unconverted=0,
                ordinary_port_conversion_paid_H1=16,ordinary_port_conversion_target_mass_lost=16,
                optimistic_local_deficit_converted=32,
                word_payload_sha256=sha256(raw).hexdigest(),seconds=time.monotonic()-began,
                scope='All632 scalar/warp arbitrary-input endpoints and frame contacts in both orientations, with a retained operation replay using the changed endpoint oracle. New operations are only dyadic ADDs at ZERO/FULL; paid/warp/adapters are inherited. Global owner charts, independent Gaussian main-job credit, encoded-batch closure, precision and kappa are not established.')
    (HERE/'NATIVE-LIFT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],paidmass,hmass,round(result['seconds'],3),flush=True)


if __name__=='__main__':main()
