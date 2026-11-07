# E8 subspace invariants of the P104 ports (no κ)

**No new κ.** This package proves four exact facts about the 104 ports of P104 and the 120 ports of the full E8 set P120 (all 9-bit vectors
of weight 3 or 7): how deep saturation goes, how many ports a subspace can hold, a star law for bicliques of the orthogonality graph, and the
mass of the best flag rectangle at every level. Nothing is priced and no word is constructed.

## Setting

Ambient space `F2^9`, dot product `x.y = wt(x & y) mod 2`. `S` is a port set (`P104 ⊂ P120`). For a subspace `V`, `N(V) = |S ∩ V|` and
`V^perp` is the orthogonal space for the dot product, so `N(V^perp)` counts ports with dot 0 to all of `V`.
`E` is the even-weight hyperplane. Every port has odd weight.

Quadratic form: `q(x) = C(wt x, 2) mod 2`, with polar form `B(x,y) = wt(x)wt(y) + wt(x & y) mod 2`. The radical of `B` is `<1>`
(all-ones, `q(1) = 0`), so `q` descends to `F2^8 = F2^9/<1>`, a nondegenerate form with 120 nonsingular vectors `= 2^7 - 2^3`, that is of plus type
(Witt index 4). The 120 nonsingular classes are the 120 lines of E8 mod 2, and each has exactly one odd representative: P120 is the set of odd
vectors with `q = 1`. For odd `x, y`, `B(x,y) = 1 + x.y`, so dot 1 means E8-orthogonal. (`check.py` verifies all of this.)

A subspace `V` is **saturated** if it contains an odd vector and all its odd vectors are ports. If `V ⊄ E` then `V` has exactly `2^(dim V - 1)` odd
vectors, so `N(V) <= 2^(dim V - 1)` with equality iff `V` is saturated.

## Statements

**Theorem 1 (saturation depth).** In `F2^9` no subspace of dimension >= 5 has all its odd vectors among the nonsingular ones. Hence for **every**
subset of P120 (in particular P104 and P120) there is no saturated subspace of dimension 5, 6, 7 or 8. The saturated subspaces of dimension 1..4 number

| dim | 1 | 2 | 3 | 4 | 5..8 |
|---|---|---|---|---|---|
| P104 | 104 | 5356 | 17958 | 3441 | 0 |
| P120 | 120 | 7140 | 32130 | 11475 | 0 |

**Theorem 2 (ports per dimension).** Let `N_e` be the maximum of `N(V)` over subspaces of dimension `e`. Then

| e | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| P104 | 1 | 2 | 4 | 8 | 12 | 20 | 36 | 60 |
| P120 | 1 | 2 | 4 | 8 | 12 | 20 | 36 | 64 |

so `N_e(P104) = N_e(P120)` for `e = 1..7`, an E8 invariant, and they differ only at `e = 8` (and 9).

**Theorem 3 (star law).** Let `beta_e = max N(V) N(V^perp)` over subspaces of dimension `e`. Call two ports adjacent when their dot product is 0; this
graph is regular of degree 48 on P104 (2496 edges) and degree 56 on P120 (3360 edges). Then

| e | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| P104 | 48 | 48 | 48 | 48 | 48 | 48 | 48 | 48 |
| P120 | 56 | 56 | 48 | 48 | 48 | 48 | 56 | 56 |

In both cases the maximum over `e` is the degree: no biclique `ports(V) x ports(V^perp)` is larger than one port's star (`e = 1`). On P104 this
holds with equality at every dimension. Consequently covering the edges by such bicliques needs at least `2496/48 = 52` (P104) respectively
`3360/56 = 60` (P120) of them.

**Theorem 4 (flag rectangles).** For `g ⊂ A` with `dim g = d - 1`, `dim A = d`, the rectangle `ports(g) x ports(A^perp)` has mass `N(g) N(A^perp)`.
The maximum mass over all flags, level `d = 2..8`:

| d | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| P104 | 30 | 32 | 32 | 36 | 32 | 32 | 30 |
| P120 | 32 | 32 | 32 | 36 | 32 | 32 | 32 |

The mass is `2^5 = 32` at every level of P120 except the middle level `d = 5`, where a 6 x 6 rectangle gives 36. P104 loses 2 at the two end levels
`d = 2` and `d = 8` and equals P120 at the other five levels. Both tables are symmetric under `d <-> 10 - d`. Since `N(g) <= N(A)`, every entry
is at most the corresponding value in Theorem 3.

**Scope.** Statements 1..4 concern port sets only. Theorem 1 is proved by hand below for any subset of P120 and re-counted exactly. Theorems 2..4 are
exact exhaustive results, not closed formulas; the pattern `N_e = 2^(e-2) + 4` for `4 <= e <= 7` (8, 12, 20, 36) fits the data but is not proved here and
fails at `e = 8` (64 and 60). Nothing is said about words, junk, lifetimes or prices.

## Proof

**Theorem 1.** Suppose `V ⊄ E` has all its odd vectors nonsingular and `dim V = 5`; any larger `V` contains such a 5-space (take a subspace containing an
odd vector), so this case suffices. The odd vectors are `u + W` with `u` odd and `W = V ∩ E`, `dim W = 4`. Since `<1>` is odd, `W` maps injectively to
`F2^8`, and `q` is well defined on `F2^8`; we work there.

1. `q(u + w) = 1` for all `w ∈ W`. For `w = 0` this gives `q(u) = 1`, and in general `q(u+w) = q(u) + q(w) + B(u,w)` gives `q(w) = B(u,w)` on `W`.
2. So `q|W` is linear. Then `q(w+w') = q(w) + q(w') + B(w,w')` forces `B(w,w') = 0`: `W` is totally isotropic for `B`. As `B` is nondegenerate on `F2^8`, `W ⊂ W^perp`
   gives `dim W <= 4`, so `W` is a maximal totally isotropic space with `W^perp = W`. If `q|W = 0`, then `B(u,·) = 0` on `W`, so `u ∈ W^perp = W`, and `q(u) = q(w) = 0`,
   a contradiction. Hence `q|W` is a nonzero linear form with kernel `W0`, a totally singular space of dimension 3.
3. `B(u,w0) = q(w0) = 0` for `w0 ∈ W0`, so `u ∈ W0^perp`. The quotient `W0^perp / W0` is a nondegenerate quadratic plane (the form stays of plus type), hence a hyperbolic plane
   `{0, e, f, e+f}` with `q(e) = q(f) = 0` and `q(e+f) = 1`. The image of `W` is a nonzero vector with `q = 1`, so it is `e+f`.
4. `B(u, w) = q(w) = 1` for `w ∈ W \ W0`, so the image `ū` of `u` satisfies `B(ū, e+f) = 1`. In the plane only `e` and `f` do that. Since `W0` is totally singular and
   `u ∈ W0^perp`, `q(u) = q(ū) = 0`, contradicting `q(u) = 1`. ∎

The exact counts above come from `check.py`, which also finds no saturated subspace of dimension 5..8 by direct enumeration.

**Theorems 2..4 (exhaustive).** Every subspace `X` of `F2^9` of dimension `k <= 4` is enumerated once in reduced echelon form (counts `[9 choose k]_2` = 511, 43435, 788035, 3309747, asserted).
For each `X` the script computes `N(X)` and `N(X^perp)`.

* Dimensions `e >= 5` are covered by `V = X^perp` (`dim V = 9 - k`), so `N_e` for `e = 5..8` is the maximum of `N(X^perp)` over `dim X = 9 - e`. For `e <= 4`, `N_e <= 2^(e-1)` and the saturated spaces of Theorem 1 attain it.
* The pair `(V, V^perp)` at dimension `e` is the pair `(V^perp, V)` at `9 - e`, so Theorem 3 needs only `k <= 4`, and it is the maximum of `N(X) N(X^perp)` over `dim X = k` or `9 - k`.
* A flag level `d <= 4` uses `A = X` and `d >= 5` uses `A = X^perp`. The hyperplanes of `A` are listed by 2^d - 1 functional representatives, and `N(g)` is the number of ports of `A` annihilated by the functional.
  A node is skipped only when an upper bound (`N(g) <= min(N(A), 2^(d-2))` for `d <= 5`, and `N(g) <= N(A)` otherwise) shows it cannot raise a record.

The same program runs both port sets in one pass (about 6 seconds). An independent implementation without the pruning, using all 511 functionals per flag and
checking every node, produced identical tables in about 3.5 minutes.

## Exact checks (`check.py`, `verify.sh`)

From the 104 ports of `research/p104-designer-toolkit-v2/words/5561.json.gz` and P120 rebuilt from coordinates: the quadratic form facts above, all subspace counts,
Theorem 1 counts, `N_e` for both sets, both degree sequences, the star-law tables, and the flag-rectangle tables, each asserted against the stated values.
Marker: `PASS_P104_E8_SUBSPACE_INVARIANTS`.

## Open next questions

1. Is there a closed-form derivation of `N_e = 2^(e-2) + 4` for `4 <= e <= 7` and of the flag masses, from the radical and the restriction of `q` to `V`?
2. Can the lower bounds of 52 (P104) and 60 (P120) on covering the edges by subspace bicliques be raised or attained, using the full list of maximal subspace bicliques rather than only their maxima?
3. Which punctures of P120 (removing two disjoint orthoframes of eight lines) keep `N_e` for `e <= 7` and the star-law values, and is P104 typical among them?

The structured form with first steps and blockers is in `TASK.json`.
