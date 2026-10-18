import os,sys,json,gzip
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import argparse
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();OUT=args.work.resolve();assert not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True,exist_ok=True)
os.environ['K8_BASE_WORD']=str(OUT/'candidate.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
w=S.w;M=S.M;m=M.Model(w);n=704;v=112
raw=[{k:F(1)} for k in range(n)]
for e in w['A']+w['cut']+w['B']:M.apply(e,raw)
bad={k for y in range(v,2*v) for k in raw[y] if k>=2*v}
touch={q for e in w['precondition'] for q in M.registers(e)}
groups=defaultdict(list)
for q in range(224,704):
 if q in bad or q in touch or q in w['centers']:continue
 first=m.chains[q][1];hi=m.hi[first];old=M.basis(w['start_extra'].get(str(q),[]))
 if hi:groups[(old,hi)].append(q)
d=[dict(helpers=qs,old=list(old),hi=list(hi),old_dim=len(old),hi_dim=len(hi)) for (old,hi),qs in groups.items()]
(OUT/'INTERFACE-CENSUS.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
