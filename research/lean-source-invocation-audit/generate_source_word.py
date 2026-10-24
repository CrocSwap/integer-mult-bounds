"""Emit a kernel-checkable trajectory certificate; never trusted for its result.
The external source binding must compare this deterministic output with the
pinned compressed template. Every raw event contributes one Event, including
frame transitions (normalized to the identity by the scalar interpreter).
"""
from pathlib import Path
import argparse,gzip,json,hashlib
ap=argparse.ArgumentParser();ap.add_argument('template',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
x=json.loads(gzip.decompress(a.template.read_bytes()));e=x['local_programs']['forward'];assert len(e)==19002
assert len(x['calls'])==72
for z in e:
 assert all(type(v) is int for v in z)
 assert z[0] in range(4)
 assert len(z)==(7 if z[0]==2 or z[0]==3 else 6)
 assert z[-1]==0
 assert 0<=z[1]<987
 if z[0]==1: assert 0<=z[2]<=987 and z[1]!=z[2]
 if z[0]>=2: assert z[2]==987
N=(len(e)+199)//200
header='''import Std
/-!
Generated normalized execution certificate for the literal PR442 forward
local word. Frame operations are present but scalar no-ops; the physical
frame interpretation is a separate obligation. 987 original roles may be
dirty. Role987 is the algorithm's clean temporary, not arbitrary scratch.
This checks the all-zero trajectory and one helper input basis, not all
inputs. `checks` requires the clean temporary preconditions at copy/erase.
-/
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace ActualWord
structure Event where
  op : Nat
  x : Nat
  y : Nat
  odd : Bool

def put (s : Nat) (i : Nat) (v : Bool) : Nat :=
  if s.testBit i == v then s else s ^^^ (1 <<< i)

def scalarStep (s : Nat) (e : Event) : Nat :=
  match e.op with
  | 0 => s
  | 1 => if e.odd && s.testBit e.y then s ^^^ (1 <<< e.x) else s
  | 2 => put s e.y (s.testBit e.x)
  | _ => put s e.y false

def checks (s : Nat) (e : Event) : Bool :=
  match e.op with
  | 0 => e.x < 987
  | 1 => e.x < 987 && e.y <= 987 && e.x != e.y
  | 2 => e.x < 987 && e.y == 987 && !(s.testBit e.y)
  | 3 => e.x < 987 && e.y == 987 && (s.testBit e.x == s.testBit e.y)
  | _ => false

def step (s : Nat × Bool) (e : Event) : Nat × Bool :=
  (scalarStep s.1 e, s.2 && checks s.1 e)

def run (es : List Event) (s : Nat × Bool) := es.foldl step s

'''
pieces=[header]
for i in range(N):
 pieces.append('def chunk%d : List Event := [%s]\n'%(i,',\n'.join('⟨%s,%s,%s,%s⟩'%(z[0],z[1],z[2],str(bool(z[3]&1)).lower()) for z in e[i*200:(i+1)*200])))
pieces+=['def chunks : List (List Event) := ['+','.join('chunk%d'%i for i in range(N))+']',
 '''def runChunks : List (List Event) → (Nat × Bool) → (Nat × Bool)
  | [], s => s
  | es :: rest, s => runChunks rest (run es s)
theorem combine (es : List Event) (rest : List (List Event))
    (s t u : Nat × Bool) (h : run es s = t) (tail : runChunks rest t = u) :
    runChunks (es :: rest) s = u := by
  simp only [runChunks]
  rw [h]
  exact tail
def runAll (s : Nat × Bool) := runChunks chunks s''']
state=1<<243
pieces+=['def state0 : Nat × Bool := (%s, true)'%state]
for i in range(N):
 for z in e[i*200:(i+1)*200]:
  op,x,y=z[:3]
  if op==1 and z[3]&1 and (state>>y)&1:state^=1<<x
  if op==2:
   assert ((state>>y)&1)==0
   state=(state&~(1<<y))|(((state>>x)&1)<<y)
  if op==3:
   assert ((state>>y)&1)==((state>>x)&1)
   state&=~(1<<y)
 pieces+=['def state%d : Nat × Bool := (%s, true)'%(i+1,state),
 'theorem checkpoint%d : run chunk%d state%d = state%d := by decide'%(i,i,i,i+1),
 'theorem zero%d : run chunk%d (0,true) = (0,true) := by decide'%(i,i)]
pieces+=['def suffix%d : List (List Event) := []'%N]
for i in reversed(range(N)):
 pieces+=['def suffix%d : List (List Event) := chunk%d :: suffix%d'%(i,i,i+1)]
pieces+=['theorem finish%d : runChunks suffix%d state%d = state%d := rfl'%(N,N,N,N),
         'theorem finishZero%d : runChunks suffix%d (0,true) = (0,true) := rfl'%(N,N)]
for i in reversed(range(N)):
 pieces+=['theorem finish%d : runChunks suffix%d state%d = state%d :=\n  combine chunk%d suffix%d state%d state%d state%d checkpoint%d finish%d'%(i,i,i,N,i,i+1,i,i+1,N,i,i+1),
          'theorem finishZero%d : runChunks suffix%d (0,true) = (0,true) :=\n  combine chunk%d suffix%d (0,true) (0,true) (0,true) zero%d finishZero%d'%(i,i,i,i+1,i,i+1)]
pieces+=['theorem helper3_checked : runAll (1 <<< 243, true) = (1 <<< 243, true) := finish0',
         'theorem zero_checked : runAll (0, true) = (0, true) := finishZero0',
         'def runForward (s : Nat) := (runAll (s,true)).1',
         'theorem basis243_output : runForward (1 <<< 243) = 1 <<< 243 := congrArg Prod.fst helper3_checked',
         'theorem zero_output : runForward 0 = 0 := congrArg Prod.fst zero_checked',
         '#print axioms helper3_checked','#print axioms zero_checked',
         '#print axioms basis243_output','#print axioms zero_output','end ActualWord']
a.out.write_text('\n'.join(pieces)+'\n')
print(json.dumps({'raw_events':len(e),'chunks':N,'template_raw_sha256':hashlib.sha256(gzip.decompress(a.template.read_bytes())).hexdigest(),'word_canonical_sha256':hashlib.sha256(json.dumps(e,separators=(',',':')).encode()).hexdigest(),'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'size':a.out.stat().st_size}))
