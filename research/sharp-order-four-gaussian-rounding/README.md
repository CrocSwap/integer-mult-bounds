# Sharp radial optimum for exact-sum Gaussian rounding that squares to wire swap

Let `C_+(u,v)=((s+i*d)/2,(s-i*d)/2)`, where `s=u+v` and `d=u-v`.
For every total map on Gaussian integer pairs that preserves `s`, has
combined Euclidean error at most one from `C_+`, and obeys
`F^2(u,v)=(v,u)`, the forward outward radial slack is at least

\[
\beta=\sqrt{19}-\sqrt{13}.
\]

An explicit global bijection attains this bound. It also commutes with
global Gaussian units, fixes equal-input pairs, commutes with common
Gaussian translation and has inverse `swap o F`. Its forward outward,
inverse outward and bilateral radial suprema all equal beta. The lower
bound requires no phase covariance, periodicity or separately assumed
matching representation.

## Proof and construction

[proof/PROOF.md](proof/PROOF.md) reduces an arbitrary candidate on the exact
sum-one fiber to a quarter-turn-equivariant unit matching on the half-grid.
A square of 36 vertices cannot close under that matching: each internal
edge orbit uses eight vertices. Its forced boundary edge has radial cost
at least beta. An explicit pairing of adjacent square rings attains it.
The finite attaining cycle is

`(3,-2) -> (3i,1-3i) -> (-2,3) -> (1-3i,3i) -> (3,-2)`.

Squared pair norms alternate between 13 and 19. The direct partner rule
uses only ring, side and parity decisions; it does not search a growing
matching table. Python models use unbounded integers, so this observation
is not a physical cost claim.

## Evidence roles and exact reproduction

The proof role's frozen proof and bounded ring checker are under `proof/`.
An independent constructive review and separately written direct integer
implementation are under `review/independent/`. That review covers the
all-ring construction and matching-class lower bound; it explicitly does
not certify the arbitrary-map reduction. The root checked that reduction
separately and supplied another direct integer implementation under
`review/root/`. All roles shared the proposed formula; no blind, human or
formal-kernel review is claimed. [ROLE-BOUNDARIES.md](ROLE-BOUNDARIES.md)
describes the actual exposure and evidence boundaries.

The independent checker covers 66,804 half-grid points, 129 ring-pair
partitions, 50,625 Gaussian pairs, 320 additional signed inputs through
4,096 bits, and seven negative controls. The proof checker separately
checks all 24 boundary edges, seven complete ring pairs, 625 pairs and
premise/interface controls. Root checks cover 6,561 pairs, 1,024 half-grid
points and 40 large cases through 1,024 bits. The top-level verifier compares
all three implementations on a common cube and compares the two direct
implementations on large inputs. Radical comparisons use integer interval
bounds, with exact finite attainment checked directly.

From the repository root, Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/sharp-order-four-gaussian-rounding --check-only
python3 -B scripts/research_package.py --package research/sharp-order-four-gaussian-rounding
```

The eight bounded normal/optimized commands are listed in `VERIFY.json`.
They are read-only. The complete all-input result rests on the written
proof; the finite checks are corroboration and failure controls.
`CHECKSUMS.sha256` and `FREEZE.json` bind the publication files. Original
worker freezes are preserved unchanged. Historical local checkpoint paths
inside those original notes identify their provenance, not runtime inputs.

## Prior work and actual interface changes

Credit Ali Romman's #6509 for conserved nearest Gaussian rounding, phase
covariance, conjugation inverse and fourth power; Nick Petalas's #6619 and
ywz65's #2589 for the norm question and obstruction lineage. #6776 already
constructs an exact-square map in a four-axis block. This package proves
the sharp one-pair radial classification and does not claim first
exact-square Gaussian rounding. Nearby #6534, #6536 and #6574 have distinct
larger-block contracts. Exact source and inspected metadata pins are kept.

The unconstrained global-half construction and the conserved
conjugation-inverse construction obtain smaller constants under different
identity contracts. There is no numerical improvement within their classes.
The present result determines the additional cost of requiring the exact
square-to-swap identity at error one and exact sum.

## Limitations

Exact sum, `F^2=swap` and inverse-by-componentwise-conjugation are mutually
incompatible, even without an error premise: at the real input `(1,0)`,
the outputs would have to be conjugates whose sum has even real part.
The actual inverse here is `swap o F`.

The constructed map is globally Gaussian-unit covariant and exact on all
integral ideal images, so the known #6778 theorem excludes commutation of
this same stateless map across rows and columns. Pair square/fourth power
does not establish a tensor-stage or native-graph identity. Ordered calls,
different maps or an enlarged representation remain separate questions.

There is no selected caller admission, fixed-width or fixed-tape graph,
clean scratch/head restoration, accelerated native tariff, complete error
recurrence or new kappa. All five selected framework assumptions and
`kappa=363005817/100000000000` remain unchanged.

## Open next questions

1. Can a precisely pinned caller use `swap o F` as its negative provider and
   accept ordered nonlinear pair stages? First identify the actual inverse,
   tensor and representation requirements; #6778 blocks same-map commutation.
2. Can a complete fixed-width implementation preserve this contract with
   proved overflow, restoration and bit costs? First choose a signed format
   and charge every temporary and complete field. No physical graph is given.
3. What is the sharp radial tradeoff for a specified larger-block contract?
   The one-pair lower reduction does not transfer automatically to a larger
   lattice; pin that class before reusing the boundary argument.

## Credit

Prepared for **@CubeJerry**, with substantial OpenAI ChatGPT/Codex assistance.
The root proposed the annular construction and boundary mechanism; a proof
role established the arbitrary-map reduction, a separate constructive role
checked the mechanism, and root independently reviewed the critical
reduction and implementation comparisons. Prior notices are preserved.
Apache-2.0.
