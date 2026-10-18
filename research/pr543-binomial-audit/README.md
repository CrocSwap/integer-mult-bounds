# Independent binomial audit of the PR #543 bit moment

The nine-stage R420 bit-supplier moment from PR #543 satisfies
\[
M(a_-)<1<M(a_+),\qquad a_+-a_-=10^{-24},
\]
at the endpoints consumed by PR #626, including the exceptional-set fallback charge.

This contribution confirms the recorded bracket using a standalone standard-library checker and an exact certificate. Powers are evaluated through an outward-rounded generalized-binomial series, without importing the existing logarithm or exponential pricing engines. The result is an independent check of the finite numerical obligation, not a new \(\kappa\).

From the repository root, run:

```sh
python3 -I -B research/pr543-binomial-audit/verify.py
```

Expected output:

```text
PASS_PR543_BINOMIAL_MOMENT
Strict adjacent 10^-24 endpoints; 71 algebraic controls; 3 mathematical controls; 8 rejected inputs.
```

## Pinned sources

At the pinned base, the [maintainer review](../../docs/research/community-k492-review.md) identifies the selected composition as **PR #626 with PR #543**, with conditional \(\kappa=0.001635527380375392\). The bit-supplier exponent audited here is not the composed \(\kappa\).

| Source | Exact commit |
|---|---|
| Repository base | `66849e1475c930fd7732b1a0067ffee7e1e95f60` |
| PR #543 bit supplier | `2065fe4f72a914d907f1046603f5a36f17018535` |
| PR #626 consuming assembly | `660de893d27bb7abd1d5b01b1640207528a5c851` |

[`SOURCES.json`](SOURCES.json) records SHA-256 pins for six source files: the supplier’s `EXPECTED.json`, `README.md`, and `NOTICE.md`; its vendored `assemble9.py` and `global_k.py`; and `research/community-k492-audit/pr626/replay/ASSEMBLY.json`.

The checker verifies all six hashes before evaluating the moment. It also checks that the assembly names the pinned supplier commit, enables the bit surcharge, and records the two endpoints in order as accepted and rejected.

## Audited moment

The dimension is \(m=1+7\cdot9=64\), the live stock is \(L=30720\), and the paid child profile is:

| Rank \(r\) | Call count \(c_r\) |
|---:|---:|
| 1 | 380160 |
| 2 | 426624 |
| 4 | 32640 |
| 5 | 34560 |
| 6 | 15360 |
| 7 | 23040 |
| 8 | 2592 |
| 42 | 3456 |

Thus
\[
E=\sum_r c_r=918432,\qquad
\sum_r r c_r=1956096.
\]
The checker verifies the deficit identity
\[
mL-\sum_r r c_r
=9984
=32(2\cdot4\cdot120-9\cdot8\cdot9).
\]

The exceptional fraction is \(10^{-16}\), with \(32m^2E=120380719104\) rank-one fallback calls. Using the same \(1/(mL)\) normalization for ordinary and fallback children gives
\[
M(a)=
\sum_r\frac{r c_r}{mL}\left(\frac mr\right)^a
+\frac{32mE}{10^{16}L}\,m^a.
\]

The checked endpoints are
\[
a_-=\frac{413456747036699736067}
{250000000000000000000000},
\qquad
a_+=\frac{1653826988146798944269}
{1000000000000000000000000}.
\]

[`certificate.json`](certificate.json) contains the exact rational residual intervals. The upper bound for \(M(a_-)-1\) is negative, and the lower bound for \(M(a_+)-1\) is positive. All weights are positive and all bases exceed one, so continuity and strict monotonicity make these endpoints a bracket of the unique crossing of one.

## Why the enclosure is valid

For integers \(0<r\le m\) and rational \(0\le a\le1\), put \(z=1-r/m\). The generalized-binomial identity gives
\[
\left(\frac mr\right)^a=(1-z)^{-a}
=\sum_{n=0}^{\infty}t_n,
\qquad
t_0=1,\qquad
t_n=t_{n-1}z\frac{a+n-1}{n}.
\]
Every term is nonnegative. Since \((a+n)/(n+1)\le1\),
\[
t_{n+1}\le zt_n,
\qquad
0\le\sum_{k=n+1}^{\infty}t_k
\le t_n\frac{z}{1-z}.
\]

[`verify.py`](verify.py) represents term bounds as integers on the scale \(S=2^{192}\). Each recurrence multiplication rounds down for the lower bound and up for the upper bound. The nonnegative multiplier preserves the enclosure inductively. Summing the lower terms bounds the full series from below; summing the upper terms and adding an upward-rounded geometric tail bounds it from above.

If \(T_n^+/S\) is the upper term bound, the stopping condition is
\[
\left\lceil T_n^+\frac{m-r}{r}\right\rceil
\le 2^{192-160}.
\]
The added tail is therefore at most \(2^{-160}\). This threshold bounds the tail, not the entire interval width; accumulated rounding remains included in the returned interval.

The cases \(a=0\) and \(r=m\) return exactly one. Otherwise, the checker stops at the tail threshold or raises an error after 16384 terms. At both audited endpoints, the rank-one power takes 6344 terms and the rank-42 power takes 94. Exact rational weighted sums then enclose \(M(a)\).

## Controls and verification

Three mathematical controls test distinctions that matter to the endpoint decision:

- **The fallback charge cannot be omitted.** At \(a_+\), the ordinary-child moment without the surcharge has upper bound below one, while the full moment has lower bound above one.
- **Rank mass and call count do not determine the moment.** Replacing one rank-one and one rank-42 call with one rank-two and one rank-41 call preserves total calls, rank mass, maximum child rank, and the fallback charge. The altered moment is strictly above one at \(a_-\). This is an arithmetic control, not a proposed legal supplier.
- **A partial sum is not an upper enclosure.** For \(a=1\), \(m=64\), and \(r=1\),
  \[
  \sum_{n=0}^{7}\left(\frac{63}{64}\right)^n
  =\frac{33319196443135}{4398046511104}<64,
  \]
  whereas the complete series equals 64.

The checker also tests 71 power enclosures by a separate algebraic comparison. For each reduced exponent \(a=p/q\), it verifies
\[
\mathrm{lo}^{\,q}\le\left(\frac mr\right)^p\le\mathrm{hi}^{\,q}
\]
using exact rational integer powers, with no second series evaluator.

Nine fixed cases cover boundaries and simple powers. The remaining distinct cases use `random.Random(71)`, sampling \(2\le m\le64\), \(1\le r\le m\), denominators from 2 through 71, and positive numerators below the denominator. Sampling stops at 71 total cases, all recorded in the certificate. The same seed sets the missing-tail degree to \(1+(71\bmod13)=7\). This coverage is finite and nonexhaustive.

Eight rejection controls cover zero rank, rank above dimension, negative exponent, exponent above one, nonrational exponent, noninteger count, zero count, and a tail left unresolved by a one-term limit.

The reproduction command compares the entire recomputed certificate with the committed one; `--emit` prints it instead. The following checks passed under Python 3.12.3:

```sh
python3 -I -B research/pr543-binomial-audit/verify.py
python3 -I -O -B research/pr543-binomial-audit/verify.py
make selected-record-check
```

Disposable-copy mutations also produced the expected failures:

| Mutation | Observed rejection |
|---|---|
| Change the committed certificate | `committed certificate differs from recomputation` |
| Change the pinned supplier `EXPECTED.json` | `source hash mismatch` |
| Drop the geometric tail | `algebraic enclosure failed: (64, 1, '1')` |
| Round upper terms down | `algebraic enclosure failed: (64, 1, '1')` |
| Omit the fallback coefficient | `claimed strict root bracket failed` |

## Dependencies and limits

The arithmetic is independent of the existing Mercator/atanh logarithm and Taylor exponential engines. The paid profile, live stock, exceptional fraction, and fallback count are inherited from the supplier accounting, however: the source hashes pin those inputs but do not establish their construction legality.

Neither supplier was rebuilt, and neither `make verify` nor the cold `make frontier626-verify` replay was run for this contribution. The construction and all-size theorem obligations remain as stated in the [maintainer review](../../docs/research/community-k492-review.md), including interface realization, hosting, residuals, precision and exact recovery, and analytic transfer. This finite audit is not a formal verification of the multiplication theorem.

## Attribution and license

Contributor: **0x-chad**, with substantial OpenAI assistance. New material is under the repository’s **Apache-2.0** license.

The R420 supplier is **eumemic’s PR #543**, prepared with substantial Anthropic Claude assistance. Its [NOTICE](../e8-bit-r420/NOTICE.md) preserves the full lineage, including eumemic’s PR #493 skeleton, DreamingOfClouds’ PR #503 dead-register totals and PR #510 nine-stage pricing, and the preceding decoder, geometry, hosting, and moment-engine contributions.

The consuming PR #626 allocation is **Chafik Boukhalfa’s** contribution, building on **Jeremy Kothe’s** K-triangle construction and dispatch work. The selected composition also retains the preceding construction and verification work credited in the maintainer review, including **Rohan Arun’s PR #559 recurrence correction**.
