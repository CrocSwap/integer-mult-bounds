## Problem

The two-axis Gaussian source margin does not tensorize to a three-axis
parameter box. Even strictly decayed repeated factors make order
`(0,1,2,4,6,5,3,7)` singular. Exact rank at actual distinct-prime
source parameters alone gives no rounding tolerance.

## Change

Prove a quantitative margin for this order and its reverse when the
three source primes share a dyadic target and have pairwise gaps
`>=t/(32p^2)`. The complete determinant expansion isolates
`(u-r)(ur+x^2)(xy-uv)(xy-rz)` as the first nonzero lower-entry-degree
part and pays every remaining coefficient.

The resulting determinant bound is `D=a^3 exp(-4a)/(2^16p^6)`.
Exact tensor-inverse displacement, arbitrary factor perturbations and
matched periodic aliases are covered. A sufficient further
periodic-factor precision is `ceil(233+42log2 p)` bits; `p` bits
suffice for `p>=4096`.

Separated-prime existence is a hypothesis of the numerical theorem.
One exact finite source fixture is supplied; eventual availability at
the retained scale follows from the explicit Trudgian theorem with
the threshold and asymptotic qualifications stated.

## Validation

Two independent arithmetic paths reconstruct all 7,529 coefficients
of both fixed-order polynomials: subset recursion and literal Leibniz
expansion. Their complete dictionary hashes agree. Exact rational
Gram checks test forward and inverse singular-value margins and
perturbation allowances. Proth-style certificates, nearest-grid
exponents, source separation and rejecting controls are replayed.
The registered normal and optimized commands use only the standard
library. See the package receipts and proof.

## Scope and credit

Two orders, common target, explicit prime separation. Close distinct
primes, all-order numerical bounds, differing targets and an admitted
coefficient producer remain open. Inverses are of selected tensors,
not selected sections of full inverses. No kappa or foundational
assumption changes.

Retain #7599/#7598/#7600, the exact-rank companion, source authors
and Tim Trudgian credit. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Separate model-assisted orchestration review is recorded in REVIEW.md;
no human or formal-kernel acceptance is claimed.

## Independent orchestration review

A root-authored complementary-minor calculation recovers the exact leading
term using only two row pairs and ten nonzero upper-only six-by-six minors.
A separate universal remainder bound 8! 16^8 < 2^48 still suffices throughout
the admitted source range, so acceptance does not depend on the sharper
exact mass table. The source gaps, perturbation bills and primary Trudgian
statement were also checked directly.

Reproduce with `python3 -B scripts/research_package.py --package research/separated-three-axis-source-margin`.
README.md documents the exact pending source fetch for metadata provenance.
