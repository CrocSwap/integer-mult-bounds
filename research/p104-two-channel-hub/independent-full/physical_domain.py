"""Independent event-grid coverage check for the frozen P104 pivot domain.

Jerry Chen / @CubeJerry with OpenAI Codex assistance. Apache-2.0.
This checks physical occupancy, not scalar histories or pairing ranks.
"""
from bisect import bisect_right
from collections import Counter, defaultdict


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frame_masks(bases):
    masks = []
    for basis in bases:
        values = [0]
        for vector in basis:
            require(vector not in values, "dependent frame basis")
            values += [value ^ vector for value in values]
        masks.append(sum(1 << value for value in values))
    return masks


def check_domain(word, receipt, prefix_times):
    """Check every event boundary/MOVE midpoint against the certified cuts.

    prefix_times maps frame IDs to all independently reconstructed NONZERO
    collection-contact times. Every unsampled cut is dominated by its preceding
    certified cut: the collection history is unchanged, the later history only
    shrinks, and its resident pivot set is a subset of the certified one.
    """
    masks = frame_masks(word['frames'])
    # Identical physical spans can have different basis encodings. In this
    # frozen source each duplicate class has at most one original-use label.
    # An unused alias has only subdivision contacts; the used representative
    # receives the same MOVE contacts and every original residence/contact.
    original_use = set(word['initial']) | set(word['final'])
    for event in word['program']:
        if event[0] == 'MOVE':
            original_use.update(event[2:4])
        elif event[0] in ('INIT', 'CLEAR'):
            original_use.add(event[2])
        else:
            original_use.add(event[-1])
    classes = defaultdict(list)
    for frame, mask in enumerate(masks):
        classes[mask].append(frame)
    aliases = []
    for labels in classes.values():
        if len(labels) < 2:
            continue
        used = [frame for frame in labels if frame in original_use]
        require(len(used) <= 1, 'duplicate physical frames with distinct original uses')
        representative = used[0] if used else min(labels)
        aliases.extend([frame, representative] for frame in labels if frame != representative)

    def strict(a, b):
        return masks[a] != masks[b] and masks[a] & masks[b] == masks[a]

    public = word['public']
    main = set(word['live']) | {x + 112 for x in word['live']}
    helpers = set(range(public)) - main
    groups = defaultdict(set)
    role_group = {}
    for role in helpers:
        key = (word['initial'][role], word['final'][role])
        groups[key].add(role)
        role_group[role] = key
    require(len(groups) == receipt['group_count'], "all boundary groups")
    eligible = {g for g, roles in groups.items()
                if len(roles) >= 2 and len(word['frames'][g[1]]) - len(word['frames'][g[0]]) >= 2}
    require(len(eligible) == receipt['checked_groups'], "eligible boundary groups")
    require({tuple(g['boundary']) for g in receipt['groups']} == eligible,
            "complete checked-group inventory")
    require({tuple(g['boundary']) for g in receipt['skipped_groups']} == set(groups) - eligible,
            "complete skipped-group inventory")

    cuts = defaultdict(dict)
    for group in receipt['groups']:
        g = tuple(group['boundary'])
        require(group['eligible_helpers'] == len(groups[g]), "helper count")
        for frame, time, pivots, _c, _d, _rank in group['census']:
            key = (*g, frame)
            require(time not in cuts[key], "duplicate certified cut")
            require(len(pivots) >= 2 and set(pivots) <= groups[g], "certified pivots")
            require(strict(g[0], frame) and strict(frame, g[1]), "strict pivot frame")
            cuts[key][time] = frozenset(pivots)
    ordered = {key: sorted(times) for key, times in cuts.items()}
    prefixes = {int(f): sorted(set(times)) for f, times in prefix_times.items()}
    charts = word['initial'][:] + [None] * word['owned_fields']
    banks = defaultdict(set)
    for role in helpers:
        banks[(*role_group[role], charts[role])].add(role)
    live_owned = set()
    seen = set()
    counts = Counter()
    valid = {}

    def inspect(time):
        counts['sampled_global_times'] += 1
        for key, residents in banks.items():
            if len(residents) < 2:
                continue
            if key not in valid:
                a, b, frame = key
                valid[key] = (a, b) in eligible and strict(a, frame) and strict(frame, b)
            if not valid[key]:
                continue
            counts['eligible_grid_cuts'] += 1
            times = ordered.get(key, [])
            at = bisect_right(times, time) - 1
            require(at >= 0, "eligible grid cut lacks preceding certificate")
            previous = times[at]
            pivots = cuts[key][previous]
            require(residents <= pivots, "uncertified resident pivot")
            contacts = prefixes.get(key[2], [])
            require(bisect_right(contacts, time) == bisect_right(contacts, previous),
                    "new collection contact after preceding certificate")
            if previous == time:
                require(residents == pivots, "wrong certified pivot set")
                seen.add((key, time))
            else:
                counts['dominated_grid_cuts'] += 1

    inspect(0)
    interiors = {}
    for index, event in enumerate(word['program']):
        op, role = event[:2]
        if op == 'MOVE':
            a, b, private = event[2:]
            require(charts[role] == a and bool(private) == (role in live_owned),
                    "MOVE source/ownership")
            require(strict(b, a) if private else strict(a, b), "nested MOVE")
            pair = (a, b)
            if pair not in interiors:
                interiors[pair] = [f for f in range(len(masks))
                                   if strict(a, f) and strict(f, b)
                                   or strict(b, f) and strict(f, a)]
            if role in helpers:
                g = role_group[role]
                banks[(*g, a)].remove(role)
                for frame in interiors[pair]:
                    banks[(*g, frame)].add(role)
            inspect(2 * index + 1)
            if role in helpers:
                for frame in interiors[pair]:
                    banks[(*g, frame)].remove(role)
                banks[(*g, b)].add(role)
            charts[role] = b
        elif op == 'INIT':
            require(role >= public and role not in live_owned, "owned INIT")
            live_owned.add(role)
            charts[role] = event[2]
        elif op == 'CLEAR':
            require(role in live_owned and charts[role] == event[2], "owned CLEAR")
            live_owned.remove(role)
            charts[role] = None
        elif op == 'SCALE':
            require(charts[role] == event[-1], "SCALE chart")
        else:
            require(op in ('ADD', 'COPY'), "known opcode")
            require(charts[role] == charts[event[2]] == event[-1], "common scalar chart")
        inspect(2 * index + 2)
    expected = {(key, time) for key, times in cuts.items() for time in times}
    require(seen == expected, "all certificate cuts physically realized")
    require(len(seen) == receipt['critical_cuts'], "critical cut count")
    require(charts[:public] == word['final'] and not live_owned, "physical endpoints")
    counts['matched_certificate_cuts'] = len(seen)
    counts['boundary_groups'] = len(groups)
    result = dict(sorted(counts.items()))
    result['unused_physical_aliases'] = aliases
    return result


def domain_controls():
    """Positive midpoint/gap cases and real altered-certificate controls."""
    from copy import deepcopy
    word = {'public': 2, 'owned_fields': 0, 'live': [],
            'frames': [[], [1], [1, 2], [1, 2, 4]],
            'initial': [0, 0], 'final': [3, 3],
            'program': [['MOVE', 0, 0, 2, False],
                        ['MOVE', 1, 0, 3, False],
                        ['MOVE', 0, 2, 3, False]]}
    receipt = {'group_count': 1, 'checked_groups': 1, 'skipped_groups': [],
               'critical_cuts': 1,
               'groups': [{'boundary': [0, 3], 'eligible_helpers': 2,
                           'census': [[2, 3, [0, 1], 0, 0, 0]]}]}
    midpoint = check_domain(word, receipt, {})
    require(midpoint['matched_certificate_cuts'] == 1, 'midpoint positive control')
    bad = deepcopy(receipt)
    bad['groups'][0]['census'] = []
    bad['critical_cuts'] = 0
    try:
        check_domain(word, bad, {})
    except ValueError as exc:
        require('lacks preceding' in str(exc), 'omitted midpoint rejection reason')
    else:
        raise ValueError('omitted midpoint accepted')
    gapword = {'public': 3, 'owned_fields': 0, 'live': [0],
               'frames': word['frames'], 'initial': [3, 0, 0], 'final': [3, 3, 3],
               'program': [['MOVE', 1, 0, 2, False], ['MOVE', 2, 0, 2, False]]
                          + [['SCALE', 0, '1', 3]] * 3
                          + [['MOVE', 1, 2, 3, False], ['MOVE', 2, 2, 3, False]]}
    gaps = {'group_count': 1, 'checked_groups': 1, 'skipped_groups': [],
            'critical_cuts': 2,
            'groups': [{'boundary': [0, 3], 'eligible_helpers': 2,
                        'census': [[2, 4, [1, 2], 0, 0, 0],
                                   [2, 10, [1, 2], 0, 0, 0]]}]}
    gap = check_domain(gapword, gaps, {2: [2, 4]})
    require(gap['dominated_grid_cuts'] == 2, 'gap positive control')
    try:
        check_domain(gapword, gaps, {2: [2, 4, 8]})
    except ValueError as exc:
        require('new collection contact' in str(exc), 'new contact rejection reason')
    else:
        raise ValueError('uncovered contact accepted')
    bad = deepcopy(gaps)
    bad['groups'][0]['census'][0][2] = [1, 99]
    try:
        check_domain(gapword, bad, {2: [2, 4]})
    except ValueError as exc:
        require('certified pivots' in str(exc), 'wrong pivot rejection reason')
    else:
        raise ValueError('wrong pivot accepted')
    return {'midpoint': midpoint, 'gap': gap,
            'rejected': ['omitted_midpoint', 'uncovered_contact', 'wrong_pivot']}
