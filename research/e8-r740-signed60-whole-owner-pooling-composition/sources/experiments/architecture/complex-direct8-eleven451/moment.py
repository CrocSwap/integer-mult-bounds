from pathlib import Path
import json,importlib.util
from fractions import Fraction
P=Path(__file__).resolve().parent
g=json.load(open(P/'hosted/GLOBAL.json'));H={int(r):n for r,n in g['profile'].items()}
mods={}
for name in ('moment','base_two_moment'):
 s=importlib.util.spec_from_file_location(name,P/'work/pr361/code/engines'/(name+'.py'));M=importlib.util.module_from_spec(s);s.loader.exec_module(M);mods[name]=M
out=mods['moment'].certify(H,89,9600,True)
fallback=32*89*89*sum(H.values())
probes={}
for side in ('lower','upper'):
 a=Fraction(out[side]);lo,hi=mods['base_two_moment'].moment(89,9600,list(H.items()),a);f,g=mods['base_two_moment'].moment(89,9600,[(1,fallback)],a);lo+=f/10**16;hi+=g/10**16
 assert hi<1 if side=='lower'else lo>1
 probes[side]=[str(lo),str(hi)]
out['independent_base_two_probes']=probes
(P/'MOMENT.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items()if k!='independent_base_two_probes'})
