"""All-current-division source joins; original provider is blocked at runtime.

All decoding, old-provider counterfactuals and snapshots are checker-only.
Counterfactual arithmetic runs after the actual source leg has finished.
Default read-only; Python standard library. Apache2.0, @CubeJerry/OpenAI.
"""
from pathlib import Path
from hashlib import sha256
import ast,inspect,json,sys,types
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def load(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def value(cells,w):
    end=cells.index(w.RIGHT,1)
    need(all(b in(0,1) for b in cells[1:end]),'observed binary Word')
    return sum(b<<k for k,b in enumerate(cells[1:end]))
def pairs(tape,m):
    a=tape.cells;i=1;out=[];width=None
    while a[i]!=m.w.RIGHT:
        need(a[i]==m.r.ROOT,'observed pair tag');i+=1;row=[]
        for _ in range(2):
            digits=[]
            while a[i]!=m.r.WORD_END:need(a[i] in(0,1),'observed pair digit');digits.append(a[i]);i+=1
            width=len(digits) if width is None else width;need(width==len(digits),'observed P extent')
            row.append(sum(bit<<j for j,bit in enumerate(digits)));i+=1
        need(a[i]==m.r.RECORD_END,'observed pair end');i+=1;out.append(row)
    return out,width
def snapshot(a):
    return {'cells':[bytes(w.cells) for w in a.words],'heads':[w.head for w in a.words],
            'identities':[(id(w.cells),id(w.port)) for w in a.words],
            'template':bytes(a.template.cells),'template_head':a.template.head,
            'available':list(a.available),'live':set(a.live),
            'arena_actions':sum(a.meter.record()[k] for k in('reads','writes','moves')),
            'port_actions':sum(sum(w.port.meter.record()[k] for k in('reads','writes','moves')) for w in a.words)}

class Observations:
    def __init__(self,m,reverse):self.m,self.reverse=m,reverse;self.calls=[];self.producers=[];self.pending=None;self.arena_meters=[]
    def __call__(self,stage,b,a,n,d,out):
        m=self.m
        if stage=='producer_before':
            self.arena_meters.append(a.meter)
            left,p=pairs(n,m);right,rp=pairs(d,m);need(p==rp and p>=4,'actual same-width current entry')
            self.producers.append({'left':left,'right':right,'p':p,'start':len(self.calls),'invocation':b.invocations})
        elif stage=='before':
            state=snapshot(a);origin=None
            for frame in inspect.stack():
                if frame.function in('remainder','inverse') and frame.filename.endswith('producer.py'):
                    origin=frame.function;break
            need(origin is not None,'exact two-site raw-call provenance')
            self.pending={'before':state,'Nslot':n.slot,'Dslot':d.slot,'origin':origin,'program_numeric':b.program.numeric_actions,
                          'producer':len(self.producers)-1}
        elif stage=='after':
            row=self.pending;q,r=out;after=snapshot(a);p=after['cells'][q.slot].index(m.w.RIGHT,1)-1
            numerator,denominator=value(row['before']['cells'][n.slot],m.w),value(row['before']['cells'][d.slot],m.w)
            need(0<denominator<1<<(p-1),'every actual divisor has strict positive high-bit margin')
            need(value(q.cells,m.w)==numerator//denominator and value(r.cells,m.w)==numerator%denominator,'direct integer division oracle')
            need(len(after['live'])==len(row['before']['live'])+2 and {q.slot,r.slot}.isdisjoint(row['before']['live']),
                 'two distinct fresh outputs')
            for slot in row['before']['live']:
                need((after['cells'][slot],after['heads'][slot],after['identities'][slot])==
                     (row['before']['cells'][slot],row['before']['heads'][slot],row['before']['identities'][slot]),'all incoming data/head/backing preserved')
            delta=b.program.numeric_actions-row['program_numeric']
            need(after['arena_actions']-row['before']['arena_actions']==delta and
                 after['port_actions']==row['before']['port_actions'],'exact disjoint actual meter ownership')
            row.update(after=after,Qslot=q.slot,Rslot=r.slot,p=p,numerator=numerator,denominator=denominator,
                       numeric_actions=delta);self.calls.append(row);self.pending=None
        elif stage=='producer_after':
            row=self.producers[-1];left,right,p=row['left'],row['right'],row['p']
            lower=0;prefix=1
            for modulus,current in left:
                lower+=prefix*((current%modulus-lower*pow(prefix,-1,modulus))%modulus)
                prefix*=modulus
            if any(current>=modulus for modulus,current in left):lower=0
            product=prefix;expected=[]
            for modulus,current in right:
                offset=lower*pow(prefix,-1,modulus)%modulus
                updated=(current+(-1 if self.reverse else 1)*offset)%modulus if current<modulus else current
                expected.append([offset,updated]);prefix*=modulus
            observed,op=pairs(out['stream'],m)
            need(op==p and observed==expected and value(out['lower'].cells,m.w)==lower and
                 value(out['product'].cells,m.w)==product,'direct exact CRT/current-coordinate oracle')
            calls=self.calls[row['start']:];e=sum(c['origin']=='inverse' for c in calls)
            v=sum(current<modulus for modulus,current in right)
            exact=3*len(left)+2*len(right)+v+2*e
            need(len(calls)==exact and len(calls)<=(p-2)*(4*p+5),'exact complete raw-call count and universal bound')
            row.update(calls=len(calls),euclidean_divisions=e,valid_right=v,output=observed,
                       literal_divisions=sum(b.calls[row['start']+i]['instructions']+124 for i in range(len(calls))))
        else:raise ValueError('unknown observation boundary')

def counterfactuals(m,old_div,observed):
    """Executed after the physical leg; old arithmetic cannot supply its work."""
    records=[]
    for row in observed.calls:
        before,after=row['before'],row['after'];a=object.__new__(m.w.Arena)
        a.capacity,a.bits,a.meter=64,row['p'],m.w.Meter();a.words=[]
        a.available,a.live=list(before['available']),set(before['live'])
        for slot,cells in enumerate(before['cells']+[before['template']]):
            word=object.__new__(m.w.Word);word.arena=a;word.slot=slot if slot<64 else -1
            word.cells=bytearray(cells);word.head=before['heads'][slot] if slot<64 else before['template_head']
            if slot<64:a.words.append(word)
            else:a.template=word
        oq,orr=old_div(m.w.Unsigned(a),a.words[row['Nslot']],a.words[row['Dslot']])
        pi={slot:slot for slot in before['live']};pi.update({oq.slot:row['Qslot'],orr.slot:row['Rslot']});pi.update(zip(a.available,after['available']))
        need(len(pi)==len(set(pi.values()))==64,'complete local weak owner bijection')
        for old,new in pi.items():
            need((old in a.live)==(new in after['live']),'related live/free membership')
            need(a.words[old].head==after['heads'][new],'related returned heads')
            if old in a.live:
                if old in before['live']:need(bytes(a.words[old].cells)==after['cells'][new],'unchanged complete incoming histories')
                else:need(bytes(a.words[old].cells[:row['p']+2])==after['cells'][new][:row['p']+2],'related complete output values')
            else:need(all(x==m.w.BLANK for x in after['cells'][new][1:]),'every retained free history blank')
        records.append({'p':row['p'],'N':row['numerator'],'D':row['denominator'],'site':row['origin'],
                        'slots':[row['Nslot'],row['Dslot'],row['Qslot'],row['Rslot']],
                        'entry_fingerprint':[row['Nslot'],row['Dslot'],*before['available'][-5:]],
                        'bijection_sha256':sha256(json.dumps(sorted(pi.items())).encode()).hexdigest()})
    return records

def modules():
    prior=load(HERE/'inputs/divider/inputs/headers/verify.py','B11_headers')
    _,previous,base,m,headers,header_hw,caller,code,labels,meta,_=prior.modules()
    previous_join=load(HERE/'inputs/divider/inputs/headers/join.py','B11_header_join')
    d=load(HERE/'inputs/divider/divider.py','B11_divider');hw=load(HERE/'inputs/divider/hardware.py','B11_hardware')
    binding=load(HERE/'inputs/divider/binding.py','B11_old_binding')
    new=load(HERE/'all_binding.py','B11_all_binding');AllBinding=new.make_binding(binding)
    dc,dl,dm=d.compile_divider()
    need(d.digest(dc)=='d36e8220def8efb2baed793d0bea6f0a19b0903b5b005b730652b5bb7d121194','unchanged exact literal child')
    raw=(HERE/'inputs/divider/inputs/headers/inputs/keypass/inputs/route/inputs/point/caller.py').read_bytes()
    return previous,base,m,header_hw,caller,code,labels,meta,previous_join,d,hw,binding,AllBinding,dc,dl,dm,raw

def baseline_spy(base,m,old_div):
    observed={'calls':0,'actions':0,'meters':{}}
    def spy(obj,n,d):
        meter=obj.arena.meter;before=base.meter_actions(meter)
        out=old_div(obj,n,d)
        observed['calls']+=1;observed['actions']+=base.meter_actions(meter)-before
        observed['meters'][id(meter)]=meter
        return out
    return spy,observed

def full_source(base,m,hw,AllBinding,dc,dl,dm,old_div,unavailable):
    m.fixture=dict(m.fixture,widths=[3,3,4,4],moduli=[5,7,13,8],initial=[1,2,12,7]);base.TAGS=tuple(range(1,17))
    reference,_,_=base.initial_fixture(m);baseline=None;baseline_bills=[]
    for reverse in(False,True):
        before_source=base.meter_actions(reference.meter)
        endpoint=m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,
                                   m.subtractive if reverse else m.numeric,m.owner,m.bridge,reference)
        it=endpoint.iterator;physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
        spy,count=baseline_spy(base,m,old_div);m.w.Unsigned.divmod=spy
        try:
            with base.seal_numerical_roles(m):endpoint.run()
        finally:m.w.Unsigned.divmod=old_div
        native=sum(base.meter_actions(t.meter) for t in(reference,*physical))-before_source+sum(base.meter_actions(t) for t in count['meters'].values())
        baseline_bills.append({'source_actions':native,'raw_division_actions':count['actions'],'raw_division_calls':count['calls']})
        if not reverse:baseline=bytes(reference.cells)
    source,_,_=base.initial_fixture(m);original=bytes(source.cells),source.head;legs=[];relations=[]
    for reverse in(False,True):
        source_before=base.meter_actions(source.meter)
        endpoint=m.writer.Endpoint(m.reverse if reverse else m.f,m.w,m.r,m.e,
                                   m.subtractive if reverse else m.numeric,m.owner,m.bridge,source)
        it=endpoint.iterator;private=tuple(m.join.Tape() for _ in range(4))
        program=hw.Program(dc,dl,dm);observed=Observations(m,reverse);binder=AllBinding(program,hw,observed);binder.attach(it,private)
        physical=(*it.bank.ports,*it.guards,*it.counters.values(),endpoint.staging)
        m.w.Unsigned.divmod=unavailable
        try:
            with binder.install(m),base.seal_numerical_roles(m):endpoint.run()
        finally:m.w.Unsigned.divmod=old_div
        need(it.closed and not it.live and not it.bank.busy,'complete actual source traversal closes')
        need(all(t.head==1 and all(s==m.w.BLANK for s in t.cells) for t in physical),'all full-source histories retired')
        need(all(t.head==0 and all(s=='_' for s in t.cells) for t in private),'descriptor histories retired')
        need(len({id(t.cells) for t in(*physical,*private)})==len(physical)+4,'disjoint retained owner union')
        need(binder.raw_calls==binder.replacements==len(observed.calls),'all full-source raw providers replaced')
        need(any(len(p['left'])>1 for p in observed.producers),'nonleaf in each source direction')
        native=sum(base.meter_actions(t.meter) for t in(source,*physical))-source_before+sum(base.meter_actions(t) for t in observed.arena_meters)
        old=baseline_bills[int(reverse)]
        need(native-program.numeric_actions==old['source_actions']-old['raw_division_actions'] and
             binder.raw_calls==old['raw_division_calls'],'exact full-source removal of all old numerical division actions')
        need(sum(t.actions for t in private)==program.selector_actions,'complete source-only descriptor action equality')
        records=counterfactuals(m,old_div,observed);relations.extend(records)
        legs.append({'reverse':reverse,'raw_divisions':binder.raw_calls,'producer_invocations':binder.invocations,
                     'literal_division_instructions':program.total,'remaining_source_symbol_actions':native-program.numeric_actions,
                     'numeric_actions_included_in_literal':program.numeric_actions,'selector_actions_included_in_literal':program.selector_actions,
                     'finite_metadata_invoice':binder.finite_control_invoice,'grant_extra_cells':28,
                     'physical_roles':len(physical)+4,'retained_symbol_cells':sum(len(t.cells) for t in(*physical,*private)),
                     'producers':observed.producers})
        if not reverse:need(bytes(source.cells)==baseline,'full forward source equals unchanged source')
    need((bytes(source.cells),source.head)==original,'full-source forward/inverse nonleaf roundtrip')
    return {'directions':legs,'baseline_directions':baseline_bills,'complete_source_roundtrip':True},relations

def controls(base,m,hw,binding,AllBinding,dc,dl,dm,old_div,unavailable):
    source,_,_=base.initial_fixture(m)
    endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
    private=tuple(m.join.Tape() for _ in range(4));program=hw.Program(dc,dl,dm);binder=AllBinding(program,hw);binder.attach(endpoint.iterator,private)
    answer=[]
    with binder.install(m):
        for active in(False,True):
            binder.active=active;binder.active_arena=object() if active else None
            try:m.w.Unsigned(object()).divmod(None,None)
            except ValueError as error:
                need('active exact current producer' in str(error),'precise out-of-scope rejection')
                answer.append('foreign_arena' if active else 'outside_producer')
            else:raise ValueError('out-of-scope interception escaped')
            finally:binder.active=False;binder.active_arena=None
    need(program.total==0,'scope guards precede physical arithmetic');endpoint.iterator.close()
    raw=(HERE/'all_binding.py').read_text();needle='return owner.divide(obj,n,d)'
    need(raw.count(needle)==1,'one exact all-call dispatch');mutant=types.ModuleType('B11_fallback_mutant')
    exec(compile(raw.replace(needle,'return old_raw(obj,n,d)'),'<deliberate fallback mutation>','exec'),mutant.__dict__)
    Bad=mutant.make_binding(binding);source,_,_=base.initial_fixture(m)
    endpoint=m.writer.Endpoint(m.f,m.w,m.r,m.e,m.numeric,m.owner,m.bridge,source)
    b=Bad(hw.Program(dc,dl,dm),hw);b.attach(endpoint.iterator,tuple(m.join.Tape() for _ in range(4)))
    m.w.Unsigned.divmod=unavailable
    try:
        try:
            with b.install(m),base.seal_numerical_roles(m):endpoint.run()
        except ValueError as error:need('OLD_DIVISION_PROVIDER_UNAVAILABLE' in str(error),'fallback sentinel catches actual source call')
        else:raise ValueError('fallback mutation escaped')
    finally:m.w.Unsigned.divmod=old_div
    answer.append('old_provider_fallback');return answer

def main():
    previous,base,m,hh,caller,code,labels,meta,hjoin,d,hw,binding,AllBinding,dc,dl,dm,raw=modules()
    old_leg=caller.run_leg;old_div=m.w.Unsigned.divmod;cases=[];all_relations=[];fallback_calls=0
    def unavailable(*args,**kwargs):
        nonlocal fallback_calls
        fallback_calls+=1;raise ValueError('OLD_DIVISION_PROVIDER_UNAVAILABLE')
    for moduli,values in(((5,7,2,3),(1,2,2,3)),((5,7,13,8),(1,2,12,7)),((11,13,8,7),(1,2,5,7))):
        widths=[max(a.bit_length(),v.bit_length()) for a,v in zip(moduli,values)]
        base.TAGS=tuple(range(1,(1<<widths[-1])+1))
        m.fixture=dict(m.fixture,widths=widths,moduli=list(moduli),initial=list(values))
        os,op,fields=base.initial_fixture(m);old_point=hh.Program(code,labels,meta);old_receipts=[]
        for reverse in(False,True):
            before=old_point.native_actions;spy,count=baseline_spy(base,m,old_div);m.w.Unsigned.divmod=spy
            try:r,_=old_leg(m,base,old_point,os,op,reverse)
            finally:m.w.Unsigned.divmod=old_div
            r['remaining_source_symbol_actions']=r['encoded_source_symbol_actions']-(old_point.native_actions-before)
            r['old_division_actions'],r['old_division_calls']=count['actions'],count['calls']
            old_receipts.append(r)
            if not reverse:baseline=(bytes(os.cells),dict(op.cells))
        source,payload,fields=base.initial_fixture(m);original=(bytes(source.cells),source.head,dict(payload.cells),payload.head)
        point=hh.Program(code,labels,meta);legs=[];owners=[]
        for reverse in(False,True):
            machine=hw.Program(dc,dl,dm);observed=Observations(m,reverse);binder=AllBinding(machine,hw,observed)
            changed,_=binding.join(hjoin,caller,binder,raw);m.w.Unsigned.divmod=unavailable
            before_native=point.native_actions
            try:receipt,stock=changed.run_leg(m,base,point,source,payload,reverse)
            finally:m.w.Unsigned.divmod=old_div
            need(fallback_calls==0 and binder.replacements==binder.raw_calls==len(observed.calls),'every actual raw call used literal core; no old provider')
            need(binder.boundary_actions==0 and binder.granted_extra_cells==28,'no half/ordinal query; explicit persistent grants')
            need(binder.finite_control_invoice==256+32*binder.invocations+16400*binder.raw_calls,'complete declared finite-control invoice')
            receipt['remaining_source_symbol_actions']=receipt.pop('encoded_source_symbol_actions')-(point.native_actions-before_native)-machine.numeric_actions
            old=old_receipts[int(reverse)]
            need(receipt['remaining_source_symbol_actions']==old['remaining_source_symbol_actions']-old['old_division_actions'] and
                 binder.raw_calls==old['old_division_calls'],'exact same-workload removal of every old division action')
            receipt['remaining_outer_adapter_symbol_actions']=receipt.pop('outer_adapter_symbol_actions')-machine.selector_actions
            need(receipt['remaining_outer_adapter_symbol_actions']==old_receipts[int(reverse)]['outer_adapter_symbol_actions'],
                 'true marker overlap removed exactly once for the same encoded height')
            receipt.update(literal_division_instructions=machine.total,literal_numeric_actions=machine.numeric_actions,
                           literal_selector_actions=machine.selector_actions,finite_metadata_invoice=binder.finite_control_invoice,
                           raw_divisions=binder.raw_calls,producer_invocations=binder.invocations,grant_extra_cells=28,
                           producers=observed.producers)
            relations=counterfactuals(m,old_div,observed);all_relations.extend(relations)
            legs.append(receipt);owners.extend(stock[0])
            if not reverse:need((bytes(source.cells),dict(payload.cells))==baseline,'exact baseline forward source and payload')
        need((bytes(source.cells),source.head,dict(payload.cells),payload.head)==original,'complete actual forward/inverse source/payload/key restoration')
        need(len(owners)==len({id(x) for x in owners})==200,'all actual histories retained')
        cases.append({'moduli':moduli,'values':values,'widths':widths,'payload_records':len(base.TAGS),
                      'directions':legs,'baseline_B9_directions':old_receipts,'retained_symbol_cells':sum(map(len,owners))})
    whole,relations=full_source(base,m,hw,AllBinding,dc,dl,dm,old_div,unavailable);all_relations.extend(relations)
    positive_provider_calls=fallback_calls;need(positive_provider_calls==0,'zero old division calls in admitted executions')
    negatives=controls(base,m,hw,binding,AllBinding,dc,dl,dm,old_div,unavailable)
    need(fallback_calls==1,'fallback sentinel detects deliberate mutation')
    need(any(len(p['left'])>1 for c in cases for r in c['directions'] for p in r['producers']),'actual nonleaf numerical group joined')
    need(any(r['D']==1 for r in all_relations),'actual unit divisors joined')
    print(json.dumps({'status':'PASS','graph':d.digest(dc),'cases':cases,'full_source':whole,'relations':all_relations,
                      'raw_divisions':len(all_relations),'old_provider_calls_during_actual_execution':positive_provider_calls,
                      'deliberate_fallback_calls':fallback_calls,'controls':negatives},indent=2,sort_keys=True))

if __name__=='__main__':main()
