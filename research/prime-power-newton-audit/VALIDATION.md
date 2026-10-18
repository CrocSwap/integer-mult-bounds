# Local validation and review scope

Executed on 2026-10-13, macOS arm64 (Darwin 25.5.0), CPython 3.9.6.
Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Only `research/prime-power-newton-audit/` is added.

- The complete frozen replay passes under `python3 -I -O -B`: 28 prime-power
  radices, all 697 primitive embeddings, 30,224 independently reconstructed
  coefficient valuations, all polygon edges and contacts, degree/product
  identities, both valuation normalizations, and nine rejecting controls.
- Eight focused tests pass under isolated optimized Python. They check all
  domain Eisenstein polynomials; a separate dense multiplication/long-division
  reference on small fields; literal radix-four coefficients; signed and
  periodic primitive exponents; strict malformed-input rejection; odd-prime
  collinear contacts; receipt numeric-type distinctions; and relocated
  source-pin verification with actual corrupted-source rejection.
- A minimal export containing this package and only its six pinned context
  files passes the full replay without Git, network, or installed packages.
  Changing its frozen coefficient-obligation count causes a nonzero exit with
  `frozen receipt mismatch` under `-I -O -B`.
- The unchanged PR621 primary verifier was freshly executed with `-I -O -B`.
  Its output is byte-identical to
  `research/prime-power-cyclic-inverse/EXPECTED.json`.
- `python3 -B scripts/verify_selected_result.py` passes, including exact κ,
  original source inventory, and proof-supplement checks. The selected record
  and `upstream/` have no diff from the base.

A separate Codex agent first derived the complete floor inequality and
valuation formula independently, then reviewed the final proof and both
implementations. No actionable correctness finding was reported. Review
covered slope signs, multiplicities, equality cases, π versus p normalization,
cyclic-ring reduction, basis substitution, primitive exponents, and controls.
The reviewer also replayed the frozen receipt and checked the radix-two sign,
basis-change involution, constant/leading coefficients, and malformed inputs.
This is AI-assisted review, not independent human peer review or formalization.

The contribution is additive research: no existing generator, supplier,
certificate, or selected construction changes. The repository-wide `make
verify`, selected cold replay `make frontier626-verify`, optional SymPy engine,
Lean, Linux execution, and remote CI were not run or claimed for this package.
The affected arithmetic and source-binding checks above were run directly;
no unrelated artifacts were globally regenerated.

The finite domain is fixed by assignment seed 68. No early-success stopping,
adaptive extra search, or empirical impossibility claim is involved. The
all-prime-power conclusion relies on the written proof and the standard
Eisenstein and Newton-polygon theorems, not on extrapolating the receipt.
Paid preparation, restoration, source access, physical hosting, compilation,
precision, tape, and analytic multiplication assumptions remain untouched.

Overlap inspection read the review ledger and the first 200 open-PR entries
at orientation, then refreshed the newest 100 through PR757. Targeted searches
for “Newton polygon”, “p-adic”, and “valuation” found no competing package
with this scope. No open sprint issue was found (only issue650). Related
PR666/668/628/692 are credited in NOTICE.md; PR736 changes the old replay's
zero-row-update performance, not the root-valuation obligation audited here.
This is a scoped queue check, not a claim of exhaustive literature novelty.
