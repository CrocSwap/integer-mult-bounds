"""STRUCTURAL instrumentation, not an executed numerical whole MOVE.

All three expensive numerical factor methods are explicitly replaced by
fixed test actions. Actual outer lift/drop, both protected coordinators,
literal header handling and physical cleanup execute on a tiny shape which
is NOT admitted by the nine-block monomial geometry. No instrumented action
is a production provider, and these tests cannot count as numerical MOVE evidence.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hashlib import sha256
import json
from check_composition import (S,P,A,RoundedMove,Tape,put,body,encode_header,
                              encode_components,decode_header,specimen,factory,need)
from signed_phase import SignedHeadroomError

def run(mode):
    need(mode in ('success','provider-reject','late-overflow'),'fixed structural fixture mode')
    triple=S.catalog.catalog()[1][13096]
    provider=RoundedMove(triple,factory);work=[Tape(3+j%5) for j in range(provider.port_count)]
    field,context=Tape(9),Tape(11);h=2;w=5;records=4;components=2*records
    header=specimen(1,1,h);header.update(outer=1,rows=1,stock=1,within_bits=2,
        row_bits=records*18,active_start=0,back_start=1,entry_start=0)
    need(header['within_bits']<3*header['H']+9*header['f']*header['K'],
         'explicitly inadmissible whole-MOVE geometry: structural fixture only')
    initial=encode_components([0]*components,h);parent=encode_header(header)
    put(field,initial);put(context,parent)
    provider.bind(work,{provider.owner:A.CodedPort(field)},A.BinaryContextPort(context))
    engine=provider.child.engine;tapes=(*work,field,context)
    ancestors=[bytes(t.cells[:t.origin]) for t in tapes];trace=[]
    before=sum(t.actions() for t in tapes);instrumentation_actions=0;admin={}

    def public_untouched():need(body(field)==bytes(initial),'public untouched before final complete commit')
    def change_component(index,value):
        nonlocal instrumentation_actions
        start=sum(t.actions() for t in tapes)
        port=A.CodedPort(engine.stage.tape);A.origin(port.tape)
        for _ in range(index*(w+1)):port.move(1)
        for j in range(w):port.write((value>>j)&1);port.move(1)
        need(port.read()==2,'instrumented component preserves delimiter')
        A.origin(port.tape);instrumentation_actions+=sum(t.actions() for t in tapes)-start
    def entrance():
        trace.append('entrance');public_untouched();change_component(0,2)
    def positive(field_view,context_view):
        need(field_view.tape is engine.stage.tape and context_view.tape is provider.wide_context.tape,
             'actual inner numerical call uses complete stage and widened parent')
        trace.append('positive');public_untouched();change_component(1,-2)
    def leave():
        trace.append('exit');public_untouched();change_component(0,1);change_component(1,-1)
        if mode=='provider-reject':raise SignedHeadroomError('injected valid-return exit rejection')
        if mode=='late-overflow':change_component(components-1,3)
    engine.entry.run=entrance;engine.child.run=positive;engine.exit.run=leave
    original_lift=provider.lift
    def lift(*args):
        original_lift(*args);trace.append('lift');public_untouched()
        need(decode_header(body(provider.wide_context.tape))==dict(header,record_bits=36,row_bits=records*36),
             'full actual widened header with original f and cutoff')
    provider.lift=lift
    original_inner_commit=engine.commit
    def inner_commit():
        trace.append('inner-commit');public_untouched();start=sum(t.actions() for t in tapes)
        original_inner_commit();admin['inner_commit']=sum(t.actions() for t in tapes)-start
        public_untouched()
    engine.commit=inner_commit
    original_drop=provider.drop
    def drop(*args):
        need(trace==['lift','entrance','positive','exit','inner-commit'],'sole grid drop follows the exact exit boundary')
        trace.append('drop');public_untouched();return original_drop(*args)
    provider.drop=drop
    original_commit=P.commit
    def public_commit(source,target):
        need(trace==['lift','entrance','positive','exit','inner-commit','drop'],'whole public commit follows completed sole rounding')
        trace.append('public-commit');start=sum(t.actions() for t in tapes)
        original_commit(source,target);admin['public_commit']=sum(t.actions() for t in tapes)-start
    P.commit=public_commit;error=None
    try:
        try:provider.run()
        except (SignedHeadroomError,P.RoundedOverflow) as caught:error=type(caught).__name__
    finally:P.commit=original_commit
    wanted_error={'success':None,'provider-reject':'SignedHeadroomError','late-overflow':'RoundedOverflow'}[mode]
    need(error==wanted_error,'precise injected-provider or true-final-overflow boundary')
    expected=[0]*components
    if mode=='success':expected[0]=1
    need(body(field)==bytes(encode_components(expected,h)),'structural whole result or complete preserved original')
    need(body(context)==bytes(parent) and all(not body(t) for t in work)
         and all(t.head==t.origin for t in tapes),'all 4368 roles retired and all origins restored')
    need(all(bytes(t.cells[:t.origin])==old for t,old in zip(tapes,ancestors)),'all ancestor prefixes preserved')
    if mode!='provider-reject':need(admin['inner_commit']==9*records*36+14,'retained exact expanded commit price')
    if mode=='success':need(admin['public_commit']==9*len(initial)+14,'exact final original-width commit price')
    return dict(mode=mode,trace=trace,error=error,source_event=13096,records=records,
                original_V=len(initial),expanded_V=records*36,ports=len(work),
                physical_structural_actions=sum(t.actions() for t in tapes)-before,
                included_test_factor_actions=instrumentation_actions,admin=admin,
                endpoint_sha256=sha256(body(field)).hexdigest(),
                private_materialized_extents=[len(t.cells)-t.origin for t in work],
                private_visited_extents=[t.visited_high-t.origin+1 for t in work],
                factor_methods_replaced=['entrance.run','positive.run','exit.run'],
                full_MOVE_geometry_admitted=False,
                numerical_whole_MOVE_executed=False)

def check():return dict(cases=[run(mode) for mode in ('success','provider-reject','late-overflow')],
                        structural_instrumentation_only=True,numerical_whole_MOVE_executed=False)

if __name__=='__main__':
    from argparse import ArgumentParser
    parser=ArgumentParser();parser.add_argument('--mode',choices=('success','provider-reject','late-overflow'))
    parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=run(args.mode) if args.mode else check()
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    cases=[result] if args.mode else result['cases']
    print('PASS_ROUNDED_MOVE_STRUCTURAL_ONLY',json.dumps(dict(cases=len(cases),
        actions=sum(x['physical_structural_actions'] for x in cases),ports=4368,
        numerical_whole_MOVE_executed=False),sort_keys=True))
