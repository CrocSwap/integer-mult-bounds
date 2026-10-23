import runpy, sys
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
g=runpy.run_path(str(ROOT/'research/coded-reverse-controller/verify.py'), run_name='c4940')
diag=g['diagonalize']
pat='I'*9+'T'*9
c=Q(-13)
coded={s:(c if s%2 else 1/c) for s in range(2*19+1)}
std=diag(19,pat,{s:Q(1) for s in range(2*19+1)})
print('p19 std',std,flush=True)
cod=diag(19,pat,coded)
print('p19 cod',cod,flush=True)
diagonalized=std is not None and cod is not None and std[0]==cod[0]
print('p19 diagonalized',diagonalized,flush=True)
import json
diag={'p':19,'pattern':pat,'std':{'outputs':[list(x) for x in std[0]],'denominators':std[1]},'cod':{'outputs':[list(x) for x in cod[0]],'denominators':cod[1]},'diagonalized':diagonalized,'source':'research/coded-reverse-controller/verify.py diagonalize(19, pattern, coded)'}
(HERE/'P19_DIAG.json').write_text(json.dumps(diag,indent=2))
