# Lemmas used by the draft (both are NEW and are the review points)

Setting: #442's complex word (#433's split-centre R560 word, m = 73, nine stages) with the idle-axis hosting of #442.
Notation: frames are subspaces of F2^9; T_U = canonical_frame(9, U) (clifford_exact.py); T_FULL is the full Fourier
transform; a helper normally climbs ∅ → … → FULL and its residual has width 9.

## 0. What is not claimed
The entrance lines used here are all of EVEN weight, i.e. totally isotropic for the F2 dot product (14 distinct rank-1
lines in the kernel word; 16 frames of rank 1, 2 and 4 in the combined word). The bit-style criterion of #440
(`validate_isometries`: an orthonormal basis whose first e rows span E, i.e. coordinate entrances) is therefore NOT met:
no orthogonal matrix of O(9,2) sends an isotropic E to coordinate axes. `code/iso1.py` shows that, restricted to
entrances that do meet it, the kernel potential and the number of gauge-eligible helpers are both 0. #442's shipped
complex audit asserts `w == 9` for hosted residuals (`idle-axis-hosting/audit.py:92`), and #433's emit asserts
`c['start'][r]==0` for compensated registers (`complex_emit.py:55`). No shipped complex word has a nonzero helper
entrance. Everything below is therefore CONDITIONAL on Lemma A and Lemma G.

## Lemma A (entrance adapter) — review point 1
Let E ⊆ F2^9, e = dim E, w = 9 − e, and Φ_E = T_E^† T_FULL (the chain ∅ → E removed from the helper's climb).
(i) Φ_E = R_E (C_[w] ⊗ I) L_E with R_E, L_E explicit Gaussian monomials (address permutation, quadratic phase, X
translation), exactly, including the global phase. This is `lower_child` applied to Φ_E: it asserts rank w,
`compiled.tab == Φ_E.tab` and `compiled.zero_state() == Φ_E.zero_state()`.
(ii) Claim (assumed, not proved): a helper that starts at frame E and ends at FULL, with its compensation moved off
the zero frame (kernel: absorbed by donors; gauge: Lemma G), acts on its residual stream as the exact coordinate
factor P_g C_[w] P_g^-1 that hosting lemma (a) of #442 uses, where the monomials R_E, L_E are rank-zero local gates like
the endpoint adapters of #425. Its residual block has width w; the e remaining local coordinates carry arbitrary
dirt and are transformed by Φ_E like any other dirt coordinate, which the arbitrary-dirt restoration identity
(replayed exactly on all 800 columns) tolerates.
Evidence: `code/nec4.py` — all 16 entrance frames of `gauge80-kernel42` pass (i); `code/nec3.py` shows the tableaux:
for coordinate frames Φ_E fixes every X_i, for the isotropic and odd-weight non-coordinate frames it does not, i.e.
the monomials are genuinely non-orthogonal GL(9,2) address maps. Part (ii) is where a reviewer must look: it is the
statement that the bank block of width w plus a non-orthogonal monomial adapter is an admissible residual route.

## Lemma K (shared-donor kernel, port of #417/#435/#434)
A pivot p with exact response relation col(p) = Σ q_d col(d) over donors d, entrance E ⊆ first frame of p and of every
donor, starts at frame E; each donor receives `d += -q_d p` at frame E before the main word (inverse after the
cleanup at the full frame); the compensation columns of pivots are dropped. Exactness is the arbitrary-dirt replay
(donor update is part of the replayed word); frames are checked by the chain assertion. Same statement as in #440,
with rational coefficients (all denominators are powers of two, as required by `primitive_bound`).

## Lemma G (entrance gauge, nonzero-frame compensation and centre scatter) — review point 2
For a helper j with entrance E_j (a member of a nested family) its compensation `y_t += c_tj x_j` is executed at
frame E_j instead of frame 0, as the first gates of the main word; the helper starts at E_j and every target t in its
response support climbs ∅ → L_t, L_t = the largest E_j with t in the support of j.
Constraints (all checked): (a) E_j ⊆ first frame of j and ⊆ the first main frame of every target in its support;
(b) the entrances touching one target are pairwise nested; (c) for every centre k, the levels L_t of the targets it
scatters into form a chain whose top lies inside the centre frame c_k. The centre scatter then runs as: copy at c_k;
lower stepwise c_k → (served levels, descending) → lowest served level; scatter into the targets of level L at frame L;
clear at the lowest level (reversed in the transposed orientation). The total lowering rank equals the baseline 8
whenever some served target has level ∅, so the rank deficit stays 2496.
Claim (assumed): a scalar add at frame E between a helper at E and a target raised to E, and the centre scatter at
frame L between a copy lowered only to L and a target at L, are the same operators as the zero-frame versions up to the
common exterior window (the common-frame lemma of #425, extended from frame 0 to frame L).
Evidence: audit (exact arbitrary-dirt and inverse-transpose replay of the full program including the gauge gates),
emit (literal scalar replay of both orientations on 800 columns, centre lifetimes, `paid` equals the audit profile),
exact Gaussian recipes for every used transition (2,940 edges for the gauge word).

## Mutation controls (to be added in the full package)
Not yet run: omit the donor update, flip a gauge coefficient sign, move an entrance out of the first frame, break a
centre chain. `audit_cxg.py` already rejects frame-chain violations by assertion.
