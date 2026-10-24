import sys,hashlib,json,ast
import binding
from types import SimpleNamespace

def check(ok,message):
 if not ok:raise RuntimeError(message)

def run(v,m,GuardedConsumer,cases=None):
 source_path=binding.ROOT/'research/selected-bit-recursive-caller/predecessor/driver.py'
 tree=ast.parse(source_path.read_bytes());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Driver')
 method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='residual');namespace={}
 exec(compile(ast.Module(body=[method],type_ignores=[]),str(source_path),'exec'),namespace)
 results=[]
 for case in cases or ['residue_inventory','index_inventory','common_guard','old_code_guard','old_boundary_guard','geometry_after','layout_after','callback_before','program_guard','callback_after','frame_guard','success','two_prefixes','post_handoff']:
  f=v.caller_fixture(m,True,1,64,2,3);source=m.records.Tape();arenas=(f.residues,f.indices)
  if case=='two_prefixes':
   body=bytes(f.fields.tape.cells[1:]);f.fields.tape.cells.extend(body);f.counts[0]=m.cardinal_counts.Count.literal(2)
  if case=='residue_inventory':f.residues.capacity=len(f.residues.words)+5
  if case=='index_inventory':f.indices.capacity=len(f.indices.words)+5
  if case=='program_guard':f.program.tape.cells[-1]=m.records.WORD_END
  if case=='old_code_guard':f.fields.tape.cells[1]=m.words.RIGHT
  if case=='old_boundary_guard':
   pos=f.fields.tape.cells.index(m.records.RECORD_END);f.fields.tape.cells[pos]=m.records.WORD_END
  before=[v.state(a) for a in arenas]
  tapes=[source,f.fields.tape,f.program.tape,*[x.tape for x in f.counts],f.context.highs.tape]
  borrowed=[bytes(t.cells) for t in tapes];available=[list(a.available) for a in arenas]
  assigned=[];handoffs=[]
  def patch(obj,key,value):assigned.append((obj,key,getattr(obj,key)));setattr(obj,key,value)
  def packet(*a,**kw):
   check(a[0] is source,'source identity at handoff');handoffs.append({'directory_sha256':hashlib.sha256(a[3].cells).hexdigest(),'directory_cells':len(a[3].cells)})
   if case=='post_handoff':raise ValueError('post handoff sentinel')
   return source
  patch(m.packet_engine,'run',packet)
  mapping={'geometry_after':'Geometry','layout_after':'Layout','callback_before':'Callback','callback_after':'Callback'}
  if case in mapping:
   name=mapping[case];original=getattr(m.consumer,name)
   def fail(*args,**kwargs):
    if case.endswith('after'):original(*args,**kwargs)
    raise ValueError('constructor sentinel')
   patch(m.consumer,name,fail)
  if case=='frame_guard':
   original=m.consumer.need
   def guard(ok,message):
    if message=='selected node and encoded incoming frame agree':raise ValueError('frame guard sentinel')
    return original(ok,message)
   patch(m.consumer,'need',guard)
  guarded=GuardedConsumer(m,f.consumer);error=None
  proxy=SimpleNamespace(event=lambda *_:None,consumer=guarded,old_directory=f.fields.tape,old_count=f.counts[0],before=f.counts[1],gap=f.counts[2],suffix=f.counts[3])
  try:
   try:out=namespace['residual'](proxy,source,0,case!='common_guard',f.spec.low)
   except ValueError as e:error=e
  finally:
   for obj,key,value in reversed(assigned):setattr(obj,key,value)
  if case in ('success','two_prefixes'):check(error is None and out is source and len(handoffs)==1,'successful source handoff')
  else:check(error is not None,'expected intended rejection')
  if case not in ('success','two_prefixes','post_handoff'):
   check(guarded.last_report['state']=='rejected','setup rejection state')
   check(error.__context__ is None,'no retained source exception chain')
  check([v.state(a) for a in arenas]==before,'incoming live numerical bytes and heads restored')
  check([bytes(t.cells) for t in tapes]==borrowed,'borrowed Tape bytes preserved')
  check(all(t.head==1 for t in tapes),'borrowed Tape heads restored')
  check(all(set(a.available)==set(range(len(a.words)))-a.live for a in arenas),'complete free partition')
  results.append({'case':case,'error':None if error is None else str(error),'report':guarded.last_report,'handoffs':handoffs})
 return results
