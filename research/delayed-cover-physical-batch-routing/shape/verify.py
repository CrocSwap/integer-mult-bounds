"""Read-only exact bounded replay; all numeric oracles stay outside programs."""
from pathlib import Path
from hashlib import sha256,sha1
import argparse
import ast
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    for item in json.loads((HERE/'SOURCES.json').read_text())['sources']:
        b=(HERE/item['copy']).read_bytes()
        need(len(b)==item['bytes']and sha256(b).hexdigest()==item['sha256'],'exact predecessor SHA')
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==item['git_blob'],'exact predecessor Git blob')
    for name in ('producer.py','bridge.py'):
        tree=ast.parse((HERE/name).read_text())
        need(not any(isinstance(x,ast.Attribute)and x.attr in
                     {'head','cells','counts','visited','floor','minimum'}for x in ast.walk(tree)),
             'program must not inspect physical coordinates or counters')


authenticate()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module


P=load('producer','producer.py')
m=P.m


def bits_packet(tape):
    """Fixture-only observer. No decoded value enters an executed program."""
    need(tape.head==1 and tape.cells.get(0)==m.LEFT,'packet origin')
    end=1
    while tape.cells.get(end,m.BLANK)in(m.ZERO,m.ONE):end+=1
    need(tape.cells.get(end)==m.RIGHT and len(tape.cells)==end+1,'complete packet')
    return [int(tape.cells[i]==m.ONE)for i in range(1,end)]


def binary_packet(tape):
    b=bits_packet(tape)
    need(b and b[-1]==1,'canonical positive packet')
    return sum(v<<i for i,v in enumerate(b))


def exact_case(low,high,child_a,parent_r,linked=False,label='toy'):
    parent_a=low*high*child_a
    child_r=high*parent_r
    parent_volume=parent_a*low*parent_r
    child_volume=parent_a*parent_r
    program=P.linked_split(low)if linked else P.build(low)
    tapes=[m.Tape()for _ in range(program.tapes)]
    for role,value in ((0,parent_a),(1,high),(2,parent_r)):
        tapes[role]=m.binary(value)
    source_roles=[0,1,2]
    payload=[]
    if linked:
        # This is ONE complete parent split bank, never the full parent V.
        payload=[int((i*i+3*i+1)%7<3)for i in range(child_volume)]
        tapes[low+9]=m.marked(m.ONE if b else m.ZERO for b in payload)
        source_roles.append(low+9)
    saved={j:(tapes[j].cells.copy(),tapes[j].head)for j in source_roles}
    machine=m.Machine(program,tapes).run(1000*parent_volume+10000)
    need(binary_packet(tapes[3])==child_a,'literal exact quotient grant')
    need(binary_packet(tapes[4])==child_r,'literal product grant')
    need(all(not tapes[j].cells and tapes[j].head==0 for j in (5,6,7,8)),'all conversion and guide scratch erased')
    if linked:
        for bank in range(low):
            expected=[payload[(a*low+bank)*child_r+rr]
                      for a in range(child_a)for rr in range(child_r)]
            need(bits_packet(tapes[9+bank])==expected,'actual PR6719 split consumes generated grants')
    for j,(cells,head)in saved.items():
        need(tapes[j].cells==cells and tapes[j].head==head,'source bytes and heads restored')
        need(not machine.write_positions[j],'source never written')
    # Explicit, charged physical retirement, not host dictionary clearing.
    consumer=m.Machine(P.retire_delivered(low,linked),tapes).run(1000*parent_volume+10000)
    owned=[3,4]+(list(range(9,9+low))if linked else [])
    need(all(not tapes[j].cells and tapes[j].head==0 for j in owned),'delivered owned copies physically retired')
    need(all(tapes[j].cells==cells and tapes[j].head==head for j,(cells,head)in saved.items()),'consumer preserves sources')
    total=machine.steps+consumer.steps
    visits=[machine.visits[j]|consumer.visits[j]for j in range(program.tapes)]
    need(total<=1000*parent_volume,'coarse proved complete local time budget')
    need(sum(len(v)for v in visits)<=100*parent_volume,'coarse proved visited budget')
    return {'L':low,'H':high,'A_parent':parent_a,'R_parent':parent_r,
            'A_child':child_a,'R_child':child_r,'parent_volume':parent_volume,
            'child_volume':child_volume,'linked_actual_child_split':linked,'label':label,
            'fixed_tapes':program.tapes,'literal_instructions':len(program.instructions),
            'literal_program_sha256':sha256(json.dumps(program.instructions,separators=(',',':')).encode()).hexdigest(),
            'execution_microtransitions':machine.steps,'consumer_microtransitions':consumer.steps,
            'visited_cells':sum(len(v)for v in visits)}


def rejects(fn):
    try:fn()
    except (ValueError,RuntimeError):return True
    raise ValueError('semantic fault was accepted')


def invalid_case(parent_a,high,parent_r,occupied=False,noncanonical=False):
    tapes=[m.Tape()for _ in range(9)]
    for j,x in enumerate((parent_a,high,parent_r)):tapes[j]=m.binary(x)
    if occupied:tapes[3]=m.Tape({0:m.ONE},0)
    if noncanonical:tapes[0]=m.marked((m.ONE,m.ZERO))
    return m.Machine(P.build(2),tapes).run(100000)


def codec_stack_case():
    B=load('bridge','bridge.py');C=B.C;s=C.s
    class ObservedTape(s.Tape):
        """Hardware observation only; the executed programs cannot query it."""
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.visited=set();self.written=set();self.child_floor=None;self.guard=None
        def read(self):
            need(self.child_floor is None or self.head>=self.child_floor,'child crosses segment boundary')
            self.visited.add(self.head);return super().read()
        def write(self,value):
            need(self.child_floor is None or self.head>=self.child_floor,'child writes across segment boundary')
            if self.guard is not None:
                end,old=self.guard
                need(self.head>=end or value==old[self.head],'parked parent overwritten')
            self.visited.add(self.head);self.written.add(self.head);super().write(value)
        def move(self,direction):
            self.visited.add(self.head);super().move(direction)
            need(self.child_floor is None or self.head>=self.child_floor,'child moves across segment boundary')
            self.visited.add(self.head)
    def put(tape,symbols,base=False,body=True):
        for symbol in symbols:
            for shift in (2,1,0):s.emit(tape,(symbol>>shift)&1)
        C.origin(tape,s.BASE if base else s.LEFT)
        if body:C.three_moves(tape,1)
    def descriptor(n):
        return [m.LEFT]+[m.ONE if n>>i&1 else m.ZERO for i in range(n.bit_length())]+[m.RIGHT]
    def observed_packet(tape):
        start=tape.head
        while start>tape.floor and tape.cells[start-1]not in(s.LEFT,s.BASE):start-=1
        end=start
        while end<len(tape.cells)and tape.cells[end]!=s.BLANK:end+=1
        raw=tape.cells[start:end]
        need(len(raw)%3==0 and all(b in(0,1)for b in raw),'complete physical codec packet')
        return [4*raw[i]+2*raw[i+1]+raw[i+2]for i in range(0,len(raw),3)]

    low,high,parent_a,parent_r=4,3,12,3
    counts=s.Counts();prefix=11
    payloads=[ObservedTape([1]*prefix,counts=counts)for _ in range(max(16,low+8))]
    control=ObservedTape([0]*prefix,s.BASE,counts)
    phase=ObservedTape([],s.BASE,counts)
    relays=[ObservedTape([],s.BASE,counts)for _ in range(4)]
    depth=ObservedTape([],s.BASE,counts)
    high_header=ObservedTape([],s.BASE,counts)
    scratch=[ObservedTape([],s.BASE,counts)for _ in range(4)]
    pipe=C.Pipeline(low,payloads,control,phase,relays,depth);ports=pipe.p
    volume=parent_a*low*parent_r
    data=[int((i*i+3*i+1)%7<3)for i in range(volume)]
    put(payloads[ports['source']],[m.LEFT]+[m.ONE if b else m.ZERO for b in data]+[m.RIGHT])
    put(payloads[ports['repeats_input']],descriptor(parent_a))
    put(payloads[ports['block_input']],descriptor(parent_r))
    put(high_header,descriptor(high),base=True)
    s.emit(depth,1);C.origin(depth,s.BASE)
    all_tapes=payloads+[control,phase]+relays+[depth,high_header]+scratch
    need(len(all_tapes)==28,'K+12 fixed physical tapes')
    source_roles=[payloads[ports[j]]for j in ('source','repeats_input','block_input')]+[high_header,depth]
    saved=[(t,t.cells.copy(),t.head)for t in source_roles]
    for t in all_tapes:t.visited.clear();t.written.clear()
    begin=counts.total
    B.GrantBridge(low).run(payloads[ports['repeats_input']],high_header,
                           payloads[ports['block_input']],relays[1],relays[2],scratch)
    need(observed_packet(relays[1])==descriptor(1),'physically produced A_child=1')
    need(observed_packet(relays[2])==descriptor(9),'physically produced R_child=9')
    need(all(all(v==s.BLANK for v in t.cells[1:])and t.head==1 for t in scratch),'coded logical blanks physically erased')
    generated=counts.total-begin
    live=[];returns=[];push,pop=s.Stack.push,s.Stack.pop
    def observed_push(stack,present):
        snap=[]
        for tape in stack.payloads:
            start=tape.head
            while start>tape.floor and tape.cells[start-1]!=s.LEFT:start-=1
            end=start
            while end<len(tape.cells)and tape.cells[end]!=s.BLANK:end+=1
            snap.append((tape.cells[:end],tape.head,end))
        push(stack,present)
        for t,(old,_,end)in zip(stack.payloads,snap):t.guard=(end,old);t.child_floor=end
        live.append(snap)
    def observed_pop(stack):
        for t in stack.payloads:t.child_floor=None
        value=pop(stack);snap=live.pop()
        for t,(old,head,end)in zip(stack.payloads,snap):
            need(t.cells[:end]==old and t.head==head,'physical pop restores all parent bytes/heads')
            t.guard=None
        returns.append(sum(x[2]for x in snap));return value
    s.Stack.push,s.Stack.pop=observed_push,observed_pop
    try:pipe.run()
    finally:s.Stack.push,s.Stack.pop=push,pop
    expected=[]
    for ap in range(parent_a):
        for lp in range(low):
            for rp in range(parent_r):
                bit=data[(ap*low+lp)*parent_r+rp]
                expected.append(1-bit if lp<2 and (ap//high)%low==0 else bit)
    need(observed_packet(payloads[ports['output']])==[m.LEFT]+[m.ONE if b else m.ZERO for b in expected]+[m.RIGHT],
         'generated grants complete actual high-address child return')
    need(len(returns)==2 and not live,'two real sequential sibling returns')
    pipe.consume_output()
    for grant in (relays[1],relays[2]):C.clear_base(grant)
    for t,old,head in saved:
        need(t.cells[:len(old)]==old and t.head==head,'root source/A/R/H/depth bytes and heads restored')
        need(not any(i<len(old)for i in t.written),'original source/header bytes never written')
    readonly={id(t)for t in source_roles}
    for t in all_tapes:
        if id(t)in readonly:continue
        need(all(v==s.BLANK for v in t.cells[t.floor+1:]),'all owned copies and scratch physically erased')
        need(t.head==t.floor+1,'retired physical head restored')
    return {'L':low,'H':high,'q':3,'N':1,'B':2,'w':2,'D':2,'j':0,
            'A_parent':parent_a,'R_parent':parent_r,'A_child':1,'R_child':9,
            'root_volume':volume,'child_volume':volume//low,'physical_tapes':len(all_tapes),
            'grant_production_and_physical_scratch_erasure_actions':generated,
            'total_physical_actions_including_grant_output_retirement':counts.total-begin,
            'visited_cells':sum(len(t.visited)for t in all_tapes),
            'retained_backing':sum(len(t.cells)for t in all_tapes),
            'complete_parent_restorations':len(returns),'output_sha256':sha256(bytes(expected)).hexdigest(),
            'boundary':'Root-before-stack production from A/H/R headers; bit-complement leaf; no weight evaluator or arbitrary-depth production claim.'}


def check():
    cases=[]
    rows=[(2,1,1,1,'toy'),(2,2,3,4,'toy'),(3,3,2,3,'toy'),
          (4,3,1,3,'GL1 q3 w2 D2 j0'),(4,3,1,9,'GL1 q3 w2 D3 j1'),
          (4,3,12,3,'GL1 q3 w2 D3 j0'),(4,9,1,9,'GL1 q3 w3 D2 j0'),
          (96,81,1,81,'GL2 q3 w2 D2 j0; descriptors only, no huge full payload')]
    for low,high,ac,r,label in rows:cases.append(exact_case(low,high,ac,r,label=label))
    for low,high,ac,r,label in rows[3:7]:cases.append(exact_case(low,high,ac,r,linked=True,label=label))
    controls={'nondivisible_A':rejects(lambda:invalid_case(5,2,3)),
              'A_smaller_than_LH':rejects(lambda:invalid_case(2,2,1)),
              'occupied_owned_output':rejects(lambda:invalid_case(4,2,1,occupied=True)),
              'noncanonical_binary_input':rejects(lambda:invalid_case(4,2,1,noncanonical=True))}
    return {'schema':'delayed-cover-child-shape-producer/1','status':'PASS_LITERAL_CHILD_GRANTS_TO_ROUTER',
            'cases':cases,'negative_controls':controls,'actual_codec_stack':codec_stack_case(),
            'scope':'A,H,R physical headers -> exact child grants -> literal actual child split. One real codec/stack edge only; H-from-width and ancestor-weight production remain explicit separate obligations.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    value=check();path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    else:need(value==json.loads(path.read_text()),'stable exact receipt')
    print(json.dumps({'status':value['status'],'arithmetic_or_linked_cases':len(value['cases']),
                      'codec_stack_physical_actions':value['actual_codec_stack']['total_physical_actions_including_grant_output_retirement']},sort_keys=True))
