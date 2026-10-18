# Variable-rank diagonal batching: a local κ>0.1 screen

**Exact source-bound local schedule; no supplier or selected κ claim.** The
selected result remains κ = 0.001672660197076918. A zero-interface-cost
relaxation of the complex side crosses κ = 0.1 only after assuming six unpaid
coordinates per live family. The required coverage endpoint, physical fusion
cost, and bit-side improvement are absent.

## Result

The pinned gauge44 word has 3,486 climb events of ranks 1–5, with total climb
rank mass 5,522. The deterministic scheduler computes, for each climb, the
gaps between the preceding and following non-climb events that touch its
destination register. It moves a climb only inside that interval and only
inside its original phase. It then greedily fuses simultaneous groups on
distinct destinations, with child rank equal to the sum of member ranks and
cap 51. That is the largest rank allowed by the selected outer halving guard.
The deterministic earliest-deadline schedule is a candidate, not an optimum
over all legal schedules.

In both orientations, 5,520 of 5,522 climb-rank units enter 256 batches. The
remaining two units are two rank-one climbs that cannot join a legal group.
After charging each batch as one child of its summed rank, the local profile is

```text
{2:97, 4:9, 6:8, 8:22, 9:1, 11:1, 12:2, 13:2, 14:1, 15:5,
 16:15, 17:1, 18:1, 19:1, 20:2, 22:1, 24:2, 25:2, 30:1,
 40:13, 48:1, 49:2, 50:2, 51:73}
```

It preserves total paid rank mass 5,586. The unchanged local checker accepts the
reordered, still-unfused events in both orientations and returns exactly the
original local and paid-profile receipts. A separate exact test checks the
heterogeneous direct-sum identity
`diag(A_i) diag(B_i) = diag(A_i B_i)` and an additive update on a dirty target.
The identity supports the algebraic rank-sum accounting; it does not supply
selected register gathering, delivery, or restoration.

At the requested primitive target `a=1/9`, the exact outward-rational moment
upper endpoint is 0.999493269793590 with six unpaid coordinates and the
existing centre mass 64. The same profile gives 1.013748787493 with five unpaid
coordinates and 1.070770858292367 with the selected one-unpaid contract (exact receipt in
[RESULT.json](RESULT.json)). The local relaxed ceiling is bracketed by
`0.1118 < a* < 0.1119`, corresponding under the retained planning conversion
to `0.10055765 < κ* < 0.10063855`. This is only a target-screen for one
supplier.

The margin is extremely narrow. Under the model's idle-displacing convention,
six added rank-one-equivalent units per call still pass at `a=1/9`, while seven
fail. Those six units would have to pay for every batch's gathering, frame
conversion, hosting, precision, output delivery, and dirty-state restoration.
The verifier does not show that any of those costs fit.

## Why this differs from earlier batching work

[PR #1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) batches
rank-one climbs into rank-16 children. The local
[diagonal-batch-commutation audit](../diagonal-batch-commutation/README.md)
extends the rank-one scheduling count to 134 batches, retaining a fixed group
size of 16. [The rank-six heterogeneous block](../complex-rank6-hetero21-seedfb19/README.md)
checks the direct-sum tensor `(2,2,1,1) → 6` but finds only 13 strict source
windows. This package instead allows unequal-rank climbs to share any summed
rank through 51 and screens the result at the explicit 0.1 target. A focused
overlap refresh on 2026-10-17 03:02 UTC covered all 243 open PRs and 1,874
discussions with complete pagination; it surfaced this PR and the #1166
handoff mentioning prior gauge44 rank-2 retiming, but no second exact open-PR
match. The current-main [kappa01 target screen](../kappa01-target-screen/README.md)
and [rank-cap floor](../kappa010-rank-cap-floor/README.md) bound the selected
profile and aggregate coverage model. They are compatible with this changed
rank histogram: the hypothetical six-unpaid endpoint and complete interface
invoice remain open. These related results and the close predecessors above
mean this package makes no broad novelty claim.

## Reproduce

From the repository root:

```sh
python3 -B research/complex-weighted-diagonal-rank51/verify.py
python3 scripts/research_package.py --package research/complex-weighted-diagonal-rank51 --check-only
python3.12 scripts/research_package.py --package research/complex-weighted-diagonal-rank51
```

The exact source archive, local checker, selected-result record, and moment
engine are pinned in [SOURCES.json](SOURCES.json). The package replay reads
frozen sources and writes only its own [RESULT.json](RESULT.json).

## Scope and next steps

The six-unpaid coverage law is hypothetical. The current selected endpoint has
one unpaid coordinate; the exact five-plane P112 decoder supplies five but its
copy invoice is far above this screen's six-unit slack. The refreshed main also
contains [a scoped P112 six-mode floor](../p112-six-mode-exclusion/README.md):
for its fixed PR2757 cover and aligned mode family, it reports cost at least 297
against the necessary gate C <= 296. I ran both registered Python 3.12 checks
(`verify.py` and `independent.py`); both report PASS with minimum 297 across 5,440
term-count cases. These are independent implementation checks, not a formal
proof-assistant result. The stated scope does not cover changed covers or mode
assignments. It closes that particular six-mode route, not every possible
six-unpaid endpoint. A separate current-main [complex lever screen](../kappa010-complex-lever-floor/README.md)
reports a different d=3 paired-plane profile with moment 0.995605 at a=1/9
and the centre retained; I reran its registered verifier on Python 3.12 and it
passes. That screen still lacks a source-bound native block and a bit-side
improvement, and no composition with this batch schedule is claimed. This
package does not price a physical weighted batch or change the bit supplier, so
the selected bound does not move.

The next decision is a changed P112 cover or mode assignment, not another search
inside the fixed aligned family. Specify its coverage identity and exact
source-to-target contract, then derive the dirty-state correction and complete
decoder plus hosted-batch invoice against the six-unit allowance. Stop if that
invoice exceeds the allowance. A separate bit-side construction must also pass
`a=1/9` before a selected κ above 0.1 is possible.

## Open next questions

1. Can a changed P112 cover or mode assignment escape the fixed aligned six-mode
   floor while realizing the six-unpaid contract? It matters because six is the
   first coverage point tested here that crosses a=1/9, while the aligned
   PR2757 family is reported to miss its necessary C <= 296 gate by one. First
   step: specify a changed endpoint geometry and derive its full dirty-input
   decoder invoice before searching. Blocker: no replacement boundary or bit
   supplier is supplied; the cited floor has not been independently replayed
   in this package.
2. Can the 256 groups be physically fused for at most six rank-one-equivalent
   units per call? It matters because the moment leaves only that much
   idle-displacing headroom. First step: implement one source-bound mixed-rank
   batch including frame, gather, output, and arbitrary-dirty restoration.
   Blocker: the present schedule only proves legal event movement and an
   algebraic direct-sum identity.
3. Can the bit supplier reach the same target under a realizable coverage and
   rank contract? It matters because the complex-side screen alone cannot
   improve the selected coupled bound. First step: bind the variable-rank
   scheduler to one pinned bit program and price its full profile. Blocker: no
   changed bit-side endpoint is supplied.

## Credit

The selected word and provider lineage retain their PR1094 attribution.
Diagonal rank-16 batching is credited to PR1779 and its local commutation audit;
heterogeneous direct-sum multiplication is credited to the rank-six block
package and its predecessors. This work adds a bounded variable-rank schedule
and exact target-0.1 screening. Prepared by Codex with OpenAI assistance; no
independent human review or proof-assistant verification is claimed. New work
is Apache-2.0.
