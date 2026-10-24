"""Exact finite corroboration, full frames and fail-closed frozen inputs."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, message):
    if not ok: raise ValueError(message)


def pins():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] != 'input': continue
        need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin: '+row['path'])
    row = manifest['external_public_input']
    need(hashlib.sha256((HERE / row['local_path']).read_bytes()).hexdigest() == row['sha256'], 'PR5148 exact proof')


def load():
    spec=importlib.util.spec_from_file_location('reversal_science', HERE/'machine.py')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fixture(m,n,width,shift=0):
    rows=[format((i*37+11)%(1<<width),'0%db'%width) for i in range(n)]
    origins=[shift+3*t for t in range(15)]
    ts=[m.Tape.fixture(origin=o) for o in origins]
    ts[m.SOURCE]=m.Tape.fixture(''.join(rows),origins[m.SOURCE])
    ts[m.BD]=m.Tape.fixture(bin(width)[2:][::-1],origins[m.BD])
    # These unused ports contain arbitrary payload, not necessarily blank.
    for t in (1,2,3):ts[t]=m.Tape.fixture('101001',origins[t])
    return rows,origins,ts


def payload(t,origin):
    chars=[]
    i=origin+1
    while t.cells.get(i,'_')!='_':
        chars.append(t.cells[i]);i+=1
    return ''.join(chars)


def check(m,n,w,shift=0,trace=False):
    rows,origins,ts=fixture(m,n,w,shift)
    saved=[(dict(t.cells),t.head) for t in ts]
    machine=m.Machine(ts)
    stages=[]
    if trace:
        while m.PROGRAM[machine.pc][0]!='done':
            if machine.pc==m.STAGE_PC and ts[m.DATA].head==origins[m.DATA]+1:
                raw=payload(ts[m.DATA],origins[m.DATA])
                stages.append([raw[i:i+w] for i in range(0,len(raw),w)])
            try:machine.run(machine.steps+1)
            except ValueError as e:need(str(e)=='execution budget','trace local error')
        machine.run(machine.steps+1)
    else:machine.run()
    need(payload(ts[m.OUTPUT],origins[m.OUTPUT])==''.join(reversed(rows)), 'record reversal endpoint')
    for i,t in enumerate(ts):
        need(t.head==origins[i]+1,'returned head')
        need(t.cells.get(origins[i])==m.LEFT,'left marker preserved')
        need(t.low>=origins[i], 'no visit before marker')
        if i in (m.SOURCE,m.BD,1,2,3):need((t.cells,t.head)==saved[i], 'borrowed/unused full frame')
        elif i!=m.OUTPUT:need(all(v==m.BLANK for p,v in t.cells.items() if p!=origins[i]),'work erased')
    k=0;s=1
    while s<n:k+=1;s*=3
    bound=256*((n+1)*(w+1)*(k+1)+w*(w.bit_length()+1)+1)
    need(machine.steps<=bound,'written action tariff')
    backing=sum(t.high-t.low+1 for t in ts)
    initial=sum(max(t[0])-min(t[0])+1 for t in saved)
    need(backing<=initial+6*n*w+7*n+w+2*w.bit_length()+60,'retained high-water tariff')
    return {'n':n,'B':w,'origin':shift,'steps':machine.steps,'backing':backing,'stage_records':stages}


def rejected(call):
    try:call()
    except (ValueError, KeyError):return
    raise ValueError('expected rejection')


def science():
    m=load()
    cases=[check(m,n,w,shift) for shift in (0,19,-23) for n in range(41) for w in (1,3,7,17)]
    stress=[check(m,n,w,31) for n,w in ((80,2),(81,2),(82,2),(242,1),(243,1),(244,1),(7,129),(3,1024))]
    seven=check(m,7,3,trace=True)
    rows=fixture(m,7,3)[0]
    need(seven['stage_records']==[[rows[i] for i in p] for p in ([2,1,0,5,4,3,6],[6,5,4,3,2,1,0])], 'source seven-record stages')
    controls=[]
    for text in ('','0','10','1x'):
        _,origins,ts=fixture(m,2,3)
        ts[m.BD]=m.Tape.fixture(text,origins[m.BD])
        rejected(lambda:m.Machine(ts).run(20000));controls.append('bad-width:'+text)
    _,o,ts=fixture(m,2,3);ts[0]=m.Tape.fixture('10101',o[0])
    rejected(lambda:m.Machine(ts).run(20000));controls.append('partial-row')
    _,o,ts=fixture(m,2,3);ts[2]=ts[1]
    rejected(lambda:m.Machine(ts));controls.append('port-alias')
    original=m.PROGRAM
    try:
        for label,tape,symbol,replacement in [('output-bit',m.OUTPUT,'0','1'),('tripled-guide',m.NEXT,'1','0')]:
            p=list(original)
            index=next(i for i,ins in enumerate(p) if ins==('write',tape,symbol))
            p[index]=('write',tape,replacement);m.PROGRAM=tuple(p)
            rejected(lambda:check(m,7,3));controls.append('actual-mutant:'+label)
    finally:m.PROGRAM=original
    data=json.dumps(cases,sort_keys=True,separators=(',',':')).encode()
    return {'schema_version':1,'claim':'fixed-three-lane physical valid-input reversal','cases':len(cases),
            'cases_sha256':hashlib.sha256(data).hexdigest(),'carry_and_stage_boundaries':stress,'program_instructions':len(m.PROGRAM),
            'max_steps':max(x['steps'] for x in cases),'seven':seven,'controls':controls,
            'unrun':['production bit-free supplier composition','heterogeneous runtime lane counts']}


def main():
    pins()
    writing=sys.argv[1:]==['--write-result']
    need(writing or not sys.argv[1:],'arguments')
    frozen=None if writing else json.loads((HERE/'RESULT.json').read_text())
    result=science()
    canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
    if writing:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(canonical(frozen)==canonical(result),'typed complete frozen receipt')
    print('PASS',result['cases'],'cases',len(result['controls']),'controls')

if __name__=='__main__':main()
