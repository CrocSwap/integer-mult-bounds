"""Actual bounded serial calls, independently predicted full signed outputs.

The numerical oracle is the authenticated predecessor's address formula;
the production service consumes only current tape ports. No source algorithm
is replaced. Prepared for @CubeJerry with substantial OpenAI assistance.
Apache-2.0.
"""
from argparse import ArgumentParser
from hashlib import sha256
import json
import time
from column_view import SerialProvider, S
from serial_sources import need
from check_descriptor import put, body, encode as header_bits
from check_fixture import factory, literal, fixture, encode
from ordinary import Ordinary


def hardware(recipe, inverse=False):
    owner=SerialProvider(recipe,factory,inverse=inverse)
    work=[S.codec.DenseTape(3+i%5) for i in range(owner.port_count)]
    field,context=S.codec.DenseTape(9),S.codec.DenseTape(11)
    for t in (*work,field,context):
        for j in range(t.origin-1):t.cells[j]=j%2
    owner.bind(work,S.abi.CodedPort(field),S.abi.BinaryContextPort(context))
    return owner,work,field,context


def execute(state, values, initial, expected, reject=False):
    owner,work,field,context=state
    put(field,initial);put(context,header_bits(values))
    tapes=(*work,field,context)
    ancestors=[bytes(t.cells[:t.origin]) for t in tapes]
    before=sum(t.actions() for t in tapes)
    old=Ordinary.run
    def forbidden(*args,**kwargs):
        raise ValueError('ordinary-runtime-entry-trap')
    # A failure detector, not a numerical substitute: every successful trace
    # must avoid the entry point entirely. All monomial bytes are unchanged.
    Ordinary.run=forbidden
    failed=False
    started=time.monotonic()
    try:
        try:owner.run()
        except S.state.phase.SignedHeadroomError:failed=True
    finally:
        Ordinary.run=old
    need(failed==reject,'expected exact signed-domain outcome')
    need(body(field)==expected,'independent complete signed endpoint')
    need(body(context)==header_bits(values),'parent descriptor preserved')
    need(all(t.head==t.origin for t in tapes),'complete heads restored')
    need(all(not body(t) for t in work),'current private bodies erased')
    need([bytes(t.cells[:t.origin]) for t in tapes]==ancestors,'all ancestors preserved')
    need(not owner.view.active and not owner.native.pool.live
         and owner.native.engine.closed and not owner.native.engine.pool.live,
         'all serial and monomial scopes closed')
    need(all(n==0 for n in owner.native.engine.compact.calls.values()),'zero Compact/ordinary runtime calls')
    return dict(columns=values['f'],rank=owner.native.rank,
                records=values['outer']*values['rows']*(1<<values['within_bits']),
                physical_bits=len(initial),physical_actions=sum(t.actions() for t in tapes)-before,
                materialized_private_cells=sum(len(t.cells) for t in work),
                fixed_private_ports=owner.port_count,ordinary_runtime_calls=0,
                signed_guard_rejected=failed,endpoint_sha256=sha256(bytes(body(field))).hexdigest(),
                elapsed_seconds=round(time.monotonic()-started,6))


def ordinary_trap_control():
    original=Ordinary.run
    def trap(*args,**kwargs):raise ValueError('ordinary-runtime-entry-trap')
    Ordinary.run=trap
    try:
        try:factory().run(None,None,None)
        except ValueError as e:need(str(e)=='ordinary-runtime-entry-trap','entry detector fired')
        else:raise ValueError('ordinary entry detector missing')
    finally:Ordinary.run=original


def batched_counterexample(recipe, values, initial):
    """The unmodified multi-column provider accepts the cancellation case."""
    owner=S.adapter.Provider(recipe,factory)
    work=[S.codec.DenseTape(3+i%5) for i in range(owner.port_count)]
    field,context=S.codec.DenseTape(9),S.codec.DenseTape(11)
    owner.bind(work)
    put(field,initial);put(context,header_bits(values))
    tapes=(*work,field,context)
    before=sum(t.actions() for t in tapes)
    owner.run(S.abi.CodedPort(field),S.abi.BinaryContextPort(context))
    need(body(field)==initial and body(context)==header_bits(values),
         'actual batched cancellation accepts most-negative component')
    need(all(t.head==t.origin for t in tapes) and all(not body(t) for t in work),
         'actual batched counterexample cleanup')
    return dict(actual_batched_execution=True,accepted=True,
                physical_actions=sum(t.actions() for t in tapes)-before,
                endpoint_sha256=sha256(bytes(initial)).hexdigest())


def run(mode):
    ordinary_trap_control()
    if mode in ('forward','inverse'):
        recipe=literal()
        inverse=mode=='inverse'
        v,initial,expected=fixture(recipe,f=2,K=1,h=4,coefficients=1,inverse=inverse)
        result=execute(hardware(recipe,inverse),v,initial,expected)
    elif mode=='phase-domain':
        recipe=dict(matrix_rows=(1,),offset=0,linear_Z4=(0,),quadratic_rows=(0,),phase=2)
        v,initial,expected=fixture(recipe,f=2,K=1,h=3,coefficients=1)
        state=hardware(recipe)
        result=execute(state,v,initial,expected)
        records=[((-(1<<2),0),)]*(1<<v['within_bits'])
        bad=encode(records,3)
        # Batched total phase is +1 and its exact output is the same representable
        # word. Serial column1 is a negation and rejects before any public write.
        rejected=execute(state,v,bad,bad,True)
        result=dict(success=result,serial_rejection=rejected,
                    combined_phase=0,first_serial_phase=2,
                    batched_endpoint_representable=True,
                    actual_batched=batched_counterexample(recipe,v,bad))
    elif mode=='history':
        recipe=dict(matrix_rows=(1,),offset=0,linear_Z4=(1,),quadratic_rows=(0,),phase=1)
        state=hardware(recipe)
        v,a,b=fixture(recipe,f=2,K=1,H=2,h=3,coefficients=1)
        large=execute(state,v,a,b)
        v,a,b=fixture(recipe,f=1,K=1,H=1,h=3,coefficients=1)
        short=execute(state,v,a,b)
        fresh=execute(hardware(recipe),v,a,b)
        need(short['physical_actions']==fresh['physical_actions'],'same small-call actions after longer history')
        need(short['materialized_private_cells']>fresh['materialized_private_cells'],'history backing retained')
        result=dict(large=large,reused_small=short,fresh_small=fresh)
    else:raise ValueError('unknown fixed fixture')
    return dict(status='PASS_SERIAL_MONOMIAL_ACTUAL_NUMERIC',mode=mode,result=result,
                actual_selected_nine_axis_move=False,ordinary_entry_detector_checked=True)


if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('mode',choices=('forward','inverse','phase-domain','history'))
    print(json.dumps(run(parser.parse_args().mode),sort_keys=True))
