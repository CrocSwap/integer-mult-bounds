#!/usr/bin/env python3
"""Pair (0, 3) beside (0, 9) on the sharp T2 window [8, 18].

Standard library only. Every scientific gate raises SystemExit, so -O cannot
silence a failure. The finite domains are the weight-3 diagonal states at
8 <= s <= 18 (at most 11,280 states in one layer; 10 column pairs; at most
36 successor candidates), the 180 one-low states at s = 8, the 56 prefixes of
each, and the joined T2 endpoint pairs. No recursion and no solver.

Interface (cited, not re-proved): research/six-source-c6-centre-classification
defines a c=6 six-source floor word and a weight-3 mask. The window question
is the open next question of PR #7176.
"""

import hashlib
import json
import sys
from pathlib import Path

C = 6
K = 6
LENGTH = 36
PAIR_SUM = 39
TOP = 18
LOW = 8
MID = 9
ALLOWED = (0, 1, 6, 7, 12)
T2 = (0, 6, 7, 7, 7, 12)
OTHER_L1 = (1, 6, 6, 7, 7, 12)
START_S = (1, 6, 6, 7, 7, 12)
LAYER_SIZES = {
    8: 3600, 9: 5520, 10: 7740, 11: 9900, 12: 11220, 13: 11280,
    14: 9780, 15: 7240, 16: 4500, 17: 2040, 18: 700,
}
FAMILY_SIZES = {
    (0, 1, 7, 7, 12, 12): 180,
    (0, 6, 7, 7, 7, 12): 120,
    (1, 1, 1, 12, 12, 12): 20,
    (1, 1, 6, 7, 12, 12): 180,
    (1, 6, 6, 7, 7, 12): 180,
    (6, 6, 6, 7, 7, 7): 20,
}
CANONICAL = "230000004223344555234555443322111111"
CITED_09 = "345555552443322111234111223344000000"
CITED_T2 = "345555554433222111234111220334400000"
PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def weight3(sv):
    """All coordinates in {0,1,6,7,12} and exactly three in {1,7}."""
    ones = 0
    for value in sv:
        if value not in ALLOWED:
            return False
        if value % C == 1:
            ones += 1
    return ones == 3


def column_options():
    """Pairs 0 <= q <= t <= 6 with q + t in the allowed set. Ten pairs."""
    return [(q, t) for t in range(C + 1) for q in range(t + 1) if q + t in ALLOWED]


def static_states(s):
    """Every weight-3 diagonal state (q_s, q_{39-s}). Pruning drops only sums past the target."""
    opts = column_options()
    parts = [((), 0, 0, 0)]
    for _ in range(K):
        grown = []
        for cols, sq, st, ones in parts:
            for q, t in opts:
                nsq, nst = sq + q, st + t
                nones = ones + ((q + t) % C == 1)
                if nsq <= s and nst <= PAIR_SUM - s and nones <= 3:
                    grown.append((cols + ((q, t),), nsq, nst, nones))
        parts = grown
    out = []
    for cols, sq, st, ones in parts:
        if sq == s and st == PAIR_SUM - s and ones == 3:
            out.append((tuple(c[0] for c in cols), tuple(c[1] for c in cols)))
    return out


def diag_sum(state):
    return tuple(a + b for a, b in zip(state[0], state[1]))


def lows(state):
    return sum(1 for value in diag_sum(state) if value <= 1)


def base_vector(state):
    return tuple(C * (value // C) for value in diag_sum(state))


def successors(state, nxt):
    """States at s+1 from an early letter a and a late letter b."""
    q, t = state
    found = []
    for a in range(K):
        qa = q[:a] + (q[a] + 1,) + q[a + 1:]
        for b in range(K):
            if t[b] == 0:
                continue
            tb = t[:b] + (t[b] - 1,) + t[b + 1:]
            if (qa, tb) in nxt:
                found.append((qa, tb))
    return found


def parameters():
    """(H, L, A, B, C, D): heavy, low, two prefix-count-1 mids, two prefix-count-0 mids."""
    rows = []
    for heavy in range(K):
        for low in range(K):
            if low == heavy:
                continue
            mids = [j for j in range(K) if j != heavy and j != low]
            for i in range(4):
                for j in range(i + 1, 4):
                    first, second = mids[i], mids[j]
                    rest = [x for x in mids if x != first and x != second]
                    rows.append((heavy, low, first, second, rest[0], rest[1]))
    return rows


def state_of(heavy, low, first, second):
    """Diagonal state at s=8 for this parameter tuple. C and D do not appear in the counts."""
    q = [0] * K
    t = [C] * K
    q[heavy] = C
    q[first] = 1
    q[second] = 1
    t[low] = 1
    return (tuple(q), tuple(t))


def three_orders(a, b, h):
    """The six permutations of three distinct letters, as the first three prefix letters."""
    raw = (a, b, h)
    orders = []
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            k = 3 - i - j
            orders.append((raw[i], raw[j], raw[k]))
    return orders


def build_word(heavy, low, first, second, third, fourth, first3):
    """Floor word with the given roles. first3 is a permutation of (first, second, heavy)."""
    word = [heavy] * LENGTH
    word[0], word[1], word[2] = first3
    word[8] = third
    pairs = [first, first, second, second, third, third, fourth, fourth, fourth]
    for offset, letter in enumerate(pairs):
        s = 9 + offset
        word[s] = letter
        word[38 - s] = letter
    word[18], word[19], word[20] = first, second, third
    word[30] = low
    for pos in range(31, LENGTH):
        word[pos] = low
    return word


def as_text(word):
    return "".join(str(letter) for letter in word)


def counts(letters, n):
    return tuple(letters[:n].count(j) for j in range(K))


def diagonal(letters, s):
    return tuple(counts(letters, s)[j] + counts(letters, PAIR_SUM - s)[j] for j in range(K))


def check_floor(letters):
    require(len(letters) == LENGTH, "length")
    require(all(0 <= x < K for x in letters), "alphabet")
    require(all(letters.count(j) == C for j in range(K)), "not a floor word")


def check_window(letters, want_03, want_09):
    """Weight-3 on [8, 18], endpoint family T2, and the requested early pairs."""
    check_floor(letters)
    for s in range(LOW, TOP + 1):
        require(weight3(diagonal(letters, s)), "window failed at s=%d" % s)
    require(tuple(sorted(diagonal(letters, TOP))) == T2, "endpoint family")
    if want_03:
        require(weight3(counts(letters, 3)), "(0,3) failed")
    if want_09:
        require(weight3(counts(letters, MID)), "(0,9) failed")


def rejects(text):
    try:
        letters = [int(ch) for ch in text]
        check_floor(letters)
    except (SystemExit, ValueError):
        return True
    return False


def prefix_census(states):
    """Every one-low state has 56 prefixes and exactly 6 make (0, 3) weight-3."""
    for state in states:
        q = state[0]
        heavy = [i for i, value in enumerate(q) if value == C]
        singles = [i for i, value in enumerate(q) if value == 1]
        require(len(heavy) == 1 and len(singles) == 2, "q shape %r" % (q,))
        h, a, b = heavy[0], singles[0], singles[1]
        seen = 0
        good = 0
        favorable = []
        for i in range(LOW):
            for j in range(LOW):
                if i == j:
                    continue
                word = [h] * LOW
                word[i] = a
                word[j] = b
                seen += 1
                q3 = tuple(word[:3].count(letter) for letter in range(K))
                both_early = i < 3 and j < 3
                require(weight3(q3) == both_early, "prefix test %r" % (word,))
                if both_early:
                    good += 1
                    favorable.append(tuple(word))
        require(seen == 56 and good == 6, "prefix counts %d %d" % (seen, good))
        expect = []
        for first3 in three_orders(a, b, h):
            expect.append(first3 + (h, h, h, h, h))
        require(set(favorable) == set(expect), "favorable prefixes")
    return 56, 6


def check_construction(rows):
    """Every parameter tuple and each of its six (0, 3) prefixes is a T2 word through (0, 9)."""
    texts = []
    for heavy, low, first, second, third, fourth in rows:
        state = state_of(heavy, low, first, second)
        for first3 in three_orders(first, second, heavy):
            word = build_word(heavy, low, first, second, third, fourth, first3)
            letters = word
            check_window(letters, True, True)
            require(counts(letters, LOW) == state[0], "constructed q8")
            require(counts(letters, PAIR_SUM - LOW) == state[1], "constructed q31")
            require(tuple(sorted(diagonal(letters, LOW))) == START_S, "S(8)")
            s9 = diagonal(letters, MID)
            require(tuple(sorted(s9)) == T2, "S(9)")
            for s in range(MID + 1, TOP + 1):
                require(diagonal(letters, s) == s9, "S moved at s=%d" % s)
            require(weight3(counts(letters, 3)) and weight3(counts(letters, MID)), "early pairs")
            texts.append(as_text(letters))
    require(len(texts) == 180 * 6 and len(set(texts)) == 180 * 6, "constructed words")
    require(CANONICAL in texts, "canonical word missing")
    return len(texts)


def build_graph():
    layers = {s: static_states(s) for s in range(LOW, TOP + 1)}
    for s, size in LAYER_SIZES.items():
        require(len(layers[s]) == size, "layer %d has %d states" % (s, len(layers[s])))
    sets = {s: set(v) for s, v in layers.items()}
    succ = {}
    steps = 0
    for s in range(LOW, TOP):
        succ[s] = {}
        for state in layers[s]:
            nxt = successors(state, sets[s + 1])
            succ[s][state] = nxt
            steps += len(nxt)
            for other in nxt:
                require(base_vector(state) == base_vector(other), "base changed at s=%d" % s)
    require(steps == 592020, "edge count %d" % steps)
    return layers, succ, steps


def family_data(layers):
    groups = {}
    for index, state in enumerate(layers[TOP]):
        groups.setdefault(tuple(sorted(diag_sum(state))), []).append(index)
    sizes = {fam: len(idx) for fam, idx in groups.items()}
    require(sizes == FAMILY_SIZES, "family sizes %r" % (sizes,))
    masks = {}
    for fam, idx in groups.items():
        mask = 0
        for bit in idx:
            mask |= 1 << bit
        masks[fam] = mask
    return masks


def backward(layers, succ, filter_09):
    reach = {TOP: {state: 1 << i for i, state in enumerate(layers[TOP])}}
    for s in range(TOP - 1, LOW - 1, -1):
        layer = {}
        for state in layers[s]:
            mask = 0
            for nxt in succ[s][state]:
                mask |= reach[s + 1][nxt]
            if filter_09 and s == MID and not weight3(state[0]):
                mask = 0
            layer[state] = mask
        reach[s] = layer
    return reach


def popcount(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count


def endpoint_relation(layers, succ, states, masks):
    """Filtered and unfiltered T2 endpoint sets agree, and forward recomputes them."""
    plain = backward(layers, succ, False)
    filtered = backward(layers, succ, True)
    t2_mask = masks[T2]
    other_mask = masks[OTHER_L1]
    reachers = [state for state in layers[LOW] if plain[LOW][state] & t2_mask]
    require(set(reachers) == set(states), "T2 starts are not the 180 one-low states")
    joined_t2 = 0
    joined_other = 0
    for state in states:
        require((plain[LOW][state] & t2_mask) == (filtered[LOW][state] & t2_mask), "T2 mask changed")
        require((plain[LOW][state] & other_mask) == (filtered[LOW][state] & other_mask), "other mask changed")
        require(popcount(filtered[LOW][state] & t2_mask) > 0, "state misses T2")
        joined_t2 += popcount(filtered[LOW][state] & t2_mask)
        joined_other += popcount(filtered[LOW][state] & other_mask)
    require(joined_t2 == 720 and joined_other == 1080, "joined counts %d %d" % (joined_t2, joined_other))
    nonzero9 = sum(1 for mask in filtered[MID].values() if mask)
    require(nonzero9 == 480, "filtered s=9 count %d" % nonzero9)
    for state, mask in filtered[MID].items():
        if mask:
            require(weight3(state[0]), "filtered s=9 state has a non-weight-3 q9")
    forward = forward_counts(layers, succ, states, t2_mask)
    for state in states:
        require(forward[state] == popcount(filtered[LOW][state] & t2_mask), "forward mismatch")
    return filtered, joined_t2, joined_other, sum(forward.values())


def forward_counts(layers, succ, states, t2_mask):
    """Popcount of T2 endpoints reachable from each start through a weight-3 q9."""
    index = {state: i for i, state in enumerate(states)}
    current = {state: 1 << index[state] for state in states}
    for s in range(LOW, TOP):
        nxt = {}
        for state, mask in current.items():
            for other in succ[s][state]:
                if s == LOW and not weight3(other[0]):
                    continue
                nxt[other] = nxt.get(other, 0) | mask
        current = nxt
    counts = {state: 0 for state in states}
    end_index = {state: i for i, state in enumerate(layers[TOP])}
    for end, mask in current.items():
        if (t2_mask >> end_index[end]) & 1 == 0:
            continue
        bit = 0
        left = mask
        while left:
            if left & 1:
                counts[states[bit]] += 1
            left >>= 1
            bit += 1
    return counts


def lift_pairs(layers, succ, filtered, states):
    """One explicit word for every filtered T2 joined pair, with a (0, 3) prefix."""
    t2_bits = []
    for index, state in enumerate(layers[TOP]):
        if tuple(sorted(diag_sum(state))) == T2:
            t2_bits.append(index)
    lifts = 0
    for start in states:
        mask = filtered[LOW][start]
        q = start[0]
        heavy = q.index(C)
        singles = [i for i, value in enumerate(q) if value == 1]
        prefix = (singles[0], singles[1], heavy, heavy, heavy, heavy, heavy, heavy)
        for bit in t2_bits:
            if (mask >> bit) & 1 == 0:
                continue
            chain = [start]
            state = start
            for s in range(LOW, TOP):
                nxt = [y for y in succ[s][state] if filtered[s + 1][y] & (1 << bit)]
                require(nxt, "path stuck at s=%d" % s)
                state = nxt[0]
                chain.append(state)
            word = chain_to_word(chain, prefix)
            check_window(word, True, True)
            require(counts(word, LOW) == chain[0][0], "lift q8")
            require(counts(word, PAIR_SUM - LOW) == chain[0][1], "lift q31")
            require(counts(word, TOP) == chain[-1][0], "lift q18")
            require(counts(word, PAIR_SUM - TOP) == chain[-1][1], "lift q21")
            lifts += 1
    require(lifts == 720, "lifts %d" % lifts)
    return lifts


def chain_to_word(chain, prefix):
    """Lift a state path. Prefix order is the only free data inside q_8."""
    word = [None] * LENGTH
    for pos, letter in enumerate(prefix):
        word[pos] = letter
    for offset in range(TOP - LOW):
        s = LOW + offset
        q, t = chain[offset]
        q2, t2 = chain[offset + 1]
        early = [j for j in range(K) if q2[j] != q[j]]
        late = [j for j in range(K) if t2[j] != t[j]]
        require(len(early) == 1 and len(late) == 1, "step letters")
        word[s] = early[0]
        word[38 - s] = late[0]
    qf, tf = chain[-1]
    pos = TOP
    for letter in range(K):
        for _ in range(tf[letter] - qf[letter]):
            word[pos] = letter
            pos += 1
    require(pos == 21, "middle fill %d" % pos)
    _q0, t0 = chain[0]
    pos = PAIR_SUM - LOW
    for letter in range(K):
        for _ in range(C - t0[letter]):
            word[pos] = letter
            pos += 1
    require(pos == LENGTH and all(x is not None for x in word), "word has holes")
    return word


def check_sources():
    sources = json.loads((PKG / "SOURCES.json").read_text(encoding="utf-8"))
    checked = 0
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "pin " + row["path"])
        text = data.decode("utf-8")
        for anchor in ("{0,1,6,7,12}", "weight-3 mask", "333333012000001111122222444444555555"):
            require(anchor in text, "anchor missing in " + row["path"])
        checked += 1
    require(checked == 1, "expected one live input")
    return checked


def check_controls(layers, states):
    """Meaningful failures: order, a chain that misses (0, 9), and malformed words."""
    heavy, low, first, second, third, fourth = 0, 1, 2, 3, 4, 5
    bad_prefix = (heavy, heavy, heavy, heavy, heavy, heavy, first, second)
    bad = build_word(heavy, low, first, second, third, fourth, (first, second, heavy))
    for pos, letter in enumerate(bad_prefix):
        bad[pos] = letter
    check_window(bad, False, True)
    require(not weight3(counts(bad, 3)), "bad prefix became weight-3 at (0,3)")
    require(tuple(bad[:LOW]).count(heavy) == C, "bad prefix changed the counts")

    cited_09 = [int(ch) for ch in CITED_09]
    check_window(cited_09, True, True)
    cited_t2 = [int(ch) for ch in CITED_T2]
    check_window(cited_t2, True, False)
    require(not weight3(counts(cited_t2, MID)), "cited T2 word became weight-3 at (0,9)")
    require(tuple(sorted(counts(cited_t2, MID))) == (0, 0, 0, 1, 2, 6), "cited q9 shape")
    q8 = counts(cited_t2, LOW)
    q31 = counts(cited_t2, PAIR_SUM - LOW)
    require((q8, q31) in set(states), "cited T2 word leaves the 180 states")

    require(rejects(CANONICAL[:-1]), "35 letters accepted")
    require(rejects(CANONICAL[:-1] + CANONICAL[0]), "a seventh copy accepted")
    stray = (6, 2, 0, 0, 0, 0), (6, 6, 6, 6, 6, 1)
    require(stray not in set(layers[LOW]), "a q-shape outside the census was enumerated")
    readme = (PKG / "README.md").read_text(encoding="utf-8")
    for text in (CANONICAL, CITED_09, CITED_T2):
        require(text in readme, "README lacks a witness")
    l0 = sum(1 for state in layers[LOW] if lows(state) == 0)
    l_high = sum(1 for state in layers[LOW] if lows(state) > 1)
    require(l0 == 3420 and l_high == 0, "s=8 low profile %d %d" % (l0, l_high))
    return 7, l0


def run():
    inputs = check_sources()
    require(len(column_options()) == 10, "column options")
    rows = parameters()
    states = [state_of(h, low, a, b) for h, low, a, b, _c, _d in rows]
    require(len(rows) == 180 and len(set(states)) == 180, "parameter count")
    for state in states:
        require(weight3(diag_sum(state)) and lows(state) == 1, "formula state")
        require(tuple(sorted(state[0])) == (0, 0, 0, 1, 1, 6), "formula q")
        require(tuple(sorted(diag_sum(state))) == START_S, "formula S")
    prefixes, favorable = prefix_census(states)
    constructed = check_construction(rows)
    layers, succ, _steps = build_graph()
    require(set(states) == {s for s in layers[LOW] if lows(s) == 1}, "formula misses a one-low state")
    no_t2_at_8 = [s for s in layers[LOW] if tuple(sorted(diag_sum(s))) == T2]
    require(no_t2_at_8 == [], "T2 multiset occurs at s=8")
    masks = family_data(layers)
    filtered, joined_t2, joined_other, forward = endpoint_relation(layers, succ, states, masks)
    lifts = lift_pairs(layers, succ, filtered, states)
    controls, l0 = check_controls(layers, states)
    print(
        "PASS_SIX_SOURCE_C6_PREFIX_PAIR_03 l1=%d prefixes=%d favorable=%d constructed=%d "
        "lifts=%d joined_t2=%d joined_other=%d forward=%d layer8=%d l0=%d controls=%d inputs=%d"
        % (len(states), prefixes, favorable, constructed, lifts, joined_t2, joined_other,
           forward, len(layers[LOW]), l0, controls, inputs)
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
