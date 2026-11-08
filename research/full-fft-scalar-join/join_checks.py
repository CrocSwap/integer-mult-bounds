"""Actual Full and forced-fast complex calls with independent endpoint checks.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The prior Full fixture and exact finite floor helper retain their attribution.
"""
from collections import Counter as Observations
from hashlib import sha256
import sys
import time
from types import ModuleType
from unittest.mock import patch

from join_sources import FULL,full_sources,load,need,opened


def reject(function,message):
    try:
        function()
    except ValueError as error:
        need(message in str(error),'specific rejecting boundary: '+message)
        return str(error)
    raise ValueError('negative control accepted: '+message)


def cold_controls():
    result=[]
    for name in ('fft_word_plan','ring_words','twiddle_setup','layout','join_engine'):
        need(name not in sys.modules,'cold control starts before source loading')
        with patch.dict(sys.modules,{name:ModuleType(name)}):
            def attempt():
                with opened():
                    raise ValueError('forged imported source reached the owner')
            result.append(dict(module=name,rejected=reject(attempt,'one cold Full/FftWord/H cohort')))
    return result


def source_case():
    with full_sources() as (dense,lower,source,compiler,reference):
        scalar=source.e.C(2,1)
        program=compiler.FullTensor(dense,lower,source,[[[[scalar,0],[0,scalar]]]],[[True]],
                                    target=8,radius_bits=1,incoming=0)
        values=[(1,1),(-1,0)]
        oracle=reference.FreshSemanticService()
        expected,semantic=program.execute(values,oracle)
        target=reference.root_exact(program,[reference.decode(z,program.incoming) for z in values])
        error=reference.distance_squared([reference.decode(z,program.bits) for z in expected],target)
        need(error<=program.total_error**2 and error<program.tau**2,
             'retained Full source meets its complete root target')
        need((program.bits,program.data_width,program.stages,program.h_count,program.diagonal_count)
             ==(407,608,21,10,11),'unchanged complete high-precision Full fixture')
        result=dict(program=program,values=values,expected=expected,
                    event_types=(compiler.Hadamard,compiler.Diagonal),
                    allocation=program.record(),semantic=semantic,oracle=oracle.stats,
                    root_error_squared_sha256=sha256(str(error).encode()).hexdigest())
    program.validate()
    return result


def method_binding():
    from join_engine import FastFullPhysical
    from physical_engine import FullPhysical
    names=('note','admit_radius','lift_input','h_event','product','coefficient_field','diagonal','run')
    need(all(getattr(FastFullPhysical,name) is getattr(FullPhysical,name) for name in names),
         'literal inherited Full stage methods')
    need(FastFullPhysical.__init__ is not FullPhysical.__init__
         and FastFullPhysical.idle is not FullPhysical.idle,
         'explicit new constructor and stronger nested idle contract')
    return list(names)


def meters(tapes):
    result={}
    for tape in tapes:
        meter=getattr(tape,'meter',None)
        if meter is None and hasattr(tape,'arena'):
            meter=tape.arena.meter
        if meter is not None:
            result[id(meter)]=meter
    return tuple(result.values())


def actions(items):
    return {key:sum(getattr(item,key) for item in items) for key in ('reads','writes','moves')}


def difference(after,before):
    return {key:after[key]-before[key] for key in before}


def saved(tapes):
    return tuple((bytes(tape.cells),tape.head) for tape in tapes)


def scalar_clean(word):
    from words import BLANK
    word.idle()
    need(word.closed and word.a is word.b is None and not word.pool.live
         and word.output.read()==BLANK,'closed scalar owner after return consumption')
    owners=(word,word.base,word.product,word.product.word,word.product.twiddles)
    need(all(not owner.pool.live for owner in owners),'every nested scalar pool empty')
    tapes=[t for owner in owners for t in owner.pool.tapes]
    tapes.extend(word.canonical)
    tapes.extend(owner.output for owner in owners)
    need(all(t.head==1 and all(x==BLANK for x in t.cells) for t in tapes),
         'every nested scalar body and marker erased')


def full_run(case,progress=False):
    from cardinal_counts import Count
    from check_support import bits,no_decode
    import check_composed
    from join_engine import FastFullPhysical,PRODUCTION_CUTOFF
    from physical_controls import PreparedFull,emit_signed
    from records import Tape
    from session import erase_marker
    from words import BLANK
    helper=load('retained_full_checks',FULL/'verify_physical.py')
    root,visits=check_composed.fixture('standard',False)
    events=Observations()
    def observe(event):
        events.update([event])
        if progress and event=='data_products' and events[event]%2==0:
            print('Full diagonal completed: '+str(events[event]//2),file=sys.stderr,flush=True)
    owner=FastFullPhysical(root,observe=observe)
    program=case['program']
    prepared=PreparedFull(program,Tape,Count,case['event_types'])
    payload=Tape()
    for pair in case['values']:
        for value in pair:
            emit_signed(payload,value,prepared.metadata['incoming_width'])
    payload.rewind()
    borrowed=(payload,prepared.code,*(x.tape for x in prepared.parameters))
    initial=saved(borrowed)
    aliases=[]
    word=owner.word
    targets=(word.pool.tapes[0],word.base.pool.tapes[0],word.product.pool.tapes[0],
             word.product.word.pool.tapes[0],word.product.twiddles.pool.tapes[0],
             word.output,word.base.output,word.product.output,
             word.product.word.output,word.product.twiddles.output)
    try:
        for target in targets:
            before=actions(meters((*borrowed,*owner.private)))
            aliases.append(reject(lambda target=target:prepared.run(owner,target),
                                  'external distinct physical Full input and metadata ports'))
            aliases.append(reject(lambda target=target:owner.run(payload,target,*prepared.parameters),
                                  'external distinct physical Full input and metadata ports'))
            need(before==actions(meters((*borrowed,*owner.private))),
                 'nested private aliases reject before physical tape traffic')
        # A real completed child return must be consumed before parent entry.
        values=tuple(Count.literal(x) for x in (2,3,2))
        try:
            with no_decode():
                raw=word.run(*values)
            need(bits(raw)==bytes((6>>i)&1 for i in range(4)),'complete padded base control return')
            child_protected=reject(lambda:prepared.run(owner,payload),
                                   'consumed complete exact FFT-word child')
            need(saved(borrowed)==initial,'child-protection rejection preserves caller inputs')
            raw.clear();erase_marker(raw)
        finally:
            for value in values:value.close()
        scalar_clean(word)
        count_before=dict(word.calls)
        all_meters=meters((*borrowed,*owner.private))
        before_actions=actions(all_meters)
        start=time.monotonic()
        bases=(program.axes,program.data_width+program.axes,program.data_width+2*program.axes)
        with helper.certified_floors(bases) as (table,uses,misses):
            with no_decode():
                returned=prepared.run(owner,payload)
        elapsed=time.monotonic()-start
        after_actions=actions(all_meters)
        output=bits(returned)
        need(output==check_composed.encode(case['expected'],program.data_width),
             'same complete Full endpoint with exact FFT scalar owner')
        need(saved(borrowed)==initial,'all Full borrowed values and heads restored')
        owner.idle();scalar_clean(word)
        need(owner.closed and owner.current is None and not owner.pool.live,
             'closed complete fast Full owner')
        need(not misses,'only the declared exact finite floor specialization was used')
        delta=difference(word.calls,count_before)
        need(delta==dict(base=92,fft=0) and owner.arithmetic.products==92,
             'Full fixture uses declared fixed production base branch')
        protected=reject(lambda:prepared.run(owner,payload),
                         'consume the previous compiler-boundary output')
        need(saved(borrowed)==initial,'protected final return preserves borrowed ports')
        result=dict(marker='PASS_FULL_FFT_OWNER',fixed_cutoff=PRODUCTION_CUTOFF,
            fixture_fft_branch=False,allocation=case['allocation'],input=case['values'],
            output_bits=len(output),output_sha256=sha256(output).hexdigest(),
            source_semantic=case['semantic'],source_oracle=case['oracle'],
            root_error_squared_sha256=case['root_error_squared_sha256'],
            calls=dict(owner.full_calls),scalar_calls=delta,scalar_products=owner.arithmetic.products,
            base_recursion=dict(word.base.calls),unused_ring_calls=dict(word.product.calls),
            physical_tape_actions=difference(after_actions,before_actions),
            native_fixture_calls=dict(root.calls),native_fixture_visits=dict(visits),
            source_H_fixture='retained standard q2 native fixture; complete H boundary, not production GL64',
            floor_certificates=[dict(n=n,numerator=a,denominator=b,result=v,calls=uses[(a,b,n)])
                                for (a,b,n),v in sorted(table.items())],
            nested_alias_controls=len(aliases),private_tapes=len(owner.private),
            nested_protected_return=child_protected,final_protected_return=protected,
            successful_parent_after_child_control=True,actual_elapsed_seconds=elapsed)
        returned.clear();erase_marker(returned)
        owner.idle();scalar_clean(word)
        return result
    finally:
        if owner.output.read()!=BLANK:
            owner.output.clear();erase_marker(owner.output)
        prepared.close();payload.clear();erase_marker(payload)


def fast_complex(diagnostics,progress=False):
    from cardinal_counts import Count
    from check_support import bits,no_decode
    import check_composed
    from join_engine import FastFullPhysical
    from ring_words import Signed
    from session import borrowed_tape,erase_marker,sealed_constructors
    root,_=check_composed.fixture('standard',False)
    events=Observations()
    owner=FastFullPhysical(root,base_bits=2,
                           observe=(lambda event:events.update([event])) if diagnostics else None)
    # (-3+i)(2+i)=-7-i; both final component divisions discard a nonzero bit.
    parts=(Signed(Count.literal(3),True),Signed(Count.literal(1)),
           Signed(Count.literal(2)),Signed(Count.literal(1)))
    widths=tuple(Count.literal(x) for x in (3,1,3,7))
    borrowed=tuple(x.magnitude.tape for x in parts)+tuple(x.tape for x in widths)
    before=saved(borrowed)
    # The retained internal product method is called only after its actual
    # parent's ordinary entry initializes the erased pool markers.
    owner.rearm()
    meter_list=meters((*owner.private,*borrowed))
    initial_actions=actions(meter_list)
    output=None
    start=time.monotonic()
    try:
        with sealed_constructors(),owner.scope.installed():
            try:
                output=owner.pool.acquire()
                with no_decode():
                    owner.product(parts[:2],parts[2:],*widths,output,'fast_complex')
                final_actions=actions(meter_list)
                output.rewind()
                actual=bits(borrowed_tape(output))
                need(actual==check_composed.encode([(-3,0)],3),
                     'actual inherited complex service, signed exact products and final rounding')
                need(saved(borrowed)==before,'fast complex borrowed preservation')
                owner.idle();scalar_clean(owner.word)
                if diagnostics:
                    need(owner.word.calls==dict(base=0,fft=4)
                         and owner.arithmetic.products==4
                         and owner.word.product.arithmetic.products==4*352,
                         'four genuine FFT scalar calls inside inherited Full product')
                else:
                    need(all(value==0 for parent in (owner,owner.word,owner.word.base,
                              owner.word.product,owner.word.product.word) for value in parent.calls.values())
                         and owner.arithmetic.products==owner.word.product.arithmetic.products==0,
                         'all scalar/wrapper passive diagnostics erased')
                result=dict(marker='PASS_FAST_FULL_COMPLEX',fixture_cutoff=2,width=3,fractional_bits=1,
                    input=[[-3,1],[2,1]],exact_numerator=[-7,-1],rounded=[-3,0],
                    nonzero_component_truncations=2,output_bits=len(actual),
                    output_sha256=sha256(actual).hexdigest(),diagnostics_enabled=diagnostics,
                    scalar_calls=dict(owner.word.calls),ring_calls=dict(owner.word.product.calls),
                    inner_word_calls=dict(owner.word.product.word.calls),
                    inner_exact_products=owner.word.product.arithmetic.products,
                    physical_tape_actions=difference(final_actions,initial_actions),
                    source_method='physical_engine.FullPhysical.product (same function object)',
                    actual_elapsed_seconds=time.monotonic()-start)
                if progress:
                    print('Fast complex completed, diagnostics='+str(diagnostics),file=sys.stderr,flush=True)
                return result
            finally:
                if output is not None:output.clear()
                owner.pool.empty()
    finally:
        for value in parts:value.close()
        for value in widths:value.close()
        for tape in owner.pool.tapes:erase_marker(tape)
        owner.output.clear();erase_marker(owner.output)
        owner.closed=True


def run(progress=False):
    cold=cold_controls()
    case=source_case()
    with opened() as state:
        binding=method_binding()
        full=full_run(case,progress)
        if progress:
            print('Complete Full passed in '+str(full['actual_elapsed_seconds'])+' seconds',file=sys.stderr,flush=True)
        fast=fast_complex(True,progress)
        erased=fast_complex(False,progress)
        need(fast['output_sha256']==erased['output_sha256']
             and fast['physical_tape_actions']==erased['physical_tape_actions'],
             'passive observer erasure preserves the entire physical complex trace')
        return dict(marker='PASS_FULL_FFT_SCALAR_JOIN',inherited_methods=binding,
                    authenticated_imports=state.authenticated_imports,cold_controls=cold,
                    full=full,fast=fast,erased=erased,no_new_kappa=True)
