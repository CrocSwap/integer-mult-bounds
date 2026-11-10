"""All raw contact phases and retained axes, by direct parity expansion."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
import hashlib
import json

from common import digest, integer, require

AXES = tuple(1 << j for j in range(265))


def normalized(entries):
    counts = Counter()
    for vector, coefficient in entries:
        integer(vector, 1, (1 << 265)-1, 'spectral source axis')
        require(type(coefficient) is int, 'spectral integer coefficient')
        counts[vector] += coefficient
    return tuple(sorted((v, a % 4) for v, a in counts.items() if a % 4))


@lru_cache(maxsize=2048)
def phase(entries):
    linear = [0]*265
    mixed = set()
    for vector, coefficient in entries:
        bits = [j for j in range(265) if vector >> j & 1]
        for j in bits:
            linear[j] = (linear[j]+coefficient) % 4
        if coefficient % 2:
            mixed.symmetric_difference_update(combinations(bits, 2))
    return tuple(linear), frozenset(mixed)


def translation(moved, target, keep):
    require(moved[1] == target[1], 'all265 mixed spectator phases cancel at contact')
    difference = tuple((b-a) % 4 for a, b in zip(moved[0], target[0]))
    require(len(moved[0]) == len(target[0]) == 265, 'all raw phase coordinates present')
    require(all(v in (0, 2) for v in difference), 'contact correction is translation, with no discarded phase')
    result = sum((v//2) << j for j, v in enumerate(difference))
    require(result & ~keep == 0, 'actual translation avoids omitted spectators')
    return result


def certify(word, controller, source, result, prior):
    recipes = {r['q']: r for r in source['recipes']}
    require(len(recipes) == len(source['recipes']), 'distinct original ports')
    events = [e for e in controller['physical_events'] if e[0] == 'LOCAL']
    stages = [e[1] for e in events]
    require(stages == [0]+list(range(1, 32, 2))+[32], 'actual retained stage order')
    retained = tuple(range(9))+tuple(j for s in stages if s for j in range(9+8*(s-1), 9+8*s))
    require(len(retained) == len(set(retained)) == 145, '145 retained source axes')
    keep = sum(1 << j for j in retained)
    contacts = []
    partial_axes = 0
    for _, stage, _, backward in events:
        require(backward is False, 'actual forward source body')
        fresh = AXES[9+8*(stage-1):9+8*stage] if stage else ()
        for q in word['ports']:
            integer(q, 1, 511, 'source main port')
            b = tuple(recipes[q]['idle_children'][0]['orthogonal_axes'][:8])
            basis = (q,)+b
            require(len(basis) == 9 and all(type(v) is int and 0 < v < 512 for v in basis)
                    and all((v & w).bit_count() % 2 == int(i == j)
                            for i, v in enumerate(basis) for j, w in enumerate(basis)), 'actual orthonormal source basis')

            def route(vector):
                changed = vector
                for old, new in zip(b, fresh):
                    if ((vector & old).bit_count() ^ (vector & new).bit_count()) & 1:
                        changed ^= old ^ new
                return changed

            require(all(route(v) == v for j, v in enumerate(AXES) if j not in retained), 'omitted raw axes fixed')
            require(route(q) == q and all(route(route(v)) == v for v in AXES), 'complete invertible source route')
            raw_x = [(q, 1)] if stage == 0 else [(v, 1) for v in AXES[:9+8*(stage-1)]]
            raw_y = [] if stage == 0 else raw_x+[(q, -1)]
            spectators = [(v, 1) for v in AXES[9:9+8*stage]]
            entry_x, entry_y = spectators+[(q, 1)], spectators
            exit_x = spectators+[(v, 1) for v in AXES[:9]]
            exit_y = exit_x+[(q, -1)]
            out_x = [(v, 1) for v in AXES[:9+8*stage]]
            out_y = out_x+[(q, -1)]
            maps = []
            for before, after in ((raw_x, entry_x), (raw_y, entry_y), (exit_x, out_x), (exit_y, out_y)):
                moved = phase(normalized([(route(v), a) for v, a in before]))
                target = phase(normalized(after))
                move = translation(moved, target, keep)
                inverse = route(move)
                require((move | inverse) & ~keep == 0, 'actual translations avoid omitted spectators')
                maps.append({'translation': move, 'inverse_translation': inverse})
            contacts.append([stage, q, maps])
            require(all(v & ~keep == 0 for v in basis+fresh), 'partial child axes lie in retained factor')
            partial_axes += len(basis)+len(fresh)
    # The source registry preserves the two map-key insertion orders.
    route_hash = hashlib.sha256(json.dumps(contacts, separators=(',', ':')).encode()).hexdigest()
    require(route_hash == result['physical_caller']['route_payload_sha256']
            == prior['whole_job_algebra']['source_route_payload_sha256'], 'exact existing contact payload, including phases')
    whole = prior['whole_job_algebra']
    require((whole['source_dimension'], whole['retained_source_rows'], whole['omitted_identity_spectator_rows'])
            == (265, 145, 120), 'same A1 retained-coordinate theorem')
    for event in controller['physical_events']:
        if event[0] == 'IDLE':
            require(set(event[2]) <= set(stages), 'whole-idle selected stages only')
    for diagonal in controller['diagonal']:
        require(len(diagonal) == 34 and all(type(v) is int for v in diagonal), 'main Laurent signature')
        require(all(not v or j in stages for j, v in enumerate(diagonal[1:])), 'main endpoint selected stages only')
    return {'raw_dimension': 265, 'retained_axes': list(retained), 'omitted_axes': 120,
            'complete_contacts': 4*len(contacts), 'all265_phase_checks': 4*len(contacts),
            'partial_local_and_fresh_axes_checked': partial_axes, 'route_payload_sha256': route_hash,
            'normalizer_prefix_rule': 'complete permutation times a Clifford on145f retained axes',
            'arbitrary_additional_spectators': True}
