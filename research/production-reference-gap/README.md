# The actual cap constructor already funds the production narrow gap

Prepared for **@CubeJerry**, with substantial OpenAI assistance. **No new kappa.**
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

The canonical `Reference.for_cap` computes a narrow row-gap certificate but
leaves its positivity conditional. This package proves that the source's
fine-theta/alpha domain and the constructor's **existing** allocation already
force its literal rational `narrow_gap` above `1/(16p^2)`. No larger target,
extra precision, altered rounding or replacement Reference is needed.

For every integer p>=2, legal cap/cut request, radius R>=1 and target t>=1,
with `theta in [1/(4p^2),1/p^2]` and `pi alpha^2>=4 log(16p)`, the result is

`reference.narrow_gap > (1/8-2^-46)/p^2 > 1/(16p^2)`.

This removes that separate production admission for this particular source
constructor. It does not apply to every manually specified Reference and
does not discharge the complete multiplication theorem's five assumptions.

## Why the implication is new

CrocSwap/integer-mult-bounds#4648 supplies the ideal narrow majorant gap and
generic half-gap rounding budget. It leaves actual W/precision binding open.
The canonical raw Gaussian proof supplies the literal certificate and the
cap constructor's error bound but keeps a positive certificate conditional.
The new observation joins those statements through the actual allocated
normalized Gaussian quantity:

`qbar>=16pB`, `Q*>=2^21 alpha^2 pB`,
`E>=47+ceil(log2 p^2)`.

Those are lower bounds on the **existing source allocation**, derived before
the global narrow inverse has been assumed to exist. The actual two outward
endpoint excesses and complete reference error then cost less than
`2^-46/p^2`. This is not a new general Gaussian or perturbation theorem.
`forward-fine-theta-conditioning` concerns the broad inverse and explicitly
excludes the narrow statement proved here.

## Proof, costs and evidence

[PROOF.md](PROOF.md) gives the all-parameter implication, exact source formulas,
source-derived precision and cutoff estimates, and a convenient explicit
`p>=2^200` onset for the usual O(p) allocation bounds. The gap implication
itself needs no new onset once its source domain and legal cuts hold.
The actual O(p^2 log p) offline weight precision, descriptor heights, later
coefficient/Schur/page work and retained backing remain charged.

[SOURCES.json](SOURCES.json) pins all 14 live canonical scientific inputs and
the frozen task-card provenance. [source.py](source.py) opens the unchanged
constructor cohort. [independent.py](independent.py) supplies separate exact
rational log/pi and direct-positive-Taylor checks. [verify.py](verify.py) and
[evidence/REPLAY.json](evidence/REPLAY.json) record 37 actual `for_cap` cases,
505 integer interval-budget checks and 6 failure controls.

Cases span p=2 through 65536, near both fine-theta endpoints, cap 1 and the actual
p^(15/16) cap, and extra rational/large radius and target values. The largest
target period is 2^37 and largest cap is 2^15. These are lazy constructor
metadata: no complete original field or large full-cell weight bank is
materialized. The fixtures do not claim source-prime generation or a native
production run. Controls exhibit actual negative certificates for low
manual entry precision, bad alpha and bad theta; invalid cap, cuts and
radius also reject.

## Reproduce

From the repository root with standard-library CPython 3.12:

```sh
python3 -B research/production-reference-gap/verify.py
python3 -O -B research/production-reference-gap/verify.py
python3 scripts/research_package.py --package research/production-reference-gap --check-only
python3 scripts/research_package.py --package research/production-reference-gap
python3 scripts/check_research_commit.py --package research/production-reference-gap --check-modes
```

Expected scientific status is `PASS_PRODUCTION_REFERENCE_GAP`. All source
identity, numerical and negative-control tests use explicit checks under
optimized Python. Finite checks corroborate the written proof; they are not
universal or proof-kernel acceptance.

## Open next questions

1. Can every production Core/halo context be delivered from one such shared
   cap-generated Reference at the complete source cost? This package supplies
   its gap admission; period legality, context geometry and owned coefficient
   delivery remain separate obligations.
2. Can the complete rational H-versus-ideal N/source-transform comparison be
   joined to the actual normalized inverse and remaining diagonal? The
   certificate theorem and component comparisons are credited; the complete
   source prefix/suffix and final recovery remain required.
3. Can the remaining native, routing and physical lifecycle premises be
   independently discharged at the same caller? This constructor lemma
   supplies no such physical theorem and no new complete kappa.

## Credit

See [NOTICE.md](NOTICE.md). The same canonical Reference, Gaussian and interval
sources retain Jose Manuel/jmbarrancoml, Mason Hale and the original project
contributors' credit. The ideal/half-gap result is unpaidmoon/#4648, with
the PR1673/PR1786/PR4100 lineage. Substantial AI assistance was used; any
independent lead review is recorded separately, without human or kernel
acceptance claims.
