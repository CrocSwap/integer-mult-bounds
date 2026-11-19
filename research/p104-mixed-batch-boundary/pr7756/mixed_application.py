"""Audit the caller, address schedule and ordinary cost of one finite batch. Apache-2.0."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json

from mixed_caller import instructions, layout_bindings, need, place_roots, split_templates
from mixed_grid import census, envelope, exact
from mixed_geometry import contact_atlas, masks_and_contacts

ODD, HEIGHT = 2025, 9


def reject(call, message):
    try:
        call()
    except ValueError as error:
        need(str(error) == message, 'unexpected control failure')
    else:
        raise ValueError('control accepted: ' + message)


def verify_caller(caller, layout, calls, legacy_signed, phase_bases):
    words = split_templates(caller)
    roots = place_roots(caller, calls)
    _, offsets, bindings = layout_bindings(words, roots, layout, calls)
    atlas = contact_atlas(layout, phase_bases)
    actual_paid, actual_targets, coordinates = masks_and_contacts(words, roots, offsets, atlas)
    counts = bindings['template_roots']
    grid = ODD << HEIGHT
    halves = {}
    profiles = {}
    signed = {}
    raw = {}
    for kind, (events, targets) in words.items():
        signed[kind] = exact(events, targets, grid)
        raw[kind] = envelope(events, len(targets))
        minimum = signed[kind]['minimum_grid']
        need(grid % minimum == 0 and exact(events, targets, minimum) == signed[kind], 'common caller grid')
        try:
            exact(events, targets, minimum//2)
        except ValueError as error:
            need(str(error) in ('inexact separate Gaussian component', 'inexact caller pre-product'),
                 'wrong insufficient-grid rejection')
        else:
            raise ValueError('insufficient grid accepted')
        k = next(i for i, e in enumerate(events) if e[0] == 'ADD')
        bad = events.copy()
        bad[k] = [*bad[k][:-1], ['0', '0']]
        reject(lambda: exact(bad, targets, grid), 'signed diagonal endpoint')
        profiles[kind] = census(events, targets)
        halves[kind] = sum(q < 0 for q, _ in targets)

    def total(column, weights):
        result = Counter()
        for kind, num in weights.items():
            result.update({r: n*num for r, n in profiles[kind][column].items()})
        return result

    old = {k: len(v['ports']) for k, v in caller['types'].items()}
    need(dict(total(0, old)) == legacy_signed['fixed_root_targets'] and
         dict(total(1, old)) == legacy_signed['fixed_caller_paid'] and
         dict(total(2, old)) == legacy_signed['uses'], 'exact inherited invoice and instruction uses')
    need(signed['A']['preproduct_divisions'] + signed['B']['preproduct_divisions'] ==
         legacy_signed['exact_preproduct_divisions'], 'independent inherited divider census')
    need(profiles['mixed'][0] == Counter({129: 2, **{r: 4 for r in range(17, 66, 8)}}) and
         profiles['mixed'][1] == Counter({r: 4 for r in range(8, 57, 8)}),
         'mixed target and whole idle profile from the actual word')

    paid, targets, uses = total(1, counts), total(0, counts), total(2, counts)
    need(actual_paid == paid and actual_targets == targets and coordinates['canonical_normalizers'] == uses['LAMBDA'],
         'literal physical-axis invoice and canonical normalizers')
    negative_q = sum(halves[k]*v for k, v in counts.items())
    extra = sum(profiles[k][3]*v for k, v in counts.items())
    census_report = dict(calls=calls, uses=dict(uses), fixed_caller_paid=dict(paid),
                         fixed_root_targets=dict(targets), root_owners=sum(targets.values()),
                         root_negative_q=negative_q, gaussian_literal_uses=extra,
                         odd_scale=ODD, dyadic_height=HEIGHT, finite_binding=bindings)
    need(census_report['root_owners'] == bindings['root_owners'], 'complete caller owners')
    guard = dict(records=sum(uses.values())+calls, stages=calls, uses=dict(uses),
                 binary_height_at_all_completed_cuts_and_products=max(v['height'] for v in raw.values()),
                 binary_height_at_native_entrances=max(v['entrance_height'] for v in raw.values()),
                 scaled_mass_at_all_cuts_and_products=str(ODD*max(Fraction(v['mass']) for v in raw.values())),
                 scaled_mass_at_native_entrances=str(ODD*max(Fraction(v['entrance_mass']) for v in raw.values())),
                 normalized_bound_uses_no_cancellation_or_commutation=True)
    copies = place_roots(caller, 32)
    first = next(iter(copies))
    bad = dict(copies)
    visits = list(bad[first])
    visits[1] = visits[0]
    bad[first] = visits
    reject(lambda: layout_bindings(words, bad, layout, 32), 'independent root colors')
    bad_words = dict(words)
    template = first[0]
    events, rr = words[template]
    bad_events = events.copy()
    k = next(i for i, e in enumerate(events) if e[0].startswith('HOST_'))
    e = events[k].copy()
    e[2] = e[3]
    bad_events[k] = e
    bad_words[template] = bad_events, rr
    reject(lambda: layout_bindings(bad_words, copies, layout, 32), 'signed main owner alias')

    proof = dict(template_grids=signed, template_bounds=raw, common_head_and_masks=coordinates, common_input_grid=grid,
                 occurrence_weighted_preproduct_divisions=sum(signed[k]['preproduct_divisions']*v
                                                              for k, v in counts.items()),
                 occurrence_weighted_component_divisions=sum(signed[k]['separate_component_divisions']*v
                                                             for k, v in counts.items()),
                 missing_add_rejected=True, insufficient_grids_rejected=True,
                 duplicate_main_rejected=True, repeated_body_color_rejected=True)
    return census_report, guard, proof


def ordinary_for_batch(native, signed, scalar_bits, ambient=153):
    """Recount the per-occurrence costs of the retained guarded-bank model for this batch."""
    stages, roots = signed['calls'], signed['root_owners']
    n, k, m, homes = (native[x] for x in ('public', 'slots', 'terms', 'numerical_homes'))
    paid = stages*k + sum(signed['fixed_caller_paid'].values())
    targets = stages*sum(native['positive_helper_ranks'].values()) + roots
    resets = 2*homes + 8*(m+k+n) + 4*n + 2*k
    transfers = 2*m + 2*(k+n) + 6*k + 4*n
    selected = native['selected_logical_operations']
    checked_reset = sum(selected[o] for o in native['fixture_addressed_cells_overwritten'])
    copies = sum(selected.values()) - checked_reset
    need(checked_reset == 2*(homes+k) and resets >= checked_reset + native['tracked_stream_reset_visits'],
         'native full overwrites and stream resets')
    need(copies == m+3*(k+n) and transfers == 2*copies+2*k, 'native staging and adapters')
    need(native['additional_independent_guarded_streams'] == 4 and homes <= 15290, 'guarded native stock')
    select_l = 14*homes+9
    select_c = 63*homes-7*homes.bit_count()+27*homes.bit_length()+59
    selections = [resets*(select_l+2)+transfers*(select_l+128),
                  resets*(select_c+3)+transfers*(select_c+320)]
    conversions = 2*(roots+stages*n)
    uses = Counter(signed['uses'])
    maps = 2*(paid+targets+stages*400) + 2*(uses['IDLE_ONE']+uses['IDLE_ODD'])
    maps += 3*uses['QUERY'] + uses['LAMBDA'] + uses['IDLE_ODD'] + signed['root_negative_q']
    complex_ops = signed.get('gaussian_literal_uses', 0)
    # The serial complex service retains the input until it has both output components.
    # Give every permutation and every phase translation its own numerical array traversal.
    port_legs = 4*400*stages
    maps += 2*complex_ops + port_legs
    scalar = dict(native_products_and_accumulations=stages*m, native_row_lifecycles=stages*4*(k+n),
                  boundary_installations=stages*2*n, private_home_flags=stages*homes,
                  sender_lifecycles=stages*2*k, caller_slots=sum(uses.values()),
                  odd_conversions=conversions,
                  extra_gaussian_component_slots=64*(complex_ops + uses['LAMBDA']))
    return dict(native_numeric_homes=homes, raw_numeric_homes=stages*homes,
                raw_numeric_homes_plus_dummy=stages*(homes+1), separate_guarded_streams_raw=4*stages,
                separate_guarded_guide_tracks_raw=stages, odd_conversions=conversions,
                reset_services_all_native_stages=stages*resets,
                typed_selected_transfer_legs_all_native_stages=stages*transfers,
                selected_total_steps_raw_L_and_constant=[stages*v for v in selections],
                raw_scalar_incidence_allowance_before_factor_32=scalar,
                scalar_services=32*sum(scalar.values()), scalar_step_rate=2**max(20, scalar_bits+8),
                ordinary_map_slots=maps, ordinary_elementary_record_upper=maps*4*(ambient+1)**2,
                raw_paid_positions=paid, raw_productive_targets=targets,
                root_negative_q_translations=signed['root_negative_q'], native_paid_wrappers=stages*k,
                ordinary_main_pair_slots=stages*400, port_view_routing_legs=port_legs,
                port_view_permutations=2*400*stages, port_view_translations=2*400*stages,
                serial_caller_real_component_arrays=16)


def check_components(caller, physical, native_bits):
    events, _ = split_templates(caller)['mixed']
    numbers = {Fraction(s) for op, *args in events if op in ('ADD', 'SCALE') for s in args[-1]}
    bits = max(native_bits, *(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) for q in numbers))
    need(bits <= 24, 'padded scalar conversion width')
    cases = 0
    for value in sorted(numbers):
        for k in (0, -127, -1, 1, 19, 2**68+1):
            x, y = k*value.denominator, k*value.numerator
            width = max(3, abs(x).bit_length()+2, abs(y).bit_length()+2)
            need(physical.scalar_service(x, value, width) == y, 'signed Gaussian component service')
            cases += 1
    return dict(coefficient_bits=bits, mixed_rational_coefficients=len(numbers),
                mixed_scalar_service_cases=cases, component_padding=26)


def comparison_invoice(previous, stages, previous_stages=16):
    """Compare the two constructions over the same number of native calls."""
    need(stages % previous_stages == 0, 'common native stage count')
    multiple = stages//previous_stages
    contract = dict(previous['contract'], boundary='P104 batch with explicit signed caller owners',
                    ambient_rank=137)
    return dict(schema=previous['schema'], contract=contract,
                paid={r: multiple*z for r, z in previous['paid'].items()},
                targets={r: multiple*z for r, z in previous['targets'].items()})


def verify_expansion(caller, layout, calls=32):
    """Read a complete emitted event stream through an independent root-position index."""
    words = split_templates(caller)
    roots = place_roots(caller, calls)
    bound, offsets, _ = layout_bindings(words, roots, layout, calls)
    owners, pointer = {}, {}
    for root, off in offsets.items():
        pointer[root] = 0
        for k in range(len(words[root[0]][1])):
            owners[off+k] = root
    native = 0
    view_step = 'ENTER'
    digest = sha256()
    counts = Counter()
    def expect(root, event):
        pos = pointer[root]
        need(words[root[0]][0][pos] == event, 'literal batch projection to the signed template')
        pointer[root] = pos+1
    for event in instructions(words, roots, bound, offsets):
        digest.update(json.dumps(event, separators=(',', ':')).encode())
        op, *args = event
        counts[op] += 1
        if op == 'PORT_VIEWS':
            side, t, ports = args
            need(side == view_step and t == (native if side == 'ENTER' else native-1)
                 and ports == [bound[t][p] for p in range(104)], 'both ordinary port views on every owner')
            view_step = 'NATIVE' if side == 'ENTER' else 'ENTER'
        elif op == 'NATIVE':
            need(view_step == 'NATIVE', 'head conjugation before every call')
            view_step = 'EXIT'
            t, color, ports = args
            need((t, color, len(ports)) == (native, native % 16, 104), 'chronological joint call')
            for p, regs in enumerate(ports):
                root = owners[regs[0]]
                need(all(owners[r] == root for r in regs), 'main registers have one local root')
                slot = roots[root].index((t, p))
                kind = 'HOST_A' if len(regs) == 4 else 'HOST_B'
                expect(root, [kind, slot, *(r-offsets[root] for r in regs)])
            native += 1
        else:
            need(view_step == 'ENTER', 'head restoration before caller operations')
            root = owners[args[0]]
            args[0] -= offsets[root]
            if op in ('ADD', 'SWAP', 'QUERY'):
                need(owners[args[1]] == root, 'scratch owner in the same root')
                args[1] -= offsets[root]
            if op.startswith('IDLE_'):
                colors = [t % 16 for t, _ in roots[root]]
                args[1] = [colors.index(j) for j in args[1]]
            expect(root, [op, *args])
    need(native == calls and view_step == 'ENTER' and all(p == len(words[r[0]][0]) for r, p in pointer.items()),
         'all template instructions consumed')
    return dict(native_calls=native, emitted_events=sum(counts.values()), op_counts=dict(counts),
                event_stream_sha256=digest.hexdigest())
