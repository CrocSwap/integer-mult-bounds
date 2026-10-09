"""PR186 completed entrance banks on the literal PR200 physical bit word.

The 18x4 / 3x24 stage-private packing and its projector checks are PR186's
(Dugongue), as scheduled by the round-8 bank supplement (Douglas Colkitt).
The exact gauge charts reuse PR197's fraction-free inverse (evmckinney9).
Prepared with Anthropic Claude assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import gcd
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REFS = HERE / 'references'
BOUND = 2**79


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bank_projectors():
    """Literal address maps on every F2 and integer basis column of two banks."""
    checks=[]
    for width,count in ((4,18),(24,3)):
        owner=[j//width for j in range(72)]
        need([owner.count(s) for s in range(count)]==[width]*count,'actual full bank partition')
        projectors=[[int(owner[j]==s) for j in range(72)] for s in range(count)]
        need(all(sum(P[j] for P in projectors)==1 for j in range(72)),'sum of actual projectors is identity')
        need(all(P[j]*P[j]==P[j] for P in projectors for j in range(72)),'idempotent bank projectors')
        need(all(P[j]*T[j]==0 for s,P in enumerate(projectors) for t,T in enumerate(projectors) if s!=t for j in range(72)),'pairwise disjoint bank projectors')
        def run(column,ring,indices):
            x=[0]*72;y=[0]*72
            (x if column<72 else y)[column%72]=1
            for s in indices:
                P=projectors[s]
                x,y=([a-P[j]*a+P[j]*b for j,(a,b) in enumerate(zip(x,y))],
                     [b-P[j]*b+P[j]*a for j,(a,b) in enumerate(zip(x,y))])
                if ring:x=[a%ring for a in x];y=[a%ring for a in y]
            return x+y
        controls={}
        for ring in (2,0):
            for column in range(144):
                expected=[0]*144;expected[(column+72)%144]=1
                need(run(column,ring,range(count))==expected,'completed bank full dirty swap formal column')
                need(run(column,ring,list(range(count))+list(reversed(range(count))))==[int(j==column) for j in range(144)],'completed bank inverse restores arbitrary contents')
            for tag,indices in (('omit_block',list(range(count-1))),('repeat_block',list(range(count))+[count-1])):
                column=72-width;expected=[0]*144;expected[column+72]=1
                need(run(column,ring,indices)!=expected,'adverse bank control rejected: '+tag)
                controls[str(ring)+':'+tag]=True
        checks.append(dict(width=width,blocks=count,ambient=72,rings=[2,0],formal_columns=288,
            inverse_columns=288,projectors_idempotent=True,projectors_disjoint=True,sum_is_identity=True,
            controls_rejected=controls,endpoint='partialSwap(P)(x,y)=(x-Px+Py,y-Py+Px)'))
    return checks


def weighted_bank_controls():
    """PR197's weighted endpoint check over Z/9, Z/25, Z/125, on PR186's two bank patterns."""
    m, cases, rejected = 72, 0, []
    patterns = ([4] * 18, [24] * 3)

    def apply(parts, modulus, reverse=False, repeat_first=False):
        rows = [{i: 1} for i in range(2 * m)]
        intervals, offset = [], 0
        for width in parts:
            intervals.append(range(offset, offset + width)); offset += width
        if repeat_first:
            intervals.append(intervals[0])
        if reverse:
            intervals.reverse()
        for interval in intervals:
            for i in interval:
                weight = (1, 2, 4)[i % 3]
                need(gcd(weight, modulus) == 1, 'unit weight')
                a, b = rows[i], rows[2 * m - 1 - i]
                rows[i] = {j: weight * x % modulus for j, x in b.items()}
                rows[2 * m - 1 - i] = {j: pow(weight, -1, modulus) * x % modulus for j, x in a.items()}
        return rows

    def expected(modulus):
        return [{2 * m - 1 - i: (1, 2, 4)[i % 3]} for i in range(m)] + [
            {m - 1 - i: pow((1, 2, 4)[(m - 1 - i) % 3], -1, modulus)} for i in range(m)]
    for modulus in (9, 25, 125):
        for pattern in patterns:
            for reverse in (False, True):
                need(apply(pattern, modulus, reverse) == expected(modulus), 'weighted completed bank endpoint')
                cases += 1
        need(apply(patterns[0], modulus, repeat_first=True) != expected(modulus), 'repeated block rejected')
        rejected.append('repeated block mod %d' % modulus)
        need(apply(patterns[0][:-1], modulus) != expected(modulus), 'omitted block rejected')
        rejected.append('omitted block mod %d' % modulus)
    return dict(formal_columns_per_case=2 * m, weighted_partition_cases=cases, rejected=rejected)


def packed_row(word, row, sink_roles):
    """Bank whole live physical chains; recipients are splices and deleted sinks have no register."""
    need((row['h'], row['m'], row['v'], row['reused_registers']) == (24, 72, 1760, 1760), 'retained bit dimensions and aliases')
    starts = {s: z['dim'] for s, z in word.gauge.items() if s not in word.donor}
    gauges = len(starts)
    need(gauges == row['selected_roles'] and row['selected_rank_histogram'] == {20: gauges}, 'actual surviving physical entrances')
    need(set(starts.values()) == {20}, 'rank20 entrance gauges only')
    need(all(word.gauge[b]['dim'] == 21 for b in word.donor), 'rank21 recipients are splices, not separate bank roles')
    sources = set(word.source.values())
    need(len(sink_roles) == row['terminal_sinks'], 'every deleted terminal sink accounted for')
    need(not sink_roles & (set(word.gauge) | set(word.donor) | set(word.donor.values()) | sources), 'deleted sinks are not entrances, splices or sources')
    live = set(word.phys.values()) - sink_roles
    need(len(live) == row['R'] and set(starts) <= live, 'live physical chains are the terminal word registers')
    rest = row['R'] - gauges
    H = dict(row['child_histogram'])
    need(H.pop(60, None) == gauges, 'remove exactly one rank60 entrance exterior per surviving gauge')
    W = Q(2 * word.v) + 3 * (Q(gauges, 18) + Q(rest, 3))
    mass = sum(r * n for r, n in H.items())
    need(72 * W - mass == row['deficit_per_vertex'], 'complete packed bank telescoping inventory')
    need(max(H) == 22 and all(0 < r < 72 and n > 0 for r, n in H.items()), 'proper paid bank children')
    need(9 * gauges % 18 == 0 and 9 * rest % 3 == 0, 'stage-private integer bank realization')
    need(3 * (9 * gauges // 18 + 9 * rest // 3) + 2 * 9 * word.v == 9 * W, 'nine-copy literal stock agrees')
    return dict(row, W_per_vertex=W, rank_per_vertex=mass, child_histogram=H, maxchild=max(H),
        physical_roles_before_banks=row['R'], bank_roles_per_vertex=W - 2 * word.v,
        bank=dict(entrance_rank=20, entrance_gauges=gauges, undeferred_physical_roles=rest, deleted_terminal_sinks=len(sink_roles),
            selected_blocks=18, selected_width=4, undeferred_blocks=3, undeferred_width=24, stages=3,
            physical_chains_spliced=True, physical_replica_count=9, moment_normalization_scale=3,
            selected_banks_per_stage=9 * gauges // 18, undeferred_banks_per_stage=9 * rest // 3)), starts


def gauge_charts(word, starts):
    """Exact integer charts for every distinct rank20 entrance frame, with PR197's fraction-free inverse."""
    inverse_integer = load('pr197_packing', REFS / 'pr197/packing.py').inverse_integer
    inventory = Counter(word.gauge[s]['frame'] for s in starts)
    digest = sha256(); maxops = maxnum = maxden = maxentry = 0
    for f, count in sorted(inventory.items()):
        A, source = word.C.A[f], word.C.B[f]
        need(len(A) == 4 and len(source) == 20, 'rank20 entrance frame with a rank4 residual')
        residual = []
        for a in A:
            row = [15 * x - sum(a) for x in a]; d = gcd(*row); residual.append([x // d for x in row])
        need(all(9 * sum(x * y for x, y in zip(a, b)) - sum(a) * sum(b) == 0 for a in residual for b in source), 'residual is G-orthogonal to the gauge frame')
        B = list(map(list, zip(*(residual + source))))
        C, d, ops = inverse_integer(B)
        for left, right in ((B, C), (C, B)):
            need(all(sum(x * y for x, y in zip(row, col)) == d * int(i == j) for i, row in enumerate(left) for j, col in enumerate(zip(*right))), 'exact two-sided inverse')
        replay = [list(map(Q, row)) for row in B]
        for op, i, j, num, den in ops:
            if op == 'swap':
                replay[i], replay[j] = replay[j], replay[i]
            elif op == 'scale':
                replay[i] = [Q(num, den) * x for x in replay[i]]
            else:
                need(op == 'add', 'known chart factor'); replay[i] = [x + Q(num, den) * y for x, y in zip(replay[i], replay[j])]
        need(all(x == int(i == j) for i, row in enumerate(replay) for j, x in enumerate(row)), 'chart factors replay to the identity')
        maxops = max(maxops, len(ops)); maxnum = max(maxnum, max(abs(o[3]) for o in ops))
        maxden = max(maxden, d, max(o[4] for o in ops)); maxentry = max(maxentry, max(abs(x) for row in C for x in row))
        digest.update(json.dumps([f, count, B, C, d, ops], separators=(',', ':')).encode())
    need(max(maxnum, maxden, maxentry) < BOUND, 'chart numerators, denominators and entries below 2^79')
    return dict(distinct_entrance_frames=len(inventory), entrance_roles=sum(inventory.values()), chart_sha256=digest.hexdigest(),
        max_chart_factors=maxops, max_num=maxnum, max_den=maxden, max_entry=maxentry, entry_bound='2^79',
        slot_separation='Distinct bank slots place the residual in disjoint coordinate blocks of an invertible chart; '
                        'every difference of two slot charts is a nonzero integer matrix over the common denominator with entries below 2^80, '
                        'so no prime q > 2^80 identifies two charts of one bank group.')
