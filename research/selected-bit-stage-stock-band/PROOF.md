# Proof: two-sided parent stock and the exact fit band of the selected BIT stage

This is a scoped written proof about the selected record #4470 at base
`cef4b52f2a59009865bf8eabde1be3f159063703`. It is not a complete
multiplication theorem. Every claim below concerns the **source reserve
prescription** of the delayed-cover BIT producer. It makes no claim about
every possible implementation of the BIT supplier.

## 0. The selected stage and its source prescription

The selected BIT side has one ordinary conversion stage. The delayed-cover
producer (uniform saving `C1 = 69/20000` after cover) is stopped at atom width
`w = ceil(e^delta)` and uses the retained old ordinary supplier
(`a_old = 384599/10^10`) at its leaves. The resulting ordinary saving is

    (1-delta)*C1 + delta*a_old = 0.0034363538396,   delta = 1/250.

Source bindings, all byte-pinned in `SOURCES.json`:

* `research/query-thinned-controllers/RESULT.json`: `ordinary_BIT.atom = 1/250`,
  `bit_strictification.uniform_N = 2^25986965159937` (so `H1 = log2 N =
  25986965159937`), and the prime rule `odd q > 2^26*N^5`.
* `research/query-thinned-controllers/PROOF.md` §4 changes the atom to 0.004.
  It substitutes the compiled constants into "the delayed-cover stock formulas"
  with `w=ceil(e^0.004)`.
* `research/joint-helper-lattice/PROOF.md` (#4470) retains that BIT stage with
  atom exponent 0.004.
* `research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md` §8 and
  `BIT-ALLSIZE-PARAMETERS.json` `stock` define the reserve:

      W(w) = B*|GL_N(F_q)|*q^(N^2*(w-1)),
      S(e,w) = W(w)^D * S_old,    D = D_N(ceil(e/w)) = floor(log_N ceil(e/w)),
      k <= D*(N^2*(w-1) + ceil(log_q(B*|GL_N(F_q)|))) + ceil(log_q S_old) + 1,

  The source text says to "borrow `k<e/2` high digits" "for sufficiently large
  `e`". The parameters file states that "any larger explicit integer bound is
  safe" for D.
* `notes/three-stage-cover-rows.tex` (a #4470 proof supplement) says that
  `S_old` is the "inherited old-leaf reserve" with a "logarithmic reserve" and
  that "small widths use the retained supplier directly".

Write `n = ceil(e/w)`, `G = |GL_N(F_q)|` and `c_B = ceil(log_q B)`. The
**parent stock** is the part that the cover recursion takes from the borrowed
row:

    k_par = D*(N^2*(w-1) + ceil(log_q(B*G))).

The **inner (old-leaf) stock** is `k_old = ceil(log_q S_old) + 1`. The
prescription borrows `k = k_par + k_old` digits from the original chunk of
`e` radix-q digits. It is feasible exactly when `k < e/2`.

## 1. Lemma (two-sided parent envelope)

For every integer `N >= 1`, odd prime `q`, integer `B >= 1` and integers
`e, w >= 1`,

    D*N^2*w  <=  k_par  <=  D*(N^2*w + c_B).

*Proof.* `G = q^(N^2) * prod_{j=1..N} (1 - q^(-j))`. The product is below one
and at least `1 - sum_{j>=1} q^(-j) = 1 - 1/(q-1) >= 1/2 > 1/q` for `q >= 3`.
Hence `q^(N^2-1) < G < q^(N^2)`.

Then `B*G > q^(N^2-1)` gives `ceil(log_q(BG)) >= N^2`. Since `B <= q^(c_B)`,
`B*G < q^(N^2+c_B)` gives `ceil(log_q(BG)) <= N^2 + c_B`. Multiply
`N^2(w-1) + [N^2, N^2+c_B]` by `D >= 0`. ∎

The lower bound is the high-matrix lift together with one full low chart per
live level. It does not use `S_old`, `B` or the size of `q` beyond `q >= 3`.

## 2. Lemma (depth classification)

Let `N >= 2` and keep the notation above. Since `n = ceil(e/w)` we have
`(n-1)*w < e <= n*w`.

(a) `D = 0` iff `n < N`. Then `k_par = 0`, and the producer runs no cover
    level.

(b) If `D >= 1` and `n <= 2*D*N^2`, then `k_par >= e/2`, so the prescription
    is infeasible whatever `S_old` is. In particular:
    * Every `D = 1` width (`N <= n < N^2`) has `k_par >= N^2*w > (N^2-1)*w >= n*w >= e`.
      The prescription asks for more digits than the chunk has.
    * Every `D = 2` width with `n <= 4N^2` is infeasible.

    *Proof.* `k_par >= D*N^2*w >= (n/2)*w >= e/2`.

(c) If `c_B <= N^2` and `n >= 8*D*N^2 + 1`, then `k_par < e/4`.

    *Proof.* `k_par <= D*(N^2*w + N^2) <= 2*D*N^2*w`, and
    `e > (n-1)*w >= 8*D*N^2*w >= 4*k_par`. For `D = 0` we have `k_par = 0 < e/4`.

(d) If `N >= 64`, every `D >= 3` width satisfies `n >= N^D >= 8*D*N^2 + 1`.

    *Proof.* `N^(D-2) >= 64^(D-2) >= 8D+1`. This holds at `D=3` (`64 >= 25`),
    and `64*(8D+1) >= 8(D+1)+1` gives the induction step.

So for `N >= 64` and `c_B <= N^2`:
* the prescription is infeasible for all `N <= n <= 4N^2`;
* it is feasible on the parent side (`k_par < e/4`) for all `n >= 16N^2+1`;
* the undetermined window is `4N^2 < n <= 16N^2`, all of which lies at `D = 2`.

## 3. Theorem (selected width bands)

Take the selected values `N = 2^H1`, `H1 = 25986965159937` and `delta = 1/250`.
Put `t = log2 e` (a real number, since `e` is an integer width).

1. **No parent stock.** If `(249/250)*t <= H1 - 1`, i.e. `t <= 26091330481863`,
   then `D = 0` and `k_par = 0`. Here `n <= e^(1-delta) + 1 <= N/2 + 1 < N`.
2. **Infeasible band.** If `H1 + 1 <= (249/250)*t <= 2*H1 + 1`, i.e.
   `26091330481866 <= t <= 52182660963729` after integer rounding of the
   endpoints inward, then `k_par >= e/2`. The source reserve cannot be borrowed
   at any such width, for any `B >= 1`, any odd prime `q`, any `S_old >= 1` and
   any admissible larger depth `D' >= D`.

   *Proof.* `w <= e^delta + 1 <= 2*e^delta`, so
   `n >= e/w >= e^(1-delta)/2 >= 2^H1 = N`. Also `w >= e^delta`, so
   `n <= e^(1-delta) + 1 <= 2^(2H1+1) + 1 <= 4N^2`. Now apply 2(b). A larger
   `D'` only increases the lower envelope `D'*N^2*w`.
3. **Fit.** If `(249/250)*t >= 2*H1 + 6`, i.e. `t >= 52182660963735`, and
   `c_B <= N^2`, then `k_par < e/4`. If in addition `k_old <= e/4`, the full
   prescription borrows `k < e/2` digits.

   *Proof.* `n >= e^(1-delta)/2 >= 2^(2H1+5) = 32N^2 >= 16N^2 + 1`. Since
   `n >= N^2`, `D >= 2`. If `D = 2`, apply 2(c). If `D >= 3`, apply 2(d)
   and then 2(c).

Therefore the least width from which the source's stated reserve fits lies
strictly between `t = 52182660963729` and `t = 52182660963735`. The proved
sufficient guard and the proved obstruction are six bits of `log2 e` apart.
The predecessor estimate "`log2 e ≈ 2 log2 N/(1-δ) = 5.2183·10^13`" (#4612)
is thus correct to within this window. The new content is the matching
**lower** side and the band below it.

The band is wide. The rank-N uniform word first becomes applicable at
`t ≈ 2.609·10^13`, but its stock fits only from `t ≈ 5.218·10^13`. For about
`2.609·10^13` bits of `log2 e`, the selected producer must not be run as
prescribed. That includes **every** width at which it would execute exactly one
cover level. In that band the conversion must call the retained supplier
directly, as `three-stage-cover-rows.tex` permits for small widths. This is a
fixed threshold, so the exponent `0.0034363538396` is unaffected. The finding is
a precise domain statement, not a counterexample to the selected κ.

## 4. Hypotheses on the two remaining factors

* `c_B <= N^2`, i.e. `B <= q^(N^2)`. It is needed only on the fit side. It
  holds if the chosen prime exceeds `B`, which the finite prime-avoidance rule
  permits because only finitely many primes are excluded. It also follows from
  the inherited nested-width bound `log2 B < N^2` used in
  `research/lockstep-live-role-audit/constant_c.py` (#4436 realization). That
  bound is cited, not re-derived here.
* `k_old <= e/4`. It is needed only on the fit side. The source calls `S_old`
  a logarithmic reserve. Under any envelope
  `log_q S_old <= sigma_old*(1 + log2 e)` it holds at `t >= 52182660963735`
  whenever `sigma_old <= 2^(t-3)/(1+t)`. For example the lockstep-live-role
  audit's assumed `log2 S_old <= 2^64 * e^delta * log2 e` is far inside this
  range. The numerical value of `S_old` is **not** derived here. The
  infeasibility statements need only `S_old >= 1`.

## 5. What is not claimed

* No new κ, supplier admission, frontier change or implementation of the BIT
  word. The word of rank `2^25986965159937` is not materialized.
* Infeasibility is a statement about the source prescription `W(w)^D S_old`
  (and any larger admissible depth). It does not prove that another cover
  design could not run in the band.
* The outer reserve constant `C`, the complex row stock, tape, precision and
  analytic premises remain inherited.
