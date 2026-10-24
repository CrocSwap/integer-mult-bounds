# Two real inputs in one complete Tensor: exact PR5095 fit

Prepared 2026-10-23 with substantial OpenAI Codex assistance. This is a source-bound proposal and error derivation, not an executed implementation, physical cost certificate, recursive closure theorem or selected-exponent improvement. Root coordinates any subsequent independent check. No code under the source repository was changed.

## Published identity and its evidence class

Robert Matusiak, *Implementing Fast Fourier Transform Algorithms of Real-Valued Sequences With the TMS320 DSP Platform*, Texas Instruments application report SPRA291, August 2001, Section 3.1 pp.5–6 and Appendix A.1 pp.18–19, gives the exact two-real-input packing and recovery formulas. Equation (22) is on printed p.18; that page was rendered and visually inspected. This is a primary published engineering report, **not a peer-reviewed mathematics paper**. Official source: <https://www.ti.com/lit/an/spra291/spra291.pdf>. Local PDF SHA256: `aae9288bbf9e4c933f542ec4589b9de22cd591024c3947471893d0ec3995cfd8`.

Steven G. Johnson and Matteo Frigo, *Implementing FFTs in Practice*, chapter 11 in C. S. Burrus (ed.), *Fast Fourier Transforms*, Rice University/Connexions, 2008, Eq.(7), printed p.17, records the underlying complex linearity for two real arrays. Its SIMD application is a different implementation direction, so no native cost result is imported. Author-hosted source: <https://math.mit.edu/~stevenj/papers/JohnsonFr08-burrus.pdf>, SHA256 `454dc303d65ee0279042e815d390abaa2ef59147cba115ee1fdfa5561a18ad9a`.

IBM's author record verifies the related Cooley–Lewis–Welch 1970 *Journal of Sound and Vibration* paper, DOI `10.1016/0022-460X(70)90075-1`. Its primary full text was not obtained; no equation or first-discovery attribution is inferred from its metadata. This proposal is standard FFT prior art with a possible new local contract binding.

## Authenticated actual source

JoyboyBrian's PR5095 head is `e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1`. The separate source worker froze `outputs/outer-bilinear-interface-20261023/APPENDIX-5095.md`, SHA256 `87243c00536e42cbc8663b645b80c83a4cf3a8558a9442d37855c6de38b75a69`, and `APPENDIX-5095-SOURCES.json`, SHA256 `a41239e2bca82f6f8fb63f79eebc11f40bd7cb3671cee30ce94d7ef217315d76`. All nine listed snapshots were hash-checked here. This worker read the appendix, literal ingress/product/recovery code, the complete Tensor proof and the source07 transform/permutation definitions. No nested dependency archive was executed.

The existing entry sends two independent borrowed radix digit streams through ingress and CRT, then **two separate complete forward Tensor calls**, scalar pointwise multiplication, one complete opposite Tensor call, exact rescaling, inverse CRT and carries. The actual nonlinear cut is scalar multiplication on `C^S`, distinct from the inner polynomial-record product `uv/r` in `(C[y]/(y^r+1))^M`.

Relevant source locators:

- `research/physical-tensor-crt-sandwich-recovery/sandwich.py:53–88,175–188`: quarter-disk ingress, literal product, recovery and call order.
- Its `PROOF.md:86–122`: conditional production approximation and strict recovery guard.
- `research/physical-gaussian-tensor/PROOF.md:25–52,151–160`: complete returned orientation, restoration gamma and error.
- `upstream/build/sections/07-resampling.tex:13–16,60–62,311–322,461–485` in the prior frozen source map: normalized transforms, frequency dilation and convolution normalization.

For source shape `(s_1,...,s_D)` let `S=product s_i`. The complete ideal forward map is

    T = R F^-_s,          (R z)_j = z_(t_1 j_1,...,t_D j_D),
    (F^-_s u)_k = (1/S) sum_j u_j exp(-2 pi i sum_i j_i k_i/s_i).

The complete opposite map is `Tplus=R F^+_s`. The source has `gcd(t_i,s_i)=1`. Both maps are contractions in coordinate sup norm. The restored Tensor exponent is `gamma=D(2 alpha^2+ceil(log2(32p))+1)` with the actual source parameters; it is not an extra factor in these already completed ideal endpoints.

## Exact proposed replacement

After the same CRT conversion, let `u,v` denote the two real arrays. Each component is a nonnegative digit divided by `2^(b+2)`, so `0<=u_j,v_j<1/4`. Their packed array

    h = u + i v

has modulus strictly below `sqrt(2)/4<1/2`, inside the existing arbitrary-half-disk Tensor ABI. Ingress is exact on the p-grid because the source requires `p>=b+2`.

Let `J` negate each source coordinate modulo its own `s_i`, and write `H# = conjugate(J H)`. Frequency dilation R commutes with J, so the usual real-input identity survives the actual retained permutation. With `H=T h`, define

    A = (H+H#)/2 = T u,
    B = (H-H#)/(2i) = T v,
    Z = A*B = (H^2-(H#)^2)/(4i).

Here products and squares are scalar coordinatewise operations. The same completed opposite call gives

    Tplus(Z) = (u*v)/S^2.

The existing recovery multiplier `S^2 * 2^(2b+4)` is therefore unchanged. The CRT digit embedding and inverse CRT are unchanged mathematical maps. This is an exact replacement of the two initial complete forward calls by one complete forward call and an explicit splitting/product operation. It is not a proposal to run the real and imaginary parts independently through a rounded Tensor: the actual packed complex call must be used, and rounded Tensor linearity is never assumed.

## A sufficient error lemma using the existing strict guard

This paragraph is a new elementary source-bound deduction, not a theorem attributed to the FFT report. Retain all source production-page and complete-Tensor approximation premises. Put

    hgrid = 2^-p,
    E = D*p^2 + 6*M + 22 + 2*D,
    epsilon = E * 2^gamma * hgrid,
    C = S^2 * 2^(2b+4).

The existing guard `(G)` is exactly `C(3 epsilon+2 hgrid)<1/2`. Source `b>=1` and `S>=1` imply `C>=64`, hence `epsilon<1/384`.

Suppose the one packed complete call returns `Htilde` with `||Htilde-H||<epsilon`. Apply the two split formulas **exactly** in sufficiently wide dyadic words. Since conjugation and J are sup-norm isometries, both split maps have operator norm at most one over the real vector space. Thus the resulting `Atilde,Btilde` each differ by less than epsilon from `A,B`; the latter are in the quarter-disk. It follows that

    ||Atilde*Btilde-A*B||
      <= epsilon*(1/4+epsilon) + epsilon/4
       = epsilon/2+epsilon^2 < 2 epsilon.

Compute this product exactly, then truncate each component once to the p-grid, as the source product does. This adds less than `sqrt(2) hgrid < 2 hgrid`. The product before truncation has norm below `(1/4+epsilon)^2<.26^2<1/2`; inward component truncation cannot increase it. Therefore the actual computed product satisfies the opposite Tensor input ABI.

The opposite map is a contraction and its actual call contributes less than epsilon, so the returned result differs from the ideal by less than `3 epsilon+2 hgrid`. Existing rescaling and strict nearest-integer recovery consequently remain valid under the **same** guard `(G)`. No p reduction is claimed. This lemma depends on exact splitting followed by a single final product truncation; silently rounding both split arrays first would require a different bound. Shared forward-call errors may be correlated, but the inequality does not assume independence.

## Physical bill and recursive boundary

The algebra changes the complete Tensor count from three to two. It does not yet establish a lower total fixed-tape cost. The remaining concrete bills are:

1. Formation of a new owned complex packed bank from the two independently borrowed digit streams, including copying, resetting and restoring cursors under the actual Tape scope rules. The two inputs are not new rewards or free scratch.
2. Access to `H_j` and `H_(-j)` in one physical operation. R commutes with J algebraically; this does not pay for a frequency-negation routing pass. Source lengths are odd, so J has only the zero tuple as a fixed point, but exploiting pairs still needs a legal fixed-tape schedule.
3. Exact half-sums/half-differences in extended dyadic words, widened integer products and one final truncation. The squared formula is an alternative algebraic expression, not an asserted cheaper multiplier circuit. Temporary banks, cleanup and all ordinary word work must be counted.
4. A source-produced production catalogue satisfying the existing guard. The existing reduced staged fixture and recovery-only supplied-approximation fixture do not supply production-sized multiplication.
5. An independent source check of the changed call chronology, recovered product, owner lifecycle and complete finite operation count before a physical saving is stated.

The present identity exploits real initial digits at this parent cut. It does **not** prove that the actual Tensor/Core/RawGaussian/Gaussian/Full recursion preserves a real or Hermitian subclass. Chirps, signed normalizers, mixed frames and independently borrowed helper streams require their own closure analysis. A reduction that merely halves both child cost and credited independent work may leave the rank-moment exponent unchanged. Root assigned a separate bounded source-only closure inventory; no recursive experiment or native emitter has been run here.

## Small independent binding test, if authorized by root

The next useful check is one existing source geometry with both independently varied real digit streams, one packed forward return, exact source-coordinate J, one fused split/product, and the unchanged opposite/recovery contract. Check the exact identity separately from the existing rounded staged reference, include an imaginary perturbation control that violates the real-input premise, authenticate all source bytes, and report additional routing/word/storage costs. This worker has not executed that test. A source audit should first confirm the changed parent ownership schedule is legal and that the source author's overlap is resolved.

Credit the standard real-FFT literature, JoyboyBrian's PR5095 wrapper, Jose Manuel / jmbarrancoml's PR3935 complete Tensor, Tekalign / tekuuu's PR4024 CRT, Mason Hale's PR2313 recovery predecessor, Harvey–van der Hoeven and all retained source/native/Gaussian/router/word-arithmetic contributors. No new selected kappa, physical supplier admission or native coded-owner embedding follows from this note.
