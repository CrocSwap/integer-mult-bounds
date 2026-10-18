"""Supplement the pinned cold replay with semantic and final cross-binding.

The native witnesses are reused only after verify.py's original complete
source/capsule binding. Owner/template generation and geometry controls are
rerun. Immutable supplier inputs are never edited or repinned.
"""
from pathlib import Path
import argparse, copy, gzip, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
EXTERNAL=HERE/'external'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    path=Path(path);blob=path.read_bytes()
    return json.loads(gzip.decompress(blob)if path.suffix=='.gz'else blob)
def need(ok,message):
    if not ok:raise RuntimeError(message)
def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')



def bind_geometry_inputs(pinned_spec,runtime_spec,engine_files,assembly):
    need(sha(runtime_spec)==sha(pinned_spec),'geometry runtime SPEC differs from pinned source')
    for name,path in engine_files.items():
        need(sha(path)==assembly['input_sha256']['engines/'+name+'.py'],
             'geometry engine differs from bound assembly: '+name)
    return {runtime_spec:sha(runtime_spec),**{path:sha(path)for path in engine_files.values()}}


def validate(package,source,run,work):
    package,source,run,work=map(lambda p:Path(p).resolve(),(package,source,run,work))
    need(not work.exists(),'fresh scratch directory required')
    work.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='500000')
    for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):
        env.pop(key,None)
    # The retained exact engines cache derived rational enclosures. Copy
    # that cache into scratch; immutable sources and run evidence stay put.
    if (run/'fine-cache').is_dir():
        shutil.copytree(run/'fine-cache',work/'fine-cache')
    env['FINE_ENGINE_CACHE']=str(work/'fine-cache')
    scripts=package/'review20261014/external/o1-admission'
    pins=read(package/'review20261014/external/SOURCE-PINS.json')
    for rec in pins['files']:
        p=package/'review20261014/external'/rec['path']
        need(sha(p)==rec['sha256'],'external source drift: '+rec['path'])
    stages=[]
    def call(name,script,*args,expect=0):
        cp=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],
                          cwd=work,env=env,text=True,capture_output=True,timeout=1200)
        (work/(name+'.log')).write_text(cp.stdout+cp.stderr)
        need(cp.returncode==expect,name+' failed: '+(cp.stdout+cp.stderr)[-3000:])
        stages.append({'name':name,'exit_code':cp.returncode,'expected_exit_code':expect})
        print('PASS',name,flush=True)
    strict=run/'strict';base=run/'native-new-base/local';extra=run/'native-new-extra/local'
    before={p:sha(p)for p in [source/'MANIFEST.json',run/'RESULT.json',
            strict/'global/audit/OWNERS-AND-PROFILE.json',
            strict/'global/audit/PREFIX-AND-INVOICE.json',
            strict/'global/audit/ASYNC-AUDIT.json']}
    need(read(run/'RESULT.json')['native_reuse']=={'base':False,'extra':False},
         'the selected evidence is not the documented cold run')
    args=[strict,run/'GEOMETRY-CONTROLS.json',base,extra,'0.001676855229071321']
    final=work/'FINAL-BINDING.json'
    call('independent-final-binding',scripts/'t74_final_binding.py',*args,final)
    fb=read(final)
    need(fb['status']=='PASS_T74_T16_PARITY_FINAL_BINDING'and all(fb['checks'].values()),'final binding failed')
    call('swapped-native-control',scripts/'t74_final_binding.py',strict,
         run/'GEOMETRY-CONTROLS.json',extra,base,'0.001676855229071321',
         work/'SWAPPED-NATIVE.json',expect=1)
    call('nonimproving-rate-control',scripts/'t74_final_binding.py',strict,
         run/'GEOMETRY-CONTROLS.json',base,extra,'0.1',
         work/'NONIMPROVING-RATE.json',expect=1)
    # Freshly regenerate every geometric artifact instead of re-hashing
    # only historical outputs. The two permitted PLAN differences must
    # still bind their actual container; every mathematical field agrees.
    owners,parent=work/'owners',work/'parent'
    call('regenerate-owners',source/'reconstruct.py','--out',owners)
    call('regenerate-parent',source/'lift_parent.py','--owners',owners,'--out',parent)
    call('independent-semantic-regeneration',scripts/'t74_semantic_regen.py',
         source,owners,parent,work/'SEMANTIC.json')
    semantic=read(work/'SEMANTIC.json')
    need(semantic['status']=='PASS_T74_SEMANTIC_REGENERATED_ARTIFACTS','semantic regeneration failed')
    # Deliberately use a different gzip compressor level, not just byte9.
    # Re-run the parent's actual generator to bind its new container hash.
    path=owners/'OWNERS.json.gz';payload=gzip.decompress(path.read_bytes())
    old=path.read_bytes();changed=gzip.compress(payload,compresslevel=1,mtime=137)
    need(old!=changed and gzip.decompress(changed)==payload,'compression control is inert')
    path.write_bytes(changed)
    alternate=work/'parent-recompressed'
    call('regenerate-parent-after-recompression',source/'lift_parent.py','--owners',owners,'--out',alternate)
    call('gzip-container-control',scripts/'t74_semantic_regen.py',source,owners,alternate,
         work/'SEMANTIC-RECOMPRESSED.json')
    recompressed=read(work/'SEMANTIC-RECOMPRESSED.json')
    need(recompressed['status']=='PASS_T74_SEMANTIC_REGENERATED_ARTIFACTS'and
         not recompressed['container_bytes_all_equal'],'semantic check rejected harmless recompression')
    roles=json.loads(payload);roles[0]['time']+=1
    path.write_bytes(gzip.compress(json.dumps(roles,separators=(',',':')).encode(),mtime=0))
    call('changed-role-control',scripts/'t74_semantic_regen.py',source,owners,alternate,
         work/'SEMANTIC-CHANGED-ROLE.json',expect=1)
    # Re-run the actual geometry mutations, recording exactly which
    # source/owner/invoice/assembly bytes they consumed.
    src=run/'parent/layout/joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold'
    runtime_spec=strict/'runtime/data/SPEC.json'
    assembly=read(strict/'ASSEMBLY.json')
    engine_files={name:src/'engines'/(name+'.py')for name in ('moment','base_two_moment','outer')}
    geometry_inputs=bind_geometry_inputs(source/'new/SPEC.json',runtime_spec,engine_files,assembly)
    badspec=work/'changed-SPEC.json';altered=read(runtime_spec);altered['invalid_review_control']=True
    write(badspec,altered)
    badengine=work/'changed-moment.py';badengine.write_bytes(engine_files['moment'].read_bytes()+b'\n# changed-source control\n')
    for name,specfile,engines in [
            ('changed_geometry_SPEC',badspec,engine_files),
            ('changed_geometry_engine',runtime_spec,{**engine_files,'moment':badengine})]:
        try:bind_geometry_inputs(source/'new/SPEC.json',specfile,engines,assembly)
        except RuntimeError:pass
        else:raise RuntimeError('accepted '+name)
        stages.append({'name':name,'status':'REJECTED_BY_INPUT_BINDING'})
        print('PASS',name,flush=True)
    geometry=work/'GEOMETRY-CONTROLS.json'
    call('fresh-geometry-controls',source/'geometry_controls.py','--source',src,'--strict',strict,'--out',geometry)
    geo=read(geometry)
    need(geo['status']=='PASS_T74_GEOMETRY_AND_CHARGE_CONTROLS'and len(geo['rejected'])==6,'geometry controls incomplete')
    aud=read(strict/'global/audit/ASYNC-AUDIT.json')
    mutations=aud['mutations_rejected'];nproviders=len(aud['provider_counts'])
    need(aud['mutation_controls_run']is True and len(mutations)==len(set(mutations))==7+8*nproviders==23,
         'actual controller mutations incomplete')
    inputs={'native_source_manifest':source/'MANIFEST.json','controller':strict/'global/audit/ASYNC-AUDIT.json',
            'owner':strict/'global/audit/OWNERS-AND-PROFILE.json',
            'invoice':strict/'global/audit/PREFIX-AND-INVOICE.json','assembly':strict/'ASSEMBLY.json',
            'geometry_generator':source/'geometry_controls.py','mixed_assembler':source/'code/assemble.py',
            'outer_ledger':package/'frontier_fusion/FRONTIER-FUSION-ARITHMETIC.json',
            'geometry_runtime_spec':runtime_spec,
            **{'geometry_engine_'+name:path for name,path in engine_files.items()}}
    need(all(sha(p)==digest for p,digest in {**before,**geometry_inputs}.items()),
         'validation changed a pinned source or completed run')
    return {'status':'PASS_PR1673_PINNED_T74_SEMANTIC_AND_FINAL_ADMISSION_SUPPLEMENT',
            'native_source_commit':'f852af5e178ce035cd46181a29d9330bcbcaa206',
            'external_reviewer':{'repository':pins['repository'],'commit':pins['commit'],
                                 'scripts_reused':['t74_final_binding.py','t74_semantic_regen.py']},
            'native_replay_mode':'Existing complete cold run, unmodified and source/capsule bound; not rerun here.',
            'new_work':'Fresh owner/template regeneration, whole-receipt final binding, '
                       'recompression and semantic rejection controls, geometry mutations.',
            'final_binding_checks':fb['checks'],'semantic_checks':semantic['checks'],
            'semantic_recompressed_checks':recompressed['checks'],
            'regenerated_semantic_hashes':{name:rec['semantic_sha256']for name,rec in semantic['files'].items()},
            'controller_controls_actual':23,'controller_count_formula':'7+8*2',
            'historical_controller_15_label_is_incorrect':True,
            'geometry_controls':geo,'geometry_runtime_spec_and_engines_bound':True,
            'geometry_discovery_environment_cleared':True,'input_sha256':{k:sha(p)for k,p in inputs.items()},
            'stages':stages,'controls_rejected':['swapped_native_directories','nonimproving_rate','changed_owner_role',
                                 'changed_geometry_SPEC','changed_geometry_engine'],
            'harmless_recompression_accepted':True,
            'scope':'Finite admission evidence for exactly the pinned PR1661 supplier '
                    'used by PR1673. No new native word or exponent; inherited '
                    'all-size/common-frame/mutable-source/hosting/precision/tape/'
                    'recovery/analytic hypotheses remain. The external T37 regression '
                    'is separate cited evidence, not a new local regression run.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-source',type=Path,required=True)
    parser.add_argument('--native-work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    need(not args.output.resolve().is_relative_to(PACKAGE),'output must be outside the package')
    spec=importlib.util.spec_from_file_location('published_package_verifier',PACKAGE/'verify.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    verifier.check_inputs(PACKAGE)
    cold=verifier.cold_binding(PACKAGE,args.native_source,args.native_work)
    with tempfile.TemporaryDirectory(prefix='phase-fusion-admission-review-')as td:
        result=validate(PACKAGE,args.native_source,args.native_work,Path(td)/'work')
    result['cold_source_binding_status']=cold['status']
    write(args.output,result)
    print(result['status'],len(result['final_binding_checks']),'final checks',
          result['controller_controls_actual'],'controller controls')


if __name__=='__main__':main()
