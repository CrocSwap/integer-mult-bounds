# Error from Gaussian input tapes to integer coefficients

This proof applies to `axis_program.Factor.run`, `fine_ring.chirp_middle` and the three calls in `product.multiply`. It covers every value for which the stated geometry, coefficient and arithmetic guards hold.

## Error on one physical axis

Use the maximum of complex moduli on a field and the maximum absolute row sum for an operator. These norms also bound fields with dirty padded holes and arbitrary spectator coordinates. Let `q` be the external grid precision, `g=condition_guard`, `G=2^g`, `w=q+80g+32`, and `u=2^-w`. Assembly gives `G>=4`. The side, the length of each short FFT, all three unscaled factors of each circle, each row norm of the residual, the real end diagonal, the norm of the Schur complement and the inverse of its strict row margin are at most G. Both the full inverse of Q and its principal submatrix on the boundary have norm at most G. These statements follow from `max_gain`, the disjoint blocks and the Schur estimate below.

Component truncation towards zero adds less than 2u in complex modulus. Each input root from `root_word` has modulus at most one. Its complex error is at most 3u from its two outward width tests. For one full short FFT of length B, the computed modulus never increases at a unit rotation or an averaged butterfly. Each of its at most G levels adds at most `u(3R+4)` error for input radius R. This holds for both DIF and DIT.

The spectral diagonal multiplies by the unnormalized eigenvalues. Their exact moduli are at most G. The emitted real and imaginary parts have complex error at most `(3G+2)u <= 4Gu` since the total absolute coefficient mass is at most G. The exact input diagonal has norm at most G. The output diagonal in the code includes B and has norm at most G². Both have coefficient error at most u. A telescoping sum through these two diagonals, the two normalized FFTs and the spectral diagonal gives

    circle error on radius R <= G^9 u (R+1).

In detail, the five error terms, before multiplication by u, are at most `G³(R+2)`, `G^4(3GR+4)`, `G²(4G²R+2)`, `G³(6G²R+4)` and `2G²R+2`. The computed spectral values have modulus at most 2G. The intermediate radii are at most 2G⁴(R+1). The exact, complete circle has norm at most G³. Its inverse circle has the same bounds with its separately tested inverse coefficients.

Let E be the boundary and D the residual there. A full residual row or its real diagonal restriction has at most G products. Coefficient truncation and product rounding give error at most `Gu(R+2) <= G³u(R+1)`. All terms are charged even for the cyclic antipodal offset on even extents.

For the narrow solve, F is the Schur complement after the interior is eliminated from Q. The strict row margin of Q is at least 1/G. This margin persists at every scalar elimination. If row i is updated at pivot k, use the old triangle inequalities in all columns and `sum_(j!=k) |a_kj| <= |a_kk|-1/G`. The new margin is at least the old margin plus `|a_ik|/(G |a_kk|)`. Principal submatrices also preserve the margin. Thus F, its principal restrictions and its subsequent Schur complements have inverse norms at most G. For the no-pivot factorization F=LU, each row of U is a row from such a complement. In particular U has margin at least 1/G. The direct Schur formula gives `||U|| <= ||F|| + ||F||² G <= 2G³`. It follows that

    ||U^-1|| <= G,      ||L^-1|| = ||U F^-1|| <= 2G⁴,
    ||L|| = ||F U^-1|| <= G².

In the latter two equalities the norms refer to the displayed products, with submultiplicativity used for the inequalities. Border accumulators only reorder the same exact sums. Consider the actual forward result y, input radius R and Y=||y||. It satisfies `||Ly-b|| <= Gu(Y+2)` because all products truncate and every stored coefficient has error at most u. Consequently `Y <= 4G⁴(R+1)` and `||y-L^-1 b|| <= 10G⁹u(R+1)`.

For the computed backward output x, write X=||x||. The accumulator z_i before multiplying by the stored pivot reciprocal satisfies `|z_i| <= Y+(2G³+Gu)X+2Gu`. The product with the inwardly rounded reciprocal has residual at most `2G³u(|z_i|+2)` after multiplication by the true pivot. Including the other row terms yields

    ||Ux-y|| <= 8G⁶u(X+Y+2).

Absorb the term `8G⁷uX` using `w>=80g+32`. Then `X <= 2G(Y+1)` and `||x-U^-1 y|| <= 32G⁸u(Y+1)`. Together with the forward error this gives

    ||computed_solve(b) - F^-1 b|| <= G^16 u(R+1).

The unnormalized narrow computation first runs J^-1. On that output it runs J and a branch that applies D, F^-1 and D. It combines the three terms `Jz + D F^-1 Dz - Dz`, with boundary restrictions and extensions at their actual locations. It runs J^-1 again and multiplies by the real end diagonal. The identity

    Q^-1 = J^-1 [J + E (D (Q^-1)_EE D - D) E^T] J^-1

follows by inserting `J=Q-EDE^T` on both sides of Q^-1. Here E in the formula is the boundary injection. All sparse motions are exact permutations or partial selection and extension with zeros. For input radius at most one, the following bounds use the primitive errors above. The second column bounds computed radius. The last column bounds error from the exact execution at that node, divided by u.

| Node | Radius | Error divided by u |
|---|---:|---:|
| z = J^-1 x | 2G³ | 2G⁹ |
| a = Jz | 3G⁶ | 5G^12 |
| b = Dz | 3G⁴ | 3G^10 |
| c = F^-1 b | 4G⁵ | 5G^20 |
| d = Dc | 5G⁶ | 6G^21 |
| a+d-b | 10G⁶ | 7G^21 |
| apply J^-1 | 11G⁹ | 8G^24 |
| multiply the real end diagonal | 12G^10 | 9G^25 |

For broad expansion the code adds only Jx and Dx. These give smaller bounds. All stored complex values fit `w+40g+16` signed bits per component. For instance a forward solve partial row is at most `R+(G²+Gu)Y+2Gu`, a backward partial row is at most `Y+(2G³+Gu)X+2Gu`, and the largest circle input in the table is at most 10G⁶. Even 2G^20 exceeds these intermediate magnitudes. Unscaled products before division have at most twice the component bit width plus a constant.

The true full padded axis map, divided by its executed `2^output_shift`, has norm at most one. Assembly proves a coefficient defect below `2^(-q-3)`. The arithmetic error in the table is below `G^27 u < 2^(-q-4)` before that division. The final pair of inward q-grid truncations adds less than `2*2^-q`. For a page admitted at the fine or primary threshold, every completed broad or narrow axis therefore adds less than `3*2^-q` absolute error, for every input of radius at most one. The second finite geometry charges its larger geometric defects separately from the digital error in [RECOVERY-RADII.md](RECOVERY-RADII.md). Finite certificate bounds are independent of payload values.

## The padded fast middle

Put M=product of all padded axes except axis zero and d=number of axes. The ring computation uses `f=q+log2(M)+11` bits or more in its default branch. Its three normalized synthetic transforms shift to `f+log2(M)` before their first butterfly. This makes every intermediate H division exact for grid inputs. The exact sign rotations preserve those factors. Each completed synthetic transform drops to f bits once. A native H replacement must implement the exact normalized arithmetic on this divisible input, as the elementary and selected-C numerator conventions do.

The two chirp-weighted inputs have radii at most 1/2 and one. Fix their supplied chirp first. The twist, the two forward transforms, the normalized negacyclic product including its f-grid drop, and the opposite transform give an error below `14*2^-f`. Multiplication by M really takes place and enlarges that term to `14M*2^-f`. Both end chirp multiplications, the inverse twist and replacement of the three supplied chirps by exact ones give the uniform bound proved in `MIDDLE.md`,

    (24M+16d+16) 2^-f + 2*2^-q.

Each f-grid root component enclosure has error at most two units, and each product contributes less than two units in complex modulus. A prefix of length d therefore has error at most `5d*2^-f`. Reusing a cached prefix does not add levels to it. Each padded side is at least two and d>=2, so d<=M and M>=2. The entire middle error is strictly below `3*2^-q`, even when M grows exponentially in the original log length. Its physical entrance guard is the component Euclidean half disk.

The root generator's refinement loop has a private precision bound. For an order m=2^t, exact quadrant cases are emitted directly. Every nonzero coordinate magnitude in the remaining positive half-angle steps is at least sin(2π/m)>=4/m. The outward integer square root adds at most one unit of its internal grid. For the true nonnegative radicand x>0, an enclosed radicand y>=0 gives `|sqrt(x)−sqrt(y)|<=|x−y|/sqrt(x)`, even when its lower endpoint vanishes. Thus one half-angle recursion increases component error by at most m times the old error plus one internal unit. With at most t levels the total error is at most `(2m)^t 2^-H` at internal H bits. Any `H>=f+(t+1)^2+4` suffices for the two-unit acceptance test. The successive precision doublings retain `O(f+t²)` private bits, which is O(p₀) for the chosen side order. The same proof applies to the roots in local Gaussian FFTs. Materializing an entire global field at this setup precision is unnecessary.

## Exact product and external precision

Write `h=2^-q`, `Gamma=sum(output_shift)` over all broad and narrow factors of one call, and `lambda=2^-Gamma`. The original periodic Gaussian identity gives `D N^-1 C P_t F_t S_gauss = P_s F_s` on each selected source. The conjugate sign follows because its two Gaussian factors are real. Its tensor product `U=R F_s` is a contraction in maximum complex modulus. The CRT map is a group isomorphism, and the source-coordinate multiplier R commutes with pointwise multiplication. The normalized opposite obeys `F_s^+ R=R^-1 F_s^+`. This gives

    (R F_s^+)[(R F_s u) pointwise (R F_s v)] = cyclic_convolution(u,v) / S².

Thus both S factors in recovery are required. All three executed calls have the same Gamma. The two digit streams have exact scale `2^(-b-2)`. The real recovery multiplier is

    K = S² * 2^(2b+4+3Gamma).

Every completed factor and the exact padded middle have norm at most one, including all hole positions. For a quarter-disk input a complete transform has error at most `m=(6d+3)h` from `lambda U`. To justify admission throughout, require `K(64d+64)h < 1/2`, exactly the integer test in the controller. It implies m<1/16. At every expansion prefix the radius is less than `1/4+3dh<1/2`, so the middle runs. Throughout the compression it remains below one. The two forward outputs have radius below `lambda/4+m<5/16`. The inward pointwise product has radius below `(5/16)²<1/4`, so the opposite call satisfies the same admission proof.

At the pointwise step the error from the ideal two normalized forward outputs is at most `(lambda/2)m + m² + 2h`. The opposite call gives

    E <= m + lambda*((lambda/2)*m + m² + 2h) < (12d+8)h.

The real coefficient error is at most KE, strictly below `K(64d+64)h<1/2`. Nearest-integer recovery is unique, including when either operand is zero. The true no-wrap requirement is `2 ceil(n/b)-1 <= S`. It gives ordinary convolution, after which the inverse CRT and integer carry scan are exact. This argument does not use an observed product or require a posteriori numerical success.

For `(s,t)=(5,8),(7,8)`, `b=8`, `q=128` and `Gamma=9`, the admitted guard is `235200 * 2^-81 < 2^-63`. With `q=8p0`, `p0=6b`, `S<2^b` and the fine-family bound `Gamma=O(d log p0)=o(p0)`, the logarithm of the guard is at most `4b+3Gamma+O(log d)-8p0`. It tends to minus infinity. The middle uses `q+2log2 M+O(d)` signed bits including its temporary synthetic lift. This is O(p0) from `log M=O(p0)`. Per-axis `g=O(ell+p0^(1/4) log p0)` under the stated gauge and inverse bounds, so its work and backing component widths are also O(p0). A private exact local setup may use more precision. The cost of that setup and the whole-array schedule are separate obligations.
