"""Two source-bound commuting-window edits after the frozen six-edit reconstruction.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import copy,importlib.util,json
HERE=Path(__file__).resolve().parent
SOURCE='c146daa0153a81f4050bc16bb607288233ee95085dd006688717ea2ecce2f79a'
FINAL='a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6'
def base():
 s=importlib.util.spec_from_file_location('unchanged_sixedit_candidate',HERE/'union_candidate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
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
 c=json.loads(encoded);before=copy.deepcopy(c);witness=[]
 def rehist():
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
  c['blocks']={k:{str(r):n for r,n in sorted(h.items())}for k,h in H.items()};assert sum(r*n for h in H.values()for r,n in h.items())==c['N']
 for a,order,expected in [(1489,[4,0,3,2,1],'414f7ded771407339f67c725594c43b0a64631a05435b49104ed0ee4f1a8b786'),(1638,[14]+list(range(14)),FINAL)]:
  old=copy.deepcopy(c['B'][a:a+len(order)]);assert len(old)==len(order)
  assert all(g[0]=='in' and 120<=g[2]<240 and all(s>=240 for s,_,_ in g[3])for g in old)
  # Every write is a target and every read is a helper. All shears commute.
  changed=copy.deepcopy([old[i]for i in order]);assert len(c['frames'][changed[0][1]])==8 and len(c['frames'][940])==7
  changed[0][1]=940;c['B'][a:a+len(order)]=changed;rehist()
  assert sha256(raw(c)).hexdigest()==expected
  witness.append(dict(phase='B',index=a,permutation=order,old=old,new=changed,output_sha256=expected,pairwise_commutation='Every gate writes only a target and reads only helpers.'))
 assert all(c[k]==before[k]for k in c if k not in ['B','blocks'])
 delta={k:{int(r):c['blocks'][k].get(r,0)-before['blocks'][k].get(r,0)for r in c['blocks'][k].keys()|before['blocks'][k].keys()if c['blocks'][k].get(r,0)!=before['blocks'][k].get(r,0)}for k in c['blocks']}
 assert delta=={'c':{},'x':{},'s':{1:-4,2:2},'y':{}}
 encoded=raw(c);assert sha256(encoded).hexdigest()==FINAL
 result=dict(source_sha256=SOURCE,output_sha256=FINAL,changes=witness,histogram_delta=delta,frames=len(c['frames']),scalar_order='Two additional commuting window permutations of five and fifteen ordinary gates, with new first frame940. The heterogeneous uncompute of helper403 is regenerated from its unchanged last source use, not copied as an ordinary gate.')
 (Path(args[-1])/'TWO-WINDOWS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 return encoded,steps+[result]
