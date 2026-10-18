# Exact L259 temporal-gauge cost

## Fixed source word and selected coordinate

The package reconstructs the frozen PR1263 scalar word from its pinned source. Its eligible helper set has 237 entries in increasing order. OS seed 32 selects index `32 mod 237 = 32`, namely helper `L259`. This coordinate is in the 218-element nonzero-static support, with static exponents `-1` forward and `+1` backward. PR1259's seed-37 slice occupies sorted eligible-helper indices `[37,53)`, so L259 is outside that slice. The zero-static search in PR1369 excludes L259; PR1350 and PR1353 concern L253 and L248.

For one orientation, enumerate the 144 chronological scalar ADDs incident to L259 in the frozen word. Write their exact dyadic coefficients as `c_i` and their signs on L259 as `s_i∈{-1,+1}`. An additional temporal gauge chooses an integer exponent `g_i` for each such ADD, begins at `g_0=0`, and returns to zero after the final ADD.

## Exact cost objective

For a nonzero dyadic `c=a·2^q` with odd positive `a`, the exact real-component ADD lowerer price is

\[
A(c)=1+\operatorname{bitlen}(a)+\operatorname{popcount}(a)+|q|
 - \mathbf 1[a=1\land q=0].
\]

At ADD `i`, the changed coefficient is `c_i·2^{s_i g_i}`. The complete real-primitive delta, including every scale needed to enter, change, and leave the schedule, is

\[
\Delta(g_1,\ldots,g_m)=
\sum_{i=1}^{m}\left(|g_i-g_{i-1}|+A(c_i2^{s_i g_i})-A(c_i)\right)+|g_m|.
\]

The verifier recomputes this integer objective from the frozen source word and checks that it equals the complete lowerer invoice difference. For a constant additional exponent `q`, the scale bill is `2|q|`; exact minimization gives `q=0` and delta 0 in each orientation.

## Finite interval and recurrence

If `c_i=a_i·2^{q_i}` with odd `a_i`, its ADD-price term is piecewise linear in `g_i`, with its only breakpoint at `g_i=-s_iq_i`. The unit-coefficient exception lies at that same breakpoint. Include the restoration breakpoint 0 and set

\[
\ell=\min(0,-s_1q_1,\ldots,-s_mq_m),\qquad
u=\max(0,-s_1q_1,\ldots,-s_mq_m).
\]

Clamping every exponent toward `[\ell,u]` cannot increase the path variation or any coefficient-price term: outside the interval all coefficient terms have the same outward slope, while clamping weakly shortens every adjacent exponent difference. Thus an optimum over all integer schedules occurs inside this finite interval.

The exact layered shortest-path recurrence stores, at layer `i` and exponent `k`, the minimum tuple

\[
\left(C_{i-1}(j)+|k-j|+A(c_i2^{s_i k})-A(c_i),\;\text{tie-break data}\right)
\]

over all previous exponents `j`; the terminal edge adds `|k|`. The verifier evaluates 41,344 exact edges for each orientation on domains `[-12,4]` forward and `[-4,12]` backward. A separate three-ADD brute-force control checks the recurrence against direct enumeration.

## Replayed result

Both optimal schedules use 21 inserted SCALE macros with total absolute scale work 24. They save 111 real primitives, or 222 complex primitives, per orientation:

| Orientation | Real before → after | Complex before → after | Payload / prefix bits |
|---|---:|---:|---:|
| Forward | 68,001 → 67,890 | 136,002 → 135,780 | 192 / 52 |
| Backward | 68,009 → 67,898 | 136,018 → 135,796 | 192 / 68 |

The complete paid recursive profile and every original nonscalar event remain identical. The pinned formal replay agrees on all 712 input columns in both orientations. Removing one inserted transition scale is detected by the endpoint replay; the zero schedule is an exact identity control.

This result is only a finite scalar circuit improvement on one helper coordinate of PR1263's frozen word. It does not compose with other helper schedules, admit a hosted supplier, change the selected record, or yield a new `κ`.
