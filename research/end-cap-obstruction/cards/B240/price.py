"""price.py: exact kappa for a k8-word local profile under #1018's composition (72*local + frozen #1018 idle),
via the package's own independent/price_profile.py (two exact engines + outer47 + PR589 bit). Same method as B232 price1018.py."""
import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__import__('os').environ['EO_ROOT']+'/inputs/repo');PKG=ROOT/'research/gauge44-slots'
plan=json.loads((PKG/'data/PLAN.json').read_text());paid=plan['provider_registry']['gauge44']['actual_paid_profile']
IDLE={int(r):n-72*paid.get(r,0) for r,n in plan['profile'].items()}
def kappa(local):
    H=dict(IDLE)
    for r,n in local.items():H[int(r)]=H.get(int(r),0)+72*n
    H={str(r):n for r,n in sorted(H.items()) if n}
    d=Path(tempfile.mkdtemp());(d/'p.json').write_text(json.dumps({'profile':H}))
    r=subprocess.run([sys.executable,'-B',str(PKG/'independent/price_profile.py'),'--main',str(ROOT),'--profile',str(d/'p.json'),'--output',str(d/'o.json')],capture_output=True,text=True,cwd=ROOT)
    if r.returncode:raise RuntimeError(r.stdout[-400:]+r.stderr[-800:])
    return json.loads((d/'o.json').read_text())['prices']['native']['outer_with_bit']['kappa_decimal']
if __name__=='__main__':
    print(kappa(json.loads(sys.argv[1])))
