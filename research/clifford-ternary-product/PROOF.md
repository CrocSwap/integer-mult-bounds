# Clifford observations for integer multiplication

The input is two ordinary binary words in low-to-high order. Their declared lengths can differ and can include high zero bits. The output is the canonical ordinary binary product. Define n as the larger declared length, or one for two empty words. Choose the least m with N = 3^m ≥ n. Thus n ≤ N < 3n for n > 1. Put d(x) = Σ xᵢ 3ⁱ for x in the binary m-cube. The choice depends only on length.

## Recover unknown Clifford operators from bits

On the positive sparse branch a digit can be one only at address d(x). The one at that address has indicator a(x) = 1_L(x) q(x), where L is an unknown affine binary subspace and q is an unknown Boolean polynomial of degree at most two on L. Each operand has its own L and q. The empty support is permitted. A signed dense extension and independent charts on many fibres are described below. These are testable conditions on literal integers.

Scan all raw cells. The producer infers the affine hull of the occupied sites. Every original polynomial restricts to that hull. On an affine coordinate basis, its values at zero, every singleton and every pair determine every coefficient. The producer fits these values and then checks all sites and holes. Thus a successful fit certifies equality of the entire input. A failure excludes this representation, including a possible larger original support. The zero operand has empty character support by convention. [Recognition proof and physical scans](IO.md) · [Source](operand.py)

On the inferred coordinates the recovered sign operator maps |z⟩ to (−1)^q(z)|z⟩. Its linear and mixed terms give Z and controlled-Z gates. The mixed terms are arbitrary. The constant gives the absolute sign. Affine placement uses binary linear coordinates and translations. Each character is an unnormalised real stabilizer state. In particular, this producer recovers unknown Clifford phase labels and their support from data. The cost of fitting one complete table is O(2^m poly(m)) after the O(N) input scan. Both fit and verification are included. No supplied probe, Clifford description or tensor train is needed.

Write U = 1_L and V = 1_L(−1)^q. Then 2a = U−V. Use that identity on both operands. It gives four signed joint charts whose sum is four times the raw pair table Y(x,y)=a(x)b(y). No dyadic amplitude normalisation is implicit.

## The readout that an integer product needs

The ordinary coefficient at bit position j is the sum of a(x)b(y) over d(x)+d(y)=j. Each local address sum is 0, 1 or 2, so its digits do not carry in radix three. For the output trit t, the allowed local pair is 00, the two pairs 01 and 10, or 11, respectively. These real bras are |00⟩*, ⟨01|+⟨10| and ⟨11|. The middle Bell bra has amplitude one on each orientation. Replacing it by a normalized Bell bra introduces a factor √2 at every mixed site.

There is an exact Clifford coefficient interpretation. Treat Y as a real matrix with one row and one column bit per site. At a site the readout matrices are M₀=(I+Z)/2, M₁=X and M₂=(I−Z)/2. Here I,X,Z are pairwise trace-orthogonal Clifford matrices of squared norm two. In their tensor product span the canonical coefficient of word W is α_W = 2^(−m) tr(WᵀY). Local antisymmetric directions are invisible to the requested product. The raw coefficient at trit word t is

    2^(number of ones in t) · Σ_W (−1)^(number of positions with tᵢ=2 and Wᵢ=Z) α_W,

where Wᵢ=X exactly at positions with tᵢ=1. This follows from the three one-site trace pairings and tensor multiplication. Conversely, each permitted Pauli word is constant on every trit fibre. Thus its trace is determined by the fibre sums. The two transcripts determine each other on integer tables, including off-span data. The joint point masses at (00,11) and (01,10) have identical trit observations, while Y⊗Y has values −1 and +1. The algorithm fuses the exact tensor-I/X/Z adjoint and its coordinate conversion by contracting M directly. The operators recovered from an operand can contain entangling controlled-Z gates at arbitrary pairs. The computation uses all the resulting interference signs. [Formal equivalence](lean/PauliEquivalence.lean) · [Independent literal Pauli decoding](check_sectors.py)

For one signed chart keep an affine equation system E(z)=0 and a quadratic phase Q(z). Its represented amplitude is (−1)^Q on the solutions and zero elsewhere. At each node decode the three observations on the most significant remaining pair x,y.

- At trit zero or two set x=y to the specified constant. Substitute it into E and Q.
- At trit one set y=1+x. If a row now contains x it uniquely determines x as an affine form of the remaining variables. Substitute that form.
- Otherwise, write Q=Q₀+x l with l affine. Summing over x gives 2·1_{l=0}(−1)^Q₀ on the other equations. Append the equation l=0 and advance the scale by one bit. An inconsistent system yields the zero chart.

At each child, eliminate dependent rows over the binary field and detect 1=0. Substitution in a quadratic only multiplies an affine form by a term of degree at most one. Repeated variables satisfy z²=z. Thus every nonzero child is another exact chart with at most 2j independent rows and O(j²) phase terms on j remaining pairs. The cost per child is bounded by a fixed polynomial in j+1 on sequential binary tapes. The integer bit masks in the finite implementation have O(j+1) bits. A fixed tape can substitute by scanning or sorting the polynomial-size lists, including duplicate cancellation and row reduction. A global m-bit row or coefficient is never copied at a one-pair leaf. [Local implementation](contraction.py) · [Exhaustive projection controls](check_contraction.py)

Induction gives the unnormalised chart times 2^e at every node, where e counts its retained doublings. At a leaf the amplitude is zero or ±2^e, with e≤m. The four passes have independent support, signs and exponents. Cancellation can be exact. The input and every operation have integer or binary-field semantics. There is zero rounding error.

## Deposit the answer at its physical bit

Traverse the children in ascending trit order. When a descent increases e, move the output head one bit right. Undo the move after the subtree. Visit every leaf, including zero leaves. Deposit one signed bit at the current head for a nonzero leaf, then advance one bit. Immediately before the deposit the head is at j+e. The proof is induction on the depth-first traversal. Each completed leaf advances the underlying j by one and each active shift contributes one to the head displacement. There are N leaves and fewer than 3N/2 edges per pass. All exponent movement, including its return, costs O(N). A single loop interprets a local stack. An event does not traverse a chain of Python generators or tape frames.

Use separate positive and negative integer tracks. Add each unit at the current bit, propagate a binary carry and return to a local mark. Each emission sets one zero to one. Each ripple step clears one earlier one. The total ripple is at most the total number of emissions for every visit order. After four passes subtract the two unsigned tracks and drop two verified zero bits. This yields the exact nonnegative product by the character identity. Every private track is owned and either erased on exit or recycled with a full extent sweep. Input words are read-only and have their origin marks restored. The maximum signed-sum extent is N+m+O(1) bits since each of four streams contributes at most Σ_{j<N}2^(j+m). No coefficient array with m bits at each address is created. [Delivery and movement](IO.md) · [Consumer](delivery.py)

The full work of a pass, including copying each parent chart and releasing the child, is bounded by

    Σ_{j=0}^m 3^(m−j) poly(j+1) = O(3^m).

The sum of the chart frames on one active path is poly(m). A fixed number of linear bit arenas and the raw or compact input copies use O(n) backing. The control program consists of the fixed binary row, substitution, traversal and counter routines. It requires no size-indexed table or external compiler.

## Dense words with independent growing periods

Set u=2^floor(m/2), K=max(1,floor(n/u)), and G=Σ_{j<K}2^(ju). Each operand may use an ordinary sparse chart with P=0, e=0, s=1, or a dense form

    A = P G + s 2^u F,    0 ≤ P < 2^u,    s ∈ {−1,+1}.

F is a nonnegative represented defect. Recover P from the low u literal bits. Generate P G by copying the word K times, subtract it from A, extract the sign, verify the low u zeros and fit the complete magnitude above them. The sign is positive for zero. Borrow and carry in the original binary word can cross any number of cells. Subtraction and absolute comparison are full linear scans. The two operands can choose different signs, periods and modes. For either mode write e for its actual shift. Compute

    A B = PₐPᵦ G²
        + sₐ 2^eₐ (FₐPᵦ) G + sᵦ 2^eᵦ (FᵦPₐ) G
        + sₐsᵦ 2^(eₐ+eᵦ) FₐFᵦ.

Each sparse defect has at most 2^m one bits. Multiply it by a u-bit period by a forward sparse scan. Add the short word at each occupied bit and return to the mark. The inner u cells can create at most u new ones per visit. Longer final ripples erase ones and cost O(u·2^m) over the whole scan, including their return. Repeat scans cost O(n+2^m u)=O(n) since 2√2<3. The short pair can use the same addition routine at cost O(u²)=O(2^m).

To multiply a binary stream by G, use consecutive base-2^u limbs. Keep the sum of the last K limbs in a window and the incoming carry. Two sequential read heads on private copies supply the entering and leaving limbs. Given limb sum S, write the low u bits of S+carry and keep its quotient by 2^u. Pad the input by K−1 zero limbs and emit the last carry. Each quantity has O(u+log(K+1)) bits. There are O(n/u+1) limbs in each of a fixed number of passes. Since m=O(u) and log(K+1)=O(m+1), they cost O(n). Conversion packs and unpacks groups of eight literal bits in scan order. Signed final addition and removal of high zeroes cost O(n), including the shift prefixes. The three multiplication terms and their temporary backing have O(n) total peak size. [Template producer, windows and consumer](templates.py)

For every large m take n=u floor(3^m/u). Choose two u-bit periods independently, with high bit one and both digits represented in a fixed positive fraction of cells. Their repetitions are dense. A defect ends near N/2 and any remaining carry or borrow stops within the next full period. Thus both unpadded input words have length n and contain Θ(n) zeros and ones. There are exponentially many independent period choices in u, in addition to the independent graphs. The class includes arbitrarily large dense canonical integers.

## Multiple independent Clifford labels in one multiplication

For h high control bits partition each positive defect into 2^h high binary prefixes. On each prefix allow its own unknown affine support and quadratic on the remaining k=m−h bits. Prefixes with a ternary hole must be all zero. This admits arbitrary changes of graph, support, rank, and sign convention between fibres. For example a(x,c)=x₀ XOR (c x₁ x₂), with high bit c, has degree three. Its nonzero points have full affine hull. An affine equation that omits x₀ must hold on all choices of the other bits. An equation that includes x₀ would make c x₁ x₂ affine. Thus a single chart cannot reproduce this operand. Each high fibre has a quadratic label. Independent high fibres can have independent cross-term graphs.

Write S=3^k. Blocks at high ternary address d(x) start at physical bit S d(x). The producer verifies all 3^h raw blocks in one ordered scan and fits all 2^h possible data blocks. Its work is O(N+2^h 3^k)=O(N). Empty fibres work on the same branch. In the consumer process each high trit word t in order. Enumerate exactly the high binary pairs whose sum is t, retaining both orientations at every mixed trit. Compute their low products by the complete four-pass decoder above. Add each to that block and the incoming ordinary base-2^S carry. Append its low S bits and carry the remaining high bits to the next block. Finish by appending and trimming the final carry. Every pair belongs to exactly one block by d(x)+d(y)=d(t), now with d(t)=Σtᵢ3ⁱ. This is ordinary integer multiplication in base 2^S. [Sector producer and consumer](sectors.py)

There are exactly 4^h low products over the *entire* run. Each low product is less than 2^(S+1), and any block has at most 2^h pairs. Hence the incoming carry stays below 4·2^h by induction and each block addition costs O(S+h+1) bits. Process one low product at a time and reset its bounded arenas before reuse. The output head advances through all N low block bits once. Store the chart catalogues in O(2^h poly(m)) bits. Access to a selected chart can use a linear scan of each catalogue per pair.

For every 0≤h≤m/2 the catalogue selection for one pair costs O(2^h poly(m))=O(3^k), since h≤k and m≤2k. The block work sums to O(4^h 3^k)=O(N(4/3)^h). The total backing is O(N). The recognizer and sector consumer accept this full range. The controller first tests a single chart per operand. If that fails it takes h=min(floor(m/2),floor(log₂(s²))) where s=max(1, bitlength(m)). This choice admits Θ((log(m+2))²) independently chosen charts per operand for large m. Its time is O(n(log(m+2))^(2 log₂(4/3))). The exponent 2 log₂(4/3) is less than one. All global and sector fits together cost O(n) even on a rejection. The size choice and small cases use integer arithmetic. [Public controller](multiply.py)

## All other inputs and the baseline

If neither full representation certifies, call the pinned complete direct Fourier implementation with the same input length. Its controller computes the production widths, square geometry and precision or uses its finite Karatsuba base. The seven unchanged executable modules and two source notices are included with hashes. The calling adapter passes the correct root for the existing rational compiler and CRT router. Zero, leading zeros, length zero, signs on the integer entry point, short words and arbitrary rejected pairs are covered. The recognition and return overhead adds O(n) time and space on rejection. On every accepted input the decoder, template operations and bit delivery above supply the entire product. [Source bindings](vendor/PINS.json) · [Complete Fourier program](vendor/direct-fourier/product.py) · [Full predecessor proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd/research/direct-circulant-fourier/COMPOSITE-OUTER.md)

The fixed-tape interpretation of that fallback inherits its published proposal of O(n(log n)^(1−0.00387992803556)) time and O(n) space, including the mixed-rank native Hadamard and BIT suppliers. The Python fallback's elementary Hadamard simulates its numerical map. The supplier price is a written fixed-tape theorem. The Clifford branches use no native supplier, floating-point arithmetic or number-theoretic oracle. The known worst-case bound remains the fallback's. The stated family comparison uses compulsory traversals of the pinned schedules and explicit intermediate output sizes. [Full cost comparisons](COMPARISONS.md)
