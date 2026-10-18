from pathlib import Path
import gzip,json,ast,re,sympy as S
from collections import Counter
R=Path(__file__).resolve().parent;w=json.load(gzip.open(R/'trace541-frozen-minimum/WORD.json.gz'));dim=[S.Matrix([w['lines'][i]for i in f]).rank()if f else 0 for f in w['frames']];mask=[sum(1<<i for i in f)for f in w['frames']];cur=w['start'][:];H=Counter()
def move(r,f):
 assert mask[cur[r]]&mask[f]==mask[cur[r]]
 if cur[r]!=f:H[int(dim[f]-dim[cur[r]])]+=1;cur[r]=f
for sec in ['D','A','B','C']:
 for f,d,ss in w[sec]:
  for r in [d]+ss:move(r,f)
for r,f in enumerate(w['final']):move(r,f)
# Compare the independently reconstructed five-stage histogram when that separate receipt exists.
p=R/'trace541-frozen-minimum/independent311-checkword.log'
if p.exists():
 official=ast.literal_eval(re.search(r'^histogram (\{.*?\}) m ',p.read_text(),re.M).group(1));five=Counter({r:5*n for r,n in H.items()});five[8]+=45
 for r in [14,7,18,4]:five[r]+=240
 assert dict(five)==official
r=dict(new_chain_profile=dict(H),scope='Exact rank profile from every final combined-word frame transition; center copies separate and unchanged9x8. Do not add standalone histogram deltas: the frame changes interact.')
(R/'trace541-frozen-minimum/PROFILE.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
