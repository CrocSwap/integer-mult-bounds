# Annihilator : the ANNIHILATOR lemma of delivery D3 in Lean

`Nov15/Annihilator.lean`, Lean 4.33.0-rc1 + Mathlib, kernel only: no `sorry`, no `native_decide`; all theorems print
`[propext, Classical.choice, Quot.sound]`. Builds in 6 s / 2.0 GB.

## Model
V finite-dimensional over a field K. A `Lineage`: charts c 0 ... c n (subspaces of V); step i is PUBLIC (c i <= c (i+1)) or an OWNED MOVE that is NESTED
(either direction: WholeFloorNest / LAT.md). `ownRank` = sum over owned steps of the descent dim (c i) - dim (c (i+1)) (truncated), i.e. the
"descending owned rank". A `Delivery`: ports a with functionals phi a (the f_a = (. u_a)), support vectors u b all lying in the START chart,
and for each port a a leaf chart c (leafIdx a) of the lineage on which phi a vanishes.

## Theorems
* `modular_le`, `step_bound`: for a nested step C -> D, dim K(D) <= dim (K(C) meet K(D)) + (dim C - dim D)^+, where K(c) = span(phi) meet Ann(c).
* `run_bound`: the running sum N_m of all K(c_j), j <= m, has dim N_m <= dim K(c_0) + (owned descents so far). (Plain "dim K(c) grows by <= descent" is not
  enough since K shrinks again on ascents; it is the cumulative sum N that carries the induction.)
* **`annihilator`**: rank of the Gram block [phi a (u b)] <= `ownRank`. Proof: Phi = span phi lies in N_n (every port has a leaf), so dim Phi <= dim K(c_0) + ownRank;
  and rank Gram = dim (E Phi) = dim Phi - dim(Phi meet ker E) <= dim Phi - dim K(c_0) (K(c_0) lies in ker E since u b in c_0).
* `identity_block_rank`, **`sparse_serves_le`**: if the Gram block over ports P has an identity sub-block (orthonormal group), then |P| <= ownRank,
  for any number of hops. `total_sparse_le`: lineages are disjoint in MOVEs (each MOVE carries one vector), so the ports served by identity-block entries total
  at most the word's descending owned rank R (hypothesis: sum of the lineages' ranks <= R; R = 56 on S22 is Theorem K + [C d3p], not in this file).

## Paper statement vs Lean
D3 sec. 1 is TRUE as written under these readings, with two points made explicit:
1. "K(start) = 0 / dim F_w >= Gram rank" holds after restricting the functionals to the start chart; in Lean this appears as
   dim Phi - dim K(c_0) >= rank Gram, and the final bound is the same inequality, rank Gram <= sum of descents.
2. The NESTING of owned MOVEs is NECESSARY. `lateral_counterexample` (V = Q^2, ch0 = span e0, ch1 = span e1, equal dim, incomparable): a lateral owned MOVE
   ch0 -> ch1 pays owned descending rank 0, the functional coord0 vanishes on ch1 and has coord0(e0) = 1 (Gram block [1] of rank 1), so rank Gram = 1 > 0 = ownRank.
   So the lemma, like the whole-floor bound (WholeFloor.md sec. 3-4), depends on the verifier's proper-nesting rule (local.py:66, LAT.md).
Also stated by the card but not formalised: that an orthonormal group NEEDS an identity block (a design requirement; here the identity block is the hypothesis),
and the count 56 / the 9-dimensionality of dense entries (F2^9 structure).
