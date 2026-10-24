# Actual raw log moments do not admit degree 23 at the fixed balanced witness

**A scoped negative finite certificate. No new κ, uniform rank, native word or selected-frontier change.** Replacing the Bernoulli chord by all actual raw log moments through degree 24 strictly sharpens every positive completed-moment bound. Nevertheless the unchanged `native-concentrated-balanced` witness fails degree 23: coefficient 0 passes, while coefficients 1 through 23 each have a rigorous lower bound exceeding the source complement capacity. This closes the predecessor's exact-raw-moment question for this fixed certificate, not for every compiler or potential.

## Fixed source and changed premise

Canonical base `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority revision 7; exact source commits, blobs and SHA256 are recorded in [SOURCES.json](SOURCES.json). All live inputs are declared in [VERIFY.json](VERIFY.json). The source files and selected record remain unchanged. The selected conditional `κ=0.00302015` is historical context, not the benchmark's `κ=0.00300120` or a result of this package.

The owning source is zxv's `research/net-tax-rank-compiler/LOG-MOMENTS.md`, `WEIGHTED-EXITS.md`, `compiler.py` and its exact `native-concentrated-balanced` benchmark. The supplied native paid and target histograms come from `research/native-lattice-retiming/RESULT.json`. This changes only the raw log-moment majorant. Keep the same native jobs, tensor product, scalar guards, completion/splitting taxes, logarithmic shift and inherited integer compiler/exit law:

```text
C = 90037/30000000,      t = 1-C,       κ = 0.00300120,
v = 260, c = 20, b = 21, u = 171/1000,  h = 3900,
A_upper = 139/40,
B_lower = 347/100 + 1679/1000,
beta = 127/125,         epsilon = 1/100000.
```

The candidate potential degree is 23 instead of 24. No parameters are searched or retuned. The raw profile, tax calculation and capacity are source-bound; only the raw-moment calculation is new. This is the assigned refinement of `formal-interface-lemma`, rather than an attempt to formalize already covered arithmetic or to change the supplier.

## Actual raw moments and two independent iid formulas

For each positive raw paid rank `r`, let `w_r=P_r*r^t`, `P_t=sum_r w_r` and `Y=ln(r)/ln(c)`. Compute the complete moment list

```text
b_n = sum_r w_r * (ln(r)/ln(c))^n / P_t,     n=0,...,24,
b_0 = 1.
```

Raw moments are not capped at 1: the source permits `Y>1`. The pinned 192-bit outward rational interval engine encloses each `r^t`, logarithm, power, weighted sum and positive division. The law is normalized by its own **paid** mass, never the target mass or the unweighted histogram count. The actual raw mean is approximately `0.860093849704`, below the predecessor's chord mean bound `431/500`.

For the chronological `v`-fold product, `X_raw=(Y_1+...+Y_v)/v`. Its exact moments satisfy both

```text
M_n = v^-n sum_(k=0..n) (v)_k Bell_(n,k)(b_1,...,b_n),
M_n = n!/v^n [z^n] (sum_(i=0..24) b_i*z^i/i!)^v.
```

The first identity groups equal indices in the expanded power. Each occupied index contributes one raw moment; the exponential Bell convention already counts partitions, so there is no extra `k!`. The second identity is the exponential generating function of the sum; truncating above degree 24 cannot affect the required coefficients. The verifier implements the Bell recurrence and a separate truncated-polynomial binary exponentiation, each with outward rational operations. Their intervals intersect at every degree, and their intersection encloses `M_n`. Independent first/second moment formulas and an exactly enumerated two-point, two-copy law corroborate normalization and the `v^-n` scaling.

## Full paid excess and capped reference are retained

Let `A_raw=P_t^v`, and let `Q_t` be the full completed/split paid moment. As in the predecessor, the actual relative excess is `(Q_t-A_raw)/A_raw`; its bound uses the original splitting tax **plus the full completion paid charge**, not the smaller net completion tax. The exact source expression remains

```text
x <= (original_splitting_tax + 2*delta^v)/alpha^v
  < 0.000001447491518642763738467578
  < epsilon = 1/100000.
```

For the capped raw reference `m_n=E[min(X_raw,1)^n]`, `m_n<=min(1,M_n)`. Original paid splitting adds at most its paid moment increase to the capped numerator; each completion contributes at most its full paid mass. Thus the completed moment is at most `(m_n+x)/(1+x)`. This expression is increasing in `x` when `m_n<=1`, giving the valid majorant

```text
mu_0=1,
mu_n=min(1,(M_n+epsilon)/(1+epsilon)).
```

The verifier applies this map to the interval-enclosed `M_n`. Neither a completion target credit nor the native net-tax surplus is used to reduce the paid law. Every positive `mu_n` upper bound is strictly below the source chord bound, while both zeroth moments remain exactly 1.

## Complete coefficient decision

The pinned `moment_coefficients` function takes the new upper moments in place of its chord moments. All Bell/Shift coefficients are nonnegative. Evaluating the same finite polynomial at the lower and upper interval endpoints therefore encloses the ratio belonging to the **chosen majorant certificate**; it does not give lower bounds for the true completed law. All 24 exact rational ratio intervals are retained in [RESULT.json](RESULT.json), rather than a grid of compiler heights.

| Quantity | Directed decimal enclosure |
|---|---|
| Capacity `eta=t*(153^260)^(t-1)` | `[0.019675906372710418424472814349, 0.019675906372710418424472814350]` |
| Degree-23 coefficient 0 | `[0.019424344760721554787093209632, 0.019424344760721554787093209633]` |
| Degree-23 coefficient 1 | `[0.019966957419831236745826239673, 0.019966957419831236745826239674]` |
| Degree-23 coefficient 23 | `[0.021677806467759466977142523404, 0.021677806467759466977142523405]` |
| Coefficient-23 ratio minus capacity | `[0.002001900095049048552669709055, 0.002001900095049048552669709056]` |
| Original degree-24 chord maximum | `[0.019352722774694608575957993948, 0.019352722774694608575957993949]` |

In particular, the highest falling-factorial coefficient simplifies exactly to `C_23=mu_1^23`, `D_23=beta^23`. It is independent of every higher moment and of the shift/ambient constants. Its ratio **lower** bound is greater than the capacity **upper** bound, proving this fixed sufficient coefficient certificate fails. Even the optimistic choice `epsilon=0` leaves the highest ratio strictly above capacity; refining higher moments or merely shrinking this paid-excess bound cannot repair the fixed degree-23 certificate.

This is stronger than failure to prove an interval comparison, but weaker than impossibility of the real compiler. The certificate uses the uncapped raw reference bound `m_n<=M_n`; directly bounding the capped law `E[min(X_raw,1)^n]` could be sharper. The actual completed law could also have smaller moments, and a different justified floor bound, certificate, potential or witness lies outside this result. The original degree-24 chord certificate remains a positive control; no claim of optimal degree over all such choices is made.

The original strict net-tax charge remains below 1, the source shift/ambient/floor/support/mean guards pass, and degree 23 still passes the ordinary base-range inequality. The exit coefficient condition already fails, so **no new `N` is emitted**. Final-rank and inherited outer-consumer guards are deliberately not bypassed or claimed: they are not reached. The predecessor's native/outer receipt and its rank witness remain unchanged.

## Reproduce and validation

```sh
python3.12 -I -B research/exact-raw-log-compiler/verify.py
python3.12 -I -O -B research/exact-raw-log-compiler/verify.py
python3.12 -B scripts/research_package.py --package research/exact-raw-log-compiler
```

The first local fixed-witness generation passed in 0.33 seconds under the global serial lock; it used no tensor histogram, flow replay, native replay, Lean, Docker or dependency installation. The verifier authenticates source bytes before executing the pinned interval/compiler code directly, bypassing bytecode-cache imports of those sources. Explicit exception checks remain active with `-O`. [VALIDATION.md](VALIDATION.md) records the test contract and limitations.

## Open next questions

See [TASK.json](TASK.json). A future contribution needs a separately justified changed exit certificate or bound before proposing a smaller sufficient rank using this law. The exact highest-coefficient identity identifies why more raw high-order arithmetic alone is insufficient here. Parameter searches, changed native laws, new rank witnesses and physical/precision admission are outside this assignment.

## Credit

Retain zxv's structural/net-tax compiler, Bell/capped-reference proof, outward interval engine and PR4453 native benchmark; Jacob Alan Sussman's Theorem 1G and finite integer compiler; PR4411/4414/4416/4433 product/completion/splitting lineage; Cinna Davis's native contributions and every retained native, stock, ownership, precision, analytic and recovery author. The new work is the actual raw moment enclosure, independent iid EGF check and exact fixed-degree-23 coefficient decision. Prepared for JoyboyBrian with substantial OpenAI Codex assistance, including a separate read-only formula review. Apache-2.0. No independent human or formal-kernel acceptance is asserted.
