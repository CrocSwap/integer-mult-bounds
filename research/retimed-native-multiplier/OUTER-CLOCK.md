# The non-native clock of the single-band product

This calculation uses the default signed tape machine at #8030, commit
6285dd829114705862e8d91facaedc1f31d3cfcb, and the same outer at #8035,
ea776471bf8ed143a0625cf2d7532f65d15eb5f9. It uses their stated private
compiler, numerical correctness and physical service theorems. It does not
discharge the five research premises of #8035. The unit is one move on a
fixed-alphabet, finite-multitape machine. All fair comparisons must fix that
unit. The Python reference uses seekable files, arbitrary integers and host
lists. Its interpreter instruction count is a different quantity.

Let n be the greater significant input bit length, with n at least 2 in
the formulas. A separate sign and two declared unsigned little-endian
magnitude intervals specify the input. Both input heads return to their
original positions. A zero product occupies one byte. Extra declared leading
zeros cost their actual aggregate length. At canonical lengths this adds at
most linear time. Let b=ceil(log2 n), p=6b, s=ceil(log2(p+2)), L be the
address width of the tensor, T=2^L and V=Tp. Its two true-width classes have
d total axes. Let ell denote the largest actual width and P the Gaussian
working precision. No table in this note takes multiplication operands as
an argument. Both source-size factors in (4·2^b·product(sides))², the
truncations to p and the actual final carry are those of the source.

## Fixed-tape scan conventions

Use separate tapes for a sender, receiver and temporary. A left-to-right
copy/erase costs fewer than 16 transitions per bit including rewind, tests,
and binary-byte delimiters. Reserve 2^24 transitions to open/clear a short
64 KiB buffer if used. A fixed-width binary comparison, shift, add or move
with both heads restored costs fewer than 2^8 transitions per bit by
forward and reverse scans. In a streamed loop keep counters low-bit first.
Consume a binary count by decrement with borrow and return to its low end.
Over m successes the number of zero crossings is at most
sum(floor(m/2^i),i>=1) + bitlength(m); the final failed decrement scrubs
the temporary. All bits above the low 16 can label a loop over complete
65536-byte chunks. Retain the low 16-bit remainder for the final copy.
A skip advances a tape head over the whole
interval. Absolute addresses in a sequential scan can be maintained by the
same ripple counter, or replaced by its specified relative move.

The installed `fiscal_scans.magnitude_bits` reads each declared byte once. It counts its trailing zero run with a low-first ripple counter, resetting that counter on each nonzero byte. Each reset pays for its own preceding zero run. It computes the endpoint once and restores the input head. The fixed sequential spools copy or skip a whole interval with a low-first block count and one bounded final piece. See [the executed scans](fiscal_scans.py) and [the fenced tape checks](check_scans.py).

For a signed w-bit word use the production difference-form Karatsuba with
terminal width 192. The sign is stored separately. Pad the width to the
next dyadic length for the bound. Tape markers separate disjoint operands,
three child results, and the output; a depth-first child frame follows its
parent. Including head returns, fewer than 64 complete interval passes,
each over fewer than 64(w+1) symbols, suffice to split, make both
differences, append each of the three entered arguments, read each result,
align the three shifts, sum, and clear. The ancestor work area has no scan
inside a child. Allocating 2^17(w+1) transitions at each internal node
and 2^36 per schoolbook terminal gives fewer than 2^40(w+1)^(8/5)
transitions: there are 3^j nodes at level j and each width halves. The
dyadic padding costs less than a factor of two in width. Word products
here never receive whole external operands except at the scalar cutoff.

## The finite interval

For s<512 the square selector uses W=64s². When the shape exists,
ell<=128s². For all admitted shapes d<=p, ell<=p and
P<=2^20 p. For this last bound insert h=max(1,floor(d/(1024s))) into
the actual pack precision. Then h(ell+6)<=d(ell+6)<=L+7d<=8(p+3).
The four logarithms of the stage count and the 67 trailing bits fit the
remaining slack. With t=2^ell and X=2^64(t+2)(P+2), the private bound
D=d X^1024 therefore satisfies

    log2 D <= s + 1024(ell+s+88).

The same proof of its private bit heights and scalar loops applies to the
old square selector. For s<=31 the right side is at most 126082079.
For 1≤s≤31 use n>2^(b−1) except at the trivial n=1 door. Because s=ceil(log2(6b+2)), subtract max(0,floor((2^(s−1)−2)/6)−1) from the private exponent before maximizing. The largest result is 84,484,466 at s=27. Other scan terms below have a separate additive bill. [Exact finite maximum](outer_clock.py)

For s>=32 it is below 2^(s-4)<log2(n). Check the quadratic numerator at
32 and double the denominator at every subsequent integer. The linear
tail at 512 makes ell smaller. Thus private generation costs at most n
from s=32 on, regardless of whether a native stage actually opens.

For small CRT groups bound the cost of all controls at one address by

    Q = 2^60 (p+2)^16 (t+2)^10.

The source lists all modular images, recursively colors both Beneš
children and forms (2ell-1) binary tables. There are fewer than 2t
recursion nodes. At one node of size at most t, allow 2^8(t+1)^2
indexed comparisons or actions, even using a quadratic permutation check.
A linear search of all saved permutations, inverses, tables, stacks and
results visits fewer than 2^12(t+1)^4(p+1)^2 bits: the local width is at
most p. A permutation, its inverse, the two colors and at most 2ell−1 switch rows occupy fewer than 2^8(t+1)^2 entries per node (ell=log2(t)). There are fewer than 2t
nodes. A fixed-width read/write, comparison, loop count and its head
restoration fit within four full such scans times 2^8(p+1). Alternate
rewrite tapes permit insertions without an uncharged shift. Restoring the
source coordinate permutes at most p bits; a group contains at most p
axes. Each left child reconstruction needs at most p CRT terms and modular
inverses on at most 4p+8 bits, including the unnormalized left sum.
The source long division/Euclid bound is 2^20(w+1)^3. Even allowing a
complete p-element search before each, these contributions are below Q
with scrub. A repair key reverses the ten operations in CompactSwitch.WORD (two four-step F words, load and unload), then calls the switches once. At most eleven such control evaluations are needed per key. For
s<=63, log2 Q<=5081414.

At s>=64 the very same greedy grouped CRT path has L>=10100G for
G=64(ell+s), H=G floor(L/(100G))>=L/101 and d>=51200. Indeed
L>=p/12 and d>L/(2W)-1. Bound ell<=128s² throughout and check
at 64, then use doubling versus quadratic growth. Every free root
quarter has at least L/8 bits and deleting its two forbidden high
reservoirs and low reservoir leaves at least 3H consecutive bits.
The non-root unused half has at least that much space too. Consequently
jobs() never returns the individual unbuffered case. A tail single's
actual dest is H. It evaluates a switch once per 2^(H+1) addresses.
CompactSwitch.raw calls its controls once per 2^H records or fewer;
the inverse code in repair_key evaluates at most eleven controls per 2^H-record
group. Even dX^1024 fits below 2^(H-16) on this range, as does Q.
Their binary logarithms grow quadratically and H>=p/1212 grows
exponentially. Even eleven Q evaluations and eleven fresh private compilations then cost fewer than 22·2^(H−16) steps per group of 2^H records. The complete control cost fits one traversal of the slice, counting at least one step per record.

On the bad-set repair, each of at most d members excludes two all-one
G-bit digits or one of the two extreme strings on 63G-2 guard bits.
The union has measure at most 3d 2^-G. This does not assume independence
between different exclusions. The complete destinations are sorted on at
most L bits. Each tag is shorter than the entire grouped buffer even when
the slice payload is just one byte per address. Since 3dL 2^-G<1, all
stable radix passes input and emit at most one additional slice of payload in total. Keys have at most L bits and each exceptional group carries at least 2^H payload bytes, with H≥L/101 and 2^H≥L. Marking, copying to the two buckets, rewinding, concatenating the two streams, deleting, rescanning for the returned hole and clearing the marked file use fewer than 32 one-way transfers of a slice after doubling for key volume. Even 2^16 transitions per transferred bit, including the restoration and counters above, cost under 2^22 slice bits. Each failed group calls the ten-operation inverse key routine once. The packing here includes every hole.

For all s<512, none of the comparator or retimed native carriers can be active:
every installed native rank logarithm is at least 1024. The ordinary leaf is the
four-bucket, at-most-p digit swap, and the positive leaf is the exact
ordered two-pair arithmetic on at most p coordinates. Its public
widen/phase/narrow and clear are counted. A crude volume multiplier
2^160(p+2)^25 suffices: one transform has at most d packs of
40000(ell+2)^6+4 stages, each with at most p single-axis passes; the
three CRTs have at most 2p³ row, target and level choices, at most
32 variable rotations per compact switch and p sparse radix passes;
each bucket swap uses at most p full four-bucket sweeps; both kinds of
stripes use at most p slices; fixed word arithmetic is less than
2^40(2^23p)^(8/5). These estimates also allow one unfused p-bit loop
counter update at every transferred byte. For s<64 multiply the scan
bound by Q. For 64<=s<512 the prior group amortization removes Q.
The result has log multiplier below 5.1 million everywhere. Add the
private compiler once. An absent shape also has a finite numeric clock:
on 2^j<=b<2^(j+1), s<=j+4 and L>=2^j-j-1. For j>=15 this exceeds
64(j+4)^2 by induction, so the scalar branch always has n<=2^32768.
Its signed word and file costs are less than 2^32820 n. Altogether
2^(84500000) n suffices for every s<512.

## The cofinal outer call count

For s>=512 use ell+2<=2^11(s+1), P<1.02p, V<48n, and G=64(ell+s).
The two widths, two root passes, true first-mixing tag and at most
ceil(d/h0) remainders give at most 80000(ell+2)^6+2048s+2 packs.
Each completed pack has at most 40000(ell+2)^6+4 H/diagonal stages,
using the local matching, its forward/inverse Beneš rows, sixteen-H
lowering and both root passes. Over the two forward and one opposite
transform their product is below 2^168(s+1)^12.

At a CRT level there are fewer than 2ell rows. At each row there are
at most 2^18 batches, since floor(H/G)>=d/51200 and there are two free
halves/quarters. A batch uses six reserve placement/return swaps, at
most K=64G colors and at most K² individual tails. A compact switch
has at most 20 whole shuttles, 10 rotations and one full repair. Count
10+32K+4K² positive-volume macro operations. Across levels and three
calls this gives fewer than 2^90(s+1)^4. For a fixed BIT or CRT
operation, sum actual stripe volumes, which are disjoint portions of
the same T-record array. Separately charge the scan of the original
bank that reaches each stripe: its count is at most 2 sqrt(p+2);
both gather and scatter pay their complete head travel, including each
marker rewind and the final erasure.

Each tensor diagonal has fewer than 3T signed complex grid products,
including partial suffixes and initialization. One has four signed
products of at most 10p+100 bits. Store coefficient tables in descending
axis-width order. Reaching table j can traverse at most (j+1)t0 records
after the fastest table of size t0, and occurs at most T/(t0·2^(j-1))
times. The sum of (j+1)/2^(j−1) over j≥0 is eight. This pays at most 8T record traversals on returns;
count a copy of the private inventory for setup. Each record includes
precision, crossing and rounding bits. Source validity can be checked
by a scan of the full d-tuple per record as its total coordinate width
is L address bits plus at most four delimiter and loop bits per axis. Keep each coordinate in its fixed-width field, and use a sequential delimiter walk of at most L+4d bits on this pass. Pointwise multiplication, conjugation, both digit-scale
and source-size recoveries, grid conversions in both directions, CRT,
sign, carry, input heads and returned output have the same or smaller
word/scan bill. Reserve 2^58 V p^(3/5) per arithmetic stage. The
spectator collector's two file scans add at most 2^38 V sqrt(p+2).
Its layout comparisons and total extent calculation are private,
at most 2^40(p+2)^8 once per stripe, which the actual stripe absorbs.

Let B denote a proved unit-volume fixed constant of the actual ordinary
swap on arbitrary exterior/gap/suffix, for a=κ+4g. Let Z denote
the corresponding positive constant at price at least κ+g: its clock
on a pack with h selected axes is at most
Z·(s+1)^2·volume·(1+h)^(1-a). The separate note gives an upper bound
for Z from B. Separately charge the two support exposures at the top
using B and width h·ell<=L. A full source record has fewer than 5p
bits; the paid services get their actual stripe extent, including all
allocated slots. One non-native macro costs at most a sum of the
above scalar, gather, grouped-control, or paid-service bills. The
extra factors from the bounded reshaping, outer byte grain, three
transforms and restoration fit in 2^400 for the whole bound. In
particular 2^168 times 2^58 leaves 174 further binary factors of two.
Replacing all the powers by the largest one yields

    time <= 2^400 (s+1)^16 (1+B+Z) V p^(1-kappa-g).

For g=10^-17 or the larger g=10^-14,
(s+1)^16/p^g <= (128/g)^16 < 2^1024. Use s+1<=4 log2 p and maximize
y^16 2^(-gy). Replacing V,p by 48n and 6 ceil(log2 n) then gives a
cofinal factor below 2^1434(1+B+Z). Add 2^(84500000) for the finite
prefix. This is an explicit reduction of the outer time constant to
the actual physical native constant. It gives no timing crossover.

## Reproducible source bindings

* [Signed entry](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/band_product.py)
* [Linear square controller, private clock and stop](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/LINEAR-GEOMETRY.md)
* [Completed pack, precision and actual transform loop](https://github.com/CrocSwap/integer-mult-bounds/blob/9585c1fa2ed5f2316ac09e04b357cb720badfcb8/research/triangular-native-supplier/multiplier.py)
* [Original axis compilation, grid/rounding/CRT/carry](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/product_path.py)
* [Finite selector, true-axis witness, fixed private instructions](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/OUTER.md)
* [Root count and odometer](https://github.com/CrocSwap/integer-mult-bounds/blob/3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd/research/direct-circulant-fourier/COMPOSITE-OUTER.md)
* [CRT eligibility, real controls and tail dest](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/crt_tree.py)
* [Exceptional keys, radix passes and rotation](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/compact_crt.py)
* [Finite binary input, extrema and carried output](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/binary_io.py)
* [Updated positive margin](https://github.com/CrocSwap/integer-mult-bounds/blob/ea776471bf8ed143a0625cf2d7532f65d15eb5f9/research/p104-single-band-signed-margin/PROOF.md)

## The 70-bit stop parameter

At g=10^−21 the previous 1024-bit inequality fails. Put y=log₂ p. For s≥512, y≥s−2, so s+1≤17y/16. For every real t≥0 one has t≤2^t, since 2^floor(t)≥floor(t)+1. Apply this with t=gy/16. It gives (s+1)^16/p^g ≤ (17/g)^16 < 2^1182. The scalar inequality is verified with integers. Since V<48n and p=6 ceil(log₂ n), conversion to the stated input unit adds at most nine bits to the factor. The cofinal exponent for (1+B+Z) is at most 400+1182+9=1591. The original 1600 allowance covers the remaining two bits for the sum of the three services. The explicit initialization and finite-prefix bounds still apply. [Actual stop, ranks and allocation](RESOLUTION.md)
