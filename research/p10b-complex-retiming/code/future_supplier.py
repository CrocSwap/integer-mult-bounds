"""Source-bound adapter for a freshly replayed portable complex supplier.

Caller must first invoke package/verify.py into a fresh external proof directory.
This function binds that run, verifies immutable package bytes and candidate,
then independently recertifies both rational moments. It does not admit a bit
word or itself establish an outer kappa. Prepared with OpenAI Codex assistance.
Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json

MANIFEST='dce8987eca4c22b3b7fb0bc4e2f1c21851fdfc73f8b7757f4c27f2442b677837'
CANDIDATE='ea52d07910dca90871c2cd928894f491e305fa10edabd2f220cb45f0648e61a5'
COARSE=Q(772881996923825,10**18)
COARSE_NO_FALLBACK=Q(772882000348983,10**18)
STAGES=['split-and-single-retiming','component-retiming','neutral-down-retiming','neutral-up-retiming','complete-supplier-admission']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def supplier(cost,other,package,proof):
    package=Path(package).resolve();proof=Path(proof).resolve()
    assert not proof.is_relative_to(package) and not (proof/'FAILURE.json').exists()
    assert sha(package/'MANIFEST.json')==MANIFEST
    files={}
    for p in package.rglob('*'):
        assert not p.is_symlink(),'symlink in package'
        if p.is_file() and p!=package/'MANIFEST.json':files[p.relative_to(package).as_posix()]=sha(p)
    assert files==read(package/'MANIFEST.json')['files'],'Changed, missing or unpinned supplier source'
    pins=read(package/'SOURCE.json');v=read(proof/'VERIFICATION.json');c=read(proof/'candidate/SUPPLIER-CHECK.json')
    assert v['status']=='PASS_PORTABLE_COMPLEX_NEUTRAL_FRAME_RETIMING_SUPPLIER'
    assert v['inputs_unchanged'] and v['manifest_sha256']==MANIFEST and v['kappa_claim'] is False
    assert [s['stage'] for s in v['fresh_stages']]==STAGES
    assert v['candidate_sha256']==pins['candidate_sha256']==CANDIDATE==sha(proof/'candidate/candidate.json')
    assert v['supplier_receipt_sha256']==sha(proof/'candidate/SUPPLIER-CHECK.json')
    assert Q(v['complex_coarse'])==Q(pins['complex_coarse'])==COARSE
    assert Q(pins['complex_coarse_without_fallback'])==COARSE_NO_FALLBACK
    assert c['status']=='PASS_RESEARCH_COMPLEX_SUPPLIER_FRAME_RETIMING'
    assert c['candidate_sha256']==CANDIDATE and c['unchanged_scalar_program'] and c['unchanged_scatter_ports_endpoints']
    assert c['source_sha256']==pins['source_uncompressed_sha256']
    assert c['gx_check']['status']=='PASS_COMPLEX_PROGRAM_GX_CHECK1_SCALAR_AND_GXCORE_MIRROR'
    assert c['gx_check']['certificate_sha256']==CANDIDATE
    assert len(c['gx_check']['controls'])==2 and len(c['mutation_controls'])==14
    guard=c['finite_guard'];assert guard['status']=='PASS_FRESH_EXACT_COMPLEX_GUARD'
    assert guard['m']==110 and guard['live_per_vertex']==14316 and guard['retained_row_coefficient']==20161
    assert set(c['reflected_splices'])=={'forward','backward'}
    assert [c['scalar_bill'][o]['totals']['real_component_primitive_steps'] for o in ('forward','backward')]==[1735572,1789788]
    word=read(proof/'candidate/candidate.json');CH=Counter()
    for block in word['blocks'].values():CH.update({int(r):5*n for r,n in block.items()})
    h,vv,R=word['h'],word['v'],word['R'];m,W=5*h,4*vv+R
    for r in (2*h-2,h-1,2*h+2,4):CH[r]+=2*vv
    assert (m,W)==(110,14316) and CH==Counter({int(r):n for r,n in c['ledger']['histogram'].items()})
    assert sum(CH.values())==c['ledger']['calls']==351655 and sum(r*n for r,n in CH.items())==c['ledger']['rank_mass']==1571680
    profile=dict(m=m,W=W,histogram=dict(CH),calls=sum(CH.values()),rank_mass=sum(r*n for r,n in CH.items()),deficit=m*W-sum(r*n for r,n in CH.items()),maxchild=max(CH))
    assert profile['deficit']==c['ledger']['deficit']==3080 and profile['maxchild']==46
    result={};grid=Q(1,10**18)
    for fallback,b in [(True,COARSE),(False,COARSE_NO_FALLBACK)]:
        label='with_fallback' if fallback else 'without_fallback';assert Q(c['roots'][label]['b'])==b
        root=cost.certify(dict(CH),m,W,fallback);assert Q(int(Q(root['lower'])*10**18),10**18)==b
        cm=cost.moment(dict(CH),m,W,b,fallback);nextcm=cost.moment(dict(CH),m,W,b+grid,fallback);assert cm[1]<1<nextcm[0]
        lower,upper=other.moment(m,W,list(CH.items()),b);nlower,nupper=other.moment(m,W,list(CH.items()),b+grid)
        if fallback:
            total=32*m*m*sum(CH.values());bl,bu=other.moment(m,W,[(1,total)],b);nbl,nbu=other.moment(m,W,[(1,total)],b+grid)
            lower+=Q(1,10**16)*bl;upper+=Q(1,10**16)*bu;nlower+=Q(1,10**16)*nbl;nupper+=Q(1,10**16)*nbu
        assert upper<1<nlower
        result[label]=dict(b=b,moment_interval=cm,next_grid_excluded=nextcm,independent_moment_interval=(lower,upper),independent_next_grid=(nlower,nupper))
    b=result['with_fallback'];b0=result['without_fallback'];assert b['b']<b0['b']
    binding=dict(manifest_sha256=MANIFEST,candidate_sha256=CANDIDATE,receipt_hashes={n:sha(proof/n) for n in ('VERIFICATION.json','candidate/SUPPLIER-CHECK.json','candidate/candidate.json')},adapter_sha256=sha(__file__),inputs_unchanged=True,all_supplier_stages_fresh=True)
    return dict(profile=profile,coarse=b['b'],moment_interval=b['moment_interval'],next_grid_excluded=b['next_grid_excluded'],coarse_without_fallback=b0['b'],moment_interval_without_fallback=b0['moment_interval'],source_program_sha256=CANDIDATE,finite_guard=guard,roots=result,source_binding=binding,scope='Complex supplier only. Caller must admit the bit supplier and freshly assemble the combined kappa. The frozen supplier receipt binding-side note describes its historical source context.')
