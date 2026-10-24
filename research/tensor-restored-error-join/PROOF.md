# A conditional restored Tensor error guard with suffix contraction

DONE / scoped finding — the downstream error join requested after [PR #5295](https://github.com/CrocSwap/integer-mult-bounds/pull/5295) is complete at the conditional analytic level. The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19150254) is released. The source production accuracy, primitive and physical premises remain explicit. No policy, supplier or kappa is changed.

Let h=2^-p, D>=1 be the number of expansion/compression axes, M=2^A the chirp ratio, beta=21/38, a=sqrt(2)+2^-11, and gamma the actual final restoration exponent. The [new expansion proof](https://github.com/CrocSwap/integer-mult-bounds/blob/351975ee703ec5aa1b18f70f73700d434026199a/research/tensor-expansion-accuracy/PROOF.md) gives error below a(1-beta^D)/(1-beta) h. The [normalized chirp](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/physical-chirp-middle/PROOF.md) has exact sup norm at most 1 and local defect below (4 sqrt(2)2^A+22)h. The [original-coordinate compression result](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/tensor-compression-error-refinement/PROOF.md) gives norm at most 1/8 and local defect below 2h at each computed input. Combining these in the actual order gives

```text
restored error < 2^(gamma-p) B(D,A)
B(D,A) = 8^-D [a(1-beta^D)/(1-beta) + 4 sqrt(2) 2^A + 22]
         + (16/7)(1-8^-D).
```

The comparison endpoint is the retained Tensor's R F_s, with its existing exact factor/coordinate identity. Each analytic or local-defect premise is retained; this result does not certify the coefficient backend or that identity anew.

**Derivation and domain.** At the computed expansion output z, split the chirp error as computed_chirp(z)-exact_chirp(z), plus the exact chirp applied to the expansion error. Normalized Fourier rows have absolute row sum 1; the Q_freq coordinate map does not increase sup norm. This gives the sum in brackets. Then apply e_next<=e/8+2h exactly D times, and finally multiply every term by 2^gamma. No rounded operator is assumed linear or Lipschitz. The expansion norm invariant supplies the chirp input below .6. The source chirp returns below .601; the compression norm recurrence keeps each later input inside its unit-disk contract. The actual schedule builds all compression halos first, so no missing boundary-cell or copy-multiplicity term is introduced.

This yields a simple all-dimension sufficient error guard:

```text
p >= gamma + max(A-3D,0) + 12  =>  restored error < 1/256.
```

For proof, a/(1-beta)<4, 4sqrt(2)<6 and D>=1 imply

```text
B(D,A) < 8^-D(6*2^A+26)+16/7
       <= [6+26/8+16/7] 2^max(A-3D,0)
       < 12 * 2^max(A-3D,0).
```

Then 12/4096<1/256. The guard applies only alongside all production requirements, including p>=101, the chirp p-A>=13 gate, the source geometry, the common p grid, the local work-precision guards, and valid coefficient/primitive contracts. It replaces only the sufficient final error comparison. It cannot waive a stronger guard required elsewhere.

The source [Tensor proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/physical-gaussian-tensor/PROOF.md) uses the coarser guard p>=gamma+A+ceil(log2(Dp^2+32+2D))+8. The joined bound makes the 3D-bit attenuation of earlier errors explicit. No claimed runtime or kappa gain follows until an actual production parameter choice and its complete cost are re-admitted. The separately assigned CRT entrance/product/return and both S factors are outside this scope.

**Evidence.** The checker authenticates the current main Tensor, chirp and compression sources, checks the five relevant composition sites and both restored components, and independently iterates the rational recurrence for D=1,...,32 and A=0,...,96. All 3,104 cases match the formula and sufficient guard. The rational constants prove the displayed all-D/all-A inequality; finite sampling is not its proof. Normal and optimized CPython 3.12.13 receipts agree. No full physical Tensor execution, production-page validation, CRT recovery, native/compiler or selected replay was run. Predecessor physical fixtures retain their stated scopes and are not counted as new execution.

Run the registered checks with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/tensor-restored-error-join
```

Expected verifier marker: PASS_JOINED_TENSOR_ERROR_GUARD.

Next step: substitute one production geometry into the joined guard while retaining all catalogue and chirp admission gates, then verify the complete physical caller. This result supplies the analytic error-budget handoff; it does not assert that this implementation check has passed.

Credit: Hiroki KUMAZAKI/kumagi supplied PR5295; JoyboyBrian supplied the compression refinement and expansion norm audit; Jose Manuel/jmbarrancoml supplied the physical Tensor, expansion, chirp and compression programs. Dugongue and the retained Gaussian, word, interval, precision and manuscript authors keep their source credit. New joined bound and checker: Ali Romman with OpenAI Codex assistance, Apache-2.0. Author-checked, not independent human or proof-kernel acceptance.


The expansion theorem is an explicit external premise at commit 351975ee703ec5aa1b18f70f73700d434026199a. Its pinned proof is linked above. The verifier does not execute or prove that external theorem. The local replay authenticates the main-branch composition, chirp and compression sources.
