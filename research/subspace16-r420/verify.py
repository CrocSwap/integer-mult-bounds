"""Cold finite replay of both suppliers, including upstream nomination controls.

The unchanged complex data controller and the inherited all-size and analytic
interfaces remain explicit dependencies. Assertions must remain enabled.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time,shutil
from pathlib import Path

if not __debug__:raise SystemExit('Do not use Python -O')
ROOT=Path(__file__).resolve().parent;V=ROOT/'vendor';P=V/'pr531'
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',required=True,type=Path);ap.add_argument('--cxx',default=os.environ.get('CXX','c++'));ap.add_argument('--boost-include',type=Path,default=Path(os.environ.get('BOOST_INCLUDE','/usr/include')));ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
O=a.work.resolve();assert not O.exists() and not O.is_relative_to(ROOT)
assert (a.boost_include/'boost/multiprecision/cpp_int.hpp').is_file()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def integrity():
    actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json' and '__pycache__' not in p.parts}
    assert actual==read(ROOT/'MANIFEST.json'),'complete package manifest'
    for path,value in read(ROOT/'SOURCES.json')['inherited_files'].items():assert sha(ROOT/path)==value,path
integrity();O.mkdir(parents=True);stages=[];began=time.monotonic()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
    start=time.monotonic();log=O/(name+'.log');print('RUN',name,flush=True)
    with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(ROOT/'code/run.py'),str(script),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
    stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));dump(O/'STAGES.json',stages)
    if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
    print('PASS',name,flush=True)
try:
    run('bit-r420-full-replay-and-interface',ROOT/'code/run_r420.py',ROOT,O/'bit-r420','--cxx',a.cxx,'--boost-include',a.boost_include)
    run('complex-static44-construction-and-controls',V/'static44/replay.py','--out',O/'static44')
    run('complex-548-frame-lifts',V/'pr548/complex-local/code/port_frames.py','--input',O/'static44/FULL-WORD.json.gz','--source',V/'pr548/complex-local/inputs/PR534-WORD.json.gz','--gk',V/'static44/gk','--out',O/'lifted')
    run('complex-548-syndrome',V/'pr548/complex-local/code/apply_syndrome.py','--input',O/'lifted/FULL-WORD.json.gz','--gk',V/'static44/gk','--out',O/'syndrome')
    run('complex-response-slice',ROOT/'code/slice.py',O/'syndrome/FULL-WORD.json.gz',O/'sliced')
    run('complex-subspace16',ROOT/'code/build_frames.py',O/'sliced/FULL-WORD.json.gz',O/'subspace16')
    local=O/'complex-local';base=O/'complex-base';host=O/'complex-hosted';audit=O/'complex-audit';audit.mkdir()
    run('complex-scalar-frame-transport',P/'code/audit_and_transport.py','--raw',O/'subspace16/FULL-WORD.json.gz','--routing',P/'inputs/data-base/split-centres/CANONICAL-WORD.json.gz','--out',local)
    run('complex-emit-local',P/'code/emit_local.py',local)
    run('complex-independent-local',P/'code/audit_local.py',local)
    run('complex-normalized-wrappers',P/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'LEMMA-A.json')
    run('complex-every-local-phase',ROOT/'code/phases_full.py',local,P/'vendor/clifford')
    controller=O/'controller-input';shutil.copytree(P/'inputs/data-base',controller)
    shutil.copyfile(V/'pr548/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz',controller/'split-centres/GLOBAL-TEMPLATE.json.gz')
    shutil.copyfile(V/'pr548/complex-global/vendor531/evidence/local/CANONICAL-WORD.json.gz',controller/'split-centres/CANONICAL-WORD.json.gz')
    run('complex-bind-retained-data',P/'code/prepare_supplier_base.py','--data-base',controller,'--local',local,'--out',base)
    run('complex-emit-whole-owners',P/'code/emit_supplier_hosted.py','--base',base,'--owners',ROOT/'data/OWNERS.json.gz','--plan',ROOT/'data/PLAN.json','--out',host)
    run('complex-independent-owners-and-controls',P/'code/audit_supplier_hosted.py',base,host,audit/'ASYNC-AUDIT.json','--mutation-controls')
    run('complex-finite-invoice',P/'code/invoice_final.py','--base',base,'--hosted',host,'--audit',audit,'--out',audit,'--retained-invoice',P/'inputs/PR523-PREFIX-AND-INVOICE.json')
    run('both-moments-and-outer-assembly',ROOT/'code/assemble.py',ROOT,O/'bit-r420/replay/RESULT9.json',O/'assembly',audit,host)
    assembly=read(O/'assembly/EXACT-ASSEMBLY.json');native=read(O/'bit-r420/replay/cout/columns.json');bit=read(O/'bit-r420/replay/RESULT9.json');bg=read(O/'bit-r420/replay/v9/hosted/AUDIT.json');owner=read(audit/'OWNERS-AND-PROFILE.json');ci=read(audit/'PREFIX-AND-INVOICE.json');phase=read(local/'CLIFFORD-REVIEW.json');controls=read(audit/'ASYNC-AUDIT.json')
    assert phase['all_child_equalities_include_global_phase'] and phase['endpoint_adapters']==224
    assert controls['mutation_controls_run'] and len(controls['mutations_rejected'])==7
    assert len(read(O/'bit-r420/replay/v9/nine/AUDIT.json')['mutations_rejected'])==17 and len(bg['mutations_rejected'])==16
    assert read(O/'bit-r420/replay/xcheck.json')['status']=='PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE'
    assert len(assembly['strict_outer_constraints'])==47 and len(assembly['outer_controls'])==4
    result={k:assembly[k] for k in ('kappa','kappa_decimal','complex_lower','bit_lower','binding_component')}
    result.update(status='PASS_SUBSPACE16_R420_BOTH_SUPPLIERS',bit_local_profile={str(r):n for r,n in native['local_raw_H']},bit_global_profile=bit['bit_profile'],bit_word_sha256=sha(O/'bit-r420/replay/word.json.gz'),bit_template_sha256=bg['template_sha256'],bit_program_sha256=bg['emitted_program_sha256'],bit_payload_prefix_bits=native['payload_prefix_bits'],bit_prefix_bits=bit['bit']['prefix_bits'],bit_charged_prefix_bits=bit['bit']['charged_prefix_bits'],bit_two_level_bits=bit['bit']['two_level_coefficient_bits'],bit_charged_two_level_bits=bit['bit']['charged_two_level_coefficient_bits'],complex_local_profile=read(local/'CANONICAL-WORD.json.gz')['local_profile'],complex_global_profile=owner['paid_profile'],complex_word_sha256=sha(local/'CANONICAL-WORD.json.gz'),complex_program_sha256=sha(local/'LOCAL-PROGRAMS.json.gz'),complex_phase_sha256=sha(local/'CLIFFORD-RECIPES.json'),complex_template_sha256=owner['template_sha256'],complex_live=owner['live'],complex_physical=owner['physical'],complex_deficit=owner['deficit'],complex_helper_roles=owner['hosted_residuals'],complex_prefix_bits=ci['global_prefix_bits'],complex_charged_prefix_bits=ci['charged_prefix_bits'],phase_edges=phase['directed_edges'],endpoint_adapters=phase['endpoint_adapters'])
    for key,value in read(ROOT/'EXPECTED.json').items():assert result[key]==value,(key,result.get(key),value)
    integrity();result.update(seconds=time.monotonic()-began,python=sys.version,manifest_sha256=sha(ROOT/'MANIFEST.json'),scope=assembly['scope']);dump(O/'RESULT.json',result)
    paths=['RESULT.json','bit-r420/DRIVER.json','bit-r420/replay/xcheck.json','bit-r420/replay/mutants.json','bit-r420/replay/cout/columns.json','bit-r420/replay/cout/columns_k4.json','bit-r420/replay/cout/columns_k5.json','bit-r420/replay/cout/legality.json','bit-r420/replay/v9/hosted/AUDIT.json','bit-r420/replay/RESULT9.json','bit-r420/replay/RESULT11.json','static44/SCALAR-AUDIT.json','sliced/RESULT.json','subspace16/RESULT.json','complex-local/INDEPENDENT-LOCAL-REPLAY.json','complex-local/CLIFFORD-REVIEW.json','complex-local/LEMMA-A.json','complex-audit/ASYNC-AUDIT.json','complex-audit/OWNERS-AND-PROFILE.json','complex-audit/PREFIX-AND-INVOICE.json','assembly/EXACT-ASSEMBLY.json']
    dump(O/'RECEIPT.json',dict(status=result['status'],stages=stages,artifacts={p:sha(O/p) for p in paths},manifest_sha256=sha(ROOT/'MANIFEST.json')))
    print(result['status'],result['kappa_decimal'],result['seconds'],flush=True)
except BaseException as e:
    dump(O/'FAILURE.json',dict(error=repr(e),stages=stages));raise
