# Round 15 research report — terminal elimination on the moving frontier

## Result

The strongest surviving result is a finite, conditional improvement to the
replayed h=24 complex producer. A terminal auxiliary accumulator that is not
an input to any later auxiliary operation can be removed. Its incoming updates
are redirected to its unique output at their original gate times and frames;
the old target-front moves and all surviving auxiliary operations remain
charged. This preserves arbitrary dirty state and the reflected inverse word.

Applied after the pinned PR118 replayed graph and the pinned PR114 saturated
placement, the construction removes 393 roles and redirects 1,221 updates:

| quantity | value |
|---|---:|
| active roles R | 28,312 |
| complex width W | 122,800,128 |
| rank sum | 70,731,011,648 |
| maximum child | 574 |
| deferred roles | 4,560 |
| exact κ | 2,188,324,161,643 / 20,000,000,000,000,000 |
| decimal κ | 0.00010941620808215 |

The common published-bit control is κ = 0.00010854280649816; the full exact
common-control comparison is
κ = 1,356,785,081,227 / 12,500,000,000,000,000. The candidate improves that
control by 87,340,158,399 / 10^17, and improves the public PR118 value by
17,468,042,283 / 2·10^16. The current public PR114 head claims
1.09281094468·10^-4; this candidate is approximately 0.124% higher. These are
conditional assembly bounds, not an unconditional new multiplication theorem.

## Identity and cost proof

For a removed role with initial frame dimension σ, first frame F, and last old
target-readout dimension M, write h=24 and m=h². Distinct targets and the
checked chronology give the before/after packets (zero entries omitted):

    old = [m-h+σ, 1, F-σ, h-1-M]
    new = [m, F-M, 0, 0].

They have equal rank mass. For 0≤σ≤M≤F≤h−1, the sorted partial sums of `new`
dominate those of `old`; at least one inequality is strict. Therefore
`sum child^(p)` strictly decreases for every 0<p<1. The complete profile
linkage checks all 576 integer hinge functions, and an exhaustive small
parameter check covers h=2,…,16. This is a finite routing identity, not a
claim of asymptotic improvement by itself.

The redirect is legal because the selected roles have no outgoing auxiliary
use, one ordinary output, no center component, no phase-one event, and every
incoming update occurs at a frame containing all required target readout
frames. The reflected word uses signed reverse gates, bank exchange, and fresh
copies. Deleted role identifiers are absent from the active trace; compacting
the finite active bank is bookkeeping only.

## Verification status

The independent audit reports:

- exact integer adjoint over denominator 42 and all-input Q(i) dirty identity;
- source injections and redirected snapshots at original times;
- 509,482 forward physical events and 247,432 reflected scalar events;
- complete reconstructed child histogram and scalar guard;
- six malformed-witness runs rejected (adjoint coefficient, phase omission,
  illegal target sigma, omitted center charge, redirect coefficient, and
  missing redirect).

The inherited stopped-product, Gaussian normal-form, streaming, fixed-tape,
analytic, and all-size assembly interfaces remain explicit assumptions.
No handwritten assembly, CPU benchmark, or asymptotic complexity claim was
introduced.

## Attribution and novelty

The public baseline is PR118 (`ec862a5…`) and its PR117 replayed graph. The
saturated nondegenerate placement is credited to PR114 (`7dfa16e…`); our
reselection reproduces its placement rules and is not claimed as new. The
terminal-elimination identity, source-time redirect construction, complete
profile majorization linkage, and independent audit are the new Round 15
contribution. Publication-level novelty remains unresolved pending review.

The earlier 3,100-role append-compatible deferral and 1,179-role refined-cube
elision are preserved as intermediate results. Maximal frame enlargement and
single-node hinge-safe enlargement were tested and rejected or neutral; they
are not part of the current claim. A target-front pruning control produced no
saving because every removed readout front was needed by the first surviving
redirect.

## Reproduction

The portable arithmetic receipt is
`round15/workers/baseline/terminal-elided-refined-replayed-portable.json`.
The exact word is
`round15/workers/construction/terminal-elided-refined-replayed/word.json.gz`.
The independent physical receipt is
`round15/workers/critic/terminal-refined-replayed-audit/receipt.json`, and
the mutation receipt is
`round15/workers/critic/refined-replayed-mutants/receipt.json`.

The source-bound portable arithmetic command is:

```sh
cd round15/workers/baseline
python3 -B verify_portable_118.py \
  --repo /path/to/unchanged/pr118-tree \
  --profile ../construction/terminal-elided-refined-replayed/complex-profile.json \
  --receipt /tmp/terminal-elided-refined-replayed.json
```

The full finite construction is regenerated in stages: PR118 graph and
matching, exact deferred export with numeric root order, PR114 placement
reselection, then `inventory_deferred_roles.py` and
`eliminate_terminal_roles.py`. The exact source hashes and commands are in
each output `SOURCE.json`; no pinned worktree was modified.

## Decision

This terminal-elimination mechanism deserves a next round only on a genuinely
new producer or a coordinated multi-role schedule. Repeating the same
single-node frame search is closed: the tested hinge-safe policy accepted zero
moves, and the public frontier is moving quickly. Preserve this checkpoint
and candidate for review before any PR or external publication.
