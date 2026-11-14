"""Exact full-field replay; standard-library observers never drive control."""
from pathlib import Path
from hashlib import sha256
import atexit,json,random,sys,tempfile
HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='borrowed-verify-');atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(_cache.name)/'required-absent')
if Path(sys.pycache_prefix).exists():raise ValueError('cache isolation prefix must be absent')
sys.path.insert(0,str(HERE))
import adapter as A
if sha256((HERE/'machine.py').read_bytes()).hexdigest()!='ffe2677bb5b82932873cb08b05f890a1218070215ebe670a0b05079518e8baee':
    raise ValueError('retained interpreter source drift')
from machine import Program,initial,fields,Rejected,MonitorViolation

def need(ok,message):
    if not ok:raise ValueError(message)
def gamma(n):
    b=bin(n)[2:];return '0'*(len(b)-1)+b
def header(shape):return ''.join(gamma(n) for n in shape)
def encode(values,w=6):
    need(all(-(1<<(w-1))<=x<(1<<(w-1)) for z in values for x in z),'oracle width')
    return ''.join(format(x%(1<<w),'0'+str(w)+'b') for z in values for x in z)
def direct(values):
    out=list(values)
    for i in range(256):
        ar,ai=values[i];br,bi=values[i+256]
        rows=(ar-ai+br+bi,ar+ai-br+bi,ar+ai+br-bi,-ar+ai+br+bi)
        need(all(x%2==0 for x in rows),'oracle exact half')
        out[i]=(rows[0]//2,rows[1]//2);out[i+256]=(rows[2]//2,rows[3]//2)
    return out
def setup(data,parked,headers,old_history=0):
    s=initial((parked,data),max(A.TAPES,max(headers)+1),old_history=old_history)
    symbols={'_':0,'0':1,'1':2,'^':3,'|':4,'$':5}
    for t,h in headers.items():
        o=s.origins[t];text='^'+h+'|$101'
        s.tapes[t][o:o+len(text)]=bytes(symbols[c] for c in text)
        s.highs[t]=max(s.highs[t],o+len(text)-1);s.entry_highs[t]=s.highs[t]
    return s
def retired(s,before,headers):
    need(s.heads==s.origins,'all heads return')
    for t,(tape,o) in enumerate(zip(s.tapes,s.origins)):
        need(tape[o]==3 and tape[o-3:o]==before[t][o-3:o] and tape[-3:]==before[t][-3:],'markers/exteriors')
        if t in headers:need(bytes(tape)==before[t],'immutable header and opaque tail')
        elif t!=0:need(not any(tape[o+1:-3]),'private DATA/body/guard retirement')
def run():
    rng=random.Random(1406144)
    values=[(2*rng.randrange(-3,4),2*rng.randrange(-3,4)) for _ in range(512)]
    data=encode(values);parked=''.join(str(rng.randrange(2)) for _ in data)
    short=header((1,1,1,1,6,1));large=header((1,1,1,1,6,(1<<129)+17));headers={3:short,34:large}
    answer1=encode(direct(values));answer2=encode(direct(direct(values)))
    need(answer1!=data and answer2==encode(values[256:]+values[:256]),'nontrivial C squared swap')
    graph,st=A.compile_home(1,header_tapes=(3,34));program=Program(graph)
    s=setup(data,parked,headers,4*len(data));before=[bytes(t) for t in s.tapes]
    program.run(s,stop=st[0]['core_return'])
    need(fields(s)==(parked,data) and s.writes[0]==0,'early HOME write before core success');core_done=s.clone()
    program.run(s,start=st[0]['core_return'],stop=st[0]['primitive_return'])
    need(fields(s)==(parked,data) and s.writes[0]==0,'early HOME write during private return');ready=s.clone()
    program.run(s,start=st[0]['primitive_return'],stop=st[1]['adapter_entry'])
    need(fields(s)==(parked,answer1) and s.writes[0]==len(data),'first same-owner scatter');first_steps=s.steps
    program.run(s,start=st[1]['adapter_entry'],stop=st[1]['core_return'])
    need(fields(s)==(parked,answer1) and s.writes[0]==len(data),'second early HOME write')
    program.run(s,start=st[1]['core_return'])
    need(fields(s)==(parked,answer2) and s.writes[0]==2*len(data),'unequal-E second scatter')
    retired(s,before,headers);need(s.writes[3]==s.writes[34]==0,'header write count')
    need(all(hi>=old for hi,old in zip(s.highs,s.entry_highs)),'old backing refund')
    V,E1,E2=len(data),len(short),len(large)
    need((E1,E2,V)==(10,268,6144),'unequal-E full fixture')
    need(s.steps<=2*((1<<24)*(V+E2+1)+256*(V+1))+256*(V+2),'complete time')
    increment=sum((hi-lo)-(eh-el) for lo,hi,el,eh in zip(s.lows,s.highs,s.entry_lows,s.entry_highs))
    need(increment<=2*2112*(V+E2+1)+16*(V+2),'history increment')
    rejected=[];controls=[]
    for name,g,bits in [('joint_cutoff',A.compile_home(2)[0],data),
       ('short_DATA',A.compile_home(1)[0],data[:-1]),
       ('late_nonintegral',A.compile_home(1)[0],encode([(0,0)]*255+[(1,0)]+[(0,0)]*256))]:
        bad=setup(bits,('01'*len(bits))[:len(bits)],{3:short});saved=bytes(bad.tapes[0]);savedh=bytes(bad.tapes[3])
        try:Program(g).run(bad)
        except Rejected:
            need(bad.writes[0]==0 and bytes(bad.tapes[0])==saved,'rejection HOME mutation')
            need(bytes(bad.tapes[3])==savedh,'rejection header mutation')
        else:raise ValueError('invalid boundary accepted '+name)
        rejected.append({'case':name,'steps':bad.steps,'HOME_writes':bad.writes[0]})
    g,t=A.compile_home(1,mutation='drop_return_bit');bad=core_done.clone()
    try:Program(g).run(bad,start=t[0]['core_return'])
    except Rejected:need(bad.writes[0]==0 and fields(bad)==(parked,data),'late mismatch scattered HOME')
    else:raise ValueError('dropped output bit scattered')
    controls.append('late_return_extent_mismatch_before_HOME_scatter')
    g,t=A.compile_home(1,selected=0);bad=ready.clone();Program(g).run(bad,start=t[0]['primitive_return'])
    need(fields(bad)!=(parked,answer1),'wrong HOME escaped');controls.append('wrong_HOME_scatter')
    g,t=A.compile_home(1,mutation='skip_return');bad=core_done.clone();Program(g).run(bad,start=t[0]['core_return'])
    need(fields(bad)!=(parked,answer1),'skipped private return escaped');controls.append('skipped_private_return')
    g,_=A.compile_home(1,mutation='guard_offset');bad=setup(data,parked,{3:short})
    try:Program(g).run(bad)
    except MonitorViolation:pass
    else:raise ValueError('wrong guard offset escaped test monitor')
    controls.append('test_monitor_detects_guard_over_B_origin')
    return {'marker':'PASS_BORROWED_HEADER_DATA_HOME','rank':1,'V_HOME':V,'header_lengths':[E1,E2],
       'cutoff_bit_lengths':[1,130],'tapes_single_header':34,'tapes_two_header_fixture':35,
       'core_locations':len(A.core(1)),'two_call_graph_states':len(graph.rules),'total_steps':s.steps,
       'first_commit_and_second_gather_steps':first_steps,'HOME_writes':s.writes[0],
       'borrowed_HEADER_writes':[s.writes[3],s.writes[34]],'history_increment_measured':increment,
       'entry_head_spans':list(zip(s.entry_lows,s.entry_highs)),'final_head_spans':list(zip(s.lows,s.highs)),
       'history_scope':'Entry includes supplied/exterior storage and prior larger history; no erasure refund.',
       'input_sha256':sha256(data.encode()).hexdigest(),'first_output_sha256':sha256(answer1.encode()).hexdigest(),
       'second_output_sha256':sha256(answer2.encode()).hexdigest(),'parked_sha256':sha256(parked.encode()).hexdigest(),
       'rejections':rejected,'fault_controls':controls,
       'reuse_boundary':'Both distinct immutable headers are supplied at initial entry; same HOME and private owners/origins reused. No host header replacement counted as implementation.',
       'scope':'Already-packed supplied Gamma6/native view; no producer, view packing, cutoff derivation, all-MOVE/caller or kappa claim.'}
if __name__=='__main__':
    r=json.loads(json.dumps(run()));dest=HERE/'RESULT.json'
    if '--write' in sys.argv:dest.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:need(r==json.loads(dest.read_text()),'receipt drift')
    print('PASS_BORROWED_HEADER_DATA_HOME: immutable headers, complete DATA-only returns and controls.')
