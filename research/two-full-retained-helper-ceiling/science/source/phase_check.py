"""Exact absolute phase admission of all changed maps, transports and helpers."""
from pathlib import Path
import gzip,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
from warp_merge import F


def main():
    started=time.monotonic()
    read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
    new=read(HERE/'ACTUAL-WORD.json.gz');old=read(ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz');c=new['canonical'];base=old['canonical']
    oldverify=F.load(ROOT/'research/warp-interface-20261022/verify_candidate.py','round3_phase_predecessor')
    result=oldverify.phases(c,new['programs'],base,old['programs'])
    result.pop('helpers_unchanged_phase_reused',None)
    ce=F.load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','round3_helper_clifford')
    P=F.load(ROOT/'research/kappa-function-composition/complex/prune_native.py','round3_helper_decode')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','round3_helper_lower')
    pairs={}
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r]
        if (a,b)!=(base['start'][r],base['final'][r]):pairs.setdefault((a,b),[]).append(r)
    helpers=[]
    for (a,b),rs in sorted(pairs.items()):
        op=ce.canonical_frame(9,c['frames'][a]).adjoint().then(ce.canonical_frame(9,c['frames'][b]));rank=len(c['frames'][b])-len(c['frames'][a]);directions={}
        for d in ('forward','backward'):
            actual=P.conjugate(ce,op) if d=='backward' else op
            rec=X.N.lower_exact(P,ce,actual);F.need(rec['rank']==rank,'Each changed arbitrary helper Fourier rank and absolute phase');directions[d]=rec
        helpers.append({'input':a,'output':b,'rank':rank,'helpers':rs,'recipes':directions})
    result['changed_helper_boundaries']=helpers
    result['status']='PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES'
    result['seconds']=time.monotonic()-started
    from hashlib import sha256
    result['actual_word_canonical_sha256']=sha256(gzip.decompress((HERE/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest()
    result['source_manifest_sha256']=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest()
    result['verifier_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE/'PHASE-VALIDATION.json.gz').write_bytes(gzip.compress((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),mtime=0))
    print(result['status'],'changed_helpers',sum(len(h['helpers']) for h in helpers),'seconds',result['seconds'],flush=True)


if __name__=='__main__':main()
