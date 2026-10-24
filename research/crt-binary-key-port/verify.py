"""Independent block semantics and actual caller continuation for the bit port.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
All decoding and source arithmetic in this file are external verifier/outer control.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name,path):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m


def modules():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        raw=(ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256 drift')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob drift')
    paths={'source':'crt-paid-key-service/service.py','query':'crt-uniform-rom-query/machine.py',
           'bridge':'crt-mask-repair-bridge/bridge.py','oracle':'crt-mask-repair-bridge/key_subroutine.py',
           'native':'crt-dense-guard-scan/machine.py','crt':'unconditional-batched-crt/check_batched_crt.py'}
    result={k:load('binary_port_'+k,ROOT/'research'/path) for k,path in paths.items()}
    result['binary']=load('binary_port_impl',P/'binary.py');return result


# Independent representation (no compiler encoding helper).
TABLE=['_','L','0','1','R','<','>','=']


def encode(symbol):
    number=TABLE.index(symbol) if type(symbol) is str else 4096+symbol[1]
    return tuple(int(c) for c in format(number,'013b')[::-1])


def encode_value(value):
    return ((int(value),)+(0,)*12+(1,)) if type(value) is bool else encode(value)+(0,)


def decode(block):
    n=sum(v*2**i for i,v in enumerate(block))
    if n<8:return TABLE[n]
    need(n>=4096,'invalid symbol code');return ('R',n-4096)


def packet(symbols):return [bit for symbol in symbols for bit in encode(symbol)]


def physical_word(tape,cell):return tuple(tape.cells.get(13*cell+j,0) for j in range(13))


def observe_register(machine,registers,name):
    return tuple(machine.registers[registers[name,j]] for j in range(14))


def primitive_checks(b):
    values=TABLE+[('R',i) for i in range(4096)]
    encodings=[encode(v) for v in values]
    need(len(set(encodings))==4104,'injective complete caller alphabet')
    need(all(b.bits(v)==encode(v) and decode(encode(v))==v for v in values),'independent encoding')
    read,_,rr=b.compile_program([('read','x','a'),('halt','accept')])
    write,_,wr=b.compile_program([('write_reg','x','a'),('halt','accept')])
    for v in values:
        tape=b.BitTape(encode(v));m=b.Machine(read,len(rr),{'x':tape});m.run()
        need(observe_register(m,rr,'a')==encode_value(v) and tape.head==0,'all-symbol read')
        tape=b.BitTape((1,)*13);m=b.Machine(write,len(wr),{'x':tape})
        for j,x in enumerate(encode_value(v)):
            if ('a',j) in wr:m.registers[wr['a',j]]=x
        m.run();need(physical_word(tape,0)==encode(v) and tape.head==0,'all-symbol dirty overwrite')
    tests=0
    # The tagged cases distinguish True/L and False/blank; every pair differs
    # in either a specific low/high position, a payload bit, or the Boolean tag.
    pairs=[(x,y) for x in TABLE+[True,False] for y in TABLE+[True,False]]
    pairs += [(('R',x),('R',x^(1<<j))) for x in (0,1,4095) for j in range(12)]
    for x,y in pairs:
        program,_,regs=b.compile_program([('eq_reg','a','b','z'),('halt','accept')])
        m=b.Machine(program,len(regs),{})
        for name,value in [('a',x),('b',y)]:
            for j,bit in enumerate(encode_value(value)):
                if (name,j) in regs:m.registers[regs[name,j]]=bit
        m.run();need(observe_register(m,regs,'z')==encode_value(type(x)==type(y) and x==y),'tagged equality');tests+=1
    for op in ('xorbit','andbit','orbit'):
        for x in '01':
            for y in '01':
                for dst in ('a','b','z'):
                    program,_,regs=b.compile_program([(op,'a','b',dst),('halt','accept')]);m=b.Machine(program,len(regs),{})
                    for name,value in [('a',x),('b',y)]:
                        for j,bit in enumerate(encode_value(value)):
                            if (name,j) in regs:m.registers[regs[name,j]]=bit
                    m.run();v=((x!=y) if op=='xorbit' else (x=='1' and y=='1') if op=='andbit' else (x=='1' or y=='1'))
                    need(observe_register(m,regs,dst)==encode_value('1' if v else '0'),'bit arithmetic alias truth table');tests+=1
    return dict(symbols=4104,read_write_cases=8208,boolean_cases=tests)


def source_step(code,state):
    """Independent marker-machine semantics, used only by the audit observer."""
    pc,regs,cells,heads=state;op,*a=code[pc];pc+=1
    if op=='read':regs[a[1]]=cells[a[0]].get(heads[a[0]],'_')
    elif op in ('write','write_reg'):cells[a[0]][heads[a[0]]]=a[1] if op=='write' else regs[a[1]]
    elif op=='move':heads[a[0]]+=a[1]
    elif op=='set':regs[a[0]]=a[1]
    elif op=='copy':regs[a[1]]=regs[a[0]]
    elif op=='eq':regs[a[2]]=regs[a[0]]==a[1]
    elif op=='eq_reg':regs[a[2]]=regs[a[0]]==regs[a[1]]
    elif op in ('xorbit','andbit','orbit'):
        x=regs[a[0]]=='1';y=regs[a[1]]=='1'
        regs[a[2]]='1' if ((x!=y) if op=='xorbit' else x and y if op=='andbit' else x or y) else '0'
    elif op=='branch':pc=a[1] if regs[a[0]] else a[2]
    elif op=='jump':pc=a[0]
    elif op=='halt':pass
    else:raise ValueError('unknown source opcode')
    return pc,regs,cells,heads


def key_run(mod,target,table,address,audited=False,fault=None):
    b=mod['binary'];source,_=mod['source'].assemble(mod['query'],target)
    program,starts,regs=b.compile_program(source,fault,lifecycle=True)
    initial={name:[] for name in mod['source'].OWNED_WIDTHS}
    initial.update(counter=['<',*format(address,'012b'),'>'],rom=['L',*map(str,table),'R'],stream=['<',('R',4095),('R',0)])
    tapes={role:b.BitTape(packet(cells),39 if role=='stream' else 0) for role,cells in initial.items()}
    m=b.Machine(program,len(regs),tapes);m.registers[:]=[1]*len(regs);source_counts=Counter();charged=0
    if audited:
        for _ in range(starts[0]):m.step()
        charged=starts[0]
        state=(0,{}, {r:dict(enumerate(c)) for r,c in initial.items()}, {r:3 if r=='stream' else 0 for r in initial})
        while m.status is None:
            pc=state[0];need(m.pc==starts[pc],'source/micro control boundary')
            op,*a=source[pc];state=source_step(source,state)
            length=starts[pc+1]-starts[pc]
            for _ in range(length):m.step()
            charged+=length;source_counts[op]+=1
            if op!='halt':need(m.pc==starts[state[0]],'relocated jump/branch')
            for role in initial:need(tapes[role].head==13*state[3][role],'physical head scaling')
            if op in ('write','write_reg'):
                role=a[0];pos=state[3][role];need(physical_word(tapes[role],pos)==encode(state[2][role][pos]),'binary write simulation')
            dest=(a[1] if op in ('read','copy') else a[0] if op=='set' else a[2] if op in ('eq','eq_reg','xorbit','andbit','orbit') else None)
            if dest is not None:need(observe_register(m,regs,dest)==encode_value(state[1][dest]),'register simulation')
        need(charged==sum(m.census.values()),'complete block instruction invoice')
    else:m.run()
    need(m.status=='accept' and not any(m.registers),'binary acceptance and control erasure')
    expected=mod['oracle'].ReverseWordKey(target,table).key_of(format(address,'012b'))
    actual=''.join(decode(physical_word(tapes['stream'],i)) for i in range(3,15))
    need(actual==expected,'key equals independent retained word')
    for r in ('counter','rom'):need(tapes[r].cells=={i:v for i,v in enumerate(packet(initial[r])) if v} and tapes[r].head==0,'borrowed restoration')
    for r in mod['source'].OWNED_WIDTHS:need(not tapes[r].cells and tapes[r].head==0,'private bit erasure and return')
    need(tapes['stream'].head==195 and all(physical_word(tapes['stream'],i)==encode(c) for i,c in enumerate(initial['stream'])),'opaque prefix and 156-bit append')
    need(sum(m.census.values())<=43*3_287_110+2*len(regs),'binary static bound')
    return dict(target=target,address=address,key=actual,binary_actions=sum(m.census.values()),audited_source_instructions=sum(source_counts.values()),census=dict(sorted(m.census.items())))


def rejection_checks(mod):
    b=mod['binary'];source,_=mod['source'].assemble(mod['query'],2)
    program,starts,regs=b.compile_program(source,lifecycle=True);rows=[]
    for payload in ('0'*11,'0'*13,'00000_000000'):
        tapes={name:b.BitTape() for name in mod['source'].OWNED_WIDTHS}
        tapes.update(counter=b.BitTape(packet(['<',*payload,'>'])),rom=b.BitTape(packet(['L',*('0'*32),'R'])),stream=b.BitTape(packet(['<',('R',4095)]),26))
        before={role:dict(tapes[role].cells) for role in ('counter','rom','stream')}
        m=b.Machine(program,len(regs),tapes);m.registers[:]=[1]*len(regs);m.run()
        need(m.status=='reject' and not any(m.registers),'framed binary rejection and control erase')
        need(all(tapes[r].cells==before[r] and tapes[r].head==(26 if r=='stream' else 0) for r in before),'rejected borrowed/append port preserved')
        need(all(not tapes[r].cells and tapes[r].head==0 for r in mod['source'].OWNED_WIDTHS),'rejected private bit cleanup')
        rows.append(sum(m.census.values()))
    return rows


class Facade:
    """Unlowered outer caller only. Its storage is the SAME physical bit tape."""
    def __init__(self,b,symbols):self.raw=b.BitTape(packet(symbols))
    def read(self):
        data=[]
        for j in range(13):
            data.append(self.raw.read())
            if j<12:self.raw.move(1)
        for _ in range(12):self.raw.move(-1)
        return decode(data)
    def write(self,symbol):
        for j,bit in enumerate(encode(symbol)):
            self.raw.write(bit)
            if j<12:self.raw.move(1)
        for _ in range(12):self.raw.move(-1)
    def move(self,d):
        for _ in range(13):self.raw.move(d)


class Captured(Exception):pass


def caller_port(mod):
    b=mod['binary'];crt=mod['crt'];bridge=mod['bridge'];target=2
    nets=[crt.benes(crt.rotation(8,5,(2*a)%5 if a<3 else 0)) for a in range(4)]
    table=[nets[a][2][1][v] for a in range(4) for v in range(8)]
    raw=[None]*4096;mask=[]
    for q in range(4096):
        u,t,y=q>>10,(q>>8)&3,q&255
        moved=crt.compact(u,t,y,lambda yy:(table[yy&31],),positions=(target,),ybits=8)
        dest=(moved[0]<<10)|(moved[1]<<8)|moved[2];raw[dest]=('R',q)
        mask.append('0' if crt.good(u,t,y,bits=2,positions=(target,),guard=6) else '1')
    counter=Facade(b,['<',*('0'*12),'>']);data=Facade(b,['<',*raw,'>']);mt=Facade(b,['<',*mask,'>'])
    good=Facade(b,['<']);bad=Facade(b,['<']);scratch=Facade(b,['<'])
    rom=b.BitTape(packet(['L',*map(str,table),'R']));private={r:b.BitTape() for r in mod['source'].OWNED_WIDTHS}
    source,_=mod['source'].assemble(mod['query'],target);program,starts,regs=b.compile_program(source,lifecycle=True)
    calls=[];saved=bridge.evaluate_key;meter={'calls':0,'interface_actions':0};capture={}
    def invoke(actual_counter,actual_bad,unused,meter):
        need(actual_counter is counter and actual_bad is bad,'original caller objects')
        address=int(''.join(decode(physical_word(counter.raw,i)) for i in range(1,13)),2)
        if len(calls)==2:
            capture.update(next_address=address,head=bad.raw.head);raise Captured()
        start=bad.raw.head;prefix=dict(bad.raw.cells);counter_before=dict(counter.raw.cells);rom_before=dict(rom.cells)
        tapes=dict(private,counter=counter.raw,stream=bad.raw,rom=rom)
        machine=b.Machine(program,len(regs),tapes);machine.registers[:]=[1]*len(regs);machine.run()
        expected=mod['oracle'].ReverseWordKey(target,table).key_of(format(address,'012b'))
        result=''.join(decode(physical_word(bad.raw,start//13+j)) for j in range(12))
        need(result==expected and machine.status=='accept' and not any(machine.registers),'actual caller key/control return')
        need(all(bad.raw.cells.get(i,0)==value for i,value in prefix.items()) and all(bad.raw.cells.get(i,0)==prefix.get(i,0) for i in range(start)),'physical opaque prefix')
        need(counter.raw.cells==counter_before and counter.raw.head==0 and rom.cells==rom_before and rom.head==0,'borrowed physical restore')
        need(all(not t.cells and t.head==0 for t in private.values()) and bad.raw.head==start+156,'physical owned return/append')
        calls.append(dict(address=address,key=result,payload=decode(physical_word(bad.raw,start//13-1))[1],binary_actions=sum(machine.census.values())))
        meter['calls']+=1
    bridge.evaluate_key=invoke
    try:
        bridge.split(mt,data,counter,good,bad,scratch,None,mod['native'].increment_and_return,meter,frozenset())
    except Captured:pass
    finally:bridge.evaluate_key=saved
    holes=[i for i,v in enumerate(mask) if v=='1']
    need([x['address'] for x in calls]==holes[:2] and capture['next_address']==holes[2],'actual mask calls and caller continuation')
    need(bad.raw.head==13*(1+2*13+1),'caller next payload head after two complete returns')
    # A projection of the two completed pairs is given to the original radix
    # consumer. Closing the captured prefix is verifier setup, not a full layer.
    first_next_record=1+2*13
    bad.raw.head=13*first_next_record;bad.write('>');bad.raw.head=0
    b0=Facade(b,['<']);b1=Facade(b,['<']);bridge.one_pass(bad,b0,b1,frozenset())
    expected_order=sorted(calls,key=lambda r:r['key'][-1])
    for i,row in enumerate(expected_order):
        cell=1+13*i;need(decode(physical_word(bad.raw,cell))==('R',row['payload']),'actual radix consumer payload')
        rotated=''.join(decode(physical_word(bad.raw,cell+j)) for j in range(1,13))
        need(rotated==row['key'][-1]+row['key'][:-1],'actual radix consumer key')
    need(all(x.raw.head==0 for x in (bad,b0,b1)),'consumer heads returned')
    return dict(source_target=target,calls=calls,continued_to_address=capture['next_address'],consumer='original one_pass on two completed captured pairs',full_layer_replayed=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args();mod=modules();b=mod['binary']
    primitive=primitive_checks(b)
    programs=[]
    for target in (0,1,2):
        source,_=mod['source'].assemble(mod['query'],target);micro,starts,regs=b.compile_program(source,lifecycle=True)
        lengths=[starts[i+1]-starts[i] for i,inst in enumerate(source) if inst[0]!='halt'];need(max(lengths)==43,'proved core per-block maximum')
        programs.append(dict(target=target,source_instructions=len(source),binary_instructions=len(micro),bit_registers=len(regs),max_core_block=43,lifecycle_actions=2*len(regs)))
    parity=[(x>>1).bit_count()&1 for x in range(32)]
    rows=[key_run(mod,0,parity,892,True),key_run(mod,0,parity,4095),key_run(mod,1,[0]*32,1023),key_run(mod,2,[0]*32,4095)]
    controls=[]
    for fault in ('short_move','dirty_head','keep_control'):
        try:key_run(mod,0,parity,892,fault=fault)
        except (ValueError,KeyError,IndexError):controls.append(fault)
        else:raise ValueError('undetected physical mutant '+fault)
    for fault in ('drop_tag',):
        program,_,regs=b.compile_program([('eq_reg','a','b','z'),('halt','accept')],fault)
        m=b.Machine(program,len(regs),{})
        for name,value in [('a',True),('b','L')]:
            for j,bit in enumerate(encode_value(value)):
                if (name,j) in regs:m.registers[regs[name,j]]=bit
        m.run();need(observe_register(m,regs,'z')!=encode_value(False),'tag mutant must differ');controls.append(fault)
    previous=b.CODES['R'];b.CODES['R']=b.CODES['L']
    try:
        try:primitive_checks(b)
        except ValueError:controls.append('marker_collision')
        else:raise ValueError('marker collision not detected')
    finally:b.CODES['R']=previous
    rejected=rejection_checks(mod)
    result=dict(status='PASS_LITERAL_BINARY_KEY_PORT',primitive=primitive,programs=programs,keys=rows,caller=caller_port(mod),behavior_controls=controls,rejected_packet_actions=rejected,
                proved_binary_actions_per_key=43*3_287_110+984,binary_sha256=hashlib.sha256((P/'binary.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'frozen result receipt')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
