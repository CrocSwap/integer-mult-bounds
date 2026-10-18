#!/usr/bin/env python3
"""Exact pre-construction invoice for helper withdrawal and owner restoration.

Prepared for androolloyd with substantial OpenAI Codex assistance. Apache-2.0.
Deleted helper computations are granted free, not claimed implemented.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def mass(h):
    return sum(r*n for r, n in h.items())


def clean(h):
    need(all(n >= 0 for n in h.values()), 'negative child count')
    return Counter({r: n for r, n in h.items() if n})


def schedule():
    """Independent transcription of the nine-stage chronological recipe."""
    result = [dict(kind='local', stage=0, pair=0)]
    idle = 0
    for pair in range(4):
        result.append(dict(kind='local', stage=2*pair+1, pair=pair))
        if pair < 3:
            result.append(dict(kind='idle', pair=pair+1, rank=14*(pair+1), idx=idle))
            idle += 1
            result.append(dict(kind='bridge', dst=pair, src=pair+1))
        result.append(dict(kind='local', stage=2*pair+2, pair=pair))
        if pair < 3:
            result.append(dict(kind='idle', pair=pair+1, rank=7, idx=idle))
            idle += 1
            result.append(dict(kind='bridge', dst=pair, src=pair+1))
        else:
            for p in range(4):
                result.append(dict(kind='idle', pair=p, rank=14*(3-p), idx=idle))
                idle += 1
    for pair in range(2, -1, -1):
        result.append(dict(kind='bridge', dst=pair+1, src=pair))
    return result


def windows(events):
    """Read each window backward, rather than tracking the parent's last-touch table."""
    result = {}
    for pos, event in enumerate(events):
        if event['kind'] != 'idle':
            continue
        stages = []
        p = event['pair']
        for before in reversed(events[:pos]):
            if before['kind'] == 'local':
                if before['pair'] == p:
                    break
                stages.append(before['stage'])
            if before['kind'] == 'bridge' and p in (before['src'], before['dst']):
                break
        result[event['idx']] = (p, event['rank'], frozenset(stages))
    return result


def expand(selection, win):
    """Independent literal owner allocation from the frozen integer selection."""
    demands = defaultdict(list)
    for idx, width, stage, count in sorted(selection['stages']):
        need(width == 8 and stage in win[idx][2], 'stage outside untouched window')
        demands[idx].extend([stage]*count)
    next_helper = Counter()
    slots = []
    remainder = {}
    patterns = defaultdict(list)
    for idx, widths, count in selection['patterns']:
        need(idx in win and count > 0 and all(w == 8 for w in widths), 'bad pattern')
        patterns[idx].append((tuple(widths), count))
    for idx in sorted(win):
        copy = take = 0
        for widths, count in sorted(patterns[idx], key=lambda z: (-sum(z[0]), z[0])):
            need(sum(widths) <= win[idx][1], 'overfull owner')
            for _ in range(count):
                offset = 0
                for width in widths:
                    need(take < len(demands[idx]), 'missing stage demand')
                    stage = demands[idx][take]
                    helper = next_helper[stage]
                    slots.append((idx, copy, offset, width, stage, helper))
                    next_helper[stage] += 1
                    offset += width
                    take += 1
                remainder[idx, copy] = win[idx][1] - offset
                copy += 1
        need(copy == 222 and take == len(demands[idx]), 'incomplete owner selection')
    need(next_helper == Counter({s: 439 for s in range(9)}), 'helper coverage')
    return slots, remainder


def audit_slots(slots, win):
    occupied = set()
    helpers = set()
    for idx, copy, offset, width, stage, helper in slots:
        need(stage in win[idx][2], 'untouched ownership lifetime')
        need(0 <= copy < 222 and width == 8 and 0 <= offset <= win[idx][1]-width,
             'owner coordinate range')
        need((stage, helper) not in helpers and 0 <= helper < 439, 'duplicate helper owner')
        helpers.add((stage, helper))
        for axis in range(offset, offset+width):
            key = idx, copy, axis
            need(key not in occupied, 'overlapping owner coordinates')
            occupied.add(key)
    need(len(helpers) == 9*439, 'missing helper owner')
    return len(occupied)


def role_profiles(word, budget):
    dims = [budget.rational_rank(word['lines'][i] for i in frame) for frame in word['frames']]
    current = word['start'][:]
    profiles = [Counter() for _ in current]

    def visit(role, frame):
        old = current[role]
        need(set(word['frames'][old]) <= set(word['frames'][frame]), 'nonnested role path')
        delta = dims[frame]-dims[old]
        if delta:
            profiles[role][delta] += 1
        current[role] = frame

    for section in ('D', 'A', 'B', 'C'):
        for frame, target, sources in word[section]:
            for role in [target, *sources]:
                visit(role, frame)
    for role, frame in enumerate(word['final']):
        visit(role, frame)
    need(all(mass(h) == 7 for h in profiles[:222]), 'data boundary ranks')
    need(all(mass(h) == 8 for h in profiles[222:]), 'helper boundary ranks')
    total = Counter({7: 9})
    for h in profiles:
        total.update(h)
    return profiles, total


def decoder_cache(word, budget, win):
    """An exact scalar sharing candidate, before ADDRESS-chart realization.

    The last source bank is the XOR of the preceding eight. Nine running
    accumulators suffice; retaining all 72 previous forms is unnecessary.
    """
    rows = [1 << i for i in range(8)]
    inputs = [rows[0]]
    rows[1] ^= rows[0]
    for pair in range(4):
        inputs.append(rows[2*pair+1])
        rows[2*pair] ^= rows[2*pair+1]
        if pair < 3:
            rows[2*pair] ^= rows[2*(pair+1)]
            rows[2*(pair+1)+1] ^= rows[2*pair+1]
        inputs.append(rows[2*pair])
        rows[2*pair+1] ^= rows[2*pair]
        if pair < 3:
            rows[2*pair] ^= rows[2*(pair+1)]
            rows[2*(pair+1)+1] ^= rows[2*pair+1]
    for pair in range(2, -1, -1):
        rows[2*(pair+1)] ^= rows[2*pair]
        rows[2*pair+1] ^= rows[2*(pair+1)+1]
    for pair in range(4):
        rows[2*pair], rows[2*pair+1] = rows[2*pair+1], rows[2*pair]
    need(rows == [1 << i for i in range(8)], 'global scalar boundary')
    need(inputs == [1, 3, 6, 14, 26, 58, 106, 234, 170], 'source bank masks')
    parity = 0
    for mask in inputs:
        parity ^= mask
    need(parity == 0 and budget.binary_rank(inputs[:8]) == 8, 'unique nine-stage dependence')

    v = word['v']
    local = [1 << i for i in range(2*v+word['R'])]
    for _, target, sources in word['A']:
        for source in sources:
            local[target] ^= local[source]
    source_forms = [local[r] & ((1 << v)-1) for r in word['ret']]
    dirty_forms = [local[r] >> (2*v) for r in word['ret']]
    reverse = [1 << i for i in range(2*v+word['R'])]
    for section in ('C', 'B'):
        for _, target, sources in reversed(word[section]):
            for source in sources:
                reverse[target] ^= reverse[source]
    need([reverse[r] for r in word['ret']] == [local[r] for r in word['ret']],
         'reflected scalar copy totals differ')
    need(budget.binary_rank(source_forms) == budget.binary_rank(dirty_forms) == 9,
         'source and dirty total ranks')
    # Each bit is an independent (original bank, live port) source input.
    version = []
    for mask in inputs:
        version.append([sum(form << (v*b) for b in range(8) if mask >> b & 1)
                        for form in source_forms])
    accumulators = [0]*9
    for stage in range(8):
        accumulators = [a ^ b for a, b in zip(accumulators, version[stage])]
    need(accumulators == version[8], 'running source total identity')
    # Supposed raw-total reuse has an independent dirty column in every
    # stage, even though its source contribution cancels.
    dirty_parities = [sum(form << (439*s) for s in range(9)) for form in dirty_forms]
    need(budget.binary_rank(dirty_parities) == 9, 'raw totals do not cancel dirt')
    need(not any(set(range(9)) <= set(stages) for _, _, stages in win.values()),
         'unexpected full-lifetime idle owner')
    return dict(source_bank_masks=inputs, source_bank_rank=8,
                source_forms_rank=9, dirty_forms_rank=9,
                symbolic_source_columns=8*v, independent_dirty_columns=9*439,
                running_accumulator_rows_per_replica=9,
                running_accumulator_rows_all_replicas=9*32,
                dirty_extraction_temporary_rows=9,
                prospective_physical_rows=28425+9*32+9,
                productive_denominator=28416,
                raw_total_parity_nonzero_rank=9,
                existing_whole_lifetime_owner_windows=0,
                dirty_form_xor_scans_per_invocation=sum(x.bit_count() for x in dirty_forms),
                accumulation_xor_scans_all_replicas=8*9*32,
                dirty_cancellation_xor_scans_first_eight_stages=8*9*32,
                saved_copy_rank_global=9*7*32,
                saved_copy_rank_per_invocation=Q(9*7*32, 288),
                address_chart_alignment_proved=False,
                scope='Exact source-only scalar identity; copy saving is an upper credit before new realization and transport costs.')


def main(out):
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for path, digest in sources['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'source hash: '+path)
    budget = module('sharing_budget', 'research/bit-role-sharing-budget/verify.py')
    mercator = module('independent_moment', 'research/complex-k492-owner-repair/vendor/multicold/engines/moment.py')
    hosting = module('parent_hosting', 'research/idle-axis-hosting/hosting_core.py')
    _, word, expected, constants = budget.pinned_inputs()
    local, local_receipt = budget.extract_word(word, expected['word'])
    profiles, total = role_profiles(word, budget)
    need(total == local, 'role partition differs from full Boolean replay')
    events = schedule()
    all_win = windows(events)
    need(all_win == hosting.windows(events), 'independent window disagreement')
    win = {i: w for i, w in all_win.items() if w[1] and w[2]}
    selection = json.loads((ROOT/'research/e8-bit-p111/data/selection9-p111.json').read_text())['bit']
    slots, rem = expand(selection, win)
    occupied = audit_slots(slots, win)
    ys = {(i, tuple(p)): n for i, p, n in selection['patterns']}
    zs = {(i, w, s): n for i, w, s, n in selection['stages']}
    parent_slots, parent_rem = hosting.expand(win, ys, zs, {s: [(h, 8) for h in range(439)] for s in range(9)}, 222)
    need(slots == parent_slots and rem == parent_rem, 'independent owner allocation disagreement')

    def idle_profile(remainders):
        h = Counter()
        for i, (_, rank, _) in all_win.items():
            if i in win:
                for copy in range(222):
                    if remainders[i, copy]:
                        h[remainders[i, copy]] += 32
            elif rank:
                h[rank] += 222*32
        return h

    idle = idle_profile(rem)
    need(idle == Counter(constants['REM']), 'reconstructed frozen remainder')
    base = Counter({r: 288*n for r, n in local.items()}) + idle
    need(dict(base) == {int(r): n for r, n in expected['nine']['profile'].items()}, 'baseline full invoice')
    checked = 0

    def price(h, root=False):
        nonlocal checked
        h = clean(h)
        first = budget.moment(h, Q(1, 99))
        second = mercator.moment(h, 64, 28416, Q(1, 99), bad=True)
        need(max(first[0], second[0]) <= min(first[1], second[1]), 'independent interval disagreement')
        need(first[1] < 1 or first[0] > 1, 'ambiguous strict target sign')
        checked += 1
        result = dict(profile=dict(sorted(h.items())), rank_mass=mass(h),
                      deficit=64*28416-mass(h), calls=sum(h.values()),
                      target_moment_interval=list(first),
                      target_moment_display=format(float(first[1]), '.16g'),
                      passes_target_arithmetic=first[1] < 1)
        if root:
            result['root'] = budget.bracket_root(h)
        return result

    def withdrawal(removed, root=False):
        # Grant a replacement producer for free. Charge every vacated owner
        # direction at the original idle boundary, joined with its old tail.
        h = base.copy()
        for helper in removed:
            for rank, count in profiles[222+helper].items():
                h[rank] -= 288*count
        returned = rem.copy()
        owners = []
        for idx, copy, offset, width, stage, helper in slots:
            if helper in removed:
                returned[idx, copy] += width
                owners.append([idx, copy, offset, width, stage, helper])
        new_idle = idle_profile(returned)
        h.subtract(idle)
        h.update(new_idle)
        h = clean(h)
        local_credit = 288*8*len(removed)
        boundary_debit = mass(new_idle)-mass(idle)
        need(local_credit == boundary_debit and mass(h) == mass(base), 'unpaid vacated owner axes')
        return dict(removed_helper_indices=sorted(removed),
                    gross_local_rank_credit=local_credit,
                    owner_boundary_rank_debit=boundary_debit, net_rank_credit=0,
                    idle_profile=dict(sorted(new_idle.items())), invoice=price(h, root),
                    returned_slots_one_replica=owners)

    singles = []
    for helper in range(439):
        result = withdrawal({helper})
        singles.append((result['invoice']['target_moment_interval'][1], helper))
    thirteen = withdrawal(set(range(13)), True)
    all_helpers = withdrawal(set(range(439)), True)
    cache = decoder_cache(word, budget, win)
    cache_best_case = base.copy()
    cache_best_case[7] -= 9*32
    cache['best_case_invoice'] = price(cache_best_case, True)
    # Independent of how much consolidation is later obtained, this one
    # linear dependence cannot remove 100 units from the complete invoice.
    need(cache['saved_copy_rank_per_invocation'] == 7, 'cache credit')

    # This refinement keeps the 222 forced data climbs at rank <=7, while
    # still granting fractional rank-8 packing of every other local unit.
    fences = {}
    for removed_mass in (99, 100, 101, 102):
        h = idle.copy()
        h[7] += 288*222
        h[8] += 288*Q(3512+63-removed_mass, 8)
        fences[str(removed_mass)] = price(h)
    need(not fences['101']['passes_target_arithmetic'] and fences['102']['passes_target_arithmetic'],
         'rank-seven boundary fence')

    # Stronger escape control: changing hosting changes the moment even
    # when it does not change mass. Erase every helper at zero producer cost,
    # grant unfragmented data climbs, and separately grant zero COPY cost.
    no_helpers_idle = Counter(all_helpers['idle_profile'])
    unlimited = {}
    for copy_mass in (63, 0):
        h = no_helpers_idle.copy()
        h[7] += 288*(222+Q(copy_mass, 7))
        unlimited[str(copy_mass)] = price(h, True)
    need(not unlimited['63']['passes_target_arithmetic'] and unlimited['0']['passes_target_arithmetic'],
         'scope control: joint boundary relaxation')

    controls = []
    def reject(name, action):
        try:
            action()
        except (ValueError, KeyError):
            controls.append(name)
        else:
            raise ValueError('negative control accepted: '+name)
    bad = slots[:]
    bad[1] = bad[0]
    reject('duplicate owner and helper', lambda: audit_slots(bad, win))
    bad = slots[:]
    old = list(bad[0]); old[4] = next(s for s in range(9) if s not in win[old[0]][2]); bad[0] = tuple(old)
    reject('cache carried beyond untouched lifetime', lambda: audit_slots(bad, win))
    bad = slots[:]
    old = list(bad[0]); old[2] = win[old[0]][1]; bad[0] = tuple(old)
    reject('owner coordinate outside pending frame', lambda: audit_slots(bad, win))
    reject('104 gross rank units reported as net', lambda: need(thirteen['net_rank_credit'] == 288*104, 'gross is not net'))
    reject('100 admitted without data rank-seven boundaries', lambda: need(fences['100']['passes_target_arithmetic'], 'target fails'))
    reject('free helpers alone admitted', lambda: need(unlimited['63']['passes_target_arithmetic'], 'target fails'))

    owner_digest = hashlib.sha256(json.dumps(slots, separators=(',', ':')).encode()).hexdigest()
    result = dict(status='PASS_PREBUILD_HOSTING_GATE_NO_100_NET_UNIT_CONSTRUCTION',
                  success_goal_met=False, supplier_built=False, target_saving=Q(1, 99),
                  live=28416, physical=28425, local_invocations=288,
                  baseline=price(base, True), local_replay=local_receipt,
                  hosting=dict(windows={i: [p, r, sorted(s)] for i, (p, r, s) in all_win.items()},
                               slots_per_replica=len(slots), slots_all_replicas=32*len(slots),
                               occupied_coordinates_per_replica=occupied, owner_sha256=owner_digest,
                               independent_parent_expansion_equal=True),
                  thirteen_helper_withdrawal=thirteen, all_helpers_free=all_helpers,
                  nine_stage_running_decoder_cache=cache,
                  all_single_withdrawals=dict(count=439, net_rank_credit_each=0,
                                             lowest_moment_helper=min(singles)[1],
                                             lowest_moment_upper=min(singles)[0],
                                             highest_moment_helper=max(singles)[1],
                                             highest_moment_upper=max(singles)[0]),
                  rank_seven_boundary_fences=fences,
                  joint_free_helper_and_copy_relaxations=unlimited,
                  largest_net_mass_credit_from_copy_erasure_per_invocation=63,
                  target_100_mass_credit_requires_effective_copy_mass=-37,
                  negative_controls=controls)
    # Keep the all-helper receipt compact; the source-bound deterministic
    # expander and its digest reconstruct all slots without a large duplicate.
    result['all_helpers_free'].pop('returned_slots_one_replica')
    result['independent_moment_comparisons'] = checked
    out.write_text(json.dumps(result, indent=2, sort_keys=True, default=str)+'\n')
    print(result['status'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    main(args.out)
