"""Uniform packed Γ6 signed ±1 ADD/SUB; classical carry, new paid ABI.
Apache-2.0. Prepared with OpenAI Codex assistance. No runtime Word oracle.
"""
from pathlib import Path
import importlib.util,sys,hashlib
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.pycache_prefix=str(HERE/'_unwritten_cache')
if Path(sys.pycache_prefix).exists():raise ValueError('bytecode isolation path exists')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
if hashlib.sha256((HERE/'inputs/tape_graph.py').read_bytes()).hexdigest()!='7d3cee3e79ba5fe410e1a6b5f4cf6a2fbe5e274f838b798cd8860344ff258b54':raise ValueError('B1 source drift')
if hashlib.sha256((HERE/'inputs/machine.py').read_bytes()).hexdigest()!='ffe2677bb5b82932873cb08b05f890a1218070215ebe670a0b05079518e8baee':raise ValueError('literal interpreter source drift')
D=load('signed_add_dispatch',HERE/'inputs/tape_graph.py')
S,T,L,W,B=1,2,3,4,5
TAPES=6

def origin_one(g,t,after):return g.rewind(t,g.jump(after,((t,1),)))

def double_plus(g,bit,after):
 """W=n unary, B blank; return W=2n+bit, B blank, both at cell1."""
 finish=origin_one(g,W,origin_one(g,B,after))
 transfer=g.state('width-transfer')
 g.add(transfer,finish,tests=((B,'_'),))
 g.add(transfer,transfer,tests=((B,'1'),),writes=((B,'_'),(W,'1')),moves=((B,1),(W,1)))
 begin_transfer=origin_one(g,B,g.jump(transfer,((W,1),)))
 erase_old=g.rewind(W,begin_transfer,erase=True)
 append=g.jump(erase_old) if not bit else g.state('width-append')
 if bit:g.add(append,erase_old,writes=((B,'1'),),moves=((B,1),))
 loop=g.state('width-double');second=g.state('width-double-second')
 g.add(loop,append,tests=((W,'_'),))
 g.add(loop,second,tests=((W,'1'),),writes=((B,'1'),),moves=((B,1),))
 g.add(second,loop,writes=((B,'1'),),moves=((B,1),(W,1)))
 return loop

def forward_width(g,after):
 loop=g.state('width-forward')
 g.add(loop,after,tests=((W,'_'),))
 g.add(loop,loop,tests=((W,'1'),),moves=((W,1),(S,1),(T,1)))
 return loop

def primitive(g,name,arity,after,stages=None):
 if name not in ('ADD','SUB') or arity!=2:raise ValueError('fixed ±1 two-operand service')
 stages={} if stages is None else stages;sub=name=='SUB'
 # Successful private cleanup; source and target working copies are returned.
 done=g.rewind(S,g.rewind(T,g.rewind(L,g.rewind(B,after))))
 clear=g.state('retire-width')
 g.add(clear,g.rewind(W,done),tests=((W,'_'),))
 g.add(clear,clear,tests=((W,'1'),),writes=((W,'_'),),moves=((W,1),))
 cleanup=clear
 next_component=g.state('next-component');reject=g.state('true-overflow');g.rules[reject]=[]
 stages['overflow']=reject;stages['component_entry']=next_component
 # After arithmetic, heads are one cell left of this component; restore its
 # full width before considering the next component. All moves are paid.
 next_ready=origin_one(g,W,next_component)
 restore=forward_width(g,next_ready)
 restore=g.jump(restore,((S,1),(T,1),(W,1)))
 loops={c:g.state('carry-'+str(c)) for c in (0,1)}
 checks={(c,o):g.state('MSB-check') for c in (0,1) for o in (0,1)}
 for (c,overflow),state in checks.items():
  g.add(state,loops[c],tests=((W,'1'),))
  g.add(state,reject if overflow else restore,tests=((W,'^'),))
 for carry,state in loops.items():
  for s in (0,1):
   for t in (0,1):
    total=t+(1-s if sub else s)+carry;out=total%2;c=total//2
    overflow=int((t!=s if sub else t==s) and out!=t)
    g.add(state,checks[c,overflow],tests=((S,str(s)),(T,str(t))),writes=((T,str(out)),),moves=((S,-1),(T,-1),(W,-1)))
 lsb=g.jump(loops[1 if sub else 0],((S,-1),(T,-1),(W,-1)))
 seek=forward_width(g,lsb)
 g.add(next_component,cleanup,tests=((S,'|'),(T,'|')))
 for s in '01':
  for t in '01':g.add(next_component,seek,tests=((S,s),(T,t)))
 # Parse/compare all six positive Γ headers. Only fifth value is decoded.
 nxt=next_component
 for field in range(5,-1,-1):
  prefix=g.state('Gamma-prefix');pop=g.state('Gamma-pop');suffix=g.state('Gamma-suffix')
  g.add(prefix,prefix,tests=((S,'0'),(T,'0')),writes=((L,'1'),),moves=((S,1),(T,1),(L,1)))
  writes=((W,'1'),) if field==4 else ()
  g.add(prefix,pop,tests=((S,'1'),(T,'1')),writes=writes,moves=((S,1),(T,1),(L,-1)))
  g.add(pop,nxt,tests=((L,'^'),),moves=((L,1),))
  g.add(pop,suffix,tests=((L,'1'),),writes=((L,'_'),),moves=((L,-1),))
  for bit in (0,1):
   resume=g.jump(pop,((S,1),(T,1)))
   destination=double_plus(g,bit,resume) if field==4 else resume
   g.add(suffix,destination,tests=((S,str(bit)),(T,str(bit))))
  nxt=prefix
 entry=g.jump(nxt,tuple((t,1) for t in (S,T,L,W,B)))
 stages['entry']=entry;stages['return']=after
 return entry

def compile_home(operation,owners=(0,1),operand_indices=(0,1),productive_count=None):
 from collections import namedtuple
 Event=namedtuple('Event','service owners');stages={}
 if productive_count is None:productive_count=len(owners)
 active=tuple(owners[i] for i in operand_indices)
 g=D.compile_graph((Event(operation,active),),owners,productive_count=productive_count,
                  primitive=lambda g,n,a,k:primitive(g,n,a,k,stages))
 return g,stages
