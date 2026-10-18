# U8 with two rank-seven helper ends: conditional κ = 0.00166202617947539

This construction gives **κ = 0.00166202617947539**, above the pinned selected
PR942 result, `0.001661960547713947`. The exact increase is
`65631761443 / 1000000000000000000`, approximately **0.00394906%** of that κ.
This compares asymptotic exponent savings, not measured runtime.

The construction combines PR869's U8 word with two smaller helper ends and
an explicit owner assignment. Helpers 588 and 589 finish in dimension seven
instead of eight. Eight B frames and two early-cleanup frames change with
those ends. The owner assignment combines the released space into rank-48
residuals. All raw scalar gates and their order retain their U8 values. The
ports, center interface, physical geometry, and 72-call schedule retain their
PR799 values.

| Quantity | U8 before this change | This construction |
| --- | ---: | ---: |
| Local rank-one children | 2548 | 2542 |
| Local rank-two children | 338 | 352 |
| Local rank-three children | 446 | 438 |
| Local rank-four / five / eight children | 162 / 72 / 8 | 162 / 72 / 8 |
| Helper width per call | 3778 | 3776 |
| Global idle profile | `{1:1, 3:1, 44:1, 48:2396}` | `{48:2400}` |

The complete global profile is
`{1:183024, 2:25344, 3:31536, 4:11664, 5:5184, 8:576, 48:2400}`.
Its rank mass is 520704, with deficit 2560. The certified complex endpoint is
`0.001664793109206301164750`; the retained PR589 bit endpoint is
`0.001733427039589844234749`. The complex supplier remains the limiting one.
The conservative calculation separately gives `κ = 0.001662026176592891`.

The 72-call construction has a certified global prefix bound of 257 bits and
retains the 512-bit allowance. Its physical row coefficient is 16467, below
the retained limit 20161. The comparison result uses 333 calls and a 1024-bit
allowance. Its all-replica bound fixes the previous local profile and helper
widths; this construction changes both.

From the repository root, use Python 3.11 or newer and Git:

```sh
python3 -B research/complex-rank7-end-pair/reproduce.py --work /tmp/rank7-end-pair
```

Use a new output directory. The command fetches the four exact source commits
in `SOURCES.json`. It rebuilds the PR741 ancestry, PR799 word, and PR869 U8
word; applies the twelve changed annotations; rebuilds the owner assignment;
and runs complete native and global admission. No optimizer or Python package
installation is required. If a local repository contains the pinned commits,
add `--git-repository /absolute/path/to/repository` to use its objects without
fetching. Source files are extracted into the output directory in either case.

Expected final output:

```text
PASS_COLD_RANK7_END_PAIR_COMPLETE_ADMISSION 0.00166202617947539
```

The required checks include all 38 U8 construction controls, every 728-input
column in both orientations, all 2,950 phase edges, exact residual wrappers,
25 native controls, and the 89 applicable inherited cold-end controls.
Dedicated controls cover the new dimension-seven ends and their frame changes.
The independent point audit uses explicit subsets of the 512-point frame
space. Owner checks cover all 36,288 roles, complete availability windows,
distinct families per call, capacity, and disjoint compact coordinate prefixes.
Discovery is followed by frozen strict admission, 69 admission controls,
12 bit-supplier controls, seven independent owner controls, and both exact
moment engines with all 47 outer inequalities. `data/EXPECTED.json` pins
the resulting word, programs, phase recipes, owner map, profile, and κ.

`evidence/VALIDATION.json` records the final cold run's environment, coverage,
and input hashes. `evidence/ASSEMBLY.json.gz` preserves the unchanged
assembler's complete output. Its historical descriptions and comparison
labels refer to its predecessors. The profile, moment endpoints, κ, and
outer inequalities are the computed results for this candidate.

`PROOF.md` explains the end frames, packing certificate, and complete cost
change. `SEARCH.json` records the finite discovery and subsequent composition
with U8. Search optimality is not needed to verify the construction.
`data/SELECTED942.json.gz` preserves the selected-result snapshot used only
for the numerical comparison; its source commit and hash are in `SOURCES.json`.

This is a finite conditional witness for
`T(n) = O(n (log n)^(1-kappa))`. The inherited all-size compiler,
common-label and mutable-source realization, whole-call hosting, precision,
tape, exact-recovery, analytic-transfer, and bit H1–H5 assumptions remain.
The command reprices the pinned PR589 bit supplier; it does not repeat its
bit-circuit construction. Finite replay does not prove the full multiplication
theorem. The selected certificate is outside this contribution's scope.

The contribution is independent of PR784. See `NOTICE.md` for predecessor
credit, licensing, and the disclosure of AI assistance.
