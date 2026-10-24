# New-main checkpoint: RAM overlap and predecessor credit

Read-only checkpoint at canonical main `624de9dc66858af0945e5f8a0942488d62280d43`. The frozen RAM lane was not edited. The relevant archived work confirms substantial prior native migration, stability, modular execution and signed-recovery coverage; none of these general concepts should be described as first applied by this literature package.

## Sources actually inspected

- [`research/pr4554-native-stability-check/README.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/624de9dc66858af0945e5f8a0942488d62280d43/research/pr4554-native-stability-check/README.md), plus its vendored `PR4554-NATIVE-STABILITY.md` in full.
- [`research/word-ram-transfer/README.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/624de9dc66858af0945e5f8a0942488d62280d43/research/word-ram-transfer/README.md).
- [`research/modular-port-borrowing/README.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/624de9dc66858af0945e5f8a0942488d62280d43/research/modular-port-borrowing/README.md).
- [`research/modular-gaussian-recovery/README.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/624de9dc66858af0945e5f8a0942488d62280d43/research/modular-gaussian-recovery/README.md).
- [`research/packed-carry-symbolic/README.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/624de9dc66858af0945e5f8a0942488d62280d43/research/packed-carry-symbolic/README.md).

## Meaningful shared and distinct scope

**Native rational stability was already developed and independently checked.** The #4554 text derives fixed-template prefix/suffix bounds K^(D+1), scalar-rounding envelopes and explicit integral/fractional widths; its #956 instance has a logarithmic recursion depth and retains a funded kernel exponent. Ryanson Jonathan's archived independent check credits Dugongue, the #956/#390/Sussman/P193 lineage and ram_cost's shear estimate. It expressly excludes the unresolved full Newton/Toeplitz preparation. Our guard-bit examples and fixed-word qualifications are an application/review of this established line, not a new general stability theorem or a complete caller. Its polyloglog absorption statement also means a precision overhead exceeding a fixed number of limbs is not automatically fatal: an explicitly bounded polyloglog cost can preserve every strict exponent below the algebraic saving.

**The general Word RAM migration already exists.** `word-ram-transfer` contains a Problem 1.8 logarithmic-word bridge, a finite TM emitter, packed tape accesses and affine/quarter-phase native kernels. It already separates local primitive correctness from complete multiplication invoices and explicitly notes Fürer's 2014 O(n) log-RAM baseline. Credit Dugongue/OpenAI Codex, the Problem 1.8 authors, Szymon Torunczyk/GPT and the detailed inherited lineage. Our contribution is not first migration, first monomial lowering, or first use of those Lean sources. The sharper packed-time comparison #4541 remains the appropriate baseline for a claimed computational gain.

**Modular dirty-port execution is also prior work.** Gareth Davidson (@bitplane)'s `modular-port-borrowing` gives an actual backend for integer-factor borrowed echoes modulo 2^w, restores arbitrary dirty ports and pays reductions, product registers and final signed recovery. It credits PR1057, PR822, PR673, PR730, PR628 and the Ben-Or–Cleve principle, and discusses Ali Romman's PR1135 rational lift. It excludes general dyadic factors because division by 2 is not defined on that quotient. Our exact cp22f base change uses odd characteristic with 2 invertible, the literal Gaussian phase letters, and two/three-call triangular maps. That is a different algebraic interface; it does not improve the existing modular backend's call count or demonstrate a complete multiplier.

**Residue-assisted Gaussian recovery and carry-free packing are already concretely implemented.** Dugongue's `modular-gaussian-recovery` extends Mason Hale's backend with a paid low-residue product to reduce numerical precision while keeping certified exact output. The archived package charges the additional child, packing and lifting and claims no κ. Our two-modulus signed CRT test is a small exact mechanism check, not first modular reconstruction in the project or a stronger end-to-end recovery theorem. The best research use would compare a complete new caller against this existing paid alternative, rather than rediscover its premise.

**Packed carry correctness has stronger prior symbolic evidence than our tiny lane test.** Philipp (@mightyOil)'s `packed-carry-symbolic` independently certifies Hanson Sun / bbMisk PR1245's matching-prefix table for every even radix, retaining PR773, PR735 and manuscript credit. Our exhaustive two-lane guarded-add test validates a simpler primitive under its own guard assumption. It is useful as a model sanity check, but it does not subsume that symbolic all-radix source-bound certificate.

The distinct positive result retained by our lane is narrowly stated: polynomial/inverse identities of the literal cp22f arbitrary-target port transport through Z[i,1/2] into split finite fields, with absolute phases and separate tensorization; the triangular block remains invertible in characteristic 5 despite singular coupling. Only its optional coupling inverse needs 15 invertible. This is not a star-homomorphism, numerical-conditioning, physical-supplier, complete-caller or new-κ claim. The lookup did not establish novelty even for this narrower application.

## Search limits

A bounded root-name scan found many related packing, CRT, precision and modular archives, including `packed-ram-speedup`, `pr4541-packed-transfer-check`, `pr4541-packed-io-check`, `modular-port-borrowing`, `modular-gaussian-recovery`, `unconditional-batched-crt`, `native-wordram-tightening` and `fft-word-parameter-bounds`. A content grep across all archived READMEs could not finish because the partial clone attempted to fetch a missing promisor blob and Git HTTPS reported `SEC_E_NO_CREDENTIALS`. Targeted primary raw URLs and already-present Git blobs supplied the six reads above. No Git configuration or authentication was changed; this is incomplete source coverage, not evidence of absent TFT/CRT/packing work.

## Exact source-byte pins

- `research/pr4554-native-stability-check/README.md`: SHA-256 `5fee242033d3c0f1af81c4bdf619ec26130b066282f465c6e85ecc0b357964b5`.
- `research/pr4554-native-stability-check/PR4554-NATIVE-STABILITY.md`: SHA-256 `260e78bf8f88667a637b804d013d1e7c6dfdf1e23ae35ffdc64a4366c7321221`.
- `research/word-ram-transfer/README.md`: SHA-256 `4160d820310fb9bcebc359e7108146ea2e1ca9713277feaa4636e820211fabef`.
- `research/modular-port-borrowing/README.md`: SHA-256 `61512ec419a9ae04b1f5321167d14515e4e25db6702704f417cdb32857243fb7`.
- `research/modular-gaussian-recovery/README.md`: SHA-256 `4242f0541146aa3f072762ec79845b36867557e9b10a87c223aed96950c48fe8`.
- `research/packed-carry-symbolic/README.md`: SHA-256 `85f47131b595189a8c6dbb6b266d726c859e3ac0ae0fc0954d22c2dcb307243c`.
