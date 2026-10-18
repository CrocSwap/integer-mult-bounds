"""Independent tiny exhaustive control for the exact temporal-gauge DP."""
from fractions import Fraction
import importlib.util
from pathlib import Path
from itertools import product

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("l284_temporal",HERE/"temporal.py")
if spec is None or spec.loader is None: raise RuntimeError("load temporal.py")
t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
terms=[(0,Fraction(3,8),1),(1,Fraction(5,4),-1),(2,Fraction(3,2),1)]
result=t.optimize(terms)
lo,hi=result["domain"]
direct=min(t.objective(terms,path) for path in product(range(lo,hi+1),repeat=len(terms)))
t.need(result["delta_real"]==direct,"DP agrees with exhaustive three-ADD enumeration")
t.need(t.objective(terms,result["schedule"])==result["delta_real"],"literal schedule objective")
t.need(result["domain"]==[-2,3],"exact breakpoint domain control")
print("PASS_K8_L284_DP_CONTROL paths=216 exact=PASS")
