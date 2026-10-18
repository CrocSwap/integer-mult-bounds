# B258: exact kappa of a global profile WITHOUT the 2560 deficit pin (deficit-honest: added rank lowers D). Uses the package's
# own price_profile.py (two exact engines + outer47 + PR589 bit), monkeypatching only the deficit assertion. NOT a package edit.
import importlib.util,json,sys,tempfile,io,contextlib
from pathlib import Path
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B248')
with contextlib.redirect_stdout(io.StringIO()):
    import pricep as PP
ROOT=PP.ROOT;PKG=PP.PKG
spec=importlib.util.spec_from_file_location('pp',PKG/'independent/price_profile.py');pp=importlib.util.module_from_spec(spec);spec.loader.exec_module(pp)
orig=pp.moment_checks
def mc(M,B,H,m,W,lower,deficit,bad):
    return orig(M,B,H,m,W,lower,m*W-sum(r*n for r,n in H.items()),bad)
pp.moment_checks=mc
def kappa(loc):
    H=dict(PP.idle)
    for r,n in loc.items():H[int(r)]=H.get(int(r),0)+72*n
    d=Path(tempfile.mkdtemp());(d/'p.json').write_text(json.dumps({'profile':{str(r):n for r,n in sorted(H.items()) if n}}))
    sys.argv=['x','--main',str(ROOT),'--profile',str(d/'p.json'),'--output',str(d/'o.json')]
    import os;cwd=os.getcwd();os.chdir(ROOT)
    with contextlib.redirect_stdout(io.StringIO()): pp.main()
    os.chdir(cwd)
    return float(json.loads((d/'o.json').read_text())['prices']['native']['outer_with_bit']['kappa_decimal'])
if __name__=='__main__':
    base={1:2412,2:418,3:432,4:142,5:82,8:8}
    k0=kappa(base);print('base',k0,'(pinned price1018 base should match)')
    for k in (1,2,4,16,32,48,64,96,128):
        l=dict(base);l[1]+=k;kk=kappa(l);print(f'+{k:3d} rank-1 local units: kappa {kk:.9e}  {100*(kk-k0)/k0:+.3f}%  per unit {100*(kk-k0)/k0/k:+.4f}%',flush=True)
