# Independent check of #4628's block-5 and block-6 bounds (2.99172, 2.97290, 2.9447)

No new κ. Nothing here is about integer multiplication. This is an independent check of one hand-argued claim of
open PR #4628 (Jacob Alan Sussman, head `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`):

> m ≥ 4: at least 2.9447 calls per array (2.99172 at m = 5, 2.97290 at m = 6), engine game, argued by hand
> (two AI reviewers reproduced the numbers).

PROOF.md §7 of #4628 says only "The block-4 hook is carried upward through projections between the frame graphs of
the engine, controlled by a coupling argument", and refers to the author's repository for the argument.

## Result

| Item | Verdict | How |
|---|---|---|
| Projection counts N_r(s) | **correct** | own derivation (section 3); brute force over **all** 15, 135 and 2,295 Lagrangians at m = 2, 3, 4 and every nonzero p, plus 60 sampled Lagrangians at m = 5 |
| T_5 = 834241/278850 = 2.991720, T_6 = 1188222/399685 = 2.972896 | **reproduced exactly** | own recursion in exact fractions |
| ≥ 2.9447 for every m ≥ 4 | **reproduced** | exact for m = 4..60 (minimum 2.944709234, decreasing in m); for m ≥ 60 by a monotone coupling whose transition inequalities I prove for every k (section 4; the author's `tail.py` checks them for k ≤ 80 only), c* = 2.944709234 |
| Soundness of the recursion | **a sound route exists** (my reconstruction, argued by hand, section 2) | induced representations over the nonzero Paulis plus Bruhat transitivity for the engine's frame group |
| Inputs | **the numbers rest on two block-4 values that nobody re-checked**: a_3 ≥ 68,320 (enters T_5) and a_2 ≥ 48,576 (enters T_6) | section 5 |

Gaps found, none of which refutes the claim:

1. **The written argument is not public.** #4628 says "The programs and the written argument are in my repository".
   At commit `86e575e2` of jacobalansussman/wht-power-saving-lean only the programs and their outputs are public
   (`research/block-bounds-and-new-rules/programs/engine-bounds-blocks-5-and-6/`). The proof they cite ("PROOF.md,
   Theorem 3", "Lemma 1(c)", "Lemma 2", "Theorems 4 and 5") is in the folder `proofs/induction/` of a private archive
   (that repository's `block-bounds-and-new-rules/README.md`, Sources). So the hand argument cannot be read by
   reviewers. Section 2 gives an independent route.
2. **Two inputs come from one program.** T_5 = (N_5(4)·a_4 + N_5(3)·a_3)/(N_5,1(1)·a_1) uses the block-4 hook values
   a_1 = 27,456 (cap, proved in Lean), a_4 ≥ 86,592 (demand, determinant certificate, C author evidence) and
   **a_3 ≥ 68,320**; T_6 also uses **a_2 ≥ 48,576**. The last two are mod-p rank lower bounds printed by the author's
   `hookG.py` (`data/block4-hook/out_rank2_blocks.txt`). Mod-p rank is the safe direction, but no certificate is
   stored, and #4628's `verify.py` does not check them. The author's README calls the three-move value "computed
   modulo a prime but not certified" (that remark is about using it as an upper bound; here it is used as a lower
   bound). With only the triangle bounds a_2 ≥ a_4 − 2a_1 = 31,680 and a_3 ≥ a_4 − a_1 = 59,136 the route gives
   T_5 ≥ 2.83219, T_6 ≥ 2.77245, T_60 ≥ 2.70821.
3. **The tail was checked numerically only up to k = 80.** The coupling needs two inequalities at every block k.
   They hold for all k (section 4), so this gap is closed here.
4. **Status of the soundness step.** My reconstruction in section 2 is argued by hand, like the original. It is
   independent: I did not see the author's proof.

Bearing on the open shapes: with T_5 and T_6 and the bound W + m (not checked here), the smallest shapes left open are
2 in 7 and 3 in 9 at block 5, and 2 in 8 and 3 in 9 at block 6. These match #4628's table. 3 in 9 needs more than
3 calls per array. This route cannot give that: its limit is 2.94471, and it falls with m. Excluded by T_m alone:
3 in 8 and 4 in 11 at blocks 5 and 6, 5 in 14 at block 6, and W in 3W − 1 for W ≤ 120 (block 5) and W ≤ 36 (block 6).
All of these match #4628.

## 1. The claim, in the form checked

Frames are Lagrangian subspaces of F_2^(2m), the symplectic space of the m-qubit Paulis. The engine's free letters
are shifts (X Paulis), invertible XOR-linear address maps, and phases i^(z·x + c). Conjugating S-phases by address
maps gives CZ. Together these generate every Pauli and every Clifford that fixes the Z-frame L_0. Their image in
Sp(2m, 2) is the whole Siegel parabolic P = {[[A, B], [0, A^(-T)]]}. A call C_v = (1+i)/2·I + (1−i)/2·X_v is √X_v,
a Clifford at frame distance 1 from L_0, and the target C^(⊗m) is at distance m.
For a subspace N kept by every free letter, raise(f g f′) = raise(g) for free f, f′. So the double cosets P\Sp/P,
which are the distances d = m − dim(L_0 ∩ gL_0), make raise a function a_d of the distance alone (with a_0 = 0).
The brute-force count confirms that every Lagrangian at the same distance gives the same projection counts.

The recursion (author's `induct.py`, re-implemented here) is a^(m)_r = Σ_s N^(m)_r(s)·a^(m−1)_s. Here N^(m)_r(s)
is the number of nonzero p ∈ F_2^(2m) for which the reductions π_p L = (L ∩ p^⊥) + ⟨p⟩ of a distance-r pair have
distance s in p^⊥/⟨p⟩. The bound at block m is T_m = a^(m)_m / a^(m)_1, by Theorem R (#4628 PROOF.md §1).

## 2. Why the recursion is a valid lower bound (independent reconstruction; argued by hand)

Let N′ be a block-(m−1) certificate kept by the block-(m−1) frame group, with profile a′. The steps:

- **Copies of N′ for each p.** For each nonzero p, pick a Clifford h_p with h_p p = z_1 and h_p(π_p L_0) = L_0.
  This is possible because the stabiliser of z_1 acts transitively on the Lagrangians containing z_1. Let U_p be
  the sum of the two eigenspaces of P taken in all f columns at once (V_+(P)^(⊗f) ⊕ V_−(P)^(⊗f)). Put the copy
  N_p = h_p^(−1)(N′ ⊗ both Z_1-eigenspaces) inside U_p; the X_1 Pauli identifies the two eigenspaces.
- **The new space.** Set U = ⊕_p U_p. A Clifford g maps U_p to U_(gp), and the eigenvalue signs cancel because all
  f columns carry the same sign. U is a representation of the finite group G generated by the letters.
- **The program identity holds on U.** A program right at every width f ≥ 1 is an identity in C[G]. Burnside–Brauer
  (faithful V, the Vandermonde argument run with exponents n ≥ 1) puts every irreducible of G into some V^(⊗f) with
  f ≥ 1. So Theorem R applies on U, with any linear (complex) mixing.
- **Free letters keep N = ⊕_p N_p.** For a free b, the map h_(bp)·b·h_p^(−1) fixes z_1 and L_0. Its reduction is
  therefore a block-(m−1) free element, which keeps N′.
- **Raise splits over p.** raise_U(g) = Σ_q raise_(N′)(h_q g h_(g⁻¹q)^(−1)). The reduced map sends the standard
  frame to h_q(π_q gL_0). Its distance from the standard frame h_q(π_q L_0) is d(π_q L_0, π_q gL_0). So raise_U(g)
  = Σ_q a′_(d(π_q L_0, π_q gL_0)), which is the recursion, up to a uniform factor 2 that cancels in T_m.

In which direction each input is needed: the cap at block m is N_1(1)·a′_1 and needs a′_1 as an upper bound, with
a′_0 = 0. The demands need a′_(m−1) and a′_(m−2) as lower bounds. The optional triangle step a_r ≥ a_m − (m−r)·a_1
is valid (raise is subadditive) and changes nothing here. The checks agree: with and without it the tops are
identical.

This route uses the frame group of the engine (Lagrangians, the Siegel parabolic). As #4628 says, it does not carry
over to the widened game (Toffoli is not Clifford).

## 3. The projection counts (own derivation)

Let L, M be at distance r, so I = L ∩ M has dim m − r and L + M = I^⊥. The cases for p:

| p | number of such p | reduced distance s |
|---|---|---|
| in I | 2^(m−r) − 1 | r |
| outside L + M | 4^m − 2^(m+r) | r (π_pL ∩ π_pM = (I ∩ p^⊥) + p) |
| in exactly one of L, M | 2(2^m − 2^(m−r)) | r − 1 (the intersection is I + p) |
| p = l + m′ (l ∈ L∖I, m′ ∈ M∖I), ω(l, m′) = 1 | (2^r − 1)·2^(r−1)·2^(m−r) | r − 1 |
| same, ω(l, m′) = 0 | (2^r − 1)(2^(r−1) − 1)·2^(m−r) | r − 2 (l also lies in the intersection) |

ω(l, m′) is well defined modulo I. The pairing L/I × M/I → F_2 is nondegenerate, which gives the split
(2^r − 1)·2^(r−1) against (2^r − 1)(2^(r−1) − 1). This is the author's closed form. `verify.py` confirms it against
brute force.

## 4. The tail for m > 60 (independent proof of the coupling inequalities)

Write j = k − r for the deficit. A random p moves block k to block k − 1, and the deficit
- goes up with probability p_up = N_r(r−2)/(4^k − 1) = (2^r − 1)(2^(r−1) − 1)·2^j/(4^k − 1);
- goes down with probability p_down = N_r(r)/(4^k − 1) = (2^j − 1 + 4^k − 2^(2k−j))/(4^k − 1).

R^(k)_r = a^(k)_r/a^(k)_1 = (1/q_k)·E[R^(k−1)_s] with q_k = N_1(1)/(4^k − 1) ≤ 1. Hence
T_m ≥ E[R^(60)_(60 − J)], where J is the deficit at block 60.

- **Up-probability.** The numerator equals 2^(2k−j−1) − 3·2^(k−1) + 2^j ≤ 2^(2k−j−1) − 2^k. This is less than
  2^(−(j+1))·(4^k − 1), so p_up ≤ 2^(−(j+1)).
- **Down-probability.** p_down ≥ 1 − 2^(−j) is equivalent to 2^j ≥ 2^(−j). Once r = 0 the chain only goes down.
- **The dominating chain.** It moves up with probability 2^(−(j+1)) and down with probability 1 − 2^(−j). It is
  monotone, since Q_up(j) + Q_down(j+1) = 1, and its stationary law is π*(j) ∝ Π_(i≤j) 1/(2^i − 1).
- **Comparison.** Started at deficit 0, J ≤_st π*. The block-60 profile is nondecreasing in r (checked), so T_m ≥
  Σ_j π*(j)·R^(60)_(60−j). The tail of the normaliser is bounded by 2w_J with J = 80 (w_(j+1)/w_j ≤ 1/3). This gives
  c* = 2.944709234 > 2.9447, the same constant as the author's.

## 5. Inputs, and what each number rests on

| input (block-4 hook, k = 8, f = 9) | used in | status |
|---|---|---|
| a_1 = 27,456 (cap) | all | proved in Lean (`hook_cap`), as an upper bound |
| a_4 ≥ 86,592 (demand) | all | 5,412 × 5,412 minor, C checker (author evidence in #4628; about an hour) |
| a_3 ≥ 68,320 | T_5 and later | mod-p rank in the author's `hookG.py`; no stored certificate; not re-checked by #4628 |
| a_2 ≥ 48,576 | T_6 and later | as above. The README of #4628 also cites 48,576 as a certified **upper** bound (two calls in a row); the induction needs it as a **lower** bound, which is again only the mod-p rank |

## Reproduce

```sh
python3.12 -B research/projection-recursion-check/verify.py       # PASS_PROJECTION_RECURSION_CHECK, about 35 s, stdlib
python3 scripts/research_package.py --package research/projection-recursion-check --check-only
python3.12 scripts/research_package.py --package research/projection-recursion-check
```

`verify.py` imports nothing from #4628 or from the author's repository. Ten controls must be rejected, and are:

- a closed form with one count moved;
- T_5 and T_6 off by one in the denominator;
- a_3 + 1 reproducing T_5;
- two weakened dominating chains;
- 3 in 9 at block 6 claimed excluded;
- 3 in 8 at block 5 claimed allowed;
- 2.99172 claimed from the triangle inputs alone;
- a nonmonotone profile.

## NOT covered

- The block-4 hook values themselves. I did not recompute a_2, a_3 or a_4 (dimension 102,960), or the Lean proofs
  of the cap.
- The author's private written proof. Section 2 is my own reconstruction; it is argued by hand, and no person has
  checked it.
- The other claims of #4628: W + m and 2W, one array, no-phase block 3, the widened-game keptness, and section 7.
  The shapes above use W + m as stated in #4628.
- Whether #288's or Harvey's models lie inside the engine game.

## Open next questions

See `open_questions` in [TASK.json](TASK.json):

1. Certify a_3 ≥ 68,320 and a_2 ≥ 48,576 with a stored minor and a separate checker.
2. Write section 2 as a full proof, or in Lean.
3. Exclude 3 in 9 at block 5 or 6. That needs a certificate above 3 calls per array, which this route cannot give.

## Sources (pins in SOURCES.json; external files by sha256)

- #4628 at head `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`: `research/complex-small-m-lower-bounds/README.md`
  (table of section 1, section 6) and `PROOF.md` §7.
- jacobalansussman/wht-power-saving-lean at `86e575e28ed94890872dcff1bb2621d7ff559cbd`, read only to locate the
  claim and its inputs; no code reused. Files under `research/block-bounds-and-new-rules/`:
  - `README.md`, sha256 `47c99107…54f50a`;
  - `data/engine-bounds-blocks-5-and-6/out_induct.txt`, `e4cf4402…bb4072`;
  - `data/engine-bounds-blocks-5-and-6/out_tail.txt`, `9861aa2c…778c2b`;
  - `programs/engine-bounds-blocks-5-and-6/induct.py`, `dabe7190…2c428c`;
  - `programs/engine-bounds-blocks-5-and-6/nrs_closed.py`, `54ba1ab4…71eeb`;
  - `programs/engine-bounds-blocks-5-and-6/tail.py`, `2ac28e4c…12e717d5d4`;
  - `data/block4-hook/out_rank2_blocks.txt` (the a_2, a_3 values).

## Credit

The claim, the projection recursion, the block-4 hook and its numbers are Jacob Alan Sussman's (#4628 and his
repository, written with AI agents). The certificate method (Theorem R / the FO lemma) is eumemic's (#288), with
Swapnil Jain's P1/P2 as cited there. The engine and cost model are OpenAI's.

Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
