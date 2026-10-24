"""Portable source-bound native provider/assembly replay, not theorem acceptance."""
from pathlib import Path
import hashlib,json,tempfile,shutil,subprocess,sys,gzip
HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def load(name):
    p=HERE/(name+'.py');n={'__name__':'authenticated_component','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),n);return n

def inventory():
    return {p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file() and p.name!='CONTENT-HASHES.json'}

def main():
    pins=json.loads((HERE/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    need(inventory()==pins,'package source hash or inventory mismatch')
    for r in json.loads((HERE/'PHASE-SOURCE-PINS.json').read_text())['files']:
        need(pins['v/'+r['path']]==r['sha256'],'public phase source pin')
    for row in json.loads((HERE/'ADDITIONAL-SOURCE-PINS.json').read_text()):
        need(pins[row['local_file']]==row['sha256'],'additional retained source pin')
    provider=load('critical_provider_check')['check']()
    lift=load('native_lift');params=lift['choose']('.0030217755','.0030217754')
    need(params==json.loads((HERE/'PARAMETERS.json').read_text()),'native parameter drift')
    arithmetic=lift['check']()
    records=load('record_product')['check']()
    with tempfile.TemporaryDirectory(prefix='native-lift-') as td:
        root=Path(td)/'v';shutil.copytree(HERE/'v',root)
        # -I ignores inherited PYTHONOPTIMIZE; public assertion checks stay enabled.
        logical=subprocess.run([sys.executable,'-I','-B',str(HERE/'operator_check.py'),str(root)],capture_output=True,text=True,timeout=180)
        need(logical.returncode==0,'literal source replay: '+logical.stderr)
        logical_result=json.loads(logical.stdout)
        ce=root/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
        bridges=subprocess.run([sys.executable,'-I','-B',str(HERE/'frame_bridge_review.py'),'--source',str(ce)],capture_output=True,text=True,timeout=60)
        need(bridges.returncode==0,'frame bridge replay: '+bridges.stderr)
        bridge_result=json.loads(bridges.stdout)
        p=root/'research/kappa-round3-warp-20261022/phase_check.py'
        phase=subprocess.run([sys.executable,'-I','-B',str(p)],capture_output=True,text=True,timeout=180)
        need(phase.returncode==0,'absolute phase replay: '+phase.stderr)
        phase_result=json.loads(gzip.decompress(p.with_name('PHASE-VALIDATION.json.gz').read_bytes()))
        need(phase_result['status']=='PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES','phase receipt')
        for row in json.loads((HERE/'PHASE-SOURCE-PINS.json').read_text())['files']:
            need(hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],'temporary source drift')
    need(inventory()==pins,'replay mutated committed sources')
    print(json.dumps(dict(status='PASS_NATIVE_PROVIDER_LIFT',authenticated_files=len(pins),kappa='0.0030217754',provider=provider,native_parameters=params,parameter_controls=arithmetic['rejecting_controls'],logical=logical_result,frame_bridges=bridge_result,absolute_phase={'status':phase_result['status'],'changed_helper_boundaries':len(phase_result['changed_helper_boundaries'])},record_products=records,scope='Exact finite identities and arithmetic; all-fiber compiler and analytic proofs are inherited informal mathematics.'),indent=2))
if __name__=='__main__':main()
