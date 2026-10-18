import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__import__('os').environ['EO_ROOT']+'/inputs/repo');PKG=ROOT/'research/gauge44-slots'
plan=json.loads((PKG/'data/PLAN.json').read_text())
paid=plan['provider_registry']['gauge44']['actual_paid_profile']
idle={int(r):n-72*paid.get(r,0) for r,n in plan['profile'].items()}
def kappa(loc):
    H=dict(idle)
    for r,n in loc.items():H[int(r)]=H.get(int(r),0)+72*n
    H={str(r):n for r,n in sorted(H.items()) if n}
    d=tempfile.mkdtemp();pf=Path(d)/'p.json';pf.write_text(json.dumps({'profile':H}));po=Path(d)/'o.json'
    r=subprocess.run([sys.executable,'-B',str(PKG/'independent/price_profile.py'),'--main',str(ROOT),'--profile',str(pf),'--output',str(po)],capture_output=True,text=True,cwd=ROOT)
    if r.returncode:raise SystemExit(r.stdout[-300:]+r.stderr[-800:])
    k=json.loads(po.read_text())['prices']['native']['outer_with_bit'];return float(k['kappa_decimal']),k['binding']
if __name__=='__main__':
    base={1:2412,2:418,3:432,4:142,5:82,8:8}
    k0,b=kappa(base);print('base',k0,b)
    def delta(name,d):
        l=dict(base)
        for r,n in d.items():l[r]=l.get(r,0)+n
        k,_=kappa(l);print(f'{name:50s} {k:.9e} d={k-k0:+.4e} ({100*(k-k0)/k0:+.3f}%)')
    delta('-1 helper (1,1,1,3,1,1,1) mass-9',{1:-6,3:-1})
    delta('-1 helper (1,1,1,1,5) mass-9',{1:-4,5:-1})
    delta('-1 helper (2,3,3) start1 end9 mass-8',{2:-1,3:-2})
    delta('-1 H1 (mass-1)',{1:-1})
    delta('+1 H1',{1:1})
    delta('-1 H3 +1 H2 +1 H1 (neutral reshape)',{3:-1,2:1,1:1})
    delta('-1 H2 + 2 H1 neutral',{2:-1,1:2})
    delta('#1005 cell (-30H1+6H2+6H3) x1',{1:-30,2:6,3:6})
