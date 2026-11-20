# Original coordinates, exact bits and total cost

Use the dense dyadic layout, bit stock, private threshold and primitives of [ASSEMBLY.md](ASSEMBLY.md). This last part discharges the hypotheses passed to the numerical Lean theorem. It also collects the time of the operations outside the two supplier recurrences.

## Identify the two kernels in the code

Each operand occupies the same CRT layout Φ(k)_i = μ_i k mod r_i. At spatial index Φ(j) and returned frequency index Φ(k) the executed character of the source Fourier transform of either sign is

    product_i exp(±2πi j k t_i μ_i² / r_i)
      = exp(±2πi j k u / S),
    u = sum_i (S/r_i) t_i μ_i² mod S.

Modulo r_i every other summand vanishes and this one is a unit. Thus u is a unit modulo S. This is the permutation induced by the retained physical transform of the actual CRT-indexed stream. Both forward transforms use u and the opposite transform uses the same u. Fourier orthogonality makes the middle frequency sum vanish unless j+k equals the recovered **original** coordinate. Three factors 1/S and one nonzero frequency sum S leave 1/S². There is no extra inverse permutation, and retaining a frequency permutation that is unrelated to Φ on the opposite leg would be incorrect. These equalities are proved for arbitrary positive coprime side lengths, computed prefix inverses and both signs in [Coordinates.lean](lean/Coordinates.lean), [Integrated.lean](lean/Integrated.lean) and [Recovery.lean](lean/Recovery.lean).

Scale each radix-B digit by 1/(4B). The two forward means have exact radius at most 1/4. Apply each transform with the public error e ≤ 3/B⁶ just derived. Form the pointwise grid product by one exact signed numerical product and componentwise truncation, with error <sqrt(2)/B⁶. This uses O(p log p) steps per record. The perturbed inputs to multiplication have radius at most 1/2. Its output is in the opposite transform's 1/2 disk. The error between the final transform and the exact result at every coordinate is at most 3e. The proof uses the two separate product-error terms and the maximum-norm contraction of the opposite mean on the propagated error. It uses no statistical averaging. See the declarations `product_error` and `recovered_product`.

For the theorem's arbitrary-complex multiplication interface use M(x,y)=Q(Q(x)·Q(y)), where Q is p-bit toward-zero truncation on both components. On the half disks, telescoping the two input errors costs at most (1/2+1/2)sqrt(2)/B⁶. The output conversion adds at most sqrt(2)/B⁶. This is strictly below 3/B⁶. On the actual represented arguments each input conversion is the identity. The same entrance convention for the two source-transform maps is proved at the end of [ASSEMBLY.md](ASSEMBLY.md).

On every valid output multiply by the exact integer (S·4B)². The result lies within

    (S·4B)² · 3e ≤ 144/B² < 1/2       (B ≥ 32).

Both the factor S² and the independent digit factors (4B)² matter. Apply nearest-integer conversion to the real component. There is no tie. On padded holes use zero. The inverse CRT is a permutation, so it can neither mix an invalid output into a valid one nor change its rounded value. On the original stream the coefficients are nonnegative, less than B³, and have no cyclic wrap. Pay O(p log p) per scalar for the exact rescale and conversion, using the same unconditional short-word primitive. The final scan sends c plus the incoming carry to the low b output bits and the quotient by B to the next position. The carry has O(b) bits, including the last residual, whose base-B digits are written in increasing order. Trim leading zero blocks according to the output convention and present 2n bits if requested. This computes the integer product, independent of operand contents. Reversing a big-endian external tape or bit stream uses a single reverse traversal on a work tape.

All hypotheses of `MixedRankIntegrated.product_at_physical_coordinates` now have producers. The actual primes and dyadic widths imply its coprimality and B bounds. The true operand length supplies the two digit bounds and support condition. The grouped Gaussian producer, synthetic middle and common public truncation supply hfw and hbw **for every signal in the half disk**. Exact short arithmetic supplies hm. Lean then proves the output radix value equals the product. The all-size producer error, the rate and the correspondence to the specified tape program are written mathematics outside that Lean declaration. The finite Python product probe uses different, explicitly small control sizes for this reason. [Formal theorem](lean/Integrated.lean) · [Small integration experiment](check_product.py)

The stronger `MixedRankPublicGrid.grid_product_at_physical_coordinates` applies this reasoning directly to `wordDecode`. It proves the signed toward-zero conversions, fixed points on represented inputs, the product perturbation, the actual radix-digit representation, and compatibility of the represented packet with the extended maps. Its only numerical arguments are the raw forward and opposite transform accuracies ≤(B⁶)⁻⁴ on represented half-disk inputs, supplied by the preceding all-size estimate. [Actual grid-word theorem](lean/PublicGrid.lean)

## Sum the complete operations

Use the mixed head's exact prices. Put a_BIT=0.003879928035646, q=κ+3g, a=κ+4g, and ξ=ε(1+q)−3/32+g. The table gives the power of p *after dividing time by V*, up to a fixed power of log p. All inequalities are strict. The 54 original inequalities and four auxiliary guards are checked at the pinned head. The last two rows here make additional whole-array movements explicit. [Kernel-checked powers](lean/OuterPrices.lean) · [Original outer equations and prices](https://github.com/CrocSwap/integer-mult-bounds/blob/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/review/independent.py)

| Operation on a complete phase | Exponent |
|---|---:|
| Middle tensor butterflies, including all significance levels | 1−εq |
| Full-support placement at a complete outer call | 1−a |
| Grouped Hadamards on the native word | ε−qβ |
| Grouped ordinary BIT moves and core gather | ε−aβ |
| One scan per group and per-stage fixed logarithms | ε−β |
| Banded matrix arithmetic with priced right-hand sides | ε+29/32−ξ |
| Current-value union movement | ε+1/2−ξ |
| Signed packed polynomial multiplication | 1−ε |
| Returned first faces, including shrinking archive transport | ε+β+54−128 |
| Three balanced CRT conversions | 1−a_BIT+2(1−ε) |
| Full padded insertion and extraction at true q images | 1−ε |

The three transforms differ only in signs and in their data. Running them and the CRT three times is a fixed factor. The internal exact native precision is turned on only during the corresponding H or BIT stage. Active complete ordinary banks, old high matrices, final transposes and cleanup have already been counted at their caller. The word is never invoked as a free oracle. Numerical scalar products and chirp scans add O(V polylog(p)). All setup scans over complete *one-axis* ranges cost 2^o(p)=o(n), while local page preparation is additionally charged at each eligible core. Exact numerator widths and determinant bit lengths are polynomial in p there. Full row-copy, compact guards, restored data, full-face transport and all recursive calls are in [FRAMES.md](FRAMES.md), [ORDINARY.md](ORDINARY.md), [COMPLEX-LAYER.md](COMPLEX-LAYER.md) and [GROUPED-GAUSSIAN.md](GROUPED-GAUSSIAN.md). For each fixed exponent with room δ>0, (log p)^K = o(p^δ) for fixed K. Thus the sum has time O(n(log n)^(1−κ)).

Use a constant number of full arenas reused by serial stages. Frame backing is geometric along an active call chain. The number of different ordinary stage indices on a chain is bounded by six. Old high matrix fibres remain live in each low child. Price cold and fallback calls, return to the saved heads, then physically erase the largest historical interval in that child. Full CRT passes run by **level** in previous/output arenas. No chain of log d full parked arrays is held. Each sparse key has O(p) bits. All face buffers, keys, masks and full RHS transposes stay within O(V). The separate 2^o(p) tables, evaluator and short-product scratch for a single call fit in O(n). A time bound alone on the Harvey–van der Hoeven primitive suffices since only one such short product runs at once. All complete Gaussian fields, including native temporaries of each scalar, use O(p)=O(6 ceil(log₂ n)) bits per component. A packed polynomial is a sequential stream of r such scalars. Total maximum *ever visited* backing on the fixed tapes is O(n).

## One machine for all lengths

Generate both finite integer templates on the fixed carrier dimensions before the large-input recursion. All loop bounds used to produce them are finite integers. Exact matrix rank and rational basis calculations determine a finite list of denominators and minors. Exclude the primes dividing them and select one sufficiently large remaining prime by trial division. Keep this word fixed for all n. It may be placed in finite control or generated once from a fixed finite description on work tapes whose maximum setup cost is a constant relative to n. The same argument applies to fixed tables for fixed q, including the q² bucket interfaces. It cannot justify a free table as a function of p. The preceding proof charges those separately. All input-dependent dyadic exponents, guards, branch counters, windows, radius thresholds, row counts and tape extents are computable. Avoid transcendental equality tests by using integer width and outward intervals as in the Gaussian producer.

Take a cutoff above all of the sufficient bounds in these proofs. Such a fixed integer is effective. Constants in finite templates come from finite enumeration. Powers beat logarithms effectively by bounding exp(δ log p) below by a Taylor term of sufficiently large fixed degree. Bounds involving exp(−c sqrt(log t)) use the explicit prime estimate and the same comparison. Fixed finite matrices and all requested inequality tests use exact rational or outward arithmetic with strict room. For horizons on stopped ordinary and complex recursions use integer power comparisons and the elementary branch at each stated bounded terminal. Alternatively check the integer geometric guards at each input and run elementary multiplication if a guard fails. The estimates above prove a common tail on which every guard passes. Use elementary multiplication at the bounded starting lengths. A large fixed constant absorbs all their times and scratch. This proves uniformity in n with a finite alphabet and tape count. It gives no practical size for the first fast input.
