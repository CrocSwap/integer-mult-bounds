# All-order margins for three narrow physical source intervals

**Result.** All 40,320 simultaneous vertex orders of the selected
three-axis physical Gaussian tensor retain full ordinary Stein
displacement rank at a stated coefficient-table accuracy. The proof
covers the exact inverse of the selected rounded tensor and matched
periodic aliases, while retaining physical phase/chirp conventions
and explicitly charging the lower-entry differences.

**The source restrictions are stronger than mere prime separation.**
The theorem requires `p>=2^20`, a common dyadic target `t>=p^72`,
and one prime in each of three prescribed narrow intervals:

```
eta=(33,47,62)/64,
gamma_l=2p^2(t/s_l-1),
|gamma_l-eta_(pi(l))| <= 2^-26
```

for some permutation `pi`. These imply the original fine-prime
interval, `s_l>=p^4` and gaps `abs(s_l-s_m)>t/(32p^2)`.
The theorem does not cover every separated-prime triple.

## The proved margin and precision

Use the retained integer
`alpha=ceil(sqrt((4/pi)ln(16p)))`, `a=pi alpha^2`,
`w=exp(-2a)` and the exact extremal-source factors

```
C_l=[[1,U_l],[V_l,1]],
U_l=exp(-a(2(t-s_l)+1)/s_l),
V_l=exp(-a(2s_l-1)/s_l),
C=C_0 tensor C_1 tensor C_2.
```

Vertices are indexed by `4x_0+2x_1+x_2`, and `E(A)=A-ZAZ^T`.
Set `D=2^-18 w^4`. In every order, matched periodic factor
tables with further absolute entry error at most `2^-73D` give

| Quantity for the selected table tensor | Lower bound |
| --- | ---: |
| Smallest singular value of its forward displacement | `2^-22D` |
| Smallest singular value of its exact inverse displacement | `2^-50D` |

A sufficient further periodic-factor accuracy is

```
b >= ceil(379+72 log2 p).
```

At `p=2^20`, this is 1819 fractional accuracy bits. `p` bits
suffice throughout the stated range, and any fixed positive `Cp`
bits suffice eventually. This is a mathematical table-error contract;
no production routine or full caller is admitted.

The proof compares the literal factors with common-lower factors
`B_l=[[1,U_l],[w,1]]`. The latter have determinant margin
`abs(det E(B))>=D` in every order. The physical difference is
paid explicitly: `abs(V_l-w)<=4aw/t<=2^-73D`.
Physical lower-entry adjustment, aliases and further table error
together stay below the complete factor allowance `2^-71D`.

The inverse is the exact inverse of the selected tensor of rounded
factor tables. It is not a selected section of a larger inverse.
Additional tensor or inverse arithmetic needs its own error and
cost account. [PROOF.md](PROOF.md) supplies all inequalities.

## Complete algebra and independent review

Axis permutation and full bit complementation reduce the 40,320
orders to 3,360 classes. Only exact sparse truncations through
lower-entry degree four are computed; no full six-variable
determinant expansion is required for every order.

The complete classification proves first lower-entry degree `d<=4`,
first upper-deficit Taylor degree `K<=4`, and `K=0` if `d=4`.
Over all representatives and center permutations, the exact
minimum leading-center magnitude is `7/131072`, the maximum
gradient bill is 156, and the shifted coefficient-mass bound is
6656. Continuous neighborhood and complete remainder bounds turn
these finite algebraic facts into the uniform theorem.

The author supplied two exact arithmetic paths:

- [classification-result.json](classification-result.json): complete
  sparse symbolic lower-degree and Taylor classification.
- [mixed-column-result.json](mixed-column-result.json): 20,160
  independent mixed-coefficient evaluations by column multilinearity
  and 547,158 scalar Bareiss determinants.

A separate worker then independently reconstructed **every leading
polynomial and every lower-degree vanishing coefficient** through
Kronecker substitution, division-free Berkowitz determinants and
balanced decoding. It also independently reconstructed the full
Taylor substitution, coefficient/gradient bills and order coverage:

- [Classification review](review/classification/REVIEW.md)
- [Classification review receipt](review/classification/RESULT.json)

The root reviewer independently checked the entire analytic/source
chain and supplied an exact rational budget checker:

- [Analytic review](review/analytic/REVIEW.md)
- [Analytic budget receipt](review/analytic/RESULT.json)

Both reviews accept their stated mathematical scopes. They are
independent model-assisted reviews, not human peer review or
formal-kernel acceptance. All author science is byte-identical to
the reviewed snapshot; [PACKAGING.md](PACKAGING.md) documents the
sole script portability adapter and its reversible hash binding.

## Exact source witnesses and a method obstruction

Three Proth-certified primes satisfy the local guards at `p=2^20`
and `t=2^1440=p^72`. The certificates, original/narrow intervals,
nonwrapping selectors and literal coefficient exponents are checked
in [source-and-controls-result.json](source-and-controls-result.json).
The witnesses establish a local source family, not a complete outer
production instance.

At the retained scale `ln t=Theta(p^(1-epsilon))`, fixed
`0<epsilon<1`, the explicit Trudgian prime-count estimate gives
eventual existence in all three intervals. The threshold can depend
on the scale constants and epsilon; no practical threshold or
existence for every finite parameter is asserted.

The exceptional class `o=(1,2,4,0,7,6,5,3)` has first
lower-entry coefficient

```
-(r-u)^3 (x^2-ru) (x-r-u)
```

and first Taylor coefficient

```
(c_0-c_2)^3 (c_0-2c_1+c_2).
```

Equally spaced, pairwise separated centers cancel that Taylor
coefficient. This is an obstruction to the present leading-term
method, **not a counterexample at physical source parameters**.
Higher Taylor terms, higher lower-entry powers and physical
differences may change the conclusion.

## Replay and exact dependencies

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/narrow-three-axis-all-order-margin --check-only
python3 -B scripts/research_package.py --package research/narrow-three-axis-all-order-margin
```

[VERIFY.json](VERIFY.json) registers all arithmetic paths and both
reviews in normal and optimized Python, plus snapshot authentication
before and after deterministic regeneration. Eight registered commands
include an explicit optimized suite that starts five isolated child
interpreters with individual timeouts. Each command is bounded;
the total declared timeout budget is 630 seconds.

The arithmetic verifiers are offline and self-contained. Exact
copies of the source selector proof, fine-prime padding and bilateral
normalization are authenticated using [DEPENDENCIES.json](DEPENDENCIES.json).
Metadata provenance additionally resolves the canonical base and
the pending #7599 source head in Git. A cold checkout needs:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git e54523517d0f03e58352e647c403a5af3e525a57
git fetch https://github.com/CubeJerry/integer-mult-bounds.git 702c7616667c5f4e583eb73687944d148b7a1ccf
```

These are explicit read-only source fetches. The external pending
head is not claimed to be an ancestor of the package branch; the
strict source-history preflight is not asserted. Every scientific
input needed by the offline checks is retained in this package.

Individual command arrays are listed in VERIFY. To regenerate the
source-prime witnesses, the optional bounded search is:

```sh
python3 -I -B research/narrow-three-axis-all-order-margin/find_source_fixture.py
```

The registered source check verifies the retained certificates
directly and does not require rerunning their search.

## Provenance

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Selected conditional kappa remains `0.00363005817`; all five
foundational assumptions remain. [SOURCES.json](SOURCES.json),
[TASK.json](TASK.json) and [OVERLAP.md](OVERLAP.md) delimit the
provenance, actual scope and bounded overlap coverage.

## Open next questions

1. Remove the narrow prescribed intervals by resolving the
   exceptional leading cancellation with higher terms and physical
   source differences.
2. Bind an actual coefficient producer and inversion algorithm to
   the table contract with complete setup, transport and error costs.
3. Replace the eight-vertex classification by a structural argument
   that can address more than three axes.

TASK records each question's first step and blocker. The complete
multiplication theorem, growing dimension and full analytic recovery
remain outside this result.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit #7599/#7598/#7600 and the two local companion packages;
Chafik Boukhalfa, Vlado Vojdanovski, IdeaOuter, Jeremy Kothe,
Tim Trudgian and the retained bilateral/framework lineage.
Apache-2.0.
