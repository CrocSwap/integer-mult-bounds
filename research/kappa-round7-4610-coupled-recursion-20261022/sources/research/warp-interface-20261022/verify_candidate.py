"""Fresh native/absolute-phase admission of the frozen changed-G candidate."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import argparse,gzip,json,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from warp_merge import J,F


def read(path):
    b=path.read_bytes();return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)


def inputs():
    pins=read(HERE/'SOURCES.json')
    for row in pins['files']:F.need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Authenticated inherited input '+row['path'])
    frozen=read(HERE/'ACTUAL-WORD-FREEZE.json');b=(HERE/'ACTUAL-WORD.json.gz').read_bytes()
    F.need(sha256(b).hexdigest()==frozen['compressed_sha256'] and sha256(gzip.decompress(b)).hexdigest()==frozen['canonical_payload_sha256'],'Frozen actual word payload')
    for name,h in frozen['discovery_sha256'].items():F.need(sha256((HERE/name).read_bytes()).hexdigest()==h,'Frozen discovery source '+name)
    payload=json.loads(gzip.decompress(b));base,old,*_=J.construct();c=payload['canonical']
    F.need(c['frames'][:len(base['frames'])]==base['frames'],'Exact inherited frame-registry prefix; old IDs preserve actual bases')
    edge=lambda p:{(e[3],e[4]) for e in p if e[0]=='climb'}
    warp=lambda p:{(e[2],e[3],e[4]) for e in p if e[0]=='warp'}
    F.need(edge(payload['programs']['forward'])==edge(payload['programs']['backward']),'Same complete paid-pair set across actual orientations')
    F.need(warp(payload['programs']['forward'])==warp(payload['programs']['backward']),'Same complete warp-pair set across actual orientations')
    return c,payload['programs'],base,old


def native(c,programs,base,old):
    started=time.monotonic();V=F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','warp_admission_rows')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','warp_admission_literal')
    need=F.need;checks={}
    expected={1:2201,2:412,3:506,4:135,5:36,8:8}
    need(c['start']==base['start'] and c['final']==base['final'] and c['ports']==base['ports'],'Unchanged complete external main/helper interfaces')
    H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];need(F.span(c['frames'][a])<F.span(c['frames'][b]),'Strict arbitrary-input helper')
        H[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(H=={4:28,7:7,8:47,9:326},'Entire unchanged productive helper census')
    for d,p in programs.items():
        print('CHECK_NATIVE_632',d,flush=True)
        need([e[1] for e in p if e[0]=='scalar']==[e[1] for e in old[d] if e[0]=='scalar'],'Every original scalar opcode/order/coefficient retained')
        need([(e[1],e[2]) for e in p if e[0]=='warp']==[(e[1],e[2]) for e in old[d] if e[0]=='warp'],'Every original logical warp identity/order retained')
        need([e for e in p if e[0] in ('center','adapter','residual_adapter')]==[e for e in old[d] if e[0] in ('center','adapter','residual_adapter')],'Owned jobs and endpoint adapters retained')
        rows,rec=X.literal_replay(V,c,p,d=='backward')
        need(all(rows['L',r]==V.expected(('L',r),[],d=='backward',False) for r in range(632)),'Every arbitrary persistent endpoint')
        rebound=deepcopy(c);rebound['local_profile']=expected;rebound['R']=len(c['start'])-2*c['v']
        rec['second_literal']=V.replay(p,rebound,[],d=='backward',False)
        need({int(k):v for k,v in rec['paid_profile'].items()}==expected,'Fresh complete new paid profile')
        need(rec['real_scalar_allowance']==(158168 if d=='backward' else 158120),'Unchanged complete scalar allowance')
        checks[d]=rec;print('PASS_NATIVE_632',d,rec['real_scalar_allowance'],rec['max_formal_prefix_l1'],flush=True)
    controls=[]
    bad=deepcopy(programs['forward']);index=next(i for i,e in enumerate(bad) if e[0]=='warp');bad[index][3]=1
    try:X.literal_replay(V,c,bad,False)
    except ValueError as error:controls.append({'name':'wrong_warp_source_frame','rejected':str(error)})
    else:raise ValueError('Wrong warp source accepted')
    badc=deepcopy(c);badc['R']=len(c['start'])-2*c['v'];badc['local_profile']={1:2237,2:388,3:494,4:147,5:36,8:8}
    try:V.replay(programs['forward'],badc,[],False,False)
    except ValueError as error:
        need('paid profile' in str(error),'Old profile control reaches complete invoice');controls.append({'name':'old_paid_profile_at_new_word','rejected':str(error)})
    else:raise ValueError('Old paid profile accepted')
    return {'status':'PASS_CHANGED_G_NATIVE_BOTH_632_COLUMN_INTERPRETERS','helpers':dict(H),'paid':expected,'native':checks,'controls':controls,'seconds':time.monotonic()-started}


def phases(c,programs,base,old):
    started=time.monotonic();need=F.need
    ce=F.load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','warp_changed_clifford')
    P=F.load(ROOT/'research/kappa-function-composition/complex/prune_native.py','warp_changed_decode')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','warp_changed_lower')
    framecache={}
    def frame(i):
        if i not in framecache:framecache[i]=ce.canonical_frame(9,c['frames'][i])
        return framecache[i]
    def Kop(cols):
        G=ce.transpose(tuple(cols),9);gi=ce.inv(G,9);tr=ce.transpose(gi,9)
        quadratic=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(tr)) for i,a in enumerate(tr))
        return ce.perm(9,G).then(ce.diag(9,quadratic))
    oldG={w['op']:w['G_columns'] for w in base['warps']};newG={w['op']:w['G_columns'] for w in c['warps']}
    need(set(oldG)==set(newG)==set(range(1,73)),'Complete exact new operator table')
    changed=[op for op in newG if oldG[op]!=newG[op]]
    # Independently evaluate the exact native phases on all 512 columns by two
    # retained pure-integer formulas, then compare with the serialized K recipe.
    sys.path.insert(0,str(ROOT/'research/native-warp-extraction-boundary'))
    operators=F.load(ROOT/'research/native-warp-extraction-boundary/operators.py','warp_native_independent_columns')
    K={};native_columns=[]
    def recipe_columns(rec):
        out=[]
        for x in range(512):
            q=sum(rec['linear_Z4'][i]*(x>>i&1) for i in range(9))+2*sum((rec['quadratic_rows'][j]>>i&1)*(x>>i&1)*(x>>j&1) for i in range(9) for j in range(i+1,9))+rec['phase']
            y=ce.mv(tuple(rec['matrix_rows']),x)^rec['offset'];out.append((y,q%4))
        return out
    for op,cols in sorted(newG.items()):
        K[op]=Kop(cols)
        if op in changed:
            a,b=operators.monomial(cols),operators.direct_columns(cols);need(a==b,'Two exact native 512-column phase formulas')
            rec=X.N.lower_exact(P,ce,K[op]);need(rec['rank']==0 and recipe_columns(rec['left'])==a,'Serialized new K_G equals every exact native column')
            native_columns.append({'operator':op,'G_columns':cols,'all_512_columns_and_absolute_phases':True,'recipe':rec})
    print('PASS_NEW_G_512_COLUMNS',len(changed),flush=True)
    warpclasses=sorted({(e[2],e[3],e[4]) for e in programs['forward'] if e[0]=='warp'})
    warp_receipts=[]
    for i,(op,a,b) in enumerate(warpclasses):
        body=K[abs(op)] if op>0 else K[abs(op)].adjoint();physical=frame(a).adjoint().then(body).then(frame(b));directions={}
        for direction in ('forward','backward'):
            actual=P.conjugate(ce,physical) if direction=='backward' else physical
            rec=X.N.lower_exact(P,ce,actual);need(rec['rank']==0 and rec['right'] is None,'Every actual frame-bound native warp is monomial')
            directions[direction]=rec
        warp_receipts.append({'operator':op,'input':a,'output':b,'G_columns':newG[abs(op)],'recipes':directions})
        if i%30==0:print('PASS_WARP_PHASE_CLASSES',i+1,'/',len(warpclasses),flush=True)
    edges=lambda p:{(e[3],e[4]) for e in p if e[0]=='climb'}
    extra=sorted(edges(programs['forward'])-edges(old['forward']));paid=[]
    for i,(a,b) in enumerate(extra):
        physical=frame(a).adjoint().then(frame(b));rank=len(c['frames'][b])-len(c['frames'][a]);directions={}
        for direction in ('forward','backward'):
            actual=P.conjugate(ce,physical) if direction=='backward' else physical
            rec=X.N.lower_exact(P,ce,actual);need(rec['rank']==rank,'Every new paid frame edge exact Fourier rank')
            directions[direction]=rec
        paid.append({'input':a,'output':b,'rank':rank,'recipes':directions})
        if i%25==0:print('PASS_NEW_PAID_PHASE_PAIRS',i+1,'/',len(extra),flush=True)
    # A valid but altered invertible map must fail the selected rank-zero
    # transported-frame contract; do not use a singular-matrix syntax mutant.
    wrong=None
    for op,a,b in warpclasses:
        if op<0 or op not in changed or not 0<len(c['frames'][a])<9:continue
        for u in range(9):
            for v in range(9):
                if u==v:continue
                cols=newG[op][:];cols[u]^=cols[v]
                physical=frame(a).adjoint().then(Kop(cols)).then(frame(b));rec,_=ce.lower_child(physical)
                if rec['rank']>0:wrong={'name':'wrong_invertible_G_column','operator':op,'column':u,'xor_column':v,'unexpected_paid_rank':rec['rank']};break
            if wrong:break
        if wrong:break
    need(wrong is not None,'Meaningful wrong-G monomial-contract control')
    bad=deepcopy(paid[0]);bad['recipes']['forward']['left']['phase']=(bad['recipes']['forward']['left']['phase']+1)%4
    ref=paid[0];physical=frame(ref['input']).adjoint().then(frame(ref['output']));rec=bad['recipes']['forward'];decoded=P.monomial(ce,rec['right'],9).then(ce.fourier(9,range(rec['rank']))).then(P.monomial(ce,rec['left'],9))
    need(decoded.tab==physical.tab and decoded.zero_state()!=physical.zero_state(),'Wrong paid absolute phase is semantically rejected')
    return {'status':'PASS_ALL_ACTUAL_WARP_AND_NEW_PAID_ABSOLUTE_PHASES','changed_G_operators':changed,'native_operator_columns':native_columns,
            'actual_warp_classes':warp_receipts,'new_paid_pairs':paid,'helpers_unchanged_phase_reused':True,'main_endpoint_adapters_unchanged':True,
            'controls':[wrong,{'name':'wrong_paid_absolute_phase','same_tableau_but_wrong_global_phase':True}],
            'inherited_frame_prefix_exact':True,'both_actual_orientation_pairsets_equal':True,
            'source_manifest_sha256':sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(),
            'actual_word_canonical_sha256':sha256(gzip.decompress((HERE/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest(),
            'verifier_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-started}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--part',choices=['native','phases'],required=True);args=ap.parse_args();c,programs,base,old=inputs()
    out=native(c,programs,base,old) if args.part=='native' else phases(c,programs,base,old)
    name='NATIVE-VALIDATION.json' if args.part=='native' else 'PHASE-VALIDATION.json.gz'
    data=(json.dumps(out,indent=2,sort_keys=True)+'\n').encode()
    (HERE/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
    print(out['status'],out['seconds'],flush=True)
