"""Direct old-address/source-frame checks of the uninterrupted full MOVE.
All decoded arithmetic here is verifier-only. Apache-2.0; prepared for
@CubeJerry with substantial OpenAI assistance and credited source oracle.
"""
from pathlib import Path
from hashlib import sha1, sha256
import json
import random
import sys
import types

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok: raise ValueError(message)


def module(path, name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m


C=module(HERE/'compose.py','_checked_full_composition')
SCHEMA=('outer','rows','stock','row_bits','within_bits','record_bits','p','d',
        'K','G','H','q0','qF','qB','D','f','rho','active_start','back_start',
        'selected_axes','entry_start','remainder','cutoff')


def authenticate():
    path=HERE/'SOURCE-PINS.json'
    entries=json.loads(path.read_text())['files']
    for e in entries:
        data=(HERE/e['local']).read_bytes()
        def matches(raw):
            return len(raw)==e['bytes'] and sha256(raw).hexdigest()==e['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['git_blob']
        need(matches(data),'source byte binding '+e['local']);need(not matches(data+b' '),'source mutation control')
    return len(entries)


def source_kernel():
    path=HERE/'inputs/core/reference/source/native_verify.py'
    need(sha256(path.read_bytes()).hexdigest()=='3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38','source oracle pin')
    witness=HERE/'inputs/core/reference/SOURCE-FRAMES.json'
    need(sha256(witness.read_bytes()).hexdigest()=='58f784587d1f21d6aaa1f6a14932779ff1f24d232496b042240e832939c9010d','source witness pin')
    frame=json.loads(witness.read_text())
    need(frame=={'event_index':24472,'event':['MOVE',415,3,99,False],'frames':{'3':[],'99':[239]}},'actual selected source event')
    n=module(path,'_independent_selected_source_kernel')
    circuit=n.adjoint(n.frame(frame['frames']['3'],9))+n.frame(frame['frames']['99'],9)
    columns=[]
    for source in range(512):
        values,denominator=n.state(circuit,source)
        need(denominator==1 and len(values)==2,'exact two-term source kernel')
        columns.append(tuple(sorted((target,pair[0],pair[1]) for target,pair in values.items())))
    return tuple(columns)


KERNEL=source_kernel()


def old_header(values):
    result=[]
    for name in SCHEMA:
        bits=list(map(int,bin(values[name])[2:][::-1]));result.extend([1]*len(bits)+[0]+bits)
    return result


def old_data(values,width):
    result=[]
    for value in values:
        for bit in range(width):result.extend((0,0,(value>>bit)&1))
        result.extend((0,1,0))
    return result


def fixture(width=4,r=1,scale=2,cutoff=1,seed=24472):
    h=dict.fromkeys(SCHEMA,0)
    h.update(outer=1,rows=1,row_bits=512*6*r*(width+1),within_bits=9,
             record_bits=6*r*(width+1),f=1,K=1,rho=0,active_start=0,
             cutoff=cutoff,G=1,H=1,d=9,selected_axes=9,back_start=8)
    rng=random.Random(seed)
    values=[scale*rng.randrange(-1,2) for _ in range(512*2*r)]
    return h,r,width,values


def oracle(values,h,r,width):
    """Direct source-frame columns on old addresses; no lowered factors used."""
    result=list(values);a=h['within_bits'];size=1<<a
    for column in range(h['f']):
        positions=[h['active_start']+(i*h['f']+column)*h['K']+h['rho'] for i in range(9)]
        physical=[1<<(a-1-p) for p in positions];mask=sum(physical)
        numerators=[0]*len(result)
        for row in range(h['outer']*h['rows']):
            for address in range(size):
                native=sum(bool(address&physical[i])<<i for i in range(9))
                for target,cr,ci in KERNEL[native]:
                    destination=(address&~mask)+sum(physical[i] for i in range(9) if target>>i&1)
                    for coefficient in range(r):
                        at=((row*size+address)*r+coefficient)*2
                        to=((row*size+destination)*r+coefficient)*2
                        ar,ai=result[at:at+2]
                        numerators[to]+=cr*ar-ci*ai;numerators[to+1]+=cr*ai+ci*ar
        need(all(x%2==0 for x in numerators),'source-kernel image not integral')
        result=[x//2 for x in numerators]
    need(all(-(1<<(width-1))<=x<(1<<(width-1)) for x in result),'source-kernel endpoint outside width')
    return result


def tapes_for(data,header):
    ts=[C.Tape(origin=3+i%7,permanent_guard=i<43) for i in range(72)]
    ts[0]=C.Tape(data,origin=3);ts[1]=C.Tape(header,origin=4);return ts


def body(t):
    end=t.origin
    while end<len(t.cells) and t.cells[end]!=C.BLANK:end+=1
    return t.cells[t.origin:end]


def returned(tapes,data,header):
    need(body(tapes[0])==data,'complete direct old-address source output')
    need(body(tapes[1])==header and tapes[1].writes==0,'original descriptor preserved')
    for i,t in enumerate(tapes):
        need(t.head==t.origin and t.low>=t.origin-1,'all72 origins/exteriors')
        need(t.cells[t.origin-2]==7,'opaque exterior preserved')
        need(t.cells[t.origin-1]==(C.LEFT if i<43 else C.BLANK),'43 permanent/29 retired guards')
        if i>=2:need(all(s==C.BLANK for s in t.cells[t.origin:]),'all70 private bodies blank')


def positive(code,labels,args,common_root=False):
    h,r,width,values=fixture(**args);expected=oracle(values,h,r,width)
    need(expected!=values,'nonidentity full MOVE fixture')
    data,header=old_data(values,width),old_header(h);ts=tapes_for(data,header);owner=ts[0]
    cpu=C.CPU(code,ts,labels);need(cpu.run(limit=300_000_000)=='DONE','uninterrupted actual full MOVE')
    need(cpu.core_entries==cpu.exit_entries==1,'one complete core invocation/return')
    need(ts[0] is owner,'original old owner identity');returned(ts,old_data(expected,width),header)
    history=sum(t.high-t.low+1 for t in ts[2:]);V,E=len(data),len(header)
    need(cpu.steps<=2**25*(h['f']*V+E+1),'complete time envelope')
    need(history<=2048*(V+E+1),'complete retained history envelope')
    if common_root:
        need(width==22 and all(x%512==0 and abs(x)<1024 for x in values),'n9 p0 h1 t0 common-root input')
    return {'parameters':args,'old_bits':V,'header_bits':E,'transitions':cpu.steps,
            'private_history':history,'common_root_numeric_model':common_root,'changed_exact_output':True}


def reject(code,labels,record,reason,short=False,before_c=False):
    h,r,width,values=record;data=old_data(values,width);header=old_header(h)
    if short:data=data[:-1]
    ts=tapes_for(data,header);cpu=C.CPU(code,ts,labels)
    need(cpu.run(limit=80_000_000)=='REJECT','required rejection: '+reason)
    need(body(ts[0])==data and ts[0].writes==0,'failure original source unchanged')
    need(body(ts[1])==header and ts[1].writes==0,'failure original descriptor unchanged')
    if before_c:need(cpu.core_entries==1 and cpu.first_numerator_write is None,'phase rejection before central C')
    return {'control':reason,'steps':cpu.steps,'entered_core':bool(cpu.core_entries),
            'entered_C_arithmetic':cpu.first_numerator_write is not None,'public_writes':ts[0].writes}


def mutated_core(code,labels,mutation):
    """Verifier-only alternative; the claimed graph never accepts a mutation."""
    retained=sys.modules['_joined_selected_core']
    child,alphabet,_=retained._compile_move(mutation)
    need(alphabet==('_','0','1','|'),'mutant source alphabet')
    out=list(code[:labels['CORE']]);offset=len(out);newlabels=dict(labels)
    for op,*args in child:
        if op=='read':out.append(('R',C.PORT_MAP[args[0]],{C.SYMBOL[s]:offset+q for s,q in args[1].items()}))
        elif op=='write':out.append(('W',C.PORT_MAP[args[0]],C.SYMBOL[args[1]]))
        elif op=='move':out.append(('M',C.PORT_MAP[args[0]],args[1]))
        elif op=='goto':out.append(('J',offset+args[0]))
        elif op=='halt':newlabels['CORE_RETURN']=len(out);out.append(('J',labels['EXIT']))
        else:raise ValueError('nonlocal mutant')
    return tuple(out),newlabels


def controls(code,labels):
    receipts=[];h,r,width,zeros=fixture(width=2,scale=0)
    # Independent review witness: native a0=a7=1 maps to old address258.
    bad=list(zeros);bad[2*258]=-2;final=oracle(bad,h,r,width)
    need(sum(x!=0 for x in final)==4 and all(abs(x)<=1 for x in final),'fitting integral endpoint witness')
    receipts.append(reject(code,labels,(h,r,width,bad),'actual endpoint-only phase overflow at old address258',before_c=True))
    odd=list(zeros);odd[0]=1
    receipts.append(reject(code,labels,(h,r,width,odd),'nonintegral central C after three actual right factors'))
    need(receipts[-1]['entered_C_arithmetic'],'actual central rejection reached')
    receipts.append(reject(code,labels,(h,r,width,zeros),'truncated old-coded field',short=True))
    for mutation in ('drop_absolute_phase','omit_offset'):
        altered,entry=mutated_core(code,labels,mutation)
        mh,mr,mw,values=fixture(width=4,scale=2,seed=24472)
        expected=old_data(oracle(values,mh,mr,mw),mw);data=old_data(values,mw);header=old_header(mh)
        ts=tapes_for(data,header);cpu=C.CPU(altered,ts,entry)
        need(cpu.run(limit=100_000_000)=='DONE','mutant should complete physical return')
        need(body(ts[0])!=expected,'source kernel detects '+mutation)
        receipts.append({'control':mutation,'steps':cpu.steps,'detected_by_direct_source_kernel':True})
    ts=tapes_for(old_data(zeros,width),old_header(h));ts[71]=ts[70]
    try:C.CPU(code,ts,labels)
    except ValueError:receipts.append({'control':'aliased added owner','detected':True})
    else:raise ValueError('alias binding escaped')
    return receipts


def main():
    sources=authenticate();code,labels=C.compile_composition()
    need(len(code)==88816 and C.TAPES==72,'fixed full composition size')
    need(max(ins[1] for ins in code if ins[0] in ('R','W','M'))==71,'complete port inventory')
    cases=[positive(code,labels,{'r':2,'width':4,'scale':2}),
           positive(code,labels,{'width':22,'scale':512,'cutoff':(1<<137)+3},True)]
    negative=controls(code,labels)
    print(json.dumps({'status':'PASS_OLD_CODED_COMPLETE_SELECTED_MOVE','source_event':['MOVE',415,3,99,False],
                      'source_event_index':24472,'fixed_tapes':72,'instructions':len(code),
                      'graph_sha256':C.digest(code),'compose_sha256':sha256((HERE/'compose.py').read_bytes()).hexdigest(),
                      'kernel_sha256':sha256(json.dumps(KERNEL,separators=(',',':')).encode()).hexdigest(),
                      'authenticated_sources':sources,'source_mutations_detected':sources,
                      'positive_cases':cases,'negative_controls':negative,
                      'full_f2_run':False,'assumptions_discharged':[],'new_kappa':False},indent=2))


if __name__=='__main__':main()
