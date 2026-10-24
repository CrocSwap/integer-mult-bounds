"""Weak source-array identity observer; no simulated physical quota."""
from contextlib import contextmanager
import weakref,sys

class Census:
 def __init__(self,arenas):
  self.arenas=arenas;self.tapes=weakref.WeakValueDictionary();self.labels={};self.active=False
  self.peak=0;self.phase='setup';self.phases={};self.max_counts=0;self.record_sites=set()
 def sample(self):
  if not self.active:return
  tapes=list(self.tapes.items())
  total=sum(len(t.cells) for _,t in tapes)+sum((len(a.words)+1)*(a.bits+2) for a in self.arenas)
  self.peak=max(self.peak,total);self.phases[self.phase]=max(self.phases.get(self.phase,0),total)
  count=sum(1 for ident,_ in tapes if self.labels[ident][0] in ('cardinality','counts','cardinal_counts','stream') and self.labels[ident][1]!='add_pass')
  self.max_counts=max(self.max_counts,count)
 def start(self):
  self.baseline={ident:(bytes(t.cells),t.head) for ident,t in self.tapes.items()};self.active=True;self.sample();self.k0=self.peak

@contextmanager
def observed(m,arenas):
 c=Census(arenas);init,write,zero=m.records.Tape.__init__,m.records.Tape.write,m.words.Arena.zero
 def new(t):
  init(t);frame=sys._getframe(1);label=(frame.f_globals.get('__name__',''),frame.f_code.co_name,type(frame.f_locals.get('self')).__name__)
  c.tapes[id(t)]=t;c.labels[id(t)]=label
  if c.active:c.record_sites.add(label)
  c.sample()
 def put(t,s):
  n=len(t.cells);write(t,s)
  if len(t.cells)!=n:c.sample()
 def alloc(a):
  n=len(a.words);w=zero(a)
  if len(a.words)!=n:c.sample()
  return w
 try:
  m.records.Tape.__init__,m.records.Tape.write,m.words.Arena.zero=new,put,alloc
  yield c
 finally:m.records.Tape.__init__,m.records.Tape.write,m.words.Arena.zero=init,write,zero
