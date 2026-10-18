"""Conditional nested-frame proof witness with actual selected Compact leaf."""
from pathlib import Path
import argparse, dataclasses, hashlib, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import HERE, load, need

def encoded(value):
    return json.dumps(value, indent=2, sort_keys=True) + '\n'

def run():
    full, native_frame, native, pins, physical, oracle = load()
    import frame as scoped
    prior = physical.prior
    # Retained PR2534 factor/oracle, repeated only to bind the nested leaf.
    reduced = {k: v for k, v in full.items() if k not in ('left', 'right')}
    for name in ('left', 'right'):
        r = full[name]
        need(r['matrix_rows'][4:] == [1 << j for j in range(4, 9)] and
             all(row < 16 for row in r['matrix_rows'][:4]) and r['offset'] < 16 and
             not any(r['linear_Z4'][4:]) and
             all(not (r['quadratic_rows'][i] >> (i+1)) for i in range(4, 9)) and
             all(not (r['quadratic_rows'][i] >> 4) for i in range(4)), 'exact four-axis factor')
        reduced[name] = {k: (v[:4] if isinstance(v, list) else v) for k, v in r.items()}
        for x in range(512):
            y, p = oracle.monomial(r, x)
            z, q = oracle.monomial(reduced[name], x % 16)
            need((y, p) == (z | (x & ~15), q), 'source monomial factor')
    single, original = oracle.columns(reduced), oracle.columns(full)
    target = native.canonical_frame(9, native_frame)
    for x, col in enumerate(original):
        vec, den = target.zero_state(x)
        need({j: (a*(2 >> den), b*(2 >> den)) for j, (a, b) in enumerate(vec) if a or b} == col,
             'native canonical operator')
        need(col == {y | (x & ~15): z for y, z in single[x % 16].items()}, 'whole selected child factor')
    cols = oracle.tensor_columns(single)
    counts = ('reads', 'writes', 'moves', 'erases')
    calls = []
    def totals(meter):
        return {k: getattr(meter, k) for k in counts}
    def checked_invoke(active, inactive, park, callee, label):
        W, S = len(active.data), sum(len(t.data) for t in inactive)
        before = totals(active.meter)
        delta = {}
        def observed(argument, child_park):
            begin = totals(argument.meter)
            output = callee(argument, child_park)
            delta.update({k: getattr(argument.meter, k)-begin[k] for k in counts})
            return output
        output, restored = scoped.invoke(active, inactive, park, observed)
        own = {k: getattr(active.meter, k)-before[k]-delta[k] for k in counts}
        expected = dict(reads=2*W+3*S, writes=2*W+3*S, moves=12*(W+S), erases=2*W+3*S)
        need(own == expected, 'exact local wrapper bill')
        calls.append({'label': label, 'active_bits': W, 'parked_bits': S, 'wrapper': own})
        return output, restored

    def nested(depth, leaf, observations):
        if not depth:
            return leaf
        def callee(argument, park):
            meter = argument.meter
            # A live foreign tape with a nonzero head belongs to this parent.
            foreign_bits = bytes((i+depth) % 2 for i in range(9+depth))
            foreign = prior.TrackingTape(meter, foreign_bits)
            foreign.read(2)
            parked_bits = bytes((i//2+depth) % 2 for i in range(5+depth))
            extent = park.push(prior.TrackingTape(meter, parked_bits))
            snapshot = (bytes(park.cells), park.head, bytes(foreign.data), foreign.head)
            packets = [bytes((i+depth) % 2 for i in range(n)) for n in (0, 3+depth, 8+depth)]
            inactive = [prior.TrackingTape(meter, x) for x in packets]
            output, restored = checked_invoke(argument, inactive, park,
                nested(depth-1, leaf, observations), 'nested-' + str(depth))
            need((bytes(park.cells), park.head, bytes(foreign.data), foreign.head) == snapshot,
                 'caller parking prefix and live tape remain unchanged')
            need([bytes(t.data) for t in restored] == packets, 'ordered dirty nested restoration')
            for t in restored:
                t.erase()
            recovered = park.pop(extent)
            need(bytes(recovered.data) == parked_bits, 'local caller parking restored')
            recovered.erase()
            foreign.erase()
            observations.append({'depth': depth, 'parent_floor': park.floor,
                                 'protected_extent': snapshot[1], 'foreign_head': snapshot[3]})
            return output
        return callee

    # The old global cleanup contract is a documented flat-caller boundary.
    inherited = {}
    old_child = prior.child
    prior.child = lambda tape, *a, **kw: tape
    try:
        for kind in ('flat', 'already_parked', 'foreign_live_tape'):
            meter = prior.Meter()
            park = prior.Park(meter, b'\1\0\1')
            if kind == 'already_parked':
                park.push(prior.TrackingTape(meter, b'\1\1\0\0\1'))
            if kind == 'foreign_live_tape':
                prior.TrackingTape(meter, b'\1\1\1\0\1\1')
            try:
                prior.invoke(prior.TrackingTape(meter, b'\0\1\0\1'),
                             [prior.TrackingTape(meter, b'\1\1\0')], park, None, None, 1, 1)
            except ValueError as error:
                inherited[kind] = str(error)
            else:
                inherited[kind] = 'PASS'
    finally:
        prior.child = old_child
    need(inherited == {'flat': 'PASS', 'already_parked': 'parking extent restored',
                       'foreign_live_tape': 'all actual working tapes cleared'}, 'inherited flat boundary')

    generic = []
    for depth, width in ((0, 0), (1, 1), (3, 37), (7, 53)):
        meter = prior.Meter()
        ancestor = b'\1\0\1\1\0'
        park = prior.Park(meter, ancestor)
        raw = bytes((i//3+i) % 2 for i in range(width))
        packets = [b'', b'\1\1\0', b'\0\1\0\1\1\0\1']
        observations = []
        before = len(calls)
        out, restored = checked_invoke(prior.TrackingTape(meter, raw),
            [prior.TrackingTape(meter, x) for x in packets], park,
            nested(depth, lambda tape, parked: tape, observations), 'generic-root')
        need(bytes(out.data) == raw and [bytes(t.data) for t in restored] == packets, 'generic nested endpoint')
        need(park.head == park.floor and park.cells == ancestor, 'generic root parking')
        for t in [out, *restored]:
            t.erase()
        need(all(not t.data and t.head == 0 for t in meter.tapes), 'generic all owned root work cleared')
        generic.append({'depth': depth, 'active_bits': width, 'calls': len(calls)-before,
                        'observations': observations})

    bits, outer, depth = 24, 1, 3
    layout = physical.layout(bits)
    values = [((i+1)*16, ((i*i+7*i) % 12289-6144)*16) for i in range(layout.records)]
    raw = prior.encode(values, bits)
    expected = oracle.apply(values, layout, cols, outer)
    meter, grid = prior.Meter(), prior.Grid(bits, 8)
    ancestor = bytes((i//2+i) % 2 for i in range(47))
    park = prior.Park(meter, ancestor)
    dirty = [bytes((i//3+i) % 2 for i in range(n)) for n in (0, 23, 113)]
    active = prior.TrackingTape(meter, raw)
    inactive = [prior.TrackingTape(meter, x) for x in dirty]
    selected_observations = []
    first_call = len(calls)
    endpoints = []
    for inverse in (False, True):
        def leaf(tape, protected):
            return physical.child(tape, reduced, grid, outer, 1, inverse)
        active, inactive = checked_invoke(active, inactive, park,
            nested(depth, leaf, selected_observations), 'selected-inverse' if inverse else 'selected-forward')
        need(prior.decode(active.data, bits) == (values if inverse else expected), 'selected nested exact endpoint')
        need([bytes(t.data) for t in inactive] == dirty and bytes(park.cells) == ancestor and park.head == park.floor,
             'selected root restoration')
        endpoints.append(hashlib.sha256(active.data).hexdigest())
    need(active.data == raw and not grid.workspace, 'selected literal inverse and arithmetic return')
    need(meter.repair_records > 0 and meter.ordinary_calls and all(c['width'] == 1 for c in meter.ordinary_calls),
         'actual completed Compact leaf dispatch')
    scientific = physical.report(meter, grid, park)
    for t in [active, *inactive]:
        t.erase()
    need(all(not t.data and t.head == 0 for t in meter.tapes) and meter.live == 0, 'selected final root cleanup')

    controls = {}
    def rejects(name, action, reason):
        try:
            action()
        except ValueError as error:
            need(str(error) == reason, 'wrong control rejection ' + name + ': ' + str(error))
            controls[name] = reason
        else:
            raise ValueError('ineffective control ' + name)
    def simple(callee):
        m = prior.Meter()
        return scoped.invoke(prior.TrackingTape(m, b'\0\1'),
             [prior.TrackingTape(m, b'\1\0\1')], prior.Park(m, b'\1\1'), callee)
    rejects('callee_pops_caller_packet', lambda: simple(lambda t, p: p.pop(1)), 'local opaque ancestor boundary')
    def leaks_park(t, p):
        p.push(prior.TrackingTape(t.meter, b'\1'))
        return t
    rejects('callee_leaves_parking', lambda: simple(leaks_park), 'local parking extent restored')
    def leaks_work(t, p):
        prior.TrackingTape(t.meter, b'\1')
        return t
    rejects('callee_leaves_work', lambda: simple(leaks_work), 'all invocation-owned working tapes cleared')
    def wrong_size(t, p):
        t.erase()
        return prior.TrackingTape(t.meter, b'\1')
    rejects('wrong_return_extent', lambda: simple(wrong_size), 'returned packet has the original extent and rewound head')
    def wrong_head(t, p):
        t.read(1)
        return t
    rejects('unrewound_return', lambda: simple(wrong_head), 'returned packet has the original extent and rewound head')
    def foreign_return():
        m = prior.Meter()
        foreign = prior.TrackingTape(m, b'\0\1')
        scoped.invoke(prior.TrackingTape(m, b'\1\0'), [], prior.Park(m, b''), lambda t,p: foreign)
    rejects('foreign_return_alias', foreign_return, 'return tape belongs to this invocation')
    m = prior.Meter()
    park = prior.Park(m, b'\1\0\1')
    view = scoped.ParkFrame(park)
    view.push(prior.TrackingTape(m, b'\0\1'))
    snapshot = (bytes(view.cells), view.head, totals(m))
    rejects('whole_extent_preflight', lambda: view.pop(3), 'local opaque ancestor boundary')
    need((bytes(view.cells), view.head, totals(m)) == snapshot, 'rejected underflow consumes nothing')
    # A raw Python mutation violates the access premise; the independent
    # boundary observer must detect it. No hostile-code isolation is claimed.
    def bad_parent(t, p):
        p.cells[0] ^= 1
        return t
    m = prior.Meter()
    park = prior.Park(m, b'\1\0\1')
    scoped.invoke(prior.TrackingTape(m, b'\0\1'), [], park, bad_parent)
    need(bytes(park.cells) != b'\1\0\1', 'effective raw mutation control')
    controls['raw_ancestor_mutation'] = 'DETECTED by independent observer; outside access premise'
    return {'status': 'PASS_SELECTED_NESTED_INVOCATION_FRAMES',
            'source_head': 'f961dcb12061c3959058aed883f48b55f365eb80',
            'inherited_flat_boundary': inherited, 'generic_cases': generic,
            'source_child': 7, 'source_events': [9394, 9396], 'native_columns': 512,
            'source_monomial_columns': 1024, 'tensor_columns': 256,
            'selected_nesting_depth': depth, 'selected_wrapper_calls': len(calls)-first_call,
            'selected_records': layout.records, 'packet_bits': len(raw),
            'bits': bits, 'fraction_bits': 8, 'initial_quantum': 16,
            'selected_endpoint_sha256': endpoints, 'selected_observations': selected_observations,
            'selected_forward_inverse_meter': scientific, 'all_local_bills': calls,
            'wrapper_bill': {'reads_writes_erases': '2W+3S', 'moves': '12(W+S)'},
            'controls': controls, 'source_members': pins,
            'scope': 'Conditional sequential finite-call-tree frame composition and exact wrapper tariff; completed selected f=2 leaf nested inside three callers, not a nonleaf C supplier, fixed-tape compiler, global hosting or new kappa.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    if args.write and args.write.exists():
        raise FileExistsError(args.write)
    saved = None if args.write else json.loads((HERE / 'RESULT.json').read_text())
    result = run()
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as f:
            f.write(encoded(result))
    else:
        need(encoded(saved) == encoded(result), 'complete receipt mismatch')
    print('PASS_SELECTED_NESTED_INVOCATION_FRAMES records=4096 depth=3 selected_calls=8 controls=8')

if __name__ == '__main__':
    main()
