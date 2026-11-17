# Nov15/PadLift.lean 
Formalises R64 PAD-LIFT (internal notes) in the AUDIT64 form: lifting of the U-INDEPENDENT rank bound plus involution (not "kills at U"). Kernel-only: no sorry, no native_decide; 10 `#print axioms` all [propext, Classical.choice, Quot.sound]. 9 s / 2.1 GB (imports Nov15.SpecRankP + Mathlib sub-imports).

## Proved (g' on index alpha, pad on index beta, |beta| = 2k, g = padG g' = fromBlocks g' 0 0 (-1))
- `rank_blockdiag`: rank(diag(A, D)) = rank A + rank D (Mathlib had no such lemma).
- (1) `pad_rank` [char != 2]: rank(1 - padG g') = rank(1 - g') + |beta|.
- (2) `pad_sq` [any char]: padG g' * padG g' = 1 <-> g' * g' = 1.
- (3) `lift_kill` [char != 2]: "r <= rank(1-g'), equality => g'^2 = 1" gives "r + |beta| <= rank(1-g), equality => g^2 = 1". `lift_budget`: with rank(1-g) <= U, r + 2k <= U, and U = r + 2k => g^2 = 1 (so the lifted kill needs U >= r + 2k, equality case involutive).
- Realisation level (the "pads dark" step): `job_dark`/`jobs_dark`: a product of jobs 1 - x y^T with x, y zero on the pad registers (x = Sum.elim x' 0) equals lift1 J' = diag(J', I_pad); `g_blockdiag`: with D = diag(D', -I), J = diag(J', I), J' invertible, D J^-1 = padG (D' J'^-1).
- Corollary (dimension-free): `rank_ge_dim` = SpecRankP.rank_ge in RB1 coordinates with Fin m S-coordinates for ANY m: m <= rank(Delta - P) (same hypotheses as rank_ge_four, which is m = 4); `rank_ge_pad`: m = 2k + 2 gives 2k + 2 <= rank(Delta - P). (SpecRankP.rank_ge already had dim S arbitrary; this is the matrix form.)

## Paper statement check
- TRUE as written provided char != 2 (the paper's standing hypothesis; R66 lists it). Counterexample otherwise: `pad_rank_char2_fails` (ZMod 2, g' = 1 on Unit, one pad register: -I = I so rank(1-g) = 0 != 0 + 1). Part (2) and the block form need no characteristic assumption.
- NOT formalised (hypotheses, as in the paper): that TS forces x, y to vanish on the pads (R42 TS, tight-set support) and D = -1 on pads at unit characters (F2); the individual kills (SPLIT/INV/LB) that supply the base bound for g'. PAD-LIFT is exactly "given those, the lift is formal": the Lean theorems take dark pads as the shape of g, J, D.
- Scope note per AUDIT64: the lift transfers bound + involution for each tight-covered profile at every k; it does not itself say "dead at U"; `lift_budget` shows the form: dead for U < r + 2k, involutive at U = r + 2k.
