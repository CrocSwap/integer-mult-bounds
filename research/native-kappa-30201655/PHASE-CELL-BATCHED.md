# Native batched phase-cell boundary inverse

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

This theorem instantiates BATCHED-INVERSE.md at the actual phase-cell Gaussian inverse in the retained RaD report, rather than the stronger near-identity subclass of PR #4554. It changes the arithmetic algorithm; no Turing-machine implementation or execution tariff is used.

## Exact source and scope

The source is references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md, sections “The Schur boundary remains small” and “Two interior passes and one boundary solve”, together with its cited review-phase-cell-inverse.md. Its actual rational rounded matrix H has diagonal-dominance gap at least 1/(8p), row norm below 2 and ||H⁻¹||∞ ≤ 8p. The Gaussian tail, similarity construction, phase cells, Schur formula and their error estimates are predecessor mathematics. We retain their exact algebra and replace the online arithmetic below. This is a sufficient complete algorithm for that inverse map on arbitrary bounded complex data, not by itself a multiplication theorem.

Let p > 100, u = α² = Θ(p^r), d = Θ(p^ε), and w = ceil(sqrt(16p/u))+2. Assume the source's actual parameter restrictions, including ε+r < 1 and ε > (1−r)/2. Every physical phase cell then eventually has more than 4w entries, and each cell has Θ(d) entries, including the two distinct endpoint cells. Put T for the full tensor volume and Rᵢ = T/sᵢ for the parallel fibers of axis i. All sᵢ and p have the source's polynomial numeric bounds in n, sᵢ = n^o(1), and eventually Rᵢ exceeds every fixed power of p.

## Constructive native algorithm and cost

In each cell, keep the first and last w entries as boundary vertices. The interior matrix is exactly diagonal-similar to the source's explicitly rounded symmetric banded Toeplitz matrix. Its inverse is evaluated by the stated Gohberg–Semencul formula: four triangular Toeplitz products, each an ordinary convolution, plus explicit diagonal scaling. Use the direct bounded-word radix-two FFT and paid root/exp routines from PR #4554 for these length-O(d) convolutions, at the guard precision below. This takes O(d log(d+2)) native instructions per cell. Both interior passes are charged. Across all fibers and axes their total cost is O(T d log(p+2)). No packed large-input multiplier is a subroutine.

The boundary Schur complement S has bᵢ = O(sᵢ w/d) vertices in inherited physical order, cyclic half-bandwidth at most 2w and row norm below 2. Its rounded dyadic form has gap at least 1/(16p). Prepare its ordinary-band LU factors and periodic Woodbury data by the source's explicit finite algorithms, once per axis. They are shared data, not advice or inverse oracles. The source gives

    ||U||∞ < 2,       ||L||∞ ≤ 65p²,
    ||L⁻¹||∞ < 32p,   ||U⁻¹||∞ ≤ 1040p³.

The periodic correction has rank at most 4w and explicitly prepared matrices Z,V,K⁻¹ with

    ||V||∞ < 2,       ||Z||∞ ≤ 16p,       ||K⁻¹||∞ ≤ 33p.

Choose a power-of-two block size H with 4w ≤ H < 8w. Pad the ordinary triangular systems with independent unit diagonal coordinates if necessary. Their contiguous diagonal-block inverses are the corresponding principal blocks of the triangular inverse, so all hypotheses of BATCHED-INVERSE.md hold with polynomial bounds in p. Prepare those inverse blocks by ordinary triangular substitution on unit columns. Apply both triangular solves to batches of H independent right-hand sides using the explicit seven-product Strassen routine. Since Rᵢ ≥ H eventually, this costs

    O(bᵢ Rᵢ H^(ω−2)),       ω = log₂ 7.

Apply the periodic closure as y − Z K⁻¹ V y. The selector/corner map V has support in O(w) coordinates and is explicitly stored. Its products, the O(w) by O(w) K⁻¹ product, and the bᵢ by O(w) Z product are partitioned into H-sized matrix blocks and the same right-hand-side batches. Their cost is covered by the same bound, because bᵢ ≥ H eventually. Do not apply Z separately to each right-hand side; that would repay the bandwidth factor.

Both off-diagonal couplings H_BI and H_IB are charged. Each cell has O(w²) coupling entries, supported only on its two boundary strips and the adjoining interior strips of length O(w). Express them as a fixed number of O(w) by O(w) dense block products against the same batches of fiber columns. The work per axis is O((sᵢ/d) Rᵢ w^(ω−1)), identical to the Schur solve bound. The O(sᵢ Rᵢ) gathers, scatters and splits are also included. Two endpoint cells and periodic corrections remain separate explicit blocks; no undeclared cyclic merge is used.

Therefore the complete online inverse per axis costs

    O(T log(p+2) + (T/d) w^(ω−1)).

Summing d axes gives the sufficient native bound

    O(T [d log(p+2) + w^(ω−1)] + n^o(1)).                 (1)

The n^o(1) term pays the complete axis preparation, including phase generation, Gaussian coefficients, GS generators, Schur entries, ordinary factors, inverse diagonal blocks and all Woodbury data. Exact rational preparation is implementable using signed multiword grade-school arithmetic and Gaussian elimination on explicitly stored finite matrices. Its dimensions and rational numerator/denominator lengths are polynomial in sᵢ and p, so it costs poly(sᵢ,p) = n^o(1), with each elementary word operation charged. Only guarded O(p)-bit coefficients are retained online. The shared native exp/phase construction additionally costs O(n^η polylog n) for any fixed η > 0 selected by the outer caller. It is paid once and is not subsumed into n^o(1).

## Stability, word width and exact periodic closure

The source already proves all polynomial inverse and intermediate bounds of the completed interior–boundary–interior composition. No stage is replaced by an assumed unknown transformation. For the new batched triangular solve, BATCHED-INVERSE.md gives error ≤ 24 B⁸ v for scalar grid spacing v, provided v ≤ 1/(12 B⁶). Here B is polynomial in p for the boundary factors and their right-hand sides: the source bounds the first interior output by 8p, boundary right-hand side by 17p, and later completed values by O(p²), on unit-norm input.

For a block matrix product the grid error is ≤ H²v per entry. Any prepared matrix coefficient errors are bounded in induced row norm by the sum over its O(w) columns, so a polynomially smaller coefficient budget covers them. The source's Z, V and K⁻¹ operator norms are polynomial, and the periodic closure has a fixed number of completed products. Thus its total new error is poly(p) v, with no exponential dependence on bᵢ, the number of cells or fibers. The arbitrary-input bound follows by homogeneous norm scaling; a log(max(1,||input||∞)) precision guard is explicitly paid.

The unchanged local GS maps may amplify internally by 2^(8p+O(1)); their four native FFT convolutions require only O(p) fractional and integral bits because d is polynomial in p. Allocate enough of the source's 2^(-32768p) grid budget to every new FFT, preparation rounding, Strassen and closure product. Equivalently choose a larger fixed constant times p if a particular FFT implementation uses a larger fixed error constant. The source's completed-map perturbation argument then preserves its final 2^(-p-10) inverse error and normalization N⁻¹/2^ceil(log₂(32p)). Every intermediate, exact product, division numerator, address and counter fits a single sufficiently large common Θ(log n)-bit physical word budget; the fixed constant must cover the FFT root-generator's private working precision too. Complex arithmetic uses four real matrix products and a fixed number of real sums.

This explicitly handles the periodic Schur closure and both coupling directions. A necessary condition, failed search or unknown inverse oracle is not being offered as the result.

## Exponent consequence for an actual outer caller

Since w² = O(p^(1−r)), formula (1) becomes

    O(T [p^ε log(p+2) + p^((ω−1)(1−r)/2)] + setup).

The exact integer inequality 7^16 < 2^45 gives ω < 45/16, so the boundary exponent is strictly below 29(1−r)/32. With Tp = Θ(n), the inverse map itself consequently admits any normalized saving strictly below

    min(1−ε, (3+29r)/32),

with its own logarithm absorbed by strict slack. Thus for small positive r its boundary component allows a fixed saving greater than 3/32. This is much larger than the approximately 0.003020165 Fourier-kernel saving under discussion and removes the old requirement that the final saving be below r. It does not by itself assert that the complete multiplication caller has that saving: root generation, forward maps, kernel, twiddles, input/output, products and recovery must be present in the full outer assembly. In particular, use the actual provider tariff T p^τ if supplied; do not substitute an unrelated εq kernel formula merely from a rank-saving name.

## Evidence and provenance

The new executable leaf batched_band.py checks the actual fixed-grid Strassen and inverse-block substitution machinery: 36 systems, 1,785 independent residual entries below 2⁻⁷⁰, including partial batches, signed inputs and an overflow rejection control. It does not replay the entire asymptotic phase-cell caller. Existing phase-cell finite prototypes and source reviews retain their original scope and credit. This corollary supplies a new informal universal assembly of those exact algebraic maps with the checked native batching primitive.

The retained phase-cell construction and reviews credit the RaD campaign, Gohberg–Semencul (1972), Feng–Wu–Wei's primary formula exposition, Harvey–van der Hoeven Gaussian resampling, and the upstream integer-multiplication manuscript. Strassen's seven-product identity is classical. PR #4554 contributes the paid native finite-word exp/phase/root/FFT routines and their Gaussian lineage. Our contribution is batched native boundary and coupling evaluation with polynomial residual control. No fresh Lean verification, new TM κ, practical speedup or worldwide novelty is claimed.
