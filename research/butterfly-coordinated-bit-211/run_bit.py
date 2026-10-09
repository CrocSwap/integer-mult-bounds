"""Full changed V7 graph/physical/terminal/prime replay, no complex rerun.

Portable changed-only verifier. Complete source/emission hashes accompany every result.
"""
from pathlib import Path
from collections import Counter
import copy, gc, gzip, hashlib, importlib.util, json, resource, signal, sys, time, traceback
assert __debug__
if sys.version_info<(3,11):raise SystemExit('Python 3.11+ required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
from common import check_source, source_pins
ROOT=P=OUT=RESULT=None
START=time.monotonic(); STAGES=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(x):
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x
def write(path,obj):
    with path.open('x') as f:json.dump(encode(obj),f,sort_keys=True,indent=2);f.write('\n')
def write_bytes(path,b):
    with path.open('xb') as f:f.write(b)
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def peak():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024 if sys.platform=='darwin' else 1)
def stage(name,fn):
    print('START '+name,flush=True);t=time.monotonic();v=fn()
    STAGES.append(dict(stage=name,status='PASS',seconds=time.monotonic()-t,peak_rss_kib=peak()))
    print('PASS '+name+' '+str(round(time.monotonic()-t,3))+'s',flush=True);gc.collect();return v
class MemoryFile:
    def __init__(self,b):self.b=b
    def read_text(self):return self.b.decode()
class MemoryDirectory:
    def __init__(self,files):self.files=files
    def __truediv__(self,name):return MemoryFile(self.files[name])
def run(bit_root,output):
    global ROOT,P,OUT,RESULT,START,STAGES
    assert not Path(bit_root).is_symlink() and not Path(output).is_symlink(),'Symlinked root'
    bit_root=Path(bit_root).resolve();ROOT=Path(output).resolve()
    assert ROOT.is_dir() and not ROOT.is_symlink(),'Caller must create a fresh output directory'
    for protected in (bit_root,HERE):assert ROOT!=protected and protected not in ROOT.parents,'Output inside protected input'
    P=bit_root/'research/paired-cube-diagonal-bit-168'
    OUT=ROOT/'effective-bit';RESULT=OUT/'receipt.json'
    assert not OUT.exists(),'Refuse to overwrite effective-bit artifacts'
    check_source(bit_root,'bit')
    pins={'files':source_pins('bit')}
    observed={str(bit_root/name):sha((bit_root/name).read_bytes()) for name in pins['files']}
    assert all(observed[str(bit_root/name)]==want for name,want in pins['files'].items())
    OUT.mkdir();START=time.monotonic();STAGES=[]
    if sys.platform!='darwin':resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(600,600));signal.alarm(900)
    loader=load('v7_frozen_candidate',HERE/'candidate.py')
    loader_hash=sha((HERE/'candidate.py').read_bytes())
    word,emitted,meta=stage('construct_source_bound_effective_candidate',lambda:loader.candidate(bit_root))
    expected={'graph_p12.json':'2bb271df49780365b22b286d9f7166b1fdf3c67ff7d679ba43ca633fc884bdcc','word_p12.json':'ef77a7d30390a21c18ed70a905e1e6c7a07c29439a523da69e3c97ab5ac94356','frames_p12.json':'4e0fce06f07a044e68583d3fe96594b5ad67fe0d19cfd43a97495c57823ae351'}
    assert meta['emitted_sha256']==expected=={k:sha(b) for k,b in emitted.items()}
    assert all(word.phys[a]!=word.phys[b] for a,b,n in word.ops)
    write(OUT/'source-metadata.json',dict(metadata=meta,loader_sha256=loader_hash,upstream_pins=pins,observed_source_pins=observed))
    for name,b in emitted.items():write_bytes(OUT/(name+'.gz'),gzip.compress(b,mtime=0))
    stage('combined_exact_decoder_frames_geometry_and_aliases',word.exact_frames)
    baseline=stage('combined_complete_physical_chains_and_target_chronology',word.row)
    # Admit a new abstract package using its actual recounted node-frame profile.
    memfiles=dict(emitted)
    for n in ('kchron','profile'):memfiles[n+'_p12.json']=(P/'selected/bit'/(n+'_p12.json')).read_bytes()
    def derive_abstract_profile():
        C=word.module.Checker(MemoryDirectory(memfiles),12)
        C.frames();C.decoder();C.geometry();H,Y,src,R=C.chains()
        hist=Counter()
        for part in (H,Y,src):
            for r,n in part.items():
                if r and n:hist[r]+=3*n
        for z in C.w['gauges']:hist[3*z['dim']]+=1
        hist[2]+=2*C.v
        profile=copy.deepcopy(C.prof);m=3*C.h;W=2*C.v+R;mass=sum(r*n for r,n in hist.items())
        assert (R,W,m,W*m-mass)==(18908,22428,72,1936)
        profile.update(child_histogram={str(k):v for k,v in sorted(hist.items())},rank_per_vertex=mass)
        return profile
    abstract=stage('derive_actual_changed_abstract_profile',derive_abstract_profile)
    memfiles['profile_p12.json']=loader.canonical(abstract)
    write_bytes(OUT/'abstract-profile.json',memfiles['profile_p12.json'])
    package=stage('complete_changed_abstract_package_admission',lambda:word.module.Checker(MemoryDirectory(memfiles),12).run())
    package_controls=[]
    for mutation in ('broken_mix','outside_cap','below_level','dropped_star','non_nested'):
        def check(mutation=mutation):
            try:word.module.Checker(MemoryDirectory(memfiles),12,mutate=mutation).run()
            except word.module.Fail as e:return str(e)
            raise AssertionError('Accepted package mutation '+mutation)
        why=stage('package_control_'+mutation,check);package_controls.append(dict(mutation=mutation,rejection=why))
    baseline_formal=[]
    for ring in (2,0):baseline_formal.append(stage('baseline_all_columns_'+('F2' if ring==2 else 'Z'),lambda ring=ring:word.formal(ring)))
    controls=[]
    for mutation in ('omit_compensation','missing_partner','stale'):
        def check(mutation=mutation):
            try:word.formal(2,mutation)
            except ValueError as e:return str(e)
            raise AssertionError('Accepted word mutation '+mutation)
        why=stage('word_control_'+mutation,check);controls.append(dict(mutation=mutation,rejection=why))
    # Degenerate-frame control must fail before any arithmetic is used.
    i=word.changed_frames[0];old=word.opframe[i];word.opframe[i]=word.register([])
    try:
        try:word.exact_frames()
        except ValueError:controls.append(dict(mutation='zero_operation_frame',rejection='REJECTED'))
        else:raise AssertionError('Accepted zero operation frame')
    finally:word.opframe[i]=old
    terminalmod=load('v7_original_terminal',P/'bit/terminal.py')
    selection=json.loads((P/'selected/bit/sinks.json').read_bytes())
    terminal=stage('terminal_complete_F2_signed_Z_columns_and_controls',lambda:terminalmod.prove(word,selection))
    formal=terminal['formal']
    def admit_formal(f):
        assert len(f)==3 and {(x['mode'],x['direction']) for x in f}=={('F2',1),('Z',1),('Z',-1)}
        assert all(x['formal_columns']==20634 and x['source_columns']==1760 and x['target_columns']==1760 and x['dirty_columns']==17114 and x['all_outputs'] and x['all_sources_and_dirty_restored'] and x['partner_mix_unmix_at_original_anchors'] and x['retained_cleanup_literal_reverse'] for x in f)
    admit_formal(formal)
    try:admit_formal(formal[:-1])
    except AssertionError:pass
    else:raise AssertionError('Truncated terminal outcomes admitted')
    assert terminal['literal_sandwich_inverse'] and terminal['all_original_adjoint_responses_retained'] and terminal['original_partner_delivery_anchors_retained']
    assert set(terminal['controls'])=={'omit-write','omit-pre-target','omit-ancestor-response'} and set(terminal['controls'].values())=={'REJECTED'}
    assert terminal['child_delta']=={'3':-102,'21':-102} and terminal['scalar_addition_delta']<=0
    primemod=load('v7_original_prime',P/'bit/prime_witnesses.py')
    prime=stage('all_actual_used_frame_prime_witnesses',lambda:primemod.certificate(word))
    used=set(word.opframe)|set(word.w['source_frame'])|set(word.w['root_frame'])|{word.w['full_frame']}
    used.update(z['frame'] for z in word.w['gauges'])
    for e in word.k['entries']:used.update((e['mix_frame'],e['deliver_frame']))
    def coverage(records):
        seen=set()
        for r in records:
            assert not seen.intersection(r['frame_ids'])
            for f in r['frame_ids']:
                assert f in used and len(word.C.B[f])==r['dimension']
                assert sha(json.dumps(word.C.B[f],separators=(',',':')).encode())==r['basis_sha256']
            seen.update(r['frame_ids'])
            primemod.validate_factor(r['cleared_gram_determinant'],r['small_prime_powers'],r['remaining_factor'])
        assert seen==used
    stage('independent_prime_coverage_and_factor_admission',lambda:coverage(prime['frame_witnesses']))
    try:coverage(prime['frame_witnesses'][:-1])
    except AssertionError:pass
    else:raise AssertionError('Missing prime witness admitted')
    witness_bytes=loader.canonical(prime);witness_gzip=gzip.compress(witness_bytes,mtime=0)
    write_bytes(OUT/'all-used-prime-witnesses.json.gz',witness_gzip)
    check_source(bit_root,'bit')
    for path,want in observed.items():assert sha(Path(path).read_bytes())==want
    for name,want in meta['source_pins'].items():
        kind,rel=name.split('/',1)
        assert kind in ('source','package')
        path=(bit_root if kind=='source' else HERE)/rel
        assert sha(path.read_bytes())==want,('Overlay/source changed during replay',name)
    assert sha((HERE/'candidate.py').read_bytes())==loader_hash
    assert {k:sha(b) for k,b in emitted.items()}==expected
    result=dict(status='PASS source-bound V7 complete changed graph physical columns terminal and primes',source_head=meta['source_head'],metadata=meta,loader_sha256=loader_hash,baseline_profile=baseline,profile=terminal['profile'],terminal_selected=terminal['selected'],package=package,abstract_profile=abstract,package_controls=package_controls,baseline_formal=baseline_formal,word_controls=controls,terminal={k:v for k,v in terminal.items() if k not in ('profile','baseline_profile','selected','seconds','maxrss')},prime_summary={k:v for k,v in prime.items() if k!='frame_witnesses'},prime_witness_path=str((OUT/'all-used-prime-witnesses.json.gz').relative_to(ROOT)),prime_witness_sha256=sha(witness_gzip),prime_canonical_sha256=sha(witness_bytes),prime_provenance_note='Prime helper input_sha256 identifies original source files; metadata.emitted_sha256 identifies the actual generated graph, word and complete frames used in this replay.',missing_prime_record_control_rejected=True,truncated_terminal_control_rejected=True,source_files_unchanged=True,stages=STAGES,seconds=time.monotonic()-START,peak_rss_kib=peak(),fresh_complex_proof_executed=False,remaining='Fresh packing/scalar/bridge arithmetic and independent final review; all-size interfaces remain conditional')
    write(RESULT,result)
    print('RESULT '+json.dumps(dict(status=result['status'],output=str(RESULT),seconds=result['seconds'],peak_rss_kib=result['peak_rss_kib'],prime_used=prime['total_used_frames'],prime_bases=prime['unique_used_bases'],emitted_sha256=expected)),flush=True)
    signal.alarm(0)
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bit-root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True,help='Existing fresh parent output directory')
    args=ap.parse_args()
    try:run(args.bit_root,args.output)
    except BaseException as e:
        print('FAILURE '+json.dumps(dict(error_type=type(e).__name__,error=str(e),stages=STAGES,seconds=time.monotonic()-START,traceback=traceback.format_exc())),flush=True)
        raise
