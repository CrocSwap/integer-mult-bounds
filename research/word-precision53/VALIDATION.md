# Local validation

Executed 2026-10-13 on Windows, Python 3.14.5, standard library only. The
three final commands ran with `-I -O -B`, after code and mathematical documents
were finalized. No background process writes a tracked validation artifact.

```text
PASS_WORD_PRECISION53 cases=20 dense_prefixes=144 controls=7
PASS_INDEPENDENT53 words=4680 corner_executions=279616 sharp_words=340 fixture_prefixes=240
PASS_PACKAGE53 relocated=1 controls=6
```

The 20 source runs cover lengths 1,2,3,8,17, margins 1/2 and 1/16, and both
directions. All 240 executed stage boundaries check source restoration,
coarse-grid closure and componentwise magnitude. Twelve small fixtures give
144 independent dense prefix error comparisons. All whole words restore
the three original nonzero arrays exactly. Fraction arithmetic is exact.

Seven mathematical controls reject self ports, invalid operator references,
negative norms, zero sign, omitted propagated error, one insufficient coarse
bit and an unplanned inverse continuation. Six package controls reject a
deleted source-pin entry, altered source, changed selected snapshot, a float
or bool substituted for an expected integer, and output overwrite. The
relocated replay copies exactly the pinned predecessor files and the package,
requires no Git/network and uses a directory name containing spaces.

An initial package test attempted to use the sandbox's default temporary
directory, which denied writes. The test now explicitly uses a temporary
directory under the checkout and passes with cleanup. A first selected-check
invocation used a nonexistent `tools/` path; the actual script is under
`scripts/` and explicitly rejects optimized Python. It is rerun with its
documented `python -B` invocation. Failed invocations are not counted as evidence.
The Python launcher also prints a harmless location diagnostic before
successful runs; exit codes and the full expected summaries are checked.

The repository selected-result check passed with exact retained kappa
1661960547713947/1000000000000000000; the staged whitespace check passed.
Full repository/native cold replay, Linux, hosted CI,
proof-assistant checking, physical tape compilation and supplier admission
were not run and are not inferred from these local checks.
