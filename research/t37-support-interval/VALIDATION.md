# Validation record

Date: 2026-10-13.
Base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
Environment: macOS, CPython 3.9.6, standard library only.
Status: mathematical research note; no new kappa and no external human review.

## Mathematical review

The theorem quantifies over every positive integer replica count and every real saving exponent in its stated interval.
The proof derives the necessary relaxation from the fixed inventory, then proves a uniform supporting inequality.
Strict concavity gives the unique boundary and all equality cases.
An explicit relaxed profile proves sharpness beyond that boundary.

A separate monotone-ratio argument checks the continuum inference.
The finite premises pass with two distinct enumeration methods and two distinct arithmetic enclosure methods.
`METHODS.md` gives their coverage and error arguments.
The same Codex-assisted author prepared both implementations; we claim no separate reviewer.

## Executed checks

The command in `README.md` produces the three committed JSON receipts in `data/`.
It reports these results:

```text
PASS_SHARP_T37_SUPPORT_INTERVAL bins=1163 critical_rank=32 16/25 < b_star < 13/20
PASS_INDEPENDENT_T37_SUPPORT_INTERVAL
PASS_T37_SUPPORT_SEMANTIC_CONTROLS negative=13 positive=4
PASS_T37_SUPPORT_INTERVAL_REPRODUCTION
```

The 13 negative controls cover missing enumeration counts, altered prices, invalid relaxed profiles, overextended support, and corrupted certificate fields.
The four positive controls check both equality candidates and both sides of the critical crossing.
A separate `python3 -O -B` execution passes every control and reproduces all three JSON receipts exactly.

A minimal relocated copy contains only this package and its five pinned source files.
It passes the same command from an unrelated working directory.
A second invocation rejects an existing output directory and preserves every output byte.
An altered predecessor source fails its hash check under `-O` before writing a certificate.

`make selected-record-check` passes with the selected kappa `1661960547713947/1000000000000000000`.
The changed Markdown passes the project's STE-100 lint.
The patch passes `git diff --check`.

## Acceptance scope

The contribution identifies the first failure left open by concurrent PR995, which already proves uniform support through `b=1/3`.
It proves the sharp interval, boundary equality cases, and a relaxed competitor that wins for every larger exponent.
It covers the entire stated relaxation rather than a small search neighborhood.
We claim no additional practical owner-search exclusion near the selected endpoint.

The selected construction, supplier code, outer transfer, source records, and `upstream/` remain unchanged.
A cold replay of the full selected supplier is outside this additive proof package's affected checks.
No timing improvement, physical realization of the relaxed countermodel, or full multiplication theorem follows from these receipts.
The publication remains subject to maintainer mathematical review.
