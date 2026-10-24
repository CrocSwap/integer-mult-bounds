"""Source-bound endpoint, caller and semantic controls; no hidden producer oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]

def need(ok,label):
    if not ok:raise ValueError(label)

def load(name,path,source=None):
    mod=types.ModuleType(name);mod.__file__=str(path)
    exec(compile(path.read_bytes() if source is None else source,str(path),'exec'),mod.__dict__)
    return mod

def authenticate():
    hashes={}
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        raw=(ROOT/row['path']).read_bytes();digest=hashlib.sha256(raw).hexdigest()
        need(digest==row['sha256'],'source SHA256 '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob')
        hashes[row['path']]=digest
    return hashes

def headers(h,s,offsets,selected,w=None):
    w=w or 4*h+8
    def word(x):return ['L',*f'{x:0{w}b}'[::-1],'R']
    return dict(h=word(h),modulus=word(s),selected_layer=word(selected),
                offsets=['L',*[b for v in offsets for b in list(f'{v:0{w}b}'[::-1])+['|']],'R'])

def check_static(code):
    allowed={'read','write','write_reg','move','set','not','copybit','eq','branch','jump','halt'}
    for op,*a in code:
        need(op in allowed,'literal finite-symbol opcode')
        if op=='move':need(type(a[1]) is int and a[1] in (-1,1),'unit move')
        if op in ('set','write'):need(a[1] in ('0','1','L','R','|','_'),'fixed symbol')
        if op=='branch':need(all(type(x)is int and 0<=x<len(code) for x in a[2:]),'static branch')
        if op=='jump':need(type(a[0])is int and 0<=a[0]<len(code),'static jump')

def expected(crt,h,s,offsets):
    nets=[crt.benes(crt.rotation(1<<h,s,a)) for a in offsets]
    return [''.join(str(bit) for net in nets for bit in net[k][1]) for k in range(2*h-1)]

def fixture(m,crt,h,s,offsets,selected,w=None,consume=False):
    incoming=headers(h,s,offsets,selected,w);before={r:list(x) for r,x in incoming.items()}
    out,tapes=m.run_producer(incoming);need(out['status']=='accept','valid producer accepted')
    rows=expected(crt,h,s,offsets)
    need(''.join(tapes['layers'])=='L'+'|'.join(rows)+'|R','canonical complete layers')
    need(''.join(tapes['rom'])=='L'+rows[selected]+'R','selected actual ROM')
    need(all(tapes[r]==before[r] for r in before),'borrowed descriptors preserved')
    need(all(v==0 for v in out['heads'].values()),'all heads returned')
    need(all(all(x=='_' for x in tapes[r]) for r in m.REGS+('arena','spool')),'private backing erased')
    n=1<<h;ww=w or 4*h+8;j=n*(h*h+3*h+1)
    bound=10**6*ww*ww*(len(offsets)+1)*(n+1)**3*(h+1)**4
    storage=100*(ww+2)+5*ww*j+len(offsets)*n*(4*h-1)+10*(h+1)+sum(map(len,before.values()))
    need(out['steps']<=bound and sum(map(len,tapes.values()))<=storage,'proved conservative bill')
    row=dict(h=h,W=ww,modulus=s,offsets=offsets,selected_layer=selected,instructions=out['steps'],
             layers_sha256=hashlib.sha256(''.join(tapes['layers']).encode()).hexdigest(),rom=rows[selected],
             instruction_bound=bound,represented_cells=sum(map(len,tapes.values())),storage_bound=storage)
    if consume:row['key_consumer']=consumer(tapes['rom'],rows[selected],selected)
    disposal=m.execute(m.disposal_program(),{r:tapes[r] for r in ('layers','rom')})
    need(disposal['status']=='accept' and all(v==0 for v in disposal['heads'].values()),'output disposal head return')
    need(all(all(x=='_' for x in tapes[r]) for r in ('layers','rom')),'owned outputs disposed')
    row['disposal_instructions']=disposal['steps']
    return row

def consumer(cells,oracle_bits,target):
    query=load('query',ROOT/'research/crt-uniform-rom-query/machine.py')
    native=load('native',ROOT/'research/crt-dense-guard-scan/machine.py')
    service=load('service',ROOT/'research/crt-paid-key-service/service.py')
    oracle=load('oracle',ROOT/'research/crt-mask-repair-bridge/key_subroutine.py')
    audit=load('key_audit',ROOT/'research/crt-paid-key-service/verify.py')
    rom=native.Tape();rom.cells=cells  # Same physical output role; no copy or oracle serialization.
    saved=list(cells);result=[]
    for address in (0,10,17,1699,4095):
        raw=f'{address:012b}';counter=native.Tape(['<',*raw,'>']);stream=native.Tape(['<',('R',819),('R',17),'_']);stream.head=3
        engine=service.Service(query,target,rom)
        roles=dict(engine.private,counter=counter,stream=stream,rom=rom)
        initial={r:audit.snapshot(t) for r,t in roles.items()};heads={r:t.head for r,t in roles.items()}
        engine.evaluate_key(counter,stream,trace=True)
        reference=oracle.ReverseWordKey(target,tuple(map(int,oracle_bits)));epochs=[];original=reference.source
        def observed(y):
            bit=original(y);epochs.append((y,bit));return bit
        reference.source=observed;want=reference.key_of(raw)
        need(''.join(stream.cells[3:15])==want,'actual key equals independent reverse word')
        need(rom.cells is cells and cells==saved and rom.head==0,'same generated ROM preserved')
        need(counter.cells==['<',*raw,'>'] and counter.head==0,'borrowed counter preserved')
        need(stream.cells[:3]==['<',('R',819),('R',17)] and stream.head==15,'opaque prefix and append')
        need(all(t.head==0 and all(v=='_' for v in t.cells.values()) for t in engine.private.values()),'consumer private cleanup')
        actual_epochs,_=audit.audit(engine,initial,heads)
        need(actual_epochs==[dict(y=y,bit=bit) for y,bit in epochs],'three actual current-state epochs')
        result.append(dict(address=address,key=want,oracle_epochs=[list(e) for e in epochs],instructions=sum(engine.last['census'].values())))
    return result

def controls(m,crt):
    rejected=[]
    for name,mutate in [
        ('h_nonbit',lambda d:d['h'].__setitem__(1,'x')),
        ('offset_origin',lambda d:d['offsets'].__setitem__(0,'_')),
        ('modulus_zero',lambda d:d.update(modulus=headers(1,0,[0],0)['modulus'])),
        ('modulus_above_N',lambda d:d.update(modulus=headers(1,3,[0],0)['modulus'])),
        ('offset_outside_modulus',lambda d:d.update(offsets=headers(1,2,[2],0)['offsets'])),
        ('selector_outside_layers',lambda d:d.update(selected_layer=headers(1,2,[0],1)['selected_layer'])),
        ('empty_offsets',lambda d:d.update(offsets=['L','R'])),
        ('truncated_offset',lambda d:d['offsets'].pop(1)),
    ]:
        d=headers(1,2,[0],0);mutate(d);out,_=m.run_producer(d,max_steps=200000)
        need(out['status']!='accept','reject '+name);rejected.append(name)
    d=headers(1,2,[0],0);d['modulus']=d['h']
    try:m.run_producer(d)
    except ValueError:rejected.append('borrowed_role_alias')
    else:raise ValueError('aliased role admitted')
    # Changed source program, not a changed expected digest: semantic controls.
    source=(P/'microcode.py').read_text()
    mutants=[('wrong_neighbor',"b.xor1('other');b.get(1,'other','other')","b.get(1,'other','other')"),
             ('missing_output_disposal',"for role in ('layers','rom'):b.erase(role)","for role in ('layers',):b.erase(role)"),
             ('wrong_selected_row',"b.equal('outlayer','selected_layer','selected_bit')","b.e('set','selected_bit','0')")]
    for name,old,new in mutants:
        need(old in source,'mutation applied '+name);bad=load('mutant',P/'microcode.py',source.replace(old,new).encode())
        try:fixture(bad,crt,2,3,[0,1],1)
        except ValueError:rejected.append(name)
        else:raise ValueError('semantic mutant accepted '+name)
    return rejected

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');parser.add_argument('--light',action='store_true');args=parser.parse_args()
    hashes=authenticate();m=load('micro',P/'microcode.py');crt=load('crt',ROOT/'research/unconditional-batched-crt/check_batched_crt.py')
    code=m.producer_program();check_static(code)
    cases=[fixture(m,crt,1,2,[0,1],0,w=4),fixture(m,crt,2,3,[0,1],1),fixture(m,crt,1,1,[0]*17,0,w=4)]
    faults=controls(m,crt)
    if args.light:print('PASS_CRT_ROM_LIGHT',json.dumps({'cases':cases,'controls':faults}));return
    cases.append(fixture(m,crt,3,5,[0,2,4,0],2,consume=True))
    result={'status':'PASS_CRT_ENCODED_BENES_ROM_PRODUCER','scope':'Uniform valid typed descriptor producer plus fixed actual key calibration; no full evaluator tariff or all-size supplier admission',
            'program_instructions':len(code),'code_sha256':hashlib.sha256((P/'microcode.py').read_bytes()).hexdigest(),
            'program_sha256':hashlib.sha256(json.dumps(code,separators=(',',':')).encode()).hexdigest(),'source_hashes':hashes,'cases':cases,'controls':faults}
    path=P/'RESULT.json'
    if args.write_result:path.write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.loads(path.read_text())==result,'frozen exact receipt')
    print(result['status'],f"cases={len(cases)} controls={len(faults)} instructions={cases[-1]['instructions']}")

if __name__=='__main__':main()
