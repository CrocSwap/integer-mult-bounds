# Validation receipt

Local verification on 2026-10-13, CPython 3.14.7, macOS 27.0.1 arm64.
Base and submission-context main: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.

Completed commands:

```sh
python3 -I -O -B research/invariant-reader-restoration/verify.py
python3 -I -O -B research/invariant-reader-restoration/test_package.py
```

Outputs:

```text
PASS_INVARIANT_READER_RESTORATION cases=5832 wrapped_adds=210->150 no_new_kappa
PASS_READER_RESTORATION_PACKAGE relocation=1 deterministic_export=1 corruption_controls=8
```

The main command includes the separate symbolic/permutation checker: all 873
permutations of widths 1..6, complete source/workspace/output map, exact prefix
bounds and independently computed invoice. The all-input general statement is
proved in README.md; finite census and emitted-program checks are not a formal
proof-assistant theorem. Three narrowly scoped Codex agents helped with the
algebra, separate backend and independent symbolic audit; no human review claimed.

Certificate SHA256:
`08d6163fc8672667cb49ed9fa7cd1f6b68644450dae062e955c6932efe273862`.
The certificate also binds SOURCE-PINS.json; retained original source bytes and
Git blobs are verified. All 11 context-source SHA256 hashes were checked against
the untouched base checkout. Selected and upstream files are unchanged.

The first implementation was complete before the final verification phase.
Verification added the independently implemented symbolic checker, tested on-disk
fault rejection and clarified that the p+5 storage bound applies to integers.
No mathematical frontier claim was added. Orientation/selection used less than
the first eight minutes of the planned forty-minute cap, and final verification
and packaging began around 19:52 UTC, after the scoped construction was complete.

Live overlap checks: 786 open PRs at entry; 802 at the 19:54 UTC refresh, plus
the discussion board. PR1155 remained at
`9821c6e9388f3fc097e94b72be9fa7b41a849527`. The 19:54 refresh found no matching criterion, but the final pre-submission
refresh through #1199 found Sagar Thakrar's direct concurrent overlap. Its
pinned README was inspected, and the package was reframed as independent
corroboration with additional noncommuting, dirt-independent and tape coverage.
No priority for the correction or identity is claimed. Read PR889's shared-factor dirty fanout
and PR1012/#974's distinct hosted-cost notes for precise credit; their heads are
in SOURCE-PINS.json. No pinned issue existed, so coordination remained local as
the user instructed. No reservation issue was opened.

Not run or claimed: selected frontier cold replay, supplier adoption, shared
artifact regeneration, hosted CI, performance timing, full multiplication
formalization, or an optimized physical bit-tape implementation. These are
outside this isolated package. Exact online primitive/word-travel savings are
separate from the paid preparation term and any end-to-end runtime improvement.
