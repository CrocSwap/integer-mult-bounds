# Executed validation

Linux x86_64, CPython 3.12.14, 13 October 2026. Exact base:
`007664306fff84fbb1c9a1b4053b69f439764034`.

- `python3 -I -O -B research/jp8-direct-small-integers/verify.py --write NEW_PATH`
  generated the exact receipt; the same command without `--write` compares it.
- Both complete primitive projections passed all 725 formal input columns at
  every macro boundary and at the final expected shear. The source pin and
  SPEC/program bindings passed. All 1,424 replacements in each orientation
  were checked, with cost/access counts and unchanged prefix/grid metrics.
- All 13 dense mathematical/interface rejection controls passed, alongside
  four early-clear positives and four reduced-coefficient positives.
- `python3 -I -O -B research/jp8-direct-small-integers/test_package.py`:
  **6 tests passed** in 11.194 seconds. Includes 3,000 integer-row arithmetic
  crosschecks, source corruption, gzip recompression, optimized minimal offline
  relocation in a path with spaces, typed-receipt corruption and existing-output
  preservation. The timing is a local test duration, not a performance claim.
- `make selected-record-check`: passed, selected conditional kappa remains
  `1661957774647029/1000000000000000000`.
- `python3 -B -m unittest discover -s tests -p 'test_selected_result.py' -v`:
  **5 existing tests passed** in 0.740 seconds.

No existing generator, production lowerer, selected artifact, workflow or
upstream source is modified. Full `make verify`, native physical/phase/owner
replay, cold supplier reconstruction, global invoice/assembly, Lean, a second
platform and hosted CI were not run. Their inherited scope is not represented
as newly verified. Relevant focused checks are used for this isolated package.

Final patch application, clean export and whitespace results are recorded in
`HANDOFF.md`. `OVERLAP.json` records the final metadata refresh and exact heads.

## Requested second audit, 13 October 2026

Reviewed the actual published PR1223 head
`86381e9adf3c9d1e958cca4d53fec15254190434`, tree
`0166b06587244338e81d81635892e5cff7ecd12e`, in a separate worktree. Its content
exactly matched the previously tested local tree. No error was found in the
claimed finite scalar construction; the candidate lowerer, primary checker,
source pins and exact receipt remain unchanged.

- Repeated the optimized isolated primary checker: the same pass line and exact
  receipt, including all 13 local rejection controls.
- Repeated `test_package.py`: six tests passed in 10.457 seconds.
- Repeated `make selected-record-check` and the five `test_selected_result.py`
  tests at the exact original base: all passed. These are checks of that pinned
  base's selected record, not a new replay of the later PR1094 construction.
- Independently compared all six recorded Git blob identities against the
  original base. Their exact or decompressed payloads also match refreshed main
  `49b3157d1d89adcef16df8be98445451672be5ba`, which still selects conditional
  PR1094, kappa `836330098538459/500000000000000000`.
- Added `recheck_fraction.py`, a second full scalar interpreter using native
  Fraction coefficients. It imports neither the primary checker nor its row
  arithmetic/controls. The two programs, their lowerers and the receipt are
  shared inputs. It checks the complete register state on all 725 formal input
  columns at every one of the 22,693 macro boundaries per orientation.
- Both Fraction replays matched **every program receipt field**: all changed
  event IDs, coefficient/frame/phase counts, paid profiles, stream digests,
  exact prefix norms and denominator depths, source/operand reads and complete
  primitive counts. The result remains **2,848 saved real primitives per
  orientation**. The first complete run took 92.212 seconds on this environment;
  this is a verification duration, not a circuit runtime claim.
- Seven additional controls check four wrong-endpoint/dirty-work mutations and
  three endpoint-preserving changes to fractional depth, magnitude or cost.
  The latter require the corresponding measured metric to increase, rather
  than merely relying on a changed stream hash.
- Rechecked Python syntax, JSON parsing, whitespace, the exact changed-path
  inventory and preservation of `upstream/`. Reviewed the elementary identity,
  arbitrary-dirty work contract, convexity/grid arguments, access counts and
  limitation statements. PR999 and PR1036 remain open at the credited heads.
- Finally exported just the twelve package files plus six pinned inputs into a
  fresh directory with spaces and no Git metadata. All three commands passed
  there under `-I -O -B`: primary replay 4.879 seconds, package tests 10.145
  seconds (six passing tests), complete Fraction replay 90.592 seconds. The
  final Fraction checker SHA-256 is
  `6285545407e210a7059a70a9201724dc94f032abd340a4afbbeb4e790350b370`.

Reproduce the added check with:

```sh
python3 -I -O -B research/jp8-direct-small-integers/recheck_fraction.py
```

Expected final line:
`PASS_JP8_FRACTION_RECHECK all_program_receipt_fields=equal no_new_kappa`.

PR1223's six hosted workflow runs reported `action_required`; no hosted test
success is claimed. The second audit does not discharge physical-frame,
whole-call, cold supplier, global invoice/assembly or analytic obligations, and
does not constitute independent human review or a full multiplication proof.
