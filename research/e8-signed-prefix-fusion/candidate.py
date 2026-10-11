"""Exact pinned PR395 signed-prefix source, inherited aliases and two frame edits.
Prepared with OpenAI Codex assistance; Apache-2.0. See NOTICE.md.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import gzip,importlib.util,json,os,shutil
HERE=Path(__file__).resolve().parent
FINAL='b3a4d85639801f4fa73b0e742c1e860d2e96aa43fb30daff875c5b009033df2b'
raw=lambda c:json.dumps(c,sort_keys=True,separators=(',',':')).encode()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def native_sources(output,ordinary):
 output=Path(output);assert not output.exists();output.mkdir()
 old=load('signed_prefix_native_ancestor',Path(ordinary)/'candidate.py')
 report=old.native_sources(output/'prefix-native')
 code=output/'e8-prefix-restoration/code';code.mkdir(parents=True)
 shutil.copyfile(output/'prefix-native/prefix_source.py',code/'bit-complex-output-shear-pack.py')
 target=output/'e8-signed-prefix';target.mkdir();pins=json.loads((HERE/'PR395-SOURCE.json').read_text());files={}
 for name,pin in pins['files'].items():
  carrier=(HERE/name).read_bytes();assert b'\r'not in carrier and sha256(carrier).hexdigest()==pin['carrier_sha256']
  assert carrier.endswith(b'\n')
  logical=carrier if pin['source_terminal_lf']else carrier[:-1]
  rows=logical.splitlines(keepends=True);assert pin['crlf_lines']==sorted(set(pin['crlf_lines']))
  assert all(1<=i<=len(rows)and rows[i-1].endswith(b'\n')for i in pin['crlf_lines'])
  source=b''.join(x[:-1]+b'\r\n'if i in pin['crlf_lines']else x for i,x in enumerate(rows,1))
  assert len(source)==pin['source_bytes']and sha256(source).hexdigest()==pin['source_sha256']
  (target/pin['source_path']).write_bytes(source)
  files[name]=dict(source_sha256=pin['source_sha256'],carrier_sha256=pin['carrier_sha256'])
 return dict(status='PASS_EXACT_PR395_SOURCE_CARRIERS',commit=pins['commit'],files=files,ancestor=report)
def old_response(source378,far_package):
 z=(Path(source378)/'data/gcert1-e8-r783-far.json.gz').read_bytes()
 assert sha256(z).hexdigest()=='f2664ee7bcdfb55893abe9f1be8ee6a394a602e8262e611de2a0328bbd508aa7'
 alias=load('signed_prefix_old_alias',Path(far_package)/'two_alias.py');c=json.loads(gzip.decompress(z))
 for d,u in [(706,268),(707,323)]:c,_=alias.build(c,d,u)
 data=raw(c);assert sha256(data).hexdigest()=='d14ea8bf581d9f5ea8f3261e614199386d71ea4cbc8bc48d6bec371954669daf';return data
def build(source378,far_package,ordinary,sources390,native_output):
 source378,far_package,sources390,native_output=map(Path,[source378,far_package,sources390,native_output])
 native_sources(native_output,ordinary)
 data=native_output/'e8-prefix-restoration/data';data.mkdir()
 for name in ['prefix18.json.gz','sink-audit.json']:shutil.copyfile(sources390/'data'/name,data/name)
 os.environ['OUTPUT_SHEAR_BASE']=str(source378.resolve())
 signed=load('pinned_signed395',native_output/'e8-signed-prefix/construct.py')
 discovery=signed.emit(native_output/'upstream-discovery')
 assert discovery['status']=='PASS_SIGNED_PREFIX_RAW_OPERATOR_AND_CONTROLS'and len(discovery['negative_controls'])==4
 c=json.loads((native_output/'upstream-discovery/candidate.json').read_bytes())
 assert sha256(raw(c)).hexdigest()=='1b096c5c2c8336205172cb4733a4c36f12fffd0ad5a72e9e2bc50899075840ae'
 alias=load('signed_prefix_alias',far_package/'two_alias.py');steps=[]
 for d,u,want in [(706,268,'aa14f57bbe722405754e9cd7b548de9c48f5c1fe60804080a8dcaa5ed9e1e596'),(707,323,'c26cf9f36bda1d2fa73de2f6214cb526cb2b5e506ebad47966c1e494d35cf9f9')]:
  c,step=alias.build(c,d,u);step['output_sha256']=sha256(raw(c)).hexdigest();assert step['output_sha256']==want;steps.append(step)
 for index,before,after,dest,donor in [(367,663,949,893,716),(393,676,948,891,725)]:
  assert c['B'][index]==['in',before,dest,[[donor,1,1]]]
  assert(len(c['frames'][before]),len(c['frames'][after]))==(6,5);c['B'][index][1]=after
 cur=c['start'].copy();H={k:Counter()for k in 'xysc'}
 def climb(r,f):
  assert alias.inside(tuple(c['frames'][cur[r]]),tuple(c['frames'][f]))
  d=len(c['frames'][f])-len(c['frames'][cur[r]])
  if d:H['x'if r<120 else 'y'if r<240 else 's'][d]+=1
  cur[r]=f
 for phase in ['A','B']:
  if phase=='B':
   for _,r,f in c['ret']:assert cur[r]==f;H['c'][len(c['frames'][f])]+=1
  for _,f,d,ss in c[phase]:
   for r in [d]+[x[0]for x in ss]:climb(r,f)
 for r,f in enumerate(c['final']):climb(r,f)
 c['blocks']={k:{str(r):n for r,n in sorted(h.items())}for k,h in H.items()}
 assert sum(r*n for h in H.values()for r,n in h.items())==c['N']
 encoded=raw(c);assert sha256(encoded).hexdigest()==FINAL
 return encoded,steps
