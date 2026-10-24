# Batched native solves for one shared Gaussian band inverse

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

This is a constructive sufficient native Word RAM algorithm, with no Turing-machine primitive. It improves the inverse adapter when the retained bandwidth grows. It does not establish a larger complete multiplication κ: in modern outer regimes the bandwidth may already be bounded, and the Fourier-kernel exponent is a separate constraint.

## Theorem

Put ω = log₂ 7. Let A be a shared s by s triangular matrix of bandwidth at most h, and let R right-hand sides be supplied. Let H be a power of two with h ≤ H < 2(h+1). Pad s to a multiple of H with independent unit diagonal coordinates. Suppose the absolute row sums of A, of its contiguous H by H diagonal blocks, and of their inverses, as well as ||A⁻¹||∞, are bounded by a known polynomial in n. The input norm means the maximum infinity norm of an INDIVIDUAL right-hand-side column, equivalently the maximum absolute input entry. It is not the induced row-sum norm of the entire R-column matrix; no factor R enters the precision bound. This norm and requested precision have O(log n) bits. Every entry is a supplied bounded-word dyadic number; no matrix or inverse oracle is supplied.

There is an explicit native algorithm with preparation O(s H²), application

    O(s (R+H) H^(ω−2)),

and O(s R+s H) stored words, at any requested absolute accuracy 2⁻ᴾ. A sufficiently large fixed constant times log n bits per physical word suffices. For R ≥ H, application is O(s R H^(ω−2)), strictly improving the scalar O(s R H) count when H grows.

## Constructive organization

Number diagonal blocks in substitution order. Because the bandwidth is at most H, only the immediately preceding block can couple to a block. Write its equation

    Dᵢ Xᵢ + Eᵢ Xᵢ₋₁ = Bᵢ.

Prepare Gᵢ ≈ Dᵢ⁻¹ by ordinary triangular substitution on H unit columns. This costs O(H³) per block, or O(s H²) in all. This is an actual bounded-word computation, not an assumed inverse. Partition the right-hand sides into batches of H and pad the final batch with zero columns. In substitution order compute

    Xᵢ = Gᵢ (Bᵢ − Eᵢ Xᵢ₋₁).

Both products are H by H products. Use Strassen's seven-product recursion, with exact-grid additions/subtractions and signed fixed-point scalar multiplication only at its leaves. Each product costs O(H^ω) word operations. Thus each batch costs O((s/H) H^ω), proving the count. An upper triangular solve uses the reversed row and column ordering. Gathering and scattering cost O(s R).

No growing-input integer multiplication is hidden: each leaf multiplies two explicitly bounded machine-word magnitudes. Signed values are sign plus magnitude; natural truncated SUB can implement a signed subtraction by comparing magnitudes first.

## Explicit stability and finite words

Let u be the fixed-point grid spacing. Set B ≥ 2 to bound H, the row norms of A and its blocks and coupling blocks, the inverse row norms of A and its diagonal blocks, and every right-hand-side norm. All these bounds are polynomial by hypothesis.

A Strassen multiplication of exact supplied grid matrices has entrywise rounding error at most H²u. To see this, input-side sums are exact. Only scalar leaf products round, each by at most u. Each output quadrant combines at most four child outputs, so the error recurrence is e(H) ≤ 4 e(H/2), with e(1) ≤ u. This proves e(H) ≤ H²u. Input-side magnitudes grow by at most H; product and output recombination magnitudes are at most H⁴ times the square of the maximum input magnitude. They are polynomially bounded. This argument covers negative values and cancellation.

In preparation, rounded triangular substitution for each inverse column has residual at most (H+M)u in each row, where M bounds the diagonal-block row norm. Each row contains at most H rounded products, and final division contributes at most M u to its equation. Hence the prepared inverse has row-norm error

    εG ≤ H ||D⁻¹||∞ (H+M)u ≤ 2 B³u.

For u ≤ 1/(12 B⁶), this is below 1, so its row norm is at most B+1. The same residual argument bounds every prepared inverse entry and all its substitution prefixes by a polynomial in B; no repeated-error exponential is assumed.

For the application, denote the full computed solution norm by x. A block's first matrix-product error is at most B²u. The approximate-inverse error and second product give, after multiplying its equation by Dᵢ, a block residual bounded by

    6 B⁵u (1+x).

For completeness, use εG ≤ 2 B³u and B²u ≤ 1 in

    M [ εG (X + Mx + B²u) + (K+1) B²u + B²u ],

where M,K,X ≤ B. This is at most the displayed bound. The residual is a rowwise equation error, so combining all blocks takes its maximum; it is not multiplied by the number of blocks. If r is the full residual norm, the actual inverse bound gives x ≤ B²+B r. Therefore

    r ≤ 6 B⁵u (1+B²+B r) ≤ 24 B⁷u,
    ||Xcomputed − A⁻¹Binput||∞ ≤ 24 B⁸u.

The assumption 6 B⁶u ≤ 1/2 closes the rearrangement. Taking

    u ≤ min(1/(12 B⁶), 2⁻ᴾ/(24 B⁸))

suffices. Only P+O(log B) fractional bits are needed. The computed solution norm is at most 3 B². The explicit Strassen and preparation magnitude bounds require only O(log B) additional integral bits and a fixed number of product limbs. Thus all arithmetic fits one sufficiently large common O(log n)-bit word budget, including raw products and division numerators. No floating-point instruction is assumed.

## Actual Gaussian inverse caller

PR #4554 supplies an explicitly formed near-identity periodic Gaussian matrix, its ordinary-band factors and its rank-at-most-2h Woodbury correction. Its proof gives polynomial inverse bounds for both triangular factors: ||L⁻¹||∞ ≤ 8 and ||U⁻¹||∞ ≤ 36(h+1), with uniformly bounded pivots and polynomial factor norms. Contiguous diagonal-block inverses are the corresponding principal blocks of the triangular inverse, so the theorem's hypotheses follow. Factor errors are separately charged by that predecessor's residual estimate.

For one axis, batch its R parallel fibers rather than solving them individually. Apply the theorem to both ordinary-band triangular factors. The small Woodbury Schur inverse is prepared by the predecessor's explicit elimination and unit-column solves. Its action on batches is another bounded matrix product. The recovery Xz has dimensions s by 2h times 2h by R; split its rows, columns and inner dimension into H-sized blocks. It has the same O(s (R+H) H^(ω−2)) count. All small Schur products are covered because s ≥ H. Every new approximation gets a polynomially smaller local grid budget, preserving O(log n) word precision.

Preparation remains O(s H²), including the ordinary factors, inverse diagonal blocks and the Woodbury data. For the intended tensor axes, s = n^o(1), the number of fibers is at least H eventually, and this preparation is n^o(1). Across d axes with T total entries, h = O(1+sqrt(p)/α), α² = Θ(d sqrt(p)), and d = Θ(p^ε), the inverse work becomes

    O(T d (1+h)^(ω−2) + n^o(1)).

For 0 < ε < 1/2, this is

    O(T p^[ε+(ω−2)(1/4−ε/2)] + n^o(1)),

instead of the previous O(T p^[1/4+ε/2]). The forward chirp cost is unchanged: O(T p^ε log p). Shared exp/root setup is still paid by #4554. For ε ≥ 1/2, h = O(1), so the new batching has no exponent gain; this is why the theorem does not imply a modern best κ by itself.

## Executable evidence

    python3.12 -I -O -B batched_band.py

The portable standard-library replay implements bounded signed dyadic arithmetic, all seven Strassen products, explicit inverse-block preparation and batched band substitution. It checks 36 systems and 1,785 individual residual entries against an independent Fraction oracle, including a non-full last batch. All residuals are below 2⁻⁷⁰; 172,305 arithmetic operations were charged, and the largest raw magnitude used 205 bits under a 384-bit cap. A deliberately undersized word fails. The fixture uses real unit-diagonal lower bands; general complex data follow by four real matrix products, and upper solves follow by reversal. These extensions are covered by the proof rather than those fixtures. It is not an emitted RamStd program or a complete asymptotic multiplier replay.

## Credit, overlap and open next questions

Strassen's seven-product identity is classical (V. Strassen, Numerische Mathematik 13 (1969), 354–356, DOI 10.1007/BF02165411). Shared band factors, Gaussian tails, explicit conditioning and Woodbury preparation here are predecessor results from Dugongue's PR #4554, with its Harvey–van der Hoeven/OpenAI Gaussian-resampling lineage. Problem 1.8's bounded-word/frame discipline motivates explicit word checks; no fresh Lean verification is claimed. The new contribution is this sufficient batched inverse organization, its residual proof and executable native fixture. We do not claim that batching triangular solves or fast matrix multiplication is historically new.

The useful next check is whether any admissible complete native outer parameter regime has growing h and is actually limited by this inverse cost. Freeze that caller and compare its full profile before claiming a new κ. A separate task is to replace Strassen by a faster constructive bounded-word matrix algorithm with an equally explicit stability bound; its exponent would enter the same formula.

## Frozen source bindings and search coverage

The inspected predecessor NATIVE-BANDED-INVERSE.md has SHA-256 1259b4242ebf6ac7f14bfe72e371afb8dc530b2755d1fd82228d9dc6f01634ba; NATIVE-RECOUNT.md has SHA-256 fc14d31113ef3abd597e654e0aec35ef7972d014268e4b8b7624f202f9ff79db. Both are from the PR #4554 local source package. The primary [Strassen paper](https://link.springer.com/article/10.1007/BF02165411) identifies the classical seven-product exponent; its identity is implemented explicitly here.

A scoped search of current-main research/ and notes/ found existing Strassen integer-power certificates in the helper/compiler family. Those precedents retain their credit; this package does not claim first use of Strassen in the repository. The new scoped application is the shared Gaussian inverse and its finite-word residual bound. A federated DAG query for Kronecker returned representation-theory results, not an applicable arithmetic convolution theorem. This is limited search evidence, not an exhaustive novelty assertion. Current-main AGENTS.md, autoresearch.md and CONTRIBUTING.md were read before construction; the task was explicitly assigned, so it was not rerolled.
