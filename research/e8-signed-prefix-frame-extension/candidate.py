"""One source-bound frame reduction after the unchanged signed25 reconstruction.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import copy,importlib.util,json
HERE=Path(__file__).resolve().parent
SOURCE='b3a4d85639801f4fa73b0e742c1e860d2e96aa43fb30daff875c5b009033df2b'
FINAL='4e84f869ce94f67d3d3419428d21117759a9e7482483786d79930a3d2e1a358b'
def base():
 s=importlib.util.spec_from_file_location('unchanged_signed25_candidate',HERE/'signed_candidate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
raw=lambda c:json.dumps(c,sort_keys=True,separators=(',',':')).encode()
def load(name,path):return base().load(name,path)
def native_sources(output,ordinary):return base().native_sources(output,ordinary)
def old_response(source378,far_package):return base().old_response(source378,far_package)
def inside(a,b):
 piv={}
 for x in b:
  while x:
   k=x.bit_length()-1
   if k in piv:x^=piv[k]
   else:piv[k]=x;break
 for x in a:
  while x:
   k=x.bit_length()-1
   if k not in piv:return False
   x^=piv[k]
 return True
def build(*args):
 encoded,steps=base().build(*args);assert sha256(encoded).hexdigest()==SOURCE
 c=json.loads(encoded);before=copy.deepcopy(c)
 assert len(c['A'])==1460 and c['B'][1566]==['in',203,201,[[491,1,2]]]
 assert len(c['frames'][203])==8 and len(c['frames'][942])==7
 c['B'][1566][1]=942
 cur=c['start'][:];H={k:Counter()for k in 'xysc'}
 def climb(r,f):
  assert inside(c['frames'][cur[r]],c['frames'][f]),(r,cur[r],f)
  d=len(c['frames'][f])-len(c['frames'][cur[r]]);assert d>=0
  if d:H['x'if r<c['v']else'y'if r<2*c['v']else's'][d]+=1
  cur[r]=f
 for phase in ['A','B']:
  if phase=='B':
   for _,r,f in c['ret']:assert cur[r]==f;H['c'][len(c['frames'][f])]+=1
  for g in c[phase]:
   for r in [g[2]]+[x[0]for x in g[3]]+(g[4]if g[0]=='out'else[]):climb(r,g[1])
 for r,f in enumerate(c['final']):climb(r,f)
 c['blocks']={k:{str(r):n for r,n in sorted(h.items())}for k,h in H.items()}
 assert sum(r*n for h in H.values()for r,n in h.items())==c['N']
 check=copy.deepcopy(c);check['B'][1566][1]=203;check['blocks']=before['blocks'];assert check==before
 delta={int(k):v-before['blocks']['s'].get(k,0)for k,v in c['blocks']['s'].items()if v!=before['blocks']['s'].get(k,0)};assert delta=={1:-2,2:1}
 encoded=raw(c);assert sha256(encoded).hexdigest()==FINAL
 witness=dict(phase='B',index=1566,global_index=3026,old_frame=203,new_frame=942,scalar_word_unchanged=True,histogram_delta=delta,source_sha256=SOURCE,output_sha256=FINAL)
 (Path(args[-1])/'FRAME.json').write_text(json.dumps(witness,sort_keys=True,indent=2)+'\n')
 return encoded,steps+[witness]
