# Register-level retiming of the gen4 five-stage word

**κ = 144727257636539/(2·10¹⁷) = 7.23636288182695 × 10⁻⁴**, conditional, bit supplier binding.
This is **+6.47 × 10⁻⁸ (+0.0089 %)** over PR279 (7.23571590007464 × 10⁻⁴). It is a small, strict
improvement of the exponent saving, not a runtime claim.

## What changed

Only `descent-selection.json` and the counts pinned to it. The package is otherwise PR279's
`five-stage-gen4-banks`: the same bit word, scalar program, banks, entrances, charts, complex supplier,
moment engines and outer assembly. `descent_transform.py` is byte-identical and applies the new frozen
selection under exactly the contract it already enforced for PR279:

- every retimed ADD gate gets a nondegenerate frame (G = 9I − J Gram test);
- the gate frame contains the exact integer source span of every non-target operand after the gate;
- every register's frame chain stays nested from its unchanged initial frame to its unchanged final frame;
- COPY lifetimes, copied-centre scatters and every gate inside a copy window are untouched;
- the scalar/COPY projection is byte-identical, and both reflected annihilator ledgers are rebuilt.

The selection retimes **1,093** ADD gates (PR279: 880), removing **922** local recursive calls (PR279: 880)
at unchanged rank mass 425,742. The five-stage profile has 482,936 calls (PR279: 483,146) and rank mass
2,809,600. Local paid-histogram delta against the parity-fused word:

```
{1: −1784, 2: +855, 3: −5, 4: +29, 5: −65, 6: +2, 7: +70, 8: −33, 9: −35, 10: +59,
 11: +5, 12: +7, 13: −24, 14: −3, 20: −880, 21: +1760, 22: −880}
```

The 880 source-pair retimings of PR279 are all retained; the further changes are on dirty-register chains.
Bit coarse saving 362080158564507/(5·10¹⁷) ≈ 7.24160317129014 × 10⁻⁴ (PR279: 7.24095525220252 × 10⁻⁴);
the adjacent 10⁻¹⁸ grid point is rejected as before.

## How the selection was found

The cost model is exact: along a nested chain a step is paid iff its dimension strictly increases, with
first-order weight r·ln(120/r); total mass per register is fixed by its endpoints, so only the number and
split of steps can change. Three searches were run on the parity-fused word (scripts in `search/`):

1. **Single-gate neighbour moves** (re-use an operand's adjacent frame). Run globally, this reproduces
   PR279's 880 gates exactly and finds nothing else: PR279 is a local optimum for that neighbourhood.
2. **Register block moves.** For one register at a time, a DP over its whole gate sequence chooses
   frames from the partner's adjacent frames, the register's own frames and their joins. The partner's
   cost change is charged inside the DP, and every accepted move is re-checked by exact recount of all
   affected chains.
3. **Raise/lower cascades.** Raise one gate to a later frame and close forward by joins (or lower and
   close backward by meets), accepting only an exact decrease.

All searches converge to the same optimum from independent random orders.

## Scoped negative results

These are reported so others need not repeat them.

**Frame retiming is nearly exhausted for this word.** Forward-minimal frames (joins of operand states
and spans) and backward-maximal frames (meets of future constraints) coincide at most gates, because
dirty registers accumulate binary-tree sums whose spans pin frames from below while shared side roots
and partner carriers pin them from above. A decoupled per-register DP bound suggests +3.35 %, but that
ignores partner coupling; with coupling, three different neighbourhoods all stop at +0.009 %.

**Target and source chains are structurally fixed.** Targets step 0→21→22→23 (or 0→20→21→22→23)
because shared side roots deliver to several targets whose 23-dimensional caps meet in a 22-dimensional
space. Delivering the last share at a target's own cap would need a different delivery order, which
would change the byte-identical scalar program.

**More compensated reuse pairs are impossible in this word.** Removing one dirty register is worth about
60 frame merges (≈ 6–8 × 10⁻⁵ relative each), so this was the most valuable lever examined. All 1,760
rank-21 gauges are eligible recipients, but the maximum matching is 1,494 even **ignoring timing**: the
binding constraint is donor-frame containment. Only 2,420 of 8,829 dead registers end inside any rank-21
gauge frame, and the 20 components of the compatibility graph have Hall deficits summing to exactly 266.
No rank-20 gauge has a single frame-compatible donor. A larger matching therefore needs a different word
(more donors with small final frames), not a different matching or schedule.

## Scope

Unchanged from PR279: conditional on the retained all-size compiler, common weighted chart, restored
rows, selectors, tape routing, prime supply, precision/recovery, complex symbolic correctness and the
analytic reduction. The finite replay is not a formal proof of the multiplication theorem.

Prepared with Anthropic Claude assistance (Claude Opus 5.5); Apache-2.0. Builds on PR279 (Rohan Arun),
PR276 (DreamingOfClouds) and every source credited in `NOTICE.md`.
