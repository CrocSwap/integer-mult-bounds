# Community review: stopped recursion and paired-cube fast track

Maintainer review with OpenAI Codex assistance, 2026-10-09. This is a
construction and dependency review, not independent human peer review or a
formal proof of integer multiplication. Main remains at
`56b66d58297deca1d7dd130247d720e960f77a37`. No PR was merged or public review
posted in this pass.

## Fast-track disposition

[PR #144](https://github.com/CrocSwap/integer-mult-bounds/pull/144), by
**icekylinx**, was reviewed at
`c8b22bc5c10dba497ac25804e27d9647d818e2ff`. Its conditional witness is

\[
\kappa=4609169/10^{10}=0.0004609169.
\]

**The scoped construction audit passes, with two small integration fixes
prepared.** The new finite construction, exact moments and written transfer
arguments support accepting this conditional witness under the retained
analytic, semantic, ordinary-leaf and fixed-tape interfaces. This does not
independently establish those upstream interfaces. The value is about 9.03
times the currently selected main saving, approximately `2^-11.0832`; it
exceeds `2^-12` but remains below `2^-11`. It is not yet main's selected
witness or a published release.

Apply [the review patch](../../research/pr-review-20261009/pr144-review-fixes.patch)
when integrating. It adds an optimized-interpreter guard to the new bit
checker, corrects one inverse-sign sentence, and updates only the two
affected certificate source hashes. All mathematical certificate fields
remain unchanged. The patch applies cleanly to the reviewed snapshot.

The [validation receipt](community-round6-validation.json) separates local
reconstruction, independent controls, inspected Linux CI and proof review.

## What was checked locally

The selected complex producer was rebuilt from the pinned PR117 restrictions
and frozen carrier arcs. Its independent finite checker passed all 3,097,600
source/target scalar entries, the cube involution, actual source itinerary,
conservative supports, complete backward/carrier intersections, signed
physical mixer, copied-center closure, selected-gauge intersections and
reverse target chains. Every regenerated profile field equals the submitted
certificate. The original thirty certificate source hashes also match.

Additional maintainer controls, without importing the submitted algebra or
moment implementation, passed:

- 84 exact weighted factorization cases over `Z/9`, `Z/25` and `Z/27`.
  These include 1,116 nonzero nonunit matrix entries. Omitting the cross
  shear changes the map in 60 cases.
- 4,770 frame-distance identities and 5,259 dirty-tail identities,
  exhaustive on subspaces in dimensions two through four, including 36
  degenerate subspaces. These check binary geometry, not exact complex phases.
- Three arbitrary-dirty integer-vector replays of the actual 26,417-role,
  49,424-operation signed mixer. All dirty values restore and the target
  receives the original source. The same-sign inverse fails all three controls.
- Independently reconstructed complete child inventories and interval moments
  using main's maintainer enclosure code. Including the entire rare-class
  fallback, the bit gap exceeds `1.4390e-10`; the complex gap exceeds
  `2.0097e-10`. The slightly stronger enclosures are validation evidence,
  not a newly selected exponent.
- The stopped bit saving, seven final margins, 47 positive submitted slacks,
  full group order and external reserve. The final strict absorption gap is
  approximately `9.94540904346e-11`. The next `1e-10` grid point is too large
  for this parameter witness.

The new checker guard and existing producer/network guards reject twelve
optimized execution modes across `-O`, `-OO`, `PYTHONOPTIMIZE=1` and `=2`,
without writing an output. Normal bit-checker help still works. These tests
cover the prepared guard patch; they are not a fresh full bit reconstruction.

## Remote evidence and the local replay limit

The exact head has 45 successful jobs in
[run 37883309807](https://github.com/icekylinx/integer-mult-bounds/actions/runs/37883309807),
including paired-cube and three-stage-cover jobs on Python 3.11, 3.13 and 3.14.
The Python 3.13 paired-cube job log was inspected: it checks out the exact
reviewed SHA, runs the producer, reconstructs the selected bit subset with
source hashes, and runs the final certificate/47-constraint check successfully.
Passing historical Lean jobs does not formally verify this new theorem.

One 1,524,681-byte compressed inherited bit witness,
`references/partial-gauge/pr97/deferred_23.json.gz`, could not be downloaded
through the connector. Blob verification detected its absence. Browser
retrieval was denied and was not retried. Thus **the selected bit reconstruction
was checked through inspected, head-pinned CI, not rerun locally**. The
underlying unchanged full bit/frame/lifted audit also has the previously
inspected exact-PR97 CI evidence documented in round five. No missing file
was fabricated and no source check was bypassed to manufacture a local pass.

## Written proof audit

The review included the new paired-cube construction/sharing/assembly notes,
the inherited arbitrary-subspace Clifford interface, the weighted local-ring
compiler and borrowed-row wrapper from #130, and the stopped compiler from
#104. Relevant ordered-affine stream hypotheses were compared with the
upstream statement and its fiber-cost proof.

For the complex construction, degenerate subspaces are represented by
Lagrangians, rather than an unavailable orthogonal projector. The preimage
distance formula and the direct-complement tail argument give the claimed
ranks. Exact Gaussian-dyadic lifts, rank-zero adapters and source Pauli
corrections remain required. Binary equality alone is not used to discard
their phases. The signed cube operator executes on the original sources at
common frames; those sources restore before inverse cleanup. Conservative
supports are retained even when scalar coefficients cancel.

Completed-core sharing is valid because each stage restores its arbitrary
logical auxiliary, giving an explicit raw operator `F_A T_sigma^-1` or its
inverse. A physical auxiliary may enter the next core with a new logical
interpretation. The three relative actions occupy orthogonal blocks; the
final width-`3 dim(sigma)` correction, data rank-two complements, all internal
operations and the full finite routing/row stock remain charged. This is
not sharing an unfinished producer with unknown residual dirty contents.

On the bit side, the weighted residual's generic factorization retains unit
pivots as child weights, avoiding an uncharged variable scaling. Split-rank
factorization is over the local ring, not merely its residue field. The
bad-class Gaussian elimination uses unit pivots and pays the complete
`32m^2` fallback; nonunits are not discarded. Both characteristic and rank
moments contract. The low-residue genericity bound applies per edge, so the
moment does not require a simultaneous good event for all edge types.

The growing high-matrix cover is batched within each fixed low role type;
its cardinality cancels from normalized volume but its digits are charged
in the `O(w log e)` reserve. Fresh role coordinates are separate from
ancestor-dependent weights. Generated descriptors take polynomial time in
`w`; the ordered-affine proof absorbs this preparation within the complete
target fiber. No arbitrary-function oracle is assumed. The fallback
ordinary swaps and weighted leaves include their reversal calls.

The ordinary two-call wrapper restores rows. Borrowed leading digits supply
its internal selector stock, with padding once outside the recursion and
an old-supplier swap of the borrowed high chunks at the end. Thus neither
padding nor the wrapper's two calls multiplies the characteristic moment.
The final binary-range embedding is invariant only at the completed endpoint,
which is sufficient for removing the outer padding.

Finally, the full complex group/router charge and numerator-bitlength bound
pay the signed dirty-response matrix. The common denominator-three grid
charges unfinished active depth, and completed children preserve the odd
exponent. Exact completion, not intermediate cancellation, justifies outer
unscaling. These remain written proof arguments, not conclusions supplied
by a finite arithmetic script.

## The two integration fixes

`paired_cube_bit.py` imports a source-pinned routine whose frame-chain
assertions disappear under optimized Python. The new entry point had no
guard. Add an explicit module-level rejection before imports. Normal-Python
CI is unaffected; this is verifier hardening, not an exponent counterexample.

The construction note says a signed addition is undone with the same sign.
For `a <- a + epsilon*b` its inverse subtracts `epsilon*b`. More generally,
`a <- ca*a + cb*b`, with signed-unit `ca,cb`, has inverse
`a <- ca*a - ca*cb*b`. The displayed dirty-word formula already uses
`M^-1`; the correction makes its elementary implementation unambiguous.
The independent dirty-word replay checks that corrected convention.

## Attribution and earlier work completed in this pass

Preserve icekylinx's new paired-cube motif, weighted compiler lineage and
integration credit; **an664's #128 completed-core sharing** is a substantial
dependency. **eumemic's #117** supplies the restricted positive producer;
**Zhihao Chen's #97** supplies the physical deferred bit ledger; **Swapnil
Jain** supplies its underlying frozen word and lifted frames. Keep all
existing notices, earlier framework contributions and AI-assistance
disclosures in the submitted provenance. Reviewing #144 does not accept
every independent claim in those contributors' other PRs.

[PR #104](https://github.com/CrocSwap/integer-mult-bounds/pull/104), head
`948ce1510df750f4c18b96bdaef436a86f8bf834`, passed its local stopped-product
target, six optimized-entry controls, independent inventory/moment checks,
30 exact rational/tensor factorization controls and 6,732 complete modular
wrapper addresses. Its 36 CI jobs passed. The written factorization,
precision grid and reserve were reviewed; no additional blocker was found.

For #97, the previously requested guard repair is now a concrete
[ten-file patch](../../research/pr-review-20261009/pr97-verifier-hardening.patch).
Its three tests pass, including 28 optimized execution cases and bad-pin
rejection. Five available normal drivers replay unchanged mathematical
payloads; the staircase check and its negative control pass. All available
source pins match. The same missing compressed bit input limits fresh local
replay; the distinction from existing CI evidence remains explicit.

The queue should resume by integrating these exact reviewed changes with
credit, then processing remaining dependency batches. A new submission or
changed head needs its own delta review. This pass did not start an overnight
goal or authorize posting an announcement on the user's behalf.
