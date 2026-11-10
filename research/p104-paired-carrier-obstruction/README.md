# Paired resident-carrier obstruction

**All 122 proportional pairs of eligible helper intervals in the exact #6702
word fail their combined repair condition.** This closes a specific pair
mechanism left open by #6765; it gives no new native word or kappa.

| Paired edit | Pairs | Complete cut systems | Span hits |
| --- | ---: | ---: | ---: |
| Three MOVEs collapse to one, shared MOVE counted once | 108 | 439 | 0 |
| Four MOVEs collapse to two, middle exports retained | 14 | 248 | 0 |

The repair alphabet permits arbitrarily many dyadic injections from the
unchanged held row into any other resident public or live owned field, and
unrestricted free full-bank output cleanup. [PROOF.md](PROOF.md) specifies
all chronological bounds, the no-feedback premise, COPY observables, exact
paired accounting, and the all-dyadic reduction. The 14 classes containing
three intervals are covered only pairwise; simultaneous triple coupling
remains untested.

## Reproduce

Registered replay from repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-paired-carrier-obstruction
```

Expected: both direct modes report `PASS_P104_PAIRED_CARRIER_OBSTRUCTION`,
followed by `PASS_REGISTERED_RESEARCH_PACKAGE`. **No new κ.**


Only the Python standard library is required:

```sh
python -I -B research/p104-paired-carrier-obstruction/verify.py
python -I -O -B research/p104-paired-carrier-obstruction/verify.py
```

All generated files use temporary storage. The complete rational census is
reconstructed from the 91,169-byte pinned word and checked against
CENSUS-SUMMARY.json; its redundant 1.7 MB expansion is not shipped.
SHARED.json and DISJOINT.json preserve the frozen primary receipts.
INDEPENDENT-REVIEW.json contains every independently generated dual witness.

The primary suffix/span primitives are retained byte-exact from #6765; only
the pair-specific candidate construction is new. The separate forward SSA
review regenerates all rational rows, classes, pairs, combined responses,
residences and 687 systems without importing the primary generator or solver.
Its 9,199 direct dot products validate all dual witnesses. The direct forward
combined-error sweep also checks all 122 errors and source no-feedback.
Positive/negative span fixtures and independent altered-witness/inventory/
target controls prevent unconditional rejection. See the independently
prepared [review](INDEPENDENT-REVIEW.md) for its precise coverage.

## Sources and credit

ORIGINS.json authenticates the exact #6702 native word used by #6726, the
#6765 primitives, the independent reviewer code and its receipt. The original
source heads are retained separately from publication retention commits.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This is independent implementation review within the same
AI-assisted session, not external human or formal-kernel acceptance. Source
native/helper, root, compiler and analytic authors retain their attribution;
see NOTICE.txt and the byte-exact retained predecessor notice.

## Open next questions

- **Simultaneous triple coupling:** the 14 size-three held-row classes are
  not excluded. A first step is to state the complete multi-cut chronology
  and exact shared-MOVE bill; the blocker is that pairwise failure does not
  imply failure of the three-way combined response equation.
- **Interacting sources or changed source basis:** first give a causal
  all-old-input identity including cross effects. The present fixed-source
  tensor argument does not justify adding errors when source rows change.
- **New paid carrier paths:** first supply an exact optimistic complete
  signed invoice and actual owned/public routing. No paid-stop exclusion
  is claimed here, and no floating pilot enters the theorem.

No new search is assigned by these questions. Publication and scientific
assessment are separate from this replayable, source-bound result.

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Exact retained-input commit: `d3e76b0a33d4c1edf3de2eab379a4225cae387be`.
Source paths and bytes are pinned in `SOURCES.json` and `ORIGINS.json`.
