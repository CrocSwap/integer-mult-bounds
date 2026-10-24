"""Fast coherent source, mathematics, replay-receipt and artifact check."""
from pathlib import Path
from hashlib import sha256
import importlib.util, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def need(ok, why):
    if not ok:
        raise ValueError(why)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE/name).read_text(encoding='utf-8'))

def load(name):
    spec = importlib.util.spec_from_file_location('complement_audit_'+name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def artifacts():
    return {p.relative_to(HERE).as_posix(): digest(p) for p in sorted(HERE.rglob('*'))
            if p.is_file() and not set(p.relative_to(HERE).parts) & {'.scratch','__pycache__'}
            and p.name != 'ARTIFACT-MANIFEST.json'}

def check():
    pins = load('replay').source_check()
    independent = load('independent').audit()
    independent['script_sha256'] = digest(HERE/'independent.py')
    independent['sources_sha256'] = digest(HERE/'SOURCES.json')
    need(json.loads(json.dumps(independent)) == read('INDEPENDENT.json'), 'Independent mathematical receipt drift')
    replay = read('REPLAY.json')
    need(replay['status']=='PASS' and replay['returncode']==0, 'Complete replay has not passed')
    need(replay['head']==pins['head'] and replay['sources_sha256']==digest(HERE/'SOURCES.json') and replay['runner_sha256']==digest(HERE/'replay.py'), 'Replay source binding')
    need(replay['stdout_sha256']==digest(HERE/'REPLAY.stdout.log') and replay['stderr_sha256']==digest(HERE/'REPLAY.stderr.log'), 'Replay log binding')
    original = json.loads((HERE/'REPLAY.stdout.log').read_bytes())
    need(replay['upstream']==original, 'Replay stdout/receipt equality')
    need(original['status']=='PASS_COMPLETE_NATIVE_DUAL_SUPPLIERS_NO_NEW_KAPPA' and original['authenticated_files']==53, 'Exact original verifier acceptance')
    need({p['provider'] for p in original['providers']}=={'B','C'}, 'Both provider regenerations')
    byname = {p['provider']: p for p in original['providers']}
    need(byname['B']['receipt']['paid_center_helper_pairs']==2088 and byname['C']['receipt']['paid_center_helper_pairs']==2048, 'Complete paid/helper pair coverage')
    need(len(original['controls'])==2 and set(original['controls'].values())=={'REJECTED'}, 'Optimized source corruption controls')
    return dict(status='PASS_FROZEN_COMPLEMENTARY_SUPPLIER_ADMISSION_AUDIT', head=pins['head'], source_files=len(pins['files']), arbitrary_persistent_inputs=632, independent_helper_inputs_per_call=408, orientations=2, independent_mathematical_controls=2, optimized_source_controls=2, input_hashes={name:digest(HERE/name) for name in ['SOURCES.json','GITHUB-METADATA.json','independent.py','INDEPENDENT.json','replay.py','REPLAY.json','REPLAY.stdout.log','REPLAY.stderr.log','README.md','PLAN.md']}, checker_sha256=digest(Path(__file__)), new_kappa=False, profitable_complete_controller=False, lean_formalization=False)

if __name__ == '__main__':
    result = check()
    if '--write-manifest' in sys.argv:
        (HERE/'BUNDLE-CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        (HERE/'ARTIFACT-MANIFEST.json').write_text(json.dumps(artifacts(),indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(result==read('BUNDLE-CHECK.json'), 'Aggregate coherent receipt drift')
        need(artifacts()==read('ARTIFACT-MANIFEST.json'), 'Frozen artifact manifest drift')
    print(result['status'], 'sources='+str(result['source_files']), 'new_kappa=false')
