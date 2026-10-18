# Executed validation and limits

Executed 2026-10-13 on macOS 27.0.1 arm64. Exact base:
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. All changes are confined to
`research/dyadic-query-pair/`. The existing PR756/PR805 branches and their
worktrees were not modified. The primary checkout was rechecked at
`4fad623a1e4ca06959f4326e221c2f8d9125c269` on its PR756 branch.

## Scoped package

Final `verify.py` replays passed with identical complete committed evidence:

- CPython **3.13.2**, isolated ordinary replay `python3 -I -B .../verify.py`.
- CPython **3.13.2**, isolated optimized replay and exact regeneration
  `python3 -I -O -B .../verify.py --emit /absolute/new/directory`.
- CPython **3.12.14**, `python3.12 -I -O -B .../verify.py`.
- CPython **3.9.6**, `/usr/bin/python3 -I -O -B .../verify.py`.

All use the standard library only. The committed certificate is compared
as canonical JSON, including every count, stream digest and source binding;
integer/Boolean substitutions are distinct.

Completed finite coverage:

- **112** signed dyadic ADDRESS words, indices 0 through 55, with literal
  inverses and eight independent rational basis columns: **1,792** columns.
  The index-55 check explicitly covers the doubled query of the seed-selected
  index-54 pair. Nine odd moduli give **16,128** modular columns.
- **110** signed symbolic pair programs (indices 0 through 54), each with
  complete baseline/fused/inverse Laurent VALUE matrices.
- Independent outer-product and literal-matrix catalogues at dimensions 2,
  3, 4 have 6, 28, 120 rank-one projectors. All **91,320** ordered products
  with opposite exponents +/-1,+/-2,+/-4 reject the centered target. The
  all-dimension/all-power result is the written proof, not this census.
- Full six-field domains have **729 addresses over Z/3** (243 fixed) and
  **15,625 over Z/5** (3,125 fixed). The declared parameters in CERTIFICATE
  give **154,160 dirty four-role basis columns per program**, with baseline
  and fused endpoints checked against a direct coordinate formula, and
  **308,320** literal inverse/completed-involution column checks. Two
  ADDRESS spectators are fixed at values 1 and 2; their arbitrary-coordinate
  identity is separately covered by the rational/modular columns and proof.
- Ten full/shorter/fixed prime-power orbit domains give **7,552** further
  basis columns per program and **15,104** inverse/involution checks.
  **92** simultaneous nonzero dirty-row cases also pass.
- All **25** declared mathematical/admission controls pass, including
  each single ADDRESS/fused event omission, query direction/power/source
  errors, source/target aliasing and dirty-spectator destruction.

`check_package.py` passes on the final certificate under CPython 3.13.2.
Its copied directory contains spaces and has no repository/Git context.
An isolated optimized offline replay passes. All **six** deliberate faults
fail at their declared predicate: immutable source drift, missing source
inventory, integer-zero-to-Boolean substitution, an unpaid child receipt,
central query-power corruption, and implementation/source-binding drift.
Original workspace bytes are not changed by these controls.

Every one of the **seven** vendored immutable inputs was additionally compared
byte for byte to its fetched pinned Git object. Both Git blob SHA-1 and SHA-256
checks are performed in every standalone replay. Licenses and notices remain
unchanged. `make selected-record-check` passes for exact conditional kappa
`1661202643272239/1000000000000000000`. Staged whitespace checks pass, and
the diff contains no changes to upstream, certificates, scripts, tests or docs.

One root `PYTHONDONTWRITEBYTECODE=1 make verify` was run on an **untouched
Git-archive export of the exact base**, so unrelated generated artifacts
did not enter this worktree. Its seven initial historical groups passed:
`verify-community`, `verify-producers`, `verify-partial-gauge`,
`verify-three-stage-cover`, `verify-paired-cube`, `verify-recycled-bit`,
and `verify-entrance-banks`. It then stopped at `gen4-bank-verify`:

```text
ModuleNotFoundError: No module named 'sympy'
make[1]: *** [gen4-bank-verify] Error 1
make: *** [verify] Error 2
```

Exit status was 2. No full repository-suite pass is claimed. The selected
PR741 cold replay and subsequent root groups were not reached. The refreshed
PR799 construction was read as publication context; its cold replay was
not run. No dependency installation or source workaround was attempted for
this isolated standard-library contribution.

## Review boundary

The executable child denotes the inherited ordinary full-row ADDRESS
interchange contract. The finite evaluator swaps address coordinates to
check its specified permutation; it is not a new recursive supplier or
fixed-tape implementation. The two independently written coordinate/matrix
references are computationally separate methods prepared with the same
substantial AI assistance, not independent human reviews.

Three queries are sharp only in the stated power-query/XOR model. The work
recurrence is typed: a centered DATA shear invokes ordinary ADDRESS
interchange. It cannot be turned into a self-recursion without an additional
compiler. j-dependent coefficient costs, physical routing/hosting, all-size
padding, actual supplier/assembly invoices and inherited tape/analytic
assumptions remain. No new kappa, runtime benchmark, Linux/remote CI result,
proof-assistant pass or full multiplication theorem is claimed.
