"""Independent actual heterogeneous eleven-stage endpoint and prefix scan."""
from pathlib import Path
import json,gzip,struct,hashlib
P=Path(__file__).resolve().parent;S=P.parent/'bit-provider-portfolio-v4/global';rd=lambda p:json.loads(p.read_text());t=json.loads(gzip.decompress((S/'GLOBAL-TEMPLATE.json.gz').read_bytes()));f=rd(S/'local/GLOBAL-BOUND.json');reg=t['provider_registry'];out={}
for kind in ['raw','signed']:
 records={pid:list(struct.iter_unpack('<6i',(Path(z['directory'])/('signed-records.bin'if kind=='signed'else'records/249-records.bin')).read_bytes()))for pid,z in reg.items()};v=[1<<i for i in range(9340)]+[0];norm=[1]*9340+[0];peak=1;unit=0;cuts=[]
 for e in t['schedule']:
  if e['kind']=='idle':continue
  if e['kind']=='local_cover_sweep':
   st,p,rev=e['stage'],e['pair'],e['reverse'];pid='lazy'if st==5 else'base';opened=False
   def mp(i):return 9340 if i==980 else((2*p+(1-i//120 if rev else i//120))*120+i%120 if i<240 else 1200+st*740+i-240)
   for op,a,b,c,fr,last in records[pid][::(-1 if rev else 1)]:
    if op==0:continue
    x,y=mp(a),mp(b)
    if op==1:
     unit+=abs(c);norm[x]+=abs(c)*norm[y];peak=max(peak,norm[x]);v[x]^=v[y]if c%2 else 0
    elif op==(3 if rev else 2):assert not opened;opened=True;v[9340]=v[x];norm[9340]=norm[x]
    else:assert opened and v[9340]==v[x];opened=False;v[9340]=norm[9340]=0
   assert not opened;cuts.append(dict(stage=st,provider=pid,prefix=str(peak)))
  elif e['kind']=='bridge':
   d,s=e['dst'],e['src']
   for a,b in [(2*d,2*s),(2*s+1,2*d+1)]:
    for i in range(120):x,y=a*120+i,b*120+i;v[x]^=v[y];norm[x]+=norm[y];peak=max(peak,norm[x]);unit+=1
  else:
   assert e['kind']=='exchange'
   for p in range(5):
    for i in range(120):x,y=2*p*120+i,(2*p+1)*120+i;v[x],v[y]=v[y],v[x];norm[x],norm[y]=norm[y],norm[x]
 assert v==[1<<i for i in range(9340)]+[0];out[kind]={'all9340_columns_restored':True,'prefix':str(peak),'unit_additions_all8':unit*8,'stages':cuts};assert out[kind]==f[kind]
out.update(status='PASS_INDEPENDENT_HETEROGENEOUS_STAGE_PARITY_AND_ABSOLUTE_SIGNED_PREFIX',scope='Full9340 scalar parity endpoint and cancellation-free signed coefficient bound. Integer local980 decoder/dirt/adjoint equality separately proven for BOTH providers. Hosted arbitrary-correlated arrays require stage cut/complete-invocation endpoint compiler premise; this parity replay alone is not global integer compiler admission.')
(P/'PORTFOLIO-PREFIX.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
