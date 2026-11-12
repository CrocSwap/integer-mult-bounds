"""Bounded source-executing restart checks; finite evidence, not a proof kernel."""
from pathlib import Path
import json
import sys

# Load source bytes explicitly, also under -I/-B; do not consume cached bytecode.
_scope = {'__file__': str(Path(__file__).with_name('checks.py')), '__name__': 'checks'}
exec(compile(Path(__file__).with_name('checks.py').read_bytes(), _scope['__file__'], 'exec'), _scope)
globals().update({k: v for k, v in _scope.items() if not k.startswith('__')})


def observe_call(m, owner, source, fields, moduli, widths, reverse, initial, maxima):
    ids = tuple(id(p.cells) for p in owner.ports)
    meter_ids = tuple(id(p.meter) for p in owner.ports)
    old_lengths = tuple(len(p.cells) for p in owner.ports)
    before = actions([source, *owner.ports])
    original_source, original_id = bytes(source.cells), id(source.cells)
    allowed = set().union(*map(set, fields))
    trace = list(schedule(len(moduli), reverse))
    expected = values(source, fields)
    index, meters, precisions = 0, [], []
    rearm_actions = 0
    take = owner._take
    def observed_take(words):
        nonlocal rearm_actions
        at = actions(owner.ports)
        out = take(words)
        rearm_actions += actions(owner.ports)-at
        return out
    owner._take = observed_take
    try:
        with sealed(m):
            endpoint = owner.start(source, reverse)
            stage = endpoint.stage
            def observed_stage(lease):
                nonlocal index, expected
                need(index < len(trace), 'no extra runtime node')
                start, half = trace[index]
                precision = 1+sum(widths[start:start+2*half])
                need(values(source, fields) == expected, 'committed actual current source')
                expected = node_oracle(moduli, expected, start, half, reverse)
                precisions.append(precision)
                for guard in endpoint.iterator.guards:
                    need(guard.cells[:precision+2] == bytearray([m.w.LEFT]+[m.w.ZERO]*precision+[m.w.RIGHT]),
                         'new exact guard precision')
                    need(all(x == m.w.BLANK for x in guard.cells[precision+2:]),
                         'all older guard history blank')
                state = bytes(source.cells), source.head
                stage(lease)
                need((bytes(source.cells), source.head) == state, 'staging borrows source read-only')
                meters.append(lease.actual.context.arena.meter)
                index += 1
            endpoint.stage = observed_stage
            endpoint.run()  # Only the real encoded frontend drives traversal.
            at = actions(owner.ports)
            owner.finish()
            finish_actions = actions(owner.ports)-at
    finally:
        owner._take = take
    need(index == len(trace), 'all actual nodes visited')
    need(rearm_actions == 80 and finish_actions == 316, '396 paid restart boundary actions')
    need(values(source, fields) == expected, 'defining-congruence endpoint')
    need(source.head == 1 and id(source.cells) == original_id, 'same physical source and head')
    need(len(source.cells) == len(original_source) and
         all(source.cells[i] == x for i, x in enumerate(original_source) if i not in allowed),
         'all source metadata and historical tail preserved')
    need(tuple(id(p.cells) for p in owner.ports) == ids, 'same 79 backing identities')
    need(tuple(id(p.meter) for p in owner.ports) == meter_ids, 'meters never reset')
    need(all(len(p.cells) >= n for p, n in zip(owner.ports, old_lengths)), 'no history shortening')
    need(blank(m, owner.ports), 'all 79 full histories retired')
    need(not owner.active and not owner.bank.busy and owner.current is None, 'whole inventory available')
    a, d = sum(widths), len(widths)
    maxima[0], maxima[1] = max(maxima[0], a), max(maxima[1], d)
    envelope = role_envelope(*maxima)
    need(len(envelope) == 79, 'complete role envelope')
    need(all(len(p.cells) <= max(k, r) for p, k, r in zip(owner.ports, initial, envelope)),
         'per-role complete historical envelope')
    volume = 2+3*a+4*d
    raw_bound = 396+2**19*(volume+2)**2+4096
    raw_bound += sum(2**21*(p+2)**4+2**16*(p+2)**2+4096 for p in precisions)
    work = actions([source, *owner.ports])-before
    work += sum(x.reads+x.writes+x.moves for x in meters)
    need(work <= raw_bound, 'full source-operation envelope')
    protected = sum(p.cells.origin if isinstance(p.cells, ShiftedCells) else 0
                    for p in owner.ports)
    return {'reverse': reverse, 'axes': d, 'width_sum': a, 'precisions': precisions,
            'nodes': index, 'actions': work, 'raw_bound': raw_bound,
            'retained_private': protected+sum(len(p.cells) for p in owner.ports),
            'private_bound': protected+sum(max(k, r) for k, r in zip(initial, envelope)),
            'output': list(expected)}


def exercise_sequence(m, specs, supplied=False, translated=False):
    source = m.e.Port(m.w)
    supplied_ports = None
    if supplied:
        supplied_ports = tuple(m.e.Port(m.w) for _ in range(79))
        for i, p in enumerate(supplied_ports):
            p.retire()
            p.cells.extend([m.w.BLANK]*(7+(i*19)%71))
    if translated:
        need(supplied_ports is not None, 'translated fixtures are preowned admission states')
        for i, p in enumerate([source, *supplied_ports]):
            prefix = bytearray((m.w.LEFT, m.w.RIGHT, m.w.ONE, m.w.ZERO)[j % 4]
                               for j in range(1+(7*i)%17))
            p.cells = ShiftedCells(p.cells, prefix)
    before_acquisition = actions(supplied_ports) if supplied_ports else 0
    owner = acquire(m, supplied_ports)
    acquisition = actions(owner.ports)-before_acquisition
    need(acquisition == (316 if supplied else 1264), 'paid initial acquisition and validation')
    prefixes = [bytes(p.cells.data[:p.cells.origin]) for p in [source, *owner.ports]] if translated else []
    initial = tuple(len(p.cells) for p in owner.ports)
    maxima, receipts = [0, 0], []
    stable = tuple(id(p.cells) for p in owner.ports)
    for moduli, widths, values_in, directions in specs:
        fields = fixture(m, source, moduli, widths, values_in, 29)
        original = values(source, fields)
        for direction in directions:
            receipts.append(observe_call(m, owner, source, fields, moduli, widths,
                                         direction, initial, maxima))
            need(tuple(id(p.cells) for p in owner.ports) == stable, 'one inventory across all inputs')
            if translated:
                need([bytes(p.cells.data[:p.cells.origin]) for p in [source, *owner.ports]] == prefixes,
                     'hostile physical left prefixes preserved')
        if tuple(directions) in ((False, True), (True, False), (False, True, True, False)):
            need(values(source, fields) == original, 'same-inventory round trip')
    protected = sum(p.cells.origin if isinstance(p.cells, ShiftedCells) else 0
                    for p in owner.ports)
    return {'supplied_clean_history': supplied, 'translated_origins': translated,
            'protected_private_left_backing': protected,
            'initial_private_backing': protected+sum(initial),
            'acquisition_actions': acquisition, 'max_width_sum': maxima[0],
            'max_axes': maxima[1], 'calls': receipts, 'roles': 79}


def controls(m):
    labels = []
    def rejects(label, action, message):
        try:
            action()
        except ValueError as error:
            need(message in str(error), 'specific rejection '+label+': '+str(error))
            labels.append(label)
        else:
            raise ValueError('undetected negative control '+label)
    def setup(cls=None):
        owner = acquire(m, cls=cls)
        source = m.e.Port(m.w)
        fields = fixture(m, source, (3,5), (2,3), (1,1), 19)
        return owner, source, fields
    owner, source, fields = setup()
    endpoint = owner.start(source)
    rejects('restart_while_traversal_active', lambda: owner.start(source), 'must finish')
    rejects('finish_before_full_traversal', owner.finish, 'must retire')
    lease = endpoint.iterator.next()
    endpoint.stage(lease)
    lease.close()
    rejects('finish_before_source_commit', owner.finish, 'must retire')
    endpoint.commit()
    owner.finish()
    rejects('double_finish', owner.finish, 'one active')
    rejects('non_boolean_direction', lambda: owner.start(source, 1), 'finite direction')
    rejects('source_aliases_private_role', lambda: owner.start(owner.ports[64]), 'source disjoint')
    rejects('incomplete_supplied_inventory', lambda: acquire(m, owner.ports[:-1]), 'complete supplied')
    bad = (*owner.ports[:78], owner.ports[0])
    rejects('aliased_supplied_inventory', lambda: acquire(m, bad), '79 distinct')
    port = owner.ports[68]
    port.cells[0] = m.w.LEFT
    rejects('supplied_unretired_marker', lambda: acquire(m, owner.ports), 'initial retired role marker')
    port.cells[0] = m.w.BLANK
    class MissingMarker(m.restart.Restart):
        def _take(self, words):
            p = super()._take(words)
            p.step(-1); p.write(words.BLANK); p.step(1)
            return p
    wrong, src, _ = setup(MissingMarker)
    rejects('omitted_rearm_marker', lambda: wrong.run(src), 'unit local movement')
    class FreshRole(m.restart.Restart):
        def _take(self, words):
            self.e.Port(words)
            return super()._take(words)
    wrong, src, _ = setup(FreshRole)
    with sealed(m):
        rejects('hidden_fresh_port_on_restart', lambda: wrong.run(src), 'new role')
    class WrongDirection(m.restart.Restart):
        def start(self, source, reverse=False):
            return super().start(source, False)
    wrong, src, f = setup(WrongDirection)
    initial = tuple(len(p.cells) for p in wrong.ports)
    rejects('wrong_inverse_provider', lambda: observe_call(m,wrong,src,f,(3,5),(2,3),True,initial,[0,0]),
            'defining-congruence endpoint')
    # A dirty hidden tail is outside admission: demonstrate that it cannot
    # be inferred clean from two local blank observations at restart.
    owner, src, f = setup()
    owner.run(src)
    victim = owner.ports[0]
    victim.cells.extend([m.w.BLANK]*80+[m.w.ONE])
    owner.run(src, True)
    rejects('outside_contract_dirty_tail_detected_by_observer',
            lambda: need(blank(m,owner.ports), 'whole-history blank contract'), 'whole-history blank')
    # These two small abstract histories witness why max-of-total footprints
    # is not a general retained-space theorem.
    rows = ((9,1),(1,9))
    rejects('max_of_totals_undercharges_distinct_role_histories',
            lambda: need(sum(max(x[i] for x in rows) for i in range(2)) <= max(map(sum,rows)),
                         'sum of per-role historical maxima'), 'per-role historical')
    return labels


def main():
    source_count = authenticate()
    m = modules()
    for module in (m.f, m.writer, m.inv):
        poison(module)
    pair = [((3,5),(2,3),(a,b),(False,True,True,False))
            for a in range(4) for b in range(8)]
    four = [((2,3,5,7),(2,2,3,3),x,(False,True,True,False))
            for x in ((0,0,0,0),(1,2,4,6),(1,1,1,1),(3,2,4,6),
                      (1,3,1,1),(3,3,7,7),(0,1,0,0),(0,1,2,1))]
    grow = [
        ((3,5),(2,3),(3,7),(False,True)),
        ((2,3,5,7,11,13,17,19),(4,4,4,4,5,5,5,5),(1,2,3,4,5,6,7,8),(True,False)),
        ((2,3,5,7),(2,2,3,3),(1,3,1,1),(False,True)),
        ((4,9),(3,4),(7,15),(True,False)),
        ((2,3,5,7),(4,4,5,5),(15,4,31,30),(True,False)),
        ((2,3,5,7,11,13,17,19),(5,5,5,5,5,5,5,5),(31,2,3,4,31,6,7,8),(False,True)),
        ((3,5),(2,3),(1,2),(True,False)),
    ]
    sequences = [exercise_sequence(m,pair), exercise_sequence(m,four),
                 exercise_sequence(m,grow,True,True)]
    result = {'status':'PASS_ENCODED_CRT_PERSISTENT_RESTART','source_count':source_count,
              'sequences':sequences,'controls':controls(m),'new_kappa':None,
              'scope':'successful 79-role source-relative restart; no arbitrary dirty-tail cleanup'}
    result['calls'] = sum(len(s['calls']) for s in sequences)
    result['nodes'] = sum(c['nodes'] for s in sequences for c in s['calls'])
    rendered = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write-result' in sys.argv:
        (HERE/'RESULT.json').write_text(rendered)
    else:
        need(rendered == (HERE/'RESULT.json').read_text(), 'frozen exact receipt')
    print(result['status'], 'calls='+str(result['calls']), 'nodes='+str(result['nodes']),
          'roles=79', 'controls='+str(len(result['controls'])))


if __name__ == '__main__':
    main()
