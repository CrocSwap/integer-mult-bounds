# Masked root-star copy-cost floor on P112: covering bound and complete trimmed-star census

Every finite fact cited as **(Fk)** is checked by `verify.py` with exact integer and F2
arithmetic. The rest is written argument. This is a scoped obstruction and a complete
finite census for one support family; it is not a theorem about all decoders.

## 1. Model and the masked identity

This is CrocSwap/integer-mult-bounds#717's B14 decoder model in its masked (E-graph) form, exactly as stated in D1(a)
of [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717) (DreamingOfClouds). The
120 E8 root lines carry labels `u_i` in F2^9 with pairing `S9(u_i,u_j) = (<r_i,r_j> + 1) mod 2`.
P112 is the 120 lines minus the 8 coordinate frame lines. A decoder is a list of terms
`(d_k, t_k)` with `sum_k d_k t_k^T = 2G` required **only on the E-graph** (the 6720 pairs of
even inner product, the diagonal included): `x_i . y_j = 0` off-diagonal and `x_i . y_i = 4`.
The 5824 odd entries of `2G` are all nonzero, so they are fixed afterwards at zero cost by
singleton terms `(c e_i, e_j)` on odd pairs, whose label pairing rank is 0 **(F1)**. Term k
costs `beta_k`, the F2 rank of the label pairing between its row and column supports, and
`cst = sum_k beta_k`. The coordinate stars `d_k = t_k = (<r_i, f_k>)_i` over the eight frame
lines satisfy `sum_k <r_i,f_k><r_j,f_k> = 2<r_i,r_j>` on every entry and cost 8 per term,
`cst = 64` **(F2)**; they are trimmed root-star atoms of the census below.

## 2. The covering lemma (frame substitution)

A **frame** is an 8-clique of the E-graph; there are exactly 1260 of them in P112 and no
9-clique **(F3)**, and every line lies in exactly 90 frames **(F4)**. Restricting the masked
identity to a frame F gives `[x_i . y_j] = 4 I_8`, a full-rank 8x8 system. Each term
contributes the block `(d_k|_F)(t_k|_F)^T`, of rank at most one, and contributes nothing
unless its row and column supports both meet F. Hence **at least 8 terms meet every frame**.
A beta-0 atom can never meet a frame: both supports inside a frame would force an
even-paired pair inside `R x A`, contradicting pairing rank 0 **(F5)**.

Let `h_k` be the number of frames term k meets and let `gamma` be the minimum of
`beta/hit` over the allowed atoms. Then

    cst = sum_k beta_k >= gamma * sum_k h_k >= gamma * 8 * 1260 = 10080 * gamma.

For the class of all supports this recovers the weakness of CrocSwap/integer-mult-bounds#717 D1(e) (sampled there at
`8/rho` about 43.8). The point here is that for a **finite** family `gamma` is exact.

## 3. The census (root-star family)

For each of the 120 root lines `alpha` the root-star supports on P112 are
`C(alpha) = {i : <r_i, alpha> != 0}` and `N(alpha) = C(alpha)` minus alpha's own line when
that line is live (for the 8 frame normals the self-line is punctured, so both coincide).
The label span of `N(alpha)` is `H_alpha = u_alpha^perp` (dimension 8), so an odd root pair
`(<alpha,beta> odd)` gives pairing rank `8 - [<alpha,beta> odd] = 7` — the mixed-beta atoms
that CrocSwap/integer-mult-bounds#717 D1(b)'s flat-support census excludes (its supports are complements of hyperplane
flats with all pairwise span pairings of rank at least 8; a trimmed star is not of that form).

The census enumerates all 240 supports and all 57,600 ordered support pairs **(F6)**:

| beta | atoms |
|---|---:|
| 7 | 7,616 |
| 8 | 37,440 |
| 9 | 12,544 |

with exact pairing ranks and exact frame-hit counts (frames met on both sides):

- `max(hit/beta) = 1170/7`, attained at beta-7 atoms such as `(N(f), N(beta))` with
  `f` a frame normal and `<f,beta>` odd; every beta-7 atom hits at most 1170 of the 1260
  frames **(F7)**. The eight best atoms are recorded in `RESULTS.json`.
- The bound over the whole family is `10080 * 7/1170 = 784/13`, about **60.31** **(F8)**.
- Restricting to atoms of pairing rank at least 8, `gamma = 8/1260` and the bound is
  **exactly 64** **(F9)**, attained by the coordinate stars of section 1.

## 4. What this establishes, and what it does not

1. **Mixed-beta trimmed stars are not excluded by the covering argument.** The task card's
   hoped-for condition (every beta-7 atom hits at most `7/8` of the frames, which would have
   forced the bound to 64) is **false**: atoms of pairing rank 7 hit 1170 frames
   (the falsifying instance; threshold was 1102). The complete covering bound for the
   root-star family is `784/13`, so an assembly of beta-7 trimmed stars at total cost 63 or
   64 is not contradicted by frame counting alone.
2. **All the slack lives in the 7,616 trimmed odd-pair atoms.** Any root-star decoder whose
   terms all have pairing rank at least 8 costs at least 64 for any number of terms, with
   the coordinate stars attaining it. This extends the star floor from the eight-term
   all-pairs statements of [PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968)
   and CrocSwap/integer-mult-bounds#717 D1(b)/(c) to arbitrary term counts under the masked identity, inside this family.
3. **The remaining question for the family is an assembly problem** in the exact window
   `[784/13, 64]`: can nine or more of the beta-7 atoms (the recorded leads hit 1170 of the
   1260 frames each) be combined so that every frame is met by at least 8 terms whose
   restricted blocks sum to `4 I_8`? Frame counting cannot answer this; a solver or an
   algebraic obstruction would. This package does not attempt that assembly.

No cost below 64 is claimed or constructed. No supplier, word, or kappa change is claimed.
The favourable-cost accounting of the task card (one cst unit is +2.81% of `b` on the
selected T37 profile per CrocSwap/integer-mult-bounds#717 P1, and any complex-side change is capped by the CrocSwap/integer-mult-bounds#589 bit
supplier at kappa 0.001730427469823602) is unchanged: nothing here lowers cst, so the paid
recursive moment does not move. Realization charges that a future construction would owe
(centre reads, frame legality, dirty restoration; CrocSwap/integer-mult-bounds#717 recorded unpaired-centre parity
costs and negative net buildability for its P104/P111 hits) are **not** checked here.

## 5. Scope

- **Covered.** The masked E-graph identity on P112; terms with support pairs from the 240
  root-star supports (untrimmed `C(alpha)` and self-trimmed `N(alpha)`, 120 normals);
  arbitrary real coefficients and arbitrary sign patterns (the covering bound depends only
  on supports); any number of terms.
- **Not covered.** Supports trimmed by more than the self-line, unions of stars, non-star
  supports (CrocSwap/integer-mult-bounds#717 D3's cost-63 P111 and cost-56 P104 decoders are non-star), general
  supports (where D1(e)'s 43.8 applies), punctures other than P112, and any assembly or
  coefficient search. The eight-term all-pairs results of CrocSwap/integer-mult-bounds#968 and CrocSwap/integer-mult-bounds#1077 are unchanged;
  the eight-term masked case is closed concurrently by
  [PR1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212) and
  [PR1213](https://github.com/CrocSwap/integer-mult-bounds/pull/1213), and one-sided
  root-linear masked factors at arbitrary term count by
  [PR1191](https://github.com/CrocSwap/integer-mult-bounds/pull/1191); those routes do not
  reach the trimmed, non-root-linear star atoms censused here.
- **Not a formal proof.** Finite replay supports the written argument; no proof assistant
  or independent human review is claimed. A finite census is not an impossibility theorem
  outside the stated family.

Prepared by **Navinor** with help from opencode. Apache-2.0.
