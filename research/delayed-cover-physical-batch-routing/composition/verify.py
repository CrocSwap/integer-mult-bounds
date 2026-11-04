"""Read-only exact finite replay of the physical composition fixture."""
from pathlib import Path
from hashlib import sha256, sha1
from itertools import product
import argparse
import ast
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def authenticate_sources():
    """Authenticate bundled source bytes before any scientific-source import."""
    for item in json.loads((HERE/'SOURCES.json').read_text())['sources']:
        b=(HERE/item['copy']).read_bytes()
        if len(b)!=item['bytes']or sha256(b).hexdigest()!=item['sha256']:
            raise ValueError('pinned exact predecessor')
        if 'git_blob'in item and sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=item['git_blob']:
            raise ValueError('original Git blob')


authenticate_sources()
spec=importlib.util.spec_from_file_location('composition',HERE/'composition.py')
C=importlib.util.module_from_spec(spec);sys.modules['composition']=C;spec.loader.exec_module(C)
s, m = C.s, C.m


class ChargedTape(s.Tape):
    """Hardware-only instrumentation; runtime programs cannot query this data."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited = set()
        self.written = set()
        self.guard = None
        self.child_floor = None

    def read(self):
        s.need(self.child_floor is None or self.head>=self.child_floor,
               'child read crossed its physical segment delimiter')
        self.visited.add(self.head)
        return super().read()

    def write(self, value):
        s.need(self.child_floor is None or self.head>=self.child_floor,
               'child write crossed its physical segment delimiter')
        self.visited.add(self.head)
        self.written.add(self.head)
        if self.guard is not None:
            limit, old = self.guard
            s.need(self.head >= limit or value == old[self.head],
                   'a live parked parent byte was overwritten')
        super().write(value)

    def move(self, direction):
        self.visited.add(self.head)
        super().move(direction)
        s.need(self.child_floor is None or self.head>=self.child_floor,
               'child move crossed its physical segment delimiter')
        self.visited.add(self.head)


def encoded(symbols):
    return [b for v in symbols for b in ((v >> 2)&1, (v >> 1)&1, v&1)]


def load_symbols(tape, symbols, marker=s.LEFT, logical_head=0):
    for b in encoded(symbols):
        s.emit(tape, b)
    C.origin(tape, marker)
    for _ in range(logical_head):
        C.three_moves(tape, 1)


def descriptor(value):
    s.need(type(value) is int and value > 0, 'positive fixture descriptor')
    return [m.LEFT]+[m.ONE if value>>i&1 else m.ZERO for i in range(value.bit_length())]+[m.RIGHT]


def hardware_packet(tape):
    """Test-only complete packet decode; no result enters the program."""
    start=tape.head
    while start >= tape.floor and tape.cells[start-1] != s.LEFT:
        start -= 1
    end=start
    while end < len(tape.cells) and tape.cells[end] != s.BLANK:
        end+=1
    raw=tape.cells[start:end]
    s.need(len(raw)%3==0 and all(v in (0,1)for v in raw),'complete physical codec packet')
    return [4*raw[i]+2*raw[i+1]+raw[i+2]for i in range(0,len(raw),3)]


def expected(bits, low, repeats, block, child_repeats, depth):
    banks=[[bits[(a*low+l)*block+r]for a in range(repeats)for r in range(block)]for l in range(low)]
    if depth:
        for bank in (0,1):
            child=banks[bank]
            banks[bank]=[1-x if (i//block)%low==0 else x for i,x in enumerate(child)]
            s.need(len(child)==child_repeats*low*block,'unequal child fixture shape')
    return [banks[l][a*block+r]for a in range(repeats)for l in range(low)for r in range(block)]


def fixture(low, child_a, block, bits, prefix=0, depth=1, cycles=1):
    """All extents enter through tapes; the test oracle alone sees integers."""
    parent_a=low*child_a
    s.need(len(bits)==parent_a*low*block,'full arbitrary input')
    counts=s.Counts()
    payloads=[ChargedTape([1]*prefix, counts=counts)for _ in range(16)]
    control=ChargedTape([0]*prefix,s.BASE,counts)
    phase=ChargedTape([],s.BASE,counts)
    relays=[ChargedTape([],s.BASE,counts)for _ in range(4)]
    dt=ChargedTape([],s.BASE,counts)
    pipe=C.Pipeline(low,payloads,control,phase,relays,dt)
    p=pipe.p
    load_symbols(payloads[p['source']],[m.LEFT]+[m.ONE if b else m.ZERO for b in bits]+[m.RIGHT],logical_head=1)
    for role,n in ((p['repeats_input'],parent_a),(p['block_input'],block)):
        load_symbols(payloads[role],descriptor(n),logical_head=1)
    load_symbols(relays[1],descriptor(child_a),marker=s.BASE)
    load_symbols(relays[2],descriptor(block),marker=s.BASE)
    for _ in range(depth):s.emit(dt,1)
    C.origin(dt,s.BASE)
    all_tapes=payloads+[control,phase]+relays+[dt]
    identities=tuple(map(id,all_tapes))
    readonly=[payloads[p['source']],payloads[p['repeats_input']],payloads[p['block_input']],relays[1],relays[2],dt]
    saved={id(t):(t.cells.copy(),t.head)for t in readonly}
    for t in all_tapes:t.visited.clear();t.written.clear()
    begin=counts.total
    observations=[]
    live=[]
    original_push,original_pop=s.Stack.push,s.Stack.pop
    def observed_push(stack,present):
        # This observer never supplies a program branch, offset or size.
        snapshots=[]
        for t in stack.payloads:
            start=t.head
            while start>t.floor and t.cells[start-1]!=s.LEFT:start-=1
            end=start
            while end<len(t.cells)and t.cells[end]!=s.BLANK:end+=1
            snapshots.append((t.cells[:end],t.head,end))
        original_push(stack,present)
        for t,(old,_,end)in zip(stack.payloads,snapshots):
            t.guard=(end,old);t.child_floor=end
        live.append(snapshots)
    def observed_pop(stack):
        # Pop is the declared transition which may revisit the parked parent.
        for t in stack.payloads:t.child_floor=None
        result=original_pop(stack)
        snapshots=live.pop()
        for t,(old,head,end)in zip(stack.payloads,snapshots):
            s.need(t.cells[:end]==old and t.head==head,'pop restores every parked parent byte and head')
            t.guard=None
        observations.append({'parent_bytes':sum(x[2]for x in snapshots),'fixed_payloads':16})
        return result
    s.Stack.push,s.Stack.pop=observed_push,observed_pop
    try:
        sizes=[]
        wanted=expected(bits,low,parent_a,block,child_a,depth)
        for _ in range(cycles):
            pipe.run()
            got=hardware_packet(payloads[p['output']])
            s.need(got==[m.LEFT]+[m.ONE if b else m.ZERO for b in wanted]+[m.RIGHT],
                   'complete split-child-return-merge endpoint')
            for t in readonly:
                old,head=saved[id(t)]
                s.need(t.cells[:len(old)]==old and t.head==head,'borrowed source/descriptors preserved')
                # Payload tapes may append a distinct child segment. The live
                # original packet itself remains read-only; standalone grant
                # tapes have no appended child use.
                s.need(not any(pos<len(old)for pos in t.written),
                       'live original source/descriptor bytes are never written')
            for role,t in enumerate(payloads):
                s.need(t.cells[:prefix]==[1]*prefix,'ancestor bytes preserved')
                if role not in (p['source'],p['output'],p['repeats_input'],p['block_input']):
                    s.need(all(v==s.BLANK for v in t.cells[prefix+1:]),'all uncredited payload scratch erased')
                    s.need(t.head==prefix+1,'retired payload head at origin')
            s.need(not live,'no live continuation frame')
            s.need(all(v==s.BLANK for v in control.cells[prefix+1:]),'all control frames erased')
            s.need(all(v==s.BLANK for v in phase.cells[1:]),'resume descriptor erased')
            for t in (relays[0],relays[3]):
                s.need(all(v==s.BLANK for v in t.cells[1:])and t.head==1,'input/output bridge erased and rewound')
            pipe.consume_output()
            sizes.append(sum(len(t.cells)for t in all_tapes))
        s.need(len(set(sizes))==1,'continuous sibling/invocation reuse has no backing growth')
    finally:
        s.Stack.push,s.Stack.pop=original_push,original_pop
    s.need(identities==tuple(map(id,all_tapes)),'fixed physical tape identities')
    actions=counts.total-begin
    return {'L':low,'parent_A':parent_a,'child_A':child_a,'R':block,'volume':len(bits),
            'depth_descriptor':depth,'cycles':cycles,'physical_tapes':len(all_tapes),
            'child_returns':len(observations),'physical_actions':actions,
            'visited_cells':sum(len(t.visited)for t in all_tapes),
            'retained_backing':sizes[-1],
            'parent_preservation_checks':len(observations),'output_sha256':sha256(bytes(wanted)).hexdigest()}


def authenticate():
    authenticate_sources()
    tree=ast.parse((HERE/'composition.py').read_text())
    s.need(not any(isinstance(x,ast.Attribute)and x.attr in {'head','cells','floor','counts','minimum','visited'}for x in ast.walk(tree)),
           'algorithm may not inspect hardware coordinates or counters')


def codec_roundtrip():
    counts=s.Counts();ts=[ChargedTape([1]*13,counts=counts)for _ in range(16)]
    control=ChargedTape([],s.BASE,counts);phase=ChargedTape([],s.BASE,counts)
    view=C.CodedTape(ts[0])
    symbols=[m.LEFT,m.ONE,m.BLANK,m.ZERO,m.UNIT,m.MARK,m.RIGHT]
    for symbol in symbols:view.write(symbol);view.move(1)
    C.coded_input_origin(ts[0])
    old,head=ts[0].cells.copy(),ts[0].head
    s.Stack(ts,control,phase).push((True,)+(False,)*15)
    child=C.CodedTape(ts[0])
    for symbol in [m.LEFT,m.ZERO,m.BLANK,m.ONE,m.RIGHT]:child.write(symbol);child.move(1)
    for t in ts:C.returned.retire(t)
    s.Stack(ts,control,phase).pop()
    s.need(ts[0].cells[:len(old)]==old and ts[0].head==head,'interior logical blank survives real suspension')
    return {'alphabet_symbols':7,'parent_symbols':symbols,'physical_actions':counts.total}


def rejected(fn):
    try:fn()
    except (ValueError,RuntimeError):return True
    raise ValueError('semantic mutation was accepted')


def negative_controls():
    controls={}
    ordinary=C.returned.return_output
    def late_copy(payloads,control,phase,relay,child_slot,parent_slot):
        # Deliberate fault: pop before saving the live child packet.
        for t in payloads:C.returned.retire(t)
        s.Stack(payloads,control,phase).pop()
    C.returned.return_output=late_copy
    try:controls['retire_pop_before_output_protection']=rejected(lambda:fixture(2,1,1,[0,1,1,0]))
    finally:C.returned.return_output=ordinary
    def aliased(payloads,control,phase,relay,child_slot,parent_slot):
        return ordinary(payloads,control,phase,relay,child_slot,0)
    C.returned.return_output=aliased
    try:controls['occupied_parent_output_alias']=rejected(lambda:fixture(2,1,1,[0,1,1,0]))
    finally:C.returned.return_output=ordinary
    leaf=C.complement_bank;C.complement_bank=lambda tape:None
    try:controls['omitted_complete_child_leaf']=rejected(lambda:fixture(3,1,1,[0,1,0,1,1,0,0,0,1]))
    finally:C.complement_bank=leaf
    controls['unsupported_extra_depth']=rejected(lambda:fixture(2,1,1,[0,1,1,0],depth=2))
    write=C.CodedTape.write
    def physical_blank(self,symbol):
        if symbol==m.BLANK:
            for _ in (0,1,2):s.emit(self.tape,s.BLANK)
            C.three_moves(self.tape,-1)
        else:write(self,symbol)
    C.CodedTape.write=physical_blank
    try:controls['logical_blank_used_as_physical_delimiter']=rejected(codec_roundtrip)
    finally:C.CodedTape.write=write
    return controls


def check():
    authenticate()
    codec=codec_roundtrip()
    cases=[]
    for bits in product((0,1),repeat=4):cases.append(fixture(2,1,1,list(bits),prefix=7))
    # Both L values use literal tables; arbitrary length and ancestor bytes are
    # not replaced by a host coordinate permutation in the executed program.
    for low,a,r,prefix in [(2,2,2,0),(2,2,3,19),(3,1,1,0),(3,2,2,37)]:
        n=low*low*a*r
        for bits in [[0]*n,[1]*n,[int(i%3==0)for i in range(n)]]:
            cases.append(fixture(low,a,r,bits,prefix=prefix,cycles=2))
    cases.append(fixture(2,1,1,[1,0,0,1],prefix=11,depth=0))
    return {'schema':'physical-router-stack-composition/1','status':'PASS_PHYSICAL_ROUTER_CODEC_STACK_BOUNDARY',
            'cases':cases,'codec_control':codec,'negative_controls':negative_controls(),
            'total_physical_actions':sum(c['physical_actions']for c in cases),
            'runtime_tapes':23,'grammar':'At most one unequal child edge; two sequential sibling calls; literal router tables; bit-complement leaf.',
            'scope':'Actual read/write/unit-step physical execution and exact finite controls. No all-selected production grammar, Gaussian child, descriptor generator, old-BIT space binding, physical supplier or kappa claim.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=check();path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:s.need(result==json.loads(path.read_text()),'stable exact result')
    print(json.dumps({'status':result['status'],'cases':len(result['cases']),
                      'physical_actions':result['total_physical_actions']},sort_keys=True))
