"""Preserve the full PR1035 independent audit with exact modular determinants.

After research/p112-signed-modular-production/, the live independent.py ships
the modular path. This opt-in package vendors pairwise Fraction-only bytes in
baseline.py and still proves engine.py against that reference.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,itertools,json,statistics,time,types
from fractions import Fraction

P=Path(__file__).resolve().parent;ROOT=P.parents[1]
OLD='research/p112-free-sink-audit97/'
BASE='ba82555c64e1879e4b7decce28186f208fcb8262'
FILES={OLD+x for x in ('verify.py','CERTIFICATE.json','SOURCES.json','BASE-SELECTED.json','README.md','PROOF.md','test_package.py')}
BASELINE=P/'baseline.py'
PRODUCTION=ROOT/(OLD+'independent.py')
PAIRWISE_SHA256='46806efe1ee7744c810a69981d471b42dfceaa336fee226991c55ba1edfd129f'

def need(ok,msg):
    if not ok:raise ValueError(msg)

def load_independent(name, source_bytes):
    """Load independent source with HERE bound to the live sink package."""
    module=types.ModuleType(name)
    module.__file__=str(PRODUCTION)
    exec(compile(source_bytes, str(PRODUCTION), 'exec', optimize=0), module.__dict__)
    return module

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def canon(x):
    return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'),allow_nan=False)

def digest(b):return hashlib.sha256(b).hexdigest()

def prepare():
    sources=json.loads((P/'SOURCES.json').read_bytes())
    need(sources['base_commit']==BASE and set(sources['files'])==FILES,'source inventory')
    for path,h in sources['files'].items():
        need(digest((ROOT/path).read_bytes().replace(b'\r\n',b'\n'))==h,'source pin: '+path)
    need(digest((P/'BASE-SELECTED.json').read_bytes().replace(b'\r\n',b'\n'))==sources['selected_snapshot_sha256'],'selected snapshot')
    baseline_meta=sources['independent_baseline']
    need(baseline_meta['path']=='research/p112-signed-modular86/baseline.py','baseline path')
    need(digest(BASELINE.read_bytes().replace(b'\r\n',b'\n'))==baseline_meta['sha256']==PAIRWISE_SHA256,'baseline pin')
    need(sources['live_independent_provenance']['pairwise_sha256']==PAIRWISE_SHA256,'provenance pairwise digest')
    # Reference engine is always the vendored Fraction-only baseline.
    original=load_independent('sink_independent86', BASELINE.read_bytes())
    original.source.checked_sources()
    engine=module('signed_modular86',P/'engine.py')
    certificate=json.loads((ROOT/(OLD+'CERTIFICATE.json')).read_bytes())
    return original,engine,certificate

def execute(original,engine,certificate,mode):
    old=original.fraction_determinant
    stats={'fast':0,'fallback':0}
    def candidate(rows):
        stats['fast' if engine.eligible(rows) else 'fallback']+=1
        return engine.determinant(rows,old)
    if mode=='candidate':original.fraction_determinant=candidate
    try:return original.audit(certificate),stats
    finally:original.fraction_determinant=old

def run():
    original,e,c=prepare();reference=original.fraction_determinant
    lines,_=original.source.geometry();signed=[]
    for m in c['minors']:
        rows=[[lines[i][j] for j in m['columns']] for i in m['rows']]
        need(e.eligible(rows),'every frozen minor enters checked bound')
        a=reference(rows);b=e.determinant(rows,reference)
        need(a==b==m['determinant'],'full signed determinant agreement')
        signed.append([m['rows'],m['columns'],b])
    result,stats=execute(original,e,c,'candidate')
    baseline,_=execute(original,e,c,'reference')
    need(result==baseline and stats=={'fast':4030,'fallback':0},'complete audit equality')
    # Production live path must match the same audit receipt when present.
    if PRODUCTION.exists():
        live_bytes = PRODUCTION.read_bytes()
        need(digest(live_bytes) == 'c77cf3dd1234c26cfb7df2d356752721e8b1b37169f20543678fe2f4d07a53f8',
             'live production source pin')
        live=load_independent('sink_independent_live', live_bytes)
        live_result=live.audit(c)
        need(live_result==result,'live production audit must match opt-in candidate')
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name)
        else:raise ValueError('accepted control: '+name)
    for name,change in (
        ('wrong signed determinant',lambda x:x['minors'][0].__setitem__('determinant',-x['minors'][0]['determinant'])),
        ('missing minor',lambda x:x['minors'].pop()),
        ('duplicate minor',lambda x:x['minors'].append(copy.deepcopy(x['minors'][0]))),
        ('Boolean determinant',lambda x:x['minors'][0].__setitem__('determinant',True)),
        ('missing pattern',lambda x:x['patterns'].pop()),
        ('false free count',lambda x:x.__setitem__('free_alternatives',1))):
        bad=copy.deepcopy(c);change(bad)
        reject(name,lambda:execute(original,e,bad,'candidate'))
    reject('insufficient modulus',lambda:e.recover(256,257,256))
    reject('invalid residue',lambda:e.recover(521,521,256))
    reject('violated determinant bound',lambda:e.recover(257,521,256))
    boundary=[[2*int(i==j) for j in range(8)] for i in range(8)]
    need(e.determinant(boundary,reference)==256,'positive Hadamard boundary')
    boundary[0],boundary[1]=boundary[1],boundary[0]
    need(e.determinant(boundary,reference)==-256,'negative Hadamard boundary')
    need(e.determinant([[1,1],[1,1]],reference)==0,'singular exact zero')
    fallback_cases=[[[521]],[[3]],[[int(i==j) for j in range(9)] for i in range(9)],[[Fraction(1,2),0],[0,2]]]
    for rows in fallback_cases:
        need(not e.eligible(rows),'fallback fixture outside fast envelope')
        need(e.determinant(rows,reference)==reference(rows),'exact fallback')
    tested=0
    for n in (1,2,3):
        for flat in itertools.product((-1,0,1),repeat=n*n):
            rows=[flat[i*n:(i+1)*n] for i in range(n)]
            need(e.determinant(rows,reference)==reference(rows),'exhaustive signed matrix')
            tested+=1
    return {'base_commit':BASE,'complete_audit':result,'dispatch':stats,'exact_minors':len(signed),
            'signed_minor_stream_sha256':digest(canon(signed).encode()),'small_signed_matrices':tested,
            'fallback_cases':4,'controls_rejected':controls,'hadamard_bound':256,'prime':521,
            'scope':'Exact signed determinant replacement inside the pinned independent audit; all28560case and4030minor obligations retained; no new mathematical exclusion or kappa.'}

def benchmark(repeats=3):
    original,e,c=prepare();samples={'reference':[],'candidate':[]};expected=None
    for repeat in range(repeats):
        for mode in (('reference','candidate') if repeat%2==0 else ('candidate','reference')):
            start=time.perf_counter();result,_=execute(original,e,c,mode);elapsed=time.perf_counter()-start
            if expected is None:expected=result
            need(result==expected,'benchmark output differs')
            samples[mode].append(elapsed)
    med={k:statistics.median(v) for k,v in samples.items()}
    return {'repeats':repeats,'samples_seconds':samples,'median_seconds':med,
            'median_speedup':med['reference']/med['candidate'],'same_input':expected,
            'scope':'Paired full audit() calls after source loading against vendored Fraction baseline; includes geometry, code coverage and all exact minors/cases; excludes interpreter startup, source hashing, package controls and certificate serialization. Local timing only.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--write-certificate',action='store_true');p.add_argument('--benchmark',action='store_true');args=p.parse_args()
    if args.benchmark:
        print(json.dumps(benchmark(),indent=2));return
    result=run();path=P/'EXPECTED.json'
    if args.write_certificate:
        need(not path.exists(),'certificate exists');path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    else:need(canon(result)==canon(json.loads(path.read_bytes())),'complete receipt mismatch')
    print('PASS_P112_SIGNED_MODULAR cases=28560 minors=4030 signed_matrices=19767 controls=9')

if __name__=='__main__':main()
