# Executed validation

Executed on 2026-10-13, Windows, CPython **3.14.5**, against base
`407d52ff15b2217b6e22bce44728b4c3907b6515`. Both implementations use only the
standard library. The claimed minimum supported version is Python 3.10 based
on language/API usage; that minimum-version interpreter was not tested.

| Check | Observed result |
|---|---|
| `python -B research/u8-supporting-uniform/verify.py` | `PASS_U8_SUPPORTING_UNIFORM`; 1,163 patterns, 42 strict ranks, uniform scaled margin greater than 554 |
| `python -B research/u8-supporting-uniform/independent_check.py` | `PASS_U8_SUPPORTING_INDEPENDENT`; independent proof integer minimum 1,794,386,594,565 at rank 44 |
| `python -B research/u8-supporting-uniform/test_verify.py` | 8 tests pass; observed duration 4.026 seconds, not a performance comparison |
| Optimized standalone execution | Both scripts pass under `-O -S -B`; checks use exceptions and do not disappear under optimization |
| Nine corrupted certificates | Both implementations reject all nine; the independent CLI must report the specific expected failure |
| Changed pinned source | Rejected with `source drift` |
| Regeneration to a fresh file | Byte-identical certificate; SHA-256 below |
| `python -B scripts/verify_selected_result.py` | Pass for base selected `1661960547713947/10^18` |
| Refreshed upstream source compatibility | All five pinned inputs unchanged at `8bddbee377e2f3ce1f1247196c4b290d55767d20` |
| Separate scoped review | No actionable mathematical or implementation issue found; AI review, not human peer review |

Certificate SHA-256:

```
3ffa4e686f92ece0ba53206068377e4ae27912a17d491463632ebd39d77ee16a
```

The controls alter rank-one price, a negative credit, worst-rank coverage,
negative-credit coverage, a cube lower endpoint, the denominator upper
endpoint, a claimed margin, equality mass, and the exponent scope. The exact
rank-32 failure at b=1 is additionally derived from a different rational
formula, rather than by corrupting the computed answer.

The first test run could not write fixture files under the desktop sandbox's
default TEMP directory. Directing TEMP/TMP/TMPDIR to a writable workspace
directory resolved this environmental error. A later run caught a source-list
mismatch after moving the changing selected frontier into context-only
metadata; both source inventories were reconciled, and rejection tests were
tightened to check the intended failure message. The final suite passes with
all mathematical coverage retained.

Repository-wide `make verify`, native selected-supplier cold replay, hosted CI,
and proof-assistant verification were **not run**. This addition changes only a
standalone research package; none of the inherited generators, construction
artifacts, selected frontier, or `upstream/` files are changed. The scoped checks
above do not certify those larger systems.
