# One actual P112 TWOSIDE profile excluded

Eleven independent P112 pieces with binary weights bounded by
`2,3,6^5,7^4` cannot have code-intersection dimension at least seven,
over any characteristic-zero field. This is one literal historical
TWOSIDE `(7,4)` profile from DreamingOfClouds/PR3154.

Delete the four weight-seven pieces. At least three code dimensions remain.
The three smallest retained pieces have total support at most 26, while
the other four have binary rank at most six. PR3234's inherited A3 theorem
then bounds the intersection by two. The earlier support 22 theorem does
not cover this caller. [PROOF.md](PROOF.md) states the complete implication.

This package authenticates the pending theorem's exact proof and checks this
application. It does not replay the theorem's geometry. The theorem remains
an author-checked dependency, with its stated Weyl-chamber assumptions.
No full C5, complete decoder floor, supplier or new kappa is claimed.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-twoside-a3-application
```

The replay authenticates the live input and retained sources, reproduces the
154 historical BK-filter survivors, checks the literal caller and all transfer
inequalities, and runs eight behavioral controls. A separate descending-sigma
filter agrees over the complete cell. Failure controls reject insufficient
deletions, excessive deletions, weakened code dimension, excessive common
support, malformed weights and changed source bytes.

`RESULT.json` is the exact application receipt. `CHECKS.json` records commands,
environments and internal review. For a fresh receipt at an absent external path:

```sh
python3.12 -B research/p112-twoside-a3-application/verify.py --output "$RUN_DIR/result.json"
```

Use a session-owned directory for RUN_DIR. The verifier refuses to overwrite
receipts or write them inside the checkout. [SOURCES.json](SOURCES.json) pins
main `463113d675af7410ac91d53a4fed51ec6494eb9a`, PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` and PR3234 at
`bd90899d5a45806288f7f3c9f177172a0ef5fa59`. The retained source scripts
are inspection inputs; they are not imported or executed.

## Sources and credit

DreamingOfClouds/PR3154 supplies the original TWOSIDE filters and decoder
reduction. Nick Petalas/PR3234 supplies support 29 A3 shortening, building on
PR3221 and PR3227. The retained E8/P112 lineage, including joaqcoo's decoder
model, remains credited. The new contribution is the literal caller binding
and deletion implication. The scoped source archive and new work are Apache-2.0.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19003035).

## Open next questions

Which original TWOSIDE profiles remain after all public exclusions? Reconcile
the original cell with exact proof hypotheses before another geometry census.
This matters for a complete decoder-floor proof; this package checks one
profile and cannot infer that the other 153 are unresolved. The pending A3
theorem and the rest of the original decoder reduction remain dependencies.

[TASK.json](TASK.json) records the scope change and bounded follow-up.
[ENGINEERING.md](ENGINEERING.md) records implementation limits.
