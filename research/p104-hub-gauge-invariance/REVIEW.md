# Independent review record

This review was performed by separate OpenAI agents for @CubeJerry. It is
independent AI mathematical/code review within the stated scope, not external
human acceptance or proof-kernel verification.

The lead read the complete PROOF, README, VERIFY contract, RESULTS and verifier.
It independently checked the stabilizer block argument, the contragredient
transport, the dyadic pairing examples, the rectangular-state distinction and
the formal changed-word counterexample. No mathematical defect was found.

A second agent, separately from the author, read those files and the retained
#6827 proof §§0–5 and #5599 proof §1. It derived the stabilizer directly: the J
rows fix the J block, the J columns kill the lower-left block, and the remaining
common-helper block commutes with A. It verified that the PURE transport keeps
both physical read/write witnesses and the whole Gram matrix, and that the
broader two-sided sufficient contract does not need suffix injectivity.

The reviewer checked the complete-helper-block premise in both directions,
including the labelled-subset and triangular-shear counterexamples. It checked
the same-total-T example: mixing occurs before frame separation, its inverse
after rejoining, and the seven MOVEs and full Laurent-polynomial endpoint are
unchanged. This supports the distinction between a fixed event word and only
a fixed public middle matrix.

The reviewer executed:

```sh
python3 -I -B research/p104-hub-gauge-invariance/verify.py
```

The complete replay passed in 7.398 seconds locally, including the 359-helper
native stabilizer, all 77 complete helper boundary classes, three matched cuts
on all 801 state slots, and the semantic rejection controls. The author's
normal and optimized direct runs and registered package runs also passed.

The review does not establish a source-wide symbolic PURE census, a universal
endpoint-rewrite theorem, a cheaper basis implementation, a new native word,
a κ change, or any of the inherited compiler/precision/analytic assumptions.
Those limits are explicit in the proof and verification contract.
