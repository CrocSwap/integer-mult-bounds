# Conditional κ = 0.0036504442446 from a timed helper update

Helper 757 can use the change in helper 1255 between two existing contacts.
Subtract 1255 in chart 3, move 757 directly to chart 603, then add 1255 back.
This replaces the old `3→595→603` path by `3→603`. It removes one paid MOVE
per native call and keeps the scalar-operation count unchanged.

The complete 17-call application supports **κ = 0.0036504442446**. The gain over the raw crossing of
[PR7604](https://github.com/CrocSwap/integer-mult-bounds/pull/7604)
is more than **0.0000002219087727**, or about **0.00608%**. The comparison uses
its certified upper bound `0.0036502223358273`.
The complete paid delta is `P1 -= 34, P2 += 17`; productive targets do not change.
This is a new paid profile, not a decimal refinement of the predecessor.

The raw crossing lies in
`(0.0036504442447168877, 0.0036504442447168879)`.
The fixed-invoice headroom above the public claim is less than
`0.0000000000001168879`. This bounds this invoice only.

```sh
python3.12 -B scripts/research_package.py --package research/p104-timed-helper757
```

All dependencies are retained in the package. Use Python 3.12 and the standard
library. The six commands check source bytes, all exact rows, physical columns,
two directed prices, the complete native application and the signed caller.
See [PROOF.md](PROOF.md), [VALIDATION.md](VALIDATION.md) and
[data/FINAL.json](data/FINAL.json). `APPLICATION-CHANGES.json` lists each change
to Hao Yan's retained application launcher. Retained files are unchanged.

The full multiplier is not materialized or executed. The same five assumptions
remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape` and
`analytic_recovery`. Finite replay does not establish formal or independent
human acceptance. No selected-frontier change or merge is requested.

## Open next questions

Can another existing field supply an entire timed update without a new paid
carrier? A new candidate needs literal early and late contacts, all output and
erasure rows, and the full application cost. The discovery screen is a finite
nomination search, not a rational exclusion of other candidates.

An independent review of this conditional application also remains open.
[TASK.json](TASK.json) states both questions and their remaining obligations.

## Credit

Ali Romman, with substantial OpenAI Codex assistance. Hao Yan/PR7604 supplies
the current word and application. SYLforge/PR7603 supplies the two-cut stock
criterion and unresolved stock census. This change extends that criterion to
actual timed stock. DreamingOfClouds/PR7601 supplies token settlement;
ToikY/PR7546 and PR7544 supply the complete native application; Rohan Arun/PR7113
supplies the signed caller. Clear1nsight, dillona, CubeJerry and all authors in
the retained native, compiler, price and BIT lineage keep their credit.
See [NOTICE](NOTICE) and [SOURCE-VERSIONS.json](SOURCE-VERSIONS.json).
