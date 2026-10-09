# Bulk resampling layout and fixed-tape transfer

This is the full tape schedule proposed for the local principal-window
construction in [the analytic report](downstream-microbox-resampling.md).
It is a new mathematical argument under independent review. Its local
inverse error and page-size bounds depend on that separate analytic
argument, and its constant number of large layout changes depends on
[the arbitrary-source router](compact-arbitrary-source-routing.md).
No new multiplication exponent is promoted here.

Retain the original d-1 tensor axes, denoted D below, source sizes s_i,
dyadic target sizes t_i, rho_i=t_i/s_i and T=product(t_i). The existing
capacity proof gives T/S<2 and 1/(4d)<rho_i-1<1/(2d-1).
Take L=2^ceil(8 log2 p), A=4096p^3. For eventual p each t_i is divisible
by L, each s_i>2(L+2A+2w), and L>=64dA. D<=p. These are polynomial
thresholds against exponentially growing axis sizes, not new assumptions
on input splitting. Let Q_i=t_i/L.

## Small complete-field moves across arbitrary spectators

The exact rectangular transpose
`[B] x [2] x [R] -> [2] x [B] x [R]` costs linear full bit volume.
Scan each complete R-block in order, send the zero/one block to two
work tapes and concatenate the tapes. For the inverse copy the two
B*R halves and interleave their complete R-blocks. An external prefix
of any positive cardinality is processed fiber by fiber with the same
tapes. Moving heads back across each work fiber costs its volume and
is included; no random seek or per-payload address arithmetic is free.
The original amortized block counters and parameter setup apply.

Move a k-bit field across B by doing this first for its most significant
bit, then for the next bit inside each preceding-bit fiber. This preserves
the field's internal binary significance and B's order. Total cost is
O(kV). The inverse uses the reverse chronology. B can include arbitrary
coarse and mixed-radix inner fields. Thus one O(log p)-bit local field can
be moved adjacent to its corresponding coarse field, or to the line suffix,
without moving any large coarse field itself.

For a field of length M<=poly(p), first insert zeros to extend only THAT
field to2^ceil(log2 M), at a factor below two. Apply the small-field move
and delete its padded zeros at the destination. The inverse uses the same
procedure with the current field length. If a line map changes its length,
the return is the appropriate mixed-radix transpose for the new length,
rather than an incorrect inversion of the old binary names. No stage pads
all D halo fields to2L. Constant temporary factors per call are removed
before the next axis, and a fixed set of tapes is reused.

## Monotone halo streams with bounded buffers

Consider one increasing periodic source row of s complete R-blocks. Its
desired windows are intervals I_k=[a_k,b_k), with increasing starts and
ends, covering consecutive cores. Every core has length at least L/2-1,
and each halo has at most A+4 records on each side. Thus consecutive
windows overlap by O(A) records and nonadjacent windows are disjoint,
including the cyclic interpretation. All endpoints have O(p) bits.

Produce an extended periodic row by retaining a head and tail of A+4
records and making the bounded forward/backward scans needed to prepend
the tail and append the head. One can first inspect a complete current
prefix fiber, retain its tail, move the source head back across that SAME
fiber and then process it forward. Its three scans cost O(sR), not a
scan from the beginning of the entire tensor. Reuse the work tapes for
the next prefix fiber. No input original is overwritten.

For I_0 read its complete window and write it. While writing, mirror only
the last segment [a_1,b_0) into an overlap tape. For I_1 first write this
saved overlap, then consume new records [b_0,b_1) from the extended source.
Mirror its last segment [a_2,b_1) into the OTHER overlap tape. Continue
with two alternating overlap tapes. Core length>2(A+4) ensures the next
saved tail is in the newly read portion, so no FIFO shifting or repeated
whole-window reads occur. Exact variable overlap endpoints are permitted.
Resetting overlap heads costs O(AR) per window, already bounded by the
output traffic. The source is read monotonically after its initial bounded
scans, every written payload is copied only a fixed number of times, and
total work is O(input volume+output volume), plus polynomial endpoint
arithmetic per complete window.

Zero padding and final cropping are ordered stream operations. Window
descriptors are read once per complete R-block or window, rather than once
per payload bit. In the applications below R includes all the other inner
fields, hence at least L^(D-1) coefficient records. This is superpolynomial
in p for every fixed epsilon>0. Polynomial setup/boundary calculations are
therefore absorbed. Fixed known head/tail or axis-padding scans also use
the original amortized counters when their suffix is shorter.

## Expansion from the prime box

Embed each source axis s_i into its retained dyadic t_i by writing zeros
after its last physical coordinate. Successive embeddings have volume at
most T<2S and cost O(TpD) with O(p)-bit coefficient records. They are
simple fixed-cut stream padding, with no computed record sort.

One large coordinate permutation now gathers all low log2 L bits into
an inner suffix, with coarse fields k_0,...,k_(D-1) in their original
order. This padded box is complete and binary. The reviewed router's
spectator construction applies at its actual short coefficient-record
width; its cost is O(Tp*p^tau*polylog p) plus polynomial setup.

For axis i, move only its inner log2 L-bit field adjacent to its coarse
field. This exposes global source index j before a complete spectator
suffix. Discard the pre-existing j>=s_i zeros while reading. Define
`J_k=[floor(kL/rho_i),floor((k+1)L/rho_i))`. They exactly partition
[0,s_i); Q_i*L=t_i. The analytic report defines monotone source windows
I_k by the global q_j selection, each containing J_k and its generous
halo. Use the monotone stream algorithm to copy I_k, pad it to L and
return that short local field to the inner suffix. The source window fits
L because the near-one size ratio supplies at least L/(8d)-1 spare slots.
This is actual near-one source padding, not rounding each source interval
up to twice its length. After every axis the padded volume is exactly T.

Inside each complete microbox, expose one short field at the line suffix,
apply the accepted normalized blocked Gaussian expansion to its source
window and keep the L target CORE rows. Return the short field. The map
uses the original global s_i,t_i and phases, including modulo-s_i source
indices; padded source slots are zeros. It uses the accepted short-block
chirp computation, never a long-L chirp with uncontrolled exponential
weights. A target core depends only on its supplied source window up to
the accepted Gaussian tail error. Successive axes are tensor operations,
so already transformed cores need no halo refresh in other axes.

## Compression and exact final assembly

The normalized target tensor is again in the binary microbox layout.
Before any local inverse, make one ordered halo pass per axis. Move the
short inner field adjacent to its coarse field, emit
`[kL-A,(k+1)L+A)` periodically, and return that current field using the
small mixed-radix transpose. Its persistent length is M=L+2A. All partial
halo tensors have volume at most
`T*(1+2A/L)^D <= T*exp(2DA/L) < 2T`. Individual records can belong to
many tensor halos, but the PRODUCT of the exact one-axis output volumes
is bounded here; a2^D worst-case multiplicity is not used as total volume.

For axis i expose its current polynomial-width local field. Apply the
principal inverse of the SAME global structured H on I_k, the original
local C selection and D normalization, and keep only the J_k source-core
rows. Pad those core rows to L and return the new short field. Other axes
still retain their own target halos. The separable tensor product identity
proves that early core cropping in a completed axis discards no input
needed by a later DIFFERENT axis. The analytic locality, contraction,
rounding and error estimates apply; there is no global halo refresh.

The local factor page is indexed by k_i, already in the original outer
order `[A_prefix] x [k_i] x [B_suffix]`. Sequentially scan the increasing
k_i catalogue once per A_prefix, retain the current page and reuse it
across B_suffix and all inner lines. Rewind the catalogue for the next
A_prefix. Its retained page has
O((L+L*w^2/d+w^2)*p) bits. Page traffic per inner line is charged to the
accepted solve cost. Whole-page traffic and polynomial setup per
(A_prefix,k_i) are absorbed by the complete inner microbox volume.
No large k_i permutation or random catalogue access is used.

Intersect windows with the ORIGINAL globally fixed phase cells. In
particular preserve the physical period cut when lifting a wrapping
window: first/last global cells must not be merged by unwrapped phase
names. Cross-cut entries remain the same global H entries. This adds
only O(w) boundary vertices and keeps the stated principal solver cost.
The complement-gap condition makes the principal window genuinely
noncyclic; |I_k|<s_i alone would not suffice.

After all axes, use small-field moves to concatenate the retained J_k
cores into the original increasing j<s_i order, append zeros through t_i
and return the log2 L-bit field to the suffix. This costs O(TpD polylog p).
One inverse large coordinate permutation returns the dyadic axis-major
layout. Remove j>=s_i zeros by the same fixed-cut scans as the initial
embedding. The result is the original prime box, with its original
normalization and tensor row order. Input identities, Fourier convention,
Gaussian scalar gamma and the subsequent CRT map are unchanged.

## Complete cost and promotion boundary

Across each scalar expansion/compression there are a constant number of
large router calls, O(D) short-field/halo/crop passes and the accepted
local arithmetic. Including factor traffic, source padding and artificial
boundary terms gives

```
O(Tp*[p^tau*polylog(p) + d*polylog(p)
      + d*p^delta + w^2*p^delta + d*w^2*p^delta/L])
+ polynomial(t,p) setup.
```

Here w^2=O(p^(1-r)), L>=p^8, d=p^epsilon. The setup is n^o(1) under
the retained axis-size relation and is amortized exactly as in the accepted
phase proof. Reused tapes and temporary padding have constant-factor
volume. The numerical maps are the same normalized analytic maps with
the retained tensor error bound; no exact multiplication machine or
unconditional theorem is supplied.

The old d separate full-width axis exposures can therefore be replaced
by one full routing scale and short local exposures, IF this complete
schedule and its analytic dependencies receive positive independent
review. Their movement margin would be a instead of a*(1-epsilon).
The Gaussian margins, complex layer exponent, coefficient precision,
recurrence stopping, prime capacity and every final assembly condition
must still be recomputed. Hypothetical arithmetic certificates alone
cannot promote that end-to-end result. The independent mixed-radix/
stream controls being developed by the independent critical reviewer supplement this
argument; they do not substitute for the written fixed-tape proof.
