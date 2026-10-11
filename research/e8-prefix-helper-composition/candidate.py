"""PR390's exact 18 target-prefix rewrites, two inherited helper aliases and two frame reductions.
Source-only reconstruction. Dugongue's unchanged PR390 prefix algorithm is supplied
as a readable LF carrier; exact upstream CRLF bytes are reconstructed and checked
before execution. Inherited PR378 and helper-substitution notices apply.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import gzip,importlib.util,json,os,sys
from collections import Counter
HERE=Path(__file__).resolve().parent
FINAL='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
raw=lambda c:json.dumps(c,sort_keys=True,separators=(',',':')).encode()
def old_response(source378,far_package):
 z=(Path(source378)/'data/gcert1-e8-r783-far.json.gz').read_bytes()
 assert sha256(z).hexdigest()=='f2664ee7bcdfb55893abe9f1be8ee6a394a602e8262e611de2a0328bbd508aa7'
 alias=load('frozen_response_alias',Path(far_package)/'two_alias.py')
 c=json.loads(gzip.decompress(z))
 for d,u in [(706,268),(707,323)]:c,_=alias.build(c,d,u)
 data=raw(c);assert sha256(data).hexdigest()=='d14ea8bf581d9f5ea8f3261e614199386d71ea4cbc8bc48d6bec371954669daf'
 return data
def native_sources(output):
 output=Path(output);assert not output.exists();output.mkdir()
 pins=json.loads((HERE/'SOURCE.json').read_text())['prefix'];result={}
 for name,key in [('prefix_source.py','source'),('prefix_selection.json','selection')]:
  carrier=(HERE/name).read_bytes();assert b'\r' not in carrier
  assert sha256(carrier).hexdigest()==pins[key+'_carrier_sha256']
  original=carrier.replace(b'\n',b'\r\n')
  assert sha256(original).hexdigest()==pins[key+'_sha256']
  (output/name).write_bytes(original)
  assert (output/name).read_bytes()==original
  result[name]=dict(carrier_sha256=sha256(carrier).hexdigest(),original_sha256=sha256(original).hexdigest(),
    original_bytes=len(original),crlf_count=original.count(b'\r\n'),terminal_crlf=original.endswith(b'\r\n'))
 return dict(status='PASS_EXACT_PR390_CRLF_SOURCE_RECONSTRUCTION',files=result,
             rule='Replace each LF in the pinned readable carrier with CRLF; verify the original SHA256 before execution or parsing.')

def build(source378,far_package,native_output):
 source378,far_package=Path(source378),Path(far_package)
 os.environ['OUTPUT_SHEAR_BASE']=str(source378.resolve())
 native_sources(native_output)
 prefix=load('source390_prefix',Path(native_output)/'prefix_source.py')
 alias=load('frozen_two_alias',far_package/'two_alias.py')
 z=(source378/'data/gcert1-e8-r783-far.json.gz').read_bytes()
 assert sha256(z).hexdigest()=='f2664ee7bcdfb55893abe9f1be8ee6a394a602e8262e611de2a0328bbd508aa7'
 selection=json.loads((Path(native_output)/'prefix_selection.json').read_bytes())
 c=prefix.transform(json.loads(gzip.decompress(z)),selection)
 assert sha256(raw(c)).hexdigest()=='ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a'
 steps=[]
 for d,u,want in [(706,268,'9f38e1500c91cbce0d8a62b4d86abb2f0420078f6a5611ed3708919c1f835188'),(707,323,'486bf3203d64ecca667b3ccb4ec56ca3644d93ffa8046876772e19ca3972cbd8')]:
  c,step=alias.build(c,d,u);assert sha256(raw(c)).hexdigest()==want
  step['output_sha256']=want;steps.append(step)
 for index,before,after,dest,donor in [(361,663,949,893,716),(387,676,948,891,725)]:
  assert c['B'][index]==['in',before,dest,[[donor,1,1]]]
  assert (len(c['frames'][before]),len(c['frames'][after]))==(6,5)
  c['B'][index][1]=after
 cur=c['start'].copy();H={k:Counter() for k in 'xysc'}
 def climb(r,f):
  assert alias.inside(tuple(c['frames'][cur[r]]),tuple(c['frames'][f]))
  d=len(c['frames'][f])-len(c['frames'][cur[r]])
  if d:H['x' if r<120 else 'y' if r<240 else 's'][d]+=1
  cur[r]=f
 for phase in ['A','B']:
  if phase=='B':
   for _,r,f in c['ret']:assert cur[r]==f;H['c'][len(c['frames'][f])]+=1
  for _,f,d,ss in c[phase]:
   for r in [d]+[x[0] for x in ss]:climb(r,f)
 for r,f in enumerate(c['final']):climb(r,f)
 c['blocks']={k:{str(r):n for r,n in sorted(h.items())}for k,h in H.items()}
 assert sum(r*n for h in H.values()for r,n in h.items())==c['N']
 out=raw(c);assert sha256(out).hexdigest()==FINAL
 return out,steps
if __name__=='__main__':
 assert len(sys.argv)==4,'SOURCE378 FROZEN_FAR_PACKAGE OUTPUT_JSON'
 out,steps=build(sys.argv[1],sys.argv[2],Path(sys.argv[3]).with_name(Path(sys.argv[3]).name+'-prefix-native'));Path(sys.argv[3]).write_bytes(out)
 print(json.dumps(dict(candidate_sha256=FINAL,steps=steps),indent=2))
