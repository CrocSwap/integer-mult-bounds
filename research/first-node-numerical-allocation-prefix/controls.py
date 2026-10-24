"""Actual source-prefix controls; all substitutions are explicitly labelled."""
import importlib,json,gzip,sys
from types import SimpleNamespace
from collections import Counter
import source_binding as binding
from ledger import BOUND,PHASES,capacities

def check(ok,msg):
 if not ok:raise RuntimeError(msg)

def modules(names):return SimpleNamespace(**{n:importlib.import_module(n) for n in names})
def state(a):return {k:(bytes(a.words[k].cells),a.words[k].head) for k in a.live}

class Observe:
 def __init__(self,m,arenas,phase):
  self.arenas=arenas;self.base=[len(a.live) for a in arenas];self.peak=[0,0];self.calls=[0,0]
  self.original=m.words.Arena.zero;self.m=m;self.phase=phase;self.sites=Counter();self.failed=[]
 def __enter__(self):
  def zero(a):
   if a in self.arenas:
    j=self.arenas.index(a);demand=len(a.live)+1;extra=demand-self.base[j]
    check(extra<=PHASES[self.phase][j],'proved phase prefix exceeded')
    self.peak[j]=max(self.peak[j],extra);self.calls[j]+=1
    f=sys._getframe(1);self.sites[f.f_code.co_filename.rsplit('/',1)[-1]+':'+f.f_code.co_name]+=1
    if not a.available and len(a.words)>=a.capacity:self.failed.append({'arena':j,'demand':demand,'capacity':a.capacity,'extra':extra})
   return self.original(a)
  self.m.words.Arena.zero=zero;return self
 def __exit__(self,*args):self.m.words.Arena.zero=self.original
 def receipt(self):return {'peak':self.peak,'requests':self.calls,'sites':dict(sorted(self.sites.items())),'failed_pending':self.failed}

def warm(a,n):
 values=[a.zero() for _ in range(max(0,n-len(a.words)))];a.free_many(*values)

def route_case(data,borrowed=0,warm_slots=0,quota=None):
 m=modules(['words','routes','directory','matrices','catalogue','low_codes'])
 a,i=m.words.Arena(5,60000),m.words.Arena(16,200);ring=m.words.Ring(a.input(9))
 ctx=SimpleNamespace(ring=ring,arena=a,raw=ring.raw,q=3,dimension=64,cap=a.literal(3))
 for _ in range(borrowed):a.literal(1);i.literal(1)
 warm(a,warm_slots);warm(i,80 if warm_slots else 0)
 geometry=json.loads(data['research/community-hyperplane599-audit/pr589/bit589/v9/nine/GEOMETRY.json'])
 template=json.loads(gzip.decompress(data['research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz']))
 call=template['calls'][32];role=1
 class Proxy:pass
 proxy=Proxy();proxy.geometry=geometry
 chart=m.catalogue.Catalogue.owner_chart(proxy,call,role);matrix=m.catalogue.Catalogue.chart_matrix(proxy,chart)
 check(any(x<0 for row in matrix for x in row),'actual selected chart has negative entries')
 low=tuple(tuple(int(r==c) for c in range(64)) for r in range(64));codes=m.low_codes.LowCodes(3,64,1)
 route=m.routes.compile_route(low,matrix,codes);arenas=(a,i);before=[state(x) for x in arenas]
 k=[len(x.words) for x in arenas];l=[len(x.live) for x in arenas];grant=capacities(k,l,[a.bits,i.bits])
 check(all(c>=n for c,n in zip(grant['capacities'],k)),'warm backing entry feasibility')
 for x,c in zip(arenas,grant['capacities']):x.capacity=c
 if quota is not None:a.capacity=l[0]+quota
 error=None;key_nonzero=None
 with Observe(m,arenas,'route') as obs:
  try:
   chart_words=m.matrices.Matrices(ring).constants(route.chart);high=m.directory.Odometer(ctx)
   key=m.routes.high_key(high.digits,route,chart_words,ctx)
   key_nonzero=sum(not w.zero() for row in key for w in row)
   m.matrices.Matrices(ring).free(key);high.close();m.matrices.Matrices(ring).free(chart_words)
  except ValueError as e:error=str(e)
 if quota is None:
  check(error is None and [state(x) for x in arenas]==before,'route normal restoration')
  check(key_nonzero==4,'actual negative chart high carry')
 else:check(error=='fixed register inventory' and len(obs.failed)==1,'actual route capacity guard')
 return dict(case='selected64_route_first_high_key',call=32,role=role,chart=list(chart.key),modulus=9,borrowed=borrowed,warm_slots=warm_slots,quota=quota,entry_allocated=k,entry_live=l,grant=grant,allocated_after=[len(x.words) for x in arenas],error=error,key_nonzero=key_nonzero,**obs.receipt())

def peel_case(data,borrowed=0,quota=None):
 m=modules(['words','records','peel','consumer','packet_engine','cardinal_counts','node'])
 a,i=m.words.Arena(3,60000),m.words.Arena(8,200);ring=m.words.Ring(a.input(3))
 ctx=SimpleNamespace(ring=ring,arena=a,raw=ring.raw,q=3,dimension=64,codes=SimpleNamespace(bits=8))
 class Specs(dict):
  def bind(self,*args):return self[0]
 specs=Specs({0:SimpleNamespace(code=0,good=True,template=SimpleNamespace(q=3,rank=1))})
 program=m.records.Program.fixture(i,a,65,2,[],code_bits=8)
 size,depth=i.literal(65),i.literal(0);incoming=m.consumer.IncomingWeights(ctx,i,program,specs,size,depth)
 for _ in range(borrowed):a.literal(1);i.literal(1)
 arenas=(a,i);before=[state(x) for x in arenas]
 with Observe(m,arenas,'constructor') as constructor:
  m.node.Node(ctx,i,program,size,depth,object(),object(),incoming)
 check([state(x) for x in arenas]==before,'actual Node constructor restoration')
 source,directory=m.records.Tape(),m.records.Tape();counts=[m.cardinal_counts.Count.literal(1) for _ in range(5)]
 k=[len(x.words) for x in arenas];l=[len(x.live) for x in arenas];grant=capacities(k,l,[a.bits,i.bits])
 check(all(c>=n for c,n in zip(grant['capacities'],k)),'warm backing entry feasibility')
 for x,c in zip(arenas,grant['capacities']):x.capacity=c
 if quota is not None:i.capacity=l[1]+quota
 events_seen=[];old=m.packet_engine.run
 def cut(src,events,layout,directory,prefixes,fields,coefficient,**kwargs):
  fibre=layout.fibre()
  try:
   for event in events:
    extents=layout.extents(event.second,event.first) if event.kind=='add' else layout.extents(event.first,event.second)
    for extent in extents:extent.close()
    row={'kind':event.kind}
    if event.kind=='add':
     value=coefficient(directory,event.request);row['negative_inverse']=event.request.negative_inverse;row['value']=value.inspect();a.free(value)
    events_seen.append(row)
   return src
  finally:fibre.close();events.close()
 m.packet_engine.run=cut;error=None
 try:
  with Observe(m,arenas,'peel') as obs:
   try:m.peel.run(source,ctx,i,size,depth,program,directory,*counts,incoming)
   except ValueError as e:error=str(e)
 finally:m.packet_engine.run=old
 if quota is None:
  check(error is None and [state(x) for x in arenas]==before,'peel normal restoration')
  check(len(events_seen)==8 and [r['value'] for r in events_seen if r['kind']=='add']==[2,1,2],'actual incoming negative inverse')
 else:check(error=='fixed register inventory' and len(obs.failed)==1,'actual peel capacity guard')
 return dict(case='actual_n65_peel_numerical_prefix',borrowed=borrowed,quota=quota,events=events_seen,entry_allocated=k,entry_live=l,grant=grant,constructor=constructor.receipt(),error=error,payload_executed=False,**obs.receipt())

def run(data):
 rows=[]
 for kwargs in ({},{'borrowed':3,'warm_slots':40000},{'quota':16389}):
  with binding.runtime(data):rows.append(route_case(data,**kwargs))
 for kwargs in ({},{'borrowed':4},{'quota':22}):
  with binding.runtime(data):rows.append(peel_case(data,**kwargs))
 check(rows[0]['peak']==rows[1]['peak'],'borrowed/warm-neutral extra route peak')
 check(rows[3]['peak']==rows[4]['peak'],'borrowed-neutral extra peel peak')
 check(rows[1]['grant']['capacities'][0]==40000,'warm backing dominates live grant')
 check(rows[2]['failed_pending'][0]['extra']==16390 and rows[5]['failed_pending'][0]['extra']==23,'pre-guard failing request retained')
 with binding.runtime(data):rows.append(local_case(data))
 return rows

def local_case(data):
 m=modules(['words','records','model','node','driver','directory','cardinal_counts'])
 catalogue=m.model.Catalogue();topology=m.model.Topology(catalogue)
 a,i=m.words.Arena(3,60000),m.words.Arena(8,200);ring=m.words.Ring(a.input(3));context=m.directory.Context(ring,catalogue.codes)
 size,depth=i.input(2),i.input(0);incoming=m.model.Incoming(context,i,(2,1));consumer=m.model.Consumer(context,i,object(),size,depth,catalogue,incoming)
 counts=[m.cardinal_counts.Count.literal(1) for _ in range(5)];old=m.records.Tape();families={j:m.records.Tape() for j in range(4)}
 for j,t in families.items():
  for k in range(48*81):t.append((j+k)%2)
  t.rewind()
 fibre=m.cardinal_counts.Count.literal(81);driver=m.driver.Driver(context,topology,consumer,old,counts[0],counts[1],counts[2],counts[3],fibre)
 before=[state(x) for x in (a,i)]
 with Observe(m,(a,i),'consumer_adapter') as obs:driver.local(families,topology.call(0,0),((1,0),(0,1)))
 check([state(x) for x in (a,i)]==before,'whole reduced local numerical restoration')
 return dict(case='complete_reduced_GL2_local_call',calls=dict(consumer.calls),children=dict(consumer.children),**obs.receipt())
