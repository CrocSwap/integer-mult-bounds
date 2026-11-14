"""Independent B12 sparse-CPU, finite-flag, alias and physical-boundary checks.

Reuses the separately frozen B10 CPU, not the author's hardware/semantics.
Integers and mutations below are checker-only. Apache-2.0; prepared for
@CubeJerry with substantial OpenAI assistance.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import types


def need(ok,message):
    if not ok:raise ValueError(message)


def load(path,name):
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def fixture(core,p,a,b,slots,history=0):
    first,second,out=slots;ports=[]
    need(first!=second or a==b,'alias fixture agrees as one physical value')
    for role in range(64):
        cells={0:'L',p+history+2:'EXTERIOR'}
        if role!=out:
            value=a if role==first else b if role==second else (19*role+3)%(1<<p)
            cells.update({k+1:str(value>>k&1) for k in range(p)});cells[p+1]='R'
        ports.append(core.Sparse(cells,1,0,p+history+3))
    for origin in (3,7,2,11):
        cells={origin-1:'BEFORE',origin+8:'AFTER'}
        cells.update({origin+k:str(k%2) for k in range(8)})
        ports.append(core.Sparse(cells,origin,origin,origin+8))
    return ports


def expected(kind,p,a,b):
    if kind=='COMPARE':return None,('CMP_NEG' if a<b else 'CMP_POS' if a>b else 'CMP_EQ')
    value=a+b if kind=='ADD' else a-b
    flag=value>=(1<<p) if kind=='ADD' else value<0
    return value%(1<<p),('ADD_C' if kind=='ADD' else 'SUB_B')+str(int(flag))


def boundary(ports,before,p,kind,a,b,slots,status):
    value,tag=expected(kind,p,a,b);need(status==tag,'independent finite result flag')
    output=slots[2]
    for role,port in enumerate(ports[:64]):
        wanted=dict(before[role][0])
        if role==output:
            wanted.update({k+1:str(value>>k&1) for k in range(p)});wanted[p+1]='R'
        need(port.head==before[role][1] and port.cells==wanted,'entire numeric body/head/history/spectator boundary')
    for role,port in enumerate(ports[64:],64):
        origin=before[role][1]
        wanted={k:v for k,v in before[role][0].items() if not origin<=k<origin+8}
        need(port.head==origin and port.cells==wanted,'complete selector retirement/origin/exterior')


def setup(core,code,labels,meta,p,a,b,kind,alias=False,history=0,slots=None):
    if slots is None:slots=(11,11 if alias else 38,None if kind=='COMPARE' else 61)
    ports=fixture(core,p,a,b,slots,history);before=[(dict(t.cells),t.head) for t in ports]
    cpu=core.CPU(code,labels,meta);need(cpu.run(ports,'ACQUIRE')['instructions']==89,'unchanged acquisition')
    descriptors=slots[:2]+(slots[:2] if kind=='COMPARE' else (slots[2],slots[2]))
    core.setters(cpu,ports,descriptors)
    return cpu,ports,before,slots


def lowering(code,meta,d,arith):
    need(d.digest(code[:meta['old_locations']])=='d36e8220def8efb2baed793d0bea6f0a19b0903b5b005b730652b5bb7d121194',
         'whole unchanged B10 instruction prefix')
    logical,ll=arith.logical_graph(d);mapping=meta['logical_to_physical'][-len(logical):]
    count=0;example=None
    for i,row in enumerate(logical):
        pc=mapping[i]
        if row[0] not in ('R','W','M') or row[1]>=4:
            want=row
            if row[0]=='R':want=('R',row[1],{s:mapping[t] for s,t in row[2].items()})
            if row[0]=='J':want=('J',mapping[row[1]])
            need(code[pc]==want,'every non-dispatch instruction relocation');continue
        for slot in range(64):
            symbols='L'+''.join(str(slot>>bit&1) for bit in range(6))+'R'
            head=0;reads=moves=jumps=0;pos=pc
            while True:
                op,*args=code[pos]
                if op in ('R','W','M') and args[0]<64:break
                if op=='R':
                    need(args[0]==64+row[1],'exact selector read owner');reads+=1;pos=args[1][symbols[head]]
                elif op=='M':
                    need(args[0]==64+row[1],'exact selector movement owner');moves+=1;head+=args[1]
                    need(0<=head<8,'eight-cell selector capability');pos+=1
                elif op=='J':jumps+=1;pos=args[0]
                else:raise ValueError('unexpected dispatch side effect')
                need(reads+moves+jumps<=29,'finite dispatch length')
            need((reads,moves,jumps,head)==(8,14,7,0),'full paid selector dispatch and return')
            need(code[pos][:2]==(row[0],slot),'exact decoded numerical owner')
            if row[0]=='R':need(code[pos][2]=={s:mapping[t] for s,t in row[2].items()},'read branch relocation')
            else:need(code[pos][2]==row[2] and code[pos+1]==('J',mapping[i+1]),'write/move and continuation relocation')
            count+=1
            if example is None:example=pos
    return logical,ll,mapping,count,example


def positive(core,code,labels,meta):
    result=[];tags=set();total=0
    for kind in ('COMPARE','ADD','SUBTRACT'):
        domain=[(4,a,b,False,0) for a in range(16) for b in range(16)]
        domain += [(4,a,a,True,257) for a in range(16)]
        for p in (5,9,17,67):
            maximum=(1<<p)-1
            domain += [(p,a,b,alias,8193) for a,b,alias in [(0,maximum,False),(maximum,1,False),
                       (maximum,maximum,False),(maximum,maximum,True),(1<<(p-1),1<<(p-1),True)]]
        for p,a,b,alias,history in domain:
            cpu,ports,before,slots=setup(core,code,labels,meta,p,a,b,kind,alias,history)
            out=cpu.run(ports,kind);boundary(ports,before,p,kind,a,b,slots,out['status'])
            need(out['instructions']+124+8<=8192*(p+2),'proposed paid primitive envelope')
            need(all(h[0]>=0 and h[1]<=p+1 for h in out['history'][:64]),'numeric history stays inside current typed extent')
            total+=out['instructions'];tags.add(out['status'])
            result.append(dict(kind=kind,p=p,a=a,b=b,alias=alias,history=history,status=out['status'],instructions=out['instructions']))
    need(tags=={'CMP_NEG','CMP_EQ','CMP_POS','ADD_C0','ADD_C1','SUB_B0','SUB_B1'},'every finite return tag witnessed')
    return result,total


def negative(core,code,labels,meta,logical,ll,mapping):
    controls=[]
    for kind,a,b,wrong in [('ADD',15,1,'ADD_C0'),('SUBTRACT',1,15,'SUB_B0'),('COMPARE',1,15,'CMP_POS')]:
        wanted=expected(kind,4,a,b)[1]
        mutant=tuple(('H',wrong) if i>=meta['old_locations'] and row==('H',wanted) else row for i,row in enumerate(code))
        cpu,ports,before,slots=setup(core,mutant,labels,meta,4,a,b,kind)
        out=cpu.run(ports,kind);need(out['status']==wrong,'finite-tag mutation returns')
        try:boundary(ports,before,4,kind,a,b,slots,out['status'])
        except ValueError as error:need('finite result flag' in str(error),'independent flag failure')
        else:raise ValueError('wrong flag escaped')
        controls.append('returning-wrong-'+kind.lower()+'-flag')
    begin=ll['COMPARE_DISTINCT_END_-1'];end=next(i for i in range(begin,len(logical)) if logical[i][0]=='H')
    at=next(mapping[i] for i in range(begin,end) if logical[i]==('W',64,'_'))
    mutant=list(code);mutant[at]=('J',at+1)
    cpu,ports,before,slots=setup(core,mutant,labels,meta,4,1,15,'COMPARE');out=cpu.run(ports,'COMPARE')
    need(out['status']=='CMP_NEG','incomplete retirement mutation returns')
    try:boundary(ports,before,4,'COMPARE',1,15,slots,out['status'])
    except ValueError as error:need('selector retirement' in str(error),'independent dirty-selector detection')
    else:raise ValueError('incomplete retirement escaped')
    controls.append('returning-missing-selector-origin-erasure')
    cpu,ports,before,slots=setup(core,code,labels,meta,4,11,11,'ADD',True)
    origin=ports[65].head;stale=17
    for bit in range(6):ports[65].cells[origin+1+bit]=str(stale>>bit&1)
    out=cpu.run(ports,'ADD');need(out['status'] in ('ADD_C0','ADD_C1'),'stale descriptor returns')
    try:boundary(ports,before,4,'ADD',11,11,slots,out['status'])
    except ValueError:pass
    else:raise ValueError('stale logical source binding escaped')
    controls.append('returning-stale-alias-input-binding')
    for name,mutate in [
        ('short-input',lambda p:p[11].cells.update({3:'R'})),
        ('unequal-input-extent',lambda p:p[38].cells.update({4:'R'})),
        ('dirty-inactive-output',lambda p:p[61].cells.update({2:'1'})),
        ('missing-left-guard',lambda p:p[11].cells.update({0:'_'})),
        ('short-selector',lambda p:p[64].cells.update({p[64].head+3:'R'})),
        ('output-input-alias',lambda p:[p[66].cells.__setitem__(p[66].head+1+k,str(11>>k&1)) for k in range(6)])]:
        cpu,ports,before,slots=setup(core,code,labels,meta,4,11,6,'ADD');mutate(ports)
        need(cpu.run(ports,'ADD')['status']=='MALFORMED','typed rejection '+name);controls.append(name)
    return controls


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--write',type=Path);args=ap.parse_args();here=Path(__file__).resolve().parent;p=args.package.resolve()
    raw=(here/'review_core.py').read_bytes();need(sha256(raw).hexdigest()=='316aace11634045aa0381cb96a22e393f6f9bf857794cf1f6223b9dcfcdf5f2e','frozen independent CPU')
    core=load(here/'review_core.py','independent_B12_CPU')
    d=load(p/'inputs/all-divisions/inputs/divider/divider.py','independent_B12_frozen_divider')
    arith=load(p/'arithmetic.py','independent_B12_graph_under_review');code,labels,meta=arith.compile_arithmetic(d)
    logical,ll,mapping,dispatches,example=lowering(code,meta,d,arith)
    mutant=list(code);row=mutant[example];mutant[example]=(row[0],(row[1]+1)%64,row[2])
    try:lowering(mutant,meta,d,arith)
    except ValueError as error:need('decoded numerical owner' in str(error),'independent wrong physical port control')
    else:raise ValueError('wrong physical port escaped static checker')
    cases,total=positive(core,code,labels,meta);controls=negative(core,code,labels,meta,logical,ll,mapping)
    controls.append('static-wrong-new-dispatch-port')
    result=dict(status='PASS',graph=d.digest(code),locations=len(code),new_logical_locations=len(logical),
        arithmetic_sha256=sha256((p/'arithmetic.py').read_bytes()).hexdigest(),independent_new_dispatch_paths=dispatches,
        cases=len(cases),full_packets=cases,literal_primitive_instructions=total,controls=controls,
        independence='Frozen sparse CPU, direct integer arithmetic, complete physical boundaries; no author hardware or numerical helper imports.')
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
