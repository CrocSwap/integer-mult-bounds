#!/usr/bin/env python3
"""Paid dirty-connector cube schedules and exact cost screens. Apache-2.0.

conorholds with substantial OpenAI Codex assistance.
"""
from fractions import Fraction
from itertools import accumulate
from math import comb, prod


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(sizes):
    require(isinstance(sizes, (list, tuple)) and sizes and
            all(type(s) is int and s > 0 for s in sizes), "positive nonempty block sizes required")
    return sum(sizes)


def blocks(sizes):
    validate(sizes)
    starts = [0, *accumulate(sizes)]
    return [list(range(starts[i], starts[i + 1])) for i in range(len(sizes))]


def cycle(coordinates):
    """Closed reflected Gray cycle; every nonzero block sum is visited."""
    for step in range(1, 1 << len(coordinates)):
        yield coordinates[(step & -step).bit_length() - 1]
    yield coordinates[-1]


def readout_count(sizes):
    n = validate(sizes)
    odd = ((1 << n) - prod(2 - (1 << s) for s in sizes)) // 2
    incidence = sum(((1 << s) - 1) * (1 << (n - s)) for s in sizes)
    return incidence + odd


def screen(sizes):
    n = validate(sizes)
    return {"sources": n, "blocks": list(sizes), "source_calls": sum(1 << s for s in sizes),
            "readout_calls": readout_count(sizes), "transfers": 0,
            "dirty_root_rows": 1}


def cost(sizes, b, a):
    b, a = map(Fraction, (b, a))
    require(b > 0 and a > 0, "invalid complete-call tariff")
    counts = screen(sizes)
    return counts["source_calls"] * b + counts["readout_calls"] * a


def partitions(n, minimum=1):
    """All unordered positive partitions, without exponential output enumeration."""
    require(type(n) is int and n > 0, "positive source count required")
    for first in range(minimum, n + 1):
        if first == n:
            yield (first,)
        else:
            for tail in partitions(n - first, first):
                yield (first, *tail)


def best_single(n, b, a):
    return min(partitions(n), key=lambda sizes: (cost(sizes, b, a), sizes))


def balanced_three(n):
    require(type(n) is int and n >= 3, "three nonempty blocks require n>=3")
    q, r = divmod(n, 3)
    return tuple(q + int(i < r) for i in range(3))


def construct(sizes):
    """One-root reference with exactly the necessary odd-dirt compensation."""
    n = validate(sizes)
    require(n <= 18, "explicit program emission is bounded to n<=18; screen has no such limit")
    groups = blocks(sizes)
    masks = [sum(1 << j for j in group) for group in groups]
    reads = [dict() for _ in sizes]; word = []
    for target in range(1, 1 << n):
        parts = [target & group for group in masks]
        if sum(part != 0 for part in parts) & 1:
            word.append(["A", target, 0])
        for phase, part in enumerate(parts):
            if part:
                reads[phase].setdefault(part, []).append(target)
    for phase, group in enumerate(groups):
        value = 0
        for source in cycle(group):
            word.append(["B", source, 0]); value ^= 1 << source
            if value:
                word.extend(["A", target, 0] for target in reads[phase].get(value, []))
        require(value == 0, "Gray cycle did not restore")
    counts = screen(sizes)
    require(len(word) == counts["source_calls"] + counts["readout_calls"],
            "constructor invoice differs from exact formula")
    return word


def palette_screen(sizes):
    n = validate(sizes)
    require(len(sizes) == 3, "palette construction requires three blocks")
    vertices = [1 << s for s in sizes]
    return {"sources": n, "blocks": list(sizes), "source_calls": sum(vertices),
            "readout_calls": 2 * ((1 << n) - 1) + prod(q - 1 for q in vertices),
            "transfers": sum(vertices),
            "dirty_root_rows": 2}


def construct_palette(sizes):
    """Both palettes through physical z0; the companion carries incoming dirt only."""
    n = validate(sizes)
    require(len(sizes) == 3 and n <= 18, "three blocks and bounded explicit n<=18 required")
    groups = blocks(sizes)
    masks = [sum(1 << j for j in group) for group in groups]
    available = ((1, 3), (2, 3), (1, 2))
    starts = (1, 3, 2)
    reads = [{1: {}, 2: {}, 3: {}} for _ in range(3)]
    for target in range(1, 1 << n):
        parts = [target & mask for mask in masks]
        active = [i for i, part in enumerate(parts) if part]
        if len(active) == 1:
            phase = active[0]; signature = starts[phase]
            reads[phase][signature].setdefault(0, []).append(target)
            reads[phase][signature].setdefault(parts[phase], []).append(target)
        elif len(active) == 2:
            first, second = active
            signature = next(iter(set(available[first]) & set(available[second])))
            for phase in active:
                reads[phase][signature].setdefault(parts[phase], []).append(target)
        else:
            for phase, signature in enumerate((1, 3, 2)):
                reads[phase][signature].setdefault(parts[phase], []).append(target)
    word = []; frame = [1, 2]
    def transfer(port):
        word.append(["C", port]); frame[port] ^= frame[1-port]
    def read(phase, value):
        signature = frame[0]
        word.extend(["A", target, 0] for target in reads[phase][signature].get(value, []))
    for phase, group in enumerate(groups):
        require(frame[0] == starts[phase], "phase entry dirt signature")
        value = 0; read(phase, value)
        for source in cycle(group):
            word.append(["B", source, 0]); value ^= 1 << source
            if value:
                read(phase, value)
                transfer(0)
                read(phase, value)
        require(value == 0, "palette source closure")
        # At this cut z0 contains only incoming dirt. One V changes the
        # companion's signature for the next color, or closes the whole frame.
        transfer(1)
    require(frame == [1, 2], "palette root-frame closure")
    counts = palette_screen(sizes)
    require(len(word) == sum(counts[name] for name in ("source_calls", "readout_calls", "transfers")),
            "palette formula differs from emitted program")
    return word


def single_frontier(n):
    """Count-Pareto one-root Gray-block references over every integer partition."""
    candidates = [(screen(sizes)["source_calls"], screen(sizes)["readout_calls"], sizes)
                  for sizes in partitions(n)]
    frontier = []; best_a = None
    for b, a, sizes in sorted(candidates):
        if best_a is None or a < best_a:
            frontier.append(sizes); best_a = a
    return frontier


def signed_single_frontier(n):
    """All count-Pareto signed references; put the largest cube first."""
    candidates = []
    for partition in partitions(n):
        sizes = tuple(reversed(partition))
        counts = signed_single_screen(sizes)
        candidates.append((counts["source_calls"], counts["readout_calls"], sizes))
    frontier = []
    best_a = None
    for b, a, sizes in sorted(candidates):
        if best_a is None or a < best_a:
            frontier.append(sizes)
            best_a = a
    return frontier


def palette_cost(sizes, b, a, transfer):
    b,a,transfer=map(Fraction,(b,a,transfer))
    require(b>0 and a>0 and transfer>=0,"invalid complete-call tariff")
    counts=palette_screen(sizes)
    return counts['source_calls']*b+counts['readout_calls']*a+counts['transfers']*transfer


def best_palette(n,b,a,transfer):
    require(type(n) is int and n>=3,"three nonempty blocks require n>=3")
    candidates=[tuple(reversed(sizes)) for sizes in partitions(n) if len(sizes)==3]
    # Count formulas are symmetric in block sizes; this ordering is deterministic.
    return min(candidates,key=lambda sizes:(palette_cost(sizes,b,a,transfer),sizes))


def capacity_threshold(n, roots):
    """First admissible source count whose optimistic paired cover reaches every mask."""
    require(type(n) is int and n>0 and roots in (1,2),"positive n and one/two roots required")
    masks=(1<<n)-1; multiplier=1 if roots==1 else 3
    lo=2*n; hi=lo
    while multiplier*hi*(hi-1)<2*masks:hi*=2
    while lo<hi:
        mid=(lo+hi)//2
        if multiplier*mid*(mid-1)>=2*masks:hi=mid
        else:lo=mid+1
    if roots==1 and lo&1:lo+=1
    return lo


def global_lower_bound(n,b,a,roots=1):
    """All-word query-tariff lower bound, not merely a Gray-family cost screen.

    One root: absent paired masks need >=4 reads (dirty parity).
    Two roots: absent paired masks need >=3 reads; all root frames are granted free.
    The concave branch is minimized at its endpoints, then the linear tail increases.
    """
    b,a=map(Fraction,(b,a))
    require(b>0 and a>0,"positive complete-call prices required")
    threshold=capacity_threshold(n,roots);minimum=2*n
    step=2 if roots==1 else 1
    candidates={minimum,threshold}
    if threshold-step>=minimum:candidates.add(threshold-step)
    masks=(1<<n)-1; base=4 if roots==1 else 3
    multiplier=1 if roots==1 else 3
    return min(k*b+a*max(2*masks,base*masks-(base-2)*multiplier*k*(k-1)//2)
               for k in candidates)


def locality_capacity(n, k, roots):
    """Optimistic paired cover, excluding repeated short-prefix mask capacity.

    There are k*h unordered cuts at cyclic distance <=h. Their masks have
    Hamming weight <=h, so those pairs collectively cover at most S(n,h).
    One-root pairs cover <=1 mask, two-root pairs <=3, in the binary cube.
    """
    require(type(n) is int and n > 0 and type(k) is int and k >= 2*n
            and roots in (1, 2), "invalid source-prefix capacity domain")
    multiplier = 1 if roots == 1 else 3
    supported = 0
    deficit = 0
    for radius in range(1, n):
        supported += comb(n, radius)
        deficit = max(deficit, multiplier*k*radius - supported)
    return multiplier*k*(k-1)//2 - deficit


def locality_lower_bound(n, b, a, roots=1):
    """Exact endpoint minimization of the stronger all-word locality bound."""
    b, a = map(Fraction, (b, a))
    require(b > 0 and a > 0 and roots in (1, 2), "invalid complete query prices/roots")
    require(type(n) is int and n > 0, "positive source count required")
    masks = (1 << n) - 1
    minimum = 2*n
    multiplier = 1 if roots == 1 else 3
    step = 2 if roots == 1 else 1
    lo, hi = minimum, minimum
    while locality_capacity(n, hi, roots) < masks:
        hi *= 2
    while lo < hi:
        mid = (lo+hi)//2
        if locality_capacity(n, mid, roots) >= masks:
            hi = mid
        else:
            lo = mid+1
    threshold = lo + (lo % 2 if roots == 1 else 0)
    candidates = {minimum, threshold}
    if threshold-step >= minimum:
        candidates.add(threshold-step)
    supported = [0]
    for radius in range(1, n):
        supported.append(supported[-1] + comb(n, radius))
    # Between intersections of the deficit lines, the unsaturated expression
    # is concave. Include the adjacent admissible integers at every intersection.
    for h in range(1, n):
        for g in range(h):
            crossing = Fraction(supported[h]-supported[g], multiplier*(h-g))
            if minimum <= crossing <= threshold:
                lower = crossing.numerator//crossing.denominator
                lower -= (lower-minimum) % step
                candidates.update(k for k in (lower, lower+step) if minimum <= k <= threshold)
    base = 4 if roots == 1 else 3
    return min(k*b + a*max(2*masks, base*masks - (base-2)*locality_capacity(n, k, roots))
               for k in candidates)


def critical_tariff(n):
    """Integer source price asymptotic to sqrt(2M), in unit-readout prices."""
    return capacity_threshold(n,1)-2+2*n-1


def signed_palette_screen(sizes):
    n = validate(sizes)
    require(len(sizes) == 3, "signed palette needs three blocks")
    q = [1 << s for s in sizes]
    return {"sources": n, "blocks": list(sizes), "source_calls": sum(q),
            "readout_calls": 2 * ((1 << n) - 1) + prod(x - 1 for x in q),
            "transfers": sum(q) + 4, "dirty_root_rows": 2}


def construct_signed_palette(sizes):
    """Signed triangular colors: one cube per block, fixed physical child port.

    Normalized columns e0, e1, -e0-e1 form a zero-sum triangle. Each vertex
    exposes two dirty functionals, so mixed targets need no negative-cube revisit.
    """
    n = validate(sizes)
    require(len(sizes) == 3 and n <= 18, "three blocks and bounded explicit n<=18 required")
    groups = blocks(sizes)
    masks = [sum(1 << j for j in group) for group in groups]
    reads = [{} for _ in groups]
    anchors = [[] for _ in groups]
    polarity = (1, 1, -1)
    signatures = (((1, 0), (1, -1)), ((0, 1), (-1, 1)), ((0, 1), (1, 0)))
    for target in range(1, 1 << n):
        parts = [target & mask for mask in masks]
        active = tuple(i for i, part in enumerate(parts) if part)
        if len(active) == 1:
            phase = active[0]
            anchors[phase].append(target)
            choices = ((phase, 0),)
        elif active == (0, 1):
            choices = ((0, 1), (1, 1))
        elif active == (0, 2):
            choices = ((0, 0), (2, 1))
        elif active == (1, 2):
            choices = ((1, 0), (2, 0))
        else:
            choices = ((0, 0), (1, 1), (2, 0))
        for phase, direction in choices:
            reads[phase].setdefault((direction, parts[phase]), []).append(target)
    word = []
    frame = [[1, 0], [0, 1]]
    closures = (((0, 1), (0, 1), (1, -1), (0, 1)),
                ((0, -1), (1, 1)), ((1, 1),))
    def transfer(port, sign):
        word.append(["C", port, sign])
        frame[port] = [a + sign * b for a, b in zip(frame[port], frame[1 - port])]
    for phase, group in enumerate(groups):
        require(tuple(frame[0]) == signatures[phase][0], "signed triangle entry frame")
        word.extend(["A", target, 0, -polarity[phase]] for target in anchors[phase])
        value = 0
        for source in cycle(group):
            before = bool(value & (1 << source))
            value ^= 1 << source
            word.append(["B", source, 0, polarity[phase] * (-1 if before else 1)])
            if value:
                direction = signatures[phase].index(tuple(frame[0]))
                word.extend(["A", target, 0, polarity[phase]]
                            for target in reads[phase].get((direction, value), []))
                sign = (-1, 1, -1)[phase] * (-1 if direction else 1)
                transfer(0, sign)
                direction = 1 - direction
                require(tuple(frame[0]) == signatures[phase][direction], "signed vertex frame")
                word.extend(["A", target, 0, polarity[phase]]
                            for target in reads[phase].get((direction, value), []))
        require(value == 0, "signed triangle source closure")
        for port, sign in closures[phase]:
            transfer(port, sign)
    require(frame == [[1, 0], [0, 1]], "signed triangle root restoration")
    counts = signed_palette_screen(sizes)
    require(len(word) == sum(counts[k] for k in ("source_calls", "readout_calls", "transfers")),
            "unpaid signed instruction")
    return word


def signed_single_screen(sizes):
    n=validate(sizes);q=[1<<s for s in sizes]
    return {'sources':n,'blocks':list(sizes),'source_calls':q[0]+2*sum(q[1:]),
            'readout_calls':readout_count(sizes),'transfers':0,'dirty_root_rows':1}


def construct_signed_single(sizes):
    n=validate(sizes);require(n<=18,"bounded signed program emission n<=18")
    groups=blocks(sizes);masks=[sum(1<<j for j in group) for group in groups]
    reads=[{} for _ in sizes];word=[]
    for target in range(1,1<<n):
        parts=[target&mask for mask in masks];active=[i for i,p in enumerate(parts) if p]
        if len(active)&1:word.append(['A',target,0,-1])
        for position,phase in enumerate(active):
            sign=1 if position<(len(active)+1)//2 else -1
            reads[phase].setdefault((sign,parts[phase]),[]).append((target,sign))
    for phase,group in enumerate(groups):
        for polarity in ((1,) if phase==0 else (1,-1)):
            value=0
            for source in cycle(group):
                before=bool(value&(1<<source));value^=1<<source
                word.append(['B',source,0,polarity*(-1 if before else 1)])
                if value:word.extend(['A',target,0,sign] for target,sign in reads[phase].get((polarity,value),[]))
            require(value==0,"signed one-root source closure")
    counts=signed_single_screen(sizes)
    require(len(word)==counts['source_calls']+counts['readout_calls'],"unpaid signed reference")
    return word
