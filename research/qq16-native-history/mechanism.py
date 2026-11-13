# SPDX-License-Identifier: Apache-2.0
"""Source-action equivariance checks; no runtime reset or queue permutation.

All reads of Python state below are checker observations. The actual numerical
and codec operations are the authenticated PR2899/PR2769 implementation.
Chris R with OpenAI Codex assistance; see MECHANISM.md for credited sources.
"""


def need(ok, why):
    if not ok:
        raise ValueError(why)


def shape(symbol):
    return 'b' if symbol in ('0', '1') else symbol


def transition_shape(table):
    """Exhaustively certify 0/1-erased control/action shape of actual TABLE."""
    classes = {}
    for state,left,right in table:
        for a in (('0','1') if left in ('0','1') else (left,)):
            for b in (('0','1') if right in ('0','1') else (right,)):
                need((state,a,b) in table,'binary counterpart transition missing')
    for (state, left, right), (nxt, writes, moves) in table.items():
        key = (state, shape(left), shape(right))
        image = (nxt, tuple(None if w is None else shape(w) for w in writes), moves)
        need(key not in classes or classes[key] == image,
             'binary values must not change literal codec control/action shape')
        classes[key] = image
    return {'transitions':len(table), 'binary_erased_classes':len(classes),
            'equal_next_state_write_presence_and_unit_moves':True}


def finite_control_bound(capacity):
    """A concrete conservative finite-control realization, NOT tape actions.

    Fixed-q role labels/live bits/available permutations are finite controller
    states. Direct transitions implement pop/push/test and indexed stable-word
    selection. Restore's remove operation is compiled from that complete finite
    state into one transition; slot decoding uses its fixed-width bit loop.
    This size allowance is a cardinality bound, not a practical compiler.
    """
    from math import factorial
    need(type(capacity) is int and capacity > 0, 'fixed positive capacity')
    # A permutation and cut position encode each ordered free list plus live
    # complement; this overcounts, intentionally. Six arenas are independent.
    one = (capacity + 1) * factorial(capacity)
    return {'capacity':capacity, 'six_arena_state_bound':one**6,
            'slot_bits':max(1,(capacity-1).bit_length()),
            'state_bits_bound':6*(one.bit_length()),
            'scope':'allocator finite-control component only; no numerical values/widths',
            'runtime_reset_sites':0, 'additional_physical_tapes':0}


def park_restore_tariff(capacities, widths, live_counts):
    """Complete successful empty-frame park/restore, no child body.

    Derivation follows every loop test/rewind/append in MECHANISM.md. The
    numerical words all start/end at origin; no protected child grants.
    """
    need(len(capacities)==len(widths)==len(live_counts)==2, "two actual codec banks")
    total=[15,2,12]
    for cap,w,m in zip(capacities,widths,live_counts):
        need(type(cap) is int and cap>0 and type(w) is int and w>0 and
             type(m) is int and 0<=m<=cap, "fixed capacity and admitted word extent")
        n=1+max(1,(cap-1).bit_length())+w
        for i,x in enumerate((14*n+10*w+32,6*n+3*w+8,12*n+10*w+30)):
            total[i]+=m*x
    return tuple(total)


def _totals(arenas, codec):
    # PhysicalWord increments both its arena observer and its Tape observer;
    # count physical Tape counters ONCE, plus both distinct dictionary counters.
    tapes = [w.tape for a in arenas for w in (*a.words,a.template)]
    return tuple(sum(getattr(t.meter,k) for t in tapes)
                 + codec.codec_counts[k] + codec.machine.counts[k]
                 for k in ('reads','writes','moves'))


def _minus(after,before):
    return tuple(x-y for x,y in zip(after,before))


def _body(word):
    from words import BLANK
    return (word.head,bytes(word.cells).rstrip(bytes([BLANK])))


def _codec_case(warm, capacity=4):
    from physical_words import PhysicalArena
    from cardinal_counts import Count
    from bank_codec import BankParking
    from words import BLANK
    arenas = (PhysicalArena(capacity), PhysicalArena(capacity))
    maximum=Count.literal(15)
    for arena in arenas:
        arena.prepare(maximum)
        if warm:
            prior=[arena.literal(i+1) for i in range(3)]
            for word in prior: arena.free(word)
    maximum.close()
    queues=tuple(tuple(a.available) for a in arenas)
    values=((3,9,6),(12,5,10))
    live=tuple(tuple(a.literal(v) for v in vv) for a,vv in zip(arenas,values))
    before_words=tuple(tuple(_body(w) for w in ws) for ws in live)
    identities=tuple(tuple(w.slot for w in ws) for ws in live)
    codec=BankParking(*arenas)
    before=_totals(arenas,codec)
    codec.park()
    child_before=_totals(arenas,codec)
    # Actual distinct child allocations may reuse suspended parent slots.
    children=tuple(a.literal(11-i) for i,a in enumerate(arenas))
    for a,w in zip(arenas,children):a.free(w)
    child_cost=_minus(_totals(arenas,codec),child_before)
    codec.restore()
    cost=_minus(_totals(arenas,codec),before)
    core=_minus(cost,child_cost)
    need(core==park_restore_tariff((capacity,capacity),(5,5),(3,3)),
         'exact source-derived complete numerical codec tariff')
    need(before_words==tuple(tuple(_body(w) for w in ws) for ws in live),
         'actual original word objects, values and heads restored')
    need(identities==tuple(tuple(w.slot for w in ws) for ws in live),
         'actual original encoded slot identities restored')
    need(codec.machine.tapes==[{}, {0:'^'}] and codec.machine.heads==[0,1]
         and codec.machine.state=='done','exact codec baseline and heads')
    for arena,ws in zip(arenas,live):
        arena.free_many(*ws)
        arena.erase_owned()
    need(all(not a.live and not a.initialized and
             all(w.head==1 and all(c==BLANK for c in w.cells)
                 for w in (*a.words,a.template)) for a in arenas),
         'successful actual numerical/template retirement')
    codec._move(1,-1);codec._write(1,'_');codec._move(1,1)
    need(codec.machine.tapes==[{},{}],'terminal codec marker retirement')
    return {'legal_warm_history':warm,'entry_free_order':[list(q) for q in queues],
            'logical_word_slot_labels':[list(q) for q in identities],
            'park_child_restore_actions':list(cost),
            'child_actions':list(child_cost),'park_restore_actions':list(core),
            'word_identity_value_head_restored':True,
            'terminal_numeric_and_codec_cleanup':True}


def checks():
    import parking_machine
    table=transition_shape(parking_machine.TABLE)
    cold,warm=_codec_case(False),_codec_case(True)
    need(cold['entry_free_order']!=warm['entry_free_order'], 'legal distinct free histories')
    need(cold['logical_word_slot_labels']!=warm['logical_word_slot_labels'],
         'different actual slot encodings')
    need(cold['park_child_restore_actions']==warm['park_child_restore_actions'],
         'matched complete codec actions despite reordered encoded slots')
    bad=dict(parking_machine.TABLE)
    nxt,writes,moves=bad[('push_copy','_','1')]
    bad[('push_copy','_','1')]=(nxt,writes,(1,0))
    try:transition_shape(bad)
    except ValueError:mutation=True
    else:raise ValueError('failed to reject bit-dependent head movement')
    missing=dict(parking_machine.TABLE);del missing[('push_copy','_','1')]
    try:transition_shape(missing)
    except ValueError:domain_mutation=True
    else:raise ValueError('failed to reject missing binary counterpart')
    control=finite_control_bound(4)
    # Huge production cardinality must be expressed symbolically, not computed.
    return {'status':'PASS_NATIVE_CODEC_EQUIVARIANCE', 'transition_shape':table,
            'cold':cold,'warm':warm,'bit_dependent_move_rejected':mutation,
            'missing_binary_counterpart_rejected':domain_mutation,
            'finite_control_example':control,
            'actual_marker_phase_control':rearm_check(),
            'runtime_mutation':'none; source allocation/free and park/restore only',
            'scope':'source-bound kernel evidence; quantified Ordinary theorem in MECHANISM.md'}


def rearm_tariff(engine, output_marker_blank):
    """Source-exact warm-entry marker bill; compile-time inventory observation."""
    need(type(output_marker_blank) is bool,'explicit consumed output marker state')
    runtime=engine.runtime
    k=(len(engine.pool.tapes)+sum(len(a.words)+1 for a in engine.banks)
       +len(runtime.roles)+len(runtime.handoff)+len(runtime.pool.tapes)+1
       +len(runtime.arena.words)+1+len(runtime.indices.words)+1)
    return {'initialized_markers':k,
            'actions':[2*k+3,k+int(output_marker_blank)+1,2*k+4],
            'includes':'Ordinary output checks, all six arenas/templates, both pools, runtime roles/handoff/output, dictionary marker',
            'excludes':'constructor and successful previous finish; no reset of available order'}


def rearm_check():
    """Actual marker-only control; this is not the fitted arithmetic witness."""
    from types import SimpleNamespace
    from ordinary import Ordinary
    from macro_code import Code
    from session import erase_marker
    from state_model import Meter
    observations=[]
    for blank in (False,True):
        engine=Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),
            SimpleNamespace(families=0),(Code((('unreachable',),),0),),capacity=4)
        engine.finish(False)
        if blank:erase_marker(engine.output)
        expected=rearm_tariff(engine,blank)
        meter=Meter(engine)
        engine.rearm()
        need(list(meter.delta())==expected['actions'],'literal six-arena rearm tariff')
        engine.finish(False);erase_marker(engine.output)
        observations.append({'output_marker_blank':blank,**expected})
    need(observations[1]['actions'][1]-observations[0]['actions'][1]==1,
         'mismatched output marker costs exactly one write')
    return {'status':'PASS_LITERAL_REARM_TARIFF','cases':observations,
            'scope':'marker and inventory control; no fitted arithmetic executed here'}
