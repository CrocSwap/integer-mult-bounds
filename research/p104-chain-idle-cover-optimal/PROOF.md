# Idle covers, top targets and shape optimality of the chain-nested root

Tags: **[P]** proved below from the stated hypotheses, **[C]** checked exactly by `verify.py` on the literal data of the
retained words, **[A]** an assumption or convention inherited from the cited words, **[X]** not proved here.
The root is the chain-nested root of #6833 (fields `A, f_0..f_{g-1}, h_0..h_{g-1}`, one full site per stage, three thin
queries; `(9|9)` is the priced shape). Its algebra (sign Gram, stage factors, chain merge) is #6833's; this note adds
lower bounds and scope statements about it.

## 0. Conventions

A *full site* `k` has a mask `M_k` of fields, a projector `P_k` onto `K^{M_k}` and a variable `D_k`; the stage factor is
`Δ_k = I + (D_k - 1)P_k`. A *query* is `T_k = I - 2 x_k y_k^T` with constant `x_k, y_k` and `y_k x_k = 0` (square zero). On
full sites `x_k, y_k` are supported in `M_k`. Thin queries have no variable (`Δ_k = I`). The field of scalars `K` has
characteristic not two. The price of one whole idle job on `m` stages is `104 H(8m)` with `H(r) = r^t`, `t = 1 - κ`, and a
`d`-dimensional bank of equal words is `d` jobs [A: #6716 pricing]. The rank of the target of a field whose
monomial involves the variables of the sites in a set `U` is `8 W(U) + 1`, where `W(U)` is the number of stages those
sites carry (`W = |U|` with one stage per site) [A: #6726/#6833 pricing].

## 1. Theorem 1: the idle cover of the chain-nested root costs at least the chain

**Setting.** The root of shape `(g|g)`: left sites `i = 0..g-1` with `M_i = {A, f_0..f_i}`, right sites `m = 0..g-1` with
`M_m = {A, h_m..h_{g-1}}`; one stage per site. Write `d_i = |M_i| - 2`, so `d_i = i` on the left and `d_m = g-1-m` on
the right.

**Hypotheses on a cover.** A *cover* is a finite family of whole idle jobs `ℓ`, each with a set `C_ℓ` of full sites and
price `104 H(8|C_ℓ|)`.

* (C1) At each full site `k`, `P_k = Π_k + Σ_{ℓ: k∈C_ℓ} E_{ℓ,k}`, where `rank Π_k ≤ 2` (the native stage acts through the two
  registers of the local gate) and each `E_{ℓ,k}` has rank at most one. (Commutation with the query, orthogonality
  and idempotence are not needed for the bound; they are needed for the job to be legal.)
* (C2) Each job lies on one side: `C_ℓ` is contained in the left sites or in the right sites.
* (C3) `0 < t ≤ 1`.

**Theorem 1 [P].** Under (C1)-(C3) every cover costs at least `2 · 104 Σ_{s=1}^{g-1} H(8s)`. For `0 < t < 1` equality holds
exactly when the job lengths `|C_ℓ|` are `g-1, g-2, ..., 1` on each side; the chain of #6833 has this form (`g = 9`: lengths
`8,...,1`, per side `Σ H(8s) = 284.4046` at `t = 1 - 0.0033718`). The mask-fixed targets are the same for every cover, so any other
cover with the same masks has a strictly larger paid side and a strictly smaller crossing `κ`.

*Lemma 1.1 (rank count).* Under (C1), site `k` lies in at least `|M_k| - 2` jobs. *Proof.* `rank P_k = |M_k|` and rank is
subadditive: `|M_k| ≤ rank Π_k + Σ_ℓ rank E_{ℓ,k} ≤ 2 + #{ℓ : k∈C_ℓ}`. ∎

*Lemma 1.2 (majorization).* Let a 0-1 matrix have row sums `r_1 ≥ r_2 ≥ ...` and column sums `c_k`, and let `c*_j = #{k : c_k ≥ j}`.
Then `r` is majorized by `c*`. *Proof.* The first `m` rows contain at most `min(c_k, m)` ones in column `k`, so
`Σ_{j≤m} r_j ≤ Σ_k min(c_k, m) = Σ_{j≤m} c*_j`; the totals are equal. ∎

*Lemma 1.3 (Karamata).* If `φ` is concave and `r` is majorized by `s` (same length after padding with zeros) then
`Σ φ(r_j) ≥ Σ φ(s_j)`. *Proof.* Let `a_j` be the slope of the chord of `φ` between `r_j` and `s_j` (the derivative if they
agree). Both endpoints are non-increasing in `j`, so `a_j` is non-increasing, and Abel summation gives
`Σ(φ(s_j) - φ(r_j)) = Σ_j (a_j - a_{j+1}) Σ_{i≤j}(s_i - r_i) ≤ 0`, because the partial sums of `s - r` are non-negative and the
total vanishes. (A common zero tail is removed first.) For strictly concave `φ` equality forces `r = s`. ∎

*Proof of Theorem 1.* Treat one side. Rows are jobs, columns the `g` sites, entries mark membership; (C2) lets each side be
handled alone. By Lemma 1.1 the column sums satisfy `c_k ≥ d_k`, hence `c*_j ≥ d*_j` entrywise, and `d* = (g-1, ..., 1)`. The
price of a job is `φ(|C_ℓ|)` with `φ(m) = 104 H(8m)`, concave, increasing and zero at zero for `0 < t ≤ 1`. By Lemmas 1.2
and 1.3, `Σ_ℓ φ(r_ℓ) ≥ Σ_j φ(c*_j) ≥ Σ_j φ(d*_j) = 104 Σ_{s=1}^{g-1} H(8s)`. Equality for `t < 1`
needs `r = c*` and `c* = d*` (strict concavity and strict monotonicity). ∎

**Exact checks [C].** The literal `CALLER.json` of #6833 has 16 whole idle jobs, no two-role idle, stage sets
`{2..9}, {3..9}, ..., {9}` and `{10}, {10,11}, ..., {10..17}`, each on one side. The number of jobs through each of the
18 sites equals `|M_k| - 2` exactly, and the cost equals the bound at five exponents. `chain_root.verify_root` re-checks the
algebra of the rank-one lines. An exhaustive minimum over all covers (sites interchangeable, state = remaining demand)
equals `Σ H(8s)` for `g = 2..9` at six exponents including `t = 0.99663`; 4,000 random covers satisfy the
majorization chain and the bound.

**What Theorem 1 does not say.**

* Jobs on both sides (violating (C2)) lower the minimum (control: `g = 4`, `t = 1/2`: `16.59` against `2 · 11.73 = 23.45`). For rank-one jobs `φ γ^T` that are idle at a left site `i` (`φ`, `γ` supported in `M_i`, `y_i φ = 0`, `γ x_i = 0`) and, after
  transport through the three thin queries (`φ' = T_3 T_2 T_1 φ`, `γ' = γ (T_3 T_2 T_1)^{-1}`), idle at a right site `m`, no such job exists in
  the literal root: for every pair (left site, right site) of `g = 3, 4, 9`, the space of vectors `φ` idle at the left site
  with `T_3 T_2 T_1 φ` idle at the right site is zero, and so is the dual space [C, exact over `Q`]. Jobs conjugated through
  other sites, non-contiguous jobs or jobs that are not rank-one idempotents are [X].
* A native stage with an active part of rank 3 or more (rank `Π_k > 2`) lowers the demand and the bound (control `demands (0,1,2)`:
  minimum 6.83 below 11.73). Such stages are priced in the native word, not here.
* A convex price (`t > 1`) breaks the bound (control: `t = 1.5`). One stage per site is assumed; with tree children a job
  covering sites of different weights is priced by the total weight, and the Schur step is not carried out for weights.
* The theorem constrains only the paid idle term; every other term of the invoice is held fixed.

## 2. Theorem 2: the largest targets of a shortest root

**Setting H.** `n` fields, `N = n + 1` queries in time order, with `T_k` as in section 0; the full sites `F` have distinct
variables and masks. The product identity holds in the Laurent ring:

`Δ_N T_N Δ_{N-1} T_{N-1} ⋯ Δ_1 T_1 = - Δ_N Δ_{N-1} ⋯ Δ_1`   (J = -I),   (H-id)

so the target of field `f` is `∏_{k: f∈M_k} D_k`. The first and last full sites are `i_0 < i_1`. Constant bases and one
variable per site are built into the setting. Site `k` carries `w_k ≥ 1` stages and `W_tot = Σ_{k∈F} w_k` (`18` for the
chain, the #6726 root with children `(4,4,1,1,4,4)`, and the gate).

**Lemma 3.1 (expansion).** Put `Δ_{<k} = ∏_{h<k} Δ_h`, `x̂_k = Δ_{<k}^{-1} x_k`, `ŷ_k^T = y_k^T Δ_{<k}`,
`Ĝ = Ŷ^T X̂`, `L̂` its strictly lower part. Then the product equals
`Δ_tot (I - 2 X̂ (I + 2L̂)^{-1} Ŷ^T)`. *Proof.* The `Δ` are diagonal and commute; moving each `Δ_k` left through the
earlier `T_h` conjugates `T_k` by `Δ_{<k}`. The standard expansion of a product of `I - 2 x̂ ŷ^T` with `ŷ_k x̂_k = 0` gives the
second factor. ∎

**Lemma 3.2 (rank one).** Under (H-id), `Z = I + 2L̂ - Ĝ` has rank one over `K(D)`. *Proof.* (H-id) says `B := X̂ (I+2L̂)^{-1} Ŷ^T = I_n`.
Then `B X̂ = X̂` gives `X̂ (I+2L̂)^{-1} Z = 0`. `X̂` is `n × N` of rank `n` (since `B = I`), so its kernel is one-dimensional and
`(I+2L̂)^{-1} Z` has rank at most one, hence `Z`. `Z` has unit diagonal, so rank exactly one. ∎

Writing `Z_{kl} = ĝ_{kl}` for `k > l` and `-ĝ_{kl}` for `k < l`: `Z_{kl} Z_{lk} = 1`, `Z_{ik} = Z_{ij} Z_{jk}` for all `i,j,k`
(minors and the cocycle of a rank-one matrix with unit diagonal).

**Lemma 3.3 (all-field).** `Z_{l+1,l} = y_{l+1}^T Δ_l x_l`, which is `D_l · c_l` for a full site `l` (as `Δ_l x_l = D_l x_l`) and a
constant for a thin one, with `c_l ≠ 0`. By the cocycle, `Z_{i_1,i_0} = c ∏_{h∈F, i_0≤h<i_1} D_h`. But
`Z_{i_1,i_0} = Σ_f y_{i_1}(f) x_{i_0}(f) ∏_{h∈[i_0,i_1), f∈M_h} D_h`, a sum of monomials with the field-coefficients of the
`y_{i_1}, x_{i_0}`. Only the monomial `∏_{h<i_1} D_h` may survive, so some field `a` has `a ∈ M_h` for all full `h < i_1`
and `y_{i_1}(a) ≠ 0`, hence `a ∈ M_{i_1}`: **a field lies in every full mask**, and its target is `S ∏_{k∈F} D_k` of rank
`8 W_tot + 1`. ∎

**Lemma 3.4 (residual identity).** Rescale `x_k → s_k x_k`, `y_k → y_k / s_k`; this changes neither `T_k`, the masks nor
the identity, and `s_k = 1/v_k(1)` (with `Z(1) = u v^T`) normalises `Z_{kl}(1) = 1` for all `k,l`: `y_k x_l = +1` for `k > l`
and `-1` for `k < l`. Comparing coefficients of the full monomial in `Z_{kl}(D)` (for `k > l` the monomial
`∏_{h∈[l,k)} D_h`; for `k < l` its inverse) and using that all other monomials vanish: for full sites `k ≠ l`

`Σ_{f : M_f ⊇ [min(k,l), max(k,l)]} y_k(f) x_l(f) = sgn(k - l)`.

(Only fields with `M_f` containing the closed interval of full sites contribute, since `y_k(f) ≠ 0` forces `f ∈ M_k`.) ∎

**Lemma 3.5 (three sites).** Let `a` be a field in all masks and put `b_k = y_k(a)`, `a_k = x_k(a)`. If for three full sites
`i < l < m` all six ordered pairs have zero residual (the identity of Lemma 3.4 is satisfied by `a` alone, `b_k a_l = sgn(k-l)`),
then `b_i a_l = b_i a_m = -1`, `b_m a_l = b_m a_i = 1`, `b_l a_i = 1`, `b_l a_m = -1`. The first pair gives `a_l = a_m`, the second `a_l = a_i`, and
then the last two give `1 = b_l a_i = b_l a_m = -1`, impossible in characteristic not two. ∎

**Theorem 2 [P].** Under H, with `W_tot` as above:

1. Some field lies in every full mask (Lemma 3.3).
2. If two or more fields do, two targets have rank `8 W_tot + 1`.
3. If exactly one field `a` does, there are two further distinct fields `f_1, f_2` with `W(M_{f_1}) + W(M_{f_2}) ≥ W_tot`,
   so their target ranks sum to at least `8 W_tot + 2`.
4. In both cases, with `n ≥ 3`, the three largest target ranks sum to at least `16 W_tot + 3`: `291` for `W_tot = 18`, and
   the multiset `{145, 73, 73}` attains it. In particular no root under H has its all-field target replaced by two
   entries of total rank `145`.

*Proof of 3.* The pair `(i_1, i_0)` (either order) has zero residual: a second field in `M_f ⊇ [i_0, i_1]` would lie in every
mask. Take a full site `l` strictly between. By Lemma 3.5 applied to `(i_0, l, i_1)` one of the pairs `(i_0, l), (l, i_0), (l, i_1),
(i_1, l)` has nonzero residual: a field `f ≠ a` with `M_f ⊇ [i_0, l]` or `M_f ⊇ [l, i_1]`. Let `P` be the set of middle sites
covered on the prefix side (down-closed) and `S` those on the suffix side (up-closed). Every middle site is in `P ∪ S`.
Let `p = max P` (or `i_0` if `P` is empty) and `s = min S` (or `i_1`), so `s` is at most the successor of `p` and the prefix
`[i_0, p]` and suffix `[s, i_1]` together carry weight at least `W_tot`. If `P` is empty, `a` is in `M_{i_0}`, and
`y_{i_0} x_{i_0} = 0` with `b_{i_0} a_{i_0} ≠ 0` (from the zero residual of `(i_0,i_1)` and `(i_1,i_0)`) forces another field
`g ≠ a` in `M_{i_0}`; likewise for `S`. The prefix field and the suffix field are distinct: one field covering both would
contain every full mask. With no middle site (`|F| = 2`) the same two end fields work. ∎
*Proof of 4.* Case 2 gives two entries `8 W_tot + 1` and a third rank `≥ 1`. Case 3 gives `(8W_tot + 1) + (8 W(M_{f_1}) + 1) + (8 W(M_{f_2}) + 1) ≥ 16 W_tot + 3`.
For the chain, `A` has 18 sites (`145`), `f_0` the nine left sites and `h_{g-1}` the nine right sites (`73` each). ∎

**Exact checks [C].**

* Chain `(9|9)`: (H-id) at three random rational `D`; `Z_{kl} Z_{lk} = 1` and the cocycle on all `21^3` triples at a random `D`;
  `Z_{i_1,i_0}` equals the product of all `D` except the last; the residual identity of Lemma 3.4 for all `18 · 17` ordered
  pairs; field `A` is the only field in all masks; target ranks `145, 73, 73, 65, 65, ...`; each of the 16 middle sites has a
  non-`A` field covering a prefix or a suffix.
* #6726 root (children `(4,4,1,1,4,4)`): (H-id) at random `D` for the nine literal queries with their masks; unique all-field;
  ranks `{145, 73, 73, 41, 41, 41, 41, 1}`; each of the four middle sites has a prefix or suffix field.
* Lemma 3.5: no solution on a grid of rational values; with one right-hand sign flipped the same grid has solutions.
* Controls: one changed query vector breaks (H-id); one sign of `Z` changed breaks `Z_{kl} Z_{lk} = 1`.

**Scope.** `J = -I` only (for other involutions the active block of the extension argument is not treated); exactly `n + 1`
queries; constant ordinary bases; one variable per site (tree children enter only through the weights `w_k`, a pricing
convention); a root equal to `-Δ_tot` as a polynomial identity (checked at random points on the literal roots, proved for the
chain family in #6833). The theorem fixes the *sum* of the three largest ranks; other splits with `m_1 + m_2 = W_tot` (such as
`81 + 65`) are not excluded by this argument. The count of queries `n + 1` is #6832's identity for square-zero queries; it is used
here as part of H and not re-proved.

## 3. Proposition 3: retirement on the chain family and #6726's witnesses

All of this is finite and [C]; the general statement is [X].

* **Masks.** #6726's root has masks of sizes `(2,4,4,4,4,2)` on six sites with children `(4,4,1,1,4,4)`. Its two published retirements release
  the stage block of site 1 from field 6 and the stage block of site 4 from field 4 (read from the literal witnesses:
  prefix stage sets `{5,6,7,8}` and `{10}`, and the targets of fields 6 and 4 before retirement). Removing field 6 from the mask of site 1
  and field 4 from the mask of site 4 gives masks of sizes `(2,3,4,4,3,2)` that are, up to a relabelling of the eight fields,
  exactly the masks of the chain gate `(4,4,1|1,4,4)`. Removing the same fields at other sites does not.
* **Invoice.** The outer histograms of the literal #6726 final caller equal those of the gate word plus the cancelling pair
  `{T_{32}: 2, P_{32}: 2}`; the unretired caller has two targets of rank `41` where the gate has two of rank `9`.
* **Census.** With the pure dual-pair census of #6827 (every non-ordinary cut, every equal-target class, every unit job of the
  forms that occur), the literal chain `(9|9)` word of #6833 has no retirement candidate and no rank-without-unit gap; the
  same census on the unretired #6726 caller finds its three known cuts (158, 383, 392).

**Not proved.** That every retirement of every shortest root is the reduction of one mask is not proved here. The
finite statements say that the two witnessed retirements are mask reductions and that the chain word carries no further
retirement under the criterion's hypotheses (equal-target classes with block-diagonal endpoint, unit jobs of the stated forms).

## 4. Proposition 4: the shape `(9|9)` among chain-nested roots

**Family.** Child sizes `s_L = (s_1, ..., s_{g_L})` (outer to centre) and `s_R` (centre to outer), total `N = Σ s`. A child of size
`s` is a binary tree of `s` leaves; each inner node on `m` leaves adds two targets of rank `8m+1`, two paid jobs of rank `8m` and one
query of rank 1. Fields: `A` (target `8N+1`), `f_i` (target `8 Σ_{j≥i} s_j + 1`, with a paid idle of rank `8 Σ_{j≥i} s_j` for `i ≥ 1`), the mirror for `h`,
an empty field when the field count is odd, and two or three thin queries by parity. The native word is the retained one, called `N` times.
The ledger `F(κ) = Σ (T_r - P_r) r^{1-κ}` has the weights of the cited pricing (104 per outer job, 1 per native item).
For the binary word the ranks are `7m, 7m+1` and the weight is 111.

**Proposition 4 [C].**

1. The ledger formula equals the literal event histograms of the built words at `(4,4,1|1,4,4)`, `(3,2|5,1,1)`, `(2,3,1,1|7)` and `(9|9)`
   and the literal `CALLER.json`, and equals the family formula of #6833 on 60 random shapes.
2. Complex histogram, `N = 18` (the stage count of the retained native word): `κ_0 = 0.00337180047549672` is the crossing of the literal `(9|9)` word.
   An exhaustive search over all `2^17` compositions of every side total, with the best binary tree for each child (checked against explicit
   enumeration of all trees up to 7 leaves), finds `(9|9)` as the unique maximum with `F(κ_0) = 0`; the runner-up `(8|10)` has `F = -0.343`,
   a first-order loss of `1.5e-6` in `κ`; every other shape is below `-0.1`.
3. Binary histogram (the retained binary native word, audited from its program): the `(9|9)` crossing lies in `(0.0038525393934, 0.0038525393935)`,
   `(9|9)` is again the unique maximum, runner-up `(8|10)` at `-0.371` (first-order loss `1.9e-6`).
4. A dynamic program of the same ledger over `N = 10..40` with the native histogram scaled by `N` (a model, not a literal word) has its
   maximum at `N = 18` for both histograms.

**Hypotheses and scope.** The family is the additive ledger above; non-balanced trees and shapes other than the four built ones
are priced by the formula and not built. Only `N = 18` uses a literal native word. Everything outside the family (cross-side idle merging,
fields with support on both sides, other coupling) is [X]. This is a statement about the invoice of the family, not a κ claim.

## 5. Status of the statements

| Statement | Result |
|---|---|
| Idle cover cost `≥ Σ_{s=1}^{8} 2H(8s)`, equality for the chain | Proved (Theorem 1) under (C1)-(C3); one-sided jobs and active rank two are hypotheses, with controls |
| Top targets `{145,73,73}` | Proved as: an all-field exists, and the three largest ranks sum to at least `16W+3 = 291`; attained, but the split `73+73` itself is not forced |
| Retirement equals mask reduction | Checked on the chain word and #6726's two witnesses; the general statement is not proved |
| `(9|9)` best on complex and binary histograms | Exact for the family at `N = 18`, with a scaled-native model for other `N` |

Inputs are copies of the pull-request files listed in `retained/SOURCE-PINS.json`; no κ changes, and the five framework assumptions of the cited
words are not discharged.
