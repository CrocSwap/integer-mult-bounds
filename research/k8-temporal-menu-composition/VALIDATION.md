# Validation

Validated on 2026-10-13 (America/New_York), using CPython 3.12.15 on macOS arm64,
standard library only, assertions enabled. All checks below passed.

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/k8-temporal-menu-composition
```

The registered runner checked metadata and pinned upstream Git objects, then ran
the explicit `-I -B` verifier command in VERIFY.json. It reported
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_FIXED19_MENU_COMPOSITION`.

The verifier established 134070/134086 complex primitives, the exact two shared
interaction corrections, strictly negative worst-case addition marginals, and
all 712 formal scalar columns in each orientation. It reproduced the static and
PR1388 pair comparators, checked all sixteen directly emitted subsets of the four
helpers with nonzero cross terms, and rejected removal of a recorded inserted SCALE.

A separate integration check copied the complete package to a read-only directory,
ran it from an unrelated working directory with explicit `--upstream` and fresh
`--output`, checked the resulting costs/endpoints, and compared every file hash
before and after. No package file changed or appeared. That replay took about
5.1 seconds. Additional checks confirmed rejection of an existing output path,
optimized Python (`-O`), and a changed MENU.json before source imports. The result
SHA-256 was `b76271a6ed334146a3b4abb05314db23299ae7c252edc5bb4bf737f406b7a4f2`.

The original bounded scientific run additionally checked all 524288 fixed-menu
subsets per orientation by independent Gray-code and least-set-bit recurrences.
EXPECTED.json retains that result. Routine registered replay proves optimality
with the strict marginal argument and does not repeat exponential enumeration;
`--exhaustive` remains available for that optional check.

The eight vendored files were independently checked against their recorded SHA-256
and Git blob identities. The native-cost boundary was checked against four pinned
upstream source blobs and the retained archive receipt leaves. This was a source
and receipt review, not a new native execution.

Ody reviewed the integrated proof, verifier, provenance, metadata and native
boundary without edits or running the checker, and reported no blocking finding.
This is additional AI review, not independent human review. Full native, adapter,
controller, owner and hosted admission remain unrun and unproved for this composed
program; no κ improvement is claimed.
