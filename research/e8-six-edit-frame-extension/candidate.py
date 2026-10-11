"""Six source-bound edits after the unchanged frozen one-frame reconstruction.
Four commuting target-update triples and two upper-frame choices.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import copy,importlib.util,json
HERE=Path(__file__).resolve().parent
SOURCE='4e84f869ce94f67d3d3419428d21117759a9e7482483786d79930a3d2e1a358b'
FINAL='c146daa0153a81f4050bc16bb607288233ee95085dd006688717ea2ecce2f79a'
def base():
 s=importlib.util.spec_from_file_location('unchanged_oneframe_candidate',HERE/'frame_candidate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
raw=lambda c:json.dumps(c,sort_keys=True,separators=(',',':')).encode()
def load(name,path):return base().load(name,path)
def native_sources(output,ordinary):return base().native_sources(output,ordinary)
def old_response(source378,far_package):return base().old_response(source378,far_package)
def build(*args):
 ancestor=base();encoded,steps=ancestor.build(*args);assert sha256(encoded).hexdigest()==SOURCE
 c=json.loads(encoded);before=copy.deepcopy(c);witness=[]
 for a,frame in [(1405,937),(1448,921),(1518,927),(1658,938)]:
  triple=copy.deepcopy(c['B'][a:a+3]);assert len(triple)==3
  assert all(g[0]=='in'for g in triple)and len({g[2]for g in triple})==1
  target=triple[0][2];assert 120<=target<240
  assert all(target not in{s for s,_,_ in g[3]}and all(s>=240 for s,_,_ in g[3])for g in triple)
  assert len({g[1]for g in triple})==1 and len(c['frames'][triple[0][1]])==8 and len(c['frames'][frame])==7
  changed=copy.deepcopy([triple[2],triple[1],triple[0]]);changed[0][1]=frame;c['B'][a:a+3]=changed
  witness.append(dict(kind='commuting_triple',phase='B',indices=[a,a+1,a+2],old=triple,new=changed,pairwise_commutation='All three additions write the same target and none reads it; their helper-only source values are unchanged.'))
 for a,old,new,target,source,coefficient in [(1115,892,940,180,221,1),(1128,902,944,192,227,-1)]:
  expected=['in',old,target,[[source,coefficient,1]]];assert c['B'][a]==expected
  assert len(c['frames'][old])==6 and len(c['frames'][new])==7;c['B'][a][1]=new
  witness.append(dict(kind='upper_frame',phase='B',index=a,old=expected,new=copy.deepcopy(c['B'][a]),canonical_basis=c['frames'][new]))
 cur=c['start'][:];H={k:Counter()for k in 'xysc'}
 def climb(r,f):
  assert ancestor.inside(c['frames'][cur[r]],c['frames'][f]),(r,cur[r],f)
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
 assert all(c[k]==before[k]for k in c if k not in ['B','blocks'])
 delta={k:{int(r):c['blocks'][k].get(r,0)-before['blocks'][k].get(r,0)for r in c['blocks'][k].keys()|before['blocks'][k].keys()if c['blocks'][k].get(r,0)!=before['blocks'][k].get(r,0)}for k in c['blocks']}
 assert delta=={'c':{},'x':{},'s':{1:-8,2:4},'y':{1:6,2:-4,6:-2,7:2}}
 encoded=raw(c);assert sha256(encoded).hexdigest()==FINAL
 result=dict(source_sha256=SOURCE,output_sha256=FINAL,changes=witness,histogram_delta=delta,frames=len(c['frames']),scalar_order='Four local commuting triple permutations; all other scalar order and every coefficient unchanged. Helper/source subword unchanged.')
 (Path(args[-1])/'SIX-EDITS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 return encoded,steps+[result]
