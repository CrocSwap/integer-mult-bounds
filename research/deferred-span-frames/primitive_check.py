#!/usr/bin/env python3
"""Independent finite check of deferred reconstruction with dirty scratch.

This is a scalar/frame primitive, not a full inherited endpoint construction.
Every scratch bit is arbitrary. Coordinate frames are literal subsets of a
four-dimensional rational space, so containment and transition ranks are exact.
"""
import hashlib
import json
from pathlib import Path
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')


def check_three_carriers():
    # Independent a,b,c are retired; their span represents a+b+c, while
    # no subset of fewer than three of these retired carriers does so.
    ns, nt, nr, h = 4, 2, 9, 5
    offset = ns + nt
    prefix = [(3,0),(4,1),(5,2),
              (6,3),(6,4),(6,5),(7,3),(7,4),(7,5)]
    clearing = [(6,7)]
    reuse = [(6,8)]
    reconstruction = [(0,1),(0,2)]
    inject = [(offset+s,i) for s,i in ((0,0),(1,1),(2,2),(8,3))]
    scatter = [(ns,offset),(ns+1,offset+6)]
    def dirty_word(middle, dual=False):
        middle = [(offset+a,offset+b) for a,b in middle]
        word = middle+scatter+middle[::-1]+inject+middle+scatter+middle[::-1]+inject
        original = [1<<i for i in range(ns+nt+nr)]
        state = original.copy()
        for a,b in reversed(word) if dual else word:
            if dual:a,b=b,a
            state[a] ^= state[b]
        expected = original.copy()
        if dual:
            for i in (0,1,2):expected[i] ^= original[ns]
            expected[3] ^= original[ns+1]
        else:
            expected[ns] ^= original[0]^original[1]^original[2]
            expected[ns+1] ^= original[3]
        return state == expected
    scalar = prefix+clearing+reuse+reconstruction
    assert dirty_word(scalar) and dirty_word(scalar,True)
    negative = {
        'omitted_third_carrier': prefix+clearing+reuse+[(0,1)],
        'corrupted_third_control': prefix+clearing+reuse+[(0,1),(0,8)],
        'destroyed_reserved_third_carrier': prefix+clearing+reuse+[(2,8)]+reconstruction,
        'uncleared_reused_carrier': prefix+reuse+reconstruction,
    }
    for middle in negative.values():
        assert not dirty_word(middle) and not dirty_word(middle,True)
    # The fresh signals alone determine dependency; actual scratch remains
    # arbitrary and is checked by the complete dirty wrapper above.
    signals = [1,2,4]
    assert all(sum(signals[i] for i in range(3) if mask>>i&1)!=7 for mask in range(7))
    frames = [0]*nr;events=[];mass=0
    def raise_to(s,target):
        nonlocal mass
        old=frames[s];assert not old & ~target
        mass += target.bit_count()-old.bit_count()
        events.append([s,old,target]);frames[s]=target
    def gate(a,b,target):raise_to(a,target);raise_to(b,target)
    for s,target in ((0,1),(1,2),(2,4),(8,1)):raise_to(s,target)
    for (a,b),target in zip(prefix[:3],(1,2,4)):gate(a,b,target)
    for s,target in ((0,9),(1,18),(2,20)):raise_to(s,target)
    assert all(frames[s] & ~7 for s in (0,1,2))
    for a,b in prefix[3:]+clearing+reuse:gate(a,b,7)
    for a,b in reconstruction:gate(a,b,31)
    for s in range(nr):raise_to(s,31)
    assert mass==nr*h==45
    return dict(status='passed',scratch_roles=nr,witness_carriers=3,
        no_one_or_two_carrier_witness_in_retired_set=True,
        arbitrary_basis_bits_checked_in_each_orientation=ns+nt+nr,
        external_map=['target_0 += source_a + source_b + source_c','target_1 += source_d'],
        both_orientations=True,all_frames_monotone=True,
        completed_scratch_rank_mass=mass,rank_excess_above_monotone_potential=0,
        negative_controls_rejected_in_both_orientations=list(negative),frame_events=events)


def check():
    # Three sources, two targets, seven arbitrary dirty scratch carriers.
    ns, nt, nr, h = 3, 2, 7, 4
    offset = ns + nt
    # Scratch labels: Q_a,Q_b,a_copy,b_copy,P,C,source_c.
    prefix = [(2,0),(3,1),(4,2),(4,3),(5,2),(5,3),
              (2,3),(2,4),(2,6)]
    migration = [(4,5)]  # P is cleared by the duplicate current anchor C.
    new_use = [(4,2)]    # Freed P now holds the unrelated value c.
    reconstruction = [(0,3)]  # Q_a + b_copy supplies old P's promised a+b.
    scalar = prefix + migration + new_use + reconstruction
    inject = [(offset+0,0),(offset+1,1),(offset+6,2)]
    scatter = [(ns+0,offset+0),(ns+1,offset+4)]

    def dirty_word(middle, dual=False):
        middle = [(offset+a,offset+b) for a,b in middle]
        word = middle+scatter+middle[::-1]+inject+middle+scatter+middle[::-1]+inject
        original = [1<<i for i in range(ns+nt+nr)]
        state = original.copy()
        for a,b in reversed(word) if dual else word:
            if dual:a,b=b,a
            state[a] ^= state[b]
        expected = original.copy()
        if dual:
            expected[0] ^= original[ns]
            expected[1] ^= original[ns]
            expected[2] ^= original[ns+1]
        else:
            expected[ns] ^= original[0]^original[1]
            expected[ns+1] ^= original[2]
        return state == expected

    assert dirty_word(scalar) and dirty_word(scalar, True)
    # Omission or premature destruction still restores scratch but corrupts
    # the promised external map; the complete dirty check detects each error.
    negative = {
        'omitted_reconstruction': prefix+migration+new_use,
        'uncleared_reused_carrier': prefix+new_use+reconstruction,
        'unprotected_reserved_control': prefix+migration+new_use+[(3,6)]+reconstruction,
    }
    for word in negative.values():
        assert not dirty_word(word)

    frames = [0]*nr
    ranks = []
    events = []
    def raise_to(s, target):
        old = frames[s]
        assert not old & ~target
        ranks.append(target.bit_count()-old.bit_count())
        events.append([s,old,target])
        frames[s] = target
    def gate(a,b,target):
        raise_to(a,target);raise_to(b,target)
    for s,target in [(0,1),(1,2),(6,1)]:raise_to(s,target)
    gate(2,0,1);gate(3,1,2)
    # These two retired signals live at frames incomparable with current g=3.
    raise_to(0,5);raise_to(1,10)
    for a,b in scalar[2:-1]:gate(a,b,3)
    gate(0,3,7)
    for s in range(nr):raise_to(s,15)
    assert sum(ranks) == h*nr == 28
    return {
        'status': 'passed', 'scratch_roles': nr,
        'arbitrary_basis_bits_checked_in_each_orientation': ns+nt+nr,
        'external_map': ['target_0 += source_a + source_b','target_1 += source_c'],
        'both_orientations': True, 'all_frames_monotone': True,
        'completed_scratch_rank_mass': sum(ranks),
        'rank_excess_above_monotone_potential': 0,
        'negative_controls_rejected': list(negative),
        'scope': 'Local compiler primitive; no standalone integer multiplication claim.',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'frame_events': events,
        'three_carrier_span': check_three_carriers(),
    }


if __name__ == '__main__':
    receipt = check()
    Path(__file__).with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS: dirty two/three-carrier reconstruction, both orientations, monotone ranks, 7 negative controls')
