"""Bounded actual-source primitive boundaries with a separately written CPU.

No old numerical provider is used by the executed source. CRT/Word decoding
and early-stop observations are checker-only. Apache-2.0; @CubeJerry/OpenAI.
"""
import argparse,ast,gc,inspect,json,sys,types
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path

def need(ok,label):
    if not ok:raise ValueError(label)

def load(path,name,raw=None):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes() if raw is None else raw,str(path),'exec'),m.__dict__);return m

@contextmanager
def blocked(m):
    names=('compare','add','subtract','divmod','shift_add_bit')
    old={n:getattr(m.w.Unsigned,n) for n in names}
    def forbidden(*args,**kwargs):raise ValueError('INDEPENDENT_OLD_ARITHMETIC_UNAVAILABLE')
    for n in names:setattr(m.w.Unsigned,n,forbidden)
    try:yield
    finally:
        for n in names:setattr(m.w.Unsigned,n,old[n])

def audit_class(prior):
    class Audit(prior.Audit):
        def __init__(self,*args):
            super().__init__(*args);self.simple=[];self.pending_simple=None;self.sites_simple={}
            for direction,module in [('forward',self.m.numeric),('inverse',self.m.subtractive)]:
                for node in ast.parse(Path(module.__file__).read_bytes()).body:
                    funcs=node.body if isinstance(node,ast.ClassDef) and node.name=='Arithmetic' else [node]
                    for f in funcs:
                        if not isinstance(f,ast.FunctionDef):continue
                        owner=module.Arithmetic if isinstance(node,ast.ClassDef) else module
                        if not hasattr(owner,f.name):continue
                        sites={}
                        for c in ast.walk(f):
                            if isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Attribute) and c.func.value.attr=='raw':
                                kinds={'compare':'COMPARE','add':'ADD','subtract_exact':'SUBTRACT'}
                                if c.func.attr in kinds:sites[c.lineno]=kinds[c.func.attr]
                        if sites:self.sites_simple[getattr(owner,f.name).__code__]=(direction,f.name,sites)
        def __call__(self,stage,binder,arena,a,b,out):
            if stage=='arithmetic_before':
                kind=binder.simple_kind;found=None;frame=inspect.currentframe().f_back
                while frame is not None:
                    if frame.f_code in self.sites_simple:
                        direction,name,sites=self.sites_simple[frame.f_code]
                        if frame.f_lineno in sites:
                            found=(direction,name,frame.f_lineno,sites[frame.f_lineno]);break
                    frame=frame.f_back
                need(found is not None and found[0]==('inverse' if self.reverse else 'forward') and found[3]==kind,'actual source-call type and line')
                x,p=self.core.word_value(a);y,q=self.core.word_value(b);need(p==q>=4,'typed same-width inputs')
                need(all(arena.words[k].port is binder.iterator.guards[k] for k in range(8)),'actual8 borrowed backing identities')
                need(all(arena.words[k].port is binder.iterator.bank.ports[k-5] for k in range(8,64)),'actual56 owned backing identities')
                self.pending_simple=dict(kind=kind,x=x,y=y,p=p,alias=a is b,site=list(found[:3]),
                    cells=[(bytes(w.cells),w.head,id(w.cells),id(w.port)) for w in arena.words],
                    live=set(arena.live),available=list(arena.available),
                    template=(bytes(arena.template.cells),arena.template.head,id(arena.template.cells)),
                    numeric=binder.program.numeric_actions,meter=prior.actions(arena.meter),
                    port_meter=sum(prior.actions(w.port.meter) for w in arena.words))
                return
            if stage=='arithmetic_after':
                row=self.pending_simple;kind,x,y,p=(row[k] for k in ('kind','x','y','p'));q=None
                if kind=='COMPARE':
                    need(out==(x>y)-(x<y),'independent delivered comparison flag')
                    need(arena.live==row['live'] and arena.available==row['available'],'comparison makes no reservation')
                else:
                    q,flag=out;z=x+y if kind=='ADD' else x-y
                    need(flag==(int(z>=1<<p) if kind=='ADD' else int(z<0)) and self.core.word_value(q)==(z%(1<<p),p),'independent delivered modular output and flag')
                    need(q.slot==row['available'][-1] and arena.available==row['available'][:-1] and arena.live==row['live']|{q.slot},'independent exact one-output owner relation')
                    need(q.slot>=8 and q is arena.words[q.slot],'fresh output is an owned physical Word')
                for k,w in enumerate(arena.words):
                    old=row['cells'][k]
                    need((w.head,id(w.cells),id(w.port))==old[1:],'every numerical head/backing identity')
                    if q is None or k!=q.slot:need(bytes(w.cells)==old[0],'all other live/free bodies preserved')
                    else:need(w.cells[0]==2 and bytes(w.cells[p+2:])==old[0][p+2:],'fresh output guard and old tail')
                    if k in arena.available:need(all(bit==4 for bit in w.cells[1:]),'entire unused history blank')
                need((bytes(arena.template.cells),arena.template.head,id(arena.template.cells))==row['template'],'allocation template preserved')
                need(prior.actions(arena.meter)-row['meter']==binder.program.numeric_actions-row['numeric'] and sum(prior.actions(w.port.meter) for w in arena.words)==row['port_meter'],'new numerical actions exactly once')
                need(all(t.head==0 and all(v=='_' for v in t.cells) for t in binder.selectors),'all four real selector owners restored')
                self.simple.append(dict(kind=kind,p=p,x=x,y=y,alias=row['alias'],site=row['site'],flag=out if q is None else out[1],instructions=binder.program.receipts[-1]['instructions']+124,output_slot=None if q is None else q.slot))
                self.pending_simple=None
                return
            super().__call__(stage,binder,arena,a,b,out)
    return Audit

def resources(package):
    here=Path(__file__).resolve().parent
    raw=(here/'review_all_source.py').read_bytes()
    need(sha256(raw).hexdigest()=='1cb940c02a5cf728842b634eaac7fe0114fbf1c4973e1e4bb1cc78eef7919204','frozen independent B11 review')
    prior=load(here/'review_all_source.py','independent_B12_source_dependency')
    r=prior.resources(package/'inputs/all-divisions');r.code=r.labels=r.meta=None;gc.collect()
    d=load(package/'inputs/all-divisions/inputs/divider/divider.py','independent_B12_retained_graph')
    arith=load(package/'arithmetic.py','independent_B12_new_graph');r.code,r.labels,r.meta=arith.compile_arithmetic(d)
    need(d.digest(r.code)=='8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045','checked combined graph')
    allb=load(package/'inputs/all-divisions/all_binding.py','independent_B12_retained_all_binding')
    newb=load(package/'binding.py','independent_B12_new_binding')
    r.All=newb.make_binding(r.basebind,allb);r.allb=allb;r.Audit=audit_class(prior);r.prior=prior
    return r

def instance(r,reverse,cls=None):
    cpu=r.core.CPU(r.code,r.labels,r.meta);audit=r.Audit(r.m,r.core,reverse)
    hw=types.SimpleNamespace(NumericPort=r.core.NumericPort,GrantedSelector=r.core.GrantedSelector,setters=r.core.setters)
    return cpu,audit,(r.All if cls is None else cls)(cpu,hw,audit)

def make_endpoint(r,source,reverse=False):
    m=r.m
    return m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,m.subtractive if reverse else m.numeric,m.owner,m.bridge,source)

def positive(r):
    m,base=r.m,r.base;m.fixture=dict(m.fixture,widths=[3,3],moduli=[5,7],initial=[1,2]);base.TAGS=tuple(range(1,9))
    source,_,_=base.initial_fixture(m);initial=bytes(source.cells),source.head;legs=[]
    for reverse in (False,True):
        endpoint=make_endpoint(r,source,reverse);it=endpoint.iterator
        physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
        private=tuple(m.join.Tape() for _ in range(4));cpu,audit,binder=instance(r,reverse);binder.attach(it,private)
        with blocked(m),binder.install(m),base.seal_numerical_roles(m):endpoint.run()
        need(it.closed and not it.live and not it.bank.busy,'complete small source direction closes')
        need(all(t.head==1 and all(v==m.w.BLANK for v in t.cells) for t in physical),'all native owner histories retired')
        need(all(t.head==0 and all(v=='_' for v in t.cells) for t in private),'all four descriptor histories retired')
        need(len({id(t.cells) for t in (*physical,*private)})==83,'actual distinct83-owner union')
        need({c['kind'] for c in audit.simple}=={'COMPARE','ADD','SUBTRACT'} and any(c['kind']=='ADD' and c['alias'] for c in audit.simple),'all new primitives and actual source doubling')
        need(binder.raw_calls==binder.replacements==len(audit.calls),'inherited division scope remains complete')
        need(binder.boundary_actions==0 and binder.granted_extra_cells==28,'no ordinal probe and exact new grants')
        need(cpu.total==89+sum(c['instructions'] for c in audit.calls)+sum(c['instructions'] for c in audit.simple),'acquisition and every selected literal entry accounted')
        legs.append(dict(reverse=reverse,primitive_calls=dict(Counter(c['kind'] for c in audit.simple)),alias_calls=sum(c['alias'] for c in audit.simple),
            primitive_boundaries=audit.simple,division_boundaries=len(audit.calls),literal_instructions=cpu.total,
            numeric_actions=cpu.numeric_actions,selector_actions=cpu.selector_actions,owner_count=83,
            retained_cells=sum(len(t.cells) for t in (*physical,*private)),producer_oracle=audit.producers))
    need((bytes(source.cells),source.head)==initial,'complete small forward/inverse source roundtrip')
    return legs

def controls(r,package):
    m,base=r.m,r.base;answer=[]
    source,_,_=base.initial_fixture(m);endpoint=make_endpoint(r,source)
    cpu,audit,binder=instance(r,False);binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)))
    with binder.install(m):
        for name in ('compare','add','subtract'):
            for active in (False,True):
                binder.active=active;binder.active_arena=object() if active else None
                try:getattr(m.w.Unsigned(object()),name)(None,None)
                except ValueError as error:need('active exact current producer' in str(error),'raw scope gate before touching operands')
                else:raise ValueError('outside/foreign primitive accepted')
                finally:binder.active=False;binder.active_arena=None
                answer.append(name+('-foreign-arena' if active else '-outside-producer'))
    need(cpu.total==0,'scope gates precede all literal work');endpoint.iterator.close()
    raw=(package/'binding.py').read_bytes()
    for label,old,new,expected,returned in [
        ('returning-wrong-host-flag-delivery',b"'CMP_NEG':-1",b"'CMP_NEG':1",'independent delivered comparison flag','CMP_NEG'),
        ('returning-unremoved-output-reservation',b'slot=arena.available.pop();arena.live.add(slot)',b'slot=arena.available[-1];arena.live.add(slot)',
         'independent exact one-output owner relation','ADD_C0')]:
        need(raw.count(old)==1,'unique bound mutation '+label)
        mutant=load(package/'binding.py','independent_B12_mutant_'+label.replace('-','_'),raw.replace(old,new))
        cls=mutant.make_binding(r.basebind,r.allb);source,_,_=base.initial_fixture(m);endpoint=make_endpoint(r,source)
        cpu,audit,binder=instance(r,False,cls);binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)))
        try:
            with blocked(m),binder.install(m),base.seal_numerical_roles(m):endpoint.run()
        except ValueError as error:
            need(expected in str(error) and cpu.receipts[-1]['status']==returned,'returning binder mutation detected by independent semantic boundary')
        else:raise ValueError('binder mutation escaped '+label)
        answer.append(label)
    return answer

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--write',type=Path);args=ap.parse_args();package=args.package.resolve()
    r=resources(package);legs=positive(r);negative=controls(r,package)
    result=dict(status='PASS',binding_sha256=sha256((package/'binding.py').read_bytes()).hexdigest(),
        graph='8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045',
        directions=legs,controls=negative,roundtrip=True,old_provider_used=False,
        scope='Independent small complete actual-source roundtrip, exact primitive flags, physical owners and source call sites; broad nonleaf and full meter/count audit are separate.')
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(text)
    print(text,end='')

if __name__=='__main__':main()
