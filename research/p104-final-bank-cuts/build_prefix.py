"""Rebuild the pinned state before the two final bank changes."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import gzip,json,sys
SOURCE=Path(__file__).resolve().parent/'retained/source7776'
sys.path[:0]=[str(SOURCE),str(SOURCE/'retained/vendor')]
from network import Network,encoded,need
from graph_delta import restore_relays,rename_senders,apply
from bank_split import apply as bank
from public_split import split,rotate_all
from puncture import puncture,in_parallel_basis

def read(name):
 b=(SOURCE/name).read_bytes();return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def dump(net,frames):
 return dict(frames=frames,initial=net.initial,final=net.final,first_output=net.first_output,moves=[[k,*v]for k,v in sorted(net.moves.items())],forms=[[k,[[j,str(q)]for j,q in sorted(r.items())]]for k,r in sorted(net.forms.items())],schedule=net.schedule())
def digest(g):return sha256(encoded(g)).hexdigest()
def events(net,es):
 for e in es:
  if 'split' in e:
   if 'relabel_before_split' in e:
    old,new=e['relabel_before_split'];move=lambda x:new if x==old else x
    net=Network(net.first_output,list(map(move,net.initial)),list(map(move,net.final)),{k:tuple(map(move,v))for k,v in net.moves.items()},net.forms)
   net=split(net,e['split'])
  elif e.get('type')=='parallel_bank_puncture':
   n=net.transpose() if e['orientation'] else net
   n=in_parallel_basis(n,e['remove'],{j:F(q)for j,q in e['receive_direction']});n=puncture(n,e);net=n.transpose() if e['orientation'] else n
  elif 'transposed' in e:net=split(net,e)
  else:net=bank(net,e)
  net.schedule()
 return net

def build():
 g=read('GRAPH.json.gz');frames=g['frames'];s=read('PARENT-SOURCES.json');need(digest(g)=='c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84','original graph')
 net=Network(g['first_output'],g['initial'],g['final'],{k:(a,b)for k,a,b in g['moves']},{k:{j:F(q)for j,q in r}for k,r in g['forms']})
 for f in ['DELTA.json','STACK-DELTA.json']:
  raw=gzip.decompress((SOURCE/'relays'/(f+'.gz')).read_bytes());need(sha256(raw).hexdigest()==s['relays']['files'][f],'peer bytes');p=json.loads(raw);need(digest(g)==p['parent_graph_sha256'],'peer preimage');net=restore_relays(net,p);g=dump(net,frames);need(digest(g)==p['joint_graph_sha256'],'peer image')
 net=rename_senders(net,{int(i):j for i,j in s['relays']['new_sender_names'].items()});g=dump(net,frames);need(digest(g)==s['relays']['renamed_graph_sha256'],'sender rename')
 for j in [read('BANK-EDITS.json'),read('PUBLIC-EDITS.json')]+read('BASIS-EDITS.json.gz'):
  need(digest(g)==j['source_sha256'],'journal source');net=events(net,j['events']);g=dump(net,frames);need(digest(g)==j['output_sha256'],'journal image')
 edits=read('JOINT-EDITS.json.gz')
 for e in edits[:-1]:
  need(digest(g)==e['source'],'joint source')
  if 'events' in e:frames=frames+e.get('new_frames',[]);net=events(net,e['events'])
  elif 'rotations' in e:net=Network(net.first_output,net.initial,net.final,net.moves,rotate_all(net,e['rotations']))
  else:net=apply(net,e)
  g=dump(net,frames);need(digest(g)==e['result'],'joint result')
 need(digest(g)==edits[-1]['source'],'last input')
 return g,net,edits[-1]

if __name__=='__main__':
 from collections import Counter
 import time
 start=time.monotonic();g,net,last=build();print('BEFORE',digest(g),len(net.moves),'seconds',time.monotonic()-start)
 def profile(n):return Counter(abs(len(g['frames'][a])-len(g['frames'][b]))for a,b in n.moves.values())
 prior=profile(net)
 for event in last['events']:
  e=event['split'];print('CUT',e['old'],len(g['frames'][e['old']]),'to',e['new'],len(g['frames'][e['new']]),'routes',[(k,net.moves[k])for k in set(e['arrivals']+e['sends'])]);net=split(net,e);now=profile(net);print('DELTA',{r:now[r]-prior[r]for r in prior|now if now[r]!=prior[r]});prior=now
 print('AFTER',digest(dump(net,g['frames'])),last['result'],len(net.moves),'seconds',time.monotonic()-start)
