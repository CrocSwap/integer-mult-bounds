# Validation and handoff

Author-checked on 2026-10-15 UTC; substantial OpenAI Codex assistance.
There has been no independent human review or Lean build of this argument.

## Executed checks

The registered package command passed on CPython **3.12.13**, macOS 27.0.1
arm64:

```sh
python3.12 scripts/research_package.py --package research/split-minmax-audit-seed63
```

Both registered commands (`-I -B` and `-I -O -B`) reproduced `EXPECTED.json`
exactly and ended with
`PASS_REGISTERED_RESEARCH_PACKAGE research/split-minmax-audit-seed63 outcome=completed`.
The metadata/provenance-only check also passed. The initial receipt was
generated and replayed on CPython 3.14.5 with the same result.

Finite evidence is 70,337 input parameterizations, 4,656 distinct block tuples,
8,701 inputs satisfying the principal-cost premise, and twelve mathematical
or certificate controls. The certificate-stream SHA256 is
`c5392a336076d070f9be63a7f3b003a552c677c5f9d525c50078427cb7224c57`.
The general result is the written theorem application in `PROOF.md`, rather
than an inference from those finite cases.

An additional local packaging check copied the package to a temporary directory
outside the repository and replayed it successfully (0.7147 seconds). Appending
bytes to the retained source excerpt was rejected with
`audited statement digest mismatch`; changing the expected input count to zero
was rejected with `finite receipt mismatch`. Both corruptions were rejected in
normal and optimized Python. These four failure runs were confined to temporary
copies. Exact environment and exit results are in `VALIDATION.json`.

## Source and proof review

The audited statement is PR2162 head
`113a718265c62aec301c5695f4bfb9c421bef7ab`, README Git blob
`1f4ae89f74c1318d95e25e8e1f56bd66405f0b48`, SHA256
`c30690ef0cf30e6d845f2e997bfae289cfa5c52451cabf8b102011d08e62e951`.
Its head was checked again before submission and had not changed.

Schrijver's 1979 paper was checked at its primary CWI archive. Theorem 3.6 is
on printed pp. 363–364; its PDF hash and immutable bibliographic reference are
in `SOURCES.json`. The paper is not redistributed. The proof review checked
the independent row/column universes, the two partition matroids, the
block-diagonal nonsingular-minor reduction, saturation of whole copy groups,
nonempty-support completion, and the principal-restriction quantifiers.

This confirms the quoted identity and its universal corollary. It does not
prove target (A) for three-total rational decoders, provide a physical decoder,
or discharge the selected multiplication construction's all-size/compiler,
hosting, precision/tape, bit H1–H5 or analytic assumptions. No selected cold
replay was required or attempted: only this new package is changed.

## Coordination and final freshness

The exact base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected
record, actual PR1094 construction, source manifest and maintainer review were
read. The accepted conditional κ is `0.001672660197076918`.

There was no pinned sprint issue. The canonical
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18941432)
was posted in the repository's handoff discussion after checking its newest
comments. The pre-claim complete index covered 539 open PRs and 1,036
Discussions; the exact min–max matches were PR2162 and PR2293 plus its handoff.
PR2293 explicitly excludes this identity from its checked scope. Other active
jet and anti-Fano work addresses different implications.

Canonical main was fetched again before submission and remained at the exact
base above. Its guidance, priority revision 4 and selected result were
unchanged. Final live overlap coverage and refresh timestamps are recorded in
`VALIDATION.json`. The package is self-contained for finite replay, and its
two open next questions are in `TASK.json` and `README.md`.
