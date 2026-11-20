# Independent review of the recursive dot and carry proofs

**Pass within the stated interfaces.** The frozen proof establishes the direct-product congruence threshold, the information needed by the correction at a fixed main return, and the dense odd channel width. The finite circuits preserve all read-only ports and erase all scratch. Their signed recursive credit is **zero**.

## Direct residue and residual information

For $m\ge2$, write $x_2=x_1+2^a v$ and $y_2=y_1+2^b z$. The exact integer identity is $x_1y_1+x_2y_2=2AB+2^{a+b-1}vz$, where $A,B$ are the respective integer half-sums. Changing a representative by $2^m$ changes its half-sum by a multiple of $2^{m-1}$. A nonzero correction uses $d=m+1-a-b$ low bits. Since $a,b\ge1$, this width satisfies $d\le m-a$ and $d\le m-b$, so the needed bits of $v,z$ are independent of the chosen representatives. The identity absorbs every separately known integer carry, including negative lifts.

For necessity, set any carry and subtract mixed differences over the four points given by the base input and independent unit changes. The one-sided terms cancel and the differences of any separate nonlinear product factor as an outer product. The target gives entries $2,2^b,2^a,2^{a+b}$ in row order. The invertible row and column eliminations in the proof give $\operatorname{diag}(2,2^{a+b-1})$. Since $m\ge2$, a product congruent to $2$ has exactly one odd factor. Its inverse and the two zero off-diagonals force the other diagonal to be zero. For $a+b\le m$, both increments exist and the second diagonal is nonzero. If either side is congruent at all $m$ bits, the correction vanishes because the other promise contributes at least one bit. At $m=2$, $(a,b)=(1,1)$ fails and $(1,2),(2,1),(2,2)$ attain the direct representation.

Fix both half-sums at zero using opposing pairs, set $z=1$, and vary $v$ through the $2^d$ residues. This fixes the main product and the incoming carry and leaves $2^d$ distinct target outputs. Symmetry gives the same separation for the other side. A decoder seeing the fixed main return and only an extra joint return needs at least $d$ effective bits in that return. A separately conveyed side summary also needs at least $d$ bits per side with the other side fixed. The low $d$-bit residual product attains the return-width bound. These are information bounds for this interface.

Two exact controls make common simplifications fail.

- At $m=2,a=b=1$ the diagonal $\operatorname{diag}(2,2)$ has determinant zero modulo $4$. Exhausting all 256 pairs of two-entry vectors modulo $4$ finds no outer-product factorization.
- With $m=5,a=b=1$, left inputs $(0,0)$ and $(-8,8)$ have the same main return and same three-bit $v$ value. Right inputs $(-1,1)$ and carry zero give outputs $0$ and $16$. A three-bit residual cannot serve this four-bit interface.

The replay checks 1,044,944 congruent pairs of operand pairs at widths 2 through 5 with varied carries, 848 signed lifts through width 1,024, and 156 fixed-main separation families.

## Dense odd channel width for each fixed carry

For $m\ge3$, set $Q=2^{m-1}$, $H=Q/2$, and $k=\lfloor c/2\rfloor$. Putting $y_i=1+2t_i$ makes the high bit the upper-half indicator of $x_1t_1+x_2t_2+b_x+k$ modulo $Q$, with $b_x=(x_1+x_2)/2$. Two equal rows give equal kernels of the surjective linear forms because the half interval has no period. The forms differ by a unit and the resulting affine permutation must preserve the half interval. The overlap size of a half interval and its translate by $s$ is $H-\min(s,Q-s)$ for $0\le s<Q$. The image of the unit shift therefore forces the multiplier to be $+1$ or $-1$.

For the multiplier $-1$, the affine intercept is $b_x+b_{x'}+2k$. Both coordinate sums $x_i+x_i'$ are multiples of $Q$. The putative intercept is even, but interval reflection requires the odd value $H-1$. For multiplier $+1$, equal intercepts require simultaneous top-bit flips or equality of both coordinates. The resulting $2^{2m-3}$ classes are all nonconstant at **each** fixed $c$. The all-zero concatenated code makes a constant row, so at least $2m-2$ coordinates per side are required. Two channels multiplying a canonical row code by one attain the width, counting the hardwired coordinate each side. The canonical representative works for all carries.

The replay enumerates every effective carry shift for $m=3,4,5,6$, plus zero as a separate lift. It finds 8, 32, 128 and 512 row classes, respectively. At $m=3$ and $c=0$, left input $(1,1)$ returns different bits on right inputs $(1,1)$ and $(1,3)$, which exposes a constant zero-code substitution. Left inputs $(1,1)$ and $(3,3)$ also differ at right input $(1,1)$, which exposes an erroneous reflection identification. The lower bound applies to the stated product-only, fixed channel-list interface. The attainment uses unrestricted decoding.

## Boolean and clean reversible invoices

The checker authenticates the frozen files and extracts only the circuit generator from its syntax tree. It independently counts the emitted gates, compiles each XOR into two CNOTs to fresh scratch and each AND into one Toffoli to fresh scratch, copies the outputs, and reverses the individual computation gates. Each case starts with an independently seeded destination and checks the resulting XOR update against direct integer arithmetic. Every scratch bit is checked for zero and all five input words, including the carry, are checked for preservation. Skipping the inverse segment keeps a correct destination on the control case while leaving live scratch. The checker detects both a dropped highest-bit correction and a dropped incoming carry.

| Width | Circuit | AND | XOR | Clean scratch bits | CNOT | Toffoli |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 4 | Two products | 38 | 38 | 76 | 156 | 76 |
| 4 | Shared carry | 21 | 29 | 50 | 120 | 42 |
| 8 | Two products | 170 | 170 | 340 | 688 | 340 |
| 8 | Shared carry | 91 | 107 | 198 | 436 | 182 |

The circuit replay covers all 65,536 admissible 4-bit input-and-carry combinations and 20,480 independently generated 8-bit combinations. Both circuits use the same read-only inputs, output destination, and promised congruences. The gate model permits unrestricted wiring and requires fresh zero scratch. The counts cover the named circuits, with identical power to read the operands and with full cleanup.

## Reconciliation with the pinned applications

The P104 #7830 comparator counts complete paid tuples by literal source occurrence and debits displaced productive fields. It includes adapters, spectators, compiler and stock work. Its rational and binary words retain 48 and 36 native calls respectively. At the current target $0.003884928046155$, computing the two histogram differences $\sum_g(T_g-P_g)g^{1-\kappa}$ at 75-digit precision agrees with the supplied directed enclosures around $-4.88039108995$ and $-1.92561529071$. That numerical cross-check uses the newer target and the frozen histograms. [#7830 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/PROOF.md)

The exact #7834 ring call reads four signed full products of packed operands. It forms the exact real difference and imaginary sum, extracts centered limbs, folds negacyclic halves and only then divides by $r2^f$. Elsewhere, the complex pointwise multiply forms both signed numerators and drops them onto the fixed grid. Forward, opposite, coefficient recovery, inverse CRT and the binary carry scan have their own paid passes and lifetimes. The submitted low-residue circuit supplies neither the full packed return nor the source-specific congruence and pricing at those call sites. The finite circuit changes zero literal paid and productive entries and earns zero signed improvement against #7830. Its local gate savings establish no new numerical $\kappa$. [#7834 product path](https://github.com/CrocSwap/integer-mult-bounds/blob/4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02/research/fine-prime-gaussian-product/product.py) · [#7834 ring implementation](https://github.com/CrocSwap/integer-mult-bounds/blob/4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02/research/fine-prime-gaussian-product/fine_ring.py) · [#7834 fixed-tape invoice](https://github.com/CrocSwap/integer-mult-bounds/blob/4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02/research/fine-prime-gaussian-product/PROOF.md)

The checker uses only the Python standard library and produces identical JSON with normal and optimized execution. It reads `reference-price.json` alongside the checker when present. The `--primary` and `--comparator` options support replay from separate directories.
