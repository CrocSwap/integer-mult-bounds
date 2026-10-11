from pathlib import Path
from hashlib import sha256
import json,gzip,struct,sys
if not __debug__:raise SystemExit('Assertions required')
getattr(sys,'set_int_max_str_digits',lambda _:None)(0)
V=Path(__file__).resolve().parent;E=V.parent;P=E/'stage-search/pr445-signed80-eleven/signed';O=V/'pr445-eleven80-independent';B=E/'stage-search/pr445-signed80-eleven/hosted'
read=lambda p:json.loads(p.read_bytes());sha=lambda p:sha256(p.read_bytes()).hexdigest()
claim=read(P/'GLOBAL-BOUND.json');assert all(sha(Path(p))==h for p,h in claim['source_inputs'].items())
g=read(B/'GLOBAL.json');t=json.loads(gzip.decompress((B/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
recipe=[dict(kind='local',stage=0,pair=0,reverse=False)];stage=1
for j in range(5):
 recipe.append(dict(kind='local',stage=stage,pair=j,reverse=True));stage+=1
 if j<4:recipe.append(dict(kind='bridge',dst=j,src=j+1,coefficient=1))
 recipe.append(dict(kind='local',stage=stage,pair=j,reverse=False));stage+=1
 if j<4:recipe.append(dict(kind='bridge',dst=j,src=j+1,coefficient=-1))
for j in reversed(range(4)):recipe.append(dict(kind='bridge',dst=j+1,src=j,coefficient=1))
recipe.append(dict(kind='exchange'))
assert recipe==[dict(e,kind='local')if e['kind']=='local_cover_sweep'else e for e in t['schedule']if e['kind']!='idle']
def scan(events):
 n=1200+11*740;temp=n;val=[1<<i for i in range(n)]+[0];norm=[1]*n+[0];peak=1;adds=copies=bridges=0
 for e in recipe:
  if e['kind']=='local':
   st,p,rev=e['stage'],e['pair'],e['reverse'];opened=None
   def at(i):
    if i==980:return temp
    if i<240:return (2*p+(1-i//120 if rev else i//120))*120+i%120
    return 1200+st*740+i-240
   for op,a,b,c,f,z in reversed(events)if rev else events:
    if op==0:continue
    x,y=at(a),at(b)
    if op==1:
     assert x!=y and x!=temp and x!=opened
     if y==temp:assert opened is not None
     norm[x]+=abs(c)*norm[y];peak=max(peak,norm[x]);adds+=abs(c)
     if c%2:val[x]^=val[y]
    elif op==(3 if rev else 2):
     assert opened is None and b==980 and val[temp]==norm[temp]==0
     opened=x;val[temp]=val[x];norm[temp]=norm[x];copies+=1
    else:
     assert op==(2 if rev else 3)and opened==x and val[temp]==val[x]
     val[temp]=norm[temp]=0;opened=None
   assert opened is None and all(val[1200+st*740+r]==1<<(1200+st*740+r)for r in range(740))
  elif e['kind']=='bridge':
   d,s=e['dst'],e['src']
   for a,b in [(2*d*120,2*s*120),((2*s+1)*120,(2*d+1)*120)]:
    for i in range(120):val[a+i]^=val[b+i];norm[a+i]+=norm[b+i];peak=max(peak,norm[a+i]);bridges+=1
  else:
   for p in range(5):
    for i in range(120):a,b=2*p*120+i,(2*p+1)*120+i;val[a],val[b]=val[b],val[a];norm[a],norm[b]=norm[b],norm[a]
 assert val==[1<<i for i in range(n)]+[0]and copies==99 and bridges==2880
 return peak,adds+bridges
raw=list(struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()));z=list(struct.iter_unpack('<6i',(P/'signed-records.bin').read_bytes()))
scans={label:scan(e)for label,e in [('raw',raw),('signed',z)]}
for key,(peak,units)in scans.items():assert str(peak)==claim[key]['prefix']and units==claim[key]['unit_additions_per_replica']
for rev,ori in [(False,'forward'),(True,'reverse')]:
 expected=[]
 for op,x,y,c,f,k in reversed(raw)if rev else raw:
  if op==0:expected.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
  elif op==1:expected.append([1,x,y,-c if rev else c,f,int(rev)])
  elif op==(3 if rev else 2):expected.append([2,x,y,c,f,8,int(rev)])
  else:expected.append([3,x,y,c,f,k,int(rev)])
 assert t['local_programs'][ori]==expected
old=read(P/'RESULT.json');fresh=read(O/'signed-rerun/RESULT.json')
assert {k:v for k,v in old.items()if k not in('seconds','input_sha256')}=={k:v for k,v in fresh.items()if k not in('seconds','input_sha256')}
for name in ['signed-records.bin','decoder-and-dirt.json']:assert(P/name).read_bytes()==(O/'signed-rerun'/name).read_bytes()
assert len(fresh['controls'])==9 and all(c['rejected']for c in fresh['controls'])
assert max(v[0]for v in scans.values())<=int(claim['finite']['charged_prefix'])<2**192
r=dict(status='PASS_INDEPENDENT_KERNEL80_ELEVEN_T8_SERIALIZED_COMPLETE_PREFIX_AND_FRESH_SIGNED_LEDGERS',
 raw_scan=scans['raw'],signed_scan=scans['signed'],all9340_F2_columns_restored_per_replica=True,
 all8_replicas_bound_by_disjoint_owners=True,full_signed980_columns_and_all9_controls_fresh=True,
 reflected_and_forward_frame_ledgers_fresh=True,actual_template_recipe_and_streams_equal=True,
 conservative_prefix=claim['finite']['charged_prefix'],prefix_bits=156,
 source_bound_receipt_sha256=sha(P/'GLOBAL-BOUND.json'),fresh_signed_receipt_sha256=sha(O/'signed-rerun/RESULT.json'),
 script_sha256=sha(Path(__file__)),scope='Local signed defining J and parity-global identity are distinct obligations. The complete actual scalar recipe prefix is independently scanned; all-size geometric/address/compiler assumptions remain conditional.')
(O/'PREFIX.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(r['status'],sha(O/'PREFIX.json'))
