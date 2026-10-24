# An unbounded FULL/QUERY controller ceiling

**No higher kappa is claimed.** For the current owned local profile, every
prefix/suffix path controller fails the necessary recursive moment test for
`0.00302728825 <= kappa < 1`. This covers every pair count p>=1, every split,
and every FULL/QUERY assignment among the 2p+1 stages.

[PROOF.md](PROOF.md) gives the reduction from this infinite family to a finite
dynamic program. [RESULT.json](RESULT.json) records exact rational bounds,
all per-p minima, source checks and negative controls. A tail inequality removes
all cases with at least 96 FULL stages. Deleting a pair of QUERY stages reduces
the remaining search to p<=96. The verifier then checks 10,290,000 state
combinations with directed integer arithmetic. It uses no floating solver.

The smallest certified paid-minus-target margin at the ceiling is greater than
`0.000000014914967918767741908079`. The best finite state remains p16/a7 with
18 FULL stages. Literal Laurent invoices on all masks through p=5 provide a
separate check of the formula and dynamic program.

The existing complete conditional comparison is
[kappa .00302728823 in PR5398](https://github.com/CrocSwap/integer-mult-bounds/pull/5398),
which uses the same recursive profile. Its remaining room within this whole
family is less than 2e-11. That construction and its compiler are credited
external results, not newly admitted here. The selected record remains
.0030217758 at canonical main `1ec1119972c9aefe42525172d07b332fcff81cb4`.

The fixed profiles come from
[PR5392](https://github.com/CrocSwap/integer-mult-bounds/pull/5392), head
`329b2ff35d2994b11abbb59f770d12da75c494ac`. Its exact result and source notice
are retained under `source/`. Paths and package descriptions in that unchanged
notice refer to PR5392, not to this package. The new theorem extends the at-most-two-stage
screen in [PR5393](https://github.com/CrocSwap/integer-mult-bounds/pull/5393)
and the fixed center-exchange invoice ceiling in
[PR5397](https://github.com/CrocSwap/integer-mult-bounds/pull/5397). It does not
repeat their construction or claim a global native-circuit lower bound.

## Reproduce

Python 3.12 and the standard library are sufficient. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/global-query-controller-ceiling
```

Expected scientific result, in both registered modes:

```text
PASS_GLOBAL_QUERY_CONTROLLER_CEILING_NO_KAPPA_GAIN
```

Direct read-only replay is `python3 -I -B research/global-query-controller-ceiling/verify.py`.
The explicit `--write` option regenerates the deterministic receipt. Source
bytes are authenticated before execution. The verifier executes authenticated
source text directly, so a preexisting bytecode cache cannot replace it.
The interval engine and source Laurent engine are reused, with their credit;
the dynamic program and the infinite-family proof are new.

The full native phase suite, complete compiler/outer replay, selected cold
replay, physical tape execution and formal kernel are not run by this package.
They are not needed for this raw necessary-condition ceiling. The retained
five framework assumptions still apply to the cited positive constructions.

## Open next questions

A larger gain needs a changed local profile, query price, idle law, connection
graph or recursive contract. First derive its complete paid and productive
inventory and identify which premise of this theorem changes. Then check the
actual operator and compiler costs before making a kappa claim. No further
search of masks or pair counts in this fixed family is proposed. TASK.json
records the scope and the specific reopening condition.

Credit Cinna Davis, Cao Yifan, zxv, Chris R, Dugongue, Jacob Alan Sussman and
the retained source authors. Ali Romman with substantial OpenAI Codex assistance;
no subagents. Apache-2.0. See source/NOTICE.md for the retained source notice.
