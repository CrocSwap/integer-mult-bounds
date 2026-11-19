# Verification record

The claim is a uniform algebraic algorithm. Its proof uses full flank independence, finite projective entry ratios and an exact residual over every tensor coordinate. The large support guarantees are proved from projector row sums. The largest support exercised by an executable is much smaller than the counts in the theorem.

Three separate OpenAI Codex reviewers tested the mathematical design and the implementation. These are separate computations within the same model family. No independent human or formal-kernel acceptance is claimed.

| Attack or independent check | Observed result |
|---|---|
| Recover from an unlabelled parity program with destructive interference | At widths 13, 25 and 27 the program returns all 19 expected matrices and Gaussian-rational coefficients. At width 13 a cap of 18 rejects the observation. The all-zero observation entry vanishes. |
| Compare with a different membership algorithm | The registered dense oracle enumerates all 24 one-qubit matrices and all 276 pairs. It compares every one of 64 coordinates against solutions from exact integer minors. On 140 dense tensors, 56 positive decisions and 224 rejections agree with the decoder. |
| Fool the pivot and cut equations | The tensor z⊗I⊗z with z=(1,1,0,0) permits the identity as a cut candidate. A full coordinate disagrees. The final equality test rejects it. |
| Hide cancellation in redundant states | A 41-state train had 21 reachable directions on each side and flattening rank one. At width 19 its full-span certificate recovered coefficient 4^19. An explicit cap of zero correctly withheld that certificate. The registered suite includes a smaller cut with the same cancellation. |
| Change internal coordinates or phase conventions | A separate script recovered all 276 one-qubit pairs through hidden gauges. Four-qubit tests used disjoint pivot positions, five support heights and large unused bond indices. A width-27 product-family test recovered all 96 normalized coefficients. |
| Attack the Clifford predicate | A phase diagonal with a cubic Boolean term is unitary and preserves Z. Its X image fails the Pauli test. The independent four-qubit real-sign census accepts exactly 1,024 of 32,768 normalized sign diagonals, matching the quadratic Boolean construction. |
| Check the character calculation below the global threshold | The original release, ordinary table member, 81 projected rows and 324 character values match their source pins. Integer or quadratic-surd comparisons bracket each cutoff on both sides. A literal one-qubit fourth-power calculation has a one-dimensional nullspace and all 24 single-column deletions have rank 23. |
| Stress the bit model | A valid 5,208-digit output exposed a default runtime conversion limit. The public reader and writer now use bounded decimal chunks. Exponential notation is outside the input grammar. The registered test verifies the exact large coefficient. Repeated sites count once per occurrence in the bit-cost proof. |

The dense oracle, Pauli census, flank certificates and principal end-to-end controls are registered in [VERIFY.json](VERIFY.json). Extra adversarial runs corroborate those tests. [Recovery proof](PROOF.md) · [Support proof](SUPPORT.md) · [Source pins](SOURCE-PINS.json)

The complete four-qubit group was not enumerated. The dense 2^104-coordinate example was not expanded. The program instead verifies a zero residual using reachable linear spans. Runtime at the million-label cutoffs, approximate-data recovery, reversible tape costs, supplier installation and a complete multiplication improvement remain unverified. None of the 100 unchanged historical package suites, the selected cold replay, Lean or Docker was required for this construction.
