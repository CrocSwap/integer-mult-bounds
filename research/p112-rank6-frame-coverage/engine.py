# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Complete maximal rank-six slice census; E8 model from PR1226/PR1323."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def model():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                root = [0] * 8
                root[i], root[j] = 2 * si, 2 * sj
                roots.append(tuple(root))
    roots.extend(r for r in itertools.product((1, -1), repeat=8)
                 if r.count(-1) % 2 == 0)
    lines, seen = [], set()
    for root in roots:
        key = max(root, tuple(-x for x in root))
        if key not in seen:
            seen.add(key)
            lines.append(root)
    puncture = []
    for k in range(4):
        for sign in (1, -1):
            root = [0] * 8
            root[2*k], root[2*k+1] = 2, 2*sign
            puncture.append(lines.index(tuple(root)))
    return dict(lines=[list(r) for r in lines], punctured_frame=puncture,
                live=[i for i in range(120) if i not in puncture])


def geometry(data):
    roots, live = data["lines"], data["live"]
    require(len(roots) == 120 and len(live) == 112, "wrong model size")
    require(all(sum(x*x for x in r) == 8 for r in roots), "wrong root norm")
    products = [[sum(x*y for x, y in zip(a, b)) for b in roots] for a in roots]
    require(all(v % 4 == 0 for row in products for v in row), "nonintegral pairing")
    ip = [[v // 4 for v in row] for row in products]
    n = [sum(((v+1) % 2) << j for j, v in enumerate(row)) for row in ip]
    supports = []
    for a in range(120):
        star = sum(1 << i for i in live if ip[a][i] != 0)
        supports.extend((star, star & ~(1 << a)))
    adjacent = [sum(1 << j for j in live if i != j and ip[i][j] == 0)
                for i in range(120)]
    frames = []

    def extend(chosen, candidates):
        if len(chosen) == 8:
            frames.append(tuple(chosen))
            return
        while candidates:
            if candidates.bit_count() < 8-len(chosen):
                return
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length()-1
            extend(chosen + [i], candidates & adjacent[i])
    extend([], sum(1 << i for i in live))
    require(len(frames) == 1260, "live frame census changed")
    incidence = Counter(i for f in frames for i in f)
    require(set(incidence) == set(live) and set(incidence.values()) == {90},
            "live frame incidence changed")
    coframe = {pair for f in frames for pair in itertools.combinations(f, 2)}
    require(all((i, j) in coframe for i, j in itertools.combinations(live, 2)
                if ip[i][j] == 0), "an orthogonal live pair has no live frame")
    return ip, n, supports, frames


def basis(values):
    pivots = {}
    for v in values:
        while v:
            p = v.bit_length()-1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return tuple(pivots.values())


def rank(n, left, right):
    return len(basis(n[i] & right for i in bits(left)))


def column_code(n, left, right):
    generators = basis(n[j] & left for j in bits(right))
    code = [0]
    for g in generators:
        code += [v ^ g for v in code]
    return sorted(code[1:])


def word_digest(records):
    return hashlib.sha256("".join(f"{w:x}\t{h}\n" for w, h in records).encode()).hexdigest()


def table_bytes(table):
    return "".join(json.dumps(row, separators=(",", ":"))+"\n" for row in table).encode()


def census(data):
    ip, n, supports, frames = geometry(data)
    frame_masks = [sum(1 << i for i in f) for f in frames]
    hit_cache, row_masks = {}, set()

    def hits(mask):
        if mask not in hit_cache:
            hit_cache[mask] = sum(1 << k for k, f in enumerate(frame_masks) if mask & f)
        return hit_cache[mask]

    parent_ranks, cut_ranks, hit_counts = Counter(), Counter(), Counter()
    table = []
    for a, left in enumerate(supports):
        for b, right in enumerate(supports):
            r = rank(n, left, right)
            parent_ranks[r] += 1
            if r != 7:
                continue
            require((a % 2 or a//2 in data["punctured_frame"]) and
                    (b % 2 or b//2 in data["punctured_frame"]) and
                    ip[a//2][b//2] % 2, "rank-seven parent classification failed")
            words = column_code(n, left, right)
            require(len(words) == len(set(words)) == 127 and all(words), "incomplete code")
            values = []
            right_hits = hits(right)
            for word in words:
                row = left ^ word
                require(word & ~left == 0, "codeword leaves parent support")
                r = rank(n, row, right)
                require(r == 6, "maximal one-axis slice is not rank six")
                cut_ranks[r] += 1
                row_masks.add(row)
                h = (hits(row) & right_hits).bit_count()
                hit_counts[h] += 1
                values.append((word, h))
            maximum = max(h for _, h in values)
            maximizers = [w for w, h in values if h == maximum]
            cut = min(maximizers, key=lambda w: (w.bit_count(), w))
            table.append([a, b, maximum, format(cut, "x"), cut.bit_count(),
                          len(maximizers), word_digest(values)])
    require(parent_ranks == {7: 7616, 8: 37440, 9: 12544}, "parent census changed")
    lookup = {(row[0], row[1]): row for row in table}
    one_axis = Counter(row[2] for row in table)
    joint = Counter(max(row[2], lookup[row[1], row[0]][2]) for row in table)
    maximum = max(one_axis)
    selected = min((row for row in table if row[2] == maximum),
                   key=lambda row: ((row[0]-20) % 240, (row[1]-20) % 240,
                                    int(row[3], 16)))
    a, b, h, cut_hex = selected[:4]
    cut = int(cut_hex, 16)
    summary = dict(
        status="PASS_COMPLETE_RANK6_FRAME_CENSUS", frames=1260,
        required_frame_hits=10080, rank7_tagged_parents=len(table),
        codeword_cases=sum(cut_ranks.values()), distinct_row_slice_supports=len(row_masks),
        parent_rank_histogram=dict(sorted(parent_ranks.items())),
        slice_rank_histogram=dict(cut_ranks), slice_frame_hit_histogram=dict(sorted(hit_counts.items())),
        one_axis_parent_maximum_histogram=dict(sorted(one_axis.items())),
        arbitrary_joint_parent_maximum_histogram=dict(sorted(joint.items())),
        maximum_frame_hits=maximum,
        averaged_frame_bound=str(Fraction(10080 * 6, maximum)),
        all_rank6_term_count_lower_bound=10,
        witness=dict(left_tag=a, right_tag=b, row_cut_hex=cut_hex,
                     retained_row_ids=list(bits(supports[a] ^ cut)),
                     column_ids=list(bits(supports[b])), copy_rank=6, frame_hits=h),
        table_sha256=hashlib.sha256(table_bytes(table)).hexdigest())
    return table, summary


def check_cover(data, cover):
    """Check a necessary-condition witness with exact bit ranks, not an LP solver."""
    _, n, supports, frames = geometry(data)
    counts = [0] * len(frames)
    diagonal = {i: 0 for i in data["live"]}
    masks = [sum(1 << i for i in f) for f in frames]
    terms = cover["terms"]
    require(len(terms) == 10, "cover must contain ten terms")
    for term in terms:
        a, b, cut_hex = term
        require(type(a) is int and type(b) is int and 0 <= a < 240 and 0 <= b < 240,
                "invalid parent tags")
        cut = int(cut_hex, 16)
        left, right = supports[a], supports[b]
        require(rank(n, left, right) == 7 and cut in column_code(n, left, right),
                "cover term is outside the maximal-cut dictionary")
        row = left ^ cut
        require(rank(n, row, right) == 6, "cover term does not cost six")
        for i, mask in enumerate(masks):
            counts[i] += bool(row & mask and right & mask)
        for i in diagonal:
            diagonal[i] += bool(row & right & (1 << i))
    require(min(counts) >= 8, "cover misses a frame demand")
    result = dict(terms=10, copy_bill=60, minimum_hits=min(counts),
                  hit_histogram=dict(sorted(Counter(counts).items())),
                  frame_counts_sha256=hashlib.sha256(bytes(counts)).hexdigest())
    require(json.loads(json.dumps(result)) == cover["exact_check"], "cover receipt changed")
    diagonal_result = dict(minimum=min(diagonal.values()),
                           histogram=dict(sorted(Counter(diagonal.values()).items())))
    require(json.loads(json.dumps(diagonal_result)) == cover["diagonal_support_coverage"],
            "diagonal support receipt changed")
    return result


def check_diagonal_coverage(data, cover):
    """Separate necessary identity check; frame feasibility does not imply it."""
    _, _, supports, _ = geometry(data)
    covered = 0
    for a, b, cut in cover["terms"]:
        covered |= (supports[a] ^ int(cut, 16)) & supports[b]
    missing = [i for i in data["live"] if not covered & (1 << i)]
    require(not missing, "uncovered diagonal prevents a masked identity: " + str(missing))
