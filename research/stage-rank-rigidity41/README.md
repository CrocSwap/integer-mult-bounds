# Every minimum-stage cross-shear call must have full rank

**Scoped structural decoder result; no new kappa or supplier.** In the
two-bank linear interface, permit arbitrary invertible within-bank bridges
and cross-shear calls of possibly different ranks. An exact exchange of
n-dimensional banks obeys

`sum(call ranks) >= 2n + max(call rank)`.

Consequently, when `n=P*v`, the rank cap is v and the controller uses the
minimum `2P+1` calls, **all calls must have rank v**. A proposed cheaper
partial-rank boundary call cannot preserve that minimum stage count.
This extends the credited PR743 uniform call-count argument to heterogeneous
rank accounting; it does not claim a new uniform-stage theorem.

`PROOF.md` gives the field-independent argument. It rotates any chosen call
to first position by conjugating moved gates with the off-diagonal endpoint,
preserving bridge type and call ranks. A diagonal-rank potential then charges
all calls except the distinguished first one.

## Reproduce

From the repository root, Python 3.10+ and the standard library:

```sh
python -I -B research/stage-rank-rigidity41/verify.py
python -I -B research/stage-rank-rigidity41/independent.py
python -I -B research/stage-rank-rigidity41/test_package.py
```

Expected principal markers:

```text
PASS_STAGE_RANK_RIGIDITY states=20160 edges=604800 rank_min=5 pareto=3:6,5:5 no_new_kappa
PASS_STAGE_RANK_INDEPENDENT dense_states=20160 decompositions=12 rotations=12 fields=2,3,5
PASS_STAGE_RANK_PACKAGE controls=8 source_inventory=exact
```

The complete GL(4,F2) calculation has 20,160 states, 30 nonzero cross shears
and 604,800 checked transitions. The finite exact Pareto tradeoff is:

| Paid calls | Minimum total rank | Status |
|---:|---:|---|
| 0, 1, 2 | impossible | complete exact layers |
| 3 | 6 | three full-rank calls |
| 4 | 6 | dominated by the three-call point |
| 5 | 5 | five rank-one calls |

The global minimum rank volume is 5 even with arbitrarily many calls, certified
by full weighted shortest paths. This makes the displayed `(3,6),(5,5)` Pareto
frontier complete for this finite model. The five-call witness also prevents
misreading minimum-stage rigidity as a claim that all longer controllers must
use full-rank calls.

The independent program uses dense modular matrices and rank-one BFS instead
of packed-row weighted Dijkstra. It matches every state distance, checks all
12 rank-two decompositions, tests 12 endpoint-conjugated rotations over three
fields, and rejects omitted calls, partial exchange, dishonest rank metadata,
an inadmissible free cross-bank bridge, and unconjugated rotation. Both programs
are AI-written; separate implementations do not imply human independent review.

## Scope, sources and credit

Assignment seed 41; exact base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. The frozen selected context remains
PR942 T37, conditional kappa `1661960547713947/10^18`. The source manifest pins
the archived campaign discussion, unchanged formal-column controller source,
actual selected assembly and review. Text hashes normalize CRLF to LF. The
selected context is a frozen snapshot, so later pointer changes do not break
this historical replay.

This addresses rank-lowering attempts within an explicit cross-shear/bridge
interface. It neither changes copied-center geometry nor treats rank as the
actual price of every decoder. No partial exchange, extra connector bank,
cross-bank bridge or nonlinear encoding is allowed. It is not a geometry-wide
or supplier-wide impossibility theorem. It introduces no circuit into a
supplier and does not rerun native physical legality, full cold suppliers,
global invoices, hosted CI or Lean. All-size, compiler, hosting, precision/tape,
analytic and bit-interface assumptions remain separate.

Credit **0xjohnnydev's PR743** for the uniform potential argument (inspected
head `f39226f49486f44e9771b88121ad11f9d0b76eee`), **Jacob Sussman** and the
retained borrowing-controller lineage for the positive construction, and
**PR397** for the indexed formal identity. The archived campaign report and
its contributors retain attribution; no original source is copied or edited.
The native controller source credits Dylan Crow, DaysSky and their disclosed
assistance. Jonathan Capalbo, Hao Yan, Jeremy Kothe, Chafik Boukhalfa,
DreamingOfClouds, eumemic and the retained source contributors receive credit
for the selected context. See `OVERLAP.json` for the distinct Gaussian copy
floors and connector mechanisms considered during scope selection.
The final overlap check also inspected PR1012's T37 restoration-deferral
mass-neutrality result; that hosted recurrence accounting is a different
interface from the cross-shear rank-volume theorem here.

Prepared for **@woklerx with substantial OpenAI Codex assistance** in research,
proof development, implementation, verification and writing. Apache-2.0.
