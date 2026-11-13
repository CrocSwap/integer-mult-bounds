"""Full actual core through HOME, exact selected-frame oracle and ABI faults."""
from pathlib import Path
import sys,json,random,hashlib,time,tempfile,shutil,subprocess
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import adapter as A
from machine import Program,initial,fields,check_retired,Rejected,MonitorViolation
from oracle import header,encode,expected_f1


def need(ok,message):
    if not ok:raise ValueError(message)


def header_parser_cases():
    g,stages=A.compile_home(parser_only=True);program=Program(g);receipts=[]
    for power in (0,1,7,63,257,1024,4096):
        shape=(1,3,2,5,4,(1<<power)+1)
        bits=header(shape)+'01011001'
        parked=('10'*len(bits))[:len(bits)]
        state=initial((bits,parked),A.TAPES,old_history=3*len(bits))
        entry=state.highs.copy();program.run(state)
        need(fields(state)==(bits,parked),'Gamma boundary or complete body changed')
        check_retired(state)
        need(state.highs[-1]>=entry[-1],'older retained history shrank')
        need(state.steps<=64*(len(bits)+100),'parser used cutoff numerical value')
        receipts.append({'cutoff_bitlength':shape[-1].bit_length(),'E':len(header(shape)),
                         'F':len(bits),'steps':state.steps,
                         'retained_guide_extent':state.highs[-1]-state.lows[-1]+1})
    return receipts


def verify():
    parser_receipts=header_parser_cases()
    g,stages=A.compile_home();program=Program(g)
    shape=(1,1,1,1,4,1);rng=random.Random(24472)
    values=[(rng.choice((-1,1)),0) for _ in range(512)]
    h=header(shape);data=encode(values,shape[4]);bits=h+data
    expected=h+expected_f1(values,shape)
    need(expected!=bits,'source field fixture is observationally nontrivial')
    parked=''.join(str(rng.randrange(2)) for _ in bits)
    state=initial((bits,parked),A.TAPES,old_history=3*len(bits))
    before=tuple(bytes(t) for t in state.tapes)
    program.run(state,stop=stages['core_return'])
    core_finished=state.clone()
    need(fields(state)==(bits,parked) and state.writes[0]==0,'HOME changed before completed primitive return')
    program.run(state,start=stages['core_return'],stop=stages['primitive_return'])
    ready=state.clone()
    need(fields(state)==(bits,parked) and state.writes[0]==0,'HOME changed during private repack')
    program.run(state,start=stages['primitive_return'])
    need(fields(state)==(expected,parked),'complete selected MOVE or parked home mismatch')
    check_retired(state)
    F=len(bits);V=len(data);E=len(h)
    need(state.steps<=128*(F+1)+(1<<24)*(shape[0]*V+E+1),'complete bill exceeded')
    controls=[]
    # Reuse a successful full-core snapshot; these controls mutate only actual
    # adapter/return suffixes, not the scientific core's numerical execution.
    bad_graph,bad_stages=A.compile_home(mutation='drop_header_return')
    bad=core_finished.clone()
    try:Program(bad_graph).run(bad,start=bad_stages['core_return'])
    except Rejected:controls.append('dropped_header_return')
    else:need(fields(bad)!=(expected,parked),'header-return mutant escaped');controls.append('dropped_header_return')
    wrong_graph,wrong_stages=A.compile_home(selected=1)
    wrong=ready.clone();Program(wrong_graph).run(wrong,start=wrong_stages['primitive_return'])
    need(fields(wrong)!=(expected,parked),'wrong HOME scatter escaped')
    controls.append('wrong_home_return')
    guard_graph,_=A.compile_home(mutation='guard_offset')
    guarded=initial((bits,parked),A.TAPES)
    try:Program(guard_graph).run(guarded)
    except MonitorViolation as exc:need('origin marker' in str(exc),'guard mutant failed for another reason')
    else:raise ValueError('native origin-1 erased permanent B marker without detection')
    controls.append('monitor_detects_native_guard_write_over_B_origin')
    # Outside numerical admission: actual core rejects after private factors;
    # no scatter instruction has yet written HOME.
    bad_shape=(1,1,1,1,3,1);bad_values=[(0,0)]*512;bad_values[0]=(1,0)
    bad_bits=header(bad_shape)+encode(bad_values,3)
    rejected=initial((bad_bits,'0'*len(bad_bits)),A.TAPES)
    saved_home=bytes(rejected.tapes[0])
    try:program.run(rejected)
    except Rejected as exc:need('scanned-symbol' in str(exc),'numerical fixture hit ABI failure')
    else:raise ValueError('nonintegral core input accepted')
    need(rejected.writes[0]==0 and bytes(rejected.tapes[0])==saved_home,'arithmetic rejection mutated HOME')
    controls.append('arithmetic_rejection_before_HOME_mutation')
    zero=initial(('0'*16,'1'*16),A.TAPES)
    try:program.run(zero)
    except Rejected:need(zero.writes[0]==0,'raw zero field changed HOME')
    else:raise ValueError('raw zero capacity was accepted as six-Gamma packet')
    controls.append('raw_zero_is_not_formatted_packet')
    with tempfile.TemporaryDirectory(prefix='_move-source-fault-',dir=HERE.parent) as temporary:
        target=Path(temporary)
        shutil.copytree(HERE/'inputs',target/'inputs',ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('adapter.py','SOURCES.json'):shutil.copy2(HERE/name,target/name)
        source=target/'inputs/native/move.py'
        source.write_bytes(source.read_bytes()+b'\n# actual corruption control\n')
        result=subprocess.run([sys.executable,'-I','-B','-c',
              'import sys;sys.path.insert(0,'+repr(str(target))+');import adapter'],capture_output=True,text=True)
        need(result.returncode!=0 and 'frozen source drift' in result.stderr,'corrupted actual core imported')
    controls.append('frozen_native_core_source_corruption')
    return {'marker':'PASS_SOURCE_BOUND_MOVE_HOME_PRIMITIVE','core_locations':len(A.core()),
            'graph_states':len(g.rules),'tapes':A.TAPES,'shape':shape,'F':F,'E':E,'V':V,
            'successful_steps':state.steps,'core_completed_prefix_steps':core_finished.steps,
            'ready_before_scatter_steps':ready.steps,'rejection_steps':rejected.steps,
            'HOME_writes_success':state.writes[0],'HOME_writes_rejection':rejected.writes[0],
            'monitored_entry_head_spans':list(zip(state.entry_lows,state.entry_highs)),
            'monitored_final_head_spans':list(zip(state.lows,state.highs)),
            'history_boundary':'K_entry also includes preserved opaque exterior storage and any earlier history; reported head windows do not infer the full entry backing',
            'input_sha256':hashlib.sha256(bits.encode()).hexdigest(),
            'output_sha256':hashlib.sha256(expected.encode()).hexdigest(),
            'parked_sha256':hashlib.sha256(parked.encode()).hexdigest(),
            'core_graph_sha256':hashlib.sha256(repr(A.core()).encode()).hexdigest(),
            'fixture':'all odd real signs and zero imaginary; half-integral source-column contributions cancel before the final integrality test',
            'parser_cases':parser_receipts,'controls':controls,
            'scope':'actual exact selected MOVE24472 primitive; supplied packed entry, cutoff and numerical admission; no initializer or complete caller'}


if __name__=='__main__':
    t=time.monotonic();result=verify();raw=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(raw)
    elif (HERE/'RESULT.json').exists():
        need(json.loads((HERE/'RESULT.json').read_text())==json.loads(raw),'scientific receipt changed')
    print(raw,end='');print('elapsed_seconds',round(time.monotonic()-t,3))
