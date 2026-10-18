# Exact scope and diagonal obstruction

## Fixed data

The pinned E8 construction supplies 120 integer line representatives `L_s` with norm 4 and Gram entries

\[
G_{st}=\langle L_s,L_t\rangle/2\in\{-1,0,1,2\}.
\]

The 9-bit labels `u_s` satisfy `u_s·u_t = 1+G_st (mod 2)`. `certificate.tsv` records the 120 roots and labels; `verify.py` independently checks every root norm, Gram parity, and one of the 14,400 label pairings. The seed-selected pencil is `e=L_51`, `d0=L_1`; the verifier confirms that `L_1` is the first of the 56 odd-pairing partners of `L_51`.

For each source line define the exact integers

\[
p_e(s)=\langle L_s,e\rangle,\qquad p_d(s)=\langle L_s,d_0\rangle.
\]

## One-row domain

A row candidate consists of a target `t` and a sink label `w` in the 511 nonzero vectors of `F_2^9`. Its paired-source set is

\[
Z(t,w)=\{s:u_s\cdot w=1\}.
\]

Retain a row only when `t∈Z`, `w != u_t`, and every off-target `s∈Z` with `p_e(s) != 0` forces the same rational value

\[
\mu=-p_d(s)/p_e(s).
\]

At least one such calibrating source is required. The row's uncorrected decoder coefficient is `p_d(s)+mu p_e(s)`. A source in `Z` with `p_e(s)=0` and `p_d(s) != 0` therefore has to be included in the extra total to zero that coefficient. The required set for row `(t,w)` is

\[
E(t,w)=\{s\in Z(t,w):s\ne t,\ p_e(s)=0,\ p_d(s)\ne0\}.
\]

Retain the row only if its target diagonal `p_d(t)+mu p_e(t)` is nonzero before adding the shared total. These definitions give a finite, exact rational replay; no floating-point comparison is used.

The verifier considers `120×511=61,320` target/label pairs. It finds 30,600 rows satisfying the sink-label and nonbaseline conditions, 63 with one consistent nonempty calibrator value, and 27 with nonzero diagonal.

## Two rows and one shared total

Take two retained rows `(t_a,w_a)` and `(t_b,w_b)` with distinct targets. The least required source set for one total serving both is

\[
Q=E(t_a,w_a)\cup E(t_b,w_b).
\]

For that total to be read by both sinks, every source required by either row must be paired at both sinks: `E_a ⊆ Z_b` and `E_b ⊆ Z_a`. The union total changes a relaxed row coefficient to

\[
N_t(s)=p_d(s)+\mu_t p_e(s)-p_d(s)\,\mathbf 1_{s\in Q}.
\]

The verifier enumerates all 351 distinct-target pairs of the 27 retained rows. All 351 satisfy shared-total source availability. In every pair, both cross-memberships hold: `t_a∈E_b` and `t_b∈E_a`. By the definition of `E_b`, the first membership gives `p_e(t_a)=0` and `p_d(t_a)\ne0`. Since `t_a∈Q`, its relaxed diagonal becomes

\[
N_{t_a}(t_a)=p_d(t_a)+\mu_a\,0-p_d(t_a)=0.
\]

The sink has unit diagonal pairing because `t_a∈Z_a`, but exact decoding requires a nonzero decoder diagonal. The same argument applies to `t_b`. Thus every pair fails exactness at both relaxed diagonals, and no exact pair exists in this searched family.

## Positive control, negative controls, and limits

On the established P112 pencil `e=L_0`, `d0=L_76`, the same calibrated-row and shared-total search recovers targets 75 and 76, sinks 329 and 438, and a shared set of 24 sources. The verifier checks the complete 112-by-112 rational decoder/pairing condition for that witness. This control shows that the row and pair predicates retain the known construction.

The certificate-integrity controls mutate one root coordinate and one label bit and confirm that the norm/Gram or pairing checks reject each mutation.

The negative conclusion is limited to this fixed P120 pencil, nonbaseline sink labels with at least one forced rational calibrator, two distinct relaxed targets, and the union shared-total rule. It is not an impossibility theorem for uncalibrated rows, other pencils, other correction mechanisms, or complete suppliers, and it supplies no cost recurrence or new `kappa`.
