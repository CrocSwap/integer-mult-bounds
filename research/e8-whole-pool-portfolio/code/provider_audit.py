from pathlib import Path
import json,sys,hashlib,time
from fractions import Fraction as Q
from collections import Counter
sys.dont_write_bytecode=True
cp=Path(sys.argv[1]);out=Path(sys.argv[2]);base=Path(sys.argv[3]);c=json.loads(cp.read_text());b=json.loads(base.read_text());assert c['frames']==b['frames'] and c['lines']==b['lines'];v=c['v'];n=2*v+c['R'];dims=[];masks=[];t0=time.time()
for frame in c['frames']:
 piv={}
 for i in frame:
  row=list(map(Q,c['lines'][i]))
  for k,r in sorted(piv.items()):
   if row[k]:
    a=row[k]/r[k];row=[x-a*y for x,y in zip(row,r)]
  if any(row):piv[next(k for k,x in enumerate(row) if x)]=row
 dims.append(len(piv));masks.append(sum(1<<i for i in frame))
def check(z):
 cur=list(z['start']);val=[1<<i for i in range(n)];sup=[1<<i if i<v else 0 for i in range(n)];H=Counter();gates=0
 def climb(r,f):
  assert masks[cur[r]]&~masks[f]==0,('frame',r,cur[r],f)
  if cur[r]!=f:
   delta=dims[f]-dims[cur[r]];assert delta>0;H[delta]+=1;cur[r]=f
 for ph in ['D','A','B','C']:
  if ph=='B':
   copy=[val[r] for r in z['ret']]
   for r in z['ret']:H[dims[cur[r]]]+=1
   for t,ks in enumerate(z['scatter']):
    for k in ks:val[v+t]^=copy[k]
  for f,d,ss in z[ph]:
   assert d not in ss and len(set(ss))==len(ss)
   for r in [d]+ss:climb(r,f)
   for s in ss:
    val[d]^=val[s];gates+=1
    if s<v or s>=2*v:assert sup[s]&~masks[f]==0,('source span',ph,s)
    sup[d]|=sup[s]
   if d>=2*v:assert sup[d]&~masks[f]==0,('target span',ph,d)
 for r,f in enumerate(z['final']):climb(r,f)
 for r in range(n):assert val[r]==((1<<r)^(1<<(r-v)) if v<=r<2*v else 1<<r),('rawcolumn',r)
 return H,gates
h,g=check(c);h0,_=check(b);delta={r:h[r]-h0[r] for r in h.keys()|h0.keys() if h[r]!=h0[r]}
controls=[]
# Each newly restored entrance must truly start at zero; reverting its start alone rejects.
for p in range(2*v,n):
 if c['start'][p]!=b['start'][p]:
  bad=json.loads(json.dumps(c));bad['start'][p]=b['start'][p]
  try:check(bad)
  except AssertionError:controls.append(p)
  else:raise AssertionError(('control accepted',p))
receipt=dict(status='PASS_EXACT_LOCAL_PORTFOLIO',word_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),parent_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),all_columns=n,integer_support=True,exact_rational_frame_dimensions=len(dims),local_profile=dict(h),delta=delta,rank_change=sum(r*k for r,k in delta.items()),controls=controls,scalar_adds=g,seconds=time.time()-t0,scope='Finite local word only; global heterogeneous invocation and owner audit required')
out.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
