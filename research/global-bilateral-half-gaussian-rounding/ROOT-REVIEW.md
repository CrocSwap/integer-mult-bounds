# Root review of the global half-unit rounding theorem

## Exact scope and proof review

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. This review concerns a global arithmetic bijection on `Z^4`, not admission to a selected physical caller.

The root checked the proof's complete coset maps, their surjectivity, the partner-score involution and tie rule, both staggered phases, signs and the central pair. The lower endpoint inequality uses two coordinates in each phase; a one-versus-three split cannot be substituted. The root separately checked the unrestricted 16-corner lower bound and both directional attaining sequences. No unproved infinite Hall matching theorem is needed for the construction: the matching is given explicitly.

The Gaussian transfer is `F_C=L^-1 F_H S`, with inverse `S F_H^-1 L`. The root rejected the stronger interpretation that complex conjugation of `F_C` is its inverse, and retained a concrete counterexample. The final proof states the actual inverse. Four failed native identities remain visible in the main verifier.

## Independent evidence and limits

- Proof role: universal argument plus independent matrix, exact-corner and attaining-family checks, without importing the root or implementation-role arithmetic. Its final proof SHA256 is `1b7bf1e00a3b9dc44ff603222423c94bba15cc9450df6483601f328993cfdf42`.
- Implementation role: 65,536 half-grid inputs, including 27,136 ties and 15,360 central cases; complete odd subsets of balls of squared radii 25, 81 and 121; large-integer round trips and exact radial checks. Its source is `review/independent/mechanism_check.py`.
- Root arithmetic: 38,416 half-grid box cases, 28,561 integer cube inputs with distinct images, 120 seeded cases through 400 decimal digits, and exact directional sequences. Three negative designs are detected: unstaggered pairing, unequal phase counts, and selection by current magnitude rather than invariant score.
- Public kernel: compared to the separately written root arithmetic on 6,561 cube inputs and 60 seeded inputs through 4,096 bits. Both inverses, exact errors, parity and the radial allowance are checked. Twenty-eight malformed public inputs are rejected. Gaussian interface tests cover 2,401 inputs and four exact failed-identity controls.

The root and implementation roles shared the proposed mathematical formulas, but did not share their arithmetic code when writing their first checks. The public kernel is subsequently extracted from the implementation role, so its comparison to that same role is provenance/regression, not independent implementation evidence. Independence is supplied by the root arithmetic and the separate written proof. No human review or formal-kernel certification is claimed.

Normal and optimized Python executions have been used to ensure that required checks are not silently lost under `-O`. Final package replay and integrity receipts record the exact publication bytes. The main proof, rather than any finite test count, establishes the universal theorem.

## Full-system relevance and remaining cost gate

The kernel needs only a fixed amount of integer arithmetic on one Gaussian pair. A direct tensor application would still require its complete number of scalar fields, bit widths, head movement, copying, inverse/restoration work and error propagation to be charged. The run's separate selected-tariff audit shows that a serial `f V` monomial implementation cannot simply inherit the selected nonleaf sublinear-in-`f` tariff. This package makes no claim to solve that problem.

The current result is an alternative rounding sub-lemma relevant to `precision_tape` and `native_all_columns`. It neither discharges an entire selected assumption nor improves the assembled multiplication exponent. In particular, the optimal **bilateral** constant does not prove the optimal **forward-only** constant, and lack of the stronger identities is not silently repaired by treating a nonlinear rounder as a tensor-linear map.

## Novelty and sources

The bounded overlap search inspected the exact #6509 and #6619 proofs, the earlier norm/finite-ball obstruction family, current PR metadata and terms concerning half-unit, radial, nonperiodic and bijective rounding. It found no identical global construction within that inspected scope. `review/root/OVERLAP-METADATA.json` and `proof/OVERLAP.json` preserve coverage and uncertainty. This is a recorded search boundary, not a proof of priority.

The separate finite Hall package at commit `58a8facd7fbae9212774925349fbb617f114f040` supplies the optional comparison lower bound `sqrt(78)-sqrt(73)`. The present global construction, its inverse and its bilateral optimum do not execute or depend on that finite certificate.
