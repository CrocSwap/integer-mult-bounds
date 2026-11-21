# Input lengths for the complete stock-aware fast path

Use the six-stage ordinary construction at a ternary input width at least
$E_6$. Here $H=240000000000000$, $N=2^H$,
$E_1=2^{\lceil25000(2H+12)/24903\rceil}$, and
$E_{i+1}=4096N^2E_i$. The complex rank is $M=2^{3300000000}$.
The separate ordinary theorem must establish the six active calls on
real atom fields at this input width. This note establishes their outer
inputs. It defines native activation as execution of a positive-rank
complex body on true Fourier axes and a nested positive-width chain of
all six ordinary bodies. Small remainders retain their paid primitive
rules. A stronger threshold puts the same chain inside the true positive
complex operation.

## Two adjacent widths

Let $n$ be the number of operand bits. Use $b=\lceil\log_2 n\rceil$,
$p=6b$, $T=2^L\in[4n/b,8n/b)$, $V=Tp$, and
$s=\lceil\log_2(p+2)\rceil$. Throughout the bounds below $s\ge512$.
Direct comparison gives $p/12\le L\le p/6$, $24n\le V<48n$.
Set $W=64s^2$ and take $d$ as the greatest power of two at most
$L/W$. Give the first $L\bmod d$ axes width $\lceil L/d\rceil$,
and all others $\lfloor L/d\rfloor$. Write $\ell$ for the maximum.
Then $W\le\ell_i\le2W$, $d\ge2^{s-13}/s^2$, the first axis is
widest, and every global quarter contains at least $L/8$ bits.

Use the alternating square bands and the first coprime odd base of the
predecessor. For its $m$ distinct excluded primes, $m+1\le p+2\le2^s$.
Odd Bonferroni truncation at $8s+1$ proves that more than
$2^{1+s(8s+2)}$ consecutive integers include a base prime to the
accumulated product. The narrower interval has at least
$2^{\ell_i/2-s-6}-2$ candidates, which exceeds this bound already for
$s\ge2$. Thus all scans succeed. The true product of the sides obeys
$3T/4\le S<T\le2^b$ and $2\lceil n/b\rceil-2<S$.
The CRT stages, true Fourier means on original positions, identity on
holes, and carry procedure are therefore admissible. [Square count,
layout and full product proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd/research/direct-circulant-fourier/COMPOSITE-OUTER.md)

For this same $p$ the old largest actual axis width was at least
$65536s^3$. Each largest dyadic side falls from at least
$2^{65536s^3}$ to at most $2^{128s^2}$. The old compiler actually
materializes its private square matrix. Its peak number of scalar entries
is at least $2^{131072s^3}$. With the retained polynomial tape compiler
the entire new private setup is at most $2^{O(s^2)}$, including scanning,
preparation of all $d$ axes, and cleanup. Section 5 gives an effective
clock. The padded array still needs $T$ records. The slots and bits in
that array do not disappear.

## Numerical guard and a true-column witness of mixing

Use the source quantities

$$
 E=4096(L+6d),\quad J=20000(d+1)(\ell+2)^6,\qquad
 P=4p+8E+4\operatorname{bitlength}(J(d+1))+64 .
$$

They give $P<2^{20}p$ at $s\ge512$ using $d,\ell,L\le p$.
Thus $s'=\lceil\log_2(P+2)\rceil\le s+20$, $G=4s'+6\le6s$.
The product assigns physical axes before all CRT conversions. Sort by
decreasing binary width and the mixing tag below. Take at most
$h_0=\lfloor d/(1024s)\rfloor$ consecutive axes of one equal-width
class per H pack. The pack uses their **entire original windows**
$K'=\ell_i$, with the actual significance $0\le j<K'$, including
$j=K'-1$. The guard $K'\ge128G$ holds for $s\ge512$.
Clipping a complete window to a smaller exposed segment is unnecessary.

Trace a genuine column of every exact stored rational local word.
The initial true wire is 0. Until the column first has more than one
nonzero component, just follow its unique wire. At its next scalar or
pair gate inspect the corresponding column. An invertible gate has a
nonzero output. Stop when both entries are nonzero and record the root
pass (one or two) and matching-layer number. This does not need to
construct a signal vector. The primitive axis certificate bounds the
operator error by $2^{-P}(64t)^{400}$, including its bounded conversions,
for $t=2^{\ell_i}$. At the stated input bound this is less than $1/(2r_i)$.
The target mean sends the true input wire 0 to all original wires with
magnitude $1/r_i$. Entry and exit diagonals cannot turn a singleton
into several wires. Thus every axis has a recorded branching gate.
The observed change cannot originate on a disconnected block of holes.

Group the physical axes by width and this pair of indices. Run the exact
same complete H stage by taking these groups in turn and splitting each
at $h_0$. Partial factors act on different coordinates and commute.
This uses at most $2\cdot40000(\ell+2)^6+O(s)$ packs. The global
arithmetic stage cap $J$ was computed allowing as many as $d$ packs.
At least one genuine-mixing group yields a pack of size

$$
 h\ \ge\min\{h_0,\lfloor d/[80000(\ell+2)^6]\rfloor\}
 \ \ge 2^{s-100-16\lceil\log_2s\rceil}.
$$

At the recorded matching layer each of its axes has a genuine mixing
pair. The local Beneš route and fixed sixteen-H lowering transport these
pairs onto one common selected significance. Thus the supplier receives
a real tensor layer on those axes. The executable tracker checks both
root passes and the actual matrix column. It does not read the operands.

The unchanged error proof bounds an arbitrary ideal interval by $2^E$,
the local grid defect by $(d+1)^22^{-P+2E}(1+\|z\|_\infty)$,
and the raw half-disk error by $2^{-4p}$. Splitting an H into packs was
already included. After conversion, the two normalized forwards, their
rounded pointwise product and the opposite mean have the source bound
$3e$ for $e=3/B^6$, where $B=2^b$. Both independent digit scales and
source-size factors appear in $(4BS)^2$. Every unscaled error is at most
$144/B^2<1/2$. The three original-coordinate CRT passes, carry, signs,
integer product and restoration retain their bounds. Each integer
and fractional component on the complete data tape occupies $O(p)$
bits. [Private synthesis and precise guards](https://github.com/CrocSwap/integer-mult-bounds/blob/3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd/research/direct-circulant-fourier/PROOF.md)

## The actual complex rows and a nested ordinary site

The completed ordinary ABI takes two actual equal-sized bit fields with
arbitrary complete exterior, gap and suffix. Within its own operand it
pads the two binary sections to trits, borrows its row field, retains
all low/high rows and recursively realises preceding exchanges. It
removes padding and returns the ordered output before another instruction
reads it. Call that ABI on the compact $fG$-type fields and exposure
shuttles. Its row stock is inside its borrowed input. The suspended
complex row labels are exterior to these two binary sections. Charge
the full ordinary backing, including a constant radial factor below
9 at each different ordinary stage. This rule avoids materialising
another copy of the ordinary stock in the complex prefix. The separate
complex owner rule requires $B_c^{D_c}$ independent rows with
$B_c\le M^{448}$ and $D_c=2+\lceil\log_M(h+1)\rceil$.
The actual periodic batch $B_c$ is a power of two. All its rows live in
the genuine dyadic input. Its at most $16/15$ per-call extension uses
separately allocated zero buffers, still charged to that call. Every
suspended complex row and ordinary reservation has its own storage.
[External row and precision rule](https://github.com/CrocSwap/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/COMPLEX-LAYER.md)
· [Concrete ordinary embedding](https://github.com/CrocSwap/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/ORDINARY.md)
· [Stopped price and batch cap](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/STREAMED-MACHINE.md)

The numerical stripe removes $r=\lfloor s/2\rfloor$ bits of one
unselected axis from the address, leaving $L'=L-r$. All active full
windows stay consecutive. On the smaller rectangle a native call has
$h\ge M$, hence $\log_2 M\le s$. Provide four disjoint intervals in
one exterior part, together with an untouched low suffix of $(s')^2$
bits. They require the following lengths.

* The complete data window uses $hK'\le ds/8\le L/(512s)$.
* Three control intervals use $3hG\le 18d/1024<L/64$ bits together.
  A raw body at any open context has at most $h$ physical columns.
* The leading complex row field uses at most
  $448(3\log_2M+s+1)<1793s\le L/16$ bits.
  Its next $\log_2B_c$ bits partition a recursive call once. The
  remainder of this genuine prefix stays available in each child.
* The grouped suffix has at most $4s^2\le L/16$ bits.

Their sum is less than $L/4$. Since $L'\ge15L/16$, at least one of the
two exterior components of the active window has length larger than
$L/4$. Place all these fields in that component in the order used by
`complex_stage.entrance`. Exchange the complete active window with its
equal-width data position there. Every bit used for the swap has an
arbitrary incoming value. Use the unchanged high exterior as independent
slabs. Use the actual row field inside each slab, perform all arithmetic,
restore every dirty control, then interchange back. Every selected
coordinate participates. There is no deferral of an unknown subset.
Below the fixed rank stop use the individually paid positive kernels.
Within a larger call stop at $\max(M,h^g)$, $g=10^{-14}$. The
corresponding slab, owner lifetimes and actual numerical charts are
described in [the numerical construction](COMPLEX.md). The original
window exposure is paid by its two genuine service calls.

The following explicit source path demands another whole-window
ordinary interchange *inside a numerical native word*. Put $m=M/4$
and $A=153^{264}$. Take any admissible unit of the periodic forest on
the empty paid path, for example its future with all minimum-rank
$17^{264}$ target factors. Take the powered target that repeats the
actual raw port `("root","rotated",191,9825,1)` exactly 264 times.
Its raw positive rank is $R=129$, verified in the authenticated word.
Its rank $R^{264}$ qualifies for productive credit since $R>17$.
On the empty path the forest binds this target to an external source.
At outer round zero and replica zero its lane is a genuine input. Its
offset is less than `owners_per_copy`, while the productive width is
at least fifteen times that count. Write $c$ for the unit's positive
column multiplicity. Its ordered source rank $u=cR^{264}$ satisfies
$3\le u\le cA\le m$.

Let $q$ be the least power of two with $qu\ge M$ and
$x=(qu-M)/4$. At round $j$ the ordered source requires
$A_x(j+qt)$, $0\le t<u$, with
$A_x(z)=\lfloor z/5\rfloor$ for $z<5x$ and $A_x(z)=z-4x$ otherwise.
We have $q\ge4$ and $x>0$ implies $q\ge8$. The Lean theorem
`requiredGap` gives $A_x(j)+2<A_x(j+2q)$ in all cases, including a
crossing of the piecewise boundary.

At the first tensor depth the powered interpreter passes this very
owner to its specified raw root with $cR^{263}\ge3$ raw columns.
The actual root destination consists of its head followed by its true
body colors; its first three canonical slots are $0,1,2$ because the
head alone spans $cR^{263}$ slots. Thus the ordered physical source
cannot already match its actual canonical destination. The raw
`align` loop necessarily exchanges two disjoint complete
$fK'$-bit slots, where $f=\lfloor h/M\rfloor$. It then performs
the native instructions on this real external owner. Its exit restores
the recorded placements on the completed physical result. The ordinal
source and canonical destination need not each be one interval; the
first three slots suffice. This is part of a productive root inside the
first actual powered level. Its return affects the full numerical
tensor used in the next multiplication stage. [Chronological source and physical tickets](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/periodic.py)
· [Tensor expansion and retained source alignment](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/powered.py)
· [Authenticated raw labels](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/tagged_sources.py)

An actual raw placement and its inverse have at most $2M$ whole-slot
swaps. Their width $fK'=O(fs^2)$ is at most a factor $O(s)$ above
$fG$. The entire outer pack exchange has width $hK'=O(hs^2)$. Together
with the physical compact row-adds and their sparse repair both charges
fit $O_F(V(1+h^{1-a_{\rm bit}})\operatorname{polylog}p)$ per local
complete layer. This includes conversion, cleanup, real exterior
values and all changed return fields. Compiler expansion and suspended
bank factors remain fixed at the stated native dimensions.

## Two complete thresholds

The physical balanced CRT router fixes $G_0=64(\ell+s)$,
$r_{\max}=\lfloor L/(100G_0)\rfloor$, and **$H_0=r_{\max}G_0$ for
each batch**, including its colored subbatches. It reserves three disjoint
$H_0$-bit fields from the opposite half or quarter. Here $L\ge10100G_0$
and hence $L/101\le H_0\le L/100$. Each of the four target-buffer
updates and two control updates in a genuine compact switch physically
shuttles its full $H_0$-bit field with the back buffer, performs its
ordered rotation, and shuttles back.

To verify that a nontrivial compact switch occurs, set the restored root
left ordinal to 1. Every right true axis then has an offset equal to
the inverse of a preceding coprime prefix modulo that side, hence
nonzero. Each of its local Beneš networks must contain a nonidentity
switch. At most $2^{18}$ batches occur at a root row because
$r_{\max}\ge d/51200$. There are fewer than $2\ell$ rows and at most
$64G_0$ colors in each. Fewer than $(64G_0)^2$ tail positions appear
per batch even if colors choose different final locations. Since
$G_0\le128\ell$, the resulting count is at most $2^{46}\ell^3$.
There are $d/2>2^{46}\ell^3$ different right axes throughout this
range, by $d\ge2^{s-13}/s^2$, $\ell\le128s^2$, $s\ge512$.
Therefore a nonidentity switch survives the exceptional one-bit tails.
Its natural return is used in that same rotation and in restoring the
true CRT addresses. Sparse bad-key repair, dense generation on complete
fibres, the original suffix, the true control and its inverse all
remain in this router. [Paid root and compact CRT shuttles](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/unconditional-batched-crt/CRT.md)

Every $p\ge4096 E_6$ gives a true ternary request
$e=\lceil H_0/\log_2 3\rceil\ge p/2424>E_6$. The traced numerical
pack has far more than $2M$ selected axes on this range. Thus every
$n\ge2^{\lceil4096 E_6/6\rceil}$ satisfies the stated complete
native criterion. At $p\ge N^{16}$ the *same genuine complex source*
also issues a ternary request $\ge fK'/2\ge E_6$. Substitute the lower bound
on $h$ above into $f=\lfloor h/M\rfloor$. The ratio
$2^s/s^{16}$ increases on this tail. Thus every
$n\ge2^{\lceil N^{16}/6\rceil}$ satisfies the stronger connected
criterion. The exact binary logarithms of $E_1,E_6,4096E_6,N^{16}$
are 481869654258536, 2881869654258596, 2881869654258608 and
3840000000000000, respectively.

For the old six-stage construction every consecutive active predecessor
stage receives at most $w+1$ trits for $w=\lceil e^{1/250}\rceil$.
It restores its $k$ borrowed positions by individual digit swaps.
Each active parent has $e^{1/250}\ge2$ from the old stock bound. Hence
$w+1\le2e^{1/250}$. For $u_i=\log_2 e_i$, the five transfers give
$u_1<u_6/250^5+250/249$ by summing the geometric series. The old actual
bottom stock already needs
$u_1>(2H+1)250/249$. All outer binary swap widths are bounded by $L+1$:
the CRT uses $H_0\le L/100$, the support exposures borrow real bits
within $L$, and the compact complex shuttles occupy their physical
chunks within the exposed stream. The one current whole-row padding
has factor below two. Bank indices are separate tapes or owner fields
and do not enter the binary swap operand. Thus $e_6\le L+2\le p$ in
the old admitted regime. A necessary old threshold for the same six
active stages is

$$
 \log_2 p>250^5\bigl((2H+1)250/249-250/249\bigr)
 >470632530120481927710843373.
$$

This lower bound applies to a nested six-native chain. The old Fourier
dispatcher can return a correct product on smaller inputs with
elementary ordinary/complex leaves. The new sufficient thresholds do
not compare wall-clock times. In particular $J_0=N^{20000}$ still
bounds native installation before numerical setup, and no strict
runtime comparison against a practical multiplier follows.

## Private setup and the complete bill

Here is a conservative sequential private compiler clock. It covers the
coefficient circuit in the pinned source. Let $t=2^\ell$ and
$X=2^{64}(t+2)(P+2)$. Count heights in **bits** of a reduced real
numerator or denominator. The following bounds can use the literal
fixed-tape transcription with binary arithmetic and sequential tables.

* The input Fourier chirps have angles with denominator at most $8t$.
  The spectral root allocates $P+O(\ell)$ bits, and the full, generator,
  triangular and phase allocations in the cited formulae add at most
  $4096(\ell+6)$ bits. This follows by substitution of
  $\Lambda\le4t$, $Q\le8t^2$, the root radius $2t$,
  and the local precision counts in their allocation functions.
  These bit counts are below $X$. The Machin arctangent series has fewer
  than $2B+64$ terms at working precision $B$. The exponential remainder
  at term 8 is below $2^{10}$ and its ratio is at most $1/2$ at subsequent
  terms. Thus at most $2B+64$ terms suffice for it too. The Taylor loop
  rounds outward at each step. An unreduced factorial or an arctangent
  partial sum has height below $2^{12}(B+1)^3$ by multiplying term
  denominators. The stored rational phase has height at most $2B+12$.
  Each spectral entry sums at most $t$ products of these phases and is
  then rounded. This gives initial field heights below $X^{10}$.
* One square-matrix operation with input component height $h$ can
  multiply entry heights by $F=2^{16}(t+1)^6$, including its additions,
  multiplications and temporary eliminations. Clear at most $8t^2$
  real denominators on each augmented matrix of dimension at most
  $2t$ by $4t$. Each integral entry now has height at most
  $(8t^2+2)(h+1)$. The determinant expansion of a minor of order at
  most $2t$ adds at most $2t\log_2(2t)$ bits to $2t$ times that
  height. Elimination entries are ratios of such minors, including the
  allowed pivot permutations and partial Gauss–Jordan rows. A single
  pre-reduction update or an intermediate inner product of at most $2t$
  terms also fits the displayed slack. These estimates apply to exact
  matrix solves and to Schur complements with a tall right side. The
  original denominators must be kept when taking a minor ratio with
  unequal row counts; the same clearing bound accounts for them.
* A leading Schur descendant of the full root is a principal section
  after eliminating one set of initial rows in the original matrix.
  Its height requires one application of $F$ independent of the number
  of ancestors, by the minor formula. Computing each $K,L$, both adjacent
  products, displacement and the accretivity check needs fewer than six
  further applications. In the Stein orthogonalization every intermediate
  residual is the original column minus its projection on the preceding
  independent columns already visited. Use the Gram matrix of those
  original columns to bound **partial** residuals, even when the
  implementation updates them successively. Its Gram product, solve,
  product with the original basis, squared norm, exact row, and two
  dyadic normalizations take at most ten more applications of $F$.
  The dyadic shift index has magnitude at most the already bounded
  bit height of the numerator and denominator.
* A triangular generator root is formed by a fixed number of scalings
  and additions. Each parity descendant is a principal section after
  eliminating a principal subset of this original triangular root in
  its parity order. The principal-section and Schur identities follow
  by eliminating the accumulated set first and then the next set. Thus
  the same minor estimate applies once throughout each triangular tree.
  The series inverse is a solve with a lower triangular Toeplitz matrix.
  Also during forward substitution each finished partial row is a minor
  ratio; partial sums contain at most $t$ terms. The subsequent two
  convolutions, cyclic and negacyclic split, $t$-term spectral sums,
  rounded local butterflies, 2-by-2 gate inverses, and fixed sixteen-H
  lowering together cost fewer than 32 additional applications of $F$
  along a coefficient dependency. There is no chain of exact large
  matrix products applied to payload. A bound $X^{512}$ on the largest
  private bit length follows from $X^{10}F^{1+6+10+32}<X^{512}$.
* There are at most $2t$ full nodes, at most $2t$ child shears and
  generators per node, $2t$ parity nodes per generated triangle and
  at most $16(t+1)^4$ arithmetic, copy or table-loop iterations per
  resulting split before the one-dimensional phase loops. Each
  phase loop with any factorial recomputation has at most $X^4$
  iterations. Allow full scans to revisit stored lists of gates, pairs
  and labels. Before replacing indexed reads by sequential scans the
  number of symbolic operations is below $X^{32}$, also allowing the
  one-axis Beneš recursion, comparison sort, square search and simple
  products of earlier side values. Side prefixes have $O(p)$ bits.
  One complete sequential scan over **all** recorded intermediate
  objects at each operation and grade-school arithmetic/GCD on
  $X^{512}$-bit integers cost below $X^{4096}$ in total. This also
  bounds historical private backing and clearing. This transcription
  stores binary values. Python decimal diagnostic strings and host
  call stack limits are not a required arithmetic operation.

Thus $dX^{4096}\le 2^{2^{20}(s+1)^2}$ for the entire private setup
on the stated tail, by $\ell\le128s^2$, $P<2^{20}p$ and $d\le p$.
For $s\ge512$, $2^{20}(s+1)^2<2^{s-9}$ by direct check at 512 and
the consecutive ratio. Its total clock and space are less than $n$.
At the smaller complete entrance the former maximum dyadic width
logarithm was at least $65536s^3$, whereas the new width logarithm
is at most $128s^2$. Even the conservative upper clock exponent here
is below the logarithm of the old **actual** dense root matrix size
$131072s^3$. This strict setup gain concerns a per-input numerical
matrix. Fixed native setup and the main two operand tapes have their
own separate costs. [Root and private arithmetic](https://github.com/CrocSwap/integer-mult-bounds/blob/3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd/research/direct-circulant-fourier/ROOT-CIRCUIT.md)
· [Full allocator and Schur program](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/rational-unitary-fft/full.py)
· [Parity and generator lowering](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/rational-unitary-fft/generator.py)
· [Interval kernel](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/cubic-cyclic-inverse/vendor/interval_kernel.py)

The two-width/mixing buckets, extra packs and all matching layers add
only fixed powers of $s$. The remaining terms are the three balanced
CRT passes $O(Vp^{1-b_{\rm bit}}\ell^2\operatorname{polylog}p)$,
global support exposure $O(Vp^{1-a_{\rm bit}}\operatorname{polylog}p)$,
complete stopped positive layers $O(Vp^{1-\kappa-\delta}\operatorname{polylog}p)$
with the retained strict $\delta>0$, word products
$O(Vp^{\log_2 3-1}\operatorname{polylog}p)$, and full grid/shift/carry/
cleanup scans. For fixed price surplus the supremum of
$(1+\log p)^k/p^\delta$ on $p\ge2$ is finite. This supremum belongs
to the recurring constant $C$. There is no requirement to wait for
the logarithm to be smaller than $p^\delta$ with coefficient **one**
before the native routine is allowed to execute. Near the new entrance
the native path can be slower than another multiplication algorithm.
The complete claimed exponent is unchanged and neither a measured
crossover nor an improvement in the least possible $C$ follows.
