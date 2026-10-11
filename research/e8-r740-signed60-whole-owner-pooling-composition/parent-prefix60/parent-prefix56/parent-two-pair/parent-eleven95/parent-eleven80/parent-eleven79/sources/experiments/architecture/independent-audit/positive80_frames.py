from pathlib import Path
from fractions import Fraction as Q
import json,struct
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/architecture/odd-coefficient-kernel/mask31';st=json.loads((S/'records/249-states.json').read_text());fr={int(k):v for k,v in json.loads((S/'records/frames.json').read_text())['frames'].items()};ev=list(struct.iter_unpack('<6i',(S/'records/249-records.bin').read_bytes()));bad=[]
for i,(op,a,b,c,f,z) in enumerate(ev):
 if op!=0:continue
 # Exact rational frame containment from orthogonal annihilator test.
 pairs=[(u,w,sum(Q(x)*Q(y) for x,y in zip(u,w))) for u in fr[b]['B'] for w in fr[c]['A']]
 wrong=[(u,w,str(d)) for u,w,d in pairs if d]
 if wrong or fr[b]['dim']>fr[c]['dim']:bad.append(dict(record=i,role=a,old=b,new=c,old_dim=fr[b]['dim'],new_dim=fr[c]['dim'],nonzero_dot_witness=wrong[:1]))
out={'status':'REJECT_80_PIVOT_MONOTONE_FRAME_ADMISSION','illegal_moves':bad,'scope':'Native exporter only uses frame dimensions. Rational old-subspace containment is separately necessary; signed scalar identity alone does not admit positive helper entrance.'};assert bad
(P/'POSITIVE80-FRAMES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
