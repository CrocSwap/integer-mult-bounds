"""Exact source census and mandatory cost-vector lower bound.

The source tariff is deliberately not equated with this physical metric.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
import gzip
import json
from source_binding import ROOT, need

# (physical reads, physical writes, physical unit moves, executed flat rows)
# Each entry is the mandatory contribution per ordinary public data bit.
PHASES = {
    'initialize_and_reset': (18, 3, 42, 12),
    'one_Horner_and_reset': (22, 3, 48, 13),
    'offset_and_rewind': (10, 3, 24, 6),
    'odd_residue_and_rewind': (10, 0, 18, 5),
    'quotient_stage': (16, 3, 36, 9),
    'global_reverse': (8, 0, 18, 6),
    'installation': (6, 3, 18, 5),
    'executor_head_returns': (6, 0, 6, 0),
    'two_current_body_retirements': (12, 6, 12, 0),
}


def coefficient_shape(q):
    q = Fraction(q)
    a, b = abs(q.numerator), q.denominator
    odd = b
    while odd % 2 == 0:
        odd //= 2
    return a, b, max(a.bit_length(), b.bit_length()), odd


def lower_vector(coefficient):
    _, _, length, odd = coefficient_shape(coefficient)
    return tuple(sum(v[j] * (length if k == 'one_Horner_and_reset' else
                            int(odd > 1) if k == 'odd_residue_and_rewind' else 1)
                     for k, v in PHASES.items()) for j in range(4))


def rounded_surcharge(q):
    _, b, _, odd = coefficient_shape(q)
    return 0 if b == 1 else 4 * (b.bit_length() + 1) * (1 + 3 * int(odd > 1))


def exchange_count(axes):
    return len(set(axes) - set(range(len(axes))))


def inspect_sources():
    word = json.loads(gzip.decompress((ROOT / 'data/word.json.gz').read_bytes()))
    caller = json.loads((ROOT / 'data/caller.json').read_text())
    program = word['program']
    native_counts = Counter(e[0] for e in program)
    joints = [e for e in caller['events'] if e[0] == 'J']
    need([e[1] for e in joints] == list(range(1, 19)), 'exact 18 native contacts')
    need(len(program) == 71144 and len(caller['events']) == 3095, 'frozen source lengths')
    add = [e for e in program if e[0] == 'ADD']
    copies = [e for e in program if e[0] == 'COPY']
    need(copies == [['COPY', 1485, 770, '1', 115]], 'COPY kept separate')
    shapes = [coefficient_shape(e[3]) for e in add]
    lengths = Counter(s[2] for s in shapes)
    total = [sum(lower_vector(e[3])[j] for e in add) * len(joints) for j in range(4)]
    old_add_per_call = sum(4 * (a.bit_length() + a.bit_count() + b.bit_length() + 1)
                           for a, b, _, _ in shapes)
    offset_add_per_call = sum(rounded_surcharge(e[3]) for e in add)

    # Independently reconstruct the entire frozen invoice. These are the
    # predecessor's scalar/pass formulas; none is presented as a physical rate.
    reviewed_scalars = 0
    native_extra = 0
    for e in program:
        if e[0] not in ('ADD', 'COPY', 'SCALE'):
            continue
        q = Fraction(e[-2]); a, b = abs(q.numerator), q.denominator
        reviewed_scalars += 4 * (a.bit_length() + b.bit_length() + 1
                                + (0 if e[0] == 'SCALE' else a.bit_count()))
        native_extra += rounded_surcharge(q)
    n = word['public']
    main = (set(word['live']) | {x + 112 for x in word['live']} |
            set(word['hosted']['X2']) | set(word['hosted']['Y2']))
    helper_count = n - len(main)
    routes = 1000 * (native_counts['MOVE'] + 2 * helper_count + 208 + 2 * 96
                     + 4 * 104 + 4 * 96 + 4 * native_counts['INIT'])
    rest = Counter(); outer_counts = Counter(); outer_extra = 0
    for ty in ('A', 'B'):
        t = caller['types'][ty]; p = len(t['ports']); roles = t['roles']
        events = [e for e in caller['events'] if e[0] in (ty, 'J')]
        rest['caller_envelope'] += 32 * roles * p * len(events)
        rest['main_normalizers'] += 26 * roles * p
        for qp, zero, *mask in t['diagonal']:
            axes = ([0] if qp else []) + [a for k, yes in enumerate(mask, 1) if yes
                                         for a in range(9 + 8 * (k - 1), 9 + 8 * k)]
            rest['main_maps'] += 1000 * p * (2 * exchange_count(axes) + 2 * bool(qp) + int(qp == -1))
        for e in events:
            if e[0] == 'J':
                continue
            op = e[1]; outer_counts[op] += p
            if op == 'QUERY':
                rest['thin_lifecycle'] += 16 * p
                rest['query_maps'] += 1000 * p * (2 + int(e[-1] == -1))
            elif op == 'IDLE_ONE':
                axes = [a for k in e[3] for a in range(9 + 8 * (k - 1), 9 + 8 * k)]
                rest['idle_maps'] += 2000 * p * exchange_count(axes)
            elif op == 'LAMBDA':
                rest['lambda_recharge'] += 1000 * p
                outer_extra += 12 * p
            elif op in ('ADD', 'SCALE'):
                outer_extra += p * rounded_surcharge(e[-1])
    converted = 18 * n * 104
    baseline = 18 * (reviewed_scalars + routes) + sum(rest.values()) + converted
    extra = 18 * native_extra + outer_extra
    need((baseline, extra) == (826265904, 17165584), 'independent complete source model reconstruction')
    current = baseline + extra
    credit = 18 * (old_add_per_call + offset_add_per_call)
    remaining = current - credit
    room = 10 ** 9 - remaining
    raw = sum(total[:3]); combined = sum(total)
    need((len(add), sum(s[2] for s in shapes), sum(s[3] > 1 for s in shapes)) ==
         (61052, 167955, 4079), 'exact native ADD census')
    need((credit, raw, combined, room) == (47484288, 497482686, 578910834, 204052800),
         'exact source-specific conversion frontier')
    need(max(s[3] for s in shapes) <= 125, 'generic compact constructor odd-divisor domain')
    return dict(native_events=len(program), caller_events=len(caller['events']),
        native_opcode_counts=dict(sorted(native_counts.items())),
        outer_physical_opcode_counts=dict(sorted(outer_counts.items())),
        native_contacts=18, native_ADD_count=61052, separate_COPY=copies,
        coefficient_length_sum=167955, coefficient_length_histogram=dict(sorted(lengths.items())),
        odd_ADD_count=4079, proposed_full_ADD_dispatch_count=18*61052,
        physical_lower_vector_per_common_data_bit=dict(zip(('reads','writes','moves','rows'), total)),
        raw_action_lower=raw, raw_plus_rows_lower=combined,
        old_ADD_tariff_per_native_call=old_add_per_call,
        old_ADD_offset_tariff_per_native_call=offset_add_per_call,
        removed_ADD_credit=credit, baseline=baseline, optimistic_extra=extra,
        optimistic_complete=current, retained_other_invoice=remaining,
        replacement_headroom=room,
        raw_required_exchange_rate=str(Fraction(raw,room)),
        raw_plus_rows_required_exchange_rate=str(Fraction(combined,room)),
        raw_equal_unit_replacement_lower=remaining+raw,
        combined_equal_unit_replacement_lower=remaining+combined,
        source_model_terms=dict(rest), native_scalar_model=reviewed_scalars,
        native_routes_model=routes, native_extra_model=native_extra,
        unit_status='No numeric tape-action/flat-row-to-tariff converter is asserted by the sources.',
        volume_status='The aggregate coefficient assumes equal per-field data-bit volume; otherwise sum the per-event weighted volumes.',
        registry_status='Hypothetical direct compact-table substitution at all ADD sites; predecessor installs only three source tokens.',
        kappa_status='No new kappa; no physical cap or full-caller impossibility claim.')
