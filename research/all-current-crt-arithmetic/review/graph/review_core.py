"""Independent literal CPU/physical divider review; no author hardware imports."""
import argparse
import ast
from hashlib import sha256,sha1
import json
from pathlib import Path
import sys
import types


def need(ok,message):
    if not ok:raise ValueError(message)


def load(path,name,raw=None):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes() if raw is None else raw,str(path),'exec'),m.__dict__)
    return m


class Sparse:
    def __init__(self,values,head,lo,hi):
        self.cells=dict(values);self.head=head;self.lo=lo;self.hi=hi;self.actions=0
    def read(self):
        need(self.lo<=self.head<self.hi,'independent sparse read extent');self.actions+=1
        return self.cells.get(self.head,'_')
    def write(self,s):
        need(self.lo<=self.head<self.hi,'independent sparse write extent');self.actions+=1
        if s=='_':self.cells.pop(self.head,None)
        else:self.cells[self.head]=s
    def step(self,d):
        need(d in(-1,1) and self.lo<=self.head+d<self.hi,'independent sparse movement extent')
        self.actions+=1;self.head+=d


class NumericPort:
    """Actual HostedWord backing, with independently implemented meter updates."""
    alphabet='01LR_'
    def __init__(self,word):self.word=word
    @property
    def cells(self):return self.word.port.cells
    @property
    def head(self):return self.word.port.head
    def read(self):
        need(0<=self.head<len(self.cells),'backed numerical read')
        self.word.arena.meter.reads+=1;return self.alphabet[self.cells[self.head]]
    def write(self,s):
        need(s in '01R_' and 0<=self.head<len(self.cells),'backed numerical write')
        self.word.arena.meter.writes+=1;self.cells[self.head]=self.alphabet.index(s)
    def step(self,d):
        need(d in(-1,1) and 0<=self.head+d<len(self.cells),'backed numerical movement')
        self.word.arena.meter.moves+=1;self.word.port.head+=d


class GrantedSelector:
    def __init__(self,tape,origin=0,granted_extent=8):
        need(granted_extent>=8 and len(tape.cells)>=origin+granted_extent and tape.head==origin,
             'explicit independent eight-cell grant')
        self.tape=tape;self.origin=origin
    @property
    def cells(self):return self.tape.cells
    @property
    def head(self):return self.tape.head
    def read(self):
        need(self.origin<=self.head<self.origin+8,'descriptor read grant')
        self.tape.actions+=1;return self.cells[self.head]
    def write(self,s):
        need(self.origin<=self.head<self.origin+8,'descriptor write grant')
        self.tape.actions+=1;self.cells[self.head]=s
    def step(self,d):
        need(d in(-1,1) and self.origin<=self.head+d<self.origin+8,'descriptor movement grant')
        self.tape.actions+=1;self.tape.head+=d


class CPU:
    def __init__(self,code,labels,metadata):
        self.code,self.labels,self.metadata=code,labels,metadata
        self.total=self.numeric_actions=self.selector_actions=self.calls=0
        self.history=[None]*68;self.receipts=[];self.logical=set(metadata['logical_to_physical'])
    def run(self,ports,entry='DIVIDE',limit=30000000):
        need(len(ports)==68 and len({id(t.cells) for t in ports})==68,'independent distinct68 backing owners')
        pc=self.metadata['entries'][entry] if isinstance(entry,str) else entry
        steps=nums=sels=logical=0;hist=[[t.head,t.head] for t in ports]
        writes=[0]*68;counts={}
        while steps<limit:
            row=self.code[pc];op=row[0];steps+=1;logical+=pc in self.logical
            counts[op]=counts.get(op,0)+1
            if op in 'RWM':
                role=row[1];port=ports[role];nums+=role<64;sels+=role>=64
            if op=='R':pc=row[2][port.read()]
            elif op=='W':port.write(row[2]);writes[role]+=1;pc+=1
            elif op=='M':
                port.step(row[2]);hist[role][0]=min(hist[role][0],port.head)
                hist[role][1]=max(hist[role][1],port.head);pc+=1
            elif op=='J':pc=row[1]
            elif op=='H':
                record=dict(status=row[1],instructions=steps,numeric_actions=nums,selector_actions=sels,
                            logical_instructions=logical,writes=writes,history=hist,op_counts=counts)
                self.total+=steps;self.numeric_actions+=nums;self.selector_actions+=sels;self.calls+=1
                for i,h in enumerate(hist):
                    prev=self.history[i];self.history[i]=h if prev is None else[min(prev[0],h[0]),max(prev[1],h[1])]
                self.receipts.append(record);return record
            else:raise ValueError('independent unknown opcode')
        raise ValueError('independent bounded replay watchdog')


def setters(program,ports,slots):
    need(len(slots)==4 and all(type(x)is int and 0<=x<64 for x in slots),'finite independent binding')
    for role,slot in enumerate(slots):
        result=program.run(ports,program.metadata['setters'][role][slot])
        need(result['status']=='BOUND' and result['instructions']==31,'exact fixed setter')


def fixture(p,n,d,slots,history=0):
    ports=[];ns,ds,qs,rs=slots
    for role in range(64):
        cells={0:'L',p+history+2:'EXTERIOR'}
        if role not in(qs,rs):
            value=n if role==ns else d if role==ds else (role*19+3)%(1<<p)
            cells.update({k+1:str(value>>k&1) for k in range(p)});cells[p+1]='R'
        ports.append(Sparse(cells,1,0,p+history+3))
    for origin in(3,7,2,11):
        cells={origin-1:'BEFORE',origin+8:'AFTER'}
        cells.update({origin+k:str(k%2) for k in range(8)})
        ports.append(Sparse(cells,origin,origin,origin+8))
    return ports


def boundary(ports,before,p,n,d,slots,retired=False):
    for role,port in enumerate(ports[:64]):
        wanted=dict(before[role][0])
        if role in slots[2:]:
            for k in range(1,p+2):wanted.pop(k,None)
            if not retired:
                value=n//d if role==slots[2] else n%d
                wanted.update({k+1:str(value>>k&1) for k in range(p)});wanted[p+1]='R'
        need(port.head==before[role][1] and port.cells==wanted,'full independent numerical boundary')
    for role,port in enumerate(ports[64:],64):
        origin=before[role][1];wanted={k:v for k,v in before[role][0].items() if not origin<=k<origin+8}
        need(port.head==origin and port.cells==wanted,'complete independent selector retirement/exterior')


def standalone_checks(code,labels,meta):
    cases=[]
    for p,n,d,slots,hist in [(4,15,7,(0,7,63,8),0),(5,29,4,(11,38,19,61),4099),
                             (7,0,1,(63,62,60,61),257),(9,511,255,(25,10,13,9),1021),
                             (17,109221,65535,(30,59,27,10),8193)]:
        ports=fixture(p,n,d,slots,hist);before=[(dict(t.cells),t.head) for t in ports]
        cpu=CPU(code,labels,meta);need(cpu.run(ports,'ACQUIRE')['instructions']==89,'exact acquisition')
        setters(cpu,ports,slots);out=cpu.run(ports);need(out['status']=='DONE','independent divide accepts')
        boundary(ports,before,p,n,d,slots)
        expected=18*p*p+36*p+458+(12*p+9)*(n//d).bit_count()
        need(out['logical_instructions']==expected,'independent exact logical bill')
        setters(cpu,ports,slots);ret=cpu.run(ports,'RETIRE')
        need(ret['status']=='RETIRED' and ret['logical_instructions']==14*p+131,'independent retirement bill')
        boundary(ports,before,p,n,d,slots,True)
        need(cpu.total<=16384*(p+2)**2,'independent lifecycle envelope')
        cases.append(dict(p=p,n=n,d=d,history=hist,slots=list(slots),instructions=cpu.total,
                          logical_division=out['logical_instructions']))
    return cases


def lowering_checks(code,meta,logical):
    """Project every physical path back to one logical instruction."""
    count=0;example=None
    mapping=meta['logical_to_physical']
    for i,row in enumerate(logical):
        start=mapping[i]
        if row[0] not in('R','W','M') or row[1]>=4:
            expected=row
            if row[0]=='R':expected=('R',row[1],{s:mapping[v] for s,v in row[2].items()})
            if row[0]=='J':expected=('J',mapping[row[1]])
            need(code[start]==expected,'complete unlowered instruction projection');continue
        for slot in range(64):
            symbols='L'+''.join(str(slot>>b&1) for b in range(6))+'R'
            pc=start;heads=[0]*4;seen=reads=moves=jumps=0
            while seen<=29:
                op,*args=code[pc]
                if op in('R','W','M') and args[0]<64:break
                seen+=1
                if op=='R':
                    need(args[0]==64+row[1],'dispatcher reads only its descriptor')
                    reads+=1;pc=args[1][symbols[heads[row[1]]]]
                elif op=='M':
                    need(args[0]==64+row[1],'dispatcher moves only its descriptor')
                    moves+=1;heads[row[1]]+=args[1]
                    need(0<=heads[row[1]]<8,'dispatcher eight-cell window');pc+=1
                elif op=='J':jumps+=1;pc=args[0]
                else:raise ValueError('dispatcher unexpected effect')
            need((seen,reads,moves,jumps)==(29,8,14,7) and heads==[0]*4,'paid full dispatch and return')
            need(code[pc][:2]==(row[0],slot),'exact dispatch physical port')
            if row[0]=='R':need(code[pc][2]=={s:mapping[v] for s,v in row[2].items()},'read projection')
            else:need(code[pc][2]==row[2] and code[pc+1]==('J',mapping[i+1]),'effect projection')
            count+=1
            if example is None:example=pc
    need(count==22272,'complete numerical dispatch coverage')
    return count,example


def core_controls(code,labels,meta):
    controls=[];p,n,d,slots=5,29,4,(11,38,19,61)
    def prepare(values=None):
        ports=fixture(p,n,d,slots);cpu=CPU(code,labels,meta)
        cpu.run(ports,'ACQUIRE');setters(cpu,ports,slots if values is None else values)
        return cpu,ports
    for label,edit in [
        ('alias descriptor',lambda ports:None),
        ('zero divisor',lambda ports:ports[38].cells.update({k:'0' for k in range(1,p+1)})),
        ('high divisor bit',lambda ports:ports[38].cells.update({p:'1'})),
        ('short divisor field',lambda ports:ports[38].cells.update({p:'R'})),
        ('malformed numerator digit',lambda ports:ports[11].cells.update({2:'|'})),
        ('short selector field',lambda ports:ports[64].cells.update({ports[64].head+3:'R'}))]:
        cpu,ports=prepare((11,11,19,61) if label=='alias descriptor' else None);edit(ports)
        need(cpu.run(ports)['status']=='MALFORMED',label+' detection');controls.append(label)
    cpu,ports=prepare();ports[4]=ports[3]
    try:cpu.run(ports)
    except ValueError:controls.append('physical backing alias')
    else:raise ValueError('physical backing alias escaped')
    small=types.SimpleNamespace(cells=['_']*7,head=0,actions=0)
    try:GrantedSelector(small,granted_extent=7)
    except ValueError:controls.append('missing eight-cell grant')
    else:raise ValueError('missing grant escaped')
    # Stale but well-formed live input can return; values must be checked.
    cpu,ports=prepare((12,38,19,61));before=[(dict(t.cells),t.head) for t in ports]
    need(cpu.run(ports)['status']=='DONE','stale donor returns')
    try:boundary(ports,before,p,n,d,slots)
    except ValueError:controls.append('returning stale operand')
    else:raise ValueError('stale operand escaped endpoint oracle')
    for label,role in [('returning wrong quotient',19),('returning borrowed-live corruption',5)]:
        cpu,ports=prepare();before=[(dict(t.cells),t.head) for t in ports]
        done=next(i for i,row in enumerate(code) if row==('H','DONE'))
        mutant=list(code);mutant[done]=('J',len(mutant))
        mutant.extend([('W',role,'0' if role==19 else '1'),('H','DONE')]);cpu.code=tuple(mutant)
        need(cpu.run(ports)['status']=='DONE',label+' returns')
        try:boundary(ports,before,p,n,d,slots)
        except ValueError:controls.append(label)
        else:raise ValueError(label+' escaped full-state oracle')
    # A single omitted physical erase still reaches RETIRED.
    cpu,ports=prepare();before=[(dict(t.cells),t.head) for t in ports];cpu.run(ports)
    setters(cpu,ports,slots)
    logical,_=AUTHOR.logical_graph();first=next(i for i in range(meta['logical_labels']['RETIRE'],len(logical))
                  if logical[i]==('W',2,'_'))
    pc=meta['logical_to_physical'][first]
    while not(code[pc][0]=='W' and code[pc][1]<64):
        row=code[pc]
        if row[0]=='R':pc=row[2][ports[row[1]].read()]
        elif row[0]=='M':ports[row[1]].step(row[2]);pc+=1
        elif row[0]=='J':pc=row[1]
        else:raise ValueError('retirement physical leaf search')
    mutated=list(code);mutated[pc]=('J',pc+1);cpu.code=tuple(mutated)
    need(cpu.run(ports,'RETIRE')['status']=='RETIRED','incomplete retirement returns')
    try:boundary(ports,before,p,n,d,slots,True)
    except ValueError:controls.append('returning incomplete retirement')
    else:raise ValueError('retirement corruption escaped full-history oracle')
    return controls


def word_value(word):
    end=word.cells.index(3,1)
    need(word.cells[0]==2 and all(x in(0,1) for x in word.cells[1:end]),'independent native word grammar')
    return sum(int(word.cells[k])<<(k-1) for k in range(1,end)),end-1


def old_allocation_relation(free,live,p,n,d):
    """Allocation trace only; integer oracle independently selects subtractions."""
    free=list(free);live=set(live)
    def take():
        slot=free.pop();need(slot not in live,'model free allocation');live.add(slot);return slot
    def retire(slot):live.remove(slot);free.append(slot)
    scan,q,r=take(),take(),take();rem=0
    for bit in reversed(range(p)):
        shifted=take();retire(r);rem=2*rem+(n>>bit&1)
        if rem>=d:
            r=take();retire(shifted);rem-=d
        else:r=shifted
    retire(scan)
    return q,r,free,live


def actual_join_checks(package,code,labels,meta):
    prior=load(package/'inputs/headers/verify.py','independent_frozen_B9')
    _,previous,base,m,headers,header_hw,caller,hcode,hlabels,hmeta,_=prior.modules()
    headjoin=load(package/'inputs/headers/join.py','independent_header_seams')
    bindpath=package/'binding.py';binding=load(bindpath,'independent_binding_under_review')
    callerpath=package/'inputs/headers/inputs/keypass/inputs/route/inputs/point/caller.py'
    caller_raw=callerpath.read_bytes()
    need(sha256(caller_raw).hexdigest()=='055e86590e1cb03555f9ef6f1d585f8c23453a4cc10cd7feda7362c77f7bce1c',
         'fixed actual caller source')
    cases=[];relations=[];typed_failures=[]
    for left,value,wrong_phase in [(5,1,False),(8,7,False),(5,1,True)]:
        m.fixture=dict(m.fixture,widths=[5,5,max(left.bit_length(),value.bit_length()),2],
                       moduli=[17,19,left,3],initial=[1,2,value,1])
        source,payload,_=base.initial_fixture(m)
        entry=(bytes(source.cells),source.head,dict(payload.cells),payload.head)
        point=header_hw.Program(hcode,hlabels,hmeta);legs=[]
        for reverse in(False,True):
            machine=CPU(code,labels,meta);pending={};local=[]
            def observe(stage,binder,arena,n,d,outputs):
                if stage=='before':
                    nv,p=word_value(n);dv,pd=word_value(d);need(p==pd,'actual equal-width operands')
                    need(all(arena.words[k].port is binder.iterator.guards[k] for k in range(8)),
                         'actual eight borrowed numerical guard backings')
                    need(all(arena.words[k].port is binder.iterator.bank.ports[k-5] for k in range(8,64)),
                         'actual56 owned numerical bank backings')
                    expected=[(17,19),(left,3)][len(local)]
                    if (nv,dv)!=expected:typed_failures.append(dict(actual=[nv,dv],expected=list(expected),wrong_phase=wrong_phase))
                    snapshot=[(bytes(w.cells),w.head,id(w.cells),id(w.port)) for w in arena.words]
                    pending.update(n=nv,d=dv,p=p,snapshot=snapshot,live=set(arena.live),
                                   old=old_allocation_relation(arena.available,arena.live,p,nv,dv),
                                   numeric=machine.numeric_actions,
                                   meter=sum(arena.meter.record()[k] for k in('reads','writes','moves')),
                                   port_meter=sum(sum(w.port.meter.record()[k] for k in('reads','writes','moves')) for w in arena.words))
                else:
                    q,r=outputs;nv,dv,p=pending['n'],pending['d'],pending['p']
                    need(word_value(q)==(nv//dv,p) and word_value(r)==(nv%dv,p),'independent actual quotient/remainder')
                    oldq,oldr,oldfree,oldlive=pending['old']
                    bijection={slot:slot for slot in pending['live']}
                    bijection.update({oldq:q.slot,oldr:r.slot});bijection.update(zip(oldfree,arena.available))
                    need(len(bijection)==len(set(bijection.values()))==64,'full independently modeled boundary bijection')
                    for a,b in bijection.items():need((a in oldlive)==(b in arena.live),'modeled live/free correspondence')
                    for slot,w in enumerate(arena.words):
                        old=pending['snapshot'][slot]
                        need(w.head==old[1]==1 and id(w.cells)==old[2] and id(w.port)==old[3],
                             'every real numerical owner and head identity')
                        if slot in pending['live']:need(bytes(w.cells)==old[0],'all incoming live bytes preserved')
                        if slot in arena.available:need(all(x==4 for x in w.cells[1:]),'entire free retained body zeroed')
                        need(all(x==4 for x in w.cells[p+2:]),'old larger numerical tail remains blank')
                    delta=sum(arena.meter.record()[k] for k in('reads','writes','moves'))-pending['meter']
                    physical=sum(sum(w.port.meter.record()[k] for k in('reads','writes','moves')) for w in arena.words)-pending['port_meter']
                    need(delta==machine.numeric_actions-pending['numeric'] and physical==0,'independent single numerical meter')
                    need(all(t.head==0 and all(x=='_' for x in t.cells) for t in binder.selectors),'all descriptor capabilities returned')
                    local.append(dict(n=nv,d=dv,p=p,actual_outputs=[q.slot,r.slot],old_outputs=[oldq,oldr],
                                      fixed_live=len(pending['live']),numeric_actions=delta,backing_meter_delta=physical,
                                      max_retained_word_cells=max(len(w.cells) for w in arena.words),
                                      exact_borrowed_owned_split=[8,56],bijection=sorted(bijection.items())))
            selected=binding
            if wrong_phase:
                raw=bindpath.read_bytes();needle=b'owner.phase=0 if owner.active else 6'
                need(raw.count(needle)==1,'unique finite source phase')
                selected=load(bindpath,'independent_wrong_source_phase',raw.replace(needle,b'owner.phase=1 if owner.active else 6'))
            binder=selected.Binding(machine,types.SimpleNamespace(NumericPort=NumericPort,GrantedSelector=GrantedSelector,setters=setters),observe)
            changed,generated=selected.join(headjoin,caller,binder,caller_raw)
            initial_native=point.native_actions
            receipt,stock=changed.run_leg(m,base,point,source,payload,reverse)
            need(binder.replacements==2 and len(local)==2 and binder.granted_extra_cells==28,'actual two current calls and explicit grants')
            source_remainder=receipt['encoded_source_symbol_actions']-(point.native_actions-initial_native)-machine.numeric_actions
            marker_remainder=receipt['outer_adapter_symbol_actions']-machine.selector_actions
            need(source_remainder>=0 and marker_remainder==14,'disjoint mixed-unit meter subtraction')
            need(binder.boundary_actions==8*binder.invocations,'paid unary-half queries')
            need(binder.finite_control_invoice==256+32*binder.invocations+16*binder.raw_calls+16384*binder.replacements,
                 'complete finite control bill')
            legs.append(dict(reverse=reverse,instructions=machine.total,numeric_actions=machine.numeric_actions,
                             selector_actions=machine.selector_actions,remaining_source=source_remainder,
                             remaining_markers=marker_remainder,query_actions=binder.boundary_actions,
                             finite_control=binder.finite_control_invoice,explicit_extra_grant=28))
            relations.extend(local)
        need((bytes(source.cells),source.head,dict(payload.cells),payload.head)==entry,'complete actual source/payload roundtrip')
        cases.append(dict(left=left,value=value,wrong_phase=wrong_phase,legs=legs,roundtrip=True))
    need(typed_failures and all(x['wrong_phase'] for x in typed_failures),'returning wrong-source-phase detection only')
    return cases,relations,typed_failures


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--write',type=Path);args=parser.parse_args();package=args.package.resolve()
    pins={'divider.py':'5caa0cb16881197ccf9acdb6cbdc3c775549c4f8d5273d22d6a3a8e633fd1a67',
          'hardware.py':'de47e14fc50d330d2fbdb13e28042a4def07249496558b14986c133831cc0886',
          'binding.py':'41e9168a6aa87ada89d3f6409388d90f9b90321e8b7d4473378ab6fcd4c2b011',
          'PROOF.md':'bf387e6be55756d19ec3777dd78288cbe1b48f266c2886309997aeba0fa27bd2'}
    for name,digest in pins.items():need(sha256((package/name).read_bytes()).hexdigest()==digest,'reviewed scientific byte pin '+name)
    sourcepins=json.loads((package/'SOURCE-PINS.json').read_text())['files']
    for pin in sourcepins:
        data=(package/pin['local']).read_bytes()
        need(len(data)==pin['bytes'] and sha256(data).hexdigest()==pin['sha256'],'retained source exact bytes')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],'retained source exact Git blob')
    global AUTHOR
    AUTHOR=load(package/'divider.py','independent_frozen_graph');code,labels,meta=AUTHOR.compile_divider()
    graph=sha256(json.dumps(code,separators=(',',':'),sort_keys=True).encode()).hexdigest()
    need(graph=='d36e8220def8efb2baed793d0bea6f0a19b0903b5b005b730652b5bb7d121194','reviewed full graph')
    logical,_=AUTHOR.logical_graph();dispatch,example=lowering_checks(code,meta,logical)
    mutant=list(code);mutant[example]=(mutant[example][0],(mutant[example][1]+1)%64,mutant[example][2])
    try:lowering_checks(mutant,meta,logical)
    except ValueError:pass
    else:raise ValueError('wrong-port dispatch mutant escaped')
    standalone=standalone_checks(code,labels,meta);controls=core_controls(code,labels,meta)
    actual,relations,typed=actual_join_checks(package,code,labels,meta)
    result=dict(status='PASS',scientific_pins=pins,graph=graph,locations=len(code),logical_locations=len(logical),
                retained_source_objects=len(sourcepins),dispatch_instances=dispatch,wrong_port_mutant_detected=True,
                standalone=standalone,controls=controls,actual_cases=actual,independent_allocation_relations=relations,
                returning_wrong_source_phase=typed,
                scope='Independent graph CPU, direct integer oracle and allocation-only source relation; retained B9 source/header providers remain external.')
    out=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(out)
    print(out,end='')


if __name__=='__main__':main()
