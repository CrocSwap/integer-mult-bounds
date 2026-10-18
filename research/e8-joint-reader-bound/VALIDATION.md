# Validation and review handoff

Validated on 14 October 2026 (Australia/Melbourne), on macOS with CPython
3.14.6 and CPython 3.12.12. All arithmetic is exact and uses the standard
library. The two new implementations and proof received separate
AI-assisted review; no independent human or proof-assistant review is claimed.

## Completed checks

```sh
python3 -I -B research/e8-joint-reader-bound/verify.py
python3 -I -O -B research/e8-joint-reader-bound/independent_check.py
python3 -I -B research/e8-joint-reader-bound/test_package.py
python3.12 -I -B research/e8-joint-reader-bound/verify.py
python3.12 -I -O -B research/e8-joint-reader-bound/independent_check.py
make selected-record-check
git diff --check
```

- Primary: PASS; all 256 standard flats, 511 nonzero reader words, all
  130,305 distinct reader pairs, eight Weyl generators, nine exact
  single-reader threshold witnesses, and 56 puncture budgets.
- Independent: PASS; alternate root ordering, normalized Fraction RREF,
  direct root-span membership, weight/XOR pair-union calculation, and
  486,200 complete sorted-rank profile visits. Four independent rejection
  controls pass. Comparison is limited to `independent_summary`.
- Package tests: **5/5 PASS**, including both new scripts in isolated
  optimized mode after relocation to a path with spaces, byte-identical
  regeneration, corrupted-cost rejection, corrupted-capacity rejection
  by both engines, and corrupted-source rejection before output overwrite.
- The fifth package test replays pinned PR631 with its negative controls.
  Its sharp thresholds, nine-puncture attaining example and <=35 theorem
  checks pass. Its intentional optimized-mode refusal also passes.
- The primary's six rejection controls distinguish individual-reader
  failure from shared-deletion incompatibility; valid relaxed profiles
  at budgets 44 and 52 are accepted, without claiming realizability.
- A 56-puncture positive boundary control makes the live code rank eight,
  justifying the stopping boundary rather than extrapolating the theorem.
- All three retained source files match GitHub Git blob IDs as well as
  local SHA256 digests. No predecessor implementation is imported by
  either new checker.
- A staged Git-tree export passes both new checkers under `-I -O -B`
  and regenerates a byte-identical certificate. This checks the exact
  staged package without relying on other checkout files.
- Selected-record integrity passes on the exact task base, with its
  PR799 conditional kappa `1661634653669567/10^18`.

## Provenance and current upstream context

Original base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
The PR631 dependency is pinned to
`fb893b5ee1317c2da3b297e6fe78eca0857d1a76`; PR875 attribution/context is
pinned to `7f334e4c749fd83d03feb6c1de4e4cda9534c9dc`.

During final verification upstream advanced to
`47481c89fd30a43f8f882eb4b391e89c29273fd0`, selecting PR890 at conditional
kappa `1661957774647029/10^18`. Its selected record, current status, review
and T21 construction proof were inspected. That new frontier is not a
dependency of this root-only structural result. The base provenance is
retained accurately rather than relabeling it as the newer commit.
There was no existing upstream directory at our package path.

The final complete metadata inventory contained 706 open PRs through #934
(the earlier inventory had 724; eighteen were integrated). Both direct
predecessor heads remained unchanged. No pinned coordination issue existed
at either check. Relevant heads and the scope comparison are in
[OVERLAP.json](OVERLAP.json). The claim and one result update are local.

## Limits

The finite checks do not enumerate all deletion sets or formally prove
the parabolic-flat argument. The written coverage proof is essential.
The primary certificate uses the inherited small-puncture result for
budgets 0–8; its source and replay are explicitly included above.

No existing generator, supplier, selected certificate or upstream source
is changed. The expensive repository-wide `make verify` and selected
supplier cold replay were not rerun for this isolated research package.
No hosted CI pass, new kappa, paid supplier or complete multiplication
theorem is claimed.
