# Finite composition and unit readout decomposition

The scalar DAG and replay routine are copied byte-for-byte from eumemic's PR117 at cbb05ce504d571546d9b7794c186a613c659c3bf. Its support checks establish the same triple-disjoint, pair-star and 24 retained center outputs, with decoder denominator 21. PR116's inherited PR110 deferral construction is applied to that DAG with its lexicographic pair-star root order. All matching eligibility, lifted frame, untouched-prefix, dirty-scratch and rank-mass checks are retained. This composition changes the physical schedule's readout placement; it does not add the savings of two different schedules.

## Why the old coefficient check failed

The old readout is the transpose-propagated row JL acting on arbitrary initial scratch. Even though the fresh-source DAG is cancellation-free, different scratch paths can combine into a readout coefficient larger than one. For the selected graph, independent exact integer expansion finds a largest numerator magnitude of 55 over the common denominator 42. The previous PR116 audit required a numerator magnitude at most 42. That assertion correctly fails on the new graph. Random finite-field replay and a contracting moment alone do not establish the missing scalar implementation.

## Exact replacement by bounded shears

For every expanded coefficient n/42, write |n| = 42q+r with 0 <= r < 42. Replace its shear by q shears with coefficient sign(n), followed, when r is nonzero, by one shear with coefficient sign(n) r/42. The selected witness is checked exhaustively to require at most two pieces for every coefficient. The implementation verifies their exact integer sum and that each piece has magnitude at most one. In particular 55/42 becomes 1 + 13/42. Zero coefficients produce no operation.

These shears share the same source port, target port and frame. If E is the source-to-target elementary off-diagonal matrix, E^2=0, so (I+aE)(I+bE)=I+(a+b)E. Thus splitting preserves the map over the exact rational coefficient ring, for arbitrary dirty data. Its inverse negates the coefficients in reverse order; the reflected schedule swaps the ports and complements the unchanged frames as before. Consecutive pieces introduce no frame transition and hence no additional recursive child. Their odd denominator still divides 21, so the retained fixed odd-denominator grid applies.

The audit independently expands every old readout coefficient, verifies its decomposition, charges each actual piece in both literal directions, checks frame continuity, and requires exactly the same complete child histogram and rank sum. The audit also retains the wrong-inverse-sign, uncomplemented-frame and wrong-signed-root controls. Additional controls reject an unpaid third piece, a dropped fractional piece, an oversized unsplit shear, and a wrong sign, and verify exact shear/inverse action on arbitrary rational dirty values.

## Paid scalar accounting

Let C=2 be the audited maximum number of pieces, and let c,R,q,v,h denote the actual circuit quantities. We conservatively multiply the entire previous scalar bound by C, rather than charging only the split readouts:

    local = C * 8 * (c + 2R + (R+q)v(h+1) + h^2 + h + 1)
    G = N + 2v * local.

The independent literal audit checks its expanded scalar count against this bound. The exact certificate recomputes E, the literal charge, B, C0, the induction gaps and all row/cutoff quantities using this G. All 47 strict constraints and seven margins must still hold. The complete recursive profile, strict bit/complex savings and final kappa are unchanged by this additional scalar work; the certificate verifies this rather than assuming it.

## Proof boundary and attribution

This is a finite conditional construction. The opposite-bank factorization, nondegenerate residual-to-child rule (including permitted alternating residuals), stopped atom streaming, common rational/odd-denominator interfaces, analytic transfer and fixed-tape assumptions remain the inherited written interfaces. Finite tests are not a formal proof of those general interfaces or a claim of global optimality.

Credit eumemic for PR117's DAG and PR114's accounting, Avi Eisenberg for PR110's deferral construction, Rohan Arun's PR116 integration, Swapnil Jain's round-seven bit word, icekylinx's stopped-product and rational-center interfaces, and all predecessors retained in the original notices. The composition was supplied with Anthropic Claude assistance. The independent audit, failure diagnosis, unit-shear correction and verification were prepared by Rohan Arun with OpenAI Codex assistance.
