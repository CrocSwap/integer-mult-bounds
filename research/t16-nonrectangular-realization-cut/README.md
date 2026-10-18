# A T16 realization obstruction beyond every joint-width cut

One explicit marginal in the actual T16 capacity-16 class passes **all** of
[PR2535](https://github.com/CrocSwap/integer-mult-bounds/pull/2535)'s joint-width
rectangle cuts and the earlier Hall/GR checks, but has no bin-level realization.
A nonrectangular call/width inequality detects it as **5 > 4**. Retiming one
helper gives a feasible assignment with exactly the same bin patterns.

This answers PR2535's second open question. Its separator already disclaims
sufficiency; no predecessor defect is alleged. The contribution is the concrete
source-compatible obstruction and a reusable stronger necessary cut, not a new
matching theorem, complete characterization, solver speedup or owner-map gain.

## The three-bin contradiction

The pinned source class is number 9 in `mindiff_cls1.py`'s sorted-physical-bin
enumeration: 224 bins of capacity 16, calls 0 through 8, widths `(4,5,7,8,9)`.
Use three nonempty bins and 221 empty bins:

| Bin | Helper widths | Used capacity |
| --- | --- | ---: |
| A | 7 | 7 |
| B | 5, 5 | 10 |
| C | 4, 5, 7 | 16 |

The desired flow is:

| Call | Helper widths |
| --- | --- |
| 0 | 5 |
| 1 | 5, 5, 7 |
| 2 | 4, 7 |
| 3 through 8 | none |

The only width-4 helper belongs to C, so C must put it at call 2. Call 1 needs
two width-5 helpers. Only B and C supply width 5, and each bin may supply at
most one helper to a call, so C must put its width-5 helper at call 1. C's
remaining width-7 helper cannot go to call 0, which requests no width 7; calls
1 and 2 are already occupied in C. Thus no realization exists.

The exact previous separator reports no violation. A separate literal check
also verifies all `31 * (2^9-1) = 15,841` nonempty width/call rectangles. It is
therefore not merely a missed prefix or a different interpretation of its
call order. The earlier source Hall/GR predicate also passes.

Move the width-7 request at call 1 to call 0. These placements realize the
new flow without changing any bin pattern:

| Bin | Call 0 | Call 1 | Call 2 |
| --- | --- | --- | --- |
| A | | | 7 |
| B | 5 | 5 | |
| C | 7 | 5 | 4 |

All other bins and calls remain empty. RESULT.json names actual source bins
for A/B/C. Source call/width demand upper bounds are respected. This is a
**local class marginal**, not a globally balanced 69,120-helper stage1
solution, a claimed failing optimizer run, or a changed physical owner map.
No source search lower bound or paid profile is invalidated.

## A valid nonrectangular inequality

Fix a set Z of allowed `(call,width)` cells. For one bin pattern p, define

```
N_Z(U) = { t : (t,w) is in Z for some w in U },
a(p,Z) = min over width subsets U of
         [ sum(w outside U) p_w + |N_Z(U)| ].
```

In any legal realization, count this bin's placements whose cells belong to Z.
Those with widths outside U number at most `sum(w outside U) p_w`. Those
with widths in U must use distinct calls in `N_Z(U)`, so number at most its
cardinality. This proves the displayed upper bound for every U, hence for
their minimum. Summing independently across all bins proves

```
sum((t,w) in Z) Y_tw <= sum_p X_p a(p,Z).
```

This is the familiar bipartite call-neighborhood/vertex-cover counting bound.
The proof above needs no optimizer, matching sufficiency assumption or claim
that passing all such inequalities realizes the global source model. Different
patterns can use different minimizing U because each coefficient is a fixed
upper bound for one bin with that pattern.

If Z is a rectangle `T x U0`, the coefficient is exactly
`min(|T|, sum(w in U0) p_w)`: choosing U to contain all widths or only those
outside U0 gives the two upper bounds; every U either contains a selected
width and pays `|T|`, or leaves all U0 outside and pays their multiplicity.
Thus this family includes the previous joint-width inequalities. The exhibited
marginal proves the inclusion is strict.

For the witness, choose

```
Z = {(1,5), (1,7), (2,4), (2,7)}.
```

Its flow is 5. Pattern A contributes at most 1; B's two width-5 slots see only
call 1 and contribute at most 1; C's selected cells see only calls 1 and 2
and contribute at most 2. Empty patterns contribute zero. The resulting cut
is `5 <= 1+1+2 = 4`, a contradiction. Each of the three bin bounds is itself
attainable. The feasible retiming gives `4 <= 4`.

## Source-model use

`cuts.py` exposes `inspect` for a validated class and a supplied cell set.
It returns the inequality and coefficients for **all 27 admissible source
patterns** in this class, including patterns absent from the candidate.
For a fixed Z, apply the coefficient to every corresponding optimizer variable;
copying only terms with nonzero candidate multiplicity would give a different,
potentially invalid inequality on later candidates.

The CLI accepts the source's actual `x,y,changed,bound` stage1 schema:

```sh
python3 -I -O -B research/t16-nonrectangular-realization-cut/verify.py \
  --stage1 candidate.json --class-index 9 \
  --cells research/t16-nonrectangular-realization-cut/CELLS.json \
  --output new-cut.json
```

It uses `mindiff_cls1.py`'s sorted-bin class numbering; `glob.py` has a different
order and requires a remap. `changed` and `bound` remain ignored solver metadata.
The command checks all supplied class marginal schemas/balances, then evaluates
one cell set for the requested class. It does not search all cell sets, validate
global demand/idle targets, realize the bins, or interpret an empty violation
as sufficient. Invalid cells and existing output paths fail closed.

## Verification and exact provenance

```sh
python3 -I -O -B research/t16-nonrectangular-realization-cut/verify.py
python3 -I -O -B research/t16-nonrectangular-realization-cut/test_verify.py
python3 scripts/research_package.py --package research/t16-nonrectangular-realization-cut
```

Standard-library CPython 3.12. Default verification is read-only and compares
every typed field of RESULT.json. `--write-result` creates only a missing receipt.

PR2535 is retained at `045c46ba090149d28ec6ee2a0e5e9651b8943978`. Its exact
geometry reconstruction, stage1 decoder and rectangle checker are reused with
credit; only the export's repository-root path is relocated. All source and
main input SHA256/Git blobs are checked before compiling the authenticated
dependency bytes directly. No cached bytecode or optimizer is loaded.
Four retained main inputs reconstruct source windows, active-pair exclusions
and demands. This is structural source binding, not a full native cold replay.

Current PR2169 is pinned separately at
`4452c98ce93b83e696fd285eeb024f6669c145c0`. Its `search/mindiff_cls1.py` and
`search/lib.py` blobs are unchanged from `01b15aee27947d3319c8574464bdab80a00d2839`,
the source head reviewed by PR2535. The two files are retained as model evidence
and never executed. This keeps the new head's provenance distinct from the
previous separator's validation. [SOURCES.json](SOURCES.json) records exact pins.

The mathematical proof is the counting argument above, independent of those
source checks. The executable additionally:

- evaluates the exact prior Hall/GR and sorted-prefix predicates and independently
  enumerates all 15,841 rectangle inequalities;
- exhausts all 54 possible placements of the six helpers in the three active
  calls, finding zero bad realizations and one feasible retiming;
- compares the new coefficient against direct assignment enumeration for all
  20 three-width patterns with at most three helpers and all 512 cell subsets:
  10,240 exact comparisons;
- verifies reduction to the previous rectangle coefficient in 8,640 cases over
  every source capacity-16 pattern, including empty width/call sets;
- demonstrates that taking the rectangular hull or dropping bin/call exclusion
  loses the actual `5 > 4` separation, and rejects malformed cell sets.

Finite coefficient equality is corroboration, not a claimed complete
characterization. Export tests cover Git-free read-only operation, source
corruption before execution, typed-receipt tampering, the real source-schema
CLI, feasible retiming and refusal to overwrite outputs.

## Open next questions

Can sparse nonrectangular violations be found cheaply in the actual optimizer?
Start with a retained failed stage1 candidate and a bounded cell-support search,
then compare identical solver settings with and without the added cuts. The
supplied-cell checker is not a complete separator or performance result.

Do any colored-degree obstructions remain after this larger family passes?
Retain an exact passing marginal and compare with bin-level realization. No
sufficient characterization, improved owner map, moment or kappa is supplied.
Structured questions and overlap limits are in [TASK.json](TASK.json).

## Credit

Canonical base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Philippe Van Velzen / PR2169 and its disclosed Claude assistance supply the
class model and source search. PR2535 supplies the rectangle cuts, exact source
geometry reconstruction and explicit remaining-obstruction handoff. The seed67
auditor, selected T16 construction, Douglas R. Colkitt and their retained source
lineage remain credited. Standard neighborhood/matching counting is not claimed
new. Prepared for **ywz65** with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing; Apache-2.0. No independent human,
formal-kernel, hosted-CI or maintainer acceptance is claimed.
