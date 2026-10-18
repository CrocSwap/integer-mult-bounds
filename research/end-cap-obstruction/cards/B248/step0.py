import pricep as P
base={1:2412,2:418,3:432,4:142,5:82,8:8}
def kg(loc,extra):
    H=dict(P.idle)
    for r,n in loc.items():H[int(r)]=H.get(int(r),0)+72*n
    for r,n in extra.items():H[int(r)]=H.get(int(r),0)+n
    return H
import json,subprocess,sys,tempfile
from pathlib import Path
def kapG(H):
    H={str(r):n for r,n in sorted(H.items()) if n}
    d=tempfile.mkdtemp();pf=Path(d)/'p.json';pf.write_text(json.dumps({'profile':H}));po=Path(d)/'o.json'
    r=subprocess.run([sys.executable,'-B',str(P.PKG/'independent/price_profile.py'),'--main',str(P.ROOT),'--profile',str(pf),'--output',str(po)],capture_output=True,text=True,cwd=P.ROOT)
    if r.returncode:return None
    return float(json.loads(po.read_text())['prices']['native']['outer_with_bit']['kappa_decimal'])
k0=kapG(kg(base,{}));print('base',k0)
def t(name,d,extra):
    l=dict(base)
    for r,n in d.items():l[r]=l.get(r,0)+n
    k=kapG(kg(l,extra))
    print(f'{name:60s}', 'REJECTED(mass)' if k is None else f'{k:.9e} {100*(k-k0)/k0:+.3f}%')
# 2 helpers removed, pattern (1,1,1,3,1,1,1) mass 9 each, global mass 18*72=1296 -> H48 +27
t('2 helpers gone, mass->idle rank48 (27 H48)',{1:-12,3:-2},{48:27})
t('2 helpers gone, mass->idle as H16 (81 H16)',{1:-12,3:-2},{16:81})
t('2 helpers gone, mass-> as 1296 H1 (idle small)',{1:-12,3:-2},{1:1296})
t('2 helpers (1,1,1,1,5) gone -> H48',{1:-8,5:-2},{48:27})
t('mass-only: 1 H1 mass->H48 equivalent (-48 H1 +1 H48)',{},{1:-48,48:1})
t('#1005-like cell -30H1+6H2+6H3 per local x8 (neutral)',{1:-240,2:48,3:48},{})
