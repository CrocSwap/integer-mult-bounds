# Exact obstruction for the seed-selected orthogonal pencil

## Fixed certificate and pencil

The input is the source-pinned 120-row root/label table from PR #1366. The
checker verifies 120 distinct integer roots of squared norm four, integral
half-Gram entries in `{-1,0,1,2}`, diagonal Gram value two, and all 14,400
label-pair identities

\[
  u_s\cdot u_t = 1 + G_{st}\pmod 2,\qquad G_{st}=\langle L_s,L_t\rangle/2.
\]

Set `e=L_48`. There are 63 indices `j` with `j != 48` and
`<L_48,L_j>=0`. Sorting those source indices and taking index `48 mod 63`
selects `d0=L_91`. The computed inner product is zero.

For each port `s`, define the exact integers

\[
  p_e(s)=\langle L_s,e\rangle,\qquad
  p_d(s)=\langle L_s,d0\rangle.
\]

## Row and total conditions

For target `t` and nonzero sink word `w` in `F_2^9`, let

\[
  Z(t,w)=\{s:u_s\cdot w=1\pmod2\}.
\]

Keep rows with `t in Z(t,w)` and `w != u_t`. A calibrated row has one nonempty
set of rational ratios

\[
  \left\{-p_d(s)/p_e(s): s\in Z(t,w),\ s\ne t,\ p_e(s)\ne0\right\}.
\]

Call its unique value `mu_t`, and require the uncorrected target diagonal
`p_d(t)+mu_t p_e(t)` to be nonzero. The off-target coefficients that the
`d0`-direction total must cancel are

\[
  E(t,w)=\{s\in Z(t,w):s\ne t,\ p_e(s)=0,\ p_d(s)\ne0\}.
\]

For two rows `a=(t_a,w_a)` and `b=(t_b,w_b)`, the single total has source set
`Q=E_a union E_b`. It can be read at both sinks exactly when
`E_a subset Z_b` and `E_b subset Z_a`. The modified row coefficient is

\[
  N_t(s)=p_d(s)+\mu_t p_e(s)-p_d(s)\,\mathbf 1_{s\in Q}.
\]

If `t_a in E_b`, then by definition `p_e(t_a)=0` and `p_d(t_a) != 0`; also
`t_a in Q`. Hence

\[
  N_{t_a}(t_a)=p_d(t_a)+\mu_a\cdot0-p_d(t_a)=0,
\]

which violates the nonzero target-diagonal requirement. The same implication
holds with `a` and `b` exchanged. Thus every available shared-total pair must
avoid both cross-target memberships to be exact.

## Complete finite census

The checker tests all `120 * 511 = 61,320` target/word pairs and uses exact
`Fraction` ratios. It finds:

| Stage | Count |
|---|---:|
| Rows with target in sink support and nonbaseline sink word | 30,600 |
| Rows with one nonempty rational calibrator | 190 |
| Rows whose pre-total target diagonal is nonzero | 65 |
| Distinct-target pairs among those rows | 2,048 |
| Pairs for which the union total is available at both sinks | 1,056 |
| Available pairs with both targets contaminated | 1,024 |
| Available pairs with exactly one target contaminated | 32 |
| Available pairs with no target contaminated | 0 |
| Exact pairs | 0 |

The script checks the source/target equations for every available pair in
addition to the diagonal obstruction. Therefore the negative result is exact
for this finite calibrated one-total family; it is not inferred from sampling.

## Controls and boundaries

The same implementation replays PR #1366's `e=L_51`, `d0=L_1` control: 27
rows, 351 available pairs, all 351 with both target diagonals contaminated.
It also finds the published P112 C.6 positive control (`e=L_0`, `d0=L_76`):
targets 75 and 76, sink words 329 and 438, and a 24-source shared total. The
checker verifies the full 112-by-112 unit and confirms that deleting one
required total source breaks it. A mutated label is rejected by the pairing
identity check.

The result does not cover uncalibrated rows, other total vectors or scalars,
more than one total, another orthogonal pair, rank-nine factorizations, other
punctures, or the full complex supplier. The selected conditional κ remains
unchanged.
