"""Exact local entrance promotions on PR484's word, upstream PR496 target."""
from pathlib import Path
import sys,json,gzip,copy,hashlib,time
from collections import Counter
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'))
import gk_word as G
P=R/'pr496-complex-full314/p442/parent/baseline/baseline/split-centres/FULL-WORD.json.gz';W=json.load(gzip.open(P));S=json.load(open(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/data/selections/gauge80-kernel42.json'))
O=R/'complex496-entrance-search';O.mkdir(exist_ok=False);(O/'BASE-WORD.json.gz').write_bytes(P.read_bytes());(O/'BASE-SELECTION.json').write_text(json.dumps(S,indent=2)+'\n')
col=G.responses(W);first=G.first_frames(W);sp={h:G.span(E) for h,E in first.items()}
def meet(hs):
 s=set.intersection(*(sp[h] for h in hs));return list(G.basis(sorted(s-{0})))
ledger=[]
def trial(label,sel):
 try:
  w=G.build(W,sel);prof={int(r):n for r,n in w['report']['local_profile'].items()};widths=G.widths_of(w)
  row=dict(label=label,status='PASS_LOCAL_CONSTRUCTOR_ONLY',profile=prof,width_counts=dict(Counter(widths)),rank=sum(9-x for x in widths),selection_sha256=hashlib.sha256(json.dumps(sel,sort_keys=True).encode()).hexdigest())
  d=O/label;d.mkdir();(d/'SELECTION.json').write_text(json.dumps(sel,indent=2)+'\n');(d/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));(d/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n')
 except AssertionError as e:row=dict(label=label,status='REJECTED_LOCAL_CONSTRUCTOR',error=str(e))
 ledger.append(row);print(row,flush=True);return row
trial('baseline',S)
# Split classes without changing any correction, retaining only nonzero rational donors.
solo=[]
for c in S['kernel']:
 for pivot in c['pivots']:
  donors=sorted(G.solve_relation(col,c['donors'],pivot));solo.append(dict(E=c['E'],donors=donors,pivots=[pivot]))
split=copy.deepcopy(S);split['kernel']=solo;trial('split-relations',split)
for j,c in enumerate(solo):
 E=meet(c['donors']+c['pivots'])
 if len(E)>len(c['E']):
  sel=copy.deepcopy(split);sel['kernel'][j]['E']=E;trial('kernel-promote-'+str(c['pivots'][0]),sel)
# Maximal legal gauge entrance under unchanged other gauges, tested independently.
for h,e in S['gauge'].items():
 h=int(h);E=first[h]
 if len(E)>len(e):
  sel=copy.deepcopy(S);sel['gauge'][str(h)]=list(E);trial('gauge-promote-'+str(h),sel)
# Gauge each unused helper at every nonzero subspace line of its first frame.
used={int(h) for h in S['gauge']}|{h for c in S['kernel'] for h in c['donors']+c['pivots']}
for h in sorted(first):
 if h in used:continue
 for v in sorted(sp[h]-{0}):
  # Restrict to existing gauge frames so target/centre nesting remains plausible.
  if [v] not in list(S['gauge'].values()):continue
  sel=copy.deepcopy(S);sel['gauge'][str(h)]=[v];trial('new-gauge-'+str(h)+'-'+str(v),sel)
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');print('COMPLETE',len(ledger),flush=True)
