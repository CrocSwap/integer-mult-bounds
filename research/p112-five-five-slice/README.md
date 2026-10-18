# Delete the weight-seven piece to exclude P112 `5,5,6^6,7`

The actual TWOSIDE `(6,3)` profile `5,5,6^6,7` is impossible over every
characteristic-zero field. Delete the last piece first. The remaining
eight independent pieces still need code-intersection dimension five,
but their A5 endpoint support requires **132 incidences against allowance
120**. The ninth piece's weight is unused in this argument.

The new result is this deletion argument and actual-profile application.
The A5 spectrum and coordinate inequality are inherited from Nick
Petalas/PR3188 and PR3169. A [concurrent claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19001119)
uses the same deletion and the coordinate inequality. This package
retains the separate endpoint count and claims no exclusive priority.
It does not settle full C5, the complete P112
decoder floor, supplier admission or kappa. The selected frontier is
unchanged. [PROOF.md](PROOF.md) states all hypotheses and dependencies.

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-five-five-slice
```

The registered replay writes no checkout outputs. For a fresh external
receipt, use an absent file in your own scratch directory:

```sh
python3.12 -W error -B research/p112-five-five-slice/verify.py --output "$RUN_DIR/result.json"
```

`verify.py` reconstructs the exact source geometry, exhausts all five- and
six-flats, checks all root planes and A5 extension orbits, and compares
the retained spectrum with a separate root-class count. The unchanged
original filter and a separate transcription bind the actual historical
profile. The older edge-only bound fails at 816 versus 795; the inherited
coordinate refinement gives 784, while the endpoint bound gives 132.
`RESULT.json` records the exact receipt; `CHECKS.json` records validation.
`test_verify.py` contains mathematical and rejecting failure controls.
Implementation bounds are in [ENGINEERING.md](ENGINEERING.md).

## Sources and credit

DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`
supplies TWOSIDE. Nick Petalas/PR3192 at
`79864770165fe0d7b72c864be4d5a6e2af5e35b5` supplies the weight-seven
handoff and retained source layout. PR3188 at
`93f1fb95a2ab1413b2e9c90a6be4f3a2c4090034` supplies the A5 spectrum;
PR3169 at `2dbbd3004b70772cef200e341037c7c05b094fbc` supplies the
coordinate inequality. Geometry and stabilizer routines retain
PR3176/PR3186 attribution and the E8/P112 decoder lineage, including
joaqcoo's model. [SOURCES.json](SOURCES.json) pins exact bytes and heads.
Retained proof links use their original package layouts.

Development used substantial automated drafting and finite checks.
Evidence is author-checked with internal mathematical review; no
independent human or proof-kernel review is claimed. The standard
Weyl-chamber theorem and original decoder reduction remain dependencies.

## Open next questions

- Does another actual weight-seven profile admit a useful deletion first?
  Establish the surviving code dimension and exact small-support budget
  before extending this argument. A generic piece deletion loses one
  guaranteed dimension; the current proof needs the surviving dimension
  five and six affordable endpoints. Check existing R7/p2 exclusions
  before counting any further profiles as new.
- Can this slice inform a complete remaining C5 obligation? First reconcile
  the original profile ledger with the public exclusions at exact source
  heads. This package does not certify the full current residue count or
  the complete decoder reduction.

[TASK.json](TASK.json) records the changed task scope and next questions.
[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19001093).
