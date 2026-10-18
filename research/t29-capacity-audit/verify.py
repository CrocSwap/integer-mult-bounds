#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Capacity-tagged whole-helper pattern feasibility of PR992's sharp T=29 profile.

PR992 (research/t37-integrality-audit) exhibits the aggregate remainder profile
{1:4, 2:1, 48:8689} at T=29 as the sharp case of its integer penalty and states
that it constructs no physical owner assignment. This checker tests the next
necessary condition that PR992 omits: do nonnegative integer counts of legal,
capacity-tagged bin patterns exist that meet the fixed U8 family's capacity
quotas (672,448,448,448)*29, its whole-helper width demands
(720,288,486,1098,1944)*29 for widths (4,5,7,8,9), and that exact remainder
profile including all 49770 rank-zero bins?

Everything is exact integer arithmetic in the standard library. No solver is
run and no floating point enters any decision. The checker

  1. verifies the sha256 pins of the consumed predecessor statements;
  2. enumerates every legal bin count vector once, by Cartesian product, and
     recomputes the signed-price table u(r) independently by a maximum-price
     dynamic program over exact fills; the two tables must agree;
  3. checks the aggregate identities for T=29: bin count, rank mass and the
     zero credit slack sum_r n_r*u(r) = -3892*29;
  4. proves the tightness lemma consequences: every bin of any realization
     attains u(r), every width-five helper sits in a {9,9,9,5} capacity-32 bin,
     the three nonzero remainder classes have the listed patterns only, and the
     width-nine demand is implied by the width-seven demand;
  5. checks WITNESS.json pattern by pattern, validates its declared
     remainder_profile against the recomputed census before any acceptance or
     --write, reconstructs it in closed form, and checks a second realization
     with different counts (the reviewer's blind construction in REVIEW.md), so
     the realization is not unique;
  6. runs negative controls: inventory mutations whose preserved and changed
     aggregate invariants (bin count, residual mass, dual credit, actual signed
     price, quotas, demands, profile) are recomputed and recorded, invalid
     witness documents, false declared profiles, and tampered proof data;
  7. compares the complete certificate with EXPECTED.json.

All checks raise explicit exceptions and stay active under python -O.
No network access, no third-party module, no file is written unless --write,
and --write writes only after every check has passed.
"""
import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYPOTHESIS = 'q_b6cf2a2ce15a43ed:e10'
STATUS = 'PASS_T29_CAPACITY_TAGGED_PATTERN_WITNESS'
WIDTHS = (4, 5, 7, 8, 9)
PRICE = {4: -1, 5: -20, 7: -8, 8: -2, 9: 4}
# capacity -> (bins per replica, capacity bonus)
CAPACITY = {8: (672, 2), 16: (448, 4), 32: (448, 8), 48: (448, -13)}
PER_CALL = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}
CALLS_PER_REPLICA = 9
T = 29
PROFILE = {0: 49770, 1: 4, 2: 1, 48: 8689}
ZERO = (0, 0, 0, 0, 0)
# Count vectors are indexed by WIDTHS: (n4, n5, n7, n8, n9).
# Second realization, transcribed from the reviewer's blind hand construction
# (REVIEW.md, "Exact proof and independently derived witness"). It differs from
# WITNESS.json in eight pattern counts, including a different rank-2 pattern.
SECOND_WITNESS = {
    (8, (2, 0, 0, 0, 0)): 8285, (8, (0, 0, 0, 1, 0)): 11203,
    (16, (0, 0, 1, 0, 1)): 4824, (16, (0, 0, 0, 2, 0)): 8168,
    (32, (0, 1, 0, 0, 3)): 8352, (32, (0, 0, 2, 0, 2)): 4635,
    (32, (1, 0, 0, 0, 3)): 4, (32, (3, 0, 0, 0, 2)): 1,
    (48, (1, 0, 0, 1, 4)): 4303, (48, ZERO): 8689,
}


class Reject(ValueError):
    """Explicit failure; independent of the assert statement and python -O."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load_json(path, what):
    try:
        return json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise Reject('%s is missing or malformed: %s' % (what, error))


def width(vec):
    return sum(w * n for w, n in zip(WIDTHS, vec))


def price(cap, vec):
    return CAPACITY[cap][1] + sum(PRICE[w] * n for w, n in zip(WIDTHS, vec))


def label(cap, vec):
    widths = [w for w, n in zip(WIDTHS, vec) for _ in range(n)]
    return '%d:{%s}' % (cap, ','.join(str(w) for w in sorted(widths, reverse=True)))


# ---------------------------------------------------------------- sources
def check_sources(root, pins):
    require(isinstance(pins, dict) and pins, 'SOURCES.json must map relative paths to sha256 digests')
    for relative, digest in sorted(pins.items()):
        path = root / relative
        require(path.is_file(), 'source pin missing: ' + relative)
        require(sha256_bytes(path.read_bytes()) == digest, 'source pin mismatch: ' + relative)
    return dict(sorted(pins.items()))


# -------------------------------------------------------------- patterns
def enumerate_patterns():
    """The one enumeration: every legal count vector per capacity by Cartesian product."""
    patterns = {}
    for cap in CAPACITY:
        patterns[cap] = [vec for vec in itertools.product(*(range(cap // w + 1) for w in WIDTHS))
                         if width(vec) <= cap]
    return patterns


def price_table(patterns):
    upper = {}
    for cap, vectors in patterns.items():
        for vec in vectors:
            r = cap - width(vec)
            p = price(cap, vec)
            if r not in upper or p > upper[r]:
                upper[r] = p
    return upper


def price_table_recurrence():
    """Independent maximum-price dynamic program over exact fills; it recomputes
    u(r) without enumerating or counting the legal count vectors."""
    upper = {}
    for cap, (_, bonus) in CAPACITY.items():
        best = {0: 0}
        for fill in range(1, cap + 1):
            candidates = [best[fill - w] + PRICE[w] for w in WIDTHS if fill >= w and fill - w in best]
            if candidates:
                best[fill] = max(candidates)
        for fill, p in best.items():
            r = cap - fill
            if r not in upper or p + bonus > upper[r]:
                upper[r] = p + bonus
    return upper


# ------------------------------------------------------------- aggregate
def aggregate(replicas, profile, upper):
    quotas = {cap: replicas * bins for cap, (bins, _) in CAPACITY.items()}
    demands = {w: replicas * CALLS_PER_REPLICA * PER_CALL[w] for w in WIDTHS}
    bins = sum(quotas.values())
    mass = sum(cap * n for cap, n in quotas.items()) - sum(w * n for w, n in demands.items())
    signed = sum(CAPACITY[cap][1] * n for cap, n in quotas.items()) + sum(PRICE[w] * n for w, n in demands.items())
    for r in profile:
        require(r in upper, 'profile uses an unattainable remainder rank: %d' % r)
    require(sum(profile.values()) == bins, 'bin count identity: profile has %d bins, quotas give %d' % (sum(profile.values()), bins))
    require(sum(r * n for r, n in profile.items()) == mass, 'rank mass identity: profile mass %d, inventory mass %d' % (sum(r * n for r, n in profile.items()), mass))
    dual = sum(upper[r] * n for r, n in profile.items())
    slack = dual - signed
    require(slack >= 0, 'profile violates the necessary signed-price inequality (slack %d)' % slack)
    require(slack == 0, 'signed-price identity (zero slack) fails: sum u(r) n_r = %d, actual total price = %d' % (dual, signed))
    return dict(replicas=replicas, quotas=quotas, demands=demands, bins=bins, mass=mass,
                signed_price=signed, dual_price=dual, slack=slack)


# ------------------------------------------------------- tightness lemma
def tight_patterns(patterns, upper, profile):
    """Patterns attaining u(r) in each remainder class present in the profile.

    Zero slack forces every bin of every realization into this set: each bin's
    price is at most u(r) and the sum of all bin prices equals sum_r n_r u(r).
    """
    classes = {}
    for r, n in profile.items():
        if n:
            classes[r] = sorted((cap, vec) for cap, vectors in patterns.items() for vec in vectors
                                if cap - width(vec) == r and price(cap, vec) == upper[r])
    return classes


def forced_structure(classes, agg):
    quotas, demands = agg['quotas'], agg['demands']
    tight = [(r, cap, vec) for r, items in classes.items() for cap, vec in items]
    fives = [(r, cap, vec) for r, cap, vec in tight if vec[1]]
    require(fives == [(0, 32, (0, 1, 0, 0, 3))], 'width-five helpers must sit in capacity-32 {9,9,9,5} bins')
    require(classes[48] == [(48, ZERO)], 'rank-48 tight pattern must be the empty capacity-48 bin')
    require(classes[1] == [(32, (1, 0, 0, 0, 3))], 'rank-1 tight pattern must be capacity-32 {9,9,9,4}')
    require(classes[2] == [(32, (1, 0, 0, 1, 2)), (32, (3, 0, 0, 0, 2))], 'rank-2 tight patterns must be capacity-32 {9,9,8,4} and {9,9,4,4,4}')
    cap48_full = [vec for cap, vec in classes[0] if cap == 48]
    require(cap48_full == [(1, 0, 0, 1, 4), (3, 0, 0, 0, 4)], 'full capacity-48 tight patterns must be {9,9,9,9,8,4} and {9,9,9,9,4,4,4}')
    others = [(cap, vec) for cap, vec in classes[0] if cap != 48 and vec != (0, 1, 0, 0, 3)]
    require(all(vec[4] == vec[2] for cap, vec in others), 'every other full tight pattern must pair each nine with one seven')
    fives_bins = demands[5]
    full48 = quotas[48] - PROFILE[48]
    nines_fixed = 4 * full48 + 3 * fives_bins + 3 * PROFILE[1] + 2 * PROFILE[2]
    require(demands[9] - nines_fixed == demands[7], 'width-nine demand is not implied by the width-seven demand')
    cap32_free = quotas[32] - fives_bins - PROFILE[1] - PROFILE[2]
    low = max(0, demands[7] - 2 * cap32_free)
    high = min(quotas[16], demands[7])
    require(low <= high, 'no room for the width-seven helpers')
    return dict(tight_patterns_by_class={str(r): [label(cap, vec) for cap, vec in items] for r, items in classes.items()},
                forced_fives_bins_cap32_9995=fives_bins,
                forced_full_capacity48_bins=full48,
                nines_in_forced_bins=nines_fixed,
                nines_remaining_equals_sevens=demands[7],
                capacity16_nine_seven_bins_necessary_range=[low, high],
                capacity16_nine_seven_bins_range_is_necessary_only=True,
                cap32_bins_free_for_rank0_without_fives=cap32_free)


# --------------------------------------------------------------- witness
def parse_witness(document):
    require(isinstance(document, dict) and isinstance(document.get('patterns'), list), 'witness must list patterns')
    entries = {}
    for item in document['patterns']:
        require(isinstance(item, dict), 'pattern entry must be an object')
        cap, widths, count = item.get('capacity'), item.get('widths'), item.get('count')
        require(type(cap) is int and cap in CAPACITY, 'unknown capacity: %r' % (cap,))
        require(isinstance(widths, list) and all(type(w) is int and w in WIDTHS for w in widths), 'unknown helper width in %r' % (widths,))
        require(type(count) is int and count >= 0, 'count must be a nonnegative integer: %r' % (count,))
        vec = tuple(widths.count(w) for w in WIDTHS)
        require(width(vec) <= cap, 'illegal pattern: width %d exceeds capacity %d' % (width(vec), cap))
        if 'remainder' in item:
            require(item['remainder'] == cap - width(vec), 'declared remainder disagrees with capacity minus width')
        key = (cap, vec)
        require(key not in entries, 'duplicate pattern entry: ' + label(cap, vec))
        entries[key] = count
    return entries


def invariants(entries, upper):
    """Aggregate quantities of a pattern-count vector; used for the control deltas."""
    quotas = Counter()
    demands = Counter({w: 0 for w in WIDTHS})
    profile = Counter()
    signed = dual = 0
    for (cap, vec), n in entries.items():
        r = cap - width(vec)
        quotas[cap] += n
        profile[r] += n
        for w, k in zip(WIDTHS, vec):
            demands[w] += k * n
        signed += n * price(cap, vec)
        dual += n * (48 * upper[r] + 13 * r) if r in upper else 0
    return dict(bins=sum(quotas.values()), mass=sum(r * n for r, n in profile.items()), dual_credit=dual,
                signed_price=signed, quotas=dict(quotas), demands=dict(demands), profile={r: n for r, n in profile.items() if n})


def check_witness(entries, agg, upper):
    quotas, demands = agg['quotas'], agg['demands']
    for cap in CAPACITY:
        have = sum(n for (c, _), n in entries.items() if c == cap)
        require(have == quotas[cap], 'capacity quota mismatch: capacity %d has %d bins, quota %d' % (cap, have, quotas[cap]))
    census = Counter()
    for (cap, vec), n in entries.items():
        census[cap - width(vec)] += n
    census = {r: n for r, n in census.items() if n}
    require(census == {r: n for r, n in PROFILE.items() if n}, 'remainder profile mismatch: %s' % dict(sorted(census.items())))
    for i, w in enumerate(WIDTHS):
        have = sum(vec[i] * n for (cap, vec), n in entries.items())
        require(have == demands[w], 'width demand mismatch: width %d used %d times, demand %d' % (w, have, demands[w]))
    total = 0
    for (cap, vec), n in entries.items():
        if n:
            require(price(cap, vec) == upper[cap - width(vec)], 'untight pattern ' + label(cap, vec))
            total += n * price(cap, vec)
    require(total == agg['signed_price'], 'total signed price %d differs from %d' % (total, agg['signed_price']))
    used = sorted(((cap, vec), n) for (cap, vec), n in entries.items() if n)
    return dict(distinct_patterns=len(used), bins=sum(n for _, n in used), total_signed_price=total,
                census={str(r): n for r, n in sorted(census.items())},
                patterns=[dict(pattern=label(cap, vec), capacity=cap, remainder=cap - width(vec), count=n) for (cap, vec), n in used])


def check_declared_profile(document, census):
    """The declared remainder_profile must equal the recomputed census exactly:
    canonical decimal rank keys, positive integer values (not booleans), no
    missing or extra classes."""
    require('remainder_profile' in document, 'witness must declare remainder_profile')
    declared = document['remainder_profile']
    require(isinstance(declared, dict) and declared, 'declared remainder_profile must be a nonempty object')
    for key, value in declared.items():
        require(isinstance(key, str) and key.isdigit() and str(int(key)) == key,
                'declared remainder_profile keys must be canonical decimal rank strings: %r' % (key,))
        require(type(value) is int and value > 0, 'declared remainder_profile values must be positive integers: %r' % (value,))
    require(declared == census, 'declared remainder_profile disagrees with the recomputed census: declared %s, census %s' % (
        json.dumps(declared, sort_keys=True), json.dumps(census, sort_keys=True)))


def admit_document(document, agg, upper):
    """Header, patterns, exact packing census and declared profile, in this order."""
    require(isinstance(document, dict), 'witness must be a JSON object')
    require(document.get('hypothesis') == HYPOTHESIS, 'witness header hypothesis must be ' + HYPOTHESIS)
    require(type(document.get('replicas')) is int and document['replicas'] == T, 'witness header replicas must be the integer %d' % T)
    entries = parse_witness(document)
    summary = check_witness(entries, agg, upper)
    check_declared_profile(document, summary['census'])
    return entries, summary


def construct_witness(agg):
    """Closed-form realization; every step is forced or a free choice made explicit."""
    quotas, demands = agg['quotas'], agg['demands']
    fives = demands[5]                      # forced: all fives in 32:{9,9,9,5}
    full48 = quotas[48] - PROFILE[48]       # forced: remaining capacity-48 bins are full
    y1 = quotas[16]                         # choice: every capacity-16 bin is 16:{9,7}
    rest7 = demands[7] - y1
    require(rest7 >= 0 and rest7 % 2 == 0, 'sevens left for 32:{9,9,7,7} must be an even nonnegative number')
    y5 = rest7 // 2
    c1 = quotas[32] - fives - PROFILE[1] - PROFILE[2] - y5   # choice: remaining capacity-32 bins are 32:{8,8,8,8}
    require(c1 >= 0, 'capacity-32 quota exceeded')
    f1 = full48                             # choice: every full capacity-48 bin is 48:{9,9,9,9,8,4}
    a1 = demands[8] - f1 - 1 - 4 * c1       # forced by the width-eight demand given the choices
    a2 = quotas[8] - a1
    require(0 <= a1 <= quotas[8], 'capacity-8 split out of range')
    fours = 2 * a2 + f1 + PROFILE[1] + PROFILE[2]
    require(fours == demands[4], 'closed-form witness fails the width-four demand: %d vs %d' % (fours, demands[4]))
    return {(8, (0, 0, 0, 1, 0)): a1, (8, (2, 0, 0, 0, 0)): a2,
            (16, (0, 0, 1, 0, 1)): y1,
            (32, (0, 1, 0, 0, 3)): fives, (32, (1, 0, 0, 0, 3)): PROFILE[1], (32, (1, 0, 0, 1, 2)): PROFILE[2],
            (32, (0, 0, 2, 0, 2)): y5, (32, (0, 0, 0, 4, 0)): c1,
            (48, ZERO): PROFILE[48], (48, (1, 0, 0, 1, 4)): f1}


# -------------------------------------------------------------- controls
def swap(entries, old, new, count=1):
    bad = dict(entries)
    require(bad.get(old, 0) >= count, 'control setup: pattern absent ' + label(*old))
    bad[old] -= count
    bad[new] = bad.get(new, 0) + count
    return bad


def control_deltas(entries, mutated, upper):
    """Which aggregate invariants a mutated pattern-count vector preserves or changes."""
    before, after = invariants(entries, upper), invariants(mutated, upper)
    delta = {k: after[k] - before[k] for k in ('bins', 'mass', 'dual_credit', 'signed_price')}
    changed = {k: v for k, v in delta.items() if v}
    inventory = {}
    for name in ('quotas', 'demands', 'profile'):
        diff = {str(k): after[name].get(k, 0) - before[name].get(k, 0)
                for k in set(before[name]) | set(after[name]) if after[name].get(k, 0) != before[name].get(k, 0)}
        if diff:
            inventory[name] = dict(sorted(diff.items()))
    return dict(delta=delta, preserved=[k for k in delta if not delta[k]], changed=sorted(changed),
                violated_inventory=inventory)


def negative_controls(entries, document, agg, upper, root, pins, patterns):
    cases = []

    def witness_case(name, build, expected):
        def run():
            mutated = build()
            try:
                check_witness(mutated, agg, upper)
            except Reject as error:
                raise Reject(str(error), control_deltas(entries, mutated, upper))
        cases.append((name, run, expected))

    # Inventory mutations; their preserved/changed invariants are recomputed and recorded.
    witness_case('width_swap_16_9_7_to_16_8_8', lambda: swap(entries, (16, (0, 0, 1, 0, 1)), (16, (0, 0, 0, 2, 0))), 'width demand mismatch')
    witness_case('width_swap_32_9995_to_32_9977', lambda: swap(entries, (32, (0, 1, 0, 0, 3)), (32, (0, 0, 2, 0, 2))), 'width demand mismatch')
    witness_case('rank2_alternative_32_9984_to_32_99444', lambda: swap(entries, (32, (1, 0, 0, 1, 2)), (32, (3, 0, 0, 0, 2))), 'width demand mismatch')
    witness_case('retag_8_8_to_16_88', lambda: swap(entries, (8, (0, 0, 0, 1, 0)), (16, (0, 0, 0, 2, 0))), 'capacity quota mismatch')
    witness_case('retag_empty_48_to_full_48_999984', lambda: swap(entries, (48, ZERO), (48, (1, 0, 0, 1, 4))), 'remainder profile mismatch')
    witness_case('rank1_untight_32_9994_to_32_8887', lambda: swap(entries, (32, (1, 0, 0, 0, 3)), (32, (0, 0, 1, 3, 0))), 'width demand mismatch')
    witness_case('one_bin_short_8_8', lambda: {**entries, (8, (0, 0, 0, 1, 0)): entries[(8, (0, 0, 0, 1, 0))] - 1}, 'capacity quota mismatch')

    # Invalid witness documents (header, patterns, declared profile).
    def mutated_document(mutate):
        copy = json.loads(json.dumps(document))
        mutate(copy)
        return copy

    def doc_case(name, mutate, expected):
        cases.append((name, lambda: admit_document(mutated_document(mutate), agg, upper), expected))

    doc_case('overfull_pattern_48_999994', lambda d: d['patterns'].append(dict(capacity=48, widths=[9, 9, 9, 9, 9, 4], count=1)), 'illegal pattern')
    doc_case('negative_count', lambda d: d['patterns'][0].__setitem__('count', -1), 'count must be a nonnegative integer')
    doc_case('fractional_count', lambda d: d['patterns'][0].__setitem__('count', 0.5), 'count must be a nonnegative integer')
    doc_case('boolean_count', lambda d: d['patterns'][0].__setitem__('count', True), 'count must be a nonnegative integer')
    doc_case('unknown_width_6', lambda d: d['patterns'].append(dict(capacity=16, widths=[6, 6], count=1)), 'unknown helper width')
    doc_case('unknown_capacity_24', lambda d: d['patterns'].append(dict(capacity=24, widths=[8, 8, 8], count=1)), 'unknown capacity')
    doc_case('duplicate_pattern_entry', lambda d: d['patterns'].append(dict(d['patterns'][0])), 'duplicate pattern entry')
    doc_case('false_declared_remainder', lambda d: d['patterns'][0].__setitem__('remainder', 5), 'declared remainder disagrees')
    doc_case('header_replicas_float', lambda d: d.__setitem__('replicas', 29.0), 'witness header replicas must be the integer')
    doc_case('header_replicas_boolean', lambda d: d.__setitem__('replicas', True), 'witness header replicas must be the integer')
    doc_case('header_wrong_hypothesis', lambda d: d.__setitem__('hypothesis', 'q_b6cf2a2ce15a43ed:e11'), 'witness header hypothesis must be')
    doc_case('declared_profile_missing', lambda d: d.pop('remainder_profile'), 'witness must declare remainder_profile')
    doc_case('declared_profile_false_rank0_count', lambda d: d['remainder_profile'].__setitem__('0', 1), 'declared remainder_profile disagrees')
    doc_case('declared_profile_missing_class_2', lambda d: d['remainder_profile'].pop('2'), 'declared remainder_profile disagrees')
    doc_case('declared_profile_extra_zero_class_3', lambda d: d['remainder_profile'].__setitem__('3', 0), 'declared remainder_profile values must be positive integers')
    doc_case('declared_profile_boolean_value', lambda d: d['remainder_profile'].__setitem__('1', True), 'declared remainder_profile values must be positive integers')
    doc_case('declared_profile_noncanonical_key_01', lambda d: d['remainder_profile'].__setitem__('01', d['remainder_profile'].pop('1')), 'declared remainder_profile keys must be canonical')
    doc_case('declared_profile_swapped_classes', lambda d: d['remainder_profile'].update({'1': 1, '2': 4}), 'declared remainder_profile disagrees')

    # Tampered proof data.
    def tampered_table():
        bad = dict(upper)
        bad[2] = 14
        require(bad == price_table(patterns), 'signed-price table disagrees with the independent enumeration')
    cases.append(('tampered_u_table_u2_14', tampered_table, 'signed-price table disagrees'))
    cases.append(('wrong_replica_count_28', lambda: aggregate(28, PROFILE, upper), 'bin count identity'))
    cases.append(('profile_off_by_one_rank1', lambda: aggregate(T, {0: 49770, 1: 5, 2: 1, 48: 8689}, upper), 'bin count identity'))
    # Same 58464 bins and same mass 417078 as the sharp profile, different credit.
    cases.append(('profile_same_bins_same_mass_positive_slack', lambda: aggregate(T, {0: 49769, 1: 6, 48: 8689}, upper), 'signed-price identity (zero slack) fails'))
    cases.append(('profile_same_bins_same_mass_negative_slack', lambda: aggregate(T, {0: 49772, 2: 3, 48: 8689}, upper), 'profile violates the necessary signed-price inequality'))

    def tampered_pin():
        bad = dict(pins)
        first = sorted(bad)[0]
        bad[first] = '0' * 64
        check_sources(root, bad)
    cases.append(('tampered_source_pin', tampered_pin, 'source pin mismatch'))

    rejected = []
    for name, run, expected in cases:
        try:
            run()
        except Reject as error:
            require(str(error.args[0]).startswith(expected), 'control %s rejected for an unexpected reason: %s' % (name, error.args[0]))
            record = dict(name=name, reason=str(error.args[0]))
            if len(error.args) > 1:
                record['invariants'] = error.args[1]
            rejected.append(record)
        else:
            raise Reject('negative control was accepted: ' + name)
    return rejected


# ------------------------------------------------------------------ main
def certificate(root, run_controls=True):
    sources = load_json(HERE / 'SOURCES.json', 'SOURCES.json')
    require(isinstance(sources, dict) and 'sha256' in sources and 'base_commit' in sources, 'SOURCES.json must record sha256 pins and the base commit')
    pins = check_sources(root, sources['sha256'])
    patterns = enumerate_patterns()
    legal = sum(len(v) for v in patterns.values())
    upper = price_table(patterns)
    require(upper == price_table_recurrence(), 'the maximum-price recurrence disagrees with the enumerated table u(r)')
    require((upper[0], upper[1], upper[2], upper[48]) == (0, 19, 13, -13), 'anchor values of u(r)')
    agg = aggregate(T, PROFILE, upper)
    classes = tight_patterns(patterns, upper, PROFILE)
    structure = forced_structure(classes, agg)
    witness_path = HERE / 'WITNESS.json'
    witness_bytes = witness_path.read_bytes() if witness_path.is_file() else b''
    document = load_json(witness_path, 'WITNESS.json')
    entries, summary = admit_document(document, agg, upper)
    require({k: v for k, v in entries.items() if v} == construct_witness(agg), 'closed-form reconstruction differs from WITNESS.json')
    y1 = entries.get((16, (0, 0, 1, 0, 1)), 0)
    low, high = structure['capacity16_nine_seven_bins_necessary_range']
    require(low <= y1 <= high, 'witness outside the derived capacity-16 range')
    second = check_witness(SECOND_WITNESS, agg, upper)
    first_counts = {k: v for k, v in entries.items() if v}
    differing = sorted(label(cap, vec) for (cap, vec) in set(first_counts) | set(SECOND_WITNESS)
                       if first_counts.get((cap, vec), 0) != SECOND_WITNESS.get((cap, vec), 0))
    require(differing, 'the second realization must differ from WITNESS.json')
    result = dict(status=STATUS, hypothesis=HYPOTHESIS, base_commit=sources['base_commit'],
                  replicas=T, widths=list(WIDTHS), prices={str(w): PRICE[w] for w in WIDTHS},
                  capacities={str(c): dict(bins_per_replica=b, bonus=z) for c, (b, z) in CAPACITY.items()},
                  helpers_per_call={str(w): PER_CALL[w] for w in WIDTHS}, calls_per_replica=CALLS_PER_REPLICA,
                  profile={str(r): n for r, n in PROFILE.items()},
                  quotas={str(c): n for c, n in agg['quotas'].items()}, demands={str(w): n for w, n in agg['demands'].items()},
                  bins=agg['bins'], rank_mass=agg['mass'], total_signed_price=agg['signed_price'], credit_slack=agg['slack'],
                  enumeration='one Cartesian product enumeration of all legal count vectors; u(r) recomputed independently by a maximum-price dynamic program over exact fills',
                  legal_patterns=legal, legal_patterns_by_capacity={str(c): len(v) for c, v in patterns.items()},
                  u={str(r): u for r, u in sorted(upper.items())},
                  tightness_lemma='sum of bin prices equals the fixed total -3892*T and equals sum_r n_r u(r); each bin price <= u(r); hence every bin attains u(r)',
                  structure=structure,
                  witness=summary, declared_profile_checked_against_census=True,
                  second_witness=dict(source='REVIEW.md blind hand construction, transcribed as data', **second),
                  realizations_checked=2, patterns_with_different_counts=differing,
                  nonuniqueness='two distinct checked realizations; no statement about any other count vector',
                  witness_file_sha256=sha256_bytes(witness_bytes), witness_canonical_sha256=sha256_bytes(canonical(document)),
                  source_sha256=pins,
                  scope='Aggregate capacity-tagged whole-helper pattern feasibility only. No chronology, owner geometry, physical schedule, controller, invoice or kappa claim; the selected PR1042 supplier is outside scope.')
    if run_controls:
        result['negative_controls'] = negative_controls(entries, document, agg, upper, root, pins, patterns)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repository', type=Path, default=HERE.parents[1], help='checkout root holding the pinned source files')
    parser.add_argument('--write', type=Path, help='write a fresh EXPECTED.json after all checks pass (refuses to overwrite)')
    parser.add_argument('--json', action='store_true', help='print the full certificate')
    parser.add_argument('--no-controls', action='store_true')
    args = parser.parse_args()
    result = certificate(args.repository.resolve(), run_controls=not args.no_controls)
    normalized = json.loads(json.dumps(result, sort_keys=True))
    if args.write:
        require(not args.write.exists(), 'refusing to overwrite ' + str(args.write))
        require(args.write.parent.is_dir(), 'output directory does not exist: ' + str(args.write.parent))
        args.write.write_text(json.dumps(normalized, indent=2, sort_keys=True) + '\n')
    else:
        expected = load_json(HERE / 'EXPECTED.json', 'EXPECTED.json')
        if args.no_controls:
            expected.pop('negative_controls', None)
        require(normalized == expected, 'certificate differs from EXPECTED.json')
    if args.json:
        print(json.dumps(normalized, indent=2, sort_keys=True))
    print('%s patterns=%d witness_bins=%d witness_patterns=%d realizations=%d controls=%d no_new_kappa' % (
        STATUS, result['legal_patterns'], result['witness']['bins'], result['witness']['distinct_patterns'],
        result['realizations_checked'], len(result.get('negative_controls', []))))


if __name__ == '__main__':
    try:
        main()
    except Reject as error:
        print('FAIL_T29_CAPACITY_TAGGED_PATTERN_WITNESS: ' + str(error.args[0]), file=sys.stderr)
        sys.exit(1)
