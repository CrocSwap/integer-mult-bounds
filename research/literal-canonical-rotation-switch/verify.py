"""Bounded exact-source and physical replay for the direct switch graph.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import types

HERE=Path(__file__).resolve().parent

def need(ok,label):
    if not ok: raise ValueError(label)
def load(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def authenticate():
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())
    for p in pins['files']:
        raw=(HERE/p['local']).read_bytes()
        need(len(raw)==p['bytes'] and sha256(raw).hexdigest()==p['sha256'],'source drift '+p['local'])
        need(sha256(raw).hexdigest()==p['sha256'],'source pin')
    need(sha256((HERE/'inputs/check_batched_crt.py').read_bytes()).hexdigest()=='681e2e3d71fa74c8b9b326f3860104fd9d89590a222e26ae6ee718d1fd40ff2e','canonical compiler pin')

def run_case(graph,hardware,code,labels,args,expected,overrides=None,outcome='DONE'):
    tapes=hardware.fixture(*args,overrides=overrides);before=[list(t.cells) for t in tapes]
    cpu=hardware.CPU(code,tapes,labels);actual=cpu.run(1024*(args[0]+3)**2)
    need(actual==outcome,'expected '+outcome+' for '+repr(args))
    history=hardware.check_return(tapes,before,actual,expected)
    if actual=='DONE': need(cpu.iterations<=args[0],'at most h child iterations')
    need(history<=16*(args[0]+4)+max(0,len(tapes[0].cells)-args[0]-8),'complete history bound')
    return {'steps':cpu.steps,'iterations':cpu.iterations,'history':history,
            'reads':sum(t.reads for t in tapes),'writes':sum(t.writes for t in tapes),
            'moves':sum(t.moves for t in tapes),'borrowed_writes':sum(t.writes for t in tapes[:5])}

def evidence():
    authenticate(); graph=load(HERE/'switch.py','literal_switch'); hw=load(HERE/'hardware.py','switch_hardware')
    reference=load(HERE/'inputs/check_batched_crt.py','exact_canonical_benes')
    code,labels=graph.compile_query()
    need(set(ins[0] for ins in code)<=set(('R','W','M','J','H')),'fixed opcode grammar')
    for ins in code:
        if ins[0]=='R':
            need(set(ins[2])==set(range(5)) and all(0<=pc<len(code) for pc in ins[2].values()),'complete finite branches')
        elif ins[0]=='J': need(0<=ins[1]<len(code),'jump range')
        elif ins[0]=='M': need(ins[2] in (-1,1),'unit moves')
        elif ins[0]=='W': need(ins[2] in range(5) and ins[1]>=5,'fixed writes/no borrowed write')
    count=networks=0; max_steps=0; max_history=0; totals={'steps':0,'reads':0,'writes':0,'moves':0}
    for h in range(1,4):
        n=1<<h
        for modulus in range(1,n+1):
            for offset in range(modulus):
                rows=reference.benes(reference.rotation(n,modulus,offset));networks+=1
                for j,(_,row) in enumerate(rows):
                    for x,expected in enumerate(row):
                        r=run_case(graph,hw,code,labels,(h,modulus,offset,j,x),expected);count+=1
                        max_steps=max(max_steps,r['steps']);max_history=max(max_history,r['history'])
                        for k in totals:totals[k]+=r[k]
    key=[];key_steps=0;key_max=0
    for a in range(17):
        row=reference.benes(reference.rotation(32,17,a))[6][1]
        for x,expected in enumerate(row):
            r=run_case(graph,hw,code,labels,(5,17,a,6,x),expected)
            key.append(expected);key_steps+=r['steps'];key_max=max(key_max,r['steps'])
    # Source-specific semantic controls, chosen separately from key row6.
    semantic=[]
    for args in [(2,3,1,0,2),(3,5,1,4,5),(3,6,5,2,1),(3,5,1,1,5),
                 (3,5,1,1,4),(4,16,15,3,15),(4,9,8,6,0),(4,9,1,6,9)]:
        h,s,a,j,x=args;expected=reference.benes(reference.rotation(1<<h,s,a))[j][1][x]
        r=run_case(graph,hw,code,labels,args,expected);semantic.append(dict(parameters=args,expected=expected,**r))
    invalid=[((0,1,0,0,0),None),((2,0,0,0,0),None),((2,5,0,0,0),None),
             ((2,3,3,0,0),None),((2,3,0,3,0),None),((2,3,0,0,4),None),
             ((2,3,0,0,0),{0:[]}),((2,3,0,0,0),{0:[0]}),
             ((2,3,0,0,0),{0:[1,0]}),((2,3,0,0,0),{0:[1,4]}),
             ((2,3,0,0,0),{1:[1,1]}),((2,3,0,0,0),{2:[0,0,0,0]}),
             ((2,3,0,0,0),{3:[0,4,0]})]
    for args,over in invalid:run_case(graph,hw,code,labels,args,None,over,outcome='REJECT')
    alias=hw.fixture(2,3,1,0,2);alias[7]=alias[6]
    try:hw.CPU(code,alias,labels)
    except ValueError:pass
    else:raise ValueError('owner alias accepted')
    mutations={}
    for name,args in [('swap_child',(3,5,1,1,5)),('drop_branch_carry',(3,5,1,1,5)),('drop_padded_first',(2,3,1,0,2))]:
        changed,lab=graph.compile_query(name);h,s,a,j,x=args
        expected=reference.benes(reference.rotation(1<<h,s,a))[j][1][x]
        tapes=hw.fixture(*args);before=[list(t.cells) for t in tapes];cpu=hw.CPU(changed,tapes,lab)
        result=cpu.run(1024*(h+3)**2)
        got=tapes[5].cells[tapes[5].origin] if result=='DONE' else None
        need(got!=expected,'semantic mutation escaped '+name)
        hw.check_return(tapes,before,result,got)
        mutations[name]={'parameters':args,'expected':expected,'actual':got,'outcome':result}
    large=[]
    for h in (7,17,65,129):
        args=(h,1<<h,1<<(h-1),h-1,0)
        # Exact dyadic half-turn passes through h-1 nonzero child reductions
        # and ends at the one-bit swap; no exponential reference is built.
        r=run_case(graph,hw,code,labels,args,1);large.append({'h':h,'expected':1,**r})
    return {'marker':'PASS_LITERAL_CANONICAL_ROTATION_SWITCH','locations':len(code),'tapes':14,
            'graph_sha256':graph.digest(code),'source_reference_sha256':sha256((HERE/'inputs/check_batched_crt.py').read_bytes()).hexdigest(),
            'full_small_networks':networks,'full_small_switch_queries':count,'small_totals':totals,
            'small_max_steps':max_steps,'small_max_history':max_history,
            'h5_s17_j6':{'queries':len(key),'bit_bytes_sha256':sha256(bytes(key)).hexdigest(),'total_steps':key_steps,'max_steps':key_max},
            'semantic_controls':semantic,'malformed_rejections':len(invalid),'alias_rejections':1,
            'semantic_mutants':mutations,'large_full_depth_queries':large,
            'source_code_sha256':sha256((HERE/'switch.py').read_bytes()).hexdigest(),
            'limitations':['finite physical fixtures do not prove all h','no CRT offset production or descriptor serialization','no complete workload gain or kappa claim']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path);a=p.parse_args()
    result=evidence();payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.receipt:a.receipt.write_text(payload)
    print(result['marker']);print(json.dumps({k:result[k] for k in ('locations','tapes','graph_sha256','full_small_switch_queries','h5_s17_j6','malformed_rejections')},sort_keys=True))
