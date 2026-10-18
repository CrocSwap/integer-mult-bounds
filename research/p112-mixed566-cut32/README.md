# A universal mixed-rank P112 common-cut32 contract

For any characteristic-zero field and ONE arbitrary common cut of at most
32 P112 coordinates, three residual pieces of binary support ranks at most
5,6,6 meet the restricted root code in dimension at most one. The theorem is
conditional on the pinned geometry, support capacities and PR3295's full-axis
concentration lemma. [PROOF.md](PROOF.md) gives the argument and dependencies.

The new step forces all three pieces onto two D6 axes. They cover at most
49 or 51 retained coordinates, where at least 50 or 52 are required. The E6
branch has the strict incidence gap 86 < 92. This strengthens the inherited
uniform-rank-six cut29 statement for this mixed profile. Sharpness is unclaimed.

PR3295 already excludes the historical `4,5^3,6^6` caller through its distinct
six-piece concentration theorem. That is prior evidence, not a new exclusion
here. The initial caller-novelty candidate was withdrawn before computation
after reading that actual public successor. This package proves a universal
arbitrary-cut implication and claims no new caller count or kappa.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-mixed566-cut32
```

The same three registered commands work directly in a Git-free export:

```sh
python3 -W error -B research/p112-mixed566-cut32/verify.py
python3 -W error -B research/p112-mixed566-cut32/independent.py
python3 -W error -O -B research/p112-mixed566-cut32/test_verify.py
```

Set TMPDIR and PYTHONPYCACHEPREFIX to private writable directories when
running from a read-only export. Tests create writable private copies by
writing fresh file bytes; they never chmod retained inputs or follow links.

The primary checker authenticates the inherited proof and finite receipts,
then checks the new incidence arithmetic and sixteen axis assignments. The
second arithmetic implementation enumerates all 91,728 integer occupancy
relaxations. These are upper bounds on coverage, not achieved root geometry.
Controls reject a changed receipt, corrupt geometry or predecessor proof,
schema booleans, added source rows and input-to-provenance relabelling. The
actual verifier process also rejects a private corrupt source.

PREDECESSORS.json retains exact PR3295 head, original paths, Git blobs and
SHA256 hashes. Its three payloads are byte-identical; fresh CI needs no pending
PR Git objects. The generic SOURCES.json binds the baseline and live geometry.
Fixed manifest hashes prevent inventory, usage or schema changes from silently
altering the source contract. JSON comparisons preserve bool/int distinctions.

Authentication is not mathematical admission. The global capacities, E6 joint
bounds, D6 plane inventory, concentration/transport checks and standard Weyl
theorem remain inherited. Their historical suites, selected cold replay,
Lean, Docker, independent human and proof-kernel review are unrun. No full C5,
global decoder floor, physical/native/restoration/consumer construction,
supplier or multiplication theorem is claimed.

## Scope and implementation choices

The revision6 card's local-word ceiling positive control passed. This is a
scoped proof side result, not its 5% supplier target. The expansion decision is
to finish this one implication and stop. Physical and consumer costs remain
unknown and are not assigned zero.

Separate Before Serializing Shared State gave the work its own package,
branch, cache and status; brief shared metadata operations use OS locks.
Prove It Works requires actual committed Git-free replay before freeze.
Power of Ten deviations are limited to Python's managed allocation, standard
library iteration and the test's bounded failure callbacks. Live input files
are bounded by 100,000 bytes, source rows by four, axis assignments by eight
per plane type and occupancy cases by 91,728. Validation uses exceptions under
optimization. No historical source code is executed or changed. Functions
remain below 60 lines after formatting. Checks and limits are in CHECKS.json.

## Open next questions

Does cut33 hold for ranks5,6,6? Inspect union82 configurations with singleton
lower bounds9,17,17. The current concentration premise is not forced there;
the losing arithmetic control is not a counterexample or a sharpness proof.

Which currently uncovered literal caller needs this exact contract? Refresh
the caller ledger and certify one common cut and its surviving code dimension.
PR3295 already supplies the motivating caller exclusion. Structured relevance,
first steps and blockers are in TASK.json. No further task is reserved.

Canonical investigation: [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19004309).

Credit Nick Petalas/PR3295 and the retained PR3278/3267/3260/3262/3269 source
chain, DreamingOfClouds/PR3154 and the E8/P112 lineage including joaqcoo.
Frozen predecessor bytes and the selected result remain unchanged. Apache-2.0.
