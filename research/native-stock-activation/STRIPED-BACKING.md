# Auxiliary backing at the same input length

Let `n` be the input length, `p = 6 ceil(log₂ n)`, `s = ceil(log₂(p+2))`,
and `V = Θ(n)` the bit volume of the mutable full numerical field. The
two adjacent axis widths in the outer construction are at least `64s²`.
Use `K = 2^floor(s/2)`. Thus `K = Θ(√p)`. The three complete CRTs and
every top numerical Hadamard pack can share sequential work arenas of
`O_F(V/K) + 2^O(s²)` bits beyond their caller-owned fields. The subscript
permits the same fixed native-program coefficients. All numerical words,
independent row values, positions, padding and required outputs still
exist. The result concerns the additional tapes that execute the moves
and transforms. The input, the retained forward spectrum and the current
signed complex field remain live on their own tapes. The complete machine
still uses `O_F(n)` bits. Its multiplication exponent is unchanged.

## One writable tape interval

Consider a complete tape with `Q` records, each of width `R`. A permutation
of the record addresses is independent of the data in those records.
Divide `R` into `k ≤ R` positive consecutive stripes whose lengths differ
by at most one. Take the stripes in increasing order. For each stripe,
scan the original bank, copy those cells of every record in source order,
and rewind. Run the complete service with every genuine address and the
shorter records. Rewind the result and scan the original bank again.
Overwrite only this stripe in every record with the returned cells.
Rewind and clear the two small streams. All intervals outside the writable
bank, including other live operands and the caller's prefix, are preserved.
The bank head returns to its entry marker. The native service finishes
before the next stripe starts.

For a destination address `j`, all its slices receive exactly the data
from `π⁻¹(j)`. Older slices are disjoint from all future reads. This proof
allows arbitrary correlated payloads on different records. It does not
rely on their values being sparse, equal or separable. It also works when
the complete service performs pointwise XOR internally. Each run retains
the whole set of source addresses. All of its high and low configurations,
owners, parent returns, temporarily singular low matrices and padding
have the existing full placement on that run. A non-destructive caller
first copies its original input to the mandatory output bank, then uses
the same in-place schedule there. That contract keeps both banks live.

The two public scans and their rewinds move `O(kV)` cells in total. The
sum of all native bit volumes equals `V`; a stripe occupies at most `2V/k`.
Private per-call control data and installed machinery have their own
bounds. Reuse the same scratch tapes and entry markers at each invocation
from the beginning of execution. Their historical maximum then obeys the
same bound as an individual live maximum. A previously visited larger
scratch tape cannot be made historically smaller by erasing it later.

The public ordinary ABI uses `k = min(R, max(1, floor(√e)))`, where both
real fields have width `e`. The full interchange cost remains
`O_F(V(1+e^(1-b)))` since the source has `b < 1/2`. The byte ABI uses
byte extents throughout. The bit ABI reads a stripe with any bit offset,
provides at most seven temporary zero bits per record, then merges the
changed bits back without changing either boundary octet's neighbors.
Packing changes subcall volume by at most a factor of eight. The bit-tape
machine can use exact cell extents. At least one bit per record remains
in every run. The complete ordinary backend's width, padding bounds,
recurring degree, six genuine reservations and their activation conditions
therefore retain their original values. The source's stack of small
descriptors and its fixed installation remain separately charged.

## Every numerical H pack

A top pack acts on one selected bit in each of `h ≤ d/(1024s)` axes of
the complete `L`-bit rectangular address. Choose one entirely unselected
axis and take `r = floor(s/2)` consecutive high bits from it. The axis
has room since its length is at least `64s²`. In chronological physical
order the whole bank has the form `[P][2^r][Q][complete numerical word]`.
The implementation extracts each complete `[P][Q][word]` in sequential
order and writes its changed words back into that same slice. Its output
has all complex integer and fractional bits. Let `j` be the physical
position of any selected original bit. It retains position `j` if it is
below the deleted field, and otherwise takes position `j-r`. No selected
window meets the deleted bits. On the packed tensor the address length
is `L' = L-r`, while `h`, the common numerical precision and all selected
window widths retain their values. Fixed bits of the deleted field have
no effect on `H_selected`. After the last stripe the next diagonal can
use every original address bit again.

The actual numerical entry moves one contiguous block of `h` whole axes,
each of width `ell`, to a disjoint region. On the stated tail `s ≥ 512`,
`L ≥ 64ds²`, `L' ≥ L/2`, `s' ≤ s+20 ≤ 2s`, `G ≤ 6s`, `ell ≤ 128s²`.
Put `B=h ell`. The input has a left and a right exterior. Their larger
length is at least `(L'-B)/2`. The required contiguous exterior extent is
`B+3hG+(s')²+rowbits`. Here `B ≤ L/(512s)` and `3hG ≤ 18d/1024`.
At native entry `M ≤ h ≤ d ≤ p` gives `log₂ M ≤ s`. The true complex
stock then needs `rowbits ≤ 448(3 log₂ M+s+1) ≤ 1800s ≤ 4s²`.
Thus the required extent is less than `L/7`, while `(L'-B)/2 > L/5`.
Place the grouped suffix, back control, numerical body, two front controls
and full leading row stock there. The one whole-block ordinary exchange
and its final inverse each pay their actual width `B`. At every nested
column placement, the width is the number of moved complete columns
times `ell`. Replacing a window of width `128G` by the whole original
width adds at most a polynomial in `s` to these prices. The six ordinary
stages and numerical rank thresholds survive. The entire recursive
call on the stripe, with all pending banks and all native scalars,
uses `1/K` of the old volume up to the previously charged fixed factors.
Any arithmetic or rounded output agrees stripe by stripe on the original
addresses. See `INTEGRATION.md` for the actual relocation and its cost.
This argument freezes only `r` bits of a genuinely unselected axis. A
single fixed-label microbox can violate the two displayed inequalities.
Splitting a numerical word into independent bit planes at an H is also
invalid. For example, adding the two words `1` and `1` carries to the
next bit. Splitting a selected address bit would separate a required
Hadamard pair.
[Complete window, suffix, reservations and their placement](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md)
· [Native all-column contract](https://github.com/CrocSwap/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/COMPLEX-LAYER.md)

The sum of native work on all stripes has the original bound. The extra
scans cost `O(KV)` per H. The new outer packs have only a polynomial in
`s` actual H stages, including the width classes, split packs, two root
passes and the fixed sixteen-H lowering. Thus these scans cost at most
`O(V√p poly(s))` across each complete direct Fourier transform. This is
within the complete budget even for a short pack. The larger cap `J`
used to certify roundoff is a separate bound. Each coordinate receives
the original chronological arithmetic at the same precision. Changing
the order between independent spectator slices introduces no new local
error, scale change or truncation.

## The three CRTs

A CRT changes record addresses across the full tensor. An individual CRT
target axis can change even at a fixed source label. On sides `(3,5)`,
the record at `(1,0)` moves to `(1,2)` in the forward map. Keep all
address axes, and instead partition the `R=Θ(p)`-bit opaque records
into `K` chunks. Their widths are `Θ(√p)`. Perform one full CRT for
each chunk. It applies the same address map to every input, including
dirty holes. The final return reassembles each complete numeric or
integer record before the next arithmetic operation or carry.

For each balanced level, switch row and color, let `T=2^L` be the full
address count. The original dense guard detector scans `O(L)` control
bits per address. Here this can exceed a stripe's word size, so charge
`O(K T L)=O(KV)` across its stripes. All expensive ordinary shuttles
retain their real `H₀`-bit fields and full dirty reservoirs. Their
aggregate volume and native cost stay fixed up to packing constants.
The original non-tail data preparation costs at most `E/2^H₀` per
address, and the exceptional density is `O(p 2^-G₀)`. The control bound
`E ≤ C 2^(4ℓ)(p+2)^16` with `G₀ = 64(ℓ+s)` gives bounded preparation
per address even with one-bit records. The thin stream still has the
complete address fibre of size `2^H₀`. Sparse keys have `O(p)` bits,
so all keys take `O(T p² 2^-G₀) = O(T)` bits. The one-bit hole stream
also fits a stripe. Any extra linear-time operation costed per long word
in the predecessor may be charged `O(V)` for each stripe. The number
of balanced levels, batches, colors and switch rows for the thin square
geometry is polynomial in `s`. This adds at most `O(V√p poly(s))`
to the three CRTs. Dense controls, pointer travel, sparse repair, old
head positions and cleanup are included. The data-dependent evaluations
have at most `2^O(s²)` private cells.
[Dense guard and separate sparse charge](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/unconditional-batched-crt/CRT.md)
· [Physical geometry and complete product costs](https://github.com/CrocSwap/integer-mult-bounds/blob/3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd/research/direct-circulant-fourier/COMPOSITE-OUTER.md)

The unchanged entry and exit diagonals, mixed-radix odometer, pointwise
short products, conversion and carry each use a scan on the assigned
full field and private word or control workspace. They need no spare
copy of its full numerical tensor. The two main numerical fields use
their own separately counted tapes. A copy required by a non-destructive
caller remains charged there. The old named receiver constructs an entire
new ternary-padded field by copying the input rectangle at a genuine
public binary shuttle. On the common cofinal input tail the unchanged
old CRT has such a shuttle. Its additional materialized field is at
least `Ω(Tp)` bits. For the same `n`, the chosen old and new controllers
have the same `T=2^L` and both have word size `Θ(p)`. The specified new
extra backing beyond those persistent fields is `O_F(Tp/√p)+2^O(s²)`.
The latter private term is `o(n/√p)` since `p=6 ceil(log₂ n)`.
The fixed finite installation also remains. This is an asymptotic
comparison with the two specified schedules. The stripe method itself
can also be applied to an old caller with the required complete contracts.
The whole original operands and their product continue to occupy linear
space. The binary tape endpoint reads each input extent once to find its
significant length and restores the input head. It converts the same
little-endian bytes directly into radix digits. Its carry loop emits the
canonical result to the output owner. It postpones runs of zero octets
with a counter, so no full binary array is needed between the numerical
bank and the destination. A zero result occupies one zero octet and has
positive sign. The transient input and carry buffers take `O(p)` bits
beyond a fixed transfer block. Leading padding adds a linear scan in its
declared length. The Python integer adapter owns materialized input and
output byte strings. The finite stopped scalar path can also materialize its
operands. The reduced auxiliary theorem is for the fast tape endpoint.
[Old binary padding copy and held layouts](https://github.com/CrocSwap/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/ORDINARY.md)

## Park the first forward result at its returned precision

Let `P` be the fractional working precision. The retained Python
`public` routine truncates a component, then shifts the integer back
left by `P-p` bits. A represented output is therefore `k·2^(P-p)`
in the working format. Park the signed integer `k` while the second
transform runs. The completed forward has exact radius at most `1/4`
and public error at most `3·2^-p`. Thus every stored component fits
in `p+1` signed bits. Zero holes fit the same fixed format. If real
and imaginary components are supplied as `a,b,c,d` in public units,
form the two integers `ac-bd` and `ad+bc`. Divide each toward zero by
`2^p`. Shifting the quotient left by `P-p` on entry to the opposite
transform gives exactly the former `public_product` value. Indeed its
input product carried a factor `2^(2(P-p))`, and its divisor before
the final shift was `2^(2P-p)`. This conversion introduces no new
rounding step and returns arbitrary legal positive or negative components.

The physical working precision satisfies `P ≥ 4p+32768L` and
`L ≥ p/12`. Hence `P ≥ (8204/3)p`. On the stated large-input range,
the ratio `P/(p+1)` exceeds 2700, even with a byte-rounded compact
word. This comparison is per fixed-width component of the one
parked spectrum. A nonzero Python working-grid integer also has at
least `P-p+1` value bits. The storage of an actual Python `int`
varies with its value, and its zero does not occupy `P` bits. The
published predecessor already allowed a public `p`-bit result. This
implementation realizes that representation instead of retaining the
left-shifted integers. One wide work field still serves the second
and opposite transforms. These figures do not give a 2700-fold
reduction in total peak memory.
[Retained public conversion and pointwise product](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/retained/fourier/product.py)
· [Two independent public-grid inputs](https://github.com/CrocSwap/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/RECOVERY-AND-COST.md)

## Verification boundaries

The Lean file `Slices.lean` proves the in-place traversal for arbitrary
dependent payload types. It proves a genuine address permutation on
every ordinal stripe and the actual signed sum/difference word on the
unpartitioned address cube after a complete traversal of the spectator
cube. The amplitudes can be correlated across any addresses. Its
signed integer identity also proves that storing the first spectrum on
the public grid gives the same complex product after truncation. The tape/counter bounds,
window and reserve inequalities, all-size analytic accuracy and their
source-to-executable bindings use the given written proofs.

The width-matched physical comparison uses the same 25,509,168 distinct
four-byte records and changes each at its true intermediate destination.
At 81 fixed stripes the 102,036,672-byte data bank remains present.
Per direction the old scalar right route used 618,597,324 total logical
tape bytes (516,560,652 beyond the input). The striped split route
used 109,673,676 (7,637,004 beyond the input). It read 1,855,791,972
bytes, wrote 3,609,547,272 and repositioned its heads by 38,117,074,284 byte
positions. The old figures were 2,910,170,916, 5,718,305,160 and
8,424,402,732. The unchanged output hash of the independently modified
record stream is in `PRODUCT-CHECK.md`. Counting reads, writes and those explicit seeks, linear tape travel is 17,052,878,808 versus 43,582,413,528 byte positions (2.56 times). This fixed 81-stripe stress case and the growing public width
rule have different stripe counts at a two-trit fixture.

The byte and packed-bit ordinary ABI was tested on 40 cases,
including dirty prefix and suffix bytes, nonradix gaps, restored
heads, unaligned bits and a bounded tape owner with absolute seeks. A
384-working-bit `(3,5)` product used two
genuine byte stripes during each of its six numerical data placements.
There are 21 independent signed tape comparisons for spectator H packs.
The full 136-bit diagnostic product used 24 complete CRT stripes, and
all 157,248 numerical H calls used spectator slices (125,496 with four
and 31,752 with eight). All three normalized numerical paths, both
inputs, public pointwise product, rounding and carry returned
`345550037539`. These finite checks use small carriers and the retained
individual H arithmetic. They do not measure elapsed time or global
historical backing at the cofinal native activation threshold.
