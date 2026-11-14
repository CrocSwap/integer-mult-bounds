"""Exact algebra, parser-boundary and complete literal HOME replay."""
from pathlib import Path
import atexit
from hashlib import sha256
import json
import random
import shutil
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='affine-verify-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True
sys.pycache_prefix=str(Path(_cache.name)/'required-absent')
import adapter as A
import affine as C
from machine import Program,initial,fields,check_retired


def need(ok,message):
    if not ok:raise ValueError(message)


def gamma(n):
    if n<1:raise ValueError('positive Gamma value')
    bits=bin(n)[2:]
    return '0'*(len(bits)-1)+bits


def header(shape):
    return ''.join(gamma(n) for n in shape)


def packed_mask(offset,f):
    return sum(((1<<f)-1)<<((8-slot)*f) for slot in range(9) if (offset>>slot)&1)


def xor_image(data,shape,offset):
    """Natural full-address XOR oracle, no slot swaps or CNOT simulation."""
    f,c,p,s,w,_=shape
    count=1<<(9*f);record=2*c*s*w;mask=packed_mask(offset,f)
    need(len(data)==p*count*record,'oracle full tensor length')
    return ''.join(data[(outer*count+(address^mask))*record:
                        (outer*count+(address^mask)+1)*record]
                   for outer in range(p) for address in range(count))


def word_image(x,word):
    for target,control in word:
        x^=((x>>control)&1)<<target
    return x


def algebra():
    maximum=0
    for offset in range(512):
        word=C.conjugator(offset);maximum=max(maximum,len(word))
        need(all(0<=a<9 and 0<=b<9 and a!=b for a,b in word),'fixed CNOT grammar')
        if not offset:
            need(not word,'zero offset word');continue
        need(word_image(1,word)==offset,'G e0 = fixed output offset')
        inverse=tuple(reversed(word))
        for x in range(512):
            need(word_image(word_image(x,word),inverse)==x,'fixed G inverse')
            need(word_image(word_image(x,inverse)^1,word)==x^offset,'conjugator chronology')
    need(maximum==10,'sharp fixed word-length envelope')
    return {'masks':512,'nonzero_mask_address_pairs':511*512,'max_CNOTs_per_word':maximum}


def parser_probes():
    from controller_reference import Tape,Machine
    class HeaderTape(Tape):
        def __post_init__(self):
            super().__post_init__();self.reads=[];self.writes=[]
        def read(self):
            self.reads.append(self.head);return super().read()
        def write(self,symbol):
            self.writes.append((self.head,symbol));super().write(symbol)
    code,_=C.T.compile_translation();result=[]
    shape0=(1,2,2,2,1)
    volume=2*shape0[1]*shape0[2]*shape0[3]*shape0[4]*(1<<(9*shape0[0]))
    rng=random.Random(742814)
    data=''.join(str(rng.randrange(2)) for _ in range(volume))
    for cutoff in (1,2,1<<63,1<<512,1<<4096):
        shape=shape0+(cutoff,);text=header(shape);prefix=header(shape0)
        origins=[7*t-139 for t in range(25)]
        tapes=[Tape({o-5:'0',o+1000000:'1'},o) for o in origins]
        h=HeaderTape(tapes[0].cells.copy(),origins[0]);tapes[0]=h
        h.cells.update({origins[0]+i:b for i,b in enumerate(text)})
        tapes[1].cells.update({origins[1]+i:b for i,b in enumerate(data)})
        before=[t.cells.copy() for t in tapes]
        cpu=Machine(code,tapes).run(5000000)
        need(h.cells==before[0] and not h.writes,'five-field consumer changed Gamma6')
        need({x-origins[0] for x in h.reads}==set(range(len(prefix))),
             'five-field consumer read trailing cutoff')
        need(h.high==origins[0]+len(prefix),'header moves crossed prefix endpoint')
        expected=xor_image(data,shape,1)
        expected_cells=before[1].copy()
        expected_cells.update({origins[1]+i:b for i,b in enumerate(expected)})
        need(tapes[1].cells==expected_cells,'retained first-slot raw bit translation')
        need([t.head for t in tapes]==origins,'parser probe head restoration')
        need(all(t.cells==old for t,old in zip(tapes[2:],before[2:])),'parser probe private retirement')
        result.append({'cutoff_bits':cutoff.bit_length(),'E5':len(prefix),'E6':len(text),
                       'steps':cpu.steps,'header_read_max':max(h.reads)-origins[0],
                       'header_head_max':h.high-origins[0]})
    need(len({r['steps'] for r in result})==1,'opaque cutoff changed first-slot runtime')
    return result


def table_checks():
    result=[]
    masks=[0]+[1<<i for i in range(9)]+[3,17,264,510,511]
    for offset in masks:
        code,alphabet,entries=C.compile_translation(offset)
        need(alphabet==('_','0','1','|'),'fixed alphabet')
        need(not any(op=='write' and args[0]==C.DATA for op,*args in code[:entries['commit']]),
             'public owner write before final commit')
        for op,*args in code:
            if op in ('read','write','move'):need(0<=args[0]<C.TAPES,'fixed port bound')
            if op=='read':need(all(0<=p<len(code) for p in args[1].values()),'fixed branch bounds')
            if op=='goto':need(0<=args[0]<len(code),'fixed jump bounds')
            if op=='move':need(args[1] in (-1,1),'unit local move')
        result.append({'offset':offset,'locations':len(code),'commit':entries['commit'],
                       'CNOT_word_length':len(C.conjugator(offset)),
                       'sha256':sha256(repr(code).encode()).hexdigest()})
    return result


def run_packet(offset,shape,data,seed):
    graph,stages=A.compile_home(offset);program=Program(graph)
    bits=header(shape)+data;expected=header(shape)+xor_image(data,shape,offset)
    parked=''.join(str(random.Random(seed+i).randrange(2)) for i in range(len(bits)))
    state=initial((parked,bits),A.TAPES,old_history=3*len(bits))
    program.run(state,stop=stages['core_return'])
    need(fields(state)==(parked,bits) and state.writes[0]==0,'early original HOME write')
    core_steps=state.steps
    program.run(state,start=stages['core_return'],stop=stages['primitive_return'])
    need(fields(state)==(parked,bits) and state.writes[0]==0,'early scatter')
    program.run(state,start=stages['primitive_return'])
    need(fields(state)==(parked,expected),'complete same-owner address XOR output')
    check_retired(state)
    need(state.writes[0]==len(bits),'sole final full HOME scatter')
    increment=sum((hi-lo)-(ehi-elo) for lo,hi,elo,ehi in
                  zip(state.lows,state.highs,state.entry_lows,state.entry_highs))
    need(increment<=320*(len(bits)+1),'historical backing envelope')
    f=shape[0]
    need(state.steps<=(1<<20)*(f*len(data)+len(header(shape))+1)+128*(len(bits)+1),
         'complete direct cost envelope')
    record={'offset':offset,'shape':shape,'F':len(bits),'E':len(header(shape)),
            'V':len(data),'steps':state.steps,'core_return_steps':core_steps,
            'HOME_writes':state.writes[0],'visited_increment':increment,
            'output_sha256':sha256(expected.encode()).hexdigest()}
    return record,state,program,parked,bits


def source_corruption():
    with tempfile.TemporaryDirectory(prefix='affine-source-control-') as tmp:
        dst=Path(tmp)
        for name in ('affine.py','SOURCES.json'):shutil.copy2(HERE/name,dst/name)
        for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
            q=dst/pin['local'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/pin['local'],q)
        q=dst/'reference/translation/translate.py';q.write_bytes(q.read_bytes()+b'\n# altered retained byte\n')
        launch=('import sys,tempfile;from pathlib import Path;'
                'd=tempfile.TemporaryDirectory();sys.dont_write_bytecode=True;'
                'sys.pycache_prefix=str(Path(d.name)/"absent");'
                'sys.path.insert(0,'+repr(str(dst))+');import affine')
        r=subprocess.run([sys.executable,'-I','-B','-c',launch],capture_output=True,text=True)
        need(r.returncode!=0 and 'frozen source drift' in r.stderr,'actual retained corruption accepted')


def run():
    exact=algebra();probes=parser_probes();tables=table_checks()
    shape=(1,1,1,1,10,1)
    data=''.join(format(i,'010b')+format(1023-i,'010b') for i in range(512))
    full,state,program,parked,bits=run_packet(511,shape,data,7428511)
    # Same objects/origins, smaller new supplied input; prior maxima remain.
    rng=random.Random(7428)
    small_shape=(1,1,1,1,2,1<<257);small_data=''.join(str(rng.randrange(2)) for _ in range(2048))
    small_bits=header(small_shape)+small_data;small_parked='0'*len(small_bits)
    old_highs=state.highs.copy();old_steps=state.steps
    text='^'+small_parked+'|'+small_bits+'|$';symbols={s:i for i,s in enumerate('_01^|$')}
    o=state.origins[0];state.tapes[0][o+1:-3]=bytes(len(state.tapes[0])-o-4)
    state.tapes[0][o:o+len(text)]=bytes(symbols[s] for s in text)
    program.run(state)
    need(fields(state)==(small_parked,header(small_shape)+xor_image(small_data,small_shape,511)),
         'same-owner long-short reuse')
    check_retired(state);need(all(x>=y for x,y in zip(state.highs,old_highs)),'old backing refunded')
    reuse={'shape':small_shape,'F':len(small_bits),'steps':state.steps-old_steps,
           'retained_guide_high':state.highs[-1]}
    mixed_shape=(1,2,2,3,3,1<<63)
    mixed_data=''.join(str(rng.randrange(2)) for _ in range(2*2*2*3*3*512))
    mixed,*_=run_packet(264,mixed_shape,mixed_data,7428264)
    identity,*_=run_packet(0,(1,1,1,1,2,1),small_data,7428000)
    controls=[]
    for mutation,expected_offset in (('omit_last_conjugator_gate',255),('wrong_conjugation_order',1)):
        graph,_=A.compile_home(511,mutation=mutation)
        s=initial((parked,bits),A.TAPES);Program(graph).run(s)
        expected=header(shape)+xor_image(data,shape,expected_offset)
        need(fields(s)==(parked,expected) and expected!=header(shape)+xor_image(data,shape,511),
             'actual conjugation omission/order mutant')
        check_retired(s);controls.append({'mutation':mutation,'actual_offset':expected_offset,'steps':s.steps})
    source_corruption()
    return {'marker':'PASS_LITERAL_GENERIC_AFFINE_HOME','algebra':exact,'parser_probes':probes,
            'core_tapes':C.TAPES,'tapes':A.TAPES,'tables':tables,'full_offset':full,
            'mixed_far_offset':mixed,'identity':identity,'same_owner_reuse':reuse,
            'executed_mutants':controls,'controls':['omitted conjugator target','wrong conjugation order',
              'actual retained-source corruption','no early original-owner write','cutoff parser extent'],
            'scope':'fixed-offset address permutation only; no source-MOVE/caller/monomial dispatcher/nonleaf admission'}


if __name__=='__main__':
    start=time.monotonic();result=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    elif (HERE/'RESULT.json').exists():
        need(json.loads((HERE/'RESULT.json').read_text())==json.loads(json.dumps(result)),'receipt drift')
    print(json.dumps(result,sort_keys=True));print('elapsed_seconds',round(time.monotonic()-start,3))
