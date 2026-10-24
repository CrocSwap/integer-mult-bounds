"""Independent endpoint, all four source calls, identity and cleanup checks."""
import argparse
import hashlib
import json
import time
import types
from pathlib import Path
import adapter as a
P=Path(__file__).resolve().parent
ROOT=P.parents[1]

def need(ok,label):
    if not ok:raise ValueError(label)

def authenticate():
    hashes={}
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        raw=(ROOT/row['path']).read_bytes();h=hashlib.sha256(raw).hexdigest()
        need(h==row['sha256'],'source SHA '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob')
        hashes[row['path']]=h
    return hashes

def borrowed(bits):
    d={x:['<',*('1'*v),'>','_'] for x,v in zip(('G','H','K','Y','J','B'),(2,2,6,8,2,0))}
    d['rom']=['L',*map(str,bits),'R'];return d

def numeric(bits,head=1):return types.SimpleNamespace(cells=bytearray([2,*bits,4]),head=head)
def blank():return types.SimpleNamespace(cells=bytearray([4]),head=0)
def binary(values):return bytes(int(b) for v in values for b in f'{v:012b}')

def inline_check(code,stages,service):
    need(len(stages['calls'])==4,'four actual service calls')
    def replace(x,col):
        if isinstance(x,tuple):
            if len(x)==2 and x[0]=='c' and x[1]=='data':return ('c',col)
            return tuple(replace(v,col) for v in x)
        return x
    for i,call in enumerate(stages['calls']):
        need(call['column']=='column'+str(i),'column dispatch')
        start,end=call['start'],call['end'];need(end-start==len(service),'whole source length')
        for offset,(op,*args) in enumerate(service):
            args=[replace(v,call['column']) for v in args]
            if op=='jump':args[0]+=start
            elif op=='branch':args[1]+=start;args[2]+=start
            elif op=='halt' and args==['accept']:op='jump';args=[end]
            need(code[start+offset]==(op,*args),'unchanged actual service instruction')

def cleanup(tapes,heads,raw,out,before,roles,result):
    need(all(v==4 for v in raw.cells) and raw.head==1,'owned raw consumed and returned')
    need(out.head==1,'numeric output head')
    need(all(heads[r]==0 for r in tapes if r not in ('raw','output')),'all resident heads returned')
    for r in (*roles,*('key_'+x for x in ('h','s','offset','target','out','count','col','row','limit','u','t','y')),*('column'+str(i) for i in range(4))):
        need(all(x=='_' for x in tapes[r]),'private and retained blank '+r)
    need(all(tapes[r]==v for r,v in before.items()),'borrowed headers and ROM')
    need(all(v is None for v in result['registers'].values()),'finite register reset')

def controls(code,roles,stages):
    short,_,_=a.assemble(ROOT,False);run=a.executor(ROOT);values=(0,4095,2048,1,4094,2,2047,1025);bits=binary(values)
    def roundtrip(program=short,payload=bits):
        raw,out=numeric(payload),blank();inputs=borrowed([0]*32);before={r:list(v) for r,v in inputs.items()}
        tapes,heads=a.prepare(roles,raw,out,inputs);rawid=id(raw.cells);outid=id(out.cells)
        result=run(program,tapes,max_steps=100000,initial_heads=heads)
        need(result['status']=='accept' and bytes(out.cells)==bytes([2])+payload+bytes([4]),'two adjacent full fibers')
        need(id(raw.cells)==rawid and id(out.cells)==outid,'backing identity')
        cleanup(tapes,heads,raw,out,before,roles,result)
        return {'steps':result['steps'],'cells':result['cell_actions']}
    light=roundtrip();rejected=[]
    def reject(label,fn):
        try:fn()
        except ValueError:rejected.append(label)
        else:raise ValueError('mutation escaped '+label)
    broken=list(short);pc=next(i for i,row in enumerate(broken) if row==('copy',a.C('column1'),'column'));broken[pc]=('copy',a.C('column2'),'column')
    reject('wrong_back_column',lambda:roundtrip(broken))
    broken=list(short);pc=next(i for i,row in enumerate(broken) if row[0]=='in');row=list(broken[pc]);row[2]=a.C(frozenset());broken[pc]=tuple(row)
    reject('missing_high_payload_bit',lambda:roundtrip(broken))
    broken=list(short);pc=max(i for i,row in enumerate(broken) if row==('write',a.C('column0'),a.C('_')));broken[pc]=('copy',a.C(None),'test')
    reject('retained_column_marker',lambda:roundtrip(broken))
    reject('incomplete_four_column_fiber',lambda:roundtrip(payload=bits[:-1]))
    m=a.source_machine(ROOT);service=m.assemble(ROOT)[0];inline_check(code,stages,service)
    broken=list(code);pc=stages['calls'][2]['start'];broken[pc]=('jump',stages['calls'][2]['end'])
    reject('skipped_third_actual_repair',lambda:inline_check(broken,stages,service))
    inputs=borrowed([0]*32);inputs['H']=inputs['G'];reject('aliased_borrowed_metadata',lambda:a.prepare(roles,numeric(bits),blank(),inputs))
    raw=numeric(bits);out=blank();out.cells=raw.cells;reject('aliased_numeric_backing',lambda:a.prepare(roles,raw,out,borrowed([0]*32)))
    raw=numeric(bits,97);reject('raw_end_head',lambda:a.prepare(roles,raw,blank(),borrowed([0]*32)))
    for v,want in [(0,True),(4095,True),(4096,False),('0'*48,False)]:
        result=m.execute((('record',a.C(('R',v)),'answer'),('halt','accept')),{'probe':['_']})
        need(result['registers']['answer'] is want,'unchanged real parser domain')
    cycle=list(code);cycle[0]=('jump',0);reject('control_only_cycle',lambda:m.control_bound(cycle))
    return {'light_roundtrip':light,'rejected':rejected}

def fixture():
    crt=a.load(ROOT/'research/unconditional-batched-crt/check_batched_crt.py')
    rows=[crt.benes(crt.rotation(8,5,v))[2][1] for v in (0,2,4,0)];rom=tuple(v for row in rows for v in row)
    raw=[None]*16384;ideal=[None]*16384;holes=[]
    for address in range(4096):
        u,t,y=address>>10,(address>>8)&3,address&255
        uu,tt,yy=crt.compact(u,t,y,lambda z:(rom[z&31],),positions=(2,),ybits=8)
        dest=(uu<<10)|(tt<<8)|yy;target=(u<<10)|(t<<8)|(y^(rom[y&31]<<2))
        for back in range(4):
            x=4*address+back;v=(x^((x>>12)*1237))&4095
            raw[4*dest+back]=v;ideal[4*target+back]=v
        if not crt.good(u,t,y,bits=2,positions=(2,),guard=6):holes.append(address)
    need(all(v is not None for v in raw+ideal),'permutation fixture')
    return binary(raw),binary(ideal),rom,holes

def expected(code,roles,stages,checks,sources):
    raw,ideal,rom,holes=fixture();old=json.loads((ROOT/'research/crt-complete-repair-control/RESULT.json').read_text())['actual'];M=4096;B=48*M;H=sum(raw)
    return {'status':'PASS_FOUR_COLUMN_ACTUAL_REPAIR','program_sha256':a.digest(code),'program_instructions':len(code),'control_factor':a.source_machine(ROOT).control_bound(code),
        'static_storage':a.static_stats(ROOT,code),'service_roles':list(roles),'source_hashes':sources,'controls':checks,'raw_sha256':hashlib.sha256(raw).hexdigest(),'ideal_sha256':hashlib.sha256(ideal).hexdigest(),
        'rom_bits':''.join(map(str,rom)),'fibers':M,'bits':B,'ones':H,'actual_service_calls':4,'key_calls_per_column':len(holes),
        'adapter_steps':20*B+105*M+3*H+143,'adapter_cells':7*B+134*M+69,
        'total_steps':4*old['steps']+20*B+105*M+3*H+143,'total_cells':4*old['cells']+7*B+134*M+69,
        'code_hashes':{f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ('adapter.py','verify.py')}}

def full(code,roles,stages,want):
    expected_bits,ideal,rom,holes=fixture();bits=(P/'RAW.bin').read_bytes();need(bits==expected_bits,'actual producer dump equals source endpoint');raw,out=numeric(bits),blank();inputs=borrowed(rom);before={r:list(v) for r,v in inputs.items()}
    tapes,heads=a.prepare(roles,raw,out,inputs);identities={r:id(v.tape.cells if isinstance(v,a.NumericPort) else v) for r,v in tapes.items()}
    events={};seen=[[] for _ in range(4)];call_steps=[];active={};m=a.source_machine(ROOT);service=m.assemble(ROOT)[0];service_regs=m.registers(service)
    key=a.load(ROOT/'research/crt-mask-repair-bridge/key_subroutine.py').ReverseWordKey(2,rom)
    def add(pc,fn):events.setdefault(pc,[]).append(fn)
    for i,call in enumerate(stages['calls']):
        def entry(pc,t,h,r,s,c,i=i):
            need(all(h[x]==0 for x in t if x not in ('raw','output')),'same-bank service entry heads')
            active[i]=(s,c,{x:list(t[x]) for x in t if x.startswith('column') and x!='column'+str(i)})
            need(all(all(v=='_' for v in t[x]) for x in (*roles,*(r for r in t if r.startswith('key_')))),'same-bank service entry blank')
        def end(pc,t,h,r,s,c,i=i):
            start_s,start_c,other=active[i];call_steps.append([s-start_s,c-start_c])
            need(all(t[x]==v for x,v in other.items()),'other back columns preserved')
            need(all(r[x] is None for x in service_regs),'service control reset before next call')
            need(all(h[x]==0 for x in t if x not in ('raw','output')),'service return heads')
            need(all(all(v=='_' for v in t[x]) for x in (*roles,*(r for r in t if r.startswith('key_')))),'service private cleanup')
        add(call['start'],entry);add(call['end'],end)
        ks,ke=call['source_key_sites'][0];key_active={}
        def key_entry(pc,t,h,r,s,c,i=i,ka=key_active):
            q=int(''.join(t['work9'][1:13]),2);seen[i].append(q);ka.update(q=q,start=h['work1'])
        def key_end(pc,t,h,r,s,c,ka=key_active):
            need(''.join(t['work1'][ka['start']:h['work1']])==key.key_of(f"{ka['q']:012b}"),'actual key at physical append cursor')
        add(call['start']+ks,key_entry);add(call['start']+ke,key_end)
    observers={pc:(lambda *args,fs=fs:[f(*args) for f in fs]) for pc,fs in events.items()}
    start=time.monotonic();result=a.executor(ROOT)(code,tapes,max_steps=800000000,observe=observers,initial_heads=heads);elapsed=time.monotonic()-start
    need(result['status']=='accept','full accepting halt');need(bytes(out.cells)==bytes([2])+ideal+bytes([4]),'entire196608-bit ideal endpoint')
    need(result['steps']==want['total_steps'] and result['cell_actions']==want['total_cells'],'exact whole instruction and cell invoice')
    old=json.loads((ROOT/'research/crt-complete-repair-control/RESULT.json').read_text())['actual']
    need(call_steps==[[old['steps'],old['cells']]]*4,'four complete actual calls')
    need(seen==[holes]*4,'all2944 bad addresses per column and no good calls')
    need(identities=={r:id(v.tape.cells if isinstance(v,a.NumericPort) else v) for r,v in tapes.items()},'all backing identities retained')
    cleanup(tapes,heads,raw,out,before,roles,result)
    for r in tapes:
        if r not in ('raw','output','G','H','K','Y','J','B','rom'):need(len(tapes[r])<=4096*13+64,'retained backing cap '+r)
    print(json.dumps({'elapsed_seconds':elapsed,'raw_sha256':want['raw_sha256'],'steps':result['steps'],'cells':result['cell_actions'],'retained_cells':{r:len(v) for r,v in tapes.items()}},sort_keys=True),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--light',action='store_true');ap.add_argument('--prepare-receipt',action='store_true');args=ap.parse_args()
    sources=authenticate();code,roles,stages=a.assemble(ROOT);checks=controls(code,roles,stages);want=expected(code,roles,stages,checks,sources)
    if args.prepare_receipt:(P/'RESULT.json').write_text(json.dumps(want,indent=2)+'\n');print('PREPARED_EXPECTED_RECEIPT_NOT_FULL_REPLAY');return
    frozen=json.loads((P/'RESULT.json').read_text());need(json.dumps(frozen,sort_keys=True,separators=(',',':'))==json.dumps(want,sort_keys=True,separators=(',',':')),'typed frozen receipt')
    if args.light:print('PASS_FOUR_COLUMN_LIGHT',json.dumps(checks));return
    full(code,roles,stages,want);print(want['status'])

if __name__=='__main__':main()
