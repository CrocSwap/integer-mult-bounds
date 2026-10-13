"""Alter actual replay files in a private copy and require binding rejection.

Run after a completed verify.py replay. Original replay/source files stay
read-only. Controls do not claim authentication of execution history.
"""
import argparse,copy,gzip,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
from common import ROOT,P,read
import final_binding as F

if not __debug__:
    raise RuntimeError('Assertions must remain enabled; do not use Python -O')

def projection(work,destination):
    """Copy only the inputs needed by the three targeted binding components."""
    paths=['ADAPTATIONS.json','CONSTRUCTION-CHECK.json','lift/PLAN.json',
           'strict/global/PLAN.json','strict/global/BINDING.json']
    paths+=['strict/global/audit/'+n for n in ('OWNERS-AND-PROFILE.json','ASYNC-AUDIT.json','PREFIX-AND-INVOICE.json','IDLE-REMAINDER-FRAMES.json')]
    summary=read(work/'strict/global/hosted/HOSTED.json')
    paths+=['strict/global/base/'+n for n in summary['source_artifacts']]
    for relative in paths:
        source=work/relative;target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    for relative in ('adapted','runtime/code','runtime/inputs','strict/global/hosted'):
        shutil.copytree(work/relative,destination/relative,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))

def mutations(work,sandbox):
    projection(work,sandbox)
    F.check_adaptations(sandbox);F.check_construction(sandbox);F.check_payload_artifacts(sandbox)
    rejected=[]
    def changed_json(path,change):
        value=read(path);change(value);data=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
        return gzip.compress(data,mtime=0) if path.suffix=='.gz' else data
    def trial(name,changes,check):
        saved={p:p.read_bytes() if p.exists() else None for p in changes}
        try:
            for path,data in changes.items():path.write_bytes(data)
            try:check(sandbox)
            except (AssertionError,ValueError) as exc:rejected.append(dict(name=name,reason=str(exc)))
            else:raise RuntimeError('Accepted altered file: '+name)
        finally:
            for path,data in saved.items():
                if data is None:path.unlink()
                else:path.write_bytes(data)
    record=sandbox/'ADAPTATIONS.json'
    trial('missing_authorized_adapter_record',{record:changed_json(record,lambda d:d.pop('runtime/assemble.py'))},F.check_adaptations)
    for filename,name in [('runtime/code/assemble.py','changed_runtime_with_updated_metadata'),('adapted/check_parent.py','changed_parent_adapter_with_updated_metadata')]:
        path=sandbox/filename;data=path.read_bytes()+b'\n# unauthorized adapter change\n';key='runtime/assemble.py' if filename.startswith('runtime/') else 'check_parent.py'
        changed=read(record);changed[key]['generated_sha256']=F.hashlib.sha256(data).hexdigest()
        trial(name,{path:data,record:json.dumps(changed).encode()},F.check_adaptations)
    trial('extra_runtime_code_file',{sandbox/'runtime/code/unlisted.py':b'# unlisted code\n'},F.check_adaptations)
    path=sandbox/'runtime/inputs/PR589-EXPECTED.json'
    trial('changed_runtime_input',{path:changed_json(path,lambda d:d.__setitem__('altered_control',True))},F.check_adaptations)
    path=sandbox/'CONSTRUCTION-CHECK.json'
    trial('changed_construction_owner_identity',{path:changed_json(path,lambda d:d.__setitem__('owner_content_sha256','0'*64))},F.check_construction)
    for name,relative,change in [
        ('changed_emitted_template','hosted/GLOBAL-TEMPLATE.json.gz',lambda d:d.__setitem__('physical',d['physical']+1)),
        ('changed_sigma_payload','hosted/ACTUAL-SIGMAS.json.gz',lambda d:d[next(iter(d))].__setitem__(0,0)),
        ('changed_idle_axes','hosted/IDLE-REMAINDER-FRAMES.json.gz',lambda d:d[0]['orthogonal_axes'].__setitem__(0,0)),
        ('changed_local_program_payload','base/providers/gauge44/LOCAL-PROGRAMS.json.gz',lambda d:d['forward'].append(['altered_control'])),
        ('missing_source_artifact_metadata','hosted/HOSTED.json',lambda d:d['source_artifacts'].pop(next(iter(d['source_artifacts'])))),
        ('changed_runtime_plan','PLAN.json',lambda d:d.__setitem__('altered_control',True)),
    ]:
        path=sandbox/'strict/global'/relative
        trial(name,{path:changed_json(path,change)},F.check_payload_artifacts)
    # Confirm the test copy is restored and successful after every mutation.
    F.check_adaptations(sandbox);F.check_construction(sandbox);F.check_payload_artifacts(sandbox)
    return rejected

def optimized_controls():
    env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None);rejected=[]
    for relative in ('verify.py','prepare.py','replay.py','final_binding.py','binding_controls.py',
                     'independent/verify_construct.py','independent/check_t37.py','independent/check_payload_controls.py'):
        result=subprocess.run([sys.executable,'-B','-O',str(P/relative),'--help'],cwd=ROOT,env=env,capture_output=True,text=True)
        assert result.returncode!=0 and 'Assertions must remain enabled' in result.stderr,('Optimized mode was not explicitly rejected',relative,result.stdout,result.stderr)
        rejected.append(relative)
    return rejected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True);parser.add_argument('--baseline',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();work=args.work.resolve();out=args.out.resolve()
    assert not out.exists() and not out.is_relative_to(ROOT),'New output outside checkout required'
    baseline=F.check(work,args.baseline.resolve())
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='t37-binding-controls-',dir=out.parent) as temporary:
        sandbox=Path(temporary).resolve();assert sandbox.is_relative_to(out.parent)
        rejected=mutations(work,sandbox)
    optimized=optimized_controls()
    assert F.check(work,args.baseline.resolve())==baseline,'Original replay changed during controls'
    result=dict(status='PASS_ACTUAL_FILE_BINDING_AND_OPTIMIZED_MODE_CONTROLS',rejected_controls=rejected,
                optimized_runs_rejected=optimized,baseline_binding_sha256=F.identity(baseline),
                scope='Twelve actual-file/metadata consistency mutations in a private copy and eight explicit optimized-mode rejections. Original replay/source bytes remain unchanged.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rejected),'file controls;',len(optimized),'optimized runs')

if __name__=='__main__':main()
