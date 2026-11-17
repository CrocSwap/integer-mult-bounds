# Proof: at most 23 distinct adjacent pairs

## Setting

A word is a cyclic sequence `w_0, ..., w_{L-1}` over the letter set
`[8] = {0,...,7}`. A *closed* word has the property that each letter count is
even, which is the standing hypothesis of the singleton connector model: the
prefix walk returns to the origin exactly when every coordinate is used an even
number of times.

For a slot `t` (indices mod `L`) the *adjacent pair* is the unordered pair
`{w_t, w_{t+1}}`. A pair `{i,i}` is a *loop*. `mult(i,j)` is the number of
slots with pair `{i,j}`; `m_i` is the number of occurrences of letter `i`; and
`G` is the simple graph on `[8]` with `{i,j}` an edge exactly when
`mult(i,j) > 0`.

## Lemma 1 (incidence identity and degree bound)

For every letter `i`,

```text
2 m_i = sum_{j != i} mult(i,j) + 2 * loops_i,
```

and therefore

```text
deg_G(i) <= sum_{j != i} mult(i,j) <= 2 m_i.
```

Also `deg_G(i) <= 7`.

**Proof.** Each occurrence of `i` at position `t` lies in exactly two slots: the
slot ending at `t` and the slot starting at `t`. Both contain `i`. Summing over
occurrences counts every non-loop slot containing `i` once and every loop at `i`
twice. This gives the identity. The number of distinct partners is at most the
number of non-loop incidences, which is at most `2 m_i`. The last inequality is
`|V(G)| = 8`. QED

## Lemma 2 (Euler correspondence)

The multiset of adjacent pairs of a closed word is exactly the edge multiset of
a connected Eulerian multigraph on the letters, with degree `2 m_i` at letter
`i`. Conversely, every connected multigraph with even degrees `2 m_i` has an
Euler circuit, and reading its vertices produces a closed word with those
multiplicities and that adjacent-pair multiset.

**Proof.** The closed word is a closed walk in the letter multigraph; every edge
is one slot. Conversely an Euler circuit traverses each edge once, and the
degree of a vertex in an Eulerian circuit equals its degree in the multigraph.
QED

## Theorem

Let `w` be a closed word of length 28 over `[8]` with multiplicities
`(4,4,4,4,4,4,2,2)`. Then `D(w)`, the number of distinct unordered adjacent
pairs, satisfies `D(w) <= 23`. The bound is attained.

**Proof.** Let `L` be the set of the two letters with `m_i = 2`. Its complement
in `[8]` is the six letters with `m_i = 4`.

For `i` in `L`, Lemma 1 gives `deg_G(i) <= 2 m_i = 4`. Since `K_8` has degree 7,
letter `i` is missing at least `7 - 4 = 3` edges to other letters.

Let `M_i` be the set of edges of `K_8` at `i` that are absent from `G`. Then
`|M_i| >= 3`. The two light letters `a, b` are distinct. If an edge belongs to
`M_a` and to `M_b`, then it is incident with both `a` and `b`, hence it is the
single edge `{a,b}`. Therefore

```text
|M_a union M_b| >= |M_a| + |M_b| - 1 >= 3 + 3 - 1 = 5.
```

Each missing edge is one of the 28 edges of `K_8`, so at least 5 edges are
missing and

```text
D(w) = |E(G)| <= 28 - 5 = 23.
```

QED

## Sharpness

Take letters `0,...,5` heavy and `6,7` light. Delete the five edges
`{6,7}, {0,6}, {1,6}, {2,7}, {3,7}` from `K_8`. The remaining graph has 23
edges and degrees

```text
deg(0)=deg(1)=deg(2)=deg(3)=6,  deg(4)=deg(5)=7,  deg(6)=deg(7)=4.
```

Add the extra copies `{0,1}` twice, `{2,3}` twice and `{4,5}` once. The
resulting loop-free connected multigraph has 28 edges and degrees

```text
(8,8,8,8,8,8,4,4).
```

Every degree is even, so Lemma 2 gives an Euler circuit, hence a closed word
with counts `(4,4,4,4,4,4,2,2)` whose distinct adjacent pairs are exactly the
23 distinct edges. One such circuit is

```text
0107547156453236250432413021.
```

The only repeated pairs are `{0,1}` and `{2,3}`, each on three slots, and
`{4,5}` on two slots; the total number of repeated slots is
`2 + 2 + 1 = 5`. So `D = 23` is attained.

## Corollaries

**Corollary 1 (weight-2 sums).** A two-letter arc has sum `e_i + e_j`. A loop
has sum 0. Hence at most `D(w) <= 23` of the 28 weight-2 vectors of `F_2^8` are
sums of two-letter arcs of `w`. At least five weight-2 vectors are not, and
because the weight of an arc sum is congruent to its length modulo 2, each of
those five must be a sum of an arc of even length at least 4.

**Corollary 2 (no all-distinct word).** Suppose the 28 adjacent pairs of a
length-28 word are all distinct. Then `G = K_8` and `deg_G(i) = 7` for every
letter. Lemma 1 forces `2 m_i = 7`, which has no integer solution. So no closed
word with 28 distinct adjacent pairs exists. In particular an Euler circuit of
`K_8` cannot be a length-28 word with the required profile: in a closed trail the
number of occurrences of a letter is half its degree, so every letter would have
to occur `7/2` times.

**Corollary 3 (repeats).** Under the theorem's hypotheses the 28 slots contain
at least five repeated pairs, that is

```text
sum_{edges e of G} (mult(e) - 1) = 28 - D(w) >= 5.
```

## What is not claimed

- No universal length-28 word is constructed or excluded; `28 <= f(8) <= 32` is
  unchanged.
- The bound 23 is sharp for the multiplicity profile, not for universality. The
  sharp word above has 156 distinct arc sums and is not universal.
- The degree count uses only two-letter arcs. It gives no bound on arcs of
  length 3 or more.
- No selected-frontier, supplier, native, precision or kappa claim.
- A search that failed to find a universal word is not a proof of nonexistence,
  and no such search is reported as evidence here.
