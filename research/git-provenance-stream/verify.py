#!/usr/bin/env python3
"""Measure complete old/new metadata checks on the same immutable source list."""
from pathlib import Path
import importlib.util,json,subprocess,sys,time,statistics,types
from unittest.mock import patch

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACKAGE=HERE.relative_to(ROOT).as_posix()

def need(ok,why):
    if not ok:raise ValueError(why)

def load_modules():
    spec=importlib.util.spec_from_file_location('streamed_research_package',ROOT/'scripts/research_package.py')
    new=importlib.util.module_from_spec(spec);spec.loader.exec_module(new)
    base=json.loads((HERE/'SOURCES.json').read_bytes())['base_commit']
    old=types.ModuleType('legacy_research_package');old.__file__=str(ROOT/'scripts/research_package.py')
    code=subprocess.check_output(['git','show',base+':scripts/research_package.py'],cwd=ROOT)
    exec(compile(code,old.__file__,'exec'),old.__dict__)
    return old,new

def measure(module):
    real=subprocess.Popen;calls=[]
    def popen(*args,**kwargs):
        calls.append(args[0]);return real(*args,**kwargs)
    start=time.perf_counter()
    with patch.object(subprocess,'Popen',side_effect=popen):
        result=module.validate(ROOT,PACKAGE)
    return result,len(calls),time.perf_counter()-start

def verify():
    old,new=load_modules();n=len(json.loads((HERE/'SOURCES.json').read_bytes())['files'])
    measurements={'legacy':[],'streamed':[]};expected=None
    for _ in range(3):
        for name,module,processes in [('legacy',old,2*n+1),('streamed',new,1)]:
            result,count,seconds=measure(module)
            if expected is None:expected=result
            need(result==expected,'old/new validation return mismatch')
            need(count==processes,'source-reader process count changed')
            measurements[name].append({'git_processes':count,'seconds':round(seconds,6)})
    # Retain old fail-closed semantics for SHA, object-id and live input drift.
    sources_path=HERE/'SOURCES.json';original=sources_path.read_bytes()
    sources=json.loads(original)
    mutations=[]
    for key,bad in [('sha256','0'*64),('git_blob','0'*40)]:
        changed=json.loads(original);changed['files'][0][key]=bad
        mutations.append((key,changed,'source '+('SHA256' if key=='sha256' else 'blob')+' provenance mismatch'))
    # Validation reads are intercepted; repository fixtures are never mutated.
    original_read=Path.read_text
    for key,changed,error in mutations:
        def altered(path,*args,**kwargs):
            return json.dumps(changed) if path==sources_path else original_read(path,*args,**kwargs)
        for module in (old,new):
            with patch.object(Path,'read_text',altered):
                try:module.validate(ROOT,PACKAGE)
                except ValueError as exc:need(error in str(exc),'wrong mutation rejection')
                else:raise ValueError('accepted '+key+' mutation')
    return {'status':'PASS_STREAMED_GIT_PROVENANCE','source_files':n,'equivalent_results':6,
            'legacy_git_processes_per_check':2*n+1,'streamed_git_processes_per_check':1,
            'measurements':measurements,'median_seconds':{k:statistics.median(x['seconds'] for x in v) for k,v in measurements.items()},
            'controls':['SHA256 mismatch rejected by both','Git blob mismatch rejected by both'],
            'scope':'Metadata source loading only; identical full pin checks, no persistent cache and no mathematical replay speed claim.'}

if __name__=='__main__':
    result=verify()
    if '--write' in sys.argv:(HERE/'BENCHMARK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
