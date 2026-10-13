# Executed validation

Base `007664306fff84fbb1c9a1b4053b69f439764034`, macOS arm64, ordinary
CPython 3.12.14 with NumPy 2.3.5. The package is new and isolated;
no existing source, generator, selected record, or `upstream/` file is changed.

- Main exact block-table census: all 60 rows and 19,683 assignments pass the
  complete frozen receipt. Minimum 439; 2,646 minimizers.
- Independent set-valued full-vector census: every record matches the same
  SHA-256, `5598bbe4112493b6f6b55051a0364b7e576e253b8c2a85f8f05dcbb5d2ef7316`.
- Original generator: 59 completed word controls, 55 distinct receiver vectors,
  with 54 changing-block representatives plus five global controls. All helper
  counts, extra-carrier sets and new-junk counts agree. These use `NODEOPT=1`:
  lowering effort allocates no helpers, and no optimized ADD invoice is claimed.
- Separate AI model review ran 51 distinct original-generator variants covering
  all 60 local entries, and independently confirmed the failed-write, punctured
  response and carrier-reuse controls. This is not human peer review.
- Seven package tests pass. The minimal offline closure includes only this
  package and its twelve pinned inputs. Both full checkers pass there without
  Git or network access; before/after byte snapshots are identical. Source
  corruption, omitted pins, invalid receiver vectors, a numeric-type receipt
  mutation, and disabled Python assertions are rejected.
- Every consumed source file's SHA-256 and Git blob identity passes. All twelve
  Git blob identities separately match the exact base tree.
- The selected-record binding check and its 17 focused tests pass. An initial
  run rejected eight Python bytecode files generated during exploratory imports
  inside inventoried predecessor packages. They were removed, and both new
  entrypoints now disable bytecode writes before loading those packages. No
  source bytes or inventory expectations were changed to repair that failure.

The geometry/keeper-plan setup is shared pinned predecessor code. The independent
claim concerns receiver propagation, elimination and helper accounting, not
independently established E8 geometry. Original controls check their generator's
runtime assertions; they are not a new native or hosted supplier replay.
Full `make verify`, the selected complex cold replay, full changed-supplier
precision/hosting invoices, Linux or hosted CI, and formal theorem verification
were not performed. No performance improvement or new kappa is asserted.
