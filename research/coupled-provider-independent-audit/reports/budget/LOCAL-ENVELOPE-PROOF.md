# One-provider local envelopes in two norm geometries

This is a local bound for the complete #5402 provider schedule at exact head `3348fccea855082786d5f0fc5558b73d4974e745`. It covers arbitrary positive fiber width under the retained square normalized native/Clifford realization. It is not a full caller rounding, recursion, coordinate, storage, movement, tape or outer-funding theorem.

Let each of the 641 fields be a vector in the same physical Hilbert space H_f, with its field Euclidean norm. Define

```
||v||max = max_j ||v_j||2
||v||joint = (sum_j ||v_j||2^2)^(1/2).
```

The first is the maximum-field geometry explicitly declared by the provider's proof. The second measures joint field Euclidean error. Their elementary COPY bounds differ; a different exponent in the second geometry is not a discrepancy in the author's first-geometry claim.

## Square unitary native contract

The pinned `clifford_exact.py` defines a normalized square Gaussian gate on a binary translation X_q by

```
C_q = ((1+i)/2) I + ((1-i)/2) X_q.
```

Here X_q is a self-adjoint unitary involution. The two coefficient squared magnitudes sum to one, and their cross terms cancel, so C_q is unitary; its inverse conjugates the coefficients and is also unitary. Address permutations, X shifts and D/phase gates are unitary. The canonical frame constructor consists of these gates and unitary conjugations. Complex conjugation of a frame preserves unitarity. A relative chart/frame transition and each normalized signed Gaussian child therefore act on a square field space by a unitary map. This does not follow merely from formal free-group invertibility.

The emitted source's 72 warp address matrices are independently checked for full binary rank nine, and every canonical frame row list is checked to be an independent subspace basis. Every literal P in the 464 boundary monomial words is checked to be invertible. Their D and phase factors have unit modulus. Tensoring/lifting these primitive address operations columnwise preserves unitarity at every positive width; exterior scalar owner coefficients remain scalar coefficients and are not tensor powered. Thus the unitary bound does not grow with the width.

The native source phase/adapter records preserve the predecessor's physical bindings; they are not newly reconstructed in this norm checker. The separate independent source/physical audit binds that inherited realization. The envelope's premise is that those records are realized by the stated square canonical Clifford maps, with no hidden nonunitary scalar rescaling. It does not newly discharge the native implementation foundation. This norm audit never executes submitted Python.

## Elementary bounds

For either geometry, ADD `v_d += q v_s` with distinct fields has norm at most `1+|q|`. In joint geometry, write the map as `I+q E_ds`, where the block matrix E_ds has operator norm one. In maximum-field geometry, use the triangle inequality for the changed destination. SCALE has bound `max(1,|q|)` on the whole bank. CLEAR and whole-field SWAP have norm at most one. A single-field unitary map, including each Gaussian/monomial/chart operation above, has norm one.

COPY overwrites one destination with its source. Its maximum-field norm is at most one. In joint geometry its norm is at most sqrt(2), since the old destination is discarded and the source contributes to two output fields. The integer power-of-two enclosure uses 2. The COPY bound applies to arbitrary perturbations; it does not rely on silently restricting the destination's error to zero. Exact zero-retag is physical identity and has norm one; correctness of its exact-zero prerequisite belongs to the separate source replay.

For each elementary operation assign exponent zero for a nonexpanding map; assign

```
ceil(log2(1+|q|))          for ADD,
ceil(log2(max(1,|q|)))    for SCALE,
0 / 1                    for COPY in max / joint geometry.
```

All ceiling decisions are exact rational comparisons against powers of two. The checker parses the actual changed WORD, both emitted basis programs, all eight input scalings, all eight emitted output scalings, all final consumption clears/swaps and the literal monomial boundaries. It counts the normalized output `cache_scalar` directly: that field already stores `1/(2 f_i)`.

If L is the sum of these nonnegative exponents, every contiguous subinterval, prefix and suffix has operator norm at most 2^L. Indeed its exponent sum is no larger than the complete sum. This is a deliberately coarse upper bound; it does not assert an optimal norm or exponent.

For residuals inserted after any local operation, the standard telescoping error expansion and the suffix bound give, in the selected same geometry,

```
||e_out|| <= 2^L (||e_in|| + sum_j ||residual_j||).
```

With m residuals each bounded by epsilon and zero initial error, this is at most `m*2^L*epsilon`. The residual bounds are whole-field norm bounds at a fixed width. There is no implicit dimension-independent conversion from coordinate error to whole-field error, and no machine precision or tape budget is inferred.

## Execution and separate scalar-invoice correction

`independent_local_envelope.py` independently reconstructs both exponents and compares the first with the author's declared maximum-field bound only after completing the literal calculation. It also checks exact rational ceiling, COPY-geometry and direct-output-SCALE controls. Its output is `LOCAL-ENVELOPE-v1.json`; root performs the guarded execution. The guarded run passed. The exact stage exponents (max / joint geometry) are: mode inputs 8/8, input basis 844/844, changed native word 17,282/17,298, output basis 854/854, and cache output normalizers 8/8; fused main wrappers contribute zero. Their sums are **18,996 / 19,012**. Thus the author's declared maximum-field bound is independently reproduced. Root's external guard recorded 0.504455 seconds and 59,138,048 sampled descendant bytes. The checker recorded 0.413036 seconds internally and 57,752 KiB maximum RSS. Checker SHA256 is `11d8b361adacac9ae44985ffa8a83ff0e9de47e94571e486427baa7201da7715`; receipt SHA256 is `f99bc2dd5f60b38d6ee9617fac9fb1f03ce9c5f10455650ccf2f7acc54bb490f`.

The original budget checker misread the emitted `cache_scalar` as the unnormalized cache coefficient and applied its reciprocal formula a second time. All eight actual output magnitudes are two. The field operation counts and all recursive profiles/moments were unaffected. The old scalar tariff of 175,038 remains a conservative overestimate but is not the exact literal scalar tariff. The fresh `screen_v3.py` uses the emitted coefficient directly and checks boundary scalar tariff 42 rather than 58, giving exact total 175,022 rather than 175,038. Its authoritative output is `RESULT-v3.json`; earlier checker/result files are retained as version-scoped history. This correction concerns this independent checker, not the provider.

Credit remains with the native, provider, Clifford, controller, compiler and other contributors retained in the pinned source. Independent derivation: Chris R/Clear1nsight with substantial OpenAI Codex assistance. No human or formal-kernel acceptance is claimed.
