# Number of grades, mask instructions and leading digits

For the exact predictor of [AI](foundations/adaptive-interchange.md), take `m>=4096`, the structured shift family, and its smallest power-of-two window `T>=10 ceil(sqrt(m))+1`. Then `D_p=T−1<=m` and `T<=24 sqrt(m)+1`. Write `kT=log2 T` and `m0=2^ceil(log2 m)`. A single unlabelled tree serves every shift: at a base leaf for query `j` its coefficient depends on `beta_j(shift)`. The same compiled token reads that shift when applied. This is allowed because all shifts use the same gate lengths and independent row count.

## Fully copied program

For each retained sum bit use the [binary carry formula](foundations/characteristic-two-count-formula.md). In a balanced sum with two digit-word operands `X,Y`, generate

    carry(0) = 0
    carry(k+1) = X_k*Y_k + (X_k+Y_k)*carry(k)
    bit(k) = (X_k+Y_k)+carry(k).

Every occurrence of `X` and `Y` requests a fresh subtree. Its arguments descend to the two halves of the current sum block. At singleton leaves a shifted digit has bit zero `1_(b=1)`, bit one `1_(b=2)`, and other bits zero. Padding creates zero leaves through `m0`. Add the fixed residue of `−u mod T` at the final level. For example the leaf indicator of `b=(k_j+beta) mod 3` equalling `a` is `1+omega^(beta−a) C_j+omega^(2(beta−a)) C_j²`; at a matching cube root its three unit summands add to one in characteristic two. Use the prescribed sign change for the inverse query. Form

    omega^(u−sum beta) * product_{i<kT}(1+(omega−1)^(2^i)*bit(i)).

The predecessor’s (B5) bounds each **fully unfolded** bit by `512m^5` raw nodes. There are at most `m` bits. A fixed scalar, scale, sum, and product need at most eight wrapper nodes per bit. Each binary node receives at most two explicit padding wrappers for its input length; affine/scalar constants at longer prescribed lengths need one padding wrapper if they have not already been padded. Even taking four times the raw size gives

    S <= 4[(512m^5+8)m+2] <= m^8.

The constructor is a depth-first stack of requests for a balanced-sum bit, a carry, product, scale, leaf or pad, with the child return linking the parent/child, side, arity, phase length and incoming node grade. The carry expansion above emits at least one node per carry or bit invocation; if an operand descriptor points to the next smaller balanced-sum block or an offset leaf, resolve at most two such aliases per emitted edge. Schedule explicit multiplication, addition and phase-zero scalar instructions from the displayed grammar. For each request, computing the dyadic block, degree (`2^i`) and child indices uses at most 128 short-word operations; allow a further 128 per emitted node to annotate grade ID, padding and parent links. Compute `bitlength` by inspecting at most `b` bits. Even using `1024(b+1)` instructions per node and `4S+4` requests the total is at most `m^12` word instructions. A DFS frame and node description need fewer than 64 words. A later token list contains at most `2S` pointers (all leaves and the identity branch of a padding), and an individual path consumes at most `S` pairs. All fit in one [short-word controller](compiler-controller.md). No list of the `w` grade tuples is constructed.

## Row width and root range

Each addition inserts one grade radix `d_g` which is a power of two at most `m`. Products concatenate rows. With `s=sum_g log2 d_g`, the exact number of independent rows per module is `w=2^s`. There are at most `S` grades, hence `s<=m^9`. The integer `s` itself fits a short word. Export the vector of grade widths and `s`; an extent tape can write the literal binary `w` as a one followed by `s` zeros instead of trying to store this huge value in a short word.

The full-bit leading batch uses `B<=7m`, `N<=m^5`, `h_K<=m` and `M_f=16^ceil(log2(m)/4)<=16m`. Therefore

    ell = ceil(log3(h_K M_f N 32 B w)) <= 2m^9 <= m^10.

Indeed `log2(h_K M_f N 32B)<=log2(3584)+8 log2 m` and the sum of that expression, `m^9` and one is at most `2m^9`. The actual rounded value, batch padding and the associated data moves are computed by the native extent/packing program.

## One coefficient on a real module row

Use the [single-factor recurrence](foundations/succinct-factor.md). For one token walk parent pointers to the root, recording the side on a stack, and then traverse the path down. At an addition with actual input grade `i` and local phase `t`, the left branch records an increment of that grade and sets `t=i`; the right branch sets `t=(t−i) mod d_g`. A product permits precisely its active concatenated interval and subtracts the length preceding that interval. A pad accepts its child before the true length and its identity token afterward. A scale acts only in phase zero. A terminal affine leaf contributes its chosen constant/query coefficient and the accumulated small-field scaling. Each iteration needs two or fewer short table loads for child/parent indices, some further grade, length and coefficient loads, bounded additions/comparisons and a scalar multiplication. Allow 128 instructions per step on each walk, and `64(S+1)` for initializing grade/token records, the leaf coefficient and traversal controls. Products in the extension use the charged lookup of [the spectral controller](compiler-spectral.md). Total at most `384(S+1)<m^10` word instructions, hence **at most `m^48` physical transitions per coefficient on a scalar**. The bound permits recomputation at each scalar; no huge table for all input-row grades or physical addresses is built. Grade digits are read from a local `S`-word odometer. Advancing across a complete grade tuple costs at most `64(S+1)` word operations even when every grade wraps. The unbounded physical suffix ends are detected by the separately priced run scanner.

An increment of a grade of radix `d_g` can use `d_g<=m` selected-role copies, moving each value slice `i` to `(i+1) mod d_g` into a fresh accumulator bank. Arbitrary higher-grade prefixes and complete lower-grade/data ranges retain their orders. Each terminal token requests at most `S` such increments, all performed after masking the original input grades. There are no recursive spatial calls in these internal grade moves. Algebraic identities for the masked token sum and the whole cyclic factor remain those of B1; the new result supplies numerical bounds at their existing cost entries.
