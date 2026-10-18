# A dirty source for the arbitrary-stride closure

## Contract and limits

Let `Z_L^w x` have entry `x_((i-w) mod L)`. Let `0 < beta <= 1/2`,
`|b| <= 1-beta`, and `u=2^-W`. The source `x` and target `y` are distinct
length-`L` arrays on the complex dyadic grid of spacing `u`. They can contain
arbitrary data. The coefficient `b` is one immutable rational complex number. Reduce the
stride modulo `L`. The bounds below use a residue with `O(log L)` bits;
reading an oversized stride descriptor is additional input work.

The function `lift` adds an approximation to

    m (I-b Z_L^w)^-1 x

to a cyclic shift of `y`. It restores `x` exactly. It needs no other data
array, no reserved zero bits, and only a constant number of clean complex
arithmetic registers. The recursion keeps integer indices and array views.
It does not keep a clean array of coefficients or closure values.

Reversible block swaps implement the data operations on two sequential
tapes. No blank data array or coefficient table is used. The source and
target occupy one tape each during a leaf. The complete kernel routes its
borrowed arrays over the same two tapes, with all movement charged below.
The optional output shift is zero or the leaf stride; these are the two
cases required by the kernel factors. The construction does not implement
the variable-coefficient case of PR846's Theorem 1.

Let `K` be the number of non-base Euclidean levels. Assume

    48 (K+1) u <= beta^3.

If `|x_i| <= B`, the unscaled target increment differs from the inverse by
at most

    64 (B+1) u / beta^5.

A multiplier of modulus at most `M`, with `M>=1`, changes this bound to

    (64 M (B+1) / beta^5 + 3) u.

The rounded increment can depend on the target's initial value within this
error bound. A negative call executes the exact inverse word. It restores
the completed positive call, including all source and target data.

## Source reuse

As in Rohan Guliani's PR846, normalize the stride and reverse the index views
when necessary. Then `0 < w <= L/2`. Split the source into chains with
indices `c, c+w, c+2w, ...`. Apply the causal integer lifts

    x_i += rnd(a_i x_(i-w)),  i=w,...,L-1.

Call the resulting source `z`. Each lift has an exact inverse on the grid:
subtract the same rounded product in reverse order. Add `z` to the target
before using any source entries as temporary storage.

The last `w` source entries contain the closure right-hand side. The first
`w` source entries are disjoint from that tail. Use this prefix as a dirty
target for the recursive closure. It contains arbitrary values; it is not
cleared. Let `F` be the completed rounded closure call. Let `H` be the
linear chain expansion. A reversible rounded conjugation implements the
additive `H` call, as specified below.
Execute

    F(tail, prefix)
    H_add(prefix, y)
    F_inverse(tail, prefix)
    H_add_inverse(prefix, y)

Then undo the original causal lifts. There are two recursive calls.

The recursive call restores its input tail. The expansion preserves the
whole source, including the changed prefix and the tail. Thus `F_inverse`
sees precisely the state left by `F` and restores the prefix exactly.
Target independence and rounded linearity are not required. The two
expansion errors are charged separately. At every depth the prefix and
tail are disjoint because `2w <= L`. This proves restoration by induction.

The negative leaf reverses the complete middle word: first the positive
expansion, then `F`, then the inverse expansion, then `F_inverse`, then the
negative baseline addition. It is not the positive word with all signs
changed in place.

In exact arithmetic the source lifts give the chain decomposition
`S x = z + H S_child z_tail`. The four instructions above add precisely the
second term. This is the usual dirty commutator, with its connector taken
from the source prefix. PR628 supplies the dirty commutator and exact grid
lift methods; PR846 supplies the chain/closure decomposition.

## Reversible transport on two dirty tapes

Write `C` for the causal map whose non-start coefficient is `a`. Split the
source and carrier views into consecutive blocks of at most `w` records.
The carrier has arbitrary contents. For each block in forward order:

1. For each position after the first block, add the rounded product of `a`
   and the preceding block's value on the carrier tape to the source.
2. Swap this whole source block with its corresponding carrier block.

At this point the source tape holds the original carrier, and the carrier
tape holds `C_round(source)`. Swap the two complete views. The causal map
has been applied, and the carrier has been restored exactly. Each block
scan and each rewind costs its block length. There is no length-`w` clean
queue. The old carrier data remains in the other tape throughout.

For the inverse, first swap the complete views. Visit the blocks in reverse
order. Swap the current block back, then subtract its rounded predecessor
products. The predecessor block is still on the carrier tape. Reverse the
order within each block as well. This is the exact inverse grid word.
Each map costs at most `64n` data-record moves on views of length `n`,
including read/write charges, block rewinds and full-view swaps. This loose
bound also covers a cyclic view that crosses the root tape boundary once.

An expansion uses this causal map on the **target**, with the source as
its dirty carrier. Apply `C_round_inverse` to the target, add
`rnd(m*b_start*prefix_i)` to its first `w` entries, then apply `C_round`.
The source is restored by each transport pass and is unchanged at the
injection. The negative expansion changes only the injection sign. It is
the exact inverse of the positive expansion.

The closure source and its dirty prefix initially lie on the same tape.
Swap the source prefix with the first `w` records of the other tape. Run
the child on the source tail and this moved prefix, then swap back. The
outer target's displaced data is never read by the child and is restored
exactly. Both child views are now on distinct tapes. Their physical spans
are contiguous. At the root an output shift of zero or the leaf stride
ensures that the moved prefix does not cross the tape boundary. All later
views are reversals or subintervals of these contiguous views.

## Two coefficients per level

No length-dependent clean coefficient table is required. Put

    g = gcd(L0,w0),  M = L0/g,  v = (w0/g)^-1 modulo M.

For `M=1`, all cycles have length one and no modular inverse is required.
At a recursive level the remaining original indices form an interval,
with orientation `s` equal to `+1` or `-1`. Its length and stride are `n,d`.
The displacement to a predecessor is `s*d` when `i>=d`, and `s*(d-n)`
otherwise. The number of original edges is the unique integer in `[1,M]`
congruent to

    (displacement/g) v modulo M.

The induced edge stops at the first remaining vertex. It cannot complete
an extra original cycle first. Thus these residues are the actual return
times, not only congruence classes. At a base level each vertex has returned
to itself, so its exponent is `M`. There are only two possible coefficients
per level, both powers of the original `b`.

The checker independently forms each new exponent by summing the old chain
exponents. It compares all resulting entries with this modular formula.
That finite comparison supports the all-length argument above.

The implementation recomputes these two powers before each pass. Scalar
temporaries are held only inside `causal`, `expand`, and `diagonal`; they
are discarded before a recursive call. The recursion retains only views,
integer metadata, and references to the immutable root descriptor.

## Rounded coefficient preparation

`power` uses binary powering from the most significant bit. After each
product it truncates both components toward zero. A truncation has complex
error at most `2u` and cannot increase the norm. Hence the value prepared
for exponent `e` has norm at most `q^e`, where `q=|b|`.

Expand the repeated squaring into a binary multiplication tree with `e`
leaves. A local error propagates through sibling products whose combined
norm is at most `q^(e-t)`, where that node contains `t` leaves. At most two
nodes have more than `floor(e/2)` leaves. All other internal nodes have at
least `ceil(e/2)` leaves outside them. Therefore the error is at most

    2u [2 + e q^ceil(e/2)] <= 2u [2 + 2/beta] <= 8u/beta.

Here `k q^k <= sum_(j=0)^(k-1) q^j <= 1/beta`. Exponents one and two
satisfy the same bound directly. The tree counts repeated operands with
their multiplicity; reuse of a scalar result does not remove its error.

Let a chain contain `t` prepared coefficients. Each coefficient and its
exact counterpart has norm at most `q`. A telescoping product comparison
gives error at most

    (8u/beta) t q^(t-1) <= 8u/beta^2.

Compare this chain product `pi` with the freshly prepared child coefficient.
They approximate the same original power. Their difference is at most

    eta = 12u/beta^2,

since `8u/beta^2 + 8u/beta <= 12u/beta^2`. Every prepared coefficient has
margin at least `beta`. These statements include complex coefficients.

## Error recurrence

Consider the exact solution of the system with the prepared coefficients
at each level. Suppose its right-hand side satisfies

    |x_i| <= A (1-|a_i|).

The shared-suffix identity used by Charles Bethin in PR764 bounds the exact
zero-seed chain value by `A(1-|pi|)`. The rounded causal pass adds at most
`u/beta`. Because the child coefficient differs from `pi` by at most `eta`,
the next weighted bound is

    A_next <= (1 + 12u/beta^3) A + u/beta^2.

Start with `A0=B/beta`. The admission condition gives
`K*12u/beta^3 <= 1/4`. Thus `(1+12u/beta^3)^K < 2`, and at every level

    A <= Astar = 2(B/beta+1).

The inverse of a system with coefficients of modulus at most `1-beta`
has infinity norm at most `1/beta`. Its stronger weighted estimate is:
if `|v_i| <= C(1-|a_i|)`, its solution has norm at most `C`. Both follow
from the absolutely convergent Neumann series and telescoping weights.

Compare the exact child solution with the exact Schur solution. Their
right-hand sides differ by at most `u/beta`, and their coefficients differ
by at most `eta`. The Schur solution is a restriction of the parent solution
and has norm at most `Astar`. Their solution difference is at most

    Dstar = u/beta^2 + 12 Astar u/beta^3.

The rounded inverse causal map differs from `C^-1` by at most `u` per
entry: each non-start entry subtracts one rounded product. The forward map
differs from `C` by at most `u/beta`. The seed injection adds at most `u`
error. Since `||C||<=1/beta`, the conjugated expansion differs from its
linear additive map by at most `3u/beta`, independently of both dirty
arrays. There are two expansions. The source pass contributes another
`u/beta`. Each chain prefix contains at
least one coefficient, so it contracts a child error by at most `1-beta`.
For the unscaled leaf error,

    e_k <= (1-beta) e_(k+1) + Dstar + 7u/beta,
    e_K <= u.

Summing the geometric series gives

    e_0 <= u + u/beta^3 + 12 Astar u/beta^4 + 7u/beta^2
        <= 64(B+1)u/beta^5.

The root multiplier scales the baseline and each seed injection. The
injection rounding was already charged above. The baseline adds at most
one further `u`; a diagonal root adds at most one. Taking `M>=1` gives the
stated conservative bound with an additional `3u` allowance.

## Complete arithmetic and storage recurrence

Let `n_k` be the level lengths after orientation changes. Then

    n_k >= 2 n_(k+1) + n_(k+2).

Indeed the next length is the normalized remainder, which is at most the
ordinary Euclidean remainder. Let `S(n,d)` be the sum of lengths over the
full binary recursion tree. It satisfies

    S(n,0)=n,
    S(n,d)=n+2 S(d,(-n) mod d) <= 5n+2d <= 6n.

The potential `5n+2d` proves the inequality directly using
`n>=2d+d_next`. Each non-base visit pays for six complete causal maps,
two seed injections, the baseline output, four closure transport swaps,
and both complete children. Each base visit pays for all divisions and
target additions. Validation scans and final head returns are also paid.
Reversal and slicing create index views; their physical accesses still pay
for every movement.

Each visit prepares at most sixteen powers, each with `O(log M)` products.
This cost is also `O(L)`, although the constant is not optimized. From
`n_k>=5n_(k+2)`, a tree of depth `K` has `O(2^K)` nodes and
`2^K=O(L^log_5(4))`. Since `log_5(4)<1`,
`2^K log L=O(L)`. The Euclidean and modular-inverse setup uses integer
arithmetic on `O(log L)` bits. The implementation retains `O(log L)`
integer metadata words, or `O(log^2 L)` bits, with no data-sized values
on the recursion stack. Index arithmetic can be charged conservatively
with sequential counter updates. A block counter costs `O(w)` bit changes
over a block, including its `O(log(w+1))` reset. Integer setup costs
`O(log^3 L)` per visit, using a conservative schoolbook division bound.
The bound on `2^K` also gives `2^K log^3 L=O(L)`, so the total control cost
is `O(L)` bit operations in
the stated tape implementation. The rational reference uses Python
indices; it is not a timing implementation of this control bound.

An explicit loose count is at most `1280L` scalar products and divisions,
including power preparation and a root multiplier. To see this, let `J`
be the number of tree visits. The direct count is at most
`9S + 32J bit_length(M) + 3L`. Since `4^8 <= 5^7`, the depth bound gives
`J <= 4 L^(7/8)`. Also `log2 L <= 8 L^(1/8)` for `L>=1`. It follows that
`J bit_length(M) <= 36L`, which proves the stated count. Mutable data
accesses are at most `71S+2L < 512L`, including both validation scans.
These constants are arithmetic bounds, not measured runtime claims.

Thus one leaf uses `O(L)` rounded scalar operations, two data arrays, and
`O(1)` clean arithmetic registers, apart from scalar arithmetic workspace.
If both incoming arrays have norm at most `D`, internal values have
magnitude bounded by a polynomial in `(D+1)/beta`, independent of `L`.
The weighted bound gives `H=3(D+1)/beta` for causal source values at every
level. Under `a*u<=1` below, a completed child changes a prefix of this
size by at most `H/beta+(H+1)/2`. Thus the changed seed has norm at most
`10(D+1)/beta^2`. Each expansion target adds at most `M` times that seed
norm plus `3u/beta`. Inside its causal conjugation, the inverse pass has
norm at most twice its input plus `u`; the injection adds its seed term;
the forward pass divides this combined bound by at most `beta` and adds
`u/beta`. Apply these inequalities to both expansion calls and the baseline.
The loose bound `512(M+1)(D+1)/beta^7` covers every intermediate value,
including the displaced carrier data. At each recursive call its initial
target is a source prefix or the completed change to that prefix; no
unbounded sequence of target magnifications is assumed. The implementation
is an exact-rational reference with explicit
rounding; it is not a fast fixed-precision arithmetic compiler.

## Products and paid precision

For a certified kernel `Q(U)=r^-1 product_j(U-rho_j)`, use the same factor
maps as PR628 and PR846, with `U=tau Z_L^w` and constant `|tau|=1`.
For an outer root use coefficient `tau/rho` and multiplier `-1/rho`.
For an inner root use coefficient `rho*conj(tau)`, stride `-w`, multiplier
`conj(tau)`, and output shift `-w`. Include `r` in one multiplier.

The implementation uses PR628's balanced four-call dirty commutator.
It requires `h=ceil(log2(r-1))` distinct arbitrary dirty arrays. The new
leaf needs no additional array. For `n` factors, the complete leaf count is

    N(1)=1,  N(n)=2N(floor(n/2))+2N(ceil(n/2)) <= 4n^2.

A negative composition reverses the order and signs of the four child
calls. Ancestor inputs and targets cannot be used as deeper scratch.
All source and borrowed data restore exactly. The final rounded increment
of a composition can depend on the initial borrowed values, as in PR628.

For a simple sufficient bound retain PR628's full-word perturbation proof.
Put `a=68(r+1)/beta^5`, `G=2+r/beta`, and let every initial array have norm
at most `D`. If `a*u<=1`, then the execution error is at most

    N a (D+1) u G^(N-1).

Choose `W` at least the incoming grid precision, the admission budget, and

    p+1 + ceil(log2(N a (D+1))) + (N-1) ceil(log2 G).

This pays the execution error to `2^(-p-1)`. The pinned factor certificate
pays the remaining error to `2^(-p-1)` after scaling by the source norm.
For general input norm `X`, coefficient preparation must use target
`p+ceil(log2(max(1,X)))`. The supplied fixtures have ample certified margin;
their scaled perturbation is checked exactly, not assumed.

With PR628's inherited `log2(1/beta)=O(r^3)`, this conservative choice is
`O(p+incoming_bits+log(D+1)+r^5+log(log L+2))` fractional bits. Integer
magnitude bits have the same order. An explicit safe integer reserve is

    ceil(log2(D+1)) + N ceil(log2 G)
      + ceil(log2(512(r+1)/beta^7)) + 3.

This note does not claim a precision improvement. Gareth Davidson's PR877
and Chafik Boukhalfa's PR905 give stronger prefix bounds for the predecessor
dispatcher. Their cubic or quartic conclusions are not imported without a
separate check of the new leaf contract.

## Complete tape and preparation bill

The meter maps every mutable array to one of **two** physical tapes and
an absolute tape offset. It charges the distance from the previous head
position plus one unit for each read or write. It counts transport swaps,
validation, source restoration, and explicit final head returns. It does
not give each borrowed array a free tape head.

One non-base visit costs at most `640n` record moves, apart from its two
children. Six causal maps cost at most `384n`. Baseline and seed scans cost
at most `24n`. The closure swaps and travel into and out of the child spans
cost at most `32n`. These total less than `640n`. The loose allowance also
covers the root cyclic view and entry positioning. A base visit costs at
most `8n`. Since `S<=6L`, validation and head returns leave the complete
leaf below **`4096L` data-record moves**. This is a proof bound, not a claim
that its constant is sharp.

For a full kernel with `h>=1`, place the last borrowed array on tape B.
Place the source, target, and other borrowed arrays consecutively on tape
A. If a leaf's two arrays are both on A, swap its target with the array on
B, execute the leaf, and swap back. The B array is distinct from both
operands in this case. Its contents never enter the leaf calculation and
are restored exactly. If a leaf already uses both tapes, no such routing
is needed. For `h=0`, put the two arrays on separate tapes directly.

This routing adds `O((h+2)L)` moves per leaf, including the distance between
array slots and returns to the tape origins. The full bound used by the
checker is `8192(N+1)(h+2)L` moves. It includes the initial validation scan.
No extra data array is allocated for transport.

Let `W_total` include the fractional bits, integer reserve, and the bit
lengths of the immutable coefficient, gauge, and margin descriptors. The generic
rational API does not bound descriptor length from coefficient magnitude.
Let `M(W_total)` include the chosen rounded scalar multiplication and
division cost. With this complete scalar word size, the resulting bill is

    preparation + O(N L) M(W_total) + O(N(h+2)L W_total).

Locating a factor on a sequential read-only descriptor tape costs at most
`O(r W_total)` per leaf, hence `O(r^3 W_total)` over the word. The original
factor and phase preparation charges remain inherited from PR628; this
descriptor access is included, not treated as free. Temporary powers,
source reads, multipliers, divisions, copies, inverse calls, and children
are all charged. The two data tapes, scalar arithmetic tapes, and metadata
stack use a fixed number of tapes. Borrowed data storage remains `hL`
complex words. Scalar arithmetic workspace has the declared word size;
the leaf index stack has `O(log^2 L)` bits. The balanced composition and
array routing retain another `O(log r (log r + log L))` metadata bits.
Their control cost is absorbed by the routing and descriptor terms, since
`log L=O(L)` and `log^2 r=O(r)`. These are metadata bits, not arithmetic
registers or data arrays.

This is a constant-coefficient kernel construction. Variable site phases,
complete-transform composition and normalization, common-label/Clifford
compilation, physical supplier hosting, and the multiplication reduction
remain open. There is no new kappa, complex b, or BIT c claim. Finite replay
is not a formal proof of the full theorem or independent human review.

Chafik Boukhalfa's concurrent PR951 gives two grouped additive calls with
no dirty connector in a neighboring-cycle layout. It uses a larger clean
scalar workspace. This note instead uses constant clean arithmetic storage
per first-order leaf, the original logarithmic dirty array budget, and
arbitrary-stride transport. It makes no claim to improve PR951's arithmetic
count or cubic precision.

Chafik Boukhalfa's PR977 removes the length admission and proves cubic
precision for PR846 in its original clean scratch model. This construction
retains its stated admission and conservative precision. Combining those
precision arguments with the new dirty leaf requires a separate proof.
