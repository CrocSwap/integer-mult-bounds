# Independent review of the frozen two-channel hub obstruction

Reviewer: @CubeJerry with substantial OpenAI GPT-6 assistance, acting as the
caller-accounting worker in the same authorized research team. Date 2026-11-08.
This is local review evidence, not a separate research claim or full native proof.

Reviewed verifier SHA256:
`cba22ca6fa82e4476e95dee808408a46871640943c6edcaea3215ad111771d8b`.
Reviewed RESULT.json SHA256:
`08ca4c0f548d7d55e006781ca964a1ac9ea47503fc74bbee747771d8cb607753`.
The decoded native payload has SHA256
`d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`.
No issue was found in the reviewed linear-algebra or chronology implementation.

## Mathematical review

1. **The pure-space extraction is complete.** Give all coordinates outside G
   priority over coordinates in G, then use numerical label order within each
   class. The online elimination stores an echelon basis in this total order.
   Distinct outside-pivot rows cannot combine to a vector with zero outside
   coordinates: the earliest outside pivot appearing in a nonzero combination
   cannot cancel. Consequently every pure vector in the row span belongs to the
   span of the inside-pivot rows. Those rows are independent and already pure.
   Thus `pure_basis` computes span(rows) intersect Q^G, and does not merely
   delete contaminating coordinates.
2. **The Gram test supplies a necessary obstruction.** Any admissible C row is
   in the earlier collection pure space and any admissible D column is in the
   later delivery pure space. A unit-pivot requirement CD=I_r implies that the
   bilinear pairing of those two spaces has rank at least r. Checking all
   2-by-2 minors against one nonzero pivot exactly decides whether that rank is
   at most one over Q. Rank at least two would not itself construct a legal
   physical hub or favorable invoice. The proposed result uses necessity only.
3. **Critical cuts cover gaps conservatively.** Contact times and pivot interval
   endpoints are all included. For any cut strictly between consecutive critical
   times, the earlier endpoint has the same earlier collection rows, at least
   as many later delivery columns, and includes every pivot resident in the
   gap. Its relaxation therefore contains the gap's possibilities. Closed
   interval endpoints may overcount simultaneous availability; that weakens an
   exclusion and cannot create a false exclusion. Initial/final occupancy,
   both sides of MOVE, and its one legal midpoint are represented.
4. **All columns remain present.** Prefix rows begin with all 801 input axes;
   INIT/CLEAR erase only the actual target as specified. Reverse suffix columns
   begin with all 801 output axes; ADD updates the source adjoint and COPY both
   transfers and erases the overwritten destination. Purity tests include every
   non-G public and owned axis. I found no dirty-column truncation.
5. **Boundary and schedule restrictions are material.** The group G consists
   only of old helper labels with one common initial/final frame pair; the
   common intermediate frame belongs to the source's stored 1,095-frame
   catalogue and is a strict monotone intermediate subspace. The cut requires
   r distinct old G pivots simultaneously at that frame, including at most the
   one moving pivot at a source MOVE midpoint. Buffers remain at the common
   frame; original scalar contacts and event order are fixed. These restrictions
   are required for the stated conclusion. New frames, retimed native queries,
   transported buffers, mixed boundary groups and modified native scalar
   contacts remain outside the theorem. The author confirmed this scope.

The author reports all 77 boundary groups considered, 30 eligible groups checked,
and 4,296 critical cuts with pairing ranks 0 at 4,292 cuts and 1 at four cuts.
The other groups have fewer than two old eligible helpers or no strict
intermediate dimension. This review does not independently rerun the complete
4,296-cut census; it checks its mathematics and selected implementation evidence.

## Executed independent checks

Portable command from the repository root:

```
python3 -I -B research/p104-two-channel-hub/independent/check_review.py
```

Result: `PASS_INDEPENDENT_HUB_REVIEW` on Python 3.12.14. The portable review authenticates the exact reviewed parent verifier before
importing it only to obtain outputs for comparison; its dense Gaussian
rank and opposite-direction contact computations are independently written.

- 2,600 exhaustive triples of nonzero vectors in {-1,0,1}^3. An independent dense
  elimination checks that the returned pure-space dimension equals
  rank(A)-rank(A_outside), that all returned rows are pure and independent, and
  that appending them does not increase the original span.
- 34 prefix contact rows reconstructed by applying the adjoint backward through
  the event prefix, independently of the author's forward-row propagation.
- 34 suffix contact columns reconstructed by propagating a single vector forward
  through the event suffix, independently of the author's reverse-column pass.
  These cover deterministic time quantiles and both parity/owned-axis contacts.
  All comparisons retain every one of the 801 axes.
- The retained first nonzero Gram witness at frame 245, time2=26349, boundary
  (3,127), was directly rebuilt from its five collection vectors and thirteen
  delivery vectors. Independent dense elimination gives exact rank one.

The receipt is REVIEW-RESULT.json. Default replay compares it without writing;
`--emit` explicitly regenerates it. Any change to the reviewed parent verifier
fails the byte pin and requires renewed review. The reviewer made no changes to the author's
package, native word, shared files or source inputs. This review does not supply
an independent native Clifford/phase replay, a physical compiler proof, a legal
rank-two hub, or a new kappa.

## Residency-lemma addendum

The lead proposed, and this reviewer checked, a strengthening after the
finite review: arbitrary intermediate frames do not enlarge the eligible
rank-two cut set under the same frozen serial physical chronology. At a
source event boundary every old pivot has a stored chart. Inside one old
MOVE only its one role can visit a new frame. Two old pivots at a common F
therefore include a stationary old role and force F to be its stored frame.
Alternate names/bases for the same physical subspace do not create a new
subspace. The argument requires no extra old-role relocation or zero-header
retag, no overlapping/retimed MOVEs, and no transported or substituted buffer
pivots. These restrictions are stated in the strengthened proof. New frames
combined with changed pivot meetings remain outside the theorem.

No numerical code or receipt changes are needed, and the reviewed SHA256
bindings above remain unchanged. This addendum checks the finite reduction;
it does not broaden the review into a native-phase or compiler proof.
