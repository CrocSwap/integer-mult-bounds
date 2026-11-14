"""Full source-bound affine MOVE replay and physical phase-lift probes."""
from pathlib import Path
import atexit,json,random,shutil,subprocess,sys,tempfile,time
from hashlib import sha256
HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='source-move-verify-');atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(_cache.name)/'absent')
import adapter as A
import move as C
from machine import Program,initial,fields,check_retired,Rejected
from oracle import header,encode,image,reverse9,gamma
from bind_source import verify as bind_source


def need(ok,label):
    if not ok:raise ValueError(label)


def phase_lift_probes():
    from controller_reference import Tape,Machine
    h=C.P.PHASE;records=[]
    for constant in range(4):
        a=C.Builder()
        for t in h.PRIVATE:
            a.op('move',t,-1);a.op('write',t,C.MARK);a.op('move',t,1)
        h.gamma(a,h.COLUMNS);h.trace_return(a,h.HEADER,h.HTRACE)
        h.initialize(a,h.COUNTERS,constant)
        for mode in range(4):a.mark('record'+str(mode));a.op('halt')
        terminals={a.labels['record'+str(mode)]:mode for mode in range(4)}
        code,_=a.finish(('_','0','1','|'))
        for f in (1,2,3,4,5,16,65):
            origins=[5*t-77 for t in range(23)]
            tapes=[Tape({},o) for o in origins];text=gamma(f)
            tapes[0].cells.update({origins[0]+i:b for i,b in enumerate(text)})
            machine=Machine(code,tapes).run(2000000);mode=terminals[machine.pc-1]
            need(mode==(constant*f)%4,'literal constant phase times f')
            for tape in h.COUNTERS:
                need(all(tapes[tape].cells.get(origins[tape]+i)=='0' for i in range(f)),
                     'literal f-bit phase counters')
                need(tapes[tape].head==origins[tape],'phase counter origin')
            need(tapes[0].head==origins[0],'phase prefix header return')
            records.append({'constant':constant,'f':f,'mode':mode,'steps':machine.steps})
    need(next(r for r in records if r['constant']==2 and r['f']==2)['mode']!=2,'constant once control')
    return records


def source_corruption():
    with tempfile.TemporaryDirectory(prefix='actual-move-corruption-') as tmp:
        dst=Path(tmp)
        for name in ('move.py','SOURCES.json','RECIPE.json'):shutil.copy2(HERE/name,dst/name)
        for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
            q=dst/pin['local'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/pin['local'],q)
        q=dst/'engines/reference/translation/translate.py';q.write_bytes(q.read_bytes()+b'\n# altered actual retained bytes\n')
        launch=('import sys,tempfile;from pathlib import Path;d=tempfile.TemporaryDirectory();'
                'sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(d.name)/"absent");'
                'sys.path.insert(0,'+repr(str(dst))+');import move')
        r=subprocess.run([sys.executable,'-I','-B','-c',launch],capture_output=True,text=True)
        need(r.returncode!=0 and 'frozen source drift' in r.stderr,'actual source corruption accepted')


def run():
    source=bind_source();probes=phase_lift_probes()
    code,alphabet,entries=C.compile_move()
    need(alphabet==('_','0','1','|'),'fixed alphabet')
    need(not any(op=='write' and args[0]==C.DATA for op,*args in code[:entries['commit']]),'early original core write')
    for op,*args in code:
        if op in ('read','write','move'):need(0<=args[0]<C.TAPES,'fixed core port')
        if op=='read':need(all(0<=p<len(code) for p in args[1].values()),'fixed branch bound')
        if op=='goto':need(0<=args[0]<len(code),'fixed jump bound')
        if op=='move':need(args[1] in (-1,1),'unit core move')
    graph,stages=A.compile_home();program=Program(graph);rng=random.Random(24476)
    shape=(1,1,1,1,8,3)
    values=[(8*rng.randrange(-1,2),8*rng.randrange(-1,2)) for _ in range(512)]
    h=header(shape);data=encode(values,8);bits=h+data
    answer=image(values,shape);expected=h+encode(answer,8)
    need(expected!=bits and any(a or b for a,b in answer),'nontrivial original-frame answer')
    parked=''.join(str(rng.randrange(2)) for _ in bits)
    state=initial((parked,bits),A.TAPES,old_history=3*len(bits));old=state.highs.copy()
    program.run(state,stop=stages['core_return'])
    need(fields(state)==(parked,bits) and state.writes[0]==0,'HOME changed before complete core return')
    core_steps=state.steps
    program.run(state,start=stages['core_return'],stop=stages['primitive_return'])
    need(fields(state)==(parked,bits) and state.writes[0]==0,'HOME changed before B1 scatter')
    program.run(state,start=stages['primitive_return'])
    need(fields(state)==(parked,expected),'complete source-bound affine MOVE image')
    need(state.writes[0]==len(bits),'sole original-owner HOME commit');check_retired(state)
    need(all(x>=y for x,y in zip(state.highs,old)),'old history refunded')
    increment=sum((hi-lo)-(ehi-elo) for lo,hi,elo,ehi in zip(state.lows,state.highs,state.entry_lows,state.entry_highs))
    need(increment<=2112*(len(bits)+1),'actual recipe complete backing envelope')
    first={'shape':shape,'F':len(bits),'E':len(h),'V':len(data),'steps':state.steps,
           'core_return_steps':core_steps,'HOME_writes':state.writes[0],'visited_increment':increment,
           'output_sha256':sha256(expected.encode()).hexdigest()}
    # Invalid joint rank cutoff, otherwise the same completely encoded packet.
    bad=header((1,1,1,1,8,2))+data;rejected=initial(('0'*len(bad),bad),A.TAPES);before=bytes(rejected.tapes[0])
    try:program.run(rejected)
    except Rejected:pass
    else:raise ValueError('joint3f cutoff accepted')
    need(rejected.writes[0]==0 and bytes(rejected.tapes[0])==before,'bad cutoff changed original HOME')
    # Construct R*x supported on native basis0/e0 with equal unit values.
    # First C0 and swap complete, then C1 encounters a genuine odd numerator.
    right=C.SOURCE['recipe']['right'];numeric=[(0,0)]*512
    for x in range(512):
        target=sum(((row&x).bit_count()&1)<<i for i,row in enumerate(right['matrix_rows']))^right['offset']
        if target in (0,1):
            q=right['phase']+sum(right['linear_Z4'][i] for i in range(9) if (x>>i)&1)
            q+=2*sum(1 for i in range(9) for j in range(i+1,9)
                     if (x>>i)&(x>>j)&1 and (right['quadratic_rows'][i]>>j)&1)
            numeric[reverse9(x)]=((1,0),(0,-1),(-1,0),(0,1))[q%4]
    late_bits=h+encode(numeric,8);late=initial(('0'*len(late_bits),late_bits),A.TAPES);saved=bytes(late.tapes[0])
    base=int(stages['core_entry'].rsplit('.',1)[1]);second='MOVE24476.'+str(base+entries['center_C1_'])
    program.run(late,stop=second);completed=late.steps
    middle=[(0,0)]*512;middle[0]=middle[128]=(1,0)
    start=late.origins[A.CORE_BASE+C.WORK]+2
    need(bytes(late.tapes[A.CORE_BASE+C.WORK][start:start+len(data)])==
         bytes(1 if b=='0' else 2 for b in encode(middle,8)),'actual right monomial and first C/swap image')
    try:program.run(late,start=second)
    except Rejected:pass
    else:raise ValueError('late nonintegral C prefix accepted')
    need(late.writes[0]==0 and bytes(late.tapes[0])==saved,'late numerical failure changed HOME')
    wrong_graph,_=A.compile_home(mutation='wrong_phase');wrong=initial((parked,bits),A.TAPES)
    Program(wrong_graph).run(wrong)
    rotated=h+encode([(-b,a) for a,b in answer],8)
    need(fields(wrong)==(parked,rotated) and rotated!=expected,'actual absolute-phase graph control')
    check_retired(wrong);source_corruption()
    return {'marker':'PASS_SOURCE_BOUND_AFFINE_MOVE_HOME','source':source,'phase_lift_probes':probes,
            'core_locations':len(code),'core_sha256':sha256(repr(code).encode()).hexdigest(),
            'HOME_states':len(graph.rules),'tapes':A.TAPES,'core_tapes':C.TAPES,'full_f1':first,
            'cutoff_rejection_steps':rejected.steps,'late_rejection':{'first_C_and_R_completed':completed,
             'steps':late.steps,'HOME_writes':late.writes[0]},'wrong_phase_steps':wrong.steps,
            'scope':'one supplied public-role727 Gamma6 direct MOVE; no caller/source-producer/nonleaf admission'}


if __name__=='__main__':
    start=time.monotonic();result=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    elif (HERE/'RESULT.json').exists():need(json.loads((HERE/'RESULT.json').read_text())==json.loads(json.dumps(result)),'receipt drift')
    print(json.dumps(result,sort_keys=True));print('elapsed_seconds',round(time.monotonic()-start,3))
