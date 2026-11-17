# Star patterns at minimum degree three: the floor n+1 on the wheel W4 and on K33 (no κ)

No κ claim, no word and no supplier change. This package extends the star-pattern
floor of DreamingOfClouds's open PR #7114 from minimum degree four to two graphs
of minimum degree three that contain no `K_4`.

## 1. Result

Notation is that of #7114 (section 8) and #6933. For a simple graph Γ on `n`
points, `G_Γ` has the points and the edges of Γ ("pairs") as vertices. A point is
adjacent to the pairs containing it, two pairs are adjacent iff they are
disjoint, and two points are never adjacent. A *k-block pattern* on a graph is a
matrix with `k x k` blocks, invertible diagonal blocks and zero blocks on
non-adjacent pairs. `H_f(G;F)` is the infimum of `rank/k` over all `k` and all
k-block patterns over the field `F` (the fractional Haemers bound of Bukh and Cox).

**Theorem 1 (finite certificate plus the scoped proof of section 2).** Let Γ be
the wheel `W_4` (a hub joined to a 4-cycle, `n = 5`) or `K_{3,3}` (`n = 6`).
For every field `F` and every `k`, every k-block pattern on `G_Γ` has rank at
least `(n+1)k`. Hence

| Γ | minimum degree | contains `K_4` | `H_f(G_Γ;F)`, every field |
|---|---|---|---|
| `W_4` | 3 | no | 6 |
| `K_{3,3}` | 3 | no | 7 |

The upper bound `n+1` is the Gram representation of #7114 Corollary 12, which
the verifier rebuilds as an integer matrix and checks entry by entry.

**Corollary 2 (star configurations, scoped proof).** Let `(K, Γ, (T_e))` be a
star configuration in a graph `G` in the sense of #7114 section 1, with
`|K| = m`. If Γ has a subgraph isomorphic to `W_4` or `K_{3,3}`, then every
k-block pattern on `G` over every field has rank at least `(m+1)k`. In the
notation of #7114 Theorem 3', `j >= k`.

**Corollary 3 (five points, exhaustive count).** All 26 labelled graphs on five
points with minimum degree at least 3 contain `W_4`, so Corollary 2 applies to
each of them. The one such graph on four points is `K_4`, where `G_Γ` is the
Petersen graph; its value 5 is the published result cited under Credit and related work and is
not re-proved here.

**Remark 4 (degree two is not enough, scoped proof).** For every cycle `C_n`,
`n >= 3`, `H_f(G_{C_n};F) = n` over every field. So the floor `n+1` can fail at
minimum degree 2.

What was known: #7114 Theorem 3' gives `j >= k` when every non-isolated vertex
of Γ has degree at least 4. At degree 3 its inequality (a) gives only
`j/k >= 1/2` for cubic Γ. The Petersen case `Γ = K_4` has value 5 by Blasiak,
Kleinberg and Lubetzky, with an all-field dual in Tuafo's merged #1744.

## 2. Why a dual certificate bounds every block pattern

This is the rank argument of Tuafo's #1744
(`research/p112-characteristic-two-minrank/README.md`, "Exact Petersen
certificate and the all-field lower bound"), restated for a general graph `G`
with vertex set `V`.

Let `B` be a k-block pattern on `G` over a field `F`. Let `W` be the row space
of `B` inside `F^(|V| k)`, let `E_v` be the span of the `k` coordinate vectors of
block `v`, and put

```text
f(S) = dim(W + sum of E_v over v in S) / k      for S a subset of V.
```

Then `f(empty) = rank(B)/k` and:

- **(N)** `f(V) = |V|`.
- **(M)** `f(S+v) - f(S) <= 1`: block `v` adds at most `k` dimensions.
- **(S)** `f(S+i) + f(S+j) >= f(S+i+j) + f(S)`: write `A_S = W + E_S`. Then
  `A_{S+i} + A_{S+j} = A_{S+i+j}` and `A_{S+i} ∩ A_{S+j}` contains `A_S`, and
  `dim X + dim Y = dim(X+Y) + dim(X ∩ Y)`.
- **(D)** `f(S+v) = f(S)` if every neighbour of `v` lies in `S`: the `k` rows of
  block row `v` lie in `W`, and they vanish outside block `v` and the blocks of
  the neighbours of `v`. Subtracting their neighbour parts, which lie in `E_S`,
  leaves `k` vectors supported in block `v` whose entries are the rows of the
  invertible block `B_vv`. They span `E_v`, so `E_v` lies in `W + E_S`.

By (D), `f(S) = f(cl S)`, where `cl S` is obtained by adding, repeatedly, every
vertex whose neighbours all lie in the set. A *certificate* is a list of
instances of (M) and (S) with positive rational multipliers whose weighted sum,
after replacing every set by its closure, is

```text
f(cl empty) - c f(V) >= r.
```

With (N) it proves `rank(B)/k = f(empty) >= r + c |V|` for every `k` and every
field. No field property is used.

`certificates.json` lists, for each graph, entries `["M", S, v]` and
`["S", S, i, j]` (sets as bit masks, points first, then pairs in the listed edge
order) with a multiplier. The verifier applies every automorphism of Γ to every
entry and gives each image the multiplier divided by the group order. Each image
is again an instance of (M) or (S), so the averaged list is a certificate in the
sense above, whatever the group is. The sizes:

| Γ | vertices of `G_Γ` | automorphisms | listed entries | `r + c |V|` |
|---|---|---|---|---|
| `W_4` | 13 | 8 | 86 | 6 |
| `K_{3,3}` | 15 | 72 | 197 | 7 |

## 3. Proofs of the corollaries and the remark

**Corollary 2.** Let Γ' be a subgraph of Γ isomorphic to `W_4` or `K_{3,3}`,
with point set `Q` inside `K`. Keep all of `K` and only the edge ports `T_e`
with `e` an edge of Γ'. By (C1) of #7114 such a port is adjacent to its two
ends, which lie in `Q`, and to no other vertex of `K`. So the induced subgraph
of `G` on these vertices is the disjoint union of the `m - |Q|` isolated
vertices `K \ Q` and a graph `H` on `Q` and the chosen ports. By (C1) and (C2),
`H` has every point-pair edge of `G_{Γ'}` and no edge between pairs that share
a point; pairs that are disjoint may or may not be adjacent. So `H` is a
spanning subgraph of `G_{Γ'}`, and a pattern on `H` is a pattern on `G_{Γ'}`
(it has the required zero blocks and more). The principal submatrix of a
k-block pattern on these vertices is block diagonal: `m - |Q|` invertible
`k x k` blocks and a pattern on `H`. Its rank is at least
`(m - |Q|)k + (|Q| + 1)k = (m+1)k` by Theorem 1, and the rank of the whole
pattern is at least that. ∎

**Corollary 3.** The verifier enumerates all `2^10` labelled graphs on five
points and all `2^6` on four, keeps those of minimum degree at least 3, and
searches each for `K_4` and `W_4`. Counts: 26 graphs on five points (11 contain
`K_4`, all 26 contain `W_4`) and one on four points (`K_4`). ∎

**Remark 4.** The `n` points are pairwise non-adjacent, so the principal
submatrix on them is block diagonal with invertible blocks and the rank is at
least `nk`. For the upper bound take the `n` cliques `{c, pair (c, c+1)}`; the
sum of the outer squares of their indicator vectors has unit diagonal, is zero
outside the cliques, and has rank at most `n` over every field. The verifier
builds this matrix for `n = 3, 4, 5, 6`; the argument is the same for every `n`. ∎

## 4. Evidence and reproduction

From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/star-pattern-degree-three-floor
python3.12 -I -B -W error -X dev research/star-pattern-degree-three-floor/verify.py
```

`verify.py` uses the standard library only and exact `Fraction` arithmetic. It
ends with

```text
PASS_STAR_PATTERN_DEGREE_THREE_FLOOR graphs=2 controls=14 cycles=4 census=27 no_new_kappa
```

and runs in under one second. For each graph it checks minimum degree 3, the
absence of `K_4`, the certificate (bound exactly `n+1`), and the integer Gram
pattern. The 14 rejecting controls are, per graph: the certificate without its
first entry, without its last entry, with the first multiplier doubled, with the
first multiplier negated, on Γ with one edge deleted, on Γ with one edge moved,
and the Gram matrix against `G_Γ` with one pair-pair adjacency removed.

`derive_certificates.py` is how the certificates were found. It needs numpy and
scipy, solves the symmetry-reduced linear program in floating point, rounds the
dual, and keeps it only if the exact check accepts it. It is not registered and
the verifier never imports it:

```sh
python3.12 -B research/star-pattern-degree-three-floor/derive_certificates.py /tmp/certificates.json
```

A different solver version may return a different optimal dual; any dual the
exact check accepts proves the same bound.

## 5. Limitations

- Finite certificates for two graphs. No statement is proved for all graphs of
  minimum degree 3.
- The prism (the other cubic graph on six points) is **not** certified. The
  floating-point optimum of its linear program is 7.0, but the rounded dual was
  rejected by the exact check, so no bound is claimed for it.
- The linear program only bounds below. On these two graphs it meets the Gram
  upper bound; on other graphs it may not.
- The block-mask model is that of #6933 and #7114: whole `k x k` blocks, one
  `k` for all ports, linear labels. Nothing is said about sub-block masks or
  port-dependent block sizes.
- The orthogonal 8-sets of P104, P112 and P120 have minimum degree 5, 6 and 7
  (#7114), so their floor 9 does not need this result. Corollary 2 matters for
  a port system or sub-configuration whose star graph has degree-3 vertices.
- #7114 is open and unreviewed. Only its definitions and its Gram labels are
  used; the labels are re-checked here as an integer matrix.
- No human or proof-kernel review of this package is claimed.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Is `j >= k` forced for **every** star configuration whose Γ has minimum
   degree at least 3? The cube `Q_3` contains none of `K_4`, `W_4`, `K_{3,3}`
   and has 8 + 12 = 20 vertices in `G_Γ`.
2. Certify or refute the prism value 7 with an exact dual.
3. What are the exact values at minimum degree 2 beyond cycles? A local,
   unshipped run of the same exact pipeline gave lower bounds 9/2 for `K_4`
   minus an edge and 11/2 for `K_{2,3}`; no matching upper bound was sought.

## Credit and related work

- DreamingOfClouds, #6933 (`research/p104-port-window-haemers`) and open PR
  #7114 (head `fc90dc68b54d613a0600e5bddd8e4f557a4b4eda`): block patterns and
  the port window, star configurations, the graphs `G_Γ`, Theorem 3', the Gram
  upper bound, and the open question this package addresses.
- Tuafo, #1744 (`research/p112-characteristic-two-minrank`): the all-field rank
  argument of section 2 and the exact Petersen dual.
- A. Blasiak, R. Kleinberg, E. Lubetzky, *Index coding via linear programming*
  (arXiv:1004.1379): the linear program and the Petersen rate 5.
- B. Bukh, C. Cox, *On a fractional version of Haemers' bound*
  (arXiv:1802.00476): `H_f`.

The two certificates, the corollaries, the cycle remark and the verifier were
produced by Nick Petalas. New work is Apache-2.0.
