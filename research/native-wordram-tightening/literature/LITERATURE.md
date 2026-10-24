# Primary-source literature and GitHub Lean search

Prepared for Dugongue with substantial OpenAI Codex assistance, 2026-10-22. This is a research search record, not an assertion of a new multiplication exponent or an exhaustive worldwide novelty search.

## Correct comparison

The native target is **O(n / (log n)^κ)** word operations on packed n-bit inputs with words of C log n bits, for a fixed sufficiently large C. It is not the multitape tariff O(n (log n)^(1−κ)). A unit instruction may multiply word-size operands; it may not multiply arbitrary n-bit operands. One can implement a fixed number of words of precision using a fixed number of ordinary word instructions. Every table and constant preparation cost remains charged.

Fürer’s 2014 Theorems 4.1(a) and 4.2 establish O(n) integer multiplication on a log-RAM. This is an important baseline, not a new improvement over an existing native O(n / (log n)^κ) result. The source-native transfer in PR #4635 already avoids a Turing-machine simulation and explicitly pays the O(p)-bit scalar arithmetic with p = Θ(log n).

## Primary sources inspected and actionable use

1. Martin Fürer, *How Fast Can We Multiply Large Integers on an Actual Computer?* (2014), https://arxiv.org/abs/1402.1811 . Sections 2 and 4 specify logarithmic registers with unit multiplication and division. Theorem 4.1(a) gives the complex Schönhage–Strassen log-RAM baseline. This rules out claiming ordinary FFT word packing as a new κ mechanism.

2. Timothy M. Chan, Ce Jin, Virginia Vassilevska Williams and Yinzhan Xu, *Faster Algorithms for Text-to-Pattern Hamming Distances*, FOCS 2023; corrected arXiv v3 dated 2024-12-19, https://arxiv.org/abs/2310.13174 . Lemma 2.2 and Appendix B supply deterministic length-L convolution over F_q in O(L log q) word operations. Their implementation uses two recursive smooth-root levels, packed finite-field arithmetic, and sublogarithmic transforms evaluated from prepared tables. The proof explicitly repairs an older incomplete extension-field shortcut. Apply this to genuinely low-modulus convolution leaves, after accounting for extension-field preparation and coefficient reconstruction. It cannot be substituted for a p-bit Gaussian evaluation merely because both computations contain convolutions.

3. Josh Alman and Baitian Li, *Kronecker Powers, Orthogonal Vectors, and the Asymptotic Spectrum*, FOCS 2025, https://arxiv.org/abs/2509.14489 . Corollary 1.1 gives depth-4 size O(N^1.249424) for matrices f(x ∨ y), and depth-2d size O(N^(1+0.498848/d)) for even d. It applies, after explicit diagonal factors, to Kronecker products of 2 × 2 matrices. The paper confines unrestricted coefficients to one layer in this general reduction. This is a concrete alternative to using the older depth-4 N^1.25 bound in a caller that truly needs a shallow circuit. The resulting shallow bound alone does not beat an O(N log N) unrestricted-depth evaluator.

4. Josh Alman and Kevin Rao, *Faster Walsh-Hadamard and Discrete Fourier Transforms From Matrix Non-Rigidity*, STOC 2023, https://arxiv.org/abs/2211.06459 . The reported improvements are leading constants: 23/24 for Walsh–Hadamard and 15/4 for real DFT arithmetic. Their low-rank-plus-sparse decomposition is relevant to finite-template synthesis. The constants are not a power saving in log n and must not be reported as a larger κ.

5. David Harvey and Joris van der Hoeven, *Integer multiplication in time O(n log n)*, Annals of Mathematics 193 (2021), 563–617, https://annals.math.princeton.edu/2021/193-2/p04 . Gaussian resampling, multidimensional power-of-two transforms and the original analytic precision/recovery foundations are predecessor work. Their native bit-complexity theorem is a multitape theorem; any word-RAM improvement needs an independently charged implementation.

6. David Harvey, Joris van der Hoeven and Grégoire Lecerf, *Even faster integer multiplication* (2014/2016), https://arxiv.org/abs/1407.3360 . Recursive short multiplication and coefficient-ring choices distinguish a valid short leaf from a circular multiplication oracle. Calling an existing algorithm on a genuinely smaller integer does not make its charged cost zero.

7. David Harvey and Daniel S. Roche, *An in-place truncated Fourier transform and applications to polynomial multiplication* (2010), https://arxiv.org/abs/1001.5272 . Truncation and in-place storage reduce padding/workspace in an actual transform implementation. They do not by themselves improve the dominant simultaneous Gaussian exponent.

8. Leslie Greengard and John Strain, *The Fast Gauss Transform*, SIAM J. Sci. Stat. Comput. 12 (1991), 79–94, https://doi.org/10.1137/0912004 ; author PDF https://math.nyu.edu/~greengar/fgt_1991.pdf . Hermite/Taylor separation gives linear work with a precision-dependent constant in fixed dimension. Integer recovery needs errors exponentially small in p. The dependence on precision, dimension and signed input norm must be retained; quoting fixed-tolerance linear time is insufficient.

9. Nir Ailon, *An n log n Lower Bound for Fourier Transform Computation in the Well Conditioned Model* (2014), https://arxiv.org/abs/1403.1307 ; *Paraunitary Matrices, Entropy, Algebraic Condition Number and Fourier Computation* (2016), https://arxiv.org/abs/1609.03278 . These lower bounds concern restricted conditioning models, not all native algorithms. They identify why a numerical lowering requires intermediate amplification data, rather than only an exact endpoint identity.

10. Rezaul Chowdhury, Francesco Silvestri and Flavio Vella, *A Computational Model for Tensor Core Units* (2019), https://arxiv.org/abs/1908.06649 . The model grants matrix-unit operations beyond an ordinary scalar Word RAM. GPU or tensor-core timings can guide a search but are not a scalar RAM complexity proof.

## Concrete mechanisms nominated

**A. Two-level tabulated low-modulus convolution.** Use the corrected finite-field algorithm in item 2 for low-modulus exact polynomial leaves. The complete replacement cost includes reduction, field construction, tables, reconstruction and output. No reviewed native caller binding was produced here; in the PR #4635 ledger the global-precision record-product row is already subdominant, so replacing that row alone does not improve κ.

**B. OR-normalized Kronecker circuits with one unrestricted layer.** The constructive normalization lemma in `KRONECKER-NORMALIZATION.md` proves that every all-nonzero 2 × 2 tensor factor reduces to the f(x ∨ y) family with two paid diagonal passes and two coordinate flips. This gives a direct applicability test for the newer Alman–Li shallow circuit theorem. An improvement needs an actual caller whose charged shallow exponent changes; it does not follow from comparing isolated circuit sizes.

**C. Hermite/Taylor Gaussian separation.** This is relevant only when the exact physical kernel is an ordinary Euclidean Gaussian sum satisfying the source’s separated-box hypotheses. A Boolean/symplectic Gaussian operator is not automatically such a sum. No precision-uniform bound improving the native simultaneous transform was proved here.

## GitHub Lean inspection

`LEAN-SOURCE-PINS.json` records exact commit, file URL, SHA-256, byte length and observed declaration headers for eight files from four repositories. No Lean process, kernel replay or axiom audit was run in this session. The inspection supplies reusable interfaces, not accepted proof evidence for a new complete theorem.

- `openai/math` at `1581d4cbdd69a0faf34b2089614fe2a814316a6a`: `lean/ComparatorChallenges/UniformFourier.lean` states exact scalar/index RAM goals. Its complex scalar type is ℂ; only integer peaks are polynomially bounded. The comparator endpoints use `sorry` as challenge statements. This is not the implementation proof file and its placeholders must not be described as a discovered defect in the implementation. The repository’s scope note explicitly excludes a bit-precision claim. The recursive Git tree API response was truncated; no full-tree completeness claim is made.
- `Verified-zkEVM/CompPoly` at `1cb8f5cd0e22a8c9ec165000915c21d0f8e12525`: actual source includes `additiveNTT_correctness`, `computableAdditiveNTTFast_eq_additiveNTT`, `NTTFast.safeFastMul_eq_mul`, and `NTTFast.withFallback_eq_mul`. These can ground exact finite-field leaf semantics and domain-fit conditions. They do not supply the required scalar word-operation complexity theorem merely by being executable Lean.
- `BlueFatWhale/flpoint` at `d5c0fa90c69c36f794f176c96f2dd4d293bb5aa3`: `matVec_backward_error` and `matVec_error_bound` use an abstract `FPModel`. They support compositional error proofs but do not establish a concrete word format’s rounding or overflow contract.
- `alerad/leancert` at `f704278b3ed525ab5dc80b2ce9545c9b8047ec30`: concrete dyadic source has directed-rounding and normalization inequalities, including `toRat_shiftDown_le`, `toRat_shiftUp_ge`, `toRat_normalizeDown_le`, and `toRat_normalizeUp_ge`. These are useful precedents for checked coefficient enclosures. No asymptotic runtime transfer is inferred from them.

## Overlap and coverage limits

The current source-bound native transfer and recent PR bodies were read through the coordinating worker’s frozen `frontier/` artifacts, including PR #4635 `NATIVE-LIFT.md`. Historical main packages `word-precision53`, `chirp-packed-correlation-audit`, and `central-factor-packed` were read to distinguish directed dependencies, correlation guard bits, and exact packed verification from new mechanisms. Main’s selected result is #4470 with inherited precision/analytic obligations. Existing tensor/lookup mechanisms already receive explicit credit in #4635; no claim is made that the literature concepts above have never appeared in any of the thousands of historical PRs.

Searches covered integer multiplication/log-RAM, packed complex arithmetic and precision, modular convolution and extension fields, shallow Kronecker circuits and matrix non-rigidity, Gaussian resampling/Hermite separation, tensor-core model changes, and public Lean FFT/NTT/rounding code. Exact query strings are in `SEARCH-QUERIES.json`. Search-engine indexing and the truncated openai/math tree limit coverage. Only primary papers and repository-owned sources support mathematical assertions; incidental third-party search results were not used as theorem evidence.

## Conclusion of this leaf

No independently verified superior native κ was produced by the literature leaf. The positive reusable result is the all-input diagonal/flip normalization with full operation and error accounting; the two leading mechanisms have explicit applicability tests. The coordinating worker must bind any claimed κ improvement to an actual changed paid supplier or charged native caller, rather than relabel known O(n) RAM multiplication or a local constant saving.
