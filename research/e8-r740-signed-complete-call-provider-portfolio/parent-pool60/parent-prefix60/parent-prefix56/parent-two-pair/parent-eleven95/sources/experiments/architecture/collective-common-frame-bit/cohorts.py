"""Actual exact cold first-frame common cohorts beyond relation catalog."""
import json,runpy,struct
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import sympy as S
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;q=runpy.run_path(str(R/'experiments/architecture/odd-coefficient-kernel/solve.py'));K=q['K'];P=R/'experiments/architecture/enlarged-even-donors';frames=json.load(open(P/'original-records/frames.json'))['frames'];first={}
for op,a,b,c,f,z in struct.iter_unpack('<6i',(P/'original-records/249-records.bin').read_bytes()):
 if op==0 and f and a not in first:first[a]=c
sel=json.load(open(P/'pivot954/SELECTION.json'));piv={e['pivot']for e in sel['entries']};don={d for e in sel['entries']for d,c in e['donor_coefficients']};ret=set(q['base']['ret']);prior={d:set(e['frame']for e in sel['entries']if any(a==d for a,c in e['donor_coefficients']))for d in don}
def inside(a,b):return all(sum(x*y for x,y in zip(u,v))==0 for u in frames[str(a)]['B']for v in frames[str(b)]['A'])
cohort=[]
for E in sorted(set(first[d]for d in range(240,980))):
 dim=frames[str(E)]['dim']
 if not 1<=dim<=4:continue
 pool=[d for d in range(240,980)if d not in piv|ret and inside(E,first[d])and (d not in don or prior[d]=={E})]
 ps=[d for d in pool if d not in don]
 if not ps or len(pool)<2:continue
 A=S.Matrix([[K[d][i]for d in pool]for i in range(120)]);rank=A.rank()
 if rank==len(pool):continue
 cohort.append({'frame':E,'rank':dim,'pool':pool,'pivots':ps,'response_rank':rank,'kernel_dimension':len(pool)-rank})
 print(E,dim,len(pool),len(ps),rank,flush=True)
(O/'COHORTS.json').write_text(json.dumps({'status':'EXACT_ACTUAL_COMMON_FIRST_FRAME_COHORTS','source_signed80_selection_sha256':__import__('hashlib').sha256((P/'pivot954/SELECTION.json').read_bytes()).hexdigest(),'cohorts':cohort,'scope':'ActualfirstMOVE newframes, exactrationalcontainment, no selectedpivots/copiedretainedsource; existingdonors onlysameframe. Current80frozen. Integerlifts/fullpaidwordnotyetadmitted.'},indent=2)+'\n')
