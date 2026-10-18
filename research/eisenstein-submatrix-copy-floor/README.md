# Eisenstein E8 decoder copy floor: 23, past the clique-method limit

**Research note; no new supplier, no κ change, selected record untouched.**
In the abstract Eisenstein E8 scalar binary decoder model of
[`research/eisenstein-clique-copy-bound`](../eisenstein-clique-copy-bound/PROOF.md)
(Jonathan Lam, PR798), every fitting decomposition costs **at least 23**
Eisenstein pairing-rank units. PR798 proved 22 and showed that *no* weighting
of cliques can prove more. This package adds the ingredient that its PROOF.md
says is needed: rank bounds on non-clique principal submatrices.

```sh
python3 -B research/eisenstein-submatrix-copy-floor/verify.py
```

Expected (about 35 s, standard library only, any CPython 3.10+):

```text
PASS_EISENSTEIN_SUBMATRIX_COPY_FLOOR: C >= 23; objective 30200/1367; 296321 flat pairs; 540 S_uw sets minrank 10; 5 controls; no new kappa
```

The geometry (40 K-lines, orthogonality, all 772 flats, pairing ranks, all
cliques) is imported unchanged from PR798's pinned `geometry.py`.

## Model (PR798, unchanged)

`B` is a 40×40 matrix over F2 with `B_tt = 1` and `B_ts = 0` for distinct
nonorthogonal lines; entries on orthogonal pairs are free in both directions.
A decomposition `B = Σ_j 1_Rj 1_Aj^T` costs `C = Σ_j c(R_j, A_j)`, with
`c(R,A) = rank_Q(V_R V_A^T)/2`. `N[x]` is `x` plus its 27 nonorthogonal lines.

## Proof

**Lemma 1 (zero-cost totals can be dropped).** If `c(R,A) = 0` then
`X_R ⊥ X_A`, so every `(t,s) ∈ R×A` is an orthogonal pair of distinct lines
(the form is positive definite): a free entry. Deleting all zero-cost totals
leaves a fitting matrix `B'` and the same cost.

**Lemma 2 (submatrix rank).** For a line set `S` let `m(S)` be the least F2
rank of `B[S,S]` over all fitting `B`. For `B'` from Lemma 1,
`m(S) ≤ rank B'[S,S] ≤ #{j : c_j ≥ 1, R_j meets S, A_j meets S}`. Hence any
weights `λ_S ≥ 0` with

    Σ_S λ_S [F meets S][G meets S] ≤ c(F,G)   for all flats F, G with c(F,G) ≥ 1   (★)

prove `C ≥ Σ_S λ_S m(S)`. Closure keeps `c` and can only add hits, so flats
suffice, exactly as in PR798. Cliques (`m(Q) = |Q|`) are PR798's method.
Asymmetric row/column sets add nothing. Define `m(P,Q)` as the least rank
of `B[P,Q]` over fitting `B`. Every entry of `B[P,Q]` outside `(P∩Q)²` is off
the diagonal, so it is zero or free; setting the free ones to zero gives
`m(P,Q) = m(P∩Q)`, while the hit count for `(P,Q)` is at least that for `P∩Q`.

**The new sets.** For distinct nonorthogonal `u, w`, let `S_uw = N[u] ∩ N[w]`
(20 lines; 540 sets). `u` and `w` are nonorthogonal to every line of `S_uw`, so
`B[S_uw,S_uw] = I_2 ⊕ B[core]` with an 18-line core, and `m(S_uw) = 2 + m(core)`.

**Lemma 3 (m(core) = 8).** The core's largest clique `Q` has 5 lines. Any
factorization `B = U V^T` with 7 columns can be normalized to
`U[Q] = V[Q] = [I_5 | 0]` (since `U[Q] V[Q]^T = I_5`, transform by an invertible
`M` with `U[Q] M = [I_5|0]`, then by `[[I,0],[W^T,I]]` to clear the rest of
`V[Q]`). Then each other line `v` has `U[v] = (B[v,Q], s_v)`,
`V[v] = (B[Q,v]^T, t_v)` with `s_v, t_v ∈ F2²`, and every remaining entry is
`B[v,Q]·B[Q,w] + s_v·t_w`. The verifier enumerates all fixed-entry-respecting
choices by exhaustive backtracking and finds none: no fitting completion of
rank ≤ 7. A rank-8 completion exists and is rebuilt and rank-checked. So
`m(S_uw) = 10`. The greedy clique bound gives only 5 + 2 = 7, and the
chromatic (orthogonal-frame) bound gives 10: F2 cancellation does not help here.

**Symmetry.** Five pinned permutations (`AUTOMORPHISMS.json`) preserve the
nonorthogonality graph and generate a group transitive on all 540
nonorthogonal pairs (checked by orbit closure). An automorphism maps the fitting
pattern to itself and `S_uw` to `S_(gu)(gw)`, so the exhaustive search runs once.

**Certificate.** Weights `184/6835` on each singleton, `13/13670` on each of
the 2,880 seven-cliques and `7/20505` on each `S_uw` satisfy (★) on all
296,321 flat pairs with positive cost (601 tight), checked in exact
arithmetic. The objective is

    40·184/6835 + 2880·7·13/13670 + 540·10·7/20505 = 30200/1367 ≈ 22.0922.

Costs are integers, so **C ≥ 23**.

## Why this works, and how far it goes

Under PR798's optimal clique dual (1/24 on the 240 pairs of twelve-line flats
with `c = 2`, 1/2 on full/full), a set `S` is "priced" at
`1/2 + e/24`, where `e` counts orthogonal pairs `(x,y)` with `S` meeting both
`x^⊥` and `y^⊥`. A set can lift the bound only if `m(S)` exceeds its price.
`S_uw` is priced at 9.5 and has `m = 10`; the whole pattern is priced at 10.5
with minrank 10.

Exploration (not part of the replay): we enumerated the 858,299 sets
`S = ⋂_{a∈A} N[a]` that are maximal for their hit pattern (every set has the
same price as such a set and at most its minrank), grouped them into 78
classes by (|A|, |S|, price), computed one minrank per class by SAT with the
Lemma 3 normalization, and solved the class-uniform LP. Only the `S_uw` class
violates the clique dual, and the LP optimum is again 30200/1367. If those
classes are orbits of the graph's automorphism group (not checked), then
30200/1367 would be the exact optimum of the whole principal-submatrix method,
and pushing past 23 would need yet another ingredient. This is conditional.

## Consequences and scope

- The abstract optimum moves from [22,40] to **[23,40]**. PR1794's necessary
  window for a beating Eisenstein supplier (C ≤ 31, ≤ 29 at the best window)
  shrinks to 23..31. PR798's conditional Dfc three-stage window (C = 22..26)
  becomes 23..26. Neither route is closed.
- Same model and premises as PR798: whole K-lines, scalar binary totals, the
  stated fitting pattern, and PR446's pairing-rank premise for any physical
  reading. Nonlinear messages (the separate `eisenstein-message-copy-bound`
  package) and sub-line operations are not covered.
- This is a written proof with exhaustive finite premises, checked by a stdlib
  replay; no proof assistant and no independent human review.

## Open next questions

1. **Is 30200/1367 the exact limit of principal-submatrix certificates?**
   Why: it tells the next prover whether more set families can help. First
   step: verify that the 78 classes are automorphism orbits (or give per-class
   rank witnesses) and exhibit the dual. Blocker: none; about one session.
2. **A cost-aware ingredient.** The Gaussian planar theorem
   (`gaussian-e8-asymmetric-copy`) charges a total by how its support's rank
   deficit relates to support size. Adapting that idea to the 12-line Eisenstein
   hyperplanes (the tight dual pairs here) might lift the bound further. First step:
   restrict to decompositions whose totals have K-rank-≤3 joint support.
   Blocker: the Eisenstein planes have up to four lines, so the matching
   argument changes.
3. **Upper side.** No decoder cheaper than 40 is known. A SAT/ILP search over
   non-clean supports at cost ≤ 31 would test PR1794's remaining window directly.

## Credit

Model, geometry, clique certificate and the method-limit theorem: Jonathan Lam
(@jonathanlam), PR798, with PR620's archived geometry (Joel Pulikkan /
GamingPuzzled). Weighted-clique method: Douglas R. Colkitt (PR703) and Sagar
Thakrar (PR738). Window and prize screen: Maximooch (PR1794). The pointer to
this target: DreamingOfClouds' note in discussion 1167. New material: Josie
Elliston, prepared with Claude Opus 5.5 (Anthropic) via Claude Code, which did
the search, proof and verifier. Apache-2.0.
