# Minimal rounded binding test specification — not executed

Purpose: discriminate the proposed two-Tensor finite parent schedule from wrong reflection, inverse sign, normalization, dyadic scales or a rounded-linearity substitution. This specification does not authorize an implementation, factory run, native child, emitter or PR. Ownership/overlap remains with the coordinator.

## Frozen configuration and separate claims

Use exactly the source's existing reduced source box (5,7), target box (8,8), p48/P80 catalogue for **staged conformance only**, with b=8 and q≤18. It has S=35, coprime odd source axes, nontrivial first-axis dilation8 mod5=3, p≥b+2, S<2^b and 2q−1≤S. Preserve the source's `require_recovery=False` diagnostic policy. The source's default production entry must continue to reject this reduced catalogue.

Do not label recovered diagnostic bits a guaranteed product. A later production correctness test requires source-produced pages and the full production catalogue/approximation premises as well as (G). Raising p at fixed (5,7) supplies no such production admission. A separately supplied-approximation recovery test can test the scalar guard/leaf, but cannot stand in for a produced Tensor return.

## Small operand set

Use two distinct borrowed digit tapes and the same q on both, including zero digits as needed. A compact set is:

1. Independent nonzero impulses at different positions, including a nonzero CRT coordinate; e.g. q=3, first digits `(0,1,0)`, second `(0,0,2)`. This makes the desired convolution and reflection distinguishable.
2. A short mixed asymmetric pair, e.g. q=4, `(255,0,3,17)` versus `(1,254,0,9)`, with both operand tapes varied independently.
3. Zero on one tape and a nonzero asymmetric sequence on the other; then interchange their roles. The zero-product case alone is insufficient.

The test must retain every S coefficient and both real/imaginary components before recovery, not merely a scalar sum or the final integer bits.

## Required schedule and references

1. Run both original ingress/CRT conversions separately; verify that each input tape is restored and the converted values remain real exact p-grid quarter-disk arrays. Form one new owned packed bank from their real components. Its unused imaginary zeros are not independent new target credit.
2. Invoke the actual complete Tensor once on that packed bank. Preserve the literal returned numerators and actual source coordinate order. Do not replace this call with separately rounded Tensor(u)+iTensor(v).
3. Pair each returned j with Jj=(−j0 mod5,−j1 mod7). Count the routing, copies and cursor restorations. The only fixed point is (0,0); write it once. Produce Atilde,Btilde with exact halves using one explicitly declared representation: raw grid p+1 with final product shift p+2, or source-parity justified exact numerator division by2 with p-grid product shift p.
4. Compute the widened exact complex product and perform one inward component truncation to grid p. Record actual input norms to the opposite call. Clear all consumed packed/split/routing banks according to ownership rules.
5. Invoke the same actual Tensor with `opposite=True`; run unchanged recovery, widened inverse CRT and carries as a diagnostic. Assert exactly two Tensor calls, three CRT conversions, and no surviving owned scratch or cursor changes to borrowed inputs.
6. Compare physical packed forward and opposite returns against separately implemented staged references run on the **same packed input and same computed product**. Do not use rounded linearity as the oracle. Compare the exact ideal Fourier/convolution identity separately using rigorous root enclosures or an exact cyclotomic representation in the source coordinate basis. These are different claims and must have separate outputs.

The staged reference can match physical operation semantics without meeting the ideal epsilon bound. Report that distinction and any recovery discrepancy visibly.

## Discriminating mutations and controls

* Replace J by the identity on a nonzero pair; at least one split array/complete product must disagree with the exact identity. Zero frequency is not sufficient to exercise this mutation.
* Omit complex conjugation, reverse the sign of division by i, use the wrong opposite sign, and use R^-1 in place of the source's same R. The (5,7)/(8,8) geometry has R²≠I, so the permutation mutation is observable.
* Omit one S recovery multiplier or apply gamma restoration a second time. Recovering the same final bits on a zero input is not evidence that either mutant is detected.
* For the raw split-sum representation only, reuse shift p rather than p+2; the p=8 scalar control H_j=H_Jj=(32+16i)/256 gives correct product numerator2 versus wrong8. If exact halves were first taken on the original grid, shift p is correct and must not be rejected.
* Verify an actual half-sum of odd arbitrary p-grid numerators uses the widened grid exactly. Separately verify that actual source-restored returns are divisible by2^gamma and therefore admit the exact-halves alternative.
* Break the real-input premise explicitly: in an exact oracle control take u=iδ0/16, v=δ0/16. Packing gives h=iδ0/8; the real-input split would return A=0, whereas Tu is nonzero, and the desired product is nonzero. Label this an expected failure outside the digit-input contract.
* Test synthetic scalar guard values strictly below, exactly at, and above C(3epsilon+2h_p)=1/2. Equality must reject. A scalar synthetic test is not a production catalogue or a claim that its chosen epsilon equals a source E2^gamma h_p.

Correlated forward errors must remain allowed. An optional exact-dyadic perturbation test may alter one reflected pair with a common complex error to exercise that case; it must not impose independence between Atilde and Btilde errors. If any split bank is rounded, the tester must include and rederive its additional error instead of silently using the present same-(G) proof.

## Required receipt and stopping rule

The receipt must pin every source/catalogue byte; report all component scales and widened word bounds; retain exact stage arrays or raw source-bound hashes; count packed-bank writes, J routing, exact half arithmetic, real word products, temporary storage and cleanup; report both independent input tapes and all helper/cursor restoration. Complete child preparation and catalogue scans stay in the bill.

Any wrong endpoint, unsafe boundary, missing return or unaccounted operation stops the physical saving claim. A staged-conformance pass establishes that finite schedule only. Production accuracy, total cost improvement and recursive/asymptotic admission remain separate and unproved.
