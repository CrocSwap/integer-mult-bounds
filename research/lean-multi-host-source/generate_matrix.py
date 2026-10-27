"""Generate untrusted symbolic checkpoints for kernel verification.
Every event is retained; Python's matrix results are checked by Lean rfl.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
from flat_data import flat_list, split_nodes
ap=argparse.ArgumentParser();ap.add_argument('template',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
raw=gzip.decompress(a.template.read_bytes());assert hashlib.sha256(raw).hexdigest()=='dd7833dcaff8c84b258847f4c4d65b6402c702700ae37d2c464083ee37b24126'
es=json.loads(raw)['local_programs']['forward'];assert len(es)==19002
chunk_size=200;N=(len(es)+chunk_size-1)//chunk_size
nodes={};roots=[]
def tree(rows):
 key=('l',rows[0]) if len(rows)==1 else ('n',tree(rows[::2]),tree(rows[1::2]))
 return nodes.setdefault(key,len(nodes))
s=[1<<i for i in range(987)]+[0]*37;roots.append(tree(s))
for i,e in enumerate(es):
 op,x,y=e[:3];assert op in range(4) and 0<=x<987 and e[-1]==0
 assert len(e)==(7 if op>=2 else 6)
 if op==1:
  assert 0<=y<=987 and x!=y
  if e[3]&1:s[x]^=s[y]
 elif op==2:
  assert y==987 and s[y]==0;s[y]=s[x]
 elif op==3:
  assert y==987 and s[y]==s[x];s[y]=0
 if (i+1)%chunk_size==0 or i+1==len(es):roots.append(tree(s))
expected=[((1<<i)^((1<<(i-120)) if 120<=i<240 else 0)) for i in range(987)]+[0]*37
assert s==expected
header='''import TreeReplay
/-!
Generated source-bound data. The literal 19,002-event forward word is retained,
including frame events. Node definitions share immutable symbolic matrices;
leaf bit i denotes arbitrary original input variable i. Role 987 and unused
leaves 988..1023 start zero. Their physical interpretation is separate.
-/
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace SourceMatrix
open LinearReplay (Event)
open TreeReplay
'''
node_lines=[]
for key,n in nodes.items():
 if key[0]=='l':node_lines+=['def node%d : Tree Nat := .leaf %d'%(n,key[1])]
 else:node_lines+=['def node%d : Tree Nat := .node node%d node%d'%(n,key[1],key[2])]
last_node=split_nodes(a.out,'MatrixNodes','TreeReplay','SourceMatrix',node_lines)
lines=[header.replace('import TreeReplay',f'import {last_node}',1)]
for i,r in enumerate(roots):lines+=['def state%d : Tree Nat × Bool := (node%d, true)'%(i,r)]
lines+=['def initial : Tree Nat := node%d'%roots[0],'def expected : Tree Nat := node%d'%roots[-1]]
for i in range(N):
 lines+=flat_list(f'chunk{i}', 'Event', ['⟨%s,%s,%s,%s⟩'%(e[0],e[1],e[2],str(bool(e[3]&1)).lower())for e in es[i*chunk_size:(i+1)*chunk_size]])
lines+=['def forwardChunks : List (List Event) := ['+','.join('chunk%d'%i for i in range(N))+']',
'def forwardWord : List Event := forwardChunks.flatten','end SourceMatrix']
a.out.joinpath('MatrixData.lean').write_text('\n'.join(lines)+'\n')
lines=['''import MatrixData
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace SourceMatrix
open LinearReplay (Event)
open TreeReplay

def runCheckedChunks : List (List Event) → (Tree Nat × Bool) → (Tree Nat × Bool)
 | [], s => s
 | es :: rest, s => runCheckedChunks rest (runCheckedRows es s)

theorem combine (es : List Event) (rest : List (List Event))
    (s t u : Tree Nat × Bool) (h : runCheckedRows es s = t)
    (tail : runCheckedChunks rest t = u) : runCheckedChunks (es :: rest) s = u := by
  simp only [runCheckedChunks]
  rw [h]
  exact tail

theorem chunks_flatten (chunks : List (List Event)) (s : Tree Nat × Bool) :
    runCheckedChunks chunks s = runCheckedRows chunks.flatten s := by
  induction chunks generalizing s with
  | nil => rfl
  | cons es rest ih =>
    simp only [runCheckedChunks, ih, List.flatten_cons, runCheckedRows, List.foldl_append]
''']
for i in range(N):
 lines+=['theorem checkpoint%d : runCheckedRows chunk%d state%d = state%d := by rfl'%(i,i,i,i+1)]
lines+=['def suffix%d : List (List Event) := []'%N]
for i in reversed(range(N)):lines+=['def suffix%d : List (List Event) := chunk%d :: suffix%d'%(i,i,i+1)]
lines+=['theorem finish%d : runCheckedChunks suffix%d state%d = state%d := rfl'%(N,N,N,N)]
for i in reversed(range(N)):
 lines+=['theorem finish%d : runCheckedChunks suffix%d state%d = state%d :=\n  combine chunk%d suffix%d state%d state%d state%d checkpoint%d finish%d'%(i,i,i,N,i,i+1,i,i+1,N,i,i+1)]
lines+=['theorem runFull_checked : runCheckedChunks forwardChunks (initial,true) = (expected,true) := finish0']
prefix='\n'.join(lines)+'\n#print axioms runFull_checked\nend SourceMatrix\n'
a.out.joinpath('MatrixCheckpoints.lean').write_text(prefix)
wrapper='''import MatrixCheckpoints
namespace SourceMatrix
open TreeReplay

theorem literal_word_checked : runCheckedRows forwardWord (initial,true) = (expected,true) :=
  (chunks_flatten forwardChunks (initial,true)).symm.trans runFull_checked

theorem literal_word_rows : runRows forwardWord initial = expected :=
  (checked_projection forwardWord (initial,true)).symm.trans
    (congrArg Prod.fst literal_word_checked)

#print axioms literal_word_checked
#print axioms literal_word_rows
end SourceMatrix
'''
a.out.joinpath('MatrixCertificate.lean').write_text(wrapper)
print(json.dumps({'events':len(es),'chunks':N,'nodes':len(nodes),'sizes':{name:a.out.joinpath(name).stat().st_size for name in ['MatrixData.lean','MatrixCheckpoints.lean','MatrixCertificate.lean']}}))
