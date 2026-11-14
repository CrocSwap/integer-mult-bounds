"""Independent all-current-source integration, reusing the frozen B10 CPU.

Direct CRT-sum and integer/allocation-only oracles are verifier-only.
No new author hardware or old-divider numerical oracle is imported.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
import argparse
import ast
from hashlib import sha256
import inspect
import json
from math import prod
from pathlib import Path
import sys
import types


def need(ok,label):
    if not ok:raise ValueError(label)


def load(path,name,raw=None):
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes() if raw is None else raw,str(path),'exec'),module.__dict__)
    return module


def actions(meter):return sum(meter.record()[k] for k in('reads','writes','moves'))


def stream_pairs(tape,m):
    data=bytes(tape.cells);pos=1;rows=[];widths=[]
    need(data[0]==m.w.LEFT,'paired stream left guard')
    while data[pos]!=m.w.RIGHT:
        need(data[pos]==m.r.ROOT,'paired stream root');pos+=1;row=[]
        for _ in range(2):
            end=data.index(m.r.WORD_END,pos);digits=data[pos:end]
            need(digits and all(x in(0,1) for x in digits),'paired stream binary field')
            row.append(sum(x<<k for k,x in enumerate(digits)));widths.append(len(digits));pos=end+1
        need(data[pos]==m.r.RECORD_END,'paired stream end');pos+=1;rows.append(row)
    need(rows and len(set(widths))==1,'complete same-width pair stream')
    return rows,widths[0]


def closed_crt(left,right,reverse):
    """Independent sum of CRT idempotents, not the source's Garner recurrence."""
    modulus=prod(x[0] for x in left);prefix=1;total=0
    for prime,value in left:
        residue=prefix*value%prime;complement=modulus//prime
        total+=residue*complement*pow(complement,-1,prime);prefix*=prime
    total%=modulus;valid=all(value<prime for prime,value in left)
    if not valid:total=0
    expected=[];prefix=modulus
    for prime,value in right:
        offset=total*pow(prefix,-1,prime)%prime
        expected.append([offset,(value+(-offset if reverse else offset))%prime if value<prime else value])
        prefix*=prime
    return total,modulus,valid,expected


class Audit:
    def __init__(self,m,core,reverse):
        self.m,self.core,self.reverse=m,core,reverse;self.calls=[];self.producers=[];self.meters={};self.pending=None
        self.sites={}
        for direction,module in [('forward',m.numeric),('inverse',m.subtractive)]:
            raw=Path(module.__file__).read_bytes();tree=ast.parse(raw)
            direct=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.FunctionDef) and node.name in('remainder','inverse'):
                    lines={n.lineno for n in ast.walk(node) if isinstance(n,ast.Call)
                           and isinstance(n.func,ast.Attribute) and n.func.attr=='divmod'}
                    need(len(lines)==1,'exact one raw call at each source method')
                    self.sites[getattr(module.Arithmetic,node.name).__code__]=(direction,node.name,next(iter(lines)))
                    direct.extend(lines)
            need(len(direct)==2,'two exact raw source sites')
    def __call__(self,stage,binder,arena,n,d,out):
        m,core=self.m,self.core
        if stage=='producer_before':
            left,p=stream_pairs(n,m);right,rp=stream_pairs(d,m);need(p==rp>=4,'current uniform P')
            self.producers.append(dict(left=left,right=right,p=p,start=len(self.calls)))
            self.meters[id(arena.meter)]=arena.meter
        elif stage=='before':
            found=None;frame=inspect.currentframe().f_back
            while frame is not None:
                if frame.f_code in self.sites:
                    found=self.sites[frame.f_code];need(frame.f_lineno==found[2],'actual exact source call line');break
                frame=frame.f_back
            need(found is not None and found[0]==('inverse' if self.reverse else 'forward'),'actual source method provenance')
            source_n,source_d=(frame.f_locals['value'],frame.f_locals['modulus']) if found[1]=='remainder' else(frame.f_locals['r0'],frame.f_locals['r1'])
            need(n is source_n and d is source_d,'source operand identity at interception')
            nv,p=core.word_value(n);dv,dp=core.word_value(d)
            need(p==dp and 0<dv<1<<(p-1) and n is not d,'every actual raw admission including unit divisors')
            need(all(arena.words[k].port is binder.iterator.guards[k] for k in range(8)),'actual eight borrowed guards')
            need(all(arena.words[k].port is binder.iterator.bank.ports[k-5] for k in range(8,64)),'actual56 owned backings')
            self.pending=dict(n=nv,d=dv,p=p,site=found[1],live=set(arena.live),
                before=[(bytes(w.cells),w.head,id(w.cells),id(w.port)) for w in arena.words],
                template=(bytes(arena.template.cells),arena.template.head,id(arena.template.cells)),
                old=core.old_allocation_relation(arena.available,arena.live,p,nv,dv),
                numeric=binder.program.numeric_actions,meter=actions(arena.meter),
                port_meter=sum(actions(w.port.meter) for w in arena.words))
        elif stage=='after':
            row=self.pending;q,r=out;p,nv,dv=row['p'],row['n'],row['d']
            need(core.word_value(q)==(nv//dv,p) and core.word_value(r)==(nv%dv,p),'independent source-call quotient/remainder')
            oldq,oldr,free,live=row['old'];pi={k:k for k in row['live']}
            pi.update({oldq:q.slot,oldr:r.slot});pi.update(zip(free,arena.available))
            need(len(pi)==len(set(pi.values()))==64,'complete independent local owner bijection')
            for a,b in pi.items():need((a in live)==(b in arena.live),'live/free relation')
            for k,w in enumerate(arena.words):
                previous=row['before'][k]
                need((w.head,id(w.cells),id(w.port))==previous[1:],'all actual owner/head identities')
                if k in row['live']:need(bytes(w.cells)==previous[0],'every incoming live body')
                if k in arena.available:need(all(s==4 for s in w.cells[1:]),'all free histories blank')
                need(all(s==4 for s in w.cells[p+2:]),'retained larger numerical tail')
            need((bytes(arena.template.cells),arena.template.head,id(arena.template.cells))==row['template'],'separate template preserved')
            numeric=binder.program.numeric_actions-row['numeric']
            need(actions(arena.meter)-row['meter']==numeric and sum(actions(w.port.meter) for w in arena.words)==row['port_meter'],
                 'independent exact numerical meter split')
            receipt=binder.program.receipts[-1]
            need(receipt['status']=='DONE' and receipt['logical_instructions']==18*p*p+36*p+458+(12*p+9)*(nv//dv).bit_count(),
                 'exact reused core logical invoice')
            self.calls.append(dict(n=nv,d=dv,p=p,site=row['site'],numeric_actions=numeric,
                bijection=sha256(json.dumps(sorted(pi.items())).encode()).hexdigest(),
                instructions=receipt['instructions']+124,max_history=max(len(w.cells) for w in arena.words)))
            self.pending=None
        elif stage=='producer_after':
            row=self.producers[-1];lower,product,valid,expected=closed_crt(row['left'],row['right'],self.reverse)
            observed,p=stream_pairs(out['stream'],m)
            need(core.word_value(out['lower'])==(lower,p) and core.word_value(out['product'])==(product,p)
                 and observed==expected and out['left_valid']==valid,'independent CRT-idempotent source oracle')
            calls=self.calls[row['start']:];e=sum(x['site']=='inverse' for x in calls)
            mcount,tcount=len(row['left']),len(row['right']);v=sum(x<M for M,x in row['right'])
            exact=3*mcount+2*tcount+v+2*e
            need(len(calls)==exact and exact<=(p-2)*(4*p+5),'exact source raw-call count')
            need(sum(x['instructions'] for x in calls)<=exact*(930*p*p+1395*p+14322),'complete per-invocation division bill')
            row.update(calls=exact,euclidean=e,valid_right=v,expected=expected,lower=lower,product=product)
        else:raise ValueError('unknown observation stage')


def resources(package):
    here=Path(__file__).resolve().parent;raw=(here/'review_core.py').read_bytes()
    need(sha256(raw).hexdigest()=='316aace11634045aa0381cb96a22e393f6f9bf857794cf1f6223b9dcfcdf5f2e','frozen independent B10 CPU')
    core=load(here/'review_core.py','independent_B10_CPU')
    prior=load(package/'inputs/divider/inputs/headers/verify.py','independent_B11_predecessor')
    _,previous,base,m,headers,hh,caller,hcode,hlabels,hmeta,_=prior.modules()
    basebind=load(package/'inputs/divider/binding.py','independent_B10_binding')
    hjoin=load(package/'inputs/divider/inputs/headers/join.py','independent_B9_seams')
    allbind=load(package/'all_binding.py','independent_all_binding_under_review')
    need(sha256((package/'all_binding.py').read_bytes()).hexdigest()=='1b62577836ffc5906bd749b3705cfb3873cf9b15380224648fff924315efc8c9','frozen all-call binding')
    d=load(package/'inputs/divider/divider.py','independent_B11_graph');code,labels,meta=d.compile_divider()
    need(d.digest(code)=='d36e8220def8efb2baed793d0bea6f0a19b0903b5b005b730652b5bb7d121194','unchanged reviewed core graph')
    caller_raw=(package/'inputs/divider/inputs/headers/inputs/keypass/inputs/route/inputs/point/caller.py').read_bytes()
    return types.SimpleNamespace(core=core,base=base,m=m,hh=hh,caller=caller,hcode=hcode,hlabels=hlabels,hmeta=hmeta,
        basebind=basebind,hjoin=hjoin,All=allbind.make_binding(basebind),code=code,labels=labels,meta=meta,caller_raw=caller_raw)


def instance(r,reverse):
    cpu=r.core.CPU(r.code,r.labels,r.meta);audit=Audit(r.m,r.core,reverse)
    hardware=types.SimpleNamespace(NumericPort=r.core.NumericPort,GrantedSelector=r.core.GrantedSelector,setters=r.core.setters)
    binder=r.All(cpu,hardware,audit)
    return cpu,audit,binder


def unavailable(*args,**kwargs):raise ValueError('INDEPENDENT_OLD_PROVIDER_FORBIDDEN')


def baseline_divider(original,record):
    def call(obj,n,d):
        before=actions(obj.arena.meter);out=original(obj,n,d)
        record['division_actions']+=actions(obj.arena.meter)-before;record['calls']+=1
        record['meters'][id(obj.arena.meter)]=obj.arena.meter;return out
    return call


def common_bill(cpu,audit,binder):
    j=len(audit.calls)
    need(binder.raw_calls==binder.replacements==j,'all raw calls use the literal core')
    need(binder.boundary_actions==0 and binder.granted_extra_cells==28,'no ordinal/half query and actual grants')
    need(binder.finite_control_invoice==256+32*binder.invocations+16400*j,'complete new metadata invoice')
    need(cpu.total==89+sum(c['instructions'] for c in audit.calls),'one acquisition and every call/setter paid once')
    return dict(raw_calls=j,unit_divisors=sum(c['d']==1 for c in audit.calls),instructions=cpu.total,
                numeric=cpu.numeric_actions,selectors=cpu.selector_actions,metadata=binder.finite_control_invoice,
                grant_cells=28,producers=audit.producers,calls=audit.calls)


def full_endpoint(r):
    m,base=r.m,r.base;old=m.w.Unsigned.divmod
    m.fixture=dict(m.fixture,widths=[3,3,4,4],moduli=[5,7,13,8],initial=[1,2,12,7])
    base.TAGS=tuple(range(1,17));reference,_,_=base.initial_fixture(m);baseline=[];forward=None
    for reverse in(False,True):
        before=actions(reference.meter)
        endpoint=m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,
            m.subtractive if reverse else m.numeric,m.owner,m.bridge,reference)
        it=endpoint.iterator;physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
        record=dict(division_actions=0,calls=0,meters={});m.w.Unsigned.divmod=baseline_divider(old,record)
        try:
            with base.seal_numerical_roles(m):endpoint.run()
        finally:m.w.Unsigned.divmod=old
        bill=sum(actions(t.meter) for t in(reference,*physical))-before+sum(actions(t) for t in record['meters'].values())
        baseline.append(dict(native=bill,old_divisions=record['division_actions'],calls=record['calls']))
        if not reverse:forward=bytes(reference.cells)
    source,_,_=base.initial_fixture(m);original=bytes(source.cells),source.head;legs=[]
    for reverse in(False,True):
        before=actions(source.meter)
        endpoint=m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,
            m.subtractive if reverse else m.numeric,m.owner,m.bridge,source)
        it=endpoint.iterator;private=tuple(m.join.Tape() for _ in range(4))
        physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
        cpu,audit,binder=instance(r,reverse);binder.attach(it,private);m.w.Unsigned.divmod=unavailable
        try:
            with binder.install(m),base.seal_numerical_roles(m):endpoint.run()
        finally:m.w.Unsigned.divmod=old
        need(it.closed and not it.live and not it.bank.busy,'full actual source traversal closes')
        need(all(t.head==1 and all(x==m.w.BLANK for x in t.cells) for t in physical),'every native owner fully retired')
        need(all(t.head==0 and all(x=='_' for x in t.cells) for t in private),'same four descriptor owners returned')
        need(len({id(t.cells) for t in(*physical,*private)})==83,'full83 physical owner union')
        native=sum(actions(t.meter) for t in(source,*physical))-before+sum(actions(t) for t in audit.meters.values())
        expected=baseline[int(reverse)]
        need(native-cpu.numeric_actions==expected['native']-expected['old_divisions'],'exact independent same-workload native remainder')
        need(sum(t.actions for t in private)==cpu.selector_actions,'entire descriptor action overlap')
        bill=common_bill(cpu,audit,binder);need(bill['raw_calls']==expected['calls'],'same count as old source')
        need(any(len(p['left'])>1 for p in audit.producers),'actual nonleaf in each complete source direction')
        bill.update(reverse=reverse,remaining_source=native-cpu.numeric_actions,owner_count=83,
                    retained_cells=sum(len(t.cells) for t in(*physical,*private)))
        legs.append(bill)
        if not reverse:need(bytes(source.cells)==forward,'complete forward commit matches retained source')
    need((bytes(source.cells),source.head)==original,'complete source forward/inverse restoration')
    return dict(legs=legs,baseline=baseline,roundtrip=True)


def payload_join(r):
    m,base=r.m,r.base;old=m.w.Unsigned.divmod;old_leg=r.caller.run_leg
    m.fixture=dict(m.fixture,widths=[3,3,2,2],moduli=[5,7,2,3],initial=[1,2,2,3]);base.TAGS=(1,2,3,4)
    source,payload,_=base.initial_fixture(m);point=r.hh.Program(r.hcode,r.hlabels,r.hmeta);baseline=[];forward=None
    for reverse in(False,True):
        record=dict(division_actions=0,calls=0,meters={});m.w.Unsigned.divmod=baseline_divider(old,record);before=point.native_actions
        try:receipt,_=old_leg(m,base,point,source,payload,reverse)
        finally:m.w.Unsigned.divmod=old
        baseline.append(dict(native=receipt['encoded_source_symbol_actions']-(point.native_actions-before),
                             old_divisions=record['division_actions'],markers=receipt['outer_adapter_symbol_actions'],calls=record['calls']))
        if not reverse:forward=(bytes(source.cells),dict(payload.cells))
    source,payload,_=base.initial_fixture(m);initial=(bytes(source.cells),source.head,dict(payload.cells),payload.head)
    point=r.hh.Program(r.hcode,r.hlabels,r.hmeta);legs=[];owners=[]
    for reverse in(False,True):
        cpu,audit,binder=instance(r,reverse);changed,_=r.basebind.join(r.hjoin,r.caller,binder,r.caller_raw)
        before=point.native_actions;m.w.Unsigned.divmod=unavailable
        try:receipt,stock=changed.run_leg(m,base,point,source,payload,reverse)
        finally:m.w.Unsigned.divmod=old
        old_bill=baseline[int(reverse)]
        remaining=receipt['encoded_source_symbol_actions']-(point.native_actions-before)-cpu.numeric_actions
        markers=receipt['outer_adapter_symbol_actions']-cpu.selector_actions
        need(remaining==old_bill['native']-old_bill['old_divisions'] and markers==old_bill['markers'],
             'independent source/payload disjoint mixed-meter vector')
        bill=common_bill(cpu,audit,binder);need(bill['raw_calls']==old_bill['calls'],'payload all raw calls')
        bill.update(reverse=reverse,remaining_source=remaining,remaining_markers=markers);legs.append(bill);owners.extend(stock[0])
        if not reverse:need((bytes(source.cells),dict(payload.cells))==forward,'exact entire forward source/payload')
    need((bytes(source.cells),source.head,dict(payload.cells),payload.head)==initial,'full source/payload/key roundtrip')
    need(len(owners)==len({id(x) for x in owners})==200,'all200 actual caller owner histories')
    return dict(legs=legs,baseline=baseline,roundtrip=True)


def controls(r,package):
    m,base=r.m,r.base;old=m.w.Unsigned.divmod;answer=[]
    source,_,_=base.initial_fixture(m)
    endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
    cpu,audit,binder=instance(r,False);binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)))
    with binder.install(m):
        for active in(False,True):
            binder.active=active;binder.active_arena=object() if active else None
            try:m.w.Unsigned(object()).divmod(None,None)
            except ValueError as error:need('active exact current producer' in str(error),'source scope rejection')
            else:raise ValueError('outside/foreign source accepted')
            finally:binder.active=False;binder.active_arena=None
            answer.append('foreign-arena' if active else 'outside-producer')
    need(cpu.total==0,'scope gate before physical instructions');endpoint.iterator.close()
    # Return from the unchanged graph after deliberately swapping the descriptors.
    source,_,_=base.initial_fixture(m)
    endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
    cpu,audit,binder=instance(r,False)
    def swapped(program,ports,slots):return r.core.setters(program,ports,(slots[1],slots[0],slots[2],slots[3]))
    binder.hardware=types.SimpleNamespace(NumericPort=r.core.NumericPort,GrantedSelector=r.core.GrantedSelector,setters=swapped)
    binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)));m.w.Unsigned.divmod=unavailable
    try:
        try:
            with binder.install(m),base.seal_numerical_roles(m):endpoint.run()
        except ValueError as error:
            need('source-call quotient/remainder' in str(error) and cpu.receipts[-1]['status']=='DONE',
                 'returning source descriptor swap detected by independent value oracle')
        else:raise ValueError('returning swapped binding escaped')
    finally:m.w.Unsigned.divmod=old
    answer.append('returning-swapped-source-binding')
    # The old routine is unavailable, including if a future edit restores a fallback.
    raw=(package/'all_binding.py').read_bytes();needle=b'return owner.divide(obj,n,d)'
    need(raw.count(needle)==1,'single unconditional source dispatch')
    mutant=load(package/'all_binding.py','independent_fallback_mutant',raw.replace(needle,b'return old_raw(obj,n,d)'))
    previous=r.All;r.All=mutant.make_binding(r.basebind)
    source,_,_=base.initial_fixture(m);endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
    cpu,audit,binder=instance(r,False);binder.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)))
    m.w.Unsigned.divmod=unavailable
    try:
        try:
            with binder.install(m),base.seal_numerical_roles(m):endpoint.run()
        except ValueError as error:need('INDEPENDENT_OLD_PROVIDER_FORBIDDEN' in str(error),'old provider sentinel')
        else:raise ValueError('fallback escaped sentinel')
    finally:m.w.Unsigned.divmod=old;r.All=previous
    answer.append('old-provider-fallback')
    return answer


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--write',type=Path);args=parser.parse_args();package=args.package.resolve()
    need(sha256((package/'PROOF.md').read_bytes()).hexdigest()=='cc65e3f5d559501fa854e263a46b647be18ef0bdbd6eab0e0e57d803f0714b11','final reviewed source/ABI proof')
    r=resources(package);whole=full_endpoint(r);payload=payload_join(r);negative=controls(r,package)
    legs=whole['legs']+payload['legs'];calls=[c for leg in legs for c in leg['calls']]
    need(any(c['d']==1 for c in calls) and all(c['d']>0 for c in calls),'new unit-divisor coverage')
    # These incorrect cost formulas disagree on the executed workload.
    for group in (whole,payload):
        for leg,old in zip(group['legs'],group['baseline']):
            expected=old['native']-old['old_divisions']
            need(leg['remaining_source']+leg['numeric']!=expected,'omitted numerical subtraction is detected')
            marker_expected=old.get('markers',0)
            need(leg.get('remaining_markers',0)+leg['selectors']!=marker_expected,'omitted selector subtraction is detected')
    negative.extend(['omitted-numerical-overlap-subtraction','omitted-selector-overlap-subtraction'])
    # Positive-coefficient expansion proves the coarse universal quartic invoice.
    # 2^15(P+2)^4 - [89+(P-2)(4P+5)(930P^2+1395P+14322)]
    # Stored low-to-high, calculated below by integer convolution.
    upper=[89,0,0,0,0];a=[-10,-3,4];b=[14322,1395,930]
    for i,x in enumerate(a):
        for j,y in enumerate(b):upper[i+j]+=x*y
    target=[32768*16,32768*32,32768*24,32768*8,32768]
    difference=[x-y for x,y in zip(target,upper)]
    need(all(x>0 for x in difference),'uniform positive-coefficient quartic margin')
    result=dict(status='PASS',binding_sha256=sha256((package/'all_binding.py').read_bytes()).hexdigest(),
                proof_sha256=sha256((package/'PROOF.md').read_bytes()).hexdigest(),
                core_graph='d36e8220def8efb2baed793d0bea6f0a19b0903b5b005b730652b5bb7d121194',
                review_core_sha256='316aace11634045aa0381cb96a22e393f6f9bf857794cf1f6223b9dcfcdf5f2e',
                full_source=whole,payload=payload,controls=negative,raw_calls=len(calls),unit_divisors=sum(c['d']==1 for c in calls),
                literal_instructions=sum(leg['instructions'] for leg in legs),
                quartic_difference_coefficients_low_to_high=difference,
                original_provider_used_by_actual_execution=False,
                independence='Frozen separately written CPU, CRT-idempotent sum, integer quotient/remainder and allocation-only boundary model; old source only supplies a separate regression/cost baseline.')
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
