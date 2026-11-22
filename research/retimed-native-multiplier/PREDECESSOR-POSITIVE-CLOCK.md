# Numerical native clock, with all input-dependent control work

Use the raw 128-factor positive word and physical service of #8030, with
either published numerical carrier M=2^610000 or M=2^1600000. #8035
uses the latter M with D=10^17 in the test e^D<=h. The 430-factor variant uses the same M with D=10^21.
Let B be a numerical upper bound on the ordinary bit service in the same
fixed-tape units, at ordinary rate a=κ+4g and g=1/D. This service must
include real payload, arbitrary exterior, its own installed data,
restoration and the full stop below its last rank. There is no observation
or arithmetic oracle in the calculation below. It uses the published
all-column, stable arithmetic and paid-port theorems. A numerical B still
needs a separate binary proof.

Use volume for a *physical* binary field in bits. Rewinding or traversing
M complete field intervals costs M times the actual field volume. Nothing
below charges a large real move to its smaller encoded offset.

## The field sizes available to control calculations

The public shape has s=ceil(log2(p+2)), and each active window has k=ell_i.
Set s'=(P+1).bit_length(), g0=4s'+6 and z=(s')². At an active parent of
selected width e>M, f=floor(e/M). The actual back position from entrance()
is start+z. That low suffix survives every native raw rotation, chart
and subsequent paid subcall. An active parent and each raw field created
by the row split preserve the complete first M f windows. The code checks
remain >= low+(e-e%M)k. Thus a raw field has at least 2^(z+M k)
records, including all exterior and holes. At stopped raw descendants the
suffix remains present. At an unnested stopped root, where the public
dispatcher instead sets the suffix to zero, the phase is addressed below.

Use J=M^1024. The source enumerates fewer than M^82 structural records
over all rounds, including omissions, the terminal/surplus slots and the
powered word. Even if the whole structural program is scanned on each
binding, the purely controlling part of *one active parent* costs less
than 2^120 J^30(p+2)^16:

* A fixed raw quartet of word/graph/port/chart identifiers and its
  positions may be reconstituted rather than indexed. Allow M^4 further
  structural reads per expanded record to select an entire M-entry
  coordinate tuple, find every port, construct its selected job and
  reverse all saved swaps. Each installed cursor read, including a
  seek back into the common image after a child, costs at most two full
  image sweeps. A map of loans, owners, slots and active cursors has at
  most M^82 entries. Even storing up to J scalar coordinates per entry,
  all such fixed tables take less than J^2(p+2)^4 cells. A reference to
  an actual data head has O(p+log J) bits; the original binary address
  has at most p bits and the field slot/cursor uses fewer than 1024 log2 M
  more. At an active parent s>=log2 M, so this is below 2048(p+2).
* Allocate two sequential rewrite tapes. For each indexed op mark a
  key, find all matching records and return the head. Even three complete
  nested searches per entry, with comparisons, arithmetic and copying
  charged as 2^20(p+2)^3 per scalar word (or as three corresponding
  scans of a full fixed key), fit the stated J^30 envelope. Offset
  normalization, decoding base-128 operands, capped binary powering for
  the D test, and cleanup use the same tapes. Computing all dynamic raw
  index lists takes at most (p+2)^4 visits per row. The cutoff D has
  at most 70 bits over these variants. Capped repeated squaring needs at most 69 squares and 29 further products for D=10^21; this fits in 2^7 elementary multiplications per test. These are once
  per active execution or once per physical row. Per-address functions
  are counted separately below, with their *entire* iteration.
* This absolute work is smaller than one actual row field. With
  H=log2 M, 30720H+120<M/2, by the two stated ranks. We also have
  16(s+1)+120<z/2 for s>=512. Thus a new full control build at every
  active parent, including per-parent generation dependent on p, costs
  less than one scan of its data. A program tape may be distinct from
  the data frame. No observation about the *number of bits in its head
  address* would suffice to pay a data-frame seek.

## One chart row on arbitrary data

The installed forms have fixed reduced scalar magnitudes at most 87 bits.
Each numerator uses at most four 23-bit limbs and denominators split
into at most 87 divisors below 2^24. For a fixed divisor, long division
scans the value in high-to-low order, maintaining its at-most-24-bit
remainder. Each input bit costs at most 2^9 moves, with sign, output
and head restoration. Schoolbook accumulation by a 23-bit constant
takes at most 23 shifts/additions. Thus even 2^25 times one field volume
suffices for a scalar update. The coefficient and its divisor list are
determined once when the row is issued and copied to fixed working tapes.
The source removes the odd factor and the residual shifts on return.

An actual ROW/NOT of c columns distributes at most c f selected
positions, where c<=M. Each address and relative bit index has fewer
than p+2 bits. A whole coefficient evaluation for a phase, carry,
bad-set check or inverse key costs at most

    2^80(p+2)^8

bit transitions. There are at most p indices (they are distinct
positions in a field of at most p bits), at most 22 forward or inverse
operator pieces, a bounded number of field-word shifts per position,
and at most p saved positions. Even a sequential re-scan of every saved
position per term followed by a full p-bit addition/shift, plus the
loop controls, is below this bound. No variable-width position is
read for free. Field.phase computes once per complete z-bit suffix;
Field.rotate computes once per 2^(lo+width) records with lo>=z.
Columns.repair also computes its decision and key once per complete
suffix, restoring every item after sorting. The bound above is less
than 2^(z-4) from s=512. Each whole group pays for its own evaluation.
The final single column selects a true bit >=z; its high/low swap uses
the physical ordinary service.

For the exceptional subset, for n=c f-1 selected positions two all-one
g0-bit digits and two extreme subranges in a (k-1)-bit guard give
probability at most n(2·2^-g0+2^(g0+3-k)). This is at most 3p·2^-g0
since k>=128g0 and n<=p. No independence is used. There are fewer than
p radix passes over the bad groups. Even with a complete p-bit key
and all its data, these cost fewer than a fixed number of full scans:
3p²2^-g0<1, and the suffix group holds more bits than the key. The
algorithm's two incoming streams, stable radix banks, restoration,
lifetime and clearing are those of compact_columns.py.

One compact row has at most 22 raw shuttles/rotations, plus those of
the high single column and one radix repair. Each genuinely swapped
address width is at most 1+M f k, including raw slot alignment and
unalignment (which use f k). If the row volume is v0, the ordinary
tariff on these moves is at most

    2^8 B v0 M (1+k)(1+f)^(1-a).

The inequality 1+M f k <= M(1+k)(1+f) bounds its actual width.
There is an independent copy/clear/rewind charge per operator and
separate physical travel to each owner.

## Number of physical moves and maximum travel

Let v be the incoming parent volume after the common fixed-grid widening
and R0 the number of independent parent output rows. A raw field in the
new local frame then has volume v/R0. The source proves
R0<60M^96 and a local slot count at most F R0 with

    F=2^19 Q_128²(G+1),  log2 Q_128<=3912,  G+1<=H+2.

At both ranks 60F<M. Therefore a maximal seek *within the newly
active frame* costs at most Fv<Mv. A return transfer, an unexpanded
terminal, or an individual residual that still accesses the caller's
frame can traverse fewer than F R0<M^97 intervals of its own width.
This distinction is necessary for a paid leaf on one owner's full
row. The program stages donors before interleaving output, so an
affine sum visits a bounded number of owner slots per full scalar
or row operation. Temporary file rewinds/shifts operate on the
sequential scratch and cost the extent traversed. A child enters past
the immediate caller and returns before the parent resumes. Its old
high-water and the saved parent interval are counted at these two
transfers. No callback repeatedly seeks through more remote ancestors.

There are fewer than M^82 structural records in one parent, including
complete rounds and the powered-word expansion. For an independent
overestimate allow each one to invoke an entire unpowered 48-call raw
program. Regenerating the actual positive word found 48 graph calls,
323573 donor terms, 6965 scheduled nodes, 5674 moves, 1291 initial
values, and at most 84 local instructions in one chart. Counting the
driver and 32 chart passes per node gives 1996901824 visits before
slot alignment. The finite census is reproduced by positive_counts.py.
Using a bound 2^60 before slot alignment, one raw program needs at
most 2^60(M+1) elementary field or chart ops since each alignment
inspects at most M canonical slots, with forward/return exposure.
Count 2^62(M+1) to include the owner clears and copies. Thus there
are fewer than M^84 physical operations per active parent. The
M^84 bound counts native fixed rows; it does not count recursive
paid job bodies. Those are priced by their actual normalized
multiplicity below. Using the larger parent volume v to price every
row is already an overestimate. The M factor from a full frame seek,
the M in the genuine ordinary tariff, and 2^25 scalar scan constants
still fit below M^89. The once-per-parent control bill also fits.

Before entering the child there can be fewer than M individual
residual axes. Each has full local prologue, pair arithmetic, routing,
scrub, and return. An individual axis on an inherited frame costs at
most 2^40 M^97 times its own actual volume: every bucket is a real
independent complete field; the saved first half and return use
sequential banks, and a fixed number of original-frame visits suffice.
These terms and both frame transfers fit M^99 v. The unnested public
stop has no grouped suffix. Its two public phases can compute the exact
population count (or its used low two bits) on each p-bit address in
linear time, using a low-end binary increment with amortized carry.
Each full Gaussian word already has Ω(p) bits. Its single top-level
integer mask costs at most 2^24(p+2)^4 once per spectator slice. Thus
even this case costs at most 2^40 per word length and active axis,
before the separate gather, scatter and restoration charges.

## Sum on the actual tree

Write b+=κ+5g; the normalized mass of issued paid leaves is at most
M^(1-b+) per fresh parent by the actual funded port price. The
independent sizes of child data are their parent's true size divided
by R0. At depth j, e_j=floor(h/M^j), and the total entering volume
is at most v M^((1-b+)j). Active work other than paid children is
bounded by

    M^99 v (1+B)(1+k)(1+floor(e_j/M))^(1-a)

per parent, with v replaced by that parent's volume. At active depths
f>=1. Use (1+f)^(1-a)<=2(h/M^(j+1))^(1-a). The power of M left
in a depth sum is M^((a-b+)j)<=1. The pure scan and residual costs
are at most M^99 v h^(1-b+) at each active depth. There are at most
s+2 depths. For a stopped child,

    M^((1-b+)j) e_j <= M^b+ h^(1-b++g b+).

This follows from e_j<=max(M,h^g) and M^j<=h/e_j. Since
(1-g)b+>a, the h power is at most 1-a. The M^b+ factor is covered
even after the 2^40 M^97 charge on a worst-positioned individual
terminal axis. The actual field has the same working precision at
every such yield. In total the complete inner positive call, including
its own residuals, native construction, scalar sweeps and data motion,
has a fixed constant

    Z <= M^100(1+B)

in front of (s+1)^2 · v · (1+h)^(1-a). Here k<=1030(s+1) and the
slack between each per-depth bound and M^100 covers all the displayed
numerical factors. The numerical publication prologue widens each
component by at most 2h+48 extra bits, with h<=p and the public grid
already P>=p. Its fixed increase in v belongs to the outer assembly.
Both actual support placement swaps at width h k are separately
charged to B at the top. No iteration requires h^g>=M.

Combining this with OUTER-CLOCK.md gives a bound

    C <= 2^(134217728) + 2^1436 M^100 (1+B)

for the complete signed product **conditional on a numerical B for the
actual physical six-stage ordinary service and the source correctness
premises**. This does not give a numerical whole-product C by itself.
The positive fixed factor alone has log2 no greater than 61000000 or
160000000 (plus the displayed outer absorptions). The proof gives
upper certificates, not a minimum factor or a measured crossover.

OuterTickets.lean checks the active depth inequality, stopped depth
inequality and both integer quotient statements against Lean's real-power
and natural division definitions. It also checks the all-size polynomial
private cutoff and the two binary-exponent absorptions. The linked program
establishes the event and volume hypotheses in the written arguments.
The local Lean 4.34.1 kernel replay accepted all seven declarations with
only propext, Classical.choice and Quot.sound; the two divisor statements
use only propext.

## Source bindings

* [Full generated epoch and resumed positions](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/epoch_tape.py)
* [M^82 record count and paid rate](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/BAND.md)
* [Physical row split and jobs](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/band_positive.py)
* [Absolute slot and order bounds](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/ACTIVATION-SPACE.md)
* [Fixed graph, rational scalar and representable width](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/STRONG-COMPLEX.md)
* [Serving public and stopped H](https://github.com/CrocSwap/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/positive_dispatch.py)
* [Actual positive placement and retained suffix](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/complex_stage.py)
* [Ordered ops, subset guard and repair](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/compact_columns.py)
* [Raw chart, align and inverse](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/raw48.py)
* [Staged owners, physical seeks, scalar division and pair phases](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/spool.py)
* [Updated signed margins](https://github.com/CrocSwap/integer-mult-bounds/blob/ea776471bf8ed143a0625cf2d7532f65d15eb5f9/research/p104-single-band-signed-margin/PROOF.md)
