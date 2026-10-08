# Independent balanced transform review

The balanced positional layout has a valid conditional transfer to the
previously reviewed compact synthetic transform. The extra top bit of each
long axis costs one bit move; the common low bits are partitioned into
balanced chunks with no low-bit prefix phase. The resulting complete cost is

```
O(T p [d + p K^(tau-1) + ell d^lambda_prime]).
```

This changes the prefix margin from `1-epsilon*(1+c)` to `1-epsilon`.
The condition `epsilon*(1+c)<1` remains a geometric feasibility condition
for `K=o(ell)`. Its gap no longer has to exceed kappa. The conclusion
depends on the accepted original arbitrary-gap chunk interchange, compact
movement/layout/repair proof, phase inverse, finite primitives, and complete
conditional multiplication interfaces. It is not a formal verification of
a fixed-tape multiplication machine and does not claim novelty.

## Positional layout and actual movement

Set `n=ell-1` and `q=floor(n/K)>=1`. Write `n=qL+t`, `0<=t<q`.
Every axis has the same partition of these n common named bit slots into
t chunks of width L+1 and q-t chunks of width L. Since
`qK<=n<(q+1)K`, the supplied width of every chunk satisfies

```
K <= K_j < 2K.
```

This includes q=1, t=0 and K=1. Each long axis's one extra top slot is
moved to the prefix while preserving all other relative bit positions.
There are at most d-1 such moves. Ordering the remaining complete chunks
from axis-major to group-major takes at most `(d-1)q-1` transpositions.
The procedure permutes existing named slots and retains the polynomial
coefficient suffix; it introduces no new coordinate or padding volume.

An unequal transposition of adjacent widths L and L+1, with any gap,
uses one original single-bit move and one completed equal-width chunk
swap. For example, `a0 x M y -> x M a0 y -> y M a0 x` exchanges the
whole left block a0x and right block y. The other orientation is
`x M b0 y -> b0 x M y -> b0 y M x`. The bit move and the equal-width
swap may cross the spectator gap and preserve its order. Their inverses
in reverse chronological order restore all slots. Both operations use
the original interfaces, rather than a proposed new routing lemma.
The cost is O(V K^tau) per transposition, with V the current full volume.
Using `(d-1)ell=O(p)`, the total order/restoration cost is
O(V p K^(tau-1)); the extra top-bit cost is O(Vd).

## Uniform compact layer and complete fields

Within one common transform round, all participating chunks belong to
one group and have the *same supplied width* K_j. The round does not
mix different column widths. Its complete rectangular index set is
`[P] x [2^K_j]^(d-1) x [S]`. The selected bits have one common offset.
Both previous/following groups and the prefix are spectators.

The original compact theorem is written for `K=floor(d^c)`. Its proof
extends uniformly to `floor(d^c)<=K_j<2floor(d^c)` by reading K_j as a
supplied round parameter. All lower width tests, including the guard and
superlogarithmic condition, follow from K_j>=K. All upper tests have at
most a fixed factor two, and `(d-1)K_j<= (d-1)ell=O(p)`. The number of
reserved complete chunks, `ceil(2dG/K_j)+ceil(dG/K_j)`, only decreases
as the supplied width increases. The row-index chunks are still disjoint
from both front fields and the back field; every role contains the whole
within-row address space after cyclic row splitting. Scratch restoration,
pointwise alignment and deletion of completed padded zero rows are the
same as in [the independent compact review](review-compact-controls.md).
The graph dependency depth and scalar guard depend on the selected axes,
not on the number of unused bit slots in a chunk.

The positional map can be generated from the axis-length flags and
`n,q,L,t` without an arbitrary table of O(p) separately encoded names.
A current round header needs only the group index, width, offset and the
fixed complete-field lengths. Each such descriptor has O(p) bits. An
implementation may also construct an O(p log p) named-slot table on a
work band as polynomial setup; it need not treat that whole table as a
constant-field address descriptor. Both versions use a fixed number of
tapes and the existing superpolynomial polynomial-record suffix absorbs
the permitted polynomial setup. This avoids interpreting a change of
labels as an uncharged arbitrary global bit permutation.

## Fourier convention, precision and inverse

Process the extra top round on long axes individually, then all common
named levels `h=ell-2,...,0` in decreasing order. Slot `(i,h)` retains
frequency significance `a_i-1-h`, with a_i the actual long/short axis
bit width. At each forward round the lower named input bits form
`k_i=sum_(v<h) 2^v x_(i,v)` and the exact monomial exponent is

```
E = -sum_i (2r/2^(h+1)) b_i k_i mod 2r.
```

The changed physical order does not alter this arithmetic. In the
opposite chronology the lower named coordinates have already been
recovered before the inverse twiddle and current butterfly. The exact
operators are therefore `L_new B F^-` and `F^+ B^-1 L_new^-1` with
the original bit-reversal frequency convention. The pointwise polynomial
product uses this same L_new alignment, and the opposite transform returns
the old box order. There is no interface mismatch with convolution.

The individual top phase uses exact dyadic kernels on a grid finer by
at most d-1 bits, so precision p+d+O(1)=O(p) suffices before its one
final truncation. Every completed common layer retains the compact
guard/repair computation and one component truncation. The completed
butterfly tensor is a contraction, and signed monomials are isometries
that commute with component truncation. The inherited transform error
`<sqrt(2)ell 2^-p` and polynomial convolution error
`<M(3ell+1)2^-p` remain valid. Individual intermediate gates have not
been assumed to be contractions.

## Independent actual operator evidence

[review_balanced_transform.py](../code/review_balanced_transform.py)
imports no producer. It actually applies normalized polynomial
butterflies and negacyclic monomial factors using exact rational
coefficients, then compares outputs to the closed tensor Fourier formula
computed independently from original input and frequency indices. The
opposite computation must equal the original input divided by M; this
normalization reflects that both retained transforms divide by their
axis sizes.

[Run 20261008T015953Z](../runs/20261008T015953Z-review-balanced-operators/)
passes 38 shapes, 454 input basis columns and 114,180 exact polynomial
matrix entries. Tiny ell=2/3, one/two-axis boxes cover every basis column
and every long/short configuration. Larger ell=4/6 boxes use five
selected boundary columns per shape; ell=6 includes actual unequal
width-three/width-two groups. All opposite compositions are exact.
This is an operator control, not an exhaustive check of every larger
box or a tape-time measurement. Python 3.14.4 used one process,
1.71 seconds measured by time -v and 22,772 KiB peak RSS. The reservation
was released on completion. Source SHA256 is
`6a61623a5298bc6a8b259bbdc78f168c45ef36d1b4ab7f5ed41d84ba2d4ad4c6`;
certificate SHA256 is
`1717f030bf307e6b5aea86dc6f7290bd1f1c5f37de400e92c3ce8f541d7921a5`.

The producer's separate finite positional control covers 3800 shapes,
2,068,936 named axis-round checks and 1718 actual unequal-width
decompositions. These provide broader finite layout checks; the written
argument above establishes the all-size transfer.

## Scoped gain and limits

The remaining routing margin is `epsilon*a*c`, the compact layer margin
is `epsilon*q` with q<a, and the retained d separate CRT/resampling
exposures have margin `a*(1-epsilon)`. Thus this family has scoped
supremum a/2, compared with the earlier `a/(2+a)`. Even without the CRT
margin, the condition `epsilon*(1+c)<1` implies
`epsilon*a*c<a*(1-epsilon)`, giving the same bound. For b>4a the complex
guard has fixed headroom as c tends to one and epsilon tends to one-half.
The exact supremum difference is `a^2/[2*(2+a)]`, only about 2.5e-18
for the current promoted bit input. This is a small changed-layout gain.
It is neither a universal exponent ceiling nor a major new multiplication
bound by itself.

The tight parameter choice uses geometric backoff 2^-64. Its explicit
numeric condition `log2(b_input)>=3*2^64` is enormous, but finite and
legitimate for the asymptotic statement. The conservative choice has a
much smaller backoff-dependent cutoff. Both retain separate eventual
prime, strict-logarithm absorption and polynomial-record domination
thresholds. A new general routing hypothesis requires its own review;
it is not used by this balanced result.

## Independent composed arithmetic

[review_balanced_assembly.py](../code/review_balanced_assembly.py)
imports only previously independent reviewer count/logarithm routines.
It recomputes finite bit and complex counts, uses longer rational logarithm
enclosures to certify both chosen savings, and independently reconstructs
all 37 saved strict slacks, the guard constants, seven margins, selected
minimum, kappa rounding and six numeric cutoff obligations. It also ties
the saved bit/complex promotion metadata to the already accepted generic
compact review and checks every executed source hash. No producer is
imported and no large finite graph is replayed for this arithmetic check.

[Run 20261008T020903Z](../runs/20261008T020903Z-review-balanced-assembly473026/)
passes both conservative and tight R473026+h28 rows. The tight result is

```
kappa = 15911230743666875756818042088353 / 10^40.
```

Its common numeric log2(b_input) cutoff is 55340232221128654848; the
conservative row's cutoff is 15083685472. In both rows the old prefix
margin is strictly smaller than kappa. Thus the claim requires this changed
layout proof rather than tighter arithmetic applied to the preceding cost
bound. The only active exponent margin is the compact layer. The scoped
upper a/2 uses an independently certified upper enclosure of the bit
saving, and both strict witnesses lie below it.

The exact review used Python 3.14.4, one process, 0.12 seconds measured
by time -v and 23,352 KiB peak RSS. The reservation was released immediately
after completion. All inputs, executed versions, portable ordered commands
and compact output hashes are preserved in the run protocol. The compact
real-logarithm width test uses the repaired denominator `32L+192`, with
`ceil(log2(6b_input))<=L+4`; the explicit compact cutoff remains 577.
