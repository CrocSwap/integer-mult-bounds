#!/usr/bin/env python3
"""Exact F2 minimum-read compiler for a supplied paired source walk.

Source-walk discovery is heuristic; readout coverage is exhaustive and the
physical-frame dynamic program considers every placement for the chosen minimum-read decomposition; it does not optimize over other decompositions.
Apache-2.0. conorholds with substantial OpenAI Codex assistance.
"""
from collections import deque
from itertools import product

IDENTITY = (1, 2)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def change(frame, port):
    following = list(frame)
    following[port] ^= following[1-port]
    return tuple(following)


def source_cuts(source_word, colors):
    n = len(colors)
    need(3 <= n <= 12 and all(type(c) is int and c in (1,2,3) for c in colors),
         'n=3..12 and nonzero F2 source colors required')
    need(len(source_word) == 2*n and all(type(j) is int and 0 <= j < n for j in source_word)
         and all(source_word.count(j) == 2 for j in range(n)), 'exactly two calls per source required')
    current = [0, 0]
    cuts = []
    for cut in range(len(source_word)+1):
        cuts.append((current[0], current[1], current[0] ^ current[1]))
        if cut < len(source_word):
            label = source_word[cut]
            for root in (0,1):
                if colors[label] & (1 << root):
                    current[root] ^= 1 << label
    need(current == [0,0], 'normalized source restoration')
    return cuts


def readout_plan(source_word, colors, targets=None):
    n = len(colors)
    values = [dict() for _ in range(3)]
    for cut, row in enumerate(source_cuts(source_word, colors)):
        for direction, value in enumerate(row):
            values[direction].setdefault(value, cut)
    # Each A query contributes one vector (source mask, dirty functional).
    # Exact BFS in F2^(n+2) minimizes read count, with no four-read cutoff.
    size = 1 << n
    if targets is None:
        targets = range(1,size)
    else:
        need(isinstance(targets,(list,tuple)) and targets and
             all(type(mask) is int and 0 < mask < size for mask in targets) and
             len(set(targets)) == len(targets),'distinct nonempty in-range target masks required')
        targets = sorted(targets)
    generators = [(value | (direction << n), (cut, direction))
                  for direction, at in enumerate(values, 1) for value, cut in at.items()]
    previous = [-1] * (4*size)
    used = [-1] * (4*size)
    previous[0] = 0
    pending = deque([0])
    while pending:
        state = pending.popleft()
        for index, (vector, query) in enumerate(generators):
            following = state ^ vector
            if previous[following] == -1:
                previous[following] = state
                used[following] = index
                pending.append(following)
    need(all(state != -1 for state in previous), 'query vectors do not span source/dirt space')
    plan = {}
    histogram = {}
    for mask in targets:
        state = mask
        reads = []
        while state:
            reads.append(generators[used[state]][1])
            state = previous[state]
        need(len(set(reads)) == len(reads), 'unremoved cancelling readouts')
        plan[mask] = tuple(reads)
        histogram[len(reads)] = histogram.get(len(reads), 0) + 1
    return plan, histogram


def construct(source_word, colors, targets=None):
    plan, histogram = readout_plan(source_word, colors, targets)
    images = source_cuts(source_word, colors)
    queries = {}
    for mask, reads in plan.items():
        for cut, direction in reads:
            key = (direction, images[cut][direction-1])
            queries.setdefault(key, []).append(mask)
    keys = sorted(queries)
    index = {key:i for i,key in enumerate(keys)}
    available = []
    for row in images:
        available.append(tuple(1 << index[d,value] if (d,value) in index else 0
                               for d,value in enumerate(row,1)))
    deadlines = [0]*len(images)
    for key, i in index.items():
        direction,value = key
        last = max(cut for cut,row in enumerate(images) if row[direction-1] == value)
        deadlines[last] |= 1 << i
    frames = tuple((a,b) for a,b in product((1,2,3), repeat=2) if a != b)
    # A used generator may be delivered at ANY cut where its value occurs.
    # The deadline DP considers all such placements and every unit-shear word.
    best = {(IDENTITY,0):(0,())}
    mandatory = 0
    peak_states = 1
    for cut, bits in enumerate(available):
        mandatory |= deadlines[cut]
        if cut == len(source_word):
            ends = {IDENTITY}
        else:
            color = colors[source_word[cut]]
            ends = {g for g in frames if ((g[0]&color).bit_count()&1) == 1
                    and ((g[1]&color).bit_count()&1) == 0}
        following = {}
        for (start, done), (bill, history) in best.items():
            first = (start, done | bits[start[0]-1])
            pending = deque([(first,())])
            seen = {first}
            while pending:
                (frame, covered), path = pending.popleft()
                if frame in ends and covered & mandatory == mandatory:
                    state = (frame,covered)
                    candidate = (bill+len(path),history+((start,path,done),))
                    if state not in following or candidate < following[state]:
                        if state not in following:
                            need(len(following)<65536,'frame DP exceeds 65536-state resource cap')
                        following[state] = candidate
                for port in (0,1):
                    after = change(frame,port)
                    state = (after,covered | bits[after[0]-1])
                    if state not in seen:
                        seen.add(state)
                        pending.append((state,path+(port,)))
        need(following, 'no legal deadline/frame schedule')
        # Honest resource rejection; never treat a truncated DP as optimal.
        need(len(following) <= 65536, 'frame DP exceeds 65536-state resource cap')
        peak_states = max(peak_states,len(following))
        best = following
    all_done = (1 << len(keys))-1
    transfer_bill, history = best[IDENTITY,all_done]
    word = []
    done = 0
    for cut,(frame,transfers,earlier) in enumerate(history):
        need(done == earlier,'frame DP history drift')
        def read():
            nonlocal done
            direction = frame[0]
            bit = available[cut][direction-1]
            if bit and not done & bit:
                key = (direction,images[cut][direction-1])
                word.extend(['A',mask,0] for mask in sorted(queries[key]))
                done |= bit
        read()
        for port in transfers:
            word.append(['C',port])
            frame = change(frame,port)
            read()
        if cut < len(source_word):
            word.append(['B',source_word[cut],0])
    need(done == all_done,'undelivered readout generator')
    counts = {'sources':len(colors),'target_outputs':len(plan),'source_calls':len(source_word),
              'readout_calls':sum(k*v for k,v in histogram.items()),
              'readout_multiplicity_histogram':{str(k):v for k,v in sorted(histogram.items())},
              'transfers':transfer_bill,'dirty_root_rows':2,'frame_dp_peak_states':peak_states}
    need(len(word) == counts['source_calls']+counts['readout_calls']+transfer_bill,
         'unpaid source-walk instruction')
    return word, counts


def source_difference_bound(n):
    """Nonzero differences of a closed twice-occurring n-label unit walk.

    n5/n6 use complete pairing censuses, independently rerun by verify_walk.py.
    Other sizes use the cube cardinality and the source-locality bound.
    """
    from families import locality_capacity
    need(type(n) is int and 0 <= n <= 12, 'difference-bound domain n=0..12')
    if n == 0:
        return 0
    if n in (5,6):
        return {5:30,6:48}[n]
    return min((1<<n)-1,locality_capacity(n,2*n,1))


def minimum_source_invoice(n,b,a):
    """F2 universal-batch lower bound at exactly 2n B calls, transfers free.

    Two calls force a fixed normalized source color. This enumerates every
    one/two/three nonempty color-size partition; it is NOT an overall optimum
    when extra B calls are admitted. Requested-subset batches are not covered.
    """
    from fractions import Fraction
    from math import prod
    from families import partitions
    need(type(n) is int and 1 <= n <= 12, 'source-invoice domain n=1..12')
    b,a=map(Fraction,(b,a))
    need(b>0 and a>0,'positive complete query prices required')
    masks=(1<<n)-1;cases=[]
    for sizes in (p for p in partitions(n) if len(p)<=3):
        if len(sizes)==1:
            paired=source_difference_bound(n)
            missing=masks-paired
            reads=4*masks-2*paired
        else:
            if len(sizes)==2:
                paired=source_difference_bound(n)+sum(source_difference_bound(s) for s in sizes)-n
            else:
                paired=sum(source_difference_bound(n-s) for s in sizes)-n
            paired=min(masks,paired)
            missing=(1<<n)-prod(source_difference_bound(s)+1 for s in sizes)
            reads=3*masks-paired+missing
        cases.append({'color_sizes':list(sizes),'paired_capacity_upper':paired,
                      'missing_two_or_three_reads_lower':missing,'readout_lower':reads})
    reads=min(case['readout_lower'] for case in cases)
    return {'source_calls':2*n,'readout_lower':reads,'query_lower_bound':2*n*b+reads*a,
            'cases':cases,'scope':'F2, all nonzero masks, exactly two B calls per active source; arbitrary A counts/transfers. Not extra-B or subset programs.'}
