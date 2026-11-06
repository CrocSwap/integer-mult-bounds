# Sharp zero-primary capped spectra at every idempotent rank

**Scoped mathematical proof with exact finite corroboration; no new kappa.**
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

For every characteristic-two field, idempotent D of rank k in dimension r,
and common zero-primary chain cap 1 <= m <= r, let ell be the largest odd
integer at most m. The exact answer is

    A+B=D,  nu_0(A),nu_0(B)<=m
    max [z(A)+z(B)] = min(2r-(k mod 2), r+(r-k)*ell).

Here z(X)=dim ker(X^r) and nu_0(X) is the nilpotency index on that zero-primary
space, with index zero for an invertible matrix. Nonzero-primary parts are
allowed. The formula includes zero/full rank and dimension one. Binary
odd-block constructions attain every case.

This resolves the specified local chain-cap question in Nick Petalas's
[#5928](https://github.com/CrocSwap/integer-mult-bounds/pull/5928). It extends
this package's initial corank-one and arbitrary-rank cap-two results into
one complete classification. At r=5,k=4 the sharp cap-four answer is eight:

| Cap m | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Sharp z(A)+z(B) | 6 | 6 | 8 | 8 | 10 |

The general proof also covers non-power-of-two even caps: r=12,k=10,m=6
has maximum 22. If one instead requires global A^m=B^m=0, a pair exists
exactly when k is even and r<=(r-k)*ell. Thus the globally nilpotent
r=5,k=4,m=4 domain is empty; that is a different contract from the value eight.

The [proof](PROOF.md) combines a surviving primary subspace for odd caps,
an injective intersection map for every even cap, the universal trace
bound, and a greedy allocation of the credited odd blocks. The even-cap
lemma does not assume that the intersection of the two kernels is invariant.
The shorter identity D(A^2+B^2)D=D is retained as a cap-two alternative.

## Evidence and reproduction

Use CPython 3.12 and its standard library, from the repository root:

```sh
python3 -I -W error -B research/capped-shared-block-spectrum/verify.py
python3 -I -O -W error -B research/capped-shared-block-spectrum/verify.py
python3 -I -W error -B research/capped-shared-block-spectrum/independent_oracle.py
python3 -I -O -W error -B research/capped-shared-block-spectrum/independent_oracle.py
python3 -I -W error -B research/capped-shared-block-spectrum/gf4_oracle.py
python3 -I -O -W error -B research/capped-shared-block-spectrum/gf4_oracle.py
python3 -B scripts/research_package.py --package research/capped-shared-block-spectrum
python3 -B scripts/check_research_commit.py --package research/capped-shared-block-spectrum
```

The author engine reports `PASS_CAPPED_SHARED_BLOCK_SPECTRUM`. It checks:

- Every binary matrix through dimension four, with 66,066 separate Leibniz
  characteristic-polynomial comparisons against matrix-power ranks.
- All 329,780 ordered pairs with coordinate idempotents of every rank, all
  1,316,964 pair/cap combinations, and every square-compression identity.
- All 13,090 (r,k,m) attaining constructions through dimension 33, plus
  explicit invalid-domain and forged-witness controls.

The separate lead engine reports `PASS_INDEPENDENT_CAPPED_SPECTRUM`. It
uses determinant polynomials and literal kernel-vector counts, without
importing the author engine or predecessor. It exhausts F2 through dimension
four and F4 through dimension two, at every rank and cap. The worker
extended its rank/cap loops around the separate arithmetic routines.

The independently written packed-column F4 engine reports
`PASS_ALL_RANK_ALL_CAP_F4_CENSUS`. It uses normalized field elimination and
kernel growth, with nonbinary arithmetic controls. It exhausts 1,049,352
ordered pairs over F4 through dimension three, at every rank and cap.
Its original scratch receipt writer was adapted to deterministic stdout;
the arithmetic engine is unchanged. No script imports another engine.

All six bounded warning-strict normal/optimized commands passed locally.
They are registered, and direct replays are read-only and
need no Git, network, third-party dependency or external input. Exact reviewed
hashes and the versioned proof/code review history are in [REVIEW.md](REVIEW.md).
These are independent AI checks, not human or formal proof-kernel acceptance.
The optional `--check-source-history` preflight refused this shallow checkout;
full-history ancestry validation is unclaimed. No history hydration or full
selected-construction replay was performed for this local result.

## Applicability to native callers

A required native length-two chain is a lower bound on available chain
length, not a zero-primary upper cap. In particular, the existing shared
triple in JoyboyBrian's #5507 has both zero-primary indices equal to three.
Its full support restrictions have a length-three zero chain plus a nonzero
scalar part; the helper extends the required native chain. Thus the native
condition alone does not justify imposing cap two on that caller. The
predecessor's complete funding obstruction and compensation remain unchanged.

To use the formula in a new caller, prove its actual shared blocks obey the
stated cap, then retain the complete ownership and target/paid accounting.
No chronological or physical realization of the attaining local matrices is
supplied here. Local sharpness alone establishes no new supplier saving.

## Sources, overlap and credit

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. [SOURCES.json](SOURCES.json) pins the original task card, selected
record and predecessor proof/open question as historical provenance.
The selected JSON governs current status despite older task text: selected
#6030 has conditional kappa 0.003125804, complex binding, admitted BIT 0.0034,
and the five retained native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery assumptions. None is discharged here.

The `bit-helper-contract` assignment is explicitly changed to this algebraic
side result. Scoped all-state PR searches for the source object, nilpotent
chain caps, ranks and idempotents found #5928 as the relevant spectral
predecessor; #4912/#6560 concern different compilation problems and #6596
concerns linear-support ownership. A bounded primary-literature check found
classical idempotent-sum and triangular-construction work, credited in the
proof. These checks are not exhaustive historical-diff, Discussion,
mathematical-literature or unpublished-work searches.

Credit Nick Petalas/#5928 for the unrestricted envelope, odd-block
construction, corank-one rigidity and cap question. Credit JoyboyBrian/#5507
for the two-owner four-support funding model and triple compensation;
Ali Romman/#5456 for the early-helper model; and the retained
#5452/#5388/#589/#555 BIT/native/owner/compiler lineage. Rank, primary-space,
Jordan, trace, triangular and telescoping methods are classical. No general
mathematical-priority claim is made. No predecessor scientific verifier is
imported or represented as independently audited.

## Limits

All dimensions and characteristic-two fields are covered by the written
proof; finite censuses stop at F2 dimension four and F4 dimension three.
Larger constructed witnesses are samples of that proof. Native chronology,
ownership, dirty restoration, physical execution, precision/tape, compiler,
complete target/paid accounting and supplier admission remain outside scope.
No new kappa, selected-frontier change, Lean or Docker run is claimed.

## Open next questions

- Establish an actual caller's zero-primary cap. Start with one pinned
  chronological block decomposition and show how its native restrictions
  bound all zero-primary chains, including helper extensions. A complete
  caller and applicability argument are still missing.
- Classify equality cases beyond the explicit attaining family. Start with
  corank two and cap three, recording when the intersection-map dimension
  bound and trace bound are tight. The present theorem proves the maximum
  and gives witnesses; it does not classify every maximizer.

Structured relevance, first steps and blockers appear in [TASK.json](TASK.json).
All engines use explicit checks active under optimization. Their managed
Python allocations are bounded by the declared finite domains; no fixed-memory
native implementation or formal acceptance is claimed.
