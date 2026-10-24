# Register coalescing with explicit frame restoration

This is a sufficient compiler transformation, not an achieved kappa gain.

Let an existing verified frame transition from E to F, E contained in F, implement the exact invertible operator U(F) U(E)^(-1) with one rank-d recursive child and its existing coordinate/monomial wrappers, where d=dim(F)-dim(E). The reverse transition is implemented by reversing that exact circuit and replacing its rank-d child by its inverse. For the normalized complex child C, C^(-1)=X C since C^2=X and X^2=I; therefore the inverse uses one rank-d child plus an explicitly charged translation and reversed wrappers. This does not make a downward frame change free. The exact all-column equation is U(E) U(F)^(-1), so composing it with the forward prefix changes the frame label correctly on arbitrary register contents.

Any scalar elementary operation at a common frame remains legal after this restoration. A proposed register coalescing must additionally provide an invertible change of basis on the reused registers, preserve every still-live source, rebuild both forward and dual dirty-data compensation from the actual scalar word, and pay all reverse wrappers and translations. Those are concrete finite circuit checks, not consequences of a clean-input row calculation alone.

For a frame path with total upward dimension u and downward dimension d, the sum of recursive ranks is u+d = (final dimension - initial dimension)+2d. Thus 112 independent dimension-one descents incur 224 additional local rank units. Across 72 invocations this is 16,128 units. Removing a logical helper ordinarily returns its formerly hosted pending coordinates to the idle remainder; it does not by itself create rank deficit. Against the inherited deficit 2,496, the naive 112-descent substitution is not a viable profile without additional genuine rank savings.

## Exact restricted gate

`coalescing_gate.py` replays the pinned PR507 constructor to the checkpoint immediately before coordinate totals. `COALESCING-GATE.json` preserves every retired row and frame, every intended own tetrad, and the target access tests.

All fourteen blocks have twelve retired rows already at rank-three face frames. None of those 168 frames is contained in either corresponding own-output tetrad frame. More strongly, none of the current packet output frames or retired frames is contained in any of the eight own-target hyperplanes of its block. The apparent rank-two opportunity exists earlier, at the snapshot point, before the face assembly raises these rows. Therefore deleting snapshots and merely reusing the later retired stock is invalid without a paid nonmonotone transition. This test does not exclude a redesigned packet assembly or a different early live-range allocation.

## Reusable source connections

The precise analogue is injective live-register renaming with a frame invariant, rather than reuse based on equal clean values alone. OpenAI `WLIdentification/WordCommands.lean`, `StackModel.Command.Exec.rename`, and P18 `Problem18IMPAssignments20261002.run_framed` were identified and source-inspected by the kernel lane; their hashes and audit scope are in that lane's `KERNEL-SOURCE-HASHES.json`. They do not automatically certify the new complex circuit. Our earlier inspected `Slots.restoreMemory`, `effects_argsCode`, and `Word.matrix_substitute` similarly supply the structural pattern: exact state restoration, preserved outside state, and additive replacement cost.
