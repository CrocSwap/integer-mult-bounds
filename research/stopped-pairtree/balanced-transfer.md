# Review of the completed stopped interface and balanced positional transfer

This review composes icekylinx's PR104, pinned at
`948ce1510df750f4c18b96bdaef436a86f8bf834`, with the balanced positional
layout used by PR34/RaD and restated in Rohan Arun's PR100, pinned at
`3dbe4e18a6a20f8115eb2f9a34a46254357d7791`. PR107 is an unchanged-interface
finite producer refinement. The inherited analytic and fixed-tape assumptions
remain required; a finite matrix test does not prove the streaming primitive.

## What completes before the outer layout invokes a bit operation

PR104's recursive primitive is the reversed atom interchange
`F_n(H,D)=(C_n D,C_n H)`. A single such call is not the ordinary interchange
required by the arbitrary-coordinate router. The complete chronological word

1. `D := D-H`;
2. `F_n`;
3. `D := D+H`;
4. `F_n`;
5. `D := H-D`

is ordinary interchange on every address, including all complete row and
spectator ranges. The two recursive invocations are sequential and restore
the same row reserve. Their constant multiplicity belongs outside the entire
recursion; it does not double its child histogram.

At a fixed invocation the atom width is constant throughout its recursion.
Peeling fewer than the fixed coarse arity atoms and stopping at a growing
atom width invoke the retained ordinary primitive. The final partial atom is
also handled by that ordinary primitive. Numerical radix padding has a fixed
volume factor and is removed only after the completed ordinary wrapper.
Therefore the outer caller sees arbitrary-width ordinary interchange and the
same complete-spectator/restored-row contract as the retained router.

`interface_check.py` independently verifies the full involution
factorization, physical lower adapter direction, its lift to multiple atoms,
module-basis and carry-boundary evaluations over Z/(101^w), and the complete
ordinary wrapper. Omitting the internal atom reversal is a rejecting control.
These checks establish finite algebra, not the asserted O(V) cost of one
ordered-affine atom update. That cost is the explicitly retained interface.

## All three row stocks remain necessary

During a complex child, its paid bit adapter may enter the coarse atom
recursion, which in turn invokes the retained ordinary leaf recursion.
Reserve

`Q = W_c^D_c * W_b^D_b * W_old^D_old`.

With the selected PR104 families the depth/width coefficients are
`17*28 + 16*28 + 9*28 = 1176`. The sufficient stock degree is 4000 and its
exact gap is `4000-(51/25)*1176 = 40024/25`. The eventual suffix allowance
is 16000 times the retained logarithmic term. Constant padding factors and
bounded depth offsets are covered by the eventual threshold. A two-factor
bridge validator cannot replace this calculation.

The balanced layout changes neither this product nor the physical position
of the complete row field. It uses one physically preceding transformed
prefix with one complete-row padding. Descendants preserve all parked and
spectator fields, and sequential wrappers/copies reuse the restored stock.

## Balanced prefix work

The PR34/PR100 layout processes the extra top FFT bit individually and uses
common named low-coordinate groups. Its extra prefix work is O(T p d), with
saving margin `1-epsilon`. The full axis/group permutations and inverses
still run through the paid ordinary arbitrary-coordinate router. The
geometric constraint `1-epsilon*(1+c)>0` remains necessary; it is not the
prefix-work margin of this layout. Local network gates, signed correction,
phase descriptors, and recursive frame schedules are not reordered by this
outer transfer.

For the rational-center complex family, the completed operator is still the
exact dyadic tensor operator, even though unfinished calls may contain odd
denominators. The common grid uses `21^K` with `K=G0*(D+1)` on the active
unfinished chain. Its invariant is a reachable-state invariant from root
dyadic inputs, not a claim about arbitrary finest-grid numerators. Completed
children preserve their incoming odd exponent. Initial/final scaling adds
O(log d) record bits and O(V log d) outer work, covered by the positive gaps
and the existing C1=1 semantic bound. No return rounding is introduced.

Consequently the completed stopped ordinary bit primitive and exact
rational-center complex primitive meet the interfaces needed by the balanced
layout, conditional on PR104's written atom-streaming proof and all retained
analytic/tape contracts. The selected numerical instance must independently
recompute the three-factor bridge, all 47 constraints, and all seven margins.
