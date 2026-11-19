"""Check the 48-call caller and bind it to a verified native carrier. Apache-2.0."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json

from closed_caller import CALLS, placement, templates
from supplier_gate import gate
from mixed_application import ordinary_for_batch, reject
from mixed_caller import instructions, layout_bindings, need
from mixed_geometry import contact_atlas, masks_and_contacts
from mixed_grid import census, envelope, exact


def main_boundary(graph, layout):
    frames = graph['frames']
    first, last = graph['initial'], graph['final']
    need(frames == layout['frames'] and len(first) == len(last) == layout['public'], 'public carrier interface')
    ports, live, hosted = layout['ports'], layout['live'], layout['hosted']
    need(len(ports) == len(live) == len(set(ports)) == 104, 'complete carrier port table')
    for x, q in zip(live, ports, strict=True):
        y = x + 112
        y_axes = frames[last[y]]
        need((frames[first[x]], frames[first[y]], frames[last[x]]) ==
             ([q], [], [1 << j for j in range(9)]), 'complete primary X and incoming Y charts')
        span = {0}
        for axis in y_axes:
            span |= {v ^ axis for v in span}
        need(len(y_axes) == 8 and span == {v for v in range(512) if (v & q).bit_count() % 2 == 0},
             'full Y complement space')
    for i, x, y in zip(hosted['Dports'], hosted['X2'], hosted['Y2'], strict=True):
        need(all(boundary[u] == boundary[v] for boundary in (first, last)
                 for u, v in ((live[i], x), (live[i] + 112, y))), 'secondary carrier charts')


def readback(words, roots, bindings, offsets):
    """Compare each row of the emitted batch with the signed input words."""
    owners = {start + i: root for root, start in offsets.items() for i in range(len(words[root[0]][1]))}
    positions = dict.fromkeys(roots, 0)
    counts = Counter()
    digest = sha256()
    native = 0
    state = 'ENTER'

    def consume(root, row):
        position = positions[root]
        need(words[root[0]][0][position] == row, 'literal signed caller instruction')
        positions[root] += 1

    for row in instructions(words, roots, bindings, offsets):
        digest.update(json.dumps(row, separators=(',', ':')).encode())
        op, *args = row
        counts[op] += 1
        if op == 'PORT_VIEWS':
            direction, t, ports = args
            need(direction == state and t == native - int(direction == 'EXIT')
                 and ports == [bindings[t][p] for p in range(104)], 'actual numerical port views')
            state = 'NATIVE' if direction == 'ENTER' else 'ENTER'
        elif op == 'NATIVE':
            t, color, ports = args
            need(state == 'NATIVE' and (t, color, len(ports)) == (native, native % 16, 104),
                 'chronological physical native call')
            for port, regs in enumerate(ports):
                root = owners[regs[0]]
                need(all(owners[r] == root for r in regs), 'single root on a physical port')
                slot = roots[root].index((t, port))
                kind = 'HOST_A' if len(regs) == 4 else 'HOST_B'
                consume(root, [kind, slot, *[r - offsets[root] for r in regs]])
            native += 1
            state = 'EXIT'
        else:
            need(state == 'ENTER', 'caller works in the restored view')
            root = owners[args[0]]
            args[0] -= offsets[root]
            if op in ('ADD', 'QUERY', 'SWAP'):
                need(owners[args[1]] == root, 'private ordinary source')
                args[1] -= offsets[root]
            if op.startswith('IDLE_'):
                colors = [t % 16 for t, _ in roots[root]]
                args[1] = [colors.index(color) for color in args[1]]
            consume(root, [op, *args])
    need(native == CALLS and state == 'ENTER' and all(positions[r] == len(words[r[0]][0]) for r in roots),
         'all emitted rows consumed')
    return dict(events=sum(counts.values()), op_counts=dict(counts), event_stream_sha256=digest.hexdigest())


def verify_caller(caller, graph, layout, phase_bases):
    main_boundary(graph, layout)
    words, roots = templates(caller), placement(caller)
    bindings, offsets, owners = layout_bindings(words, roots, layout, CALLS)
    counts = owners['template_roots']
    need(counts == {'A': 120, 'rotated': 192}, 'finite root census')
    paid, targets, geography = masks_and_contacts(words, roots, offsets, contact_atlas(layout, phase_bases))
    uses, listed_paid, listed_targets = Counter(), Counter(), Counter()
    extra = negative = 0
    rows, bounds = {}, {}
    coefficients = set()
    for name, (events, outputs) in words.items():
        record = exact(events, outputs, 2025 << 9)
        minimum = record['minimum_grid']
        need(exact(events, outputs, minimum) == record, 'exact minimum grid')
        try:
            exact(events, outputs, minimum // 2)
        except ValueError as error:
            need(str(error) in ('inexact separate Gaussian component', 'inexact caller pre-product'),
                 'half-grid rejection')
        else:
            raise ValueError('half grid accepted')
        pos = next(i for i, row in enumerate(events) if row[0] == 'ADD')
        bad = events.copy()
        bad[pos] = [*bad[pos][:-1], ['0', '0']]
        reject(lambda: exact(bad, outputs, minimum), 'signed diagonal endpoint')
        t, p, u, literals = census(events, outputs)
        if name == 'rotated':
            need(t == Counter({129: 2, **{r: 4 for r in range(17, 66, 8)}}) and
                 p == Counter({r: 4 for r in range(8, 57, 8)}), 'rotated signed profile')
        weight = counts[name]
        for total, local in ((listed_targets, t), (listed_paid, p), (uses, u)):
            total.update({k: v * weight for k, v in local.items()})
        extra += weight * literals
        negative += weight * sum(q < 0 for q, _ in outputs)
        rows[name] = record
        bounds[name] = envelope(events, len(outputs))
        coefficients.update(Fraction(x) for op, *args in events if op in ('ADD', 'SCALE') for x in args[-1])
    need(listed_paid == paid and listed_targets == targets and uses['LAMBDA'] == geography['canonical_normalizers'],
         'matching physical and symbolic caller invoices')
    bad_roots = dict(roots)
    first = next(iter(bad_roots))
    bad_roots[first] = [bad_roots[first][0], *bad_roots[first]]
    reject(lambda: layout_bindings(words, bad_roots, layout, CALLS), 'independent root colors')
    bad_words = dict(words)
    events, outputs = bad_words['rotated']
    bad_events = events.copy()
    pos = next(i for i, row in enumerate(events) if row[0] == 'HOST_B')
    row = bad_events[pos].copy()
    row[2] = row[3]
    bad_events[pos] = row
    bad_words['rotated'] = bad_events, outputs
    reject(lambda: layout_bindings(bad_words, roots, layout, CALLS), 'signed main owner alias')
    signed = dict(calls=CALLS, root_owners=sum(targets.values()), uses=dict(uses),
                  fixed_caller_paid=dict(paid), fixed_root_targets=dict(targets), root_negative_q=negative,
                  gaussian_literal_uses=extra, odd_scale=2025, dyadic_height=9, finite_binding=owners)
    guard = dict(records=sum(uses.values()) + CALLS, stages=CALLS, uses=dict(uses),
                 binary_height_at_all_completed_cuts_and_products=max(v['height'] for v in bounds.values()),
                 binary_height_at_native_entrances=max(v['entrance_height'] for v in bounds.values()),
                 scaled_mass_at_all_cuts_and_products=str(2025 * max(Fraction(v['mass']) for v in bounds.values())),
                 scaled_mass_at_native_entrances=str(2025 * max(Fraction(v['entrance_mass']) for v in bounds.values())),
                 normalized_bound_uses_no_cancellation_or_commutation=True)
    proof = dict(template_grids=rows, template_bounds=bounds, common_head_and_masks=geography,
                 component_divisions=sum(counts[k] * r['separate_component_divisions'] for k, r in rows.items()),
                 missing_add_rejected=True, insufficient_grid_rejected=True, repeated_color_rejected=True,
                 shared_main_rejected=True, readback=readback(words, roots, bindings, offsets))
    return signed, guard, proof, coefficients


def apply(native, signed, guard, coefficients, conversion, physical, claim, tested, lower, upper, bit_cap):
    """Bind the supplied native proof and BIT cap at the selected price points."""
    weights = {}
    for side, field, fixed in (('T', 'positive_helper_ranks', 'fixed_root_targets'),
                               ('P', 'paid_native_ranks', 'fixed_caller_paid')):
        total = Counter({int(r): CALLS * n for r, n in native[field].items()})
        total.update({int(r): n for r, n in signed[fixed].items()})
        weights[side] = total
    bits = max(conversion["scalar_cases"]["coefficient_bits"],
               *(max(abs(c.numerator).bit_length(), c.denominator.bit_length()) for c in coefficients))
    need(bits <= 24, 'padded scalar component width')
    for c in coefficients:
        for k in (-127, -1, 0, 1, 19, 2**68 + 1):
            x, y = k * c.denominator, k * c.numerator
            width = max(abs(x).bit_length(), abs(y).bit_length()) + 3
            need(physical.scalar_service(x, c, width) == y, 'ordinary scalar component service')
    ordinary = ordinary_for_batch(native, signed, bits)
    # Allow one scalar service per factor on every native and caller conversion.
    scalars = ordinary["raw_scalar_incidence_allowance_before_factor_32"]
    scalars["additional_odd_factor_steps"] = (len(conversion["odd_factors"]) - 1) * ordinary["odd_conversions"]
    ordinary["scalar_services"] = 32 * sum(scalars.values())
    need(sum(weights['T'].values()) == ordinary['raw_productive_targets'] and
         sum(weights['P'].values()) == ordinary['raw_paid_positions'], 'complete physical invoice')
    compiler = gate(weights, claim, tested, lower, upper, bit_cap)
    root = physical.root_envelope({'candidate': native}, guard)
    depth = physical.check_depth_guard(root, int(compiler['H']))
    return dict(invoice={'targets': dict(weights['T']), 'paid': dict(weights['P'])}, ordinary=ordinary,
                compiler=compiler, common_root=root, depth_guard=depth, claim=claim, bracket=[lower, upper])
