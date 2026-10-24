"""Proof checker for a two-change helper interface on the frozen PR4610 word.

Native synthesis/replay conventions derive from Cinna Davis PR4470 and PR4610
warp-interface-20261022 (4b4c75bc0fd64d3eee54029e8d2fab834251fca6).
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse,gzip,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
P={1:2202,2:414,3:505,4:134,5:36,8:8}
H={4:28,7:8,8:47,9:325}
PREDECESSOR='4b4c75bc0fd64d3eee54029e8d2fab834251fca6'
def need(v,s):
    if not v:raise ValueError(s)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def span(b):
    s={0}
    for x in b:s|={y^x for y in list(s)}
    return s
def synth(c,word):
    current=c['start'][:];out=[];spaces=list(map(span,c['frames']))
    def move(r,f):
        old=current[r]
        if old==f:return
        need(spaces[old]<spaces[f],f'Nested paid edge {r}:{old}->{f}')
        out.append(['climb','warp_retimed',r,old,f,len(c['frames'][f])-len(c['frames'][old])]);current[r]=f
    for e in word:
        if e[0]=='climb':continue
        if e[0]=='scalar':
            g=e[1];refs=g[1:3] if g[0] in ('add','copy') else g[1:2]
            for typ,r in refs:
                if typ=='L':move(r,e[2])
        elif e[0]=='warp':move(e[1][1],e[3]);current[e[1][1]]=e[4]
        out.append(deepcopy(e))
    for r,f in enumerate(c['final']):move(r,f)
    return out
def regenerate(payload):
    c=deepcopy(payload['canonical']);words=deepcopy(payload['programs'])
    need(len(c['start'])==632 and c['start'][621]==0,'Exact independent helper entrance')
    label=len(c['frames']);c['frames'].append([30,429]);c['start'][621]=label
    expected={'forward':['add',['L',514],['L',621],-2,1],'backward':['add',['L',621],['L',514],2,1]}
    for dr,w in words.items():
        need(w[12704]==['scalar',expected[dr],0],'Pinned first contact in both orientations');w[12704][2]=label
    words={dr:synth(c,w) for dr,w in words.items()}
    need(c['start'][:224]==payload['canonical']['start'][:224] and c['final']==payload['canonical']['final'],'Public endpoints and all final charts fixed')
    for dr,w in words.items():
        old=payload['programs'][dr]
        need([e[1] for e in w if e[0]=='scalar']==[e[1] for e in old if e[0]=='scalar'],'Scalar word unchanged')
        need([e for e in w if e[0] in ('warp','center','adapter','residual_adapter')]==[e for e in old if e[0] in ('warp','center','adapter','residual_adapter')],'Warps, owned queries and external adapters unchanged')
        counts=Counter(e[5] for e in w if e[0]=='climb');counts.update(e[4] for e in w if e[0]=='center');need(counts==P,'Regenerated paid census')
    return c,words

def verify(root):
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row.get('usage')=='provenance':continue
        path=(HERE/row['path']) if row.get('scope')=='package' else root/row['path']
        need(sha256(path.read_bytes()).hexdigest()==row['sha256'],'Authenticated source '+str(path))
    # No inherited executable is loaded before every declared input is authenticated.
    need(sha256((HERE/'predecessor/ACTUAL-WORD.json.gz').read_bytes()).hexdigest()=='d578875344095047c383ef513e69b9deb9d99d2b75abe14f7359d06365a924ac','Frozen PR4610 payload')
    raw=gzip.decompress((HERE/'predecessor/ACTUAL-WORD.json.gz').read_bytes());payload=json.loads(raw);c,words=regenerate(payload)
    V=load(root/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','helper621_rows')
    X=load(root/'research/kappa-rebuild/complex/native_extensions.py','helper621_literal')
    checks={}
    for dr,w in words.items():
        print('NATIVE',dr,flush=True);rows,rec=X.literal_replay(V,c,w,dr=='backward')
        need(all(rows['L',r]==V.expected(('L',r),[],dr=='backward',False) for r in range(632)),'All 632 independent endpoints')
        cc=deepcopy(c);cc['local_profile']=P;cc['R']=408;rec['second_literal']=V.replay(w,cc,[],dr=='backward',False)
        need({int(k):v for k,v in rec['paid_profile'].items()}==P,'Fresh complete invoice')
        need(rec['real_scalar_allowance']==(158120 if dr=='forward' else 158168),'Scalar allowance')
        need(str(rec['max_formal_prefix_l1'])==('457' if dr=='forward' else '169'),'Prefix bound');checks[dr]=rec
    ce=load(root/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','helper621_clifford')
    prune=load(root/'research/kappa-function-composition/complex/prune_native.py','helper621_prune')
    fc={}
    def frame(i):
        if i not in fc:fc[i]=ce.canonical_frame(9,c['frames'][i])
        return fc[i]
    def lower(op,rank):
        records={}
        for dr in ('forward','backward'):
            actual=prune.conjugate(ce,op) if dr=='backward' else op
            rec=X.N.lower_exact(prune,ce,actual);need(rec['rank']==rank,'Exact absolute-phase lowered rank');records[dr]=rec
        return records
    pairs=sorted({(e[3],e[4],e[5]) for w in words.values() for e in w if e[0]=='climb'}|{(e[2],e[3],e[4]) for w in words.values() for e in w if e[0]=='center'})
    paid=[]
    for index,(a,b,r) in enumerate(pairs):
        paid.append({'from':a,'to':b,'rank':r,'recipes':lower(frame(a).adjoint().then(frame(b)),r)})
        if index%250==0:print('PAID_PHASE_PROGRESS',index+1,len(pairs),flush=True)
    print('PAID_PHASES',len(paid),flush=True)
    witness=next(x for x in paid if x['rank']>0);rec=deepcopy(witness['recipes']['forward']);rec['left']['phase']=(rec['left']['phase']+1)%4
    decoded=prune.monomial(ce,rec['right'],9).then(ce.fourier(9,range(rec['rank']))).then(prune.monomial(ce,rec['left'],9));actual=frame(witness['from']).adjoint().then(frame(witness['to']))
    need(decoded.tab==actual.tab and decoded.zero_state()!=actual.zero_state(),'Wrong absolute phase rejected')
    sys.path.insert(0,str(root/'research/native-warp-extraction-boundary'))
    operators=load(root/'research/native-warp-extraction-boundary/operators.py','helper621_columns');K={};columns=[]
    for wr in c['warps']:
        cols=wr['G_columns'];G=ce.transpose(tuple(cols),9);tr=ce.transpose(ce.inv(G,9),9)
        quadratic=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(tr)) for i,a in enumerate(tr))
        K[wr['op']]=ce.perm(9,G).then(ce.diag(9,quadratic))
        aa=operators.monomial(cols);need(aa==operators.direct_columns(cols),'Independent exact 512-column G phase formulas')
        rec=X.N.lower_exact(prune,ce,K[wr['op']]);need(rec['rank']==0,'Logical warp monomial')
        rr=rec['left'];decoded=[]
        for x in range(512):
            q=rr['phase']+sum(rr['linear_Z4'][i]*(x>>i&1) for i in range(9))+2*sum((rr['quadratic_rows'][j]>>i&1)*(x>>i&1)*(x>>j&1) for i in range(9) for j in range(i+1,9))
            decoded.append((ce.mv(tuple(rr['matrix_rows']),x)^rr['offset'],q%4))
        need(decoded==aa,'Exact serialized logical warp phase');columns.append(wr['op'])
    warps=[]
    for op,a,b in sorted({(e[2],e[3],e[4]) for w in words.values() for e in w if e[0]=='warp'}):
        body=K[abs(op)] if op>0 else K[abs(op)].adjoint();warps.append({'op':op,'from':a,'to':b,'recipes':lower(frame(a).adjoint().then(body).then(frame(b)),0)})
    helpers=[];hh=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];op=frame(a).adjoint().then(frame(b));rank=ce.rank([x for x,z,p in op.tab[9:]])
        need(rank>0,'Independent productive helper');hh[rank]+=1;helpers.append({'role':r,'from':a,'to':b,'rank':rank,'recipes':lower(op,rank)})
    def check_helpers(claim):need(dict(hh)==claim,'Actual relative helper rank census')
    check_helpers(H)
    helper621=next(x for x in helpers if x['role']==621);need(helper621['rank']==7,'Helper621 exact relative rank7')
    bad=deepcopy(words['forward']);idx=next(i for i,e in enumerate(bad) if e[0]=='warp');bad[idx][3]=1
    try:X.literal_replay(V,c,bad,False)
    except ValueError:pass
    else:raise ValueError('Wrong warp frame mutation accepted')
    badc=deepcopy(c);badc['local_profile']={1:2201,2:412,3:506,4:135,5:36,8:8};badc['R']=408
    try:V.replay(words['forward'],badc,[],False,False)
    except ValueError as err:need('paid profile' in str(err),'Wrong profile reaches invoice check')
    else:raise ValueError('Old paid profile accepted')
    try:check_helpers({4:28,7:7,8:47,9:326})
    except ValueError:pass
    else:raise ValueError('Old helper credit accepted')
    data=(json.dumps({'canonical':c,'programs':words},sort_keys=True,separators=(',',':'))+'\n').encode()
    return {'status':'PASS_HELPER621_NATIVE_AND_ABSOLUTE_PHASE','predecessor_head':PREDECESSOR,'predecessor_payload_sha256':sha256(raw).hexdigest(),'candidate_payload_sha256':sha256(data).hexdigest(),'paid':P,'helpers':H,'native':checks,'phase_checks':{'paid':paid,'warps':warps,'helpers':helpers,'logical_operators_all_512_columns':columns},'controls':['wrong_warp_frame','old_paid_profile','old_helper_credit','wrong_absolute_phase'],'scope':'Native provider proof only. Whole target matching, numerical compiler and scalar stock admission are separate registered gates.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=HERE.parents[1]);ap.add_argument('--write',action='store_true');args=ap.parse_args();result=verify(args.root)
    path=HERE/'NATIVE-RESULT.json.gz';data=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    if args.write:path.write_bytes(gzip.compress(data,mtime=0))
    else:need(json.loads(gzip.decompress(path.read_bytes()))==json.loads(data),'Stored native receipt equals fresh verification')
    print(result['status'])
if __name__=='__main__':main()
