# Local PR1048 repair: certified pricing and bounded continuation coverage

This package supplies a usable reference-root pricer and an independently
reconstructed bounded move experiment. It does **not** certify PR1048's
advertised 645,900-pair exhaustion or claim a new supplier or kappa.

The maintainer's existing fixed-exponent counterexample reproduces. At
a=1/2, profile A has the smaller weighted count, yet
root_A < 47/1000 < root_B. This is Douglas Colkitt's prior finding, not ours.
Woklerx's overlapping PR1182 also reproduces: two false brackets at the
original default precision, four fixtures including two neighboring controls, its independent
integer checker, and its fail-closed controls all pass. Its bisection is
reused unchanged and credited, rather than duplicated.

The new contribution addresses the remaining comparison and coverage gaps:

- `pricing.py` certifies both PR589 reference endpoint signs and encloses the
  surcharge-inclusive signed comparison across the **entire** root bracket.
  It reports `BETTER`, `WORSE_OR_EQUAL`, or `UNRESOLVED`; exact profile ties
  are identified separately. Signed coefficients reverse interval endpoints.
- `coverage.py` independently reconstructs rational frame geometry, literal
  legal slots, stable operation identities, retained COPY constraints, and
  integer paid profiles. It recomputes post-first-move domains in both A and B.
- `independent.py` uses a separately written enclosing arithmetic engine,
  direct residual endpoint checks, fixed source inventory and semantic
  corruptions. It imports neither the primary pricer nor its interval engines
  for the arithmetic acceptance decisions.

## Verified bounded result

| Quantity | Result |
|---|---:|
| Named first operations | A[2028], A[2076], A[2129], A[281], B[1] |
| Legal literal first moves in their declared frame domain | 9,950 |
| Deterministically selected first states | 10 |
| Adjacent second-operation rows, both sections | 150 |
| Legal literal second moves | 125,698 |
| Cross-section second moves | 9,424 |
| Distinct exact local profile deltas, with full replay representatives | 24 |
| Certified improving occurrences | 0 |
| Certified no-larger-root occurrences | 135,648 |
| Of those, identical-profile exact ties | 56,685 |
| Strictly worse occurrences | 78,963 |
| Unresolved arithmetic occurrences in this bounded experiment | 0 |

These counts are ordered candidate paths, including commuting transports;
they are not distinct final words. First-state selection and each literal
candidate-set digest are recorded in `evidence/COVERAGE.json`. The frame
domain is the 636 original catalogue frames plus the exact rational span
closure of each slot's lower frame bound. It is deterministic and does not
accumulate unrelated earlier closure frames. It does not contain all possible
subspaces.

Six concrete pairs have both moves nominated by the original tuner but their
cross-section ordering is omitted by the old pair-search loop. The retained
witnesses are exact profile ties. This does not establish a missed improving
word, or show that equivalent final words cannot occur by other paths.

Different equal-profile first states can have different literal continuation
domains. The receipt separately records reachable profile-set comparisons;
profile equality alone is not used as a continuation cache key. The old
verifier's one global best candidate per operation does not prove per-slot
equivalence after every first state.

More concretely, neutral B[1] placements at frame 217 in slots 0 and 367 have
different reachable final-profile sets. From slot 0, transporting B[368] to
slot 92 at its recorded rational closure frame produces delta `{1: 4, 2: -2}`;
that profile is absent from the slot-367 state's declared second domain. It
is strictly worse. Three other equal-profile pairs have different literal
domains but identical reachable profile sets, so path differences alone are
not described as objective losses.

The retained-total restriction being incorrectly applied to B, and failure to
check the new last A touch after a removal, are demonstrated by small semantic
fixtures. No invalid old `all_legal_moves` candidate was found in the inspected
real-word domain. In particular, this word's B section never touches retained
registers, so the B-rule defect is latent here. Exact whole-profile versus
touched-register deltas are checked on all selected first states and one
representative of every observed final delta class.

## Reproduce locally

From the repository root, using Python 3.11+ and the already installed NumPy
required by the original tuner comparison adapter:

```sh
python3 -I -O -B research/pr1048-certified-repair/run.py --out /tmp/pr1048-repair-fresh
```

Use a new output directory. The driver authenticates all 36 mandatory inputs,
regenerates pricing and coverage, then independently checks the **fresh**
receipts. `EXECUTION.json` records commands, interpreter and elapsed times.
The bounded coverage run takes roughly 30 seconds on the development Mac;
this is verifier timing, not a multiplication-runtime claim. No network,
paid service, full search, native compiler or selected-frontier rebuild is
required. A pricing-only run is explicitly labelled as such.

Predecessor reproductions, run separately and retained in
`evidence/PREDECESSOR-RERUN.json`:

```sh
python3 -I -B research/community-batch1099-audit/check_pr1048_counterexample.py
python3 -I -B research/profile-bracket-audit64/verify.py
python3 -I -O -B research/profile-bracket-audit64/independent.py
python3 -I -O -B research/profile-bracket-audit64/controls.py
```

For another candidate local profile relative to the frozen PR589 baseline,
instantiate `ReferencePricer` once and call `compare_delta` with the exact
signed integer histogram change. Reuse the result only for pricing equal
deltas, not for identifying search states. Fixed m, W, replication and idle
profiles are essential; a changed pipeline needs a separate derivation.

## Sources, review and remaining scope

The separate checkout is based on
`ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`. The PR1048 research package at
`07730cd8302c378607259a9ad0efb73e0b57a2f2` and PR1182 package at
`0213b8911bfeefd5c81ddf320bac6a0fb7e86215` are retained byte-for-byte, including
licenses and notices. Their historical assertions are preserved as audit
evidence, not endorsed. All 24 fetched Git blobs and all seven dependencies
listed in PR1048's `EXPECTED.json` were verified locally. `SOURCE-PINS.json`
also binds the maintainer finding and selected record. `OVERLAP.json` records
the non-atomic read-only queue check through PR1190 and the distinct complex
provider scope of PR1186.

See `PROOF.md` for the comparison derivation, `REVIEW.md` for separate Astra
review/rerun, and `NOTICE.md` for full attribution. Brian Ross's Krenn
independent reconstruction and semantic-corruption methods and ThetaTwist
exact-arithmetic discipline are explicit methodological inspirations. No code
from either project is copied. Original search, supplier and counterexample
credit remains with flemhhh, woklerx, Douglas Colkitt, eumemic,
DreamingOfClouds and the retained lineage.

The following remain open: a complete independently justified first-state
domain; all second neighborhoods after every legal first frame and slot;
any completeness-preserving slot or frame pruning theorem; the separate
Steinberg family; other frame universes; candidate supplier/native admission;
all-size/compiler, hosting, precision and analytic obligations. No improving
candidate was found in the bounded slice. No full multiplication theorem,
global local-optimality result or original 645,900-pair exclusion follows.

Everything is local. The completed K492 package and PR1162 are preserved;
this task pushes nothing and creates no pull request.
