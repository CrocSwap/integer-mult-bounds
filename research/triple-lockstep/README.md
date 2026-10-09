# PR #139 correction: the proposed triple-core lockstep is invalid

**Retracted:** the proposed conditional kappa 0.00045019844704 is NOT an established bound, nor does its rank-3r child histogram correspond to a valid physical shared-scratch implementation. This branch is now a **negative-control research artifact**, not a new multiplication exponent.

## Reviewer feedback and exact counterexample

Swapnil Jain identified the fundamental interference in PR #139:
https://github.com/CrocSwap/integer-mult-bounds/pull/139#issuecomment-6073712785

The same issue was independently replayed and acknowledged by ikeboy, who retracted PR #132:
https://github.com/CrocSwap/integer-mult-bounds/pull/132#issuecomment-6073596754

The local core's address frame labels identify directions in one **shared physical stream**. Orthogonality of those labels does NOT create disjoint physical storage. When all cores' source contributions are live simultaneously, each readout receives other cores' sources. A joint rank-3r Clifford child may equal the *product* of the three individual frame transforms, but that algebra does not validate the interleaved scalar schedule.

For one dirty auxiliary stream z and three inputs x1,x2,x3, the transparent macro for core i is:

    yi -= z;  z += xi;  yi += z;  z -= xi

Executed **consecutively**, each yi receives only xi and z is restored. Executed **lockstep**, all three initial yi subtractions occur before any xi is removed; each receives x1+x2+x3, with contributions from both other cores.

The new executable regression uses exact Q(i) arithmetic (Python Fraction), 64 address entries, nontrivial Clifford C and its inverse on three orthogonal two-coordinate active blocks. It independently verifies the frame gates commute and all scratch is restored. All 3 x 64 target entries are nevertheless incorrect under lockstep; the consecutive schedule has 0 target errors.

This counterexample tests the claimed **shared-dirty scheduling principle**, not every PR137 circuit gate. Along with the cited PR #132 independent replay, it is sufficient to invalidate the submitted lockstep *justification*. Retaining separate data-front child charges cannot repair values already mixed in the shared auxiliary streams.

## Implemented fix: no unsupported merged children

The executable certificate has been replaced. It **does not build or accept** the optimistic triple-lockstep rank histogram. Instead it imports and recomputes the original frozen PR #137 sequential three-core certificate, checks its complete 47 strict inequalities and 7 margins, and requires its original 9 separate local word copies to remain paid.

Safe reference (under PR137 inherited conditional contracts):

- ambient dimension 72
- physical streams per three-vertex cell: 91,935
- recursive rank mass: 6,612,144
- deficit: 7,176
- largest recursive child: 66
- PR137 conditional kappa: **0.000413596233702**

PR #138 separately refines the slack parameters, reporting kappa **0.000413596659368**, which is HIGHER than this inherited PR137 baseline.

**No new higher kappa is claimed on this branch.**

## Reproduce

    python3 research/triple-lockstep/lockstep_counterexample.py
    python3 research/triple-lockstep/certificate.py

CI now runs the exact negative control and the inherited sequential check, and fails if the lockstep corruption disappears unexpectedly. The PR137 source package, licenses and compiler remain unchanged.

## Work needed for an actual improvement

A new construction would require an *explicit* alternative way of maintaining independent live data in shared auxiliary storage (or provably paid cancellation), with a full literal signed forward/reflected and arbitrary-dirty replay. The physical schedule must be certified **before** replacing 3 rank-r children by rank-3r children in the recurrence. A new exponent additionally needs the full positive moment and assembly accounting.

This PR remains a Draft negative control and must not be merged as a new bound. Thanks to Swapnil Jain and ikeboy for the counterexample and acknowledgement. Original PR137/PR130/PR124 author attributions and licenses are retained; this correction and regression were prepared with OpenAI assistance.
