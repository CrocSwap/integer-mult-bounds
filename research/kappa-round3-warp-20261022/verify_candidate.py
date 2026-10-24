"""Fresh exact replay of new joint helper/native-map discovery, no solver trust."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
from warp_merge import J,F


def load(path):return json.loads(gzip.decompress(path.read_bytes()))


def inputs():
    pins=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    for row in pins['files']:
        F.need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Authenticated predecessor '+row['path'])
    frozen=json.loads((HERE/'ACTUAL-WORD-FREEZE.json').read_text(encoding='utf-8'));raw=(HERE/'ACTUAL-WORD.json.gz').read_bytes()
    F.need(sha256(raw).hexdigest()==frozen['compressed_sha256'] and sha256(gzip.decompress(raw)).hexdigest()==frozen['canonical_payload_sha256'],'Frozen complete actual word')
    new=json.loads(gzip.decompress(raw));base,old,*_=J.construct();c=new['canonical']
    F.need(c['frames'][:len(base['frames'])]==base['frames'],'Inherited actual frame registry prefix')
    edges=lambda word:{(e[3],e[4]) for e in word if e[0]=='climb'}
    warps=lambda word:{(e[2],e[3],e[4]) for e in word if e[0]=='warp'}
    F.need(edges(new['programs']['forward'])==edges(new['programs']['backward']),'Identical paid pair sets in both orientations')
    F.need(warps(new['programs']['forward'])==warps(new['programs']['backward']),'Identical transported warp classes in both orientations')
    return c,new['programs'],base,old


def main():
    started=time.monotonic();inputs();new=load(HERE/'ACTUAL-WORD.json.gz');old=load(ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz')
    c=new['canonical'];programs=new['programs'];base=old['canonical'];original=old['programs']
    V=F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','round3_rows')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','round3_literal')
    F.need(c['start'][:224]==base['start'][:224] and c['final'][:224]==base['final'][:224],'Complete main endpoint interfaces unchanged')
    H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r]
        F.need(F.span(c['frames'][a])<F.span(c['frames'][b]),'Strict arbitrary-input helper')
        H[len(c['frames'][b])-len(c['frames'][a])]+=1
    profiles={};checks={}
    for d,p in programs.items():
        print('CHECK',d,flush=True)
        F.need([e[1] for e in p if e[0]=='scalar']==[e[1] for e in original[d] if e[0]=='scalar'],'Unchanged scalar opcodes, coefficients and order')
        F.need([(e[1],e[2]) for e in p if e[0]=='warp']==[(e[1],e[2]) for e in original[d] if e[0]=='warp'],'Unchanged logical warp identities and order')
        F.need([e for e in p if e[0] in ('center','adapter','residual_adapter')]==[e for e in original[d] if e[0] in ('center','adapter','residual_adapter')],'Owned jobs/adapters unchanged')
        rows,rec=X.literal_replay(V,c,p,d=='backward')
        F.need(all(rows['L',r]==V.expected(('L',r),[],d=='backward',False) for r in range(632)),'All632 arbitrary persistent endpoints')
        profiles[d]=Counter({int(k):v for k,v in rec['paid_profile'].items()})
        rebound=deepcopy(c);rebound['R']=len(c['start'])-2*c['v'];rebound['local_profile']=dict(profiles[d])
        rec['second_literal']=V.replay(p,rebound,[],d=='backward',False)
        checks[d]=rec
        print('PASS',d,dict(profiles[d]),flush=True)
    F.need(profiles['forward']==profiles['backward'],'Equal complete dual invoices')
    controls=[]
    bad=deepcopy(programs['forward']);next(e for e in bad if e[0]=='climb')[5]+=1
    try:X.literal_replay(V,c,bad,False)
    except (ValueError,AssertionError) as err:controls.append({'name':'wrong_paid_rank','rejected':str(err)})
    else:raise ValueError('Incorrect emitted paid rank was accepted')
    result={'status':'PASS_JOINT_HELPER_MAPS_NATIVE_BOTH_632_INTERPRETERS','helpers':dict(H),'paid':dict(profiles['forward']),'native':checks,'controls':controls,
            'actual_word_canonical_sha256':sha256(gzip.decompress((HERE/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest(),
            'verifier_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-started}
    (HERE/'NATIVE-VALIDATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='native'},sort_keys=True))


if __name__=='__main__':main()

