# Completion and application of the compiler-cut review

The frozen proof SHA256 is
`162dd4bb7a020dfb72dd3c80cb9a1de37212cc7f812f36fd4365d487d49b341b`.
Its original pending-review text and AUTHOR-RECEIPT.json are preserved historical
records. The independent review in `review/CROSS-REVIEW.md` accepts that exact
proof with the scope clarification below. Neither the frozen proof nor the
parent precision theorem has been rewritten.

## Scope at the actual source

The source requires lambda >= 1 and Q >= 1 individually, in addition to every
retained all-size rank, phase-service, component-conditioning and per-atom error
premise. Their product being at least one is insufficient; the independent
checker supplies the unclamped scalar counterexample. The theorem concerns the
stored exact gate program. Its four operators are prefix, suffix, inverse prefix
and inverse suffix at any complete-gate cut. The Full sufficient envelope is
`K = 2 L0 B H`; arbitrary intervals have the conservative bound `K^2`.

A matching may be partially completed only by selecting whole one- or two-wire
gates. Incomplete coordinate writes, arithmetic scratch, rounded assignment
states and altered recursive implementations require their own analysis. The
bound retains the predecessor's sufficient constant; it does not compare a cut
with the actual measured maximum of its adjacent completed-layer endpoints.

## Prior work and attribution

Brian / JoyboyBrian's #4976 gives unrestricted sharp sqrt(2) interpolation.
Nick Petalas's merged #5940, head
`b709a6adb6a9543247260900b108166a4d469f6f`, already gives sharp conditioned
interpolation and unitary no-loss. The present addition exploits the whole pinned
source word, including its two same-direction shears, and extends a sufficient
envelope through actual source timestamps. It does not sharpen that generic
interpolation formula or settle its four-way sharpness question.

Armin Pourshafeie / apoursh's merged #5240, head
`6d0a6043120880c696d0850e9242a16e6fb980a5`, already identifies the singular
coordinate-write swap and audits rounded-event/component-width interfaces.
Those are credited boundary controls here, not new discoveries. The mathematical
inputs and inherited compiler contributors are listed in NOTICE.md and the
independent review. Full PR bodies were used for this bounded overlap comparison;
these two predecessor proofs were not independently re-audited by the cut reviewer.

## Reproduction and result

The parent VERIFY.json runs both author and independent methods normally and
under optimized Python. The reviewer never imports the author audit. Retained
source bytes are authenticated with SHA256, Git blob identifiers and lengths.
The written induction supplies the universal implication under its hypotheses;
finite checks discriminate source and order errors. No selected assumption,
physical tariff, integer-recovery contract or kappa improvement is claimed.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
