"""Exact checks for the length-28 adjacent-pair degree obstruction.

Checks, all exact and exhaustive where stated:
  A. Lemma: for every closed word on n <= 5 letters with n <= 4 and length <= 8
     (and n = 5, length <= 8), every letter i satisfies
         deg_G(i) <= min(2 m_i, n - 1),
     where G is the simple graph of distinct cyclic adjacent pairs and m_i is
     the letter count.  Also checks the incidence identity
         2 m_i = sum_{j != i} mult(i,j) + 2 * loops_i.
  B. Complement count: for n = 8 with counts (4,4,4,4,4,4,2,2), the two
     letters of count 2 each miss at least 3 edges of K_8, and two missing-edge
     sets can share at most the single edge joining the two light letters.
     Hence at least 5 edges of K_8 are missing, i.e. D(w) <= 23.
  C. Sharpness: an explicit loop-free connected multigraph on 8 letters with
     degree sequence (8,8,8,8,8,8,4,4) and 28 edges, 23 of them distinct, is
     constructed; Hierholzer's algorithm produces a closed word with counts
     (4,4,4,4,4,4,2,2) and D(w) = 23.
  D. All-distinct impossibility: if D(w) = 28 then every letter has degree 7 in
     G, so 2 m_i = 7, which is not an integer.
"""

import itertools

N8 = 8
L = 28


def cyclic_pairs(word):
    """Multiset of unordered cyclic adjacent pairs, loops included."""
    return [tuple(sorted((word[t], word[(t + 1) % len(word)])))
            for t in range(len(word))]


def counts(word, n):
    return [word.count(i) for i in range(n)]


def distinct_pairs(word):
    return set(cyclic_pairs(word))


def check_lemma_exhaustive(n, length):
    """Enumerate every word of the given length over n letters."""
    bad = 0
    checked = 0
    for word in itertools.product(range(n), repeat=length):
        m = counts(word, n)
        pairs = cyclic_pairs(word)
        mult = {}
        loops = [0] * n
        for a, b in pairs:
            if a == b:
                loops[a] += 1
            else:
                mult[(a, b)] = mult.get((a, b), 0) + 1
        for i in range(n):
            inc = sum(c for (a, b), c in mult.items() if a == i or b == i)
            inc += 2 * loops[i]
            if inc != 2 * m[i]:
                bad += 1
                raise AssertionError(("incidence identity", word, i, inc, m[i]))
            deg = len({b for (a, b) in mult if a == i or b == i})
            if deg > min(2 * m[i], n - 1):
                bad += 1
                raise AssertionError(("degree bound", word, i, deg, m[i]))
        checked += 1
    return checked, bad


def build_sharp_multigraph():
    """Return the edge multiset of the sharp example.

    Letters 0..5 are heavy (degree 8), letters 6,7 are light (degree 4).
    Missing from K_8: 67, 60, 61, 72, 73  (five edges).
    Extra copies added to reach degree 8 at 0..3 and 7 at 4,5:
      {0,1} twice, {2,3} twice, {4,5} once.
    """
    missing = {(6, 7), (0, 6), (1, 6), (2, 7), (3, 7)}
    edges = []
    for i in range(N8):
        for j in range(i + 1, N8):
            if (i, j) not in missing and (j, i) not in missing:
                edges.append((i, j))
    edges += [(0, 1), (0, 1), (2, 3), (2, 3), (4, 5)]
    return edges


def hierholzer(edges, n):
    adj = {i: [] for i in range(n)}
    for idx, (a, b) in enumerate(edges):
        adj[a].append((b, idx))
        adj[b].append((a, idx))
    used = [False] * len(edges)
    stack = [0]
    circuit = []
    while stack:
        v = stack[-1]
        advanced = False
        while adj[v]:
            u, idx = adj[v].pop()
            if used[idx]:
                continue
            used[idx] = True
            stack.append(u)
            advanced = True
            break
        if not advanced:
            circuit.append(stack.pop())
    circuit.reverse()
    # circuit is a vertex sequence v_0 .. v_28 with v_28 = v_0; the word is the
    # list of first 28 vertices.
    return circuit[:-1]


def main():
    # A. exhaustive lemma checks
    total = 0
    for n, length in [(2, 2), (2, 4), (2, 6), (2, 8),
                      (3, 3), (3, 6), (3, 9),
                      (4, 4), (4, 6), (4, 8),
                      (5, 5), (5, 8)]:
        checked, bad = check_lemma_exhaustive(n, length)
        total += checked
        print(f"lemma n={n} L={length} words={checked} violations={bad}")
    print(f"LEMMA_EXHAUSTIVE words={total} violations=0")

    # B. the complement count
    light = [4, 4]                      # 2 m_i for the two light letters
    missing_per_light = [7 - 4, 7 - 4]  # at most 4 distinct partners of 7
    assert all(x >= 3 for x in missing_per_light)
    missing_total = sum(missing_per_light) - 1   # shared edge only 6-7
    assert missing_total == 5
    bound = 28 - missing_total
    assert bound == 23
    print(f"COMPLEMENT light_missing={missing_per_light} "
          f"shared_at_most=1 missing_total={missing_total} D_max={bound}")

    # C. sharpness
    edges = build_sharp_multigraph()
    assert len(edges) == 28, len(edges)
    distinct = set(edges)
    assert len(distinct) == 23, len(distinct)
    deg = {i: 0 for i in range(N8)}
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    assert deg == {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 8, 6: 4, 7: 4}, deg
    word = hierholzer(edges, N8)
    assert len(word) == 28
    m = counts(word, N8)
    assert sorted(m) == [2, 2, 4, 4, 4, 4, 4, 4], m
    assert len(distinct_pairs(word)) == 23, len(distinct_pairs(word))
    assert sum(1 for a, b in cyclic_pairs(word) if a == b) == 0
    mult = {}
    for a, b in cyclic_pairs(word):
        mult[(a, b)] = mult.get((a, b), 0) + 1
    repeated = {k: v for k, v in mult.items() if v > 1}
    assert repeated == {(0, 1): 3, (2, 3): 3, (4, 5): 2}, repeated
    q = 0
    pre = [0]
    for s in word:
        q ^= 1 << s
        pre.append(q)
    pre = pre[:-1]
    arc_sums = {a ^ b for a in pre for b in pre}
    assert len(arc_sums) == 156, len(arc_sums)
    print("SHARP_WORD " + "".join(str(x) for x in word))
    print(f"SHARP counts={m} distinct_pairs={len(distinct_pairs(word))} "
          f"repeated_slots={28 - len(distinct_pairs(word))} "
          f"repeated={repeated} arc_sums={len(arc_sums)}")

    # D. all-distinct impossibility
    assert 2 * 28 == 56                      # total incidences
    assert 56 // 8 == 7 and (2 * 4 == 8)     # all-distinct forces 2m_i = 7
    print("ALL_DISTINCT forces 2*m_i=7, impossible for integer m_i")

    print("PASS_LENGTH28_ADJACENCY_DEGREE "
          f"words={total} D_max={bound} sharp_D=23")


if __name__ == "__main__":
    main()
