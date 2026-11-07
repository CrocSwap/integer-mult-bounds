# No subset of 97 or more E8 lines has a rank-8k complex realisation (no κ)

**No new κ.** This package proves that, under a stated label pattern, no set of 97 or more of the 120 E8 lines has a realisation of inner
dimension exactly `8k`, over any field. The obstruction is the 14-port Hall deficiency of #6846 in a 13-line form, and the minimum number of
lines that meets every such configuration is exactly 24.

## Statement

**Hypothesis (complex label pattern; the one of #6846).** Let `S` be a set of the 120 E8 lines (one line per pair `±r` of roots). Each `T` in
`S` carries a pair of `k × d` matrices `U_T, W_T` over a field `F` (`k >= 1`), and the pairing `B_ST = W_S U_T^T` (`k × k`) satisfies

* `B_ST = 0` for every pair `S != T` that is **non-orthogonal** (the "forced-zero" pairs: `|<r_S, r_T>| = 1` for roots of norm 2);
* `B_TT` invertible for every `T`.

`W != U` is allowed. The pattern is an assumption about how the pairing of labels is constrained at frame contacts; it is not proved here
for any word.

**Theorem.** If `|S| >= 97` there is no realisation of inner dimension `d = 8k`, over any field, for any `k >= 1`.
Equivalently: every set of 97 lines contains one of `F13`, 1,209,600 specific 13-line sets, each of which is Hall-deficient; and the minimum
hitting set of `F13` has exactly 24 lines (so 96 lines can avoid `F13`, and nothing is claimed about them).

**Scope.** Subsets of the 120 E8 lines with this mask only. Ranks `8k < d < 9k` (`k >= 2`), other masks, line systems that are not subsets
of the 120 lines, and any pricing are not covered. No claim is made for sets of at most 96 lines.

## The 13-line obstruction

The forced-zero graph `NO` on the 120 lines (adjacent = non-orthogonal) is strongly regular with parameters `(120, 56, 28, 24)`; its
clique number is 8 and it has 8,640 8-cliques. For a 8-clique `K` and a line `t` outside it, let `A(t)` be the members of `K` orthogonal
to `t` (not forced zero to `t`). Exactly one line has `A(t) = {a, b}` for each pair `{a, b}` that occurs. Take `C` a 4-subset of `K`
and `O` the five lines whose `A(t)` are five of the six pairs inside `C` (a K4 minus an edge). The 13-line set `K ∪ O` is a witness;
`F13` is the family of all of them. Two lines of `O` that share a coordinate of `C` are forced zero and share exactly that one coordinate.

**Hall deficiency (the argument of #6846 with six lines on five coordinates replaced by five lines on four).** Suppose `K ∪ O ⊆ S` has a
realisation with `d = 8k`.

1. *Gauge.* `K` is a forced-zero clique, so `B_KK` is block diagonal with invertible blocks and has rank `8k`; as `B_KK = W_K U_K^T` with both
   factors `8k × 8k`, both are invertible. Replacing `U` by `U g`, `W` by `W h` with `g = U_K^{-1}`, `h = g^{-T}` leaves the pairing unchanged and gives `U_K = I`, `W_K = B_KK`;
   multiplying each block row of `W_K` on the left by `B_kk^{-1}` keeps every zero block and every invertible diagonal block, so `U_K = W_K = I`.
2. *Support.* `B_{kT} = U_T[k]^T` and `B_{Tk} = W_T[k]`, so a forced-zero pair `(T, k)` gives `U_T[k] = W_T[k] = 0`; both are supported on `A(T)`.
3. *Block diagonal products.* Fix `c` in `C` and `O_c = {T in O : c in A(T)}`. Two distinct members of `O_c` are forced zero and share only `c`, so
   `W_S[c] U_T[c]^T = 0`. The stacks `X = (W_T[c])` and `Y = (U_T[c])` over `O_c` give a block-diagonal `X Y^T` of rank at most `k`, so
   `sum_{T in O_c} rank(W_T[c] U_T[c]^T) <= k`.
4. *Rank sum.* `B_TT = sum_{c in A(T)} W_T[c] U_T[c]^T` is invertible, so `sum_c rank(W_T[c] U_T[c]^T) >= k`. Summing over the five lines of `O`:
   `5k <= sum_{c in C} sum_{T in O_c} rank(...) <= 4k`. Contradiction.

For `k = 1` this is pigeonhole: five lines each need a coordinate where both entries are non-zero, no coordinate serves two of them, and `C` has four.
In the Hall (fractional matching) form the demand per line is `lam <= 4/5 < 1`.

## Every 97-line set contains a witness

Let `D` be a set of lines meeting every member of `F13`, and suppose `|D| <= 23`.

1. **Spectral inequality (exact).** With `A` the adjacency matrix of `NO`, `A^2 = 32 I + 4 A + 24 J`, so `M = 2A + 8I - J` satisfies
   `M^2 = 24 M` (checked entrywise). Hence `u^T M u = |Mu|^2 / 24 >= 0` for every vector `u`. For the indicator of any `k`-set `D`, `u^T A u = 2 e(D)`, so
   `4 e(D) + 8k - k^2 >= 0`, i.e. `e(D) >= (k^2 - 8k)/4` for every `k`-set (not only for sets that hit anything). For `k = 23`: `e(D) >= 87`.
2. **Local lemma (SAT, DRAT).** Fix a line `x`, write `N(x)` for its 56 forced-zero neighbours. *There is no set `D` with `x` not in `D`, meeting
   `w \ {x}` for every `w` in `F13` containing `x`, with `|D| <= 23` and `|D ∩ N(x)| <= 11`.* For `x = 0` this is a CNF with 998 variables and
   136,295 clauses (`retained/local-lemma.drat.xz` is a DRAT proof of its unsatisfiability; `check.py` regenerates the CNF and pins both by sha256).
   Nine reflections in E8 roots preserve `NO`, hence the family `F13`, which is defined from `NO` alone, and move line 0 to every line, so the lemma
   holds at every `x`. (The same instance was also solved directly at every one of the 120 lines, with no symmetry, and is unsatisfiable at each.)
3. **Count.** Enlarge `D` to exactly 23 lines and let `S` be its 97 complement lines. By step 2 each `x` in `S` has `|N(x) ∩ D| >= 12`. Counting
   `NO`-edges between `S` and `D` two ways:
   `97 * 12 = 1164 <= sum_{x in S} |N(x) ∩ D| = sum_{d in D} (56 - deg_D(d)) = 56*23 - 2 e(D) <= 1288 - 174 = 1114`. Contradiction.

So every hitting set of `F13` has at least 24 lines. **Tightness.** The 24-line set printed in `check.py` (the nonsingular points of the perpendicular of a
totally singular 2-space of `E8/2E8`) meets every witness, has `e = 96 = (24^2 - 8*24)/4`, and sees exactly 12 of its lines from every outside line, so the minimum is exactly 24 and the
theorem is sharp for this family.

## What `check.py` verifies (about one minute, standard library)

* the 120 lines from coordinates; `NO` is SRG(120,56,28,24); `M^2 = 24 M`;
* all 1,209,600 witnesses, each instance passing the Hall-deficiency test (five lines supported on four coordinates, sharing pairs forced zero with one common coordinate); the family sha256;
* `k = 1` exhaustive search over `F_2` and `F_3` on sampled witnesses (the gauge-fixed system has no solution) and a control with one `O` line removed (solvable);
* the nine reflections preserve `NO` and have a transitive orbit on line 0;
* the local CNF at line 0 regenerated and compared with its sha256; the proof file compared with its sha256;
* `97*12 > 56*23 - 2*87`; the 24-line set meets all witnesses and has 96 internal edges.

`./verify.sh --drat` additionally decompresses the proof and runs `drat-trim` (not part of the standard library; set `DRAT_TRIM` or put it on `PATH`); it reports `s VERIFIED`.
The CNF is satisfiable if either bound is relaxed (`|D| <= 23` with `|D ∩ N(0)| <= 14`, or `|D| <= 24` with `|D ∩ N(0)| <= 12`), so the bounds are not vacuous.

## Open next questions

1. **Sets of 96 lines.** Is there a rank-`8k` realisation of some 96-line set that avoids `F13`, for instance the complement of the 24-line extremal set? A realisation would make 96 sharp for realisability; a further obstruction would lower it.
2. **Ranks strictly between `8k` and `9k`** (`k >= 2`). The gauge needs `d = 8k`; with a free extra column the rank sum may or may not close.
3. **Break a forced zero.** Which mechanism forces the pairing to vanish on non-orthogonal pairs, and can a contact be routed through a paid helper so that one forced zero inside every `F13` witness is broken?

See `TASK.json` for first steps and blockers. Credit: DreamingOfClouds.
