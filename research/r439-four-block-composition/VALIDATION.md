# Validation receipt

Completed locally on 2026-10-13 on Windows, CPython **3.14.5**. Native checks
used the existing **MSVC 19.51.36260** x64 compiler and **Boost 1.88.0** headers.
No packages were installed or global settings changed. Exact compiler/header
hashes and commands are in `NATIVE-ENVIRONMENT.json`.

## Completed checks

- `python -I -B research/r439-four-block-composition/verify.py`: all **16**
  subset words, **32** cover edges, all **661** dirty-input columns per word,
  full H1-H5/decomposition, all complete frame paths, emitted record semantics,
  exact cost/prefix bounds and **9** negative controls passed. The final
  native invocation also replayed this command and compared the complete
  deterministic `CERTIFICATE.json`.
- Independent `check_blocks.py`: **11,264** local Boolean inputs, exact local
  integer maps, reversed-positive domination, all **447** B participant
  columns and independent full-B splice construction passed. **298** entries
  strictly decrease in the combined reversed-positive matrix, none increases.
- `python -I -O -B research/r439-four-block-composition/test_package.py`:
  **5 tests passed**, 32.760 seconds on the final isolated worktree. They
  reproduce the full package with only declared inputs and no Git metadata;
  reject an altered subset receipt, corruption of all **13** execution/native
  source inputs, an omitted witness, four rehashed circuit corruptions, and
  an edit outside the claimed B slices. The same five tests previously passed
  without `-O` in 32.869 seconds.
- `python -I -B research/r439-four-block-composition/native.py`: fresh compiled
  legality and **5/9/11-stage** formal-column checks passed for both words.
  Column counts are **883/1327/1549** per word, with **96** bridge-omission
  controls rejected in total. The final run in the isolated worktree produced
  identical mathematical `NATIVE.json` to the first run. Its canonical JSON
  SHA-256 is `3cdf18f8d82e162d5d6909cd096f7863441f9f71dbd5a5547f71006eef50f580`.
  Canonical here means `json.dumps(value, sort_keys=True, separators=(",", ":"))`
  encoded as UTF-8, retaining every field. The environment receipt uses the
  same canonical form for its source-registry digest.
- `python -I -B scripts/verify_selected_result.py`: passed with unchanged
  selected `kappa = 1661960547713947/10^18` and source/proof-supplement inventory.

The final native run retained logs and generated words outside the checkout at
`F:\MEESEEKS MATH\r439-final-native`. Ordinary replay uses temporary storage;
these local paths are not needed to reproduce the contribution. In the
restricted sandbox, package tests needed TEMP/TMP redirected to an accessible
workspace directory; no source or mathematical assertion was altered for this.

## Development findings

An early source registry listed the frame508 nomination file while the
independent reader consumed its reviewed `CERTIFICATE.json`. The registry and
declared input list were corrected to the actually consumed file **before**
the isolated-source and final native runs. A later provenance-only addition
made the first environment receipt's registry digest outdated; the final native
run regenerated that environment evidence and reproduced identical mathematics.
An ad hoc changed-destination control was initially a no-op, was corrected to
change the destination, and then rejected. Committed controls make real edits.

Concurrent work changed the original shared checkout's branch. The contribution
was copied to a separate worktree at the same exact base and reverified there;
unrelated files and branches were not staged, reset or removed.

Git staging exposed CRLF-to-LF normalization of generated receipts. Final JSON
artifacts were normalized to UTF-8/LF, generators now request LF explicitly,
and the environment's registry digest was changed to canonical JSON so it is
independent of checkout line endings. The existing native mathematical receipt
was compared field for field with both fresh runs; only serialization and
environment digest metadata changed. The final local verifier was rerun after
this portability fix.

## Overlap and scope

The assignment/base is recorded in CLAIM.md. Immediately before packaging,
Curiosity Bot refreshed recent PRs through **#984**, including #973's distinct
frame509 and #980's phase-A admission work. No competing four-block composition
was found in those results or the R439 composition query; this is a bounded
metadata check, not a claim to have exhaustively reviewed every open PR.
Fetched `origin/main` was `55645f9d4d806d67875c1c8b9840b0b039ece22e`; its changes
since the base do not alter the consumed supplier/checker or four predecessor
directories. The contribution retains its exact original base.

No global source generator or selected construction is changed, so validation
is the affected isolated package plus selected-record integrity, not a repeat
of expensive unrelated `make verify`/selected complex ancestry regeneration.
The full hosted parent invoice, supplier adoption and outer assembly were not
run. No Linux CI, Lean multiplication proof, unrestricted circuit optimum,
new bit exponent or new kappa is claimed. Inherited assumptions are listed in
README.md. Review and independent replay were AI-assisted; no human review is
implied.
