# Sprint claim — agent-08 (verification engineering, seed 85)

- Track: 85–94 verification engineering (OS random seed 85, drawn 2026-10-13
  from `RandomNumberGenerator` on this host).
- Base commit: `91a2094f2e022930069e8cfdc810a3ea1b81cd09` (origin/main at start).
- Branch: `research/agent-08-verifeng-seed85`.
- No pinned sprint coordination issue exists (only #650 and #913 are open), so
  this claim is recorded locally, per the task instructions.

## Object being investigated

Locale dependence of the offline verification entry points in `make verify`:
two members of the suite (`ranked-pair-check` and `machine-transfer-check`)
decode UTF-8 proof sources with the platform locale codec
(`Path.read_text()` without `encoding=`), so they fail on Windows/cp1252 and
would fail under any non-UTF-8 locale, while passing on UTF-8 (Linux) hosts.
The mathematical checks themselves are locale-independent; only text decoding
is not.

## Three candidate tasks considered (track 85–94)

1. Locale independence of the offline verification entry points (chosen).
2. Accelerate the unclaimed `verify-research` tier (`audit_mixed_point` 53.8 s,
   `audit_parity_side` 48.3 s, `audit_early_sharing` 45.5 s,
   `audit_bit_compression` 41.2 s, `audit_inplace_side` 30.9 s on this host).
   Declined: the same track's speedup method is already mined by #752/#824/
   #853/#921 and neighbours; fixing a failing check is the more useful,
   underexplored object.
3. Speed up `scripts/verify_supplier_consolidation.py --component-tests`
   (48.9 s). Declined as the narrower version of candidate 2.

## Method and scope

- Static inventory of locale-dependent text I/O across the verification
  surface, with hash-pin status per affected file.
- Minimal fixes: explicit UTF-8 where sources are not hash-pinned; UTF-8 mode
  at the invocation boundary where package bytes are frozen by a publication
  manifest. No mathematical content, certificate, or pinned byte changes.
- A regression guard that runs the affected checks under a hostile
  (non-UTF-8) locale and requires byte-identical receipts.

## Expected deliverable

A focused PR labelled **tooling improvement (verification reproducibility)**:
fixes + guard test + evidence package + before/after receipts. No new kappa.

## Expected finish

Within this session (target: complete before the verification window).

## Outcome (recorded at completion)

Delivered as claimed. Root causes: locale-dependent `Path.read_text()` in two
offline checks (hard failures on non-UTF-8 hosts) and unpinned text writes in
the `scripts/` generators (CRLF-translated certificates, 39/39 byte-different
on Windows). Fixes: `export PYTHONUTF8=1` in the Makefile, explicit UTF-8 in
the unpinned `ranked-pair-verification` chain, and `encoding='utf-8',
newline='\n'` on 139 write sites in 126 `scripts/` files (mechanical, ast
codemod). 27 certificates regenerated with digest-only diffs; 43 frontier- or
receipt-frozen scripts skipped; three first-pass edits reverted after the
freeze detector caught binding receipt pins. Four regression guards added in
`tests/test_locale_reproducibility.py`; full isolated suite failing set equals
the recorded base-commit environmental set. See the package README for scope
and residual obligations.
