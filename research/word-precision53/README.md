# Fixed word precision from directed dependencies

The existing six interacting cyclic-inverse shears need fewer sufficient
fractional bits when their planner follows each array's dependencies. The
complete forward/inverse word still makes all 12 calls and uses the unchanged
rounded leaf and exact source-restoration implementation.

For target accuracy 2^-40 and initial array norms <=1:

| Stability margin | Old coarse / working bits | New coarse / working bits |
|---|---:|---:|
| 1/2 | 86 / 145 | 69 / 112 |
| 1/16 | 151 / 291 | 117 / 226 |

These are sufficient proof budgets, not measured speedups or minimal physical
precisions. Both planners reserve clean low bits in owned source words.
There is no new kappa, arbitrary dirty-bit contract or supplier admission.

From the repository root, Python 3.11+ and the standard library suffice:

```sh
python -I -O -B research/word-precision53/verify.py
python -I -O -B research/word-precision53/independent.py
python -I -O -B research/word-precision53/test_package.py
```

Expected summaries are 20 source cases / 144 dense prefix checks / 7
mathematical controls; 4,680 independent words / 279,616 corner executions /
340 saturation witnesses; and one relocated replay / 6 package controls.
`verify.py --write-certificate /new/path.json` exclusively creates a replay
receipt. The main verifier checks exact typed canonical receipt equality and
the entire required source inventory before importing the unchanged leaf.
The package test uses a temporary directory inside the checkout, cleans it
up, and also works in a path containing spaces without Git or network.

[PROOF.md](PROOF.md) gives the all-word recurrence and full local cost/storage
boundary. [EXPECTED.json](EXPECTED.json) records every fixture, prefix and
partial execution counter. These counters include validation and phase
reads but are not a physical tape or bit-operation invoice. The source's
coefficient preparation, source storage, scalar workspace, layout, compiler
and arithmetic charges remain. No execution call is omitted or amortized.

This corroborates the source's valid fixed-precision composition contract
and improves its enclosing sufficient bound. It changes neither its scan
nor PR1054's within-leaf cubic analysis. PR1057's exact additive port borrowing
has a different contract; the rounded functions here may be nonlinear.
See [OVERLAP.json](OVERLAP.json), [NOTICE.md](NOTICE.md), and [VALIDATION.md](VALIDATION.md).

Only this package is added. Its selected-result snapshot is immutable context;
later movement of the repository's selected pointer does not invalidate a
replay of these pinned sources. The retained T37 result and all global
obligations remain unchanged.
