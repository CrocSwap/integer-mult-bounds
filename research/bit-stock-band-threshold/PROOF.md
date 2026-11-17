# Proof: the six-bit window of the selected BIT stage's stock fit closes

Scoped written proof with exact finite checks. No new kappa, supplier admission or
frontier change. Every claim concerns the **source reserve prescription** of the
delayed-cover BIT producer at the one ordinary-BIT stage that PR #4954 analyses. It
says nothing about other implementations of that supplier.

## 0. Setting, hypotheses and what is cited

The stage has rank `N = 2^H1` with `H1 = 25986965159937` and atom exponent `1/250`
(pinned in `research/query-thinned-controllers/RESULT.json`). For an integer width
`e >= 1` the source prescription (DELAYED-COVER-BRIDGE section 8,
`BIT-ALLSIZE-PARAMETERS.json` `stock`) is

    w   = ceil(e^(1/250)),           n = ceil(e/w),        D = floor(log_N n),
    cG  = ceil(log_q(B*|GL_N(F_q)|)),
    k   = D*(N^2*(w-1) + cG) + k_old,        k_old = ceil(log_q S_old) + 1,

with `q` an odd prime and `B >= 1` an integer. It borrows `k` high digits and **fits**
exactly when `k < e/2`, that is `2k < e`. Write `k_par = D*(N^2*(w-1) + cG)`,
`c_B = ceil(log_q B)`, `t = log2 e` and `A = 250`.

Two hypotheses are used on the fit side only.

* **(HB)** `c_B <= N^2`. This is the hypothesis of #4954. The open PR #7101 derives
  `c_B <= 2^(H1+13) <= N^2` from the inherited nested-width bound. That derivation is
  cited and not replayed here.
* **(Hold)** `k_old <= N^2`. PR #4970 shows `S_old = 1`, so `k_old = 1`, and gives
  the conservative fallback `k_old <= 103`. Both readings satisfy (Hold). Neither is
  re-derived here.

The infeasibility statements need none of these: only `B >= 1`, `q >= 3` and
`k_old >= 0`.

Constants, all exact rationals:

    t*  = 250*(2*H1 + 2)/249 = 500*(H1 + 1)/249 = 52182660963730.923694779116465863...
    t** = 250*(2*H1 + 3)/249 = t* + 250/249       = 52182660963731.927710843373493975...
    tau = 2^(-2*10^11).

## 1. Lemma 1 (chart envelope; PR #4954 Lemma 1)

For every `N >= 1`, odd prime `q` and `B >= 1`: `N^2 <= cG <= N^2 + c_B`.

*Proof.* `|GL_N(F_q)| = q^(N^2) * prod_{j=1..N}(1 - q^(-j))`. The product is below
one and at least `1 - 1/(q-1) >= 1/2 > 1/q`, so `q^(N^2-1) < |GL| < q^(N^2)`. Then
`B*|GL| > q^(N^2-1)` gives `cG >= N^2`, and `B <= q^(c_B)` gives
`B*|GL| < q^(N^2+c_B)`, so `cG <= N^2 + c_B`. QED

Write `delta_B = cG - N^2`, so `0 <= delta_B <= c_B`.

## 2. Lemma 2 (exact criterion at depth two; new)

If `D = 2`, that is `N^2 <= n < N^3`, then `k = 2*N^2*w + 2*delta_B + k_old` and

    the prescription fits   if and only if   e > 4*N^2*w + 4*delta_B + 2*k_old.

Hence:

* **(a)** if `e <= 4*N^2*w`, it does not fit, for every `B`, `q` and `S_old`;
* **(b)** under (HB) and (Hold), if `e > 4*N^2*w + 6*N^2`, it fits.

*Proof.* `k = 2*(N^2*(w-1) + N^2 + delta_B) + k_old`, so `2k = 4*N^2*w + 4*delta_B
+ 2*k_old`, and `2k < e` is the displayed inequality. For (a), `2k >= 4*N^2*w >= e`.
For (b), `4*delta_B + 2*k_old <= 4*N^2 + 2*N^2`. QED

## 3. Lemma 3 (other depths; PR #4954 Lemma 2)

* **(a)** If `D = 1` it does not fit, for every `B`, `q`, `S_old`. Here `n <= N^2 - 1`,
  so `e <= n*w < N^2*w <= k_par`.
* **(b)** If `D >= 3`, `N >= 64`, (HB) and (Hold), it fits, with `k_par < e/4`.

*Proof of (b).* `N^(D-2) >= 64^(D-2) >= 8*D + 1` for `D >= 3` (true at `D = 3`, and
`64*(8D+1) >= 8(D+1) + 1` gives the step), so `n >= N^D >= 8*D*N^2 + 1`. Then
`e > (n-1)*w >= 8*D*N^2*w`. By Lemma 1 and (HB), `k_par <= D*(N^2*w + N^2) <=
2*D*N^2*w`, so `4*k_par < e`. Also `e > 8*D*N^2 >= 24*N^2` gives `k_old <= N^2 < e/4`.
Hence `k < e/2`. QED

## 4. Lemma 4 (from `log2 e` to integer comparisons; new)

Let `e` be an integer width with `t/250 >= 2*10^11 + 3`, and put `rho = e^(-1/250) =
2^(-t/250)`. By definition `e^(1/250) <= w < e^(1/250) + 1 = e^(1/250)*(1 + rho)`. Write
`u = e^(249/250)/(4*N^2) = 2^(249*(t - t*)/250)`, which uses `249*t*/250 = 2*H1 + 2`.

* **(a)** If `t <= t*`, then `e <= 4*N^2*w`.
* **(b)** If `t >= t* + tau`, then `e > 4*N^2*w + 6*N^2`.
* **(c)** If `t >= t*`, then `n >= 2*N^2`, so `D >= 2`.
* **(d)** If `t <= t**`, then `e <= 8*N^2*w`. If `t >= t** + tau`, then
  `8*N^2*w + 8*N^2 < e`.
* **(e)** For `e = 2^t` with integer `t`, `D >= k` if `249*t - 250*k*H1 >= 1`, and
  `D < k` if `249*t - 250*k*H1 <= -1`.

*Proof.* (a) `u <= 1` gives `e^(249/250) <= 4*N^2`, so `e <= 4*N^2*e^(1/250) <=
4*N^2*w`.

(b) Since `w < e^(1/250) + 1`, `4*N^2*w + 6*N^2 < 4*N^2*e^(1/250) + 10*N^2`. This is at
most `e` when `e^(249/250) >= 4*N^2 + 10*N^2*rho`, that is when `u >= 1 + 2.5*rho`
(multiply by `e^(1/250)` and use `e^(1/250)*rho = 1`). Now `t >= t* + tau` gives `u >=
2^(249*tau/250) >= 1 + 0.69*tau`, using `2^x >= 1 + x*ln 2`. The number `t*/250` is at
least `2*10^11 + 3`, so `4*rho <= 2^(-2*10^11 - 1) <= tau`. Hence `0.69*tau >= 2.5*rho`.

(c) `n >= e/w >= e^(249/250)/(1 + rho) >= 4*N^2/2`.

(d) The same two steps with `8*N^2` for `4*N^2`: `e^(249/250) <= 8*N^2` gives `e <=
8*N^2*w`; and `8*N^2*(w + 1) < 8*N^2*e^(1/250) + 16*N^2 <= e` when `u' >= 1 + 2*rho`
for `u' = e^(249/250)/(8*N^2)`, which `t >= t** + tau` gives as above.

(e) `e/w <= n <= e/w + 1`, with `e^(249/250)/(1 + rho) <= e/w <= e^(249/250)`. If
`249*t - 250*k*H1 >= 1` then `e^(249/250) >= N^k*2^(1/250)`, so `n >= N^k*2^(1/250)/(1 + rho)
>= N^k`. If it is at most `-1` then `n <= N^k*2^(-1/250) + 1 < N^k`, because `N^k >= 370`.
QED

## 5. Theorem (the window closes)

For the selected `N`, `A = 250`:

* **(T1)** Every integer width `e` with `D >= 1` and `log2 e <= t*` fails to fit, for
  every `B >= 1`, odd prime `q` and `S_old >= 1`, and for every larger admissible depth.
* **(T2)** Under (HB) and (Hold), every integer width with `log2 e >= t* + tau` fits.
* **(T3)** Consequently the least width `e_fit` such that every width `e >= e_fit` fits
  satisfies `t* < log2 e_fit <= t* + 2*tau`. The window left by #4954 had `log2 e` between
  `52182660963729` and `52182660963735`; it now has width at most `2*2^(-2*10^11)` around
  `t* = 500*(H1 + 1)/249 = 52182660963730.9236947791...`, independent of `B` and of
  `S_old` within (HB) and (Hold).
* **(T4)** For widths `e = 2^t` with integer `t`: every `t` from `26091330481865`
  (the first with depth at least one; #4954 states `...866` conservatively) through `52182660963730` does not fit, and every
  `t >= 52182660963731` fits under (HB) and (Hold).
* **(T5)** The sufficient guard `k_par < e/4` that #4954 used fails for `D >= 1` and
  `log2 e <= t**` and holds for `log2 e >= t** + tau` under (HB); at integer `t` the
  threshold is `52182660963732` (it fails at `52182660963731`).

*Proof.* (T1): if `D = 1`, Lemma 3(a). If `D >= 2`, then `k_par >= D*N^2*w >=
2*N^2*w` by Lemma 1, and `t <= t*` gives `e <= 4*N^2*w` by Lemma 4(a), so `2k >= e`.
A larger depth only increases `k_par`.

(T2): by Lemma 4(c), `D >= 2`. If `D = 2`, Lemma 4(b) and Lemma 2(b). If `D >= 3`,
Lemma 3(b) (`N = 2^H1 >= 64`).

(T3): widths with `t* - 1 <= log2 e <= t*` have `D >= 2` (the argument of Lemma 4(c)
loses one bit: `n >= 4*N^2*2^(-1)/(1 + rho) >= N^2`), so they fail by (T1); hence
`e_fit > 2^(t*)`. By (T2) every integer `e >= 2^(t* + tau)` fits, so `e_fit <=
ceil(2^(t* + tau))`, and `log2 ceil(x) <= log2 x + 1.45/x` with `x = 2^(t* + tau)` far
below `tau`.

(T4): `t = 52182660963730` is below `t*` by `0.9237`; `t = 52182660963731` is above it
by `0.0763 >> tau`. For the integer `t` the verifier makes the same decision with exact
integers: `e = 2^t` satisfies `(A-1)*t <= A*(2*H1 + 2)` (infeasible), or
`(e - 10*N^2)^A >= (4*N^2)^A * e` (fit), because the ratio of the two sides is
`2^((A-1)*t - A*(2*H1+2)) * (1 - 10*N^2/e)^A` with exponent margin at least `1` and
`10*N^2/e <= 1/1000`, where `(1000/999)^250 < 2`. The depth at `e = 2^t` follows from
Lemma 4(e), since `249*t - 250*k*H1` is never zero for the `t` used.

(T5): same as (T1), (T2) with Lemma 4(d); at depth one `k_par > e`; depth three and
beyond by Lemma 3(b). QED

## 6. What the verifier checks

`verify.py` (standard library, about two seconds) does the following.

1. **Sources.** It authenticates the six pinned inputs by SHA-256, reads `H1` and the
   atom `1/250` from the selected-stage result, matches the four stock-formula strings
   of the parameters file, and requires the cited sentences of the bridge, #4954's proof
   and README, and #4970's README (including the open "six-bit window" question).
2. **Lemma 1.** The `GL` order bounds and `N^2 <= cG <= N^2 + c_B` for 170 cases over
   `N` in 2..5 and `B = q^j, q^j + 1`.
3. **Lemma 2.** All 336,636 depth-two instances in `N in {2,3,4,5}`, `q in {3,5,7}`,
   `k_old in {1,2,5}` and every width of depth two: the source formula's fit decision
   equals `e > 4*N^2*w + 4*delta_B + 2*k_old` in each.
4. **Lemma 3(b).** `N^(D-2) >= 8*D + 1` for `D = 3..399` at `N = 64`.
5. **Lemma 4 in exact integers.** For `N in {8,16,32}` and atom denominators `A in
   {2,3,4,5}` it scans the widths around (and, up to 150000, all below) the two edges
   `e^(A-1) <= (4*N^2)^A` and `(e - 10*N^2)^A >= (4*N^2)^A * e`. On every width the
   best reading of the formula (`delta_B = 0`, `k_old = 1`) fails below the first edge and
   the worst reading (`delta_B = N^2`, `k_old = N^2`) fits above the second. The scans
   are exhaustive from `e = 1` where marked in `RESULT.json` (`e_lo = 1`); the others
   are windowed 300 widths below the first edge and above the second.
6. **Exact transition at large rank.** For `N = 2^h` with `(h, A)` in `(40,2)`, `(41,3)`,
   `(51,5)`, `(59,11)`, `(100,2)`, `(101,3)` it computes, with exact big integers and block
   by block in `w`, the least width from which every width of depth two fits. It does so
   for the best reading (`delta_B = 0`, `k_old = 1`) and the worst reading (`delta_B = N^2`,
   `k_old = N^2`), and checks that both lie in the bracket between the two edges. The best
   reading sits `4*N^2` to `8*N^2` above the infeasible edge and the worst `10*N^2` to
   `18*N^2`, a relative offset of order `1/w`. This is the regime of the selected stage, in
   which `w` is huge, at ranks small enough to evaluate.
7. **Selected rank.** Exact integer comparisons give `t*`, `t**`, the integer split at
   `52182660963730 | 52182660963731` (and `52182660963731 | 52182660963732` for the
   guard), the depth-one onset `t = 26091330481865`, the margin
   `t*/250 >= 2*10^11 + 3`, and a table of `t = 52182660963724 ..
   52182660963738` with the depth and both decisions.
8. **Controls.** Ten rejection controls: a tampered selected rank; an off-by-one, a
   dropped-chart-excess and a factor-two version of the depth-two criterion; an inflated
   infeasible edge in the translation scans and in the large-rank check, and a deflated fit
   edge in the translation scans; a shifted rank that
   must change the table; a fit claim at `52182660963730` and an infeasible claim at
   `52182660963731`. Each must be rejected. Every check raises, so `python -O` does not
   skip it.

The stored `RESULT.json` is the exact receipt that `verify.py --write` regenerates.

## 7. What is not claimed

* No new kappa, supplier admission, frontier change, or materialisation of the rank
  `2^25986965159937` word. The decision is arithmetic in the exponent of `2`.
* The result is for the **source prescription** with the exact depth
  `D = floor(log_N ceil(e/w))`. The parameters file allows "any larger explicit integer
  bound"; the infeasible side holds for it, the fit side as stated does not.
* (HB) and (Hold) are cited hypotheses. The derivation of `c_B <= N^2` in #7101 and of
  `S_old = 1` in #4970 are not replayed here.
* The remaining window around `t*` has width at most `2^(-2*10^11)` in `log2 e`. Its
  exact resolution depends on the realised `B`, the chart excess and the ceiling in
  `w`; this package does not decide it.
* The sources pinned here are the #4470 stage of #4954. #7101 states that the same
  rank is retained by the later `frontier6030` BIT stage; that statement is not
  checked here, and nothing is claimed about the current selected record beyond the
  shared parameters used above.
* The tail steps of Lemma 4 are real-analysis inequalities proved above. The verifier
  checks their integer constants and runs the same chain exactly at small parameters; it
  does not evaluate `2^(5*10^13)`-sized numbers.

## Open next questions

1. **Larger admissible depth.** The parameters file allows any larger explicit bound
   `D' >= D`. Replacing `D` by `D'` in Lemma 2 moves the first edge to
   `250*(2*H1 + log2(2*D'))/249`. Which bound does the compiled prescription use, and
   where does the fit start for it? *First step:* read the depth bound in the compiled
   stock formula. *Blocked by:* the bound is not pinned in the sources used here.
2. **Exact remaining window.** Can the last `2^(-2*10^11)`-wide window be decided?
   *First step:* fix `q` and `B` from the compiler realisation and find the block of
   `w = ceil(e^(1/250))` that contains `4*N^2*w`. *Blocked by:* `B` is not materialised.
3. **Current selected record.** Does the later `frontier6030`/`frontier7000` BIT stage use
   the same rank, atom exponent and stock formula, so that `t*` applies to it as stated?
   *First step:* compare its stage record with `query-thinned-controllers/RESULT.json`.
   *Blocked by:* the comparison needs that stage's source bindings, not attempted here.
