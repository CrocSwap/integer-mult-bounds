"""Retimed local constructions from PR505's separate response-matroid candidates.
Use the exact inventory dual as a necessary improvement screen, not admission.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,sys,importlib.util,traceback
R=Path(__file__).resolve().parent;O=R/'async505-retimed-new-kernels';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
spec=importlib.util.spec_from_file_location('moment_screen',R/'stage4-local-verification/baseline/work/pr361/code/engines/moment.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
W=json.load(gzip.open(R/'pr501-retimed-bare-core.json.gz'));cert=json.load(open(R/'async505-inventory-bound/EXACT-WALL.json'));beta={int(k):Q(v)for k,v in cert['beta'].items()};m=cert['ambient'];b=Q(cert['rejected_endpoint']);cost=lambda H:m*M.moment(H,m,1,b,True)[0];baseline=json.load(open(R/'complex501-selective-gauges/baseline/RESULT.json'));base=cost({int(k):v for k,v in baseline['profile'].items()})+sum(n*beta[int(w)]for w,n in baseline['width_counts'].items());rows=[]
for name in ['COMPONENT','JOINT-47','JOINT-51']:
 d=O/name;d.mkdir();selection=json.load(open(R/'source505-review/research-notes/kernel'/(name+'-SELECTION.json')));(d/'SELECTION.json').write_text(json.dumps(selection,indent=2)+'\n')
 try:
  w=G.build(W,selection);H={int(k):v for k,v in w['report']['local_profile'].items()};wc=Counter(G.widths_of(w));score=cost(H)+sum(n*beta[k]for k,n in wc.items());gain=base-score;row=dict(label=name,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=H,widths=dict(wc),dual_score_improvement=str(gain),dual_score_improvement_float=float(gain),scope='Necessary local cost screen. Positive value still requires physical allocation, scalar/phase/guarded admission, full finite invoice and exact assembly.');(d/'WORD.json.gz').write_bytes(G.dump(w))
 except Exception as e:row=dict(label=name,status='REJECTED_LOCAL_CONSTRUCTOR',error=repr(e));(d/'FAILURE.txt').write_text(traceback.format_exc())
 (d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(row,flush=True)
(O/'COMPLETE.json').write_text(json.dumps(rows,indent=2)+'\n')
