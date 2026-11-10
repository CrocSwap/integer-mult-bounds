# Three shared-carrier input lifts

The complete conditional claim is **kappa = 0.00315120**, up from PR6372's
**0.00315087**. The gain is **0.00000033** (+3.3e-7), about **0.0105 percent**.
This is a small, source-bound improvement. It inherits the same five
framework assumptions as PR6372, PR6353 and PR6349.

The PR6372 word has six public helpers that are prepared at the zero frame `Z`
and leave it for a first-destination frame. Here each of the six instead
starts at a smaller entrance frame `F` inside its first destination. The
`Z`-column response of the helper is delivered by ordinary ADD events. Rows of
the same first-destination group receive it right after they arrive. Three
carrier rows, each making one detour `Z -> F -> old destination`, receive it at
`F`. A carrier is shared by the two helpers of its pair. Each lifted helper is
restored at the final frame by ordinary ADDs.

| carrier (group dim) | entrance F | lifted helpers (first-destination dim) |
|---|---|---|
| 171 (2) | span{30}, frame 106 | 520 (3); 655 (5) |
| 208 (2) | span{51}, frame 105 | 544 (3); 671 (5) |
| 130 (2) | span{51}, frame 105 | 472 (3); 624 (5) |

The word has 17,768 events (PR6372: 17,757), 770 public inputs, 29 owned
fields, 43 owned lifetimes and peak owned storage 13. No owned field or
lifetime is added. The lifts add 40 MOVE and ADD events and no INIT or CLEAR.

Exact local changes per full caller copy:

```text
paid:       +6 at rank 1, -3 at rank 3, +3 at rank 4, -3 at rank 5
productive: +6 at rank 8, -6 at rank 9.
```

The margin change per copy is `6(H8-H9) - 6H1 + 3(H3-H4+H5)` with
`H_r = r^(1-kappa)`. There are 19 full copies in the fixed caller, which has
70,713 paid jobs, 14,214 productive jobs and rank-mass surplus 808. The
complete rational crossing is in
`(0.00315120852329, 0.0031512085233)`.

## Tariff scope

The gain is exactly zero at linear cost (`kappa = 0`): paid and productive rank
mass both fall by six per copy. It is positive only for power exponents `s` of
about 0.873 to 1 in `H_r = r^s`, with margin change +0.0839 over the 19 copies
at the claimed exponent. It is negative for smaller exponents and for tariffs
such as the square root. The claim therefore holds at the stated
`kappa` exponent only, the same basis as the exact power-moment check of
PR6349. It is **not** a result for every concave tariff.

Read [PROOF.md](PROOF.md), [LIFTS.json](LIFTS.json) and [RESULT.json](RESULT.json).

## Reproduce

Use Python 3.12 with no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p104-shared-carrier-lifts --check-only
python3.12 -B scripts/research_package.py --package research/p104-shared-carrier-lifts
```

The registered normal and optimized commands authenticate the pinned inputs,
rebuild the word from PR6372's word using `construct.py` and `LIFTS.json`,
and check every word field, all 799 scalar columns, native absolute phases,
all caller contacts, two rational price engines, completion, compiler bounds
and all 54 strict plus four functional outer predicates. They also run the
rejection controls: the PR6372 caller and price controls, the damaged-input
controls and nine lift-specific controls (response doubled, response sign
flipped, restore dropped, first restore dropped, first delivery dropped, anchor
MOVE dropped, last MOVE dropped, MOVE destination shifted, entrance reverted).
[VALIDATION.md](VALIDATION.md) records the checks actually run.

## Sources, coordination and limits

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Source: the
PR6372 word at head `b556600ffe14be72406b03a47c661f3c7f1aff06`, retained in
`inputs/` with exact Git and SHA256 pins. This PR stacks on PR6372, as PR6372
stacked on PR6353.

All five inherited assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The uniform large word
and rounded multiplier are not materialized. No global optimum, practical
speedup, independent scientific acceptance, formal-kernel acceptance or
selected-frontier change is claimed. The gain is a mild-curvature effect near
the stated exponent (see Tariff scope).

## Open next questions

An independent reviewer can check the lift responses, the carrier trips and
the exact signed bill. A gain that is positive at linear cost needs a changed
mechanism and a full bill. Structured questions are in [TASK.json](TASK.json).

## Credit

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
Apache-2.0. Ali Romman's PR6372, PR6353, PR6349 and PR6348 line supplies the
source word, the joint basis method, the native transpose, the native
input-lift move class, the fixed binary-tree caller and the price engine.
PR6349 builds on DreamingOfClouds PR6314. [NOTICE](NOTICE) preserves the
predecessor notices.
