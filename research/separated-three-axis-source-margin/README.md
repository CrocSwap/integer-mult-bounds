# A quantitative margin on separated three-axis source factors

**Result.** The order `(0,1,2,4,6,5,3,7)` is singular for every
repeated directed factor `[[1,u],[v,1]] tensor 3`, including strict
positive-decay factors. For actual extremal-phase fine-prime factors,
a common dyadic target and explicit prime separation give this order
and its reverse a uniform determinant and inverse-displacement margin.
The margin tolerates matched periodic aliases and a factor error that
needs only `ceil(233+42 log2 p)` fractional bits; `p` bits suffice for
`p>=4096`.

## Exact scope

Let `p>=4096`, let `t` be dyadic and let three distinct odd primes satisfy

```
s_l >= p^4,
(1-1/(2p^2))t < s_l <= (1-1/(4p^2))t,
|s_l-s_m| >= t/(32p^2)     for l != m.
```

Use the retained integer `alpha=ceil(sqrt((4/pi)ln(16p)))`,
`a=pi alpha^2`, `w=exp(-2a)`, and the literal selected factors

```
C_l = [[1,U_l],[V_l,1]],
U_l = exp(-a(2(t-s_l)+1)/s_l),
V_l = exp(-a(2s_l-1)/s_l),
C = C_0 tensor C_1 tensor C_2.
```

Physical bit axes have vertex index `4x_0+2x_1+x_2`.
For the displayed order and its reverse, with `E(A)=A-ZAZ^T`, set
`D=a^3 w^2/(2^16 p^6)`. The proof gives:

| Quantity | Lower bound |
| --- | ---: |
| `abs(det E(C))` | `D` |
| `sigma_min(E(C))` | `2^-21 D` |
| `sigma_min(E(C^-1))` | `2^-49 D` |
| Forward margin after the permitted factor errors | `2^-22 D` |
| Inverse margin after the permitted factor errors | `2^-50 D` |

Factor error `<=2^-71 D` suffices. Matched periodic aliases use
`<=2^-73 D` per factor entry; a further periodic-table error
`<=2^-73 D` still meets the contract. The inverse is the exact
inverse of the selected tensor of factor tables. Additional arithmetic
in tensor or inverse construction requires its own error and cost bill.

These are **two vertex orders**, not an all-order numerical theorem.
The common target and prime gaps are hypotheses, not consequences of
mere distinctness. There is an exact source-prime fixture at `p=4096`
and a qualified eventual existence proof at the retained scale
`ln t=Theta(p^(1-epsilon))`, fixed `0<epsilon<1`; no practical
existence threshold is asserted.

## Why the source separation works

For independent directed factors `(u,v),(x,y),(r,z)`, the determinant's
first nonzero homogeneous part in the lower entries `v,y,z` is

```
(u-r)(ur+x^2)(xy-uv)(xy-rz).
```

Complete exact expansion has 7,529 terms. Its remaining weighted
coefficient mass is 7,682,848, below `2^23`. On the actual source
curve `U(s)` and `q(s)=U(s)V(s)=exp(-2at/s)`, the prime gaps
give `abs(U_l-U_m)>=a/(32p^2)` and
`abs(q_l-q_m)>=aw/(32p^2)`. This controls the leading term while
the full higher-degree remainder is paid explicitly.

[PROOF.md](PROOF.md) supplies the continuous inequalities, inverse
Schur/reversal identity, all perturbation constants, aliases and
prime-selection limits. No physical phase or chirp is discarded.

## Evidence and replay

[RESULT.json](RESULT.json) records the primary subset-recursion
polynomial reconstruction, two exact rational margin fixtures, sixteen
positive Gram checks, source-prime certificates and rejecting controls.
[review/LEIBNIZ-RESULT.json](review/LEIBNIZ-RESULT.json) independently
reconstructs both complete polynomials through Kronecker assembly and
literal Leibniz expansion. Each order expands 16,687 nonzero determinant
permutation products into 1,186,624 signed monomials before collection.
Full coefficient dictionary hashes agree. The second implementation
imports no primary code; both were written by the same AI worker.

```sh
python3 -I -W error -B research/separated-three-axis-source-margin/verify.py
python3 -I -W error -B research/separated-three-axis-source-margin/review/check_leibniz.py
python3 -B scripts/research_package.py --package research/separated-three-axis-source-margin --check-only
python3 -B scripts/research_package.py --package research/separated-three-axis-source-margin
```

The registered replay also runs both arithmetic paths under `-O`.
Python 3.12 and the standard library suffice. No network is used by
the arithmetic verifiers. Their three copied scientific inputs are
authenticated against exact byte counts and SHA256 in
[DEPENDENCIES.json](DEPENDENCIES.json). Metadata provenance additionally
needs canonical main and the pinned #7599 Git object. In a fresh
checkout where that pending source is absent, fetch that explicit head
before running the metadata gate:

```sh
git fetch --depth=1 --filter=blob:none https://github.com/CubeJerry/integer-mult-bounds.git 702c7616667c5f4e583eb73687944d148b7a1ccf
```

This fetch is a documented dependency, not a claim that the pending
head is an ancestor of the package branch. Direct arithmetic replay is
self-contained in the committed package.

The independent root [review](REVIEW.md) also recovers the leading term
from complementary minors and proves a sufficient coarse remainder bound
8! 16^8 < 2^48 without using the exact higher-degree coefficient mass.

## Sources and relation to prior work

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`.
Selected conditional kappa remains `0.00363005817`; all five
foundational assumptions remain. [SOURCES.json](SOURCES.json) records
the historical provenance, and [OVERLAP.md](OVERLAP.md) records the
bounded overlap screen.

- #7599, head `702c7616667c5f4e583eb73687944d148b7a1ccf`, supplies
  the extremal physical selector, two-axis box bounds, alias estimate
  and inverse-error framework.
- #7598, head `0a6315b71a47b37a4faa2a4f555c5bc4e9e87811`, supplies
  the prior exact source-specialization argument. That transcendence
  argument is not needed for this quantitative separated-family proof.
- #7600, head `8df9a7c57aaf87873556867f96658c2474518238`, supplies
  the local two-axis scalar adapter; no three-axis producer admission
  is claimed here.
- The [published companion](https://github.com/CubeJerry/integer-mult-bounds/tree/34c09f760300e84a6d4f32e77c2c21c9e03078e3/research/three-axis-extremal-source-rank), source commit
  `34c09f760300e84a6d4f32e77c2c21c9e03078e3`, proves all-order exact
  source rank without a quantitative margin. This package addresses
  its first open question under extra source separation.
- Tim Trudgian, [Updating the error term in the prime number theorem](https://arxiv.org/html/1401.2689v2#S2),
  theorem 2, supplies the retained prime-count estimate with `x>=229`.

## Open next questions

[TASK.json](TASK.json) records each question's relevance, first step
and blocker.

1. Bound the higher-degree remainder along close distinct-prime source
   curves, where the present coarse coefficient mass loses the leading
   gap factors.
2. Identify a genuinely different order type and test whether the same
   separated-source hypothesis controls its leading determinant.
3. Bind an actual six-scalar producer to the matched periodic tables,
   then pay coefficient precision, tensor formation, inverse arithmetic
   and full-caller transport costs.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Chafik Boukhalfa, Vlado Vojdanovski, IdeaOuter, Jeremy Kothe and
the retained bilateral/framework lineage. This is local research
evidence, not a new kappa, complete multiplication theorem, human
peer review or formal-kernel acceptance. Apache-2.0.
