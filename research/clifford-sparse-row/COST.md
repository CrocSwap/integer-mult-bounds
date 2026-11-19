# Cost of one width-13 Bell observation

This is the cost of the coset-sum reader in Section 2 of [PR #7799](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md). Its input in this model is an arbitrary dense matrix `Y` of normalized width-13 observations in computational coordinates. Each row and column has thirteen four-bit indices. A coordinate probe returns one exact complex entry. Transporters, Bell labels and phases are fixed in advance. The four-qubit Clifford image is a restricted subspace of this domain.

## One block and one trace

For an ordered input tuple write its six Weyl labels as `(x_j,z_j)`. Use primes for the output tuple. The Bell vector for one label has amplitude `(-1)^(z·r)/4` on the ordered pair `(r xor x,r)` for each nibble `r`. For six nibbles `r`, let `R(r,a)` concatenate the six pairs `(r_j xor x'_j,r_j)` followed by the singleton row `a`. Define `C(s,b)` the same way using the input shifts. Before the singleton Weyl corrections the block is

```text
B[a,b] = 4 sum_(r,s) (-1)^(sum_j z'_j·r_j + z_j·s_j) Y[R(r,a), C(s,b)].
```

There are twelve independent nibbles. The scalar is `4^13 / 4^12 = 4` from undoing the column normalization and applying twelve normalized Bell vectors. The corrections permute and sign the sixteen singleton row and column indices. The transport phase rotates the result by a known Gaussian unit.

For the identity Clifford coefficient, the subsequent scalar is the trace of the corrected block divided by 16. If `w,w'` are the input/output label sums and `x(w),x(w')` their X parts, the original singleton entries required by the diagonal satisfy `b = a xor x(w') xor x(w)`. Each of these sixteen entries has a known sign. Thus the coefficient of every retained coordinate in this scalar is a Gaussian unit times `1/4`.

| Requested output from one block | Distinct input entries | Binary signed complex combines |
|---|---:|---:|
| One singleton entry | 2⁴⁸ | 2⁴⁸ − 1 |
| All 256 singleton entries | 2⁵⁶ | 2⁵⁶ − 256 |
| One normalized identity trace | 2⁵² | 2⁵² − 1 |

Each count is attained by visiting the indicated coordinates and reducing their signed values. Copies, fixed signs, Gaussian-unit rotations and powers-of-two scalings are separate from binary combines. The coordinates are distinct because the second nibble of every pair recovers its free index. Different singleton addresses give disjoint sets. On zero input, perturbing an unread required entry would change at least one answer. Hence even an adaptive exact reader must probe every listed entry in the worst case. In a linear circuit with binary addition/subtraction and unary scaling, every required input has a path to an output. A binary gate can merge at most two connected components, and every component remaining on those paths contains an output. The circuit needs at least the number of required inputs minus the number of outputs in binary gates.

## The complete compiled identity row

The compiler fixes one realization of each block on arbitrary observations. Combining its 4,265 weighted traces gives a sharper bill for this specific output. Group terms by the twelve four-bit X shifts of their Bell labels, six on the output followed by six on the input. These shifts are read directly from a raw coordinate by XORing its adjacent pairs. Thus different groups read disjoint coordinates. In all 22 groups the singleton X corrections agree on both sides and the trace uses a common singleton nibble `a=b`. The emitted transport phase is one on this identity row.

Within a group the free coordinates are the 52 bits of `v=(r_1,...,r_6,s_1,...,s_6,a)`. A term with signed integer block numerator `n` contributes the raw weight

```text
(n/4096) (-1)^(frequency · v).
```

The first twelve frequency nibbles are the Z parts of the output and input labels in that order. The last nibble is `z(w') xor z(w)` from the trace. In fact `W_w^-1 W_(w')` is exactly this diagonal Z when the X parts agree. The denominator is the block denominator 1,024 multiplied by the four in the single-trace formula above.

For each group, binary elimination expresses its frequencies in a basis of rank `r ≤ 10`. Evaluate their weighted Walsh sum at every assignment of the `r` independent parity bits. Every assignment occurs exactly `2^(52-r)` times among the raw coordinates. Exhausting **10,530** assignments across the 22 groups therefore covers the full sum, including cancellations. This produces the following multiplicities in the normalized identity row.

| Raw weight | Multiplicity |
|---|---:|
| +1/32 | 10,133,099,161,583,616 |
| −1/32 | 10,133,099,161,583,616 |
| +1/8 | 492,581,209,243,648 |
| −1/8 | 492,581,209,243,648 |
| Zero inside the 22 groups | 77,827,831,060,496,384 |

Every coordinate outside the groups is zero as well. Hence the input-query cost on arbitrary dense observations is exactly **151 × 2⁴⁷ = 21,251,360,741,654,528**. On zero input a single unseen nonzero-weight coordinate could change the answer. Conversely, the compiler solves the parity equations at each nonzero assignment. Its streaming iterator visits every point of the resulting affine set by flipping one free bit at a time in reflected Gray order. Distinct groups and distinct assignments have disjoint supports. This supplies the matching schedule and a separate indexed lookup without storing or traversing the full support. The program verifies boundary addresses and the equality of the squared weights to `2^45`.

With arbitrary unary scales and signs, the exact binary-combine count is the number of probes minus one. The connected-component argument above gives the lower bound. Summing the two signed magnitude classes and combining the subtotals attains it. If all real and imaginary input numerators have magnitude at most H on grid `2^-p`, one can use grid `2^(-p-5)` throughout the accumulator. The absolute numerator bound per component is `(144+4·7)2^47 H = 43·2^49 H`. On arbitrary signed data it can be attained by matching the row signs.

For the row-major record tape below, the extremal active addresses are hexadecimal `00000000000210000000000021` and `fffffffffffdefffffffffffde`. To certify them, map one affine cell's origin and free binary directions to their 104-bit addresses. Echelon reduction of the directions, followed by clearing or setting attainable leading bits in descending order, gives the exact minimum and maximum in that cell. Taking extrema over all active cells proves the two addresses. Starting and returning at record zero costs exactly twice the maximum in input-head movement. An ordered scan attains the movement bound, while the Gray iterator attains the query count. An ordered scan can also restrict its arithmetic probes by the coefficient lookup. None of these counts pays for producing the dense tape or moving its arithmetic workspace.

## Precision, movement and cleanup

For input real and imaginary numerators in `[-H,H]` on a common grid `2^-p`, unscaled entry accumulators need magnitude at most `2^48 H`. Multiplying the result by four can shift the shared exponent, or increase the bound to `2^50 H` on the original grid. A direct trace accumulator needs magnitude at most `2^52 H` on its numerator and can return it on grid `2^(-p-2)`. For a bound `M`, a signed register of `1 + ceil(log2(M+1))` bits suffices. No rounding is required.

On a row-major dense tape with one fixed-size record per entry, start the read-only head at record zero and require its return. The minimum required address `m` for the full block has nibbles `(0,x'_1,...,0,x'_6,0,0,x_1,...,0,x_6,0)`, with each zero/shift pair ordered as in the formula. For the trace replace the final zero by `x(w') xor x(w)`. Complementing every nibble preserves all pair constraints and the trace constraint, so the maximum required address is `M = 2^104 - 1 - m`. Every exact algorithm on this tape makes at least `2M` input-head moves on zero input. One ordered forward scan to `M` followed by the return attains this count. The scan can generate the selected addresses in order by enumerating the first nibble of each pair and deriving the second by XOR. It reads values into the arithmetic only at selected addresses. Traversed intermediate records still count toward movement.

The forward pass needs up to 256 complex sums for the block or one for the trace, plus fixed-width address and loop counters. With write-once final output and all mutable storage charged, a one-pass block reader also has a working-state lower bound. At the cut where the highest row bit first becomes one, exactly half of each singleton sum's terms have occurred. Varying the prefix on its disjoint supports gives `(2^48 H+1)^512` distinct vectors of partial real and imaginary sums. The common zero suffix preserves all these distinctions at output. This requires at least `ceil(512 log2(2^48 H+1))` live bits at the cut for integer `H >= 1`.

The head count is in record units and excludes arithmetic-workspace movement. An ordinary reader can emit the scaled sums and clear its accumulators. A reversible implementation may copy the result to clean output and undo the accumulations on the return sweep, which adds a second probe of each selected entry. Bit-serial arithmetic, physical preparation of the observations and a complete multiplier invoice require additional accounting.

Different transported blocks can reuse input coordinates. The single-block lower bounds do not add across the decoder. They also do not apply directly to a compact word or a promised Clifford expansion. For example, the repository already computes phase-sensitive contractions from compact affine supports. Connecting such a producer to the decoder requires an explicit input contract. [Compact contractions](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/clifford-exact-contractions/README.md)

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
