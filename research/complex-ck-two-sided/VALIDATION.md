# Validation and handoff

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Environment: macOS 26.5.2 arm64; CPython **3.14.6**; standard library only.
No Linux or hosted-CI pass is implied by these local checks.

## Executed checks

- `python3 -I -B research/complex-ck-two-sided/verify.py`: complete deterministic
  recipe/receipt reproduction. All 12,544 target-edge prices and 128,524 helper
  cases completed. Separate Prim/census arithmetic agrees.
- Both original and replacement full scalar programs pass on 716 logical plus
  nine arbitrary private input columns, under Fraction and separate integer
  dyadic arithmetic. Complete counts are 224,938 -> 149,620 and
  224,986 -> 149,668. Native emitter output equals the constructed programs.
  Both engines also agree that every intermediate symbolic coefficient needs
  at most 3 forward / 8 backward binary denominator bits, unchanged from baseline.
- Unchanged inherited native audit passes both 716-column frame/wrapper checks,
  unchanged paid profiles, and all **25** original negative controls.
- **10** new controls detect omitted target/helper preparation or restoration,
  wrong helper or residual sign, reversed target order, illegal wrapped-helper
  access and omitted initial dirty-work clear. The illegal-helper control
  preserves source count and checks the exact rejection reason. Omitted target
  preparation deliberately passes helper-only checking and fails full checking.
- `python3 -I -B research/complex-ck-two-sided/test_package.py`: **7 tests pass**,
  including every emitted coefficient on arbitrary source/target/work, source
  mutation/removal, recompression, non-scalar preservation and bad recipe costs.
- `python3 -I -B research/complex-ck-two-sided/test_independent.py`: **6 tests
  pass**, covering exact dyadic arithmetic, private dirt, copy aliasing, restored
  helpers and malformed instructions.
- All three commands also pass with `-O`; inherited native subprocesses use
  isolated mode without `-O`, retaining their assertion-based checks.
- A minimal source closure at a temporary path containing spaces passes from
  outside the checkout, after recompressing the program input. A typed receipt
  mutation and a helper-gain recipe mutation are rejected; verification leaves
  existing output bytes unchanged, including on failure.
- `make selected-record-check` and the five tests in
  `tests/test_selected_result.py` pass on the unchanged selected PR799 record.

The exact reproducible results are in `EXPECTED.json`; source and predecessor
pins are in `SOURCES.json`. Compression container changes are deliberately
accepted only when the decompressed source payload is unchanged.

## Scope

Only this research directory is added. `upstream/`, selected-result records,
existing generators, unrelated artifacts and predecessor implementations are
unchanged. Full repository `make verify`, full cold construction rebuilding,
global hosting/invoice/assembly admission and Lean are not claimed. The relevant
checks here establish the finite compensation rewrite and native local interface;
the selected production construction has not been modified.

Current main was fetched unchanged during the pre-submission overlap check.
The final complete snapshot contained 705 open PRs through #915. Exact heads for
PR807/816 remain those in `SOURCES.json`. No pinned sprint issue exists, so the
claim and result are local. No matching two-sided CK work was found. PR816's
standalone target-forest minimum is independently corroborated; this adds helper
changes *after* that transformation, with a full recomputed cost and replay.

Production adoption still needs a typed alternative-compensation step and new
source bindings, complete global invoices and admission. Neither the historical
CK checkpoint nor current X4 selection receives a new κ from this package.
