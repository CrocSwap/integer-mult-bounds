"""Emit actual frame-label trajectory certificate and scalar-word identity.
The generator is untrusted: Lean checks every checkpoint and every scalar
projection chunk. Bind these raw entries to the original event JSON in replay.
"""
import argparse,gzip,json,hashlib
from pathlib import Path
from flat_data import flat_list, split_nodes
p=argparse.ArgumentParser();p.add_argument('template',type=Path);p.add_argument('states',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
t=json.loads(gzip.decompress(a.template.read_bytes()));states=json.loads(a.states.read_bytes());word=t['local_programs']['forward'];assert len(word)==19002
entries=[]
for e in word:
 op,x,y,c,f=e[:5];assert op in range(4)
 if op==0:old,new,rank=y,c,f
 elif op==1:old,new,rank=f,f,0
 else:old,new,rank=c,f,e[5]
 entries.append((op,x,y,bool(c&1),old,new,rank))
cur=[states['initial'][str(i)] for i in range(987)]+[0]*37;center=None;snaps=[(cur[:],center)]
for k,e in enumerate(entries):
 op,x,y,odd,old,new,rank=e
 assert x<987
 if op==0:
  assert cur[x]==old and center!=x;cur[x]=new
 elif op==1:
  assert y<=987 and x!=y and cur[x]==cur[y]==old and center!=x and(y!=987 or center is not None)
 elif op==2:
  assert y==987 and cur[x]==old and center is None and rank==8;cur[y]=new;center=x
 else:
  assert y==987 and cur[x]==old and cur[y]==new and center==x and rank==0;cur[y]=0;center=None
 if (k+1)%200==0 or k+1==len(entries):snaps.append((cur[:],center))
assert cur[:987]==[states['final'][str(i)]for i in range(987)] and center is None and cur[987:]==[0]*37
# Hash-cons only the96checkpoint trees, not an asserted computation result.
nodes=[];cache={}
def intern(xs):
 key=('leaf',xs[0])if len(xs)==1 else('node',intern(xs[::2]),intern(xs[1::2]))
 if key not in cache:cache[key]=len(nodes);nodes.append(key)
 return cache[key]
roots=[intern(xs)for xs,_ in snaps]
defs=['import FrameTraceCore','set_option maxRecDepth 100000','set_option maxHeartbeats 0','namespace SourceFrameTrace','open FrameTrace','open TreeReplay (Tree)']
checks=['import FrameTraceLiterals','import MatrixData','set_option maxRecDepth 100000','set_option maxHeartbeats 0','namespace SourceFrameTrace','open FrameTrace','open TreeReplay (Tree)']
cert=['import FrameTraceCheckpoints','set_option maxRecDepth 100000','set_option maxHeartbeats 0','namespace SourceFrameTrace','open FrameTrace','open TreeReplay (Tree)']
node_lines=[f'def node{i} : Tree Nat := '+(f'.leaf {n[1]}'if n[0]=='leaf'else f'.node node{n[1]} node{n[2]}') for i,n in enumerate(nodes)]
last_node=split_nodes(a.out.parent,'FrameTraceNodes','FrameTraceCore','SourceFrameTrace',node_lines)
defs[0]=f'import {last_node}'
for i,(_,center)in enumerate(snaps):defs.append(f'def state{i} : State := ⟨node{roots[i]}, '+('none'if center is None else f'some {center}')+'⟩')
N=len(snaps)-1
checks.append('theorem initial_tabulate : Tree.tabulate 10 (fun i => state0.frames.get i) = state0.frames := by decide +kernel')
checks.append(f'theorem final_tabulate : Tree.tabulate 10 (fun i => state{N}.frames.get i) = state{N}.frames := by decide +kernel')
for i in range(N):
 es=entries[200*i:200*(i+1)];defs.extend(flat_list(f'chunk{i}', 'Entry', ['⟨⟨%d,%d,%d,%s⟩,%d,%d,%d⟩'%(op,x,y,str(odd).lower(),old,new,rank)for op,x,y,odd,old,new,rank in es]))
 checks.append(f'theorem project{i} : chunk{i}.map Entry.scalar = SourceMatrix.chunk{i} := rfl')
 checks.append(f'theorem checkpoint{i} : runChecked chunk{i} (state{i},true) = (state{i+1},true) := by decide +kernel')
defs.append('def chunks : List (List Entry) := ['+','.join(f'chunk{i}'for i in range(N))+']')
defs.append('def forward : List Entry := chunks.flatten')
cert.append('theorem scalar_word : forward.map Entry.scalar = SourceMatrix.forwardWord := by\n  simp only [forward, chunks, List.flatten_cons, List.flatten_nil, List.map_append, List.map_nil, '+', '.join(f'project{i}'for i in range(N))+', SourceMatrix.forwardWord, SourceMatrix.forwardChunks]')
checks.append('theorem combine (p q : List Entry) (s t u : State × Bool) (h : runChecked p s = t) (k : runChecked q t = u) : runChecked (p ++ q) s = u := by\n  simp only [runChecked, List.foldl_append]\n  rw [show List.foldl checkedStep s p = t from h]\n  exact k')
defs.append(f'def suffix{N} : List Entry := []')
for i in reversed(range(N)):defs.append(f'def suffix{i} : List Entry := chunk{i} ++ suffix{i+1}')
checks.append(f'theorem finish{N} : runChecked suffix{N} (state{N},true) = (state{N},true) := rfl')
for i in reversed(range(N)):checks.append(f'theorem finish{i} : runChecked suffix{i} (state{i},true) = (state{N},true) := combine chunk{i} suffix{i+1} (state{i},true) (state{i+1},true) (state{N},true) checkpoint{i} finish{i+1}')
cert+=['theorem forward_checked : runChecked forward (state0,true) = (state96,true) := finish0','theorem forward_valid : Valid forward state0 := checked_valid forward (state0,true) (congrArg Prod.snd forward_checked)','#print axioms scalar_word','#print axioms forward_checked','#print axioms forward_valid']
outputs={a.out.with_name('FrameTraceLiterals.lean'):defs,a.out.with_name('FrameTraceCheckpoints.lean'):checks,a.out:cert}
for path,lines in outputs.items():path.write_text('\n'.join(lines+['end SourceFrameTrace'])+'\n')
print(json.dumps({'events':len(entries),'chunks':N,'nodes':len(nodes),'source_word_sha256':hashlib.sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest(),'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in outputs}}))
