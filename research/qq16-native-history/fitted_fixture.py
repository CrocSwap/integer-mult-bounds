# SPDX-License-Identifier: Apache-2.0
"""Actual fitted Ordinary execution under legal completed histories.

The reduced declared grammar is inherited unchanged from PR2899's check_engine.
It executes Ordinary.fitted and the encoded physical nested dispatcher, not the
production radix/profile selector and not a substituted arithmetic endpoint.
"""
from pathlib import Path
import sys
from hashlib import sha256
from state_model import Meter, arenas, body, need, snapshot, codec_backing


def source_fixture():
    import ordinary
    sys.path.insert(0, str(Path(ordinary.__file__).parent))
    import check_engine
    return check_engine


def make_engine():return source_fixture().fixture_engine()


def invoke(engine, width, *, fitted, shape=(1,1,1), seed=0x53):
    from records import Tape
    from cardinal_counts import Count
    from words import BLANK
    from physical_words import PhysicalArena
    prefix,gap,suffix=shape; extent=1<<width
    volume=prefix*extent*gap*extent*suffix
    payload=Tape()
    for address in range(volume):
        payload.append(((address*13) ^ (address>>3) ^ (address>>7) ^ seed) & 1)
    payload.rewind(); initial=body(payload)
    descriptors=tuple(Count.literal(v) for v in (width,prefix,gap,suffix))
    descriptor_states=[(bytes(x.tape.cells),x.tape.head) for x in descriptors]
    before=snapshot(engine)
    native_counts_before=dict(engine.runtime.counts)
    import runtime
    lifecycle=sys.modules.get('history_lifecycle') or runtime.module(
        'history_lifecycle',Path(__file__).resolve().parent/'lifecycle.py')
    life_before=lifecycle.snapshot(engine)
    pending=[]; roots=[]
    def observe(stage,padded,returned):
        if stage=='before':
            need(not pending,'one fitted root');pending.append((body(padded),padded.head));return
        saved,head=pending.pop(); expected=bytearray(len(saved))
        for address,bit in enumerate(saved):
            row,rest=divmod(address,128);first,rest=divmod(rest,32)
            middle,second=divmod(rest,4)
            rev1=((first&1)<<1)|(first>>1);rev2=((second&1)<<1)|(second>>1)
            target=((row*4+rev2)*8+middle)*4+rev1;expected[target]=bit
        need(body(returned)==expected,'actual padded native endpoint')
        need(body(padded)==saved and padded.head==head==returned.head==1,'padded borrowed preservation')
        roots.append(dict(payload_bits=len(saved),output_sha256=sha256(body(returned)).hexdigest()))
    engine.observe=observe
    names={id(bank):name for name,bank in arenas(engine)}
    allocation={name:dict(count=0,first_slots=[]) for name,_ in arenas(engine)}
    original_zero=PhysicalArena.zero
    codec_frames=[]
    codec=engine.runtime.numerical;codec_class=type(codec);original_park=codec_class.park
    original_move=codec_class._move;machine_class=type(codec.machine);original_step=machine_class.step
    def observed_move(value,*args,**kwargs):
        result=original_move(value,*args,**kwargs)
        if value is codec:codec_backing(codec)
        return result
    def observed_step(value,*args,**kwargs):
        result=original_step(value,*args,**kwargs)
        if value is codec.machine:codec_backing(codec)
        return result
    def observed_park(value,*args,**kwargs):
        selected=value is codec and len(codec_frames)<2
        slots=[sorted(bank.live) for bank in value.arenas] if selected else None
        result=original_park(value,*args,**kwargs)
        if selected:
            codec_frames.append(dict(live_slots=slots,slot_bits=list(value.slot_bits),
                heads=list(value.machine.heads),state=value.machine.state,
                tapes=[sorted(t.items()) for t in value.machine.tapes]))
        return result
    def observed_zero(bank):
        value=original_zero(bank)
        if id(bank) in names:
            row=allocation[names[id(bank)]];row['count']+=1
            if len(row['first_slots'])<32:row['first_slots'].append(value.slot)
        return value
    meter=Meter(engine,payload,*descriptors)
    PhysicalArena.zero=observed_zero;codec_class.park=observed_park
    codec_class._move=observed_move;machine_class.step=observed_step
    try:
        output=(engine.execute_plan(payload,*descriptors,source_fixture().toy_plan)
                if fitted else engine.run(payload,*descriptors))
    finally:
        PhysicalArena.zero=original_zero;codec_class.park=original_park
        codec_class._move=original_move;machine_class.step=original_step
    actions=list(meter.delta())
    expected=bytearray(volume)
    for address,bit in enumerate(initial):
        quotient,last=divmod(address,suffix);quotient,second=divmod(quotient,extent)
        quotient,between=divmod(quotient,gap);first_prefix,first=divmod(quotient,extent)
        target=((((first_prefix*extent+second)*gap+between)*extent+first)*suffix+last)
        expected[target]=bit
    need(output is engine.output,'fixed Ordinary public output identity')
    need(body(output)==expected,'nonconstant ordinary interchange')
    need(body(payload)==initial and payload.head==output.head==1,'borrowed payload/head')
    need(descriptor_states==[(bytes(x.tape.cells),x.tape.head) for x in descriptors],'borrowed encoded descriptors')
    need(engine.last_fitted is fitted and engine.closed and engine.runtime.closed,'actual branch and successful closure')
    need(len(roots)==(2 if fitted else 0) and not pending,'fitted actual root count')
    returned=snapshot(engine)
    for bank in returned['arenas']:
        need(not bank['live'] and not bank['initialized'],'empty erased six arenas')
    output_sha=sha256(body(output)).hexdigest();output.clear()
    consumed=snapshot(engine)
    life_after=lifecycle.snapshot(engine)
    lifecycle_receipt=lifecycle.validate_closed(life_after)
    backing_receipt=lifecycle.backing_monotone(life_before,life_after)
    payload.clear()
    for count in descriptors:count.close()
    return dict(width=width,shape=list(shape),seed=seed,payload_bits=volume,
        branch='fitted' if engine.last_fitted else 'fallback',actions=actions,
        roots=roots,allocation=allocation,codec_frames=codec_frames,
        native_dispatch_delta={k:v-native_counts_before[k] for k,v in engine.runtime.counts.items()},before=before,returned=returned,consumed=consumed,
        output_sha256=output_sha,borrowed_preserved=True,
        lifecycle=lifecycle_receipt,backing=backing_receipt,
        lifecycle_rejections=lifecycle.rejection_controls(life_after),output_identity_preserved=True,
        scope='Actual declared-small-grammar Ordinary.fitted and nested encoded machine; not production select admission.')


def run_discriminator():
    left,right=make_engine(),make_engine()
    warm_left=invoke(left,1,fitted=False)
    warm_right=invoke(right,2,fitted=False,shape=(1,2,1),seed=0x35)
    first=invoke(left,5,fitted=True)
    # A different nonconstant input warms actual numerical parking/slot histories.
    warm_fitted=invoke(right,5,fitted=True,seed=0x6c)
    intervening=invoke(right,2,fitted=False,shape=(2,1,2),seed=0x36)
    second=invoke(right,5,fitted=True)
    different=[a['name'] for a,b in zip(first['before']['arenas'],second['before']['arenas'])
               if a['available']!=b['available']]
    need(different and any(name.startswith('runtime.') for name in different),
         'completed fitted/fallback history changes native encoded-slot arena order')
    need(first['output_sha256']==second['output_sha256'],'same fitted semantic output')
    need(first['output_sha256']!=warm_fitted['output_sha256'],'distinct nonconstant fitted payload control')
    return dict(status='PASS_LEGAL_FITTED_HISTORY_DISCRIMINATOR',
        warm_histories=[warm_left,warm_right,warm_fitted,intervening],different_queues=different,
        fitted_pair=[first,second],delta=[b-a for a,b in zip(first['actions'],second['actions'])],
        distinct_payload_delta=[b-a for a,b in zip(first['actions'],warm_fitted['actions'])],
        classification='observed_equal_actions' if first['actions']==second['actions'] else 'observed_action_difference',
        fitted_fallback_fitted=[warm_fitted['branch'],intervening['branch'],second['branch']],
        theorem=False)
