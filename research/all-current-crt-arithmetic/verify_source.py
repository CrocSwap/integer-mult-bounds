"""Actual-source closure tests. All old arithmetic providers are unavailable.

Oracles, snapshots and counterfactuals are verifier-only and never providers.
"""
from pathlib import Path
from contextlib import contextmanager
from collections import Counter
import types,sys,json
HERE=Path(__file__).resolve().parent
def load(path,name):
 m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def need(x,s):
 if not x:raise ValueError(s)
PROVIDERS=('compare','add','subtract','divmod')
@contextmanager
def old_spy(base,m):
 original={n:getattr(m.w.Unsigned,n) for n in PROVIDERS};depth=0
 info={'calls':Counter(),'actions':0,'meters':{},'nested_calls':Counter()}
 def wrap(name):
  def call(raw,*args):
   nonlocal depth
   meter=raw.arena.meter;outer=depth==0;before=base.meter_actions(meter)
   info['calls' if outer else 'nested_calls'][name]+=1;info['meters'][id(meter)]=meter;depth+=1
   try:return original[name](raw,*args)
   finally:
    depth-=1
    if outer:info['actions']+=base.meter_actions(meter)-before
  return call
 for n in PROVIDERS:setattr(m.w.Unsigned,n,wrap(n))
 try:yield info
 finally:
  for n in PROVIDERS:setattr(m.w.Unsigned,n,original[n])
@contextmanager
def blocked(m,counter):
 names=(*PROVIDERS,'shift_add_bit');original={n:getattr(m.w.Unsigned,n) for n in names}
 def unavailable(*args,**kwargs):counter['calls']+=1;raise ValueError('OLD_ARITHMETIC_PROVIDER_UNAVAILABLE')
 for n in names:setattr(m.w.Unsigned,n,unavailable)
 try:yield
 finally:
  for n in names:setattr(m.w.Unsigned,n,original[n])

def observer_class(prior):
 class Observer(prior.Observations):
  def __init__(self,*args):super().__init__(*args);self.simple=[];self.pending_simple=None
  def __call__(self,stage,b,a,n,d,out):
   if stage=='arithmetic_before':
    self.pending_simple=(prior.snapshot(a),b.program.numeric_actions,b.simple_kind,n.slot,d.slot);return
   if stage=='arithmetic_after':
    before,native,kind,ns,ds=self.pending_simple;after=prior.snapshot(a);w=self.m.w;p=n.cells.index(w.RIGHT,1)-1
    x,y=prior.value(before['cells'][ns],w),prior.value(before['cells'][ds],w)
    if kind=='COMPARE':
     need(out==((x>y)-(x<y)),'direct comparison oracle');q=None
     need(after['live']==before['live'] and after['available']==before['available'],'comparison has no allocation')
    else:
     q,flag=out;z=x+y if kind=='ADD' else x-y
     need(flag==(int(z>=1<<p) if kind=='ADD' else int(z<0)) and prior.value(q.cells,w)==z%(1<<p),'direct sum/difference and finite flag oracle')
     need(q.slot==before['available'][-1] and after['available']==before['available'][:-1] and after['live']==before['live']|{q.slot},'exact one-output owner relation')
     need(q.head==1 and bytes(q.cells[p+2:])==before['cells'][q.slot][p+2:] and q.cells[0]==w.LEFT,'output head/guard/history')
    for slot in range(64):
     need(after['identities'][slot]==before['identities'][slot],'all real backing/head identities')
     if q is None or slot!=q.slot:need((after['cells'][slot],after['heads'][slot])==(before['cells'][slot],before['heads'][slot]),'all incoming live/free contents and heads')
    need(after['template']==before['template'] and after['template_head']==before['template_head'],'unused template preserved')
    need(after['arena_actions']-before['arena_actions']==b.program.numeric_actions-native and after['port_actions']==before['port_actions'],'new simple primitive meter included once')
    entry=b.simple_calls[-1];slope,constant=((125,388) if ns==ds else(247,602)) if kind=='COMPARE' else((279,735) if ns==ds else(401,949))
    need(entry['instructions']==slope*p+constant,'exact source-call physical count')
    self.simple.append({'kind':kind,'p':p,'alias':ns==ds,'slots':entry['slots'],'instructions':entry['instructions']+124,'flag':out if q is None else out[1]})
    self.pending_simple=None;return
   super().__call__(stage,b,a,n,d,out)
   if stage=='producer_before':self.producers[-1]['simple_start']=len(self.simple)
   elif stage=='producer_after':
    row=self.producers[-1];p=row['p'];left,right=len(row['left']),len(row['right']);e=row['euclidean_divisions'];simple=self.simple[row['simple_start']:]
    cap=(6*p+3)*e+left*(10*p+7)+right*(8*p+6)
    need(len(simple)<=cap<=(p-2)*(12*p*p+22*p+10),'complete universal nondivision call bound')
    row.update(simple_calls=len(simple),simple_counts=dict(Counter(x['kind'] for x in simple)),aliased_calls=sum(x['alias'] for x in simple),simple_instructions=sum(x['instructions'] for x in simple))
 return Observer
def check_counts(binder,observed,machine,old):
 counts=Counter({'divmod':binder.raw_calls})
 counts.update({'compare':sum(x['kind']=='COMPARE' for x in observed.simple),'add':sum(x['kind']=='ADD' for x in observed.simple),'subtract':sum(x['kind']=='SUBTRACT' for x in observed.simple)})
 need(counts==old['calls'],'every exact source provider call replaced')
 need(binder.raw_calls==binder.replacements==len(observed.calls),'every division replaced')
 need(binder.finite_control_invoice==256+32*binder.invocations+16400*binder.raw_calls+16408*len(observed.simple),'complete fixed metadata/finite flag invoice')
 need(machine.total==89+sum(x['instructions']+124 for x in binder.calls)+sum(x['instructions'] for x in observed.simple),'all literal setup/setters/entries counted')
 return dict(counts)

def full_source(prior,base,m,hw,Binding,c,l,meta,Observer,old_div,counter):
 m.fixture=dict(m.fixture,widths=[3,3,4,4],moduli=[5,7,13,8],initial=[1,2,12,7]);base.TAGS=tuple(range(1,17))
 reference,_,_=base.initial_fixture(m);baseline_bills=[];forward=None
 for reverse in(False,True):
  before=base.meter_actions(reference.meter);endpoint=m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,m.subtractive if reverse else m.numeric,m.owner,m.bridge,reference)
  it=endpoint.iterator;physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
  with old_spy(base,m) as bill:
   with base.seal_numerical_roles(m):endpoint.run()
  native=sum(base.meter_actions(t.meter) for t in(reference,*physical))-before+sum(base.meter_actions(t) for t in bill['meters'].values())
  baseline_bills.append({'source_actions':native,'arithmetic_actions':bill['actions'],'calls':dict(bill['calls']),'nested_calls':dict(bill['nested_calls'])})
  if not reverse:forward=bytes(reference.cells)
 source,_,_=base.initial_fixture(m);original=(bytes(source.cells),source.head);legs=[];relations=[]
 for reverse in(False,True):
  before=base.meter_actions(source.meter);endpoint=m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,m.subtractive if reverse else m.numeric,m.owner,m.bridge,source)
  it=endpoint.iterator;private=tuple(m.join.Tape() for _ in range(4));physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
  machine=hw.Program(c,l,meta);observed=Observer(m,reverse);binder=Binding(machine,hw,observed);binder.attach(it,private)
  with blocked(m,counter):
   with binder.install(m),base.seal_numerical_roles(m):endpoint.run()
  need(counter['calls']==0 and it.closed and not it.live and not it.bank.busy,'complete literal-source traversal')
  need(all(t.head==1 and all(s==m.w.BLANK for s in t.cells) for t in physical),'all original physical histories retired')
  need(all(t.head==0 and all(s=='_' for s in t.cells) for t in private),'descriptor histories retired')
  need(len({id(t.cells) for t in(*physical,*private)})==len(physical)+4,'disjoint actual owner union')
  need(any(len(row['left'])>1 for row in observed.producers),'actual nonleaf each direction')
  native=sum(base.meter_actions(t.meter) for t in(source,*physical))-before+sum(base.meter_actions(t) for t in observed.arena_meters)
  old=baseline_bills[int(reverse)];need(native-machine.numeric_actions==old['source_actions']-old['arithmetic_actions'],'exact outermost-only arithmetic action subtraction')
  need(sum(t.actions for t in private)==machine.selector_actions,'exact descriptor action equality')
  counts=check_counts(binder,observed,machine,old);relations.extend(prior.counterfactuals(m,old_div,observed))
  legs.append({'reverse':reverse,'calls':counts,'literal_instructions':machine.total,'literal_numeric_actions':machine.numeric_actions,'literal_selector_actions':machine.selector_actions,'remaining_source_actions':native-machine.numeric_actions,'finite_metadata_invoice':binder.finite_control_invoice,'grant_extra_cells':28,'physical_roles':len(physical)+4,'retained_cells':sum(len(t.cells) for t in(*physical,*private)),'simple_alias_calls':sum(x['alias'] for x in observed.simple),'producers':observed.producers})
  if not reverse:need(bytes(source.cells)==forward,'unchanged complete forward source')
 need((bytes(source.cells),source.head)==original,'full source inverse roundtrip')
 return {'directions':legs,'baseline':baseline_bills,'roundtrip':True},relations

def payload(prior,base,m,hh,caller,point_code,point_labels,point_meta,hjoin,old_binding,hw,Binding,c,l,meta,raw,Observer,old_div,counter):
 m.fixture=dict(m.fixture,widths=[3,3,2,2],moduli=[5,7,2,3],initial=[1,2,2,3]);base.TAGS=tuple(range(1,5))
 old_leg=caller.run_leg;os,op,_=base.initial_fixture(m);point=hh.Program(point_code,point_labels,point_meta);baseline=[];forward=None
 for reverse in(False,True):
  before=point.native_actions
  with old_spy(base,m) as bill:r,_=old_leg(m,base,point,os,op,reverse)
  r['remaining_source_actions']=r['encoded_source_symbol_actions']-(point.native_actions-before)
  r.update(arithmetic_actions=bill['actions'],calls=dict(bill['calls']),nested_calls=dict(bill['nested_calls']));baseline.append(r)
  if not reverse:forward=(bytes(os.cells),dict(op.cells))
 source,data,_=base.initial_fixture(m);original=(bytes(source.cells),source.head,dict(data.cells),data.head);point=hh.Program(point_code,point_labels,point_meta);legs=[];owners=[];relations=[]
 for reverse in(False,True):
  machine=hw.Program(c,l,meta);observed=Observer(m,reverse);binder=Binding(machine,hw,observed);changed,_=old_binding.join(hjoin,caller,binder,raw);before=point.native_actions
  with blocked(m,counter):r,stock=changed.run_leg(m,base,point,source,data,reverse)
  need(counter['calls']==0,'no old provider in actual source/payload execution');old=baseline[int(reverse)]
  native=r.pop('encoded_source_symbol_actions')-(point.native_actions-before)-machine.numeric_actions
  need(native==old['remaining_source_actions']-old['arithmetic_actions'],'exact payload-call outermost arithmetic subtraction')
  marker=r.pop('outer_adapter_symbol_actions')-machine.selector_actions;need(marker==old['outer_adapter_symbol_actions'],'same-width retained marker bill')
  counts=check_counts(binder,observed,machine,old);relations.extend(prior.counterfactuals(m,old_div,observed))
  r.update(calls=counts,literal_instructions=machine.total,literal_numeric_actions=machine.numeric_actions,literal_selector_actions=machine.selector_actions,remaining_source_actions=native,remaining_marker_actions=marker,finite_metadata_invoice=binder.finite_control_invoice,grant_extra_cells=28,simple_alias_calls=sum(x['alias'] for x in observed.simple),producers=observed.producers)
  legs.append(r);owners.extend(stock[0])
  if not reverse:need((bytes(source.cells),dict(data.cells))==forward,'unchanged actual forward source/payload')
 need((bytes(source.cells),source.head,dict(data.cells),data.head)==original,'full source/payload/key inverse roundtrip')
 need(len(owners)==len({id(x) for x in owners})==200,'actual retained payload caller owners')
 return {'directions':legs,'baseline':baseline,'roundtrip':True,'physical_roles_per_leg':100,'retained_cells':sum(map(len,owners))},relations
def controls(base,m,hw,Binding,c,l,meta,old_binding,all_divisions,counter):
 source,_,_=base.initial_fixture(m);endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
 machine=hw.Program(c,l,meta);binder=Binding(machine,hw);binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)));found=[]
 with binder.install(m):
  for name in PROVIDERS:
   for active in(False,True):
    binder.active=active;binder.active_arena=object() if active else None
    try:getattr(m.w.Unsigned(object()),name)(None,None)
    except ValueError as error:need('active exact current producer' in str(error),'precise scope rejection');found.append(name+('_foreign' if active else '_outside'))
    else:raise ValueError('out-of-scope provider escaped')
    finally:binder.active=False;binder.active_arena=None
 need(machine.total==0,'scope guards precede physical actions');endpoint.iterator.close()
 raw=(HERE/'binding.py').read_text();needle='return owner.simple(raw,a,b,kind)';need(raw.count(needle)==1,'one simple provider dispatch')
 replacement="return original[{'COMPARE':'compare','ADD':'add','SUBTRACT':'subtract'}[kind]](raw,a,b)"
 bad=types.ModuleType('B12_fallback_mutation');exec(compile(raw.replace(needle,replacement),'<deliberate provider fallback>','exec'),bad.__dict__)
 Bad=bad.make_binding(old_binding,all_divisions);source,_,_=base.initial_fixture(m);endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
 binder=Bad(hw.Program(c,l,meta),hw);binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)))
 with blocked(m,counter):
  try:
   with binder.install(m),base.seal_numerical_roles(m):endpoint.run()
  except ValueError as error:need('OLD_ARITHMETIC_PROVIDER_UNAVAILABLE' in str(error),'actual source fallback sentinel')
  else:raise ValueError('fallback mutation escaped')
 found.append('actual_old_provider_fallback');return found

def main():
 prior=load(HERE/'inputs/all-divisions/verify.py','B12_prior')
 previous,base,m,hh,caller,pc,pl,pm,hjoin,d,hw,old_binding,_,dc,dl,dm,raw=prior.modules()
 del dc,dl,dm
 all_divisions=load(HERE/'inputs/all-divisions/all_binding.py','B12_all_divisions');binding=load(HERE/'binding.py','B12_binding');arithmetic=load(HERE/'arithmetic.py','B12_arithmetic')
 Binding=binding.make_binding(old_binding,all_divisions);c,l,meta=arithmetic.compile_arithmetic(d);Observer=observer_class(prior);old_div=m.w.Unsigned.divmod;counter={'calls':0}
 whole,rel1=full_source(prior,base,m,hw,Binding,c,l,meta,Observer,old_div,counter)
 joined,rel2=payload(prior,base,m,hh,caller,pc,pl,pm,hjoin,old_binding,hw,Binding,c,l,meta,raw,Observer,old_div,counter)
 need(counter['calls']==0,'all positive provider counts zero');negative=controls(base,m,hw,Binding,c,l,meta,old_binding,all_divisions,counter);need(counter['calls']==1,'one deliberately inserted fallback')
 calls=Counter();literal=alias=0
 for package in(whole,joined):
  for leg in package['directions']:calls.update(leg['calls']);literal+=leg['literal_instructions'];alias+=leg['simple_alias_calls']
 print(json.dumps({'status':'PASS','graph':d.digest(c),'locations':len(c),'old_provider_calls':0,'deliberate_fallback_calls':counter['calls'],'calls':dict(calls),'literal_instructions':literal,'aliased_simple_calls':alias,'full_source':whole,'payload':joined,'division_owner_relations':rel1+rel2,'controls':negative},indent=2,sort_keys=True))
if __name__=='__main__':main()
