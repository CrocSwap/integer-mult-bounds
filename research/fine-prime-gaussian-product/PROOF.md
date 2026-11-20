# From two binary words to an exact product

Let n be the larger of the two input lengths, including leading zeroes. For n in the fine regime put b=ceil(log₂ n), p=6b, d=2^floor(.997 log₂ p) and q=8p. Let T be the least power of two at least ceil(4n/b). Distribute log₂ T address bits as evenly as possible among d axes, longest first. Each target side is r or r/2. Write ell=log₂ r, S=∏s_i, and V=Tp. All asymptotic constants are independent of the payload and its length. The fixed source prime of the ordinary interchange is a separate constant.

## The controller admits all sufficiently large lengths

The code computes every floor in these exponents with integer powers and bit lengths. We have d=Θ(p^.997), ell=Θ(p^.003), T=Θ(n/b) and V=Θ(n). It searches odd integers in

    ceil(tp²/(p²+1)) ≤ s ≤ floor(4tp²/(4p²+1)).

The interval contains the fine interval in the retained proof. Apply Trudgian's bound for π(x)−li(x) at the two endpoints. The integral over an interval of length Θ(t/p²) is Ω(t/(p² log t)). The ratio of the endpoint errors to this count tends to zero since p²(log t)^(1/4) exp(−c sqrt(log t)) tends to zero. The count eventually exceeds d at both sizes. The two intervals are disjoint. Trial division over every candidate costs at most d·poly(p,r)=2^o(p)=o(n). For the selected primes 1/(4p²)≤θ=t/s−1≤1/p² and T/S≤(1+1/p²)^d=1+o(1). Consequently 2ceil(n/b)−1≤S<2^b eventually. [Fine prime construction](../unconditional-batched-crt/vendor/FINE-PRIME.md) · [Trudgian, Theorem 2](https://arxiv.org/html/1401.2689v2#S2)

Set α=2+floor(sqrt(2ceil(log₂(16p)))), W=2α(1+floor(sqrt(q+1))) and B=2^floor((9/8)log₂ p). Then α²=Θ(log p), W=O(sqrt(p log p)), B=Θ(p^(9/8)), and eventually 4W<B≤min t_i. Every B is a dyadic divisor of every target side. Below the fine regime the controller has two finite Gaussian geometries and an explicit binary shift-and-add algorithm. Only a failed parameter search or a failed input-independent coefficient certificate can select that elementary algorithm. A payload assertion or a damaged byte stream cannot do so. The CLI returns the route in its receipt.

## The source operator on the executed coordinates

For each input coefficient at j put q_j=floor(tj/s+1/2), β_j=tj/s−q_j. Distinct j occupy distinct original target cells. The expansion A is the periodized broad Gaussian with those input columns. It has an identity column at each hole. N is the original normalized narrow matrix on the occupied coordinates and identity on the other coordinates. D is exp(πα²β_j²) there and one on the holes. C is the restriction to occupied coordinates. Negative Fourier matrices below divide by their lengths. P_t reads target frequency −sk modulo t and P_s reads source frequency tj modulo s. Periodization and Poisson summation give the one-axis identity

    D N⁻¹ C P_t F_t A = P_s F_s.

For example, before the input column gauge D, applying P_t F_t to the periodically sampled broad kernel and summing the Fourier series of the Gaussian gives the narrow periodization acting on P_s F_s. Its selected row j and column j+h, after the column gauge, have exponent −πα²[(t h/s+β_j)²−β_(j+h)²]. Every h in the source congruence class contributes. Since N is invertible, left inversion gives the displayed equation. The source theorem supplies this exact analytic identity. Its separate sufficient bounds for numerical inversion on a wide-θ family are unnecessary here. The augmented identity columns act on the zero holes at ingress. All numerical error bounds apply to arbitrary padded entries during computation. Complex conjugation gives the other sign. [Original resampling argument](../../upstream/build/sections/07-resampling.tex) · [Independent source definitions](../certified-gaussian-recovery/PROOF.md)

`gaussian_pages.py` uses outward intervals for π, exp and positive reciprocals. The two arctangent series follow from π/4=atan(1/2)+atan(1/3). On a reduced exponent in [0,1/8], consecutive Taylor terms bracket the remainder. The code rounds their products out before alternating the signs. At the first term of upper size one unit it adds that unit to the appropriate endpoint. Squaring outward restores the unreduced exponent. For 3x≥P+1 the direct enclosure [0,2^-P] of exp(−πx) is valid. For smaller x, there are O(log P) squarings, each of which increases interval width by at most a constant factor. Summing O(P) grid errors in the reduced series thus gives width poly(P)2^-P. Positive reciprocals add their explicit condition factors. The generator sums both signs of every displacement through W at the actual global period, then adds a rigorous geometric bound for all omitted terms. Dense rational matrices occur only in this input-independent setup.

On aligned B-blocks without holes, q_j=j+c with one c. Two diagonal factors then turn the truncated Gaussian into a Toeplitz kernel. Fold that kernel modulo B and call the resulting gauged circulant J. J is identity on impure blocks. E contains all their positions and the first and last W positions of each pure block. Use one rational reference Q. Set Q to the direct global-period midpoint on E×E and to the product of the actual rounded block factors elsewhere. The truncated true kernel and an unwrapped J agree outside E×E before rounding. Artificial wraps are entirely in E×E. Thus Q=J+E R Eᵀ exactly. Each circle runs two normalized FFTs of length B on contiguous low bits of the chosen coordinate. Its final diagonal restores B once. The narrow operation evaluates

    Q⁻¹ = J⁻¹ [J + E(R F⁻¹ R − R)Eᵀ] J⁻¹,
    F⁻¹ = Eᵀ Q⁻¹ E.

The middle F is the Schur complement after eliminating interior intervals. Each such interval touches only the strips on its two sides. In cyclic E-order R and F therefore have bandwidth at most 4W+2. The executable source checks the band before it emits coefficients. It solves with bordered LU, including its last dense rows and columns, and then applies D. The broad map only evaluates J+EREᵀ. [Gauges, wraps and local inverse](CIRCULANTS.md) · [Schur complement and border schedule](SCHUR.md)

## Coefficient admission and size

The retained absolute-row estimate for the original narrow map gives
‖N−I‖∞≤exp(−2aθ)+5exp(−2a), where a=πα². Here a≥4 ln(16p), so the dominance gap is Ω(p^-2) eventually. The shifted local circulant has a separate Ω(p^-2) gap, proved in [CIRCULANTS.md](CIRCULANTS.md). Every local gauge and reciprocal is bounded by exp(O(α²θB²+log p))=2^O(p^(1/4)log p). In the broad factor the recentering of the linear chirp is essential to that estimate. The diagonal D is at most exp(a/4)=poly(p). [Original row estimate and conditioning](../unconditional-batched-crt/vendor/FINE-PRIME.md)

The coefficient grid uses P=2q+128+4 bitlength(t), with 64 additional setup bits for the local exponential gauges. Multiplying the interval unit by any polynomial in P,t and the preceding gauge bounds gives 2^(-2q+o(q)). The broad discarded row tail is O(poly(p) exp(−π(s/t)²(W+1/2)²/α²)), which is smaller than 2^(-2q) eventually. The narrow Gaussian has a smaller tail even after the D factor. Consequently the explicit induced-row defect tested for Q is 2^(-2q+o(q)). This also holds for D. There is no requirement to represent every tiny entry by a positive grid unit. Only the two diagonal gauges and the reciprocals that are actually used must be nonzero.

The direct broad row sum is O(1). This follows by summing the shifted absolute Gaussian over the integers, with s/t≥1/2, including the factor 1/α and the extra hole identity. The narrow gap persists for Q by perturbation. Hence ‖Q⁻¹‖∞=O(p²), and the inverse perturbation bound in `assemble_factor` is at most poly(p)2^(-2q+o(q)). This proves eventual acceptance of each normalized local defect at the strict 2^(-q−3) guard. It also proves that broad shifts are O(1) and narrow shifts are O(log p). With Γ the sum of the generated shifts per complete call, Γ=O(d log p)=o(p).

Setup includes the entire encoded axis catalogue, the cyclic inverse and both dense exact inversions for F. To bound rational growth, clear the common dyadic denominator in Q and J. All entries then have poly(t,p) bits. Each inverse entry and intermediate Gauss–Jordan pivot is a ratio of minors of dimension at most t. The determinant expansion bounds their bit lengths by O(t(L+log t)) when L bounds entry lengths. Apply this bound successively to the principal restriction of Q⁻¹ and to the resulting F. There are a fixed number of successive inversions. Slotwise rational reduction and even a complete linear tape search for every setup access cost poly(t,p). Exact private arithmetic, spectral tables, serialization, readback, assembly and clearing summed over all d axes cost 2^o(p) time and space. The setup grid and those rational lengths are private.

All factors used in the online algorithms are bounded by G=2^g, where g=O(ell+p^(1/4)log p). For the condensed solve use the Schur formula, ‖Q⁻¹‖ and preserved row margins. For J⁻¹ use the local circulant gap with the two reciprocal gauges. The numerical field uses q+80g+32 fractional bits and q+120g+48 signed bits per component during a factor. The synthetic polynomial middle lifts by O(log(T/r)+d). The C program on h≤d axes adds O_word(h) bits. Every full-array component width is O(p). The online Kronecker product separately packs one frequency row into O(rp)-bit integers. It consumes and releases that row before advancing to the next frequency. Its four real multiplications, their signed codecs and all temporary storage are included in the ring bill.

## Rounding, CRT and carry

The triangular CRT permutes an exponent k to k/(∏_(j>i)s_j) mod s_i in physical axis i. It is a group isomorphism. Both input streams go through it and the output uses its true inverse. It injects and crops all fields on the original q_j, including the final opposite result. Source frequency permutations are present in both signs. For U=P_s F_s and U⁺=P_s F_s⁺ on the tensor source,

    U⁺[(Uu)·(Uv)] = (u*v)/S².

Indeed the source permutation commutes with pointwise products, and F_s⁺ P_s=P_s⁻¹ F_s⁺. Two normalized forwards, one normalized opposite and a normalized source transform leave two divisors S. Each operand also has digit scale 2^(-b−2). The exact integer scale applied in `recover` is S²2^(2b+4+3Γ). The synthetic FFT has its own single restoration T/r already inside the normalized middle. [Chirp and ring normalization](MIDDLE.md) · [Original coordinates and CRT](ROUTING.md)

Every fully normalized axis is a contraction. At the producer's work grid the arithmetic defects of the two local FFTs, spectral tables, border arithmetic, two inverse circles and the D factor sum to less than 2^(-q−4) before its final shift. Under the fine coefficient admission guard each completed factor has absolute error <3·2^-q on a disk of radius one. The complete chirp middle admits half-disk inputs. Its defect is <3·2^-q on the grid actually used. The exact intermediate disk proof and the strict inequalities, including the separately folded ring product and both scalar drops at the pointwise product, are in [ACCURACY.md](ACCURACY.md).

On the fine geometry the controller computes the following common rounding radius before digit ingress. It depends only on the geometry and generated coefficients.

    (64d+64) S² 2^(2b+4+3Γ−q).

Since log₂ S<b, b=p/6 and Γ=o(p), the radius tends to zero. The proof checks the physical half-disk entrance before applying the global recovery bound. On the second finite geometry, linear operator error is charged at the actual input and intermediate radii using the contraction of the generated reference as well as the true operator. The integer guard remains strict after rounding the rational bound upward to the public grid. [Finite geometry with interior cells](RECOVERY-RADII.md)

All true coefficients are nonnegative integers. Strict radius below 1/2 gives their unique nearest integers, including true zeroes. The recovery pass also scales the imaginary part and checks the exact squared complex distance to that integer against the admitted squared radius. Its additional word products cost O(V log² p) and one running maximum. The proof of which integer is correct comes from the operator error. By 2ceil(n/b)−1≤S, cyclic wrap cannot change the ordinary convolution. The inverse CRT returns coefficients in digit order. A carry from the low end followed by the exact fixed-width binary output gives the input product. The default CLI prints these bits in linear time. An optional JSON receipt formats finite diagnostics.

## Fixed-tape invoice

| Executed work | Bit time, up to fixed powers of log(p+2) |
| --- | --- |
| Parameter search, all Gaussian setup and the emitted catalogue | 2^o(p) |
| Two binary ingresses, pointwise, original masks, recovery, inverse-order carry and output | O(V) per scan or scalar product pass |
| Broad and narrow circulating kernels | O(Vd log B) scalar/word passes |
| Boundary gathers and their inverse | O(Vd[1+μ log r]) |
| Cyclic residual and bordered LU | O(Vd μ(W+1)) |
| Nonlinear CRT prefix shifts | O(Vd)+2^o(p) for setup, with prefix work O(d T poly(p)/min t_i) |
| CRT bit permutations | O(V ceil(p/d) d^.998263) |
| Cached chirps, ring rotations and short signed word products | O(V(ell+log p)²+V ell) |
| Grouped butterflies in the three synthetic ring FFTs per middle | O(V ell d^.998263) |

Here μ≤2W/B+B(t−s)/t=O(W/B+B/p²). The sparse arithmetic terms have powers at most .997+1−9/8=.872 and .997+9/8−2+1/2=.622 before logarithms. The sparse movement terms have powers at most .375 and .125. The dense per-axis terms use p^.997. No full-field permutation of all ell bits is run on each axis. The local Gaussian FFTs connect only log₂ B bit pairs. The complete layout costs, including all fit and exceptional rows in an ordinary request, give the stated butterfly price under the primitive results identified below. [Grouped butterfly recurrence](BUTTERFLIES.md) · [Disjoint CNOT and arbitrary spectators](DISJOINT-CNOT.md)

The common power for CRT permutations and the middle is 1−.997·.001737 = .998268211. It is strictly below 1−.00173097911567079247276057, even after absorbing every fixed polylog(p). Repeating complete transformations or CRT conversion three times is a constant. This is the required time comparison for the #4100 budget. It does not put this construction ahead of the selected conditional numerical frontier. [Outer construction](../unconditional-batched-crt/PROOF.md)

The tape interpreter charges real head displacement in bits, not unit indexed access. A dyadic split alternates contiguous chunks; its public index fits O(p) bits. Each full complex record has Θ(p) bits. Prefix rotations charge arithmetic on O(p)-bit counters once per exponentially long row. An ordinary packet uses its actual opaque suffix width. The few external Python lists serialize complete streams between stages. Their writes, reads, copies, rewinds and erasures add O(V) per crossing, included in the table. Setup tables of size 2^o(p) may be naively indexed with a linear search. Word products above the fixed base case go through the acyclic physical FFT word. The numerical trace counts model tape events only. It is neither Python process memory nor a count of every bit transition of a child.

At every Gaussian stage only a constant number of full fields coexist. The compact stream is ≤T records and the border has at most one line plus its pages. The CRT uses fixed role banks, the C recursion parks complete inactive rows on one stack with geometrically decreasing volume, and the ordinary child uses its own fixed inventory. The binary port and diagnostics add O(V). This gives O(V)+F_Q peak backing, including all private Gaussian setup and the fixed ordinary compilation constant. Each success path restores borrowed inputs and cursor origins at their specified interfaces and releases owned payloads, scratch, page storage and temporary packets.

## Scope of the argument

The analytic Poisson identity, Trudgian's prime-count theorem, the short physical word multiplication theorem (including its normalized FFT numerical proof), the finite all-column dyadic C word existence theorem, and the compact caller's logical endpoint, stock and refinement theorems are predecessor results. The last three repository proof chains retain their published review status. The ordinary and butterfly argument needs their stated domains for the proposed complete-rate conclusion. It does not posit a Gaussian/Fourier service that already performs the task. Finite products check executed code; the universal implications above are mathematical arguments. See [the dependency and attribution record](SOURCES.md).
