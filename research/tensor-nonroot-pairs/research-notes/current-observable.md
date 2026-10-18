# Observable-state gate deletion: sufficient rule and bounded PR473 screen

Status: no positive candidate; no new kappa claimed. No source word was modified.

## Exact sufficient scalar rule
Let A be an invertible linear helper-building network over F2, using read-only sources and dirty helpers. Let the following centre/scatter and delivery network write only target registers. Let C=A^{-1} restore helper/source registers after the target outputs have been produced. At any A gate d += sum(sources), propagate the target projection backwards through the complete suffix (deliveries, centre/scatter and remaining A gates). Denote its column for destination d by R_d.

If R_d=0, deleting this gate leaves every target output unchanged for every initial source, target and helper value. This follows directly from the rank-one difference of the two prefix states: only coordinate d differs immediately after the deleted gate, and the remaining target map kills that difference. Replacing C by the inverse of the modified A restores every helper and source. Thus the full scalar arbitrary-dirty endpoint identity is preserved, with initial compensation unchanged. This is a sufficient deletion construction, not a necessary obstruction.

A framed implementation still must check monotone frame visits, all operand spans, updated centre dimensions, and the complete paid child profile. No claim that scalar invisibility makes physical transport free is used. If the modified word passes those existing exact interface checks, it is a valid provider replacement with that measured profile.

## Bounded native screen
observable.cpp propagates 120-bit response columns exactly through B backwards, adds the centre/scatter contributions, then traverses A backwards. It tested each of 2926 gates of pinned PR473. Every destination response was nonzero: zero eligible deletions. This is only exhaustion of the single-gate response-null protocol. It does not exclude paired rewrites, source changes, or different basis representations.

The executable also contains a floating-rank paid-profile screen for potential candidates; because none survived the exact response test, that profile code did not establish any new witness or enter a claimed exact price. Source kernel entrances and all public words remain unchanged.

## Actual library analogy
Problem18AnchorInvariantCoordinates20261001.lean, conjugated_gram_blocks (line15) and invariant_forces_cross_zero (line31), uses invariant block coordinates to force cross-action to vanish. This motivates isolating invisible directions, but that Lean theorem does not prove this circuit rewrite or its costs. No Lean certification was performed here.

## Other bounded routes
The preceding round's exact source-assisted virgin protocol has no compatible nonzero-response helper sites on470. Its sufficient affine-controller identity remains saved in D:/proof/research/kappa-next-tensor-20261011/bit/SUMMARY.md; physical inter-stage response transport has not been instantiated. No gain is attributed to it.

PR475 complementary FFT reservoirs removes particular complete-FFT reservation/top-bit terms. Its proof expressly retains Gaussian/scalar constraints and claims no numerical kappa. It therefore supplies no immediate paid bit-supplier improvement to combine in this lane.

Additional exact check: although C is not the literal reversed A event list (commuting source summands are ordered differently), scalar A followed by C is the identity on all955 formal columns. A writes only helpers; B writes only targets. These source conditions were checked directly on the pinned word.
