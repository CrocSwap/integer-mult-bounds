# Validation record

Executed 2026-10-16 with CPython 3.12.14 (Clang 22.1.3), macOS 26.5.2,
arm64, standard library only. This is local scoped evidence, not hosted CI,
independent human review, formal-kernel verification or full supplier admission.

## Source and task bindings

The session started at 12:53:46 UTC. The isolated branch is based on canonical
main `d112c69dcfae71849feb8ffdb463b244c16db545`. `AGENTS.md`, `autoresearch.md`
and `CONTRIBUTING.md` were read before choosing the task. The single successful
picker draw, selected card, original scope, refinement, exact catalogue pins,
60-minute budget and overlap limitations are recorded in `TASK.json`.

`scripts/research_baseline.py` returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
The selected record remains `836330098538459/500000000000000000`, with
`make frontier1094-verify` as its full replay. That full replay was not run:
this package neither modifies nor re-admits the selected construction.

All eight frozen inputs match actual Git blobs from PR2930 at
`81f3b5d12977eba09e06fbff729167d59faabe90`; byte lengths, SHA256 values and
Git blob IDs are in `INPUTS.json`. The verifier seals that manifest itself and
rejects added/missing inputs, symlinks and malformed JSON before mathematics.
The predecessor's Python files are documentary definitions and are not imported.

At the 13:18 UTC refresh, canonical main was
`0d747bd0d48315856267d8896a1fa6e77f944784`. All three guidance files, the
revision-5 task catalogue and selected record retained their original blob IDs.
The latest PR bodies through PR2942 and the current Discussion2612 comments
were inspected. PR2930's head was unchanged. PR2942 changes the inventory;
its stronger reported headline is outside this certificate. The original
472-open-PR snapshot was fully paginated; the later refresh covered the newest
100 open PRs. Discussion coverage is manual and incomplete across the board,
and neither snapshot certifies novelty or unpublished-work absence.

## Exact replay

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/paired-cap-uniform-optimality
python3.12 -I -O -B research/paired-cap-uniform-optimality/test_verify.py
```

The registered runner passes all three declared commands: ordinary verifier,
optimized verifier and the 17 test groups. The same 17 groups pass separately
with optimization. Acceptance checks do not depend on Python `assert`.

The mathematical receipt is identical in both modes:

```text
PASS_PAIRED_CAP_UNIFORM_OPTIMALITY
canonical receipt SHA256:
360876fceabd1a8f922a1e441d4224479de5b48fe62ae51ecfc02bd4ca6e91d5
reduced-cost records SHA256:
c6fc9248644baa279e696d5f97ac52b6c823a262dc655dc720c0fa6b71d8210d
```

It proves the nine primal equations, complete-profile equality, conserved mass,
all 1,163 symbolic reduced costs, 11 exact equalities, 1,152 strict uniform
inequalities greater than `1/250`, and both strict root endpoint signs.
The README supplies the weak-duality and unique-root argument needed to turn
these inequalities into exact optimality at the unknown root.

## Portability and failure controls

A separate package-only export, without Git or repository files, was made
read-only (files 0444, directories 0555). From an unrelated working directory,
ordinary and optimized `verify.py` and `test_verify.py` all passed. Whole emitted
JSON bytes from `verify.py --emit` matched between modes; their SHA256 is
`c7b7023580fa721b02301e50f367ef81d2720221a5a96f2929fcee4dbb6aa310`.
The complete exported file inventory and hashes were unchanged afterward.

The first read-only test run exposed fixture copies retaining read-only modes.
The test harness now makes only its newly created temporary mutation copies
writable; the exported inputs remain read-only. The repeated run passed. A final CLI check also caught a trailing status line in
`--emit`; it now emits exactly one parseable JSON document, covered by its own test.

Controls include independent Cartesian enumeration, exact rational square-root
calibrations, over-capacity/unknown-width and singular/duplicate bases,
fractional/negative/boolean counts, same-mass profile corruption, invalid
brackets, strict JSON, warm-cache type rejection, source/manifest/inventory
corruption and numerically equal but wrongly typed receipt corruption.
A deliberately broad interval is rejected by the conservative enclosure;
this does not assert that the true dual becomes infeasible on that interval.

## Separate cross-checks and limits

An independent AI-assisted derivation used nondecreasing multisets, rational
elimination, a direct 2,048-term atanh logarithm series and a 32-term exponential
Taylor enclosure. It imported neither this package nor predecessor code. It
agreed on all 1,163 patterns, the nine dual entries, 11 tight types, the complete
profile, the strict `1/250` uniform margin and both endpoint signs. A separate
read-through found no mathematical defect. This is supplementary internal
review; the portable public evidence is the proof and checker in this package.

Separately running the original pinned PR2930 `check_cap.py` returned
`PASS_LITERAL_ALLOCATION_ATTAINS_FIXED_INVENTORY_CAP`. That is a reproduction
of the primary cap checker, not an independent owner/native/supplier replay.

Literal owner-window reconstruction, chronological realization, native operator
identities, buffer and physical-stock semantics, precision/tape, full supplier
and outer admission, all-size/compiler and analytic hypotheses remain outside
scope. The source local profile and inventory derivation remain inherited.
No allocation search, new kappa, selected-frontier change or universal packing
barrier is claimed. Human/maintainer review and hosted CI remain separate.
