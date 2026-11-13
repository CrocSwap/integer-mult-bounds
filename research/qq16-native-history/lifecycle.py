# SPDX-License-Identifier: Apache-2.0
"""Read-only successful-return lifecycle oracle; never a runtime state reset.

Snapshots inspect host objects for finite evidence. No predicate here is charged
as a machine instruction or offered as proof that escaped aliases do not exist.
"""
from copy import deepcopy

ARENAS = ('outer.body', 'outer.high', 'outer.remainder', 'outer.indices',
          'runtime.residues', 'runtime.indices')

def need(value, why):
    if not value:
        raise ValueError(why)

def arenas(engine):
    result = tuple(engine.banks) + (engine.runtime.arena, engine.runtime.indices)
    need(len(result) == 6 and len({id(x) for x in result}) == 6,
         'six distinct native numerical arenas')
    return tuple(zip(ARENAS, result))

def tape_snapshot(tape):
    return {'head': tape.head, 'cells': list(tape.cells),
            'backing_cells': len(tape.cells)}

def snapshot(engine):
    """Observer only, valid at any cut; validation is a separate operation."""
    banks = []
    for name, bank in arenas(engine):
        banks.append({'name': name, 'capacity': bank.capacity,
                      'available': list(bank.available), 'live': sorted(bank.live),
                      'initialized': bank.initialized,
                      'words': [dict(slot=w.slot, **tape_snapshot(w.tape))
                                for w in bank.words],
                      'template': tape_snapshot(bank.template.tape)})
    runtime = engine.runtime
    return {'arenas': banks, 'closed': engine.closed,
            'runtime_closed': runtime.closed,
            'scope_active': engine.scope.manager is not None,
            'outer_leases': sorted(engine.pool.live),
            'runtime_leases': sorted(runtime.pool.live),
            'output': tape_snapshot(engine.output),
            'runtime_output': tape_snapshot(runtime.output),
            'codec': {'state': runtime.numerical.machine.state,
                      'heads': list(runtime.numerical.machine.heads),
                      'tapes': [dict(t) for t in runtime.numerical.machine.tapes]},
            'owned_roles': [tape_snapshot(t) for t in
                (*engine.pool.tapes, *runtime.roles.values(),
                 *runtime.handoff.values(), *runtime.pool.tapes)]}

def _blank(tape, *, marker=False):
    from words import BLANK, LEFT
    need(tape['head'] == 1, 'closed physical head at one')
    need(tape['backing_cells'] == len(tape['cells']), 'literal retained backing')
    need(len(tape['cells']) >= 1, 'origin cell exists; unvisited body is implicit blank')
    need(all(x == BLANK for x in tape['cells'][1:]), 'no remaining numerical or payload body')
    need(tape['cells'][0] in ((LEFT, BLANK) if marker else (BLANK,)),
         'closed owned origin marker')

def validate_closed(state):
    """Validate a consumed *successful outer* Ordinary return snapshot.

    Ownership of all six arenas and absence of escaped Word handles are caller
    premises, not properties inferred from this snapshot.
    """
    need(state['closed'] and state['runtime_closed'], 'completed outer and native root session')
    need(not state['scope_active'], 'no installed outer allocation scope')
    need(not state['outer_leases'] and not state['runtime_leases'], 'no live scratch leases')
    need(tuple(a['name'] for a in state['arenas']) == ARENAS, 'all six exact arena names')
    for arena in state['arenas']:
        n = arena['capacity']
        need(type(n) is int and n > 0, 'fixed positive inventory')
        need(not arena['live'] and not arena['initialized'], 'closed numerical residents and template')
        need(len(arena['words']) == n and
             [w['slot'] for w in arena['words']] == list(range(n)), 'stable physical slot identities')
        need(len(arena['available']) == n and set(arena['available']) == set(range(n)),
             'complete duplicate-free free-slot partition')
        for word in arena['words']:
            _blank(word)
        _blank(arena['template'])
    _blank(state['output'], marker=True)
    _blank(state['runtime_output'])
    for tape in state['owned_roles']:
        _blank(tape)
    codec = state['codec']
    need(codec['state'] == 'done' and codec['heads'] == [0, 1] and codec['tapes'] == [{}, {}],
         'closed dictionary codec state and exact heads')
    return {'status': 'PASS_CLOSED_SIX_ARENA_BOUNDARY', 'arenas': 6,
            'available_orders_need_not_be_canonical': True,
            'no_escaped_word_handles_is_owner_premise': True}

def validate_preserved(before, after):
    """Borrowed bytes and heads; backing may only grow by blank tail visits."""
    from words import BLANK
    need(before['head'] == after['head'], 'borrowed head restored')
    n = len(before['cells'])
    need(after['cells'][:n] == before['cells'] and
         all(x == BLANK for x in after['cells'][n:]), 'borrowed symbols restored')
    need(after['backing_cells'] >= before['backing_cells'], 'borrowed high-water backing retained')
    return True

def backing_monotone(before, after):
    """Per physical slot, not a current-live sum or a whole-engine space bound."""
    need(tuple(a['name'] for a in before['arenas']) == ARENAS and
         tuple(a['name'] for a in after['arenas']) == ARENAS, 'same six arenas')
    total_before = total_after = 0
    for a, b in zip(before['arenas'], after['arenas']):
        need(a['capacity'] == b['capacity'], 'no replacement numerical inventory')
        for x, y in zip(a['words'] + [a['template']], b['words'] + [b['template']]):
            need(y['backing_cells'] >= x['backing_cells'], 'erasure does not reclaim historical backing')
            total_before += x['backing_cells']; total_after += y['backing_cells']
    return {'before_numerical_cells': total_before, 'after_numerical_cells': total_after,
            'scope': 'six preallocated numerical arenas and templates only'}

def rejection_controls(valid):
    """Mutated *receipts*, not claimed reachable histories or machine repairs."""
    validate_closed(valid)
    rejected = []
    cases = ('one_arena_only', 'live_resident', 'initialized_template',
             'live_scratch_lease', 'active_scope', 'protected_output',
             'stale_slot_encoding', 'stale_codec_state', 'wrong_codec_head',
             'wrong_word_head', 'false_free_partition', 'backing_undercount')
    for name in cases:
        s = deepcopy(valid)
        if name == 'one_arena_only': s['arenas'] = s['arenas'][:1]
        elif name == 'live_resident': s['arenas'][5]['live'] = [0]
        elif name == 'initialized_template': s['arenas'][4]['initialized'] = True
        elif name == 'live_scratch_lease': s['runtime_leases'] = [0]
        elif name == 'active_scope': s['scope_active'] = True
        elif name == 'protected_output': s['output']['cells'][1] = 1
        elif name == 'stale_slot_encoding': s['codec']['tapes'][1] = {1: '0', 2: '$'}
        elif name == 'stale_codec_state': s['codec']['state'] = 'push'
        elif name == 'wrong_codec_head': s['codec']['heads'][0] = 1
        elif name == 'wrong_word_head': s['arenas'][3]['words'][0]['head'] = 2
        elif name == 'false_free_partition': s['arenas'][2]['available'][0] = s['arenas'][2]['available'][1]
        else: s['arenas'][1]['words'][0]['backing_cells'] -= 1
        try: validate_closed(s)
        except ValueError: rejected.append(name)
        else: raise ValueError('accepted lifecycle receipt mutation: ' + name)
    return {'status': 'PASS_LIFECYCLE_REJECTION_CONTROLS', 'rejected': rejected,
            'scope': 'checker mutation controls; no reachable-history or paid-reset claim'}


def first_use_marker_potential(slots, *, completed_calls):
    """Exact controller-only potential; native primitive history is separate.

    One fresh original C backend with at least one successful complete call,
    no discard/reconstruction between calls, and each output consumed under the
    fixed-copy or proved adopted-return adapter. The witness is source origin
    handling, not an invoice for the complete backend body.
    """
    need(type(slots) is int and slots > 0, 'positive fixed original packet inventory')
    need(type(completed_calls) is int and completed_calls > 0,
         'nonempty successful backend invocation epoch')
    return {'reads': 0, 'writes': slots - 1, 'moves': 0,
            'bank_first_marker_writes': slots, 'first_output_marker_credit': 1,
            'paid_once_per_backend_epoch': True,
            'scope': 'fresh versus warmed original complex controller marker state only'}


def marker_potential_control():
    """Actual authenticated Tape/origin/arm_empty counters, reduced+704 roles.

    Constructors and preparation happen outside the measured local interval.
    Their complete construction/retirement bill is retained by the comparison.
    """
    from records import Tape
    from machine import origin
    from bank_packets import arm_empty
    from session import erase_marker
    from words import LEFT
    rows = []
    for slots in (1, 2, 704):
        for touch in (origin, arm_empty):
            cold = tuple(Tape() for _ in range(slots + 1))
            warm = tuple(Tape() for _ in range(slots + 1))
            for tape in cold[:-1]: erase_marker(tape)
            erase_marker(warm[-1])
            def totals(roles):
                return tuple(sum(getattr(t.meter, k) for t in roles)
                             for k in ('reads', 'writes', 'moves'))
            def run(roles):
                initial = totals(roles)
                for tape in roles[:-1]: touch(tape)
                origin(roles[-1])
                final = totals(roles)
                need(all(t.head == 1 and t.cells[0] == LEFT for t in roles),
                     'first touch joins identical physical marker/head state')
                return tuple(x - y for x, y in zip(final, initial))
            a, b = run(cold), run(warm)
            delta = [x - y for x, y in zip(a, b)]
            need(delta == [0, slots - 1, 0], 'literal cold-minus-warm marker potential')
            rows.append({'slots': slots, 'packet_first_touch': touch.__name__,
                         'cold_actions': list(a), 'warm_actions': list(b), 'delta': delta})
    rejected = []
    for name, kwargs in [('zero_calls', {'slots': 704, 'completed_calls': 0}),
                         ('empty_inventory', {'slots': 0, 'completed_calls': 1}),
                         ('boolean_inventory', {'slots': True, 'completed_calls': 1})]:
        try: first_use_marker_potential(**kwargs)
        except ValueError: rejected.append(name)
        else: raise ValueError('accepted marker-potential domain mutation: ' + name)
    return {'status': 'PASS_SOURCE_FIRST_USE_MARKER_POTENTIAL', 'cases': rows,
            'production_controller_potential': first_use_marker_potential(704, completed_calls=1),
            'rejected': rejected,
            'scope': 'literal marker subtrace calibration and written whole-epoch induction; not production payload execution'}
