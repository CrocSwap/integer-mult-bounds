# A complete sparse transport/consumer/return interface

## 1. Result and hypotheses

This note composes the separately pinned
[first-face tape transport](../sparse-halo-tape-transaction/PROOF.md) and
[shrinking-reference halo consumer](../shrinking-reference-halo/PROOF.md).
The composition itself is the result: a sorted saved stream enters the
consumer without host regrouping; its output returns to exactly the dense
boundary coordinates; every codec operation and its storage are priced.
The retained #4100 first-face geometry and #6880 numerical splice are
predecessor mechanisms, not new claims here.

Let `L=2^ell`, `N_i=2^(k_i+ell)`, `k_i>=1`, `L>4A`, and `0<=b<A`.
There are `g` active axes and an optional complete binary spectator prefix.
For each axis fix one real periodic reference matrix `H_i=I-E_i`, where
`E_i` has cyclic half-bandwidth `W_i` and `||E_i||_infty<=1-delta_i`, with
`0<delta_i<=1`. All numerical pages and comparisons refer to this same
matrix; independently rounded windows are not permitted. Identity-hole
rows and period cuts are allowed.

The numerical plans have `J_i>=1`, `b_i=(J_i-1)W_i<=b`, a common grid
`2^-q`, radius `R`, and dyadic normalizers `a_i=2^u_i` satisfying
`a_i delta_i>=1` and `q>=u_i`. The incoming dense values are exactly on that
grid and have component-l1 radius at most R. Their two sign-magnitude
components have the consumer's exact width `q+R.bit_length()+1`; the
transport payload is their concatenation, of width P. There is no free
precision conversion at the interface. A finer common grid may be supplied
before entry, with that caller work and radius accounted separately.

For target intervals of lengths `m_i`, each consumer rectangle is the
expansion by `b_i`. The transport may save the larger common-b expansion.
Both expanded lengths are below `N_i`, because `L+2b<2L<=N_i`.
Thus each local offset has one unambiguous periodic coordinate. The
canonical input layout and dyadic descriptor remain transport premises.

**Composed interface theorem.** Under these hypotheses and the two pinned
component theorems, the sequential codec in `join.py` preserves the exact
saved incoming numerical values and gives every discarded target exactly
the value produced by the consumer's global-reference rounded recurrence.
It preserves the current dense core value at every kept coordinate. The
complete movement and scalar-macro bill is the one in Section 5. This is
not an unconditional multiplication theorem: an actual same-reference
numerical core and the outer caller still require their own admission.

## 2. Rectangle grouping, crop, and exact input identity

For core c, first face f and side s, let the target local intervals be

```text
i < f: [A,L-A)
i = f: [0,A) or [L-A,L)
i > f: [0,L).
```

Write their lower endpoints and lengths as `lo_i,m_i`, and absolute target
lower endpoints as `t_i=c_i L+lo_i`. The transport sorts complete keys

```text
spectator || core fields || one-hot face || side
          || common-b expanded local offsets || canonical source address.
```

All fields have fixed declared widths. Hence a rectangle is a contiguous
stream block, ordered lexicographically by its local offsets. A source
address is redundant after the full offset tuple because the expanded
intervals have no periodic aliases. One-hot binary ordering may place
larger face indices earlier; the codec requires contiguous grouping, not
increasing numerical face index.

`Codec.run` reads the next prefix through actual transport tape reads and
unit moves. If it differs from the current prefix, the previous rectangle
is consumed and cleared before the new descriptor is constructed. Strictly
increasing prefixes are checked. No dictionary, indexed payload lookup,
array of rectangle bodies, or host sort performs the grouping. Live tuples
hold only the current encoded geometry/control fields. In particular,
payloads are never stored in a host container by the codec.

For a common-b offset `u_i`, keep the record precisely when

```text
b-b_i <= u_i < m_i+b+b_i,
```

then recode it as `v_i=u_i-(b-b_i)`. This selects exactly the smaller
consumer domain and preserves lexicographic order. The coordinate identity

```text
(t_i-b_i)+v_i = (t_i-b)+u_i
```

holds over the integers, including when either side is outside the chosen
canonical period. The codec additionally checks the supplied canonical
source suffix against the right-hand side reduced modulo `N_i`.

An odometer validates every full common-b offset exactly once before the
optional crop. The declared rectangle volume must match the observed
record count. The cropped count must match the consumer's volume. These
checks reject a missing/duplicated offset, a malformed prefix, or a foreign
source suffix on the admitted fixed-width schema. They are executable
boundary checks; the transport theorem already guarantees completeness
for its own output.

The consumer's shorter offset fields receive the recoded unsigned key.
Each of the P payload bits is read from its current transport head and
written to the current consumer head with an explicit unit step. The codec
does not decode/re-encode the numeric payload. Therefore it neither changes
rounding nor silently normalizes a noncanonical negative zero. The
consumer's existing signed-word reader rejects that representation.

## 3. Consumer chronology and exact return identity

The transport saves the entire common-b input before core mutation. Its
saved role remains unchanged throughout consumer execution. One
`TensorWorkspace` is allocated before the first rectangle and reused for
all rectangles. Its eight physical roles return blank after each output
has been consumed; the same protected reference archive supplies every
local page. The generic proof charges the whole archive scan, including
other axes, and does not substitute a unit-cost coefficient oracle.

The consumer retains the immutable input of each tensor axis until all
lines of that axis finish. Its shrinking-domain theorem establishes exact
agreement with the corresponding restriction of the full-period rounded
recurrence. This full dense recurrence is a proof/oracle device; the
production composition evaluates only the saved rectangles.

An output key contains offsets relative to the consumer's original
expanded lower endpoints. A target coordinate has offset `b_i+r_i`, with
`0<=r_i<m_i`, so its lifted coordinate is

```text
(t_i-b_i)+(b_i+r_i) = t_i+r_i.
```

The codec checks target membership, reduces each coordinate modulo the
dyadic period, prefixes the spectator bits, and emits the canonical global
key. It copies the returned payload cells unchanged. Output order is
irrelevant because the transport supplies a complete sparse sort before
the dense merge.

The first-face rectangles partition the discarded output coordinates:
choose the first local coordinate outside `[A,L-A)`, then its unique side.
Thus returns from different rectangles are disjoint and exhaustive. The
transport's merge independently checks that semantic target set, rejecting
missing, duplicate, or kept-row returns. It uses the *current* core stream
only for kept interiors. No original input is substituted for a current
core value, and no mutated core value is used as a saved halo input.

## 4. Numerical implication and the retained core premise

Use the component-l1 norm for each complex payload and the maximum of that
norm over coordinates. Let `s_i=2W_i+1`. The pinned consumer theorem gives
the per-axis numerical and tail allowances

\[
 \nu_i=\frac{(s_iR+2)2^{-q}}{\delta_i},\qquad
 R\tau_i=\frac{R(1-\delta_i)^{J_i}}{a_i\delta_i}.
\]

Since the codec preserves exact grid values and keys, it adds no numerical
error. Every returned target differs from
`[product_i (H_i^-1/a_i)] x` by at most

\[
 E_{\rm halo}=\sum_i\nu_i+R\sum_i\tau_i.
\]

This bound uses actual intermediate radii. It does not assume additivity
or nonexpansiveness of rounded programs. The same-reference consumer
contract and all its precision/normalization premises remain in force.

If an independently admitted core algorithm produces the kept coordinates
with error `E_keep` against the same `H_i`, normalizers, input and output
grid, then the complete splice has error at most
`max(E_keep,E_halo)`, because kept and discarded outputs have disjoint
ownership. That conditional implication is the splice used in #6880.
The test core here complements opaque payload bits and may produce invalid
numeric words at interiors; it is only a destructive ownership test.
Neither its output nor the successful return tests establish `E_keep`.

## 5. Complete generic time and retained backing

Distinguish two models. The transport program has finite local control and
executes 14-symbol tape reads/writes/unit moves. Its four-bit block
simulation costs at most ten binary tape primitives per reported action,
up to a further fixed control compilation factor. The numerical consumer
and joined codec execute binary data movement but use explicitly priced
scalar/control macros for bounded integers. They are not claimed to be a
fully lowered transition table. Combining raw symbol and binary counts as
one exact bit-step count would be incorrect.

Let `M` be dense records, `C_B` all common-b copies, `Q` returned targets,
and `R_rect` rectangles. Let `C_r` be the cropped input volume of rectangle
r, `K_r` its consumer key width, and `G=sum_i N_i s_i` the complete
reference archive's coefficient count. Let w bound the **entire encoded
control block**, including full keys/payloads, absolute origins, all axis
plans, periods, exact gap data, loop counters and cumulative record
counters. In particular, `log J_i` cannot be inferred from halo size when
`W_i=0` and is included explicitly.

The codec costs

\[
 O((C_B+Q+R_{\rm rect})w^2)
 \tag{1}
\]

bit work, in addition to the numerical consumer. Copies use actual tape
primitives; comparisons, shifts, additions, modulo powers of two, field
encoding/decoding and descriptor construction admit the conservative
ordinary binary macro bound in (1). Aggregate axis work does not introduce
an unexplained extra g factor: fields are sequential parts of one encoded
block whose lengths sum to O(w). Coordinatewise operations cost their own
field widths. If the dimension-factor widths are `ell_i`, successive
prefix products cost at most a constant times
`sum_i (sum_{j<i} ell_j) ell_i <= (sum_i ell_i)^2/2 = O(w²)`.
Per-product additions and rewinds add `O(gw)<=O(w²)`; prefix operand
lengths are not incorrectly counted as occurring only once.
Cumulative counter widths are also included. A fixed number of scratch
control tapes suffices.

The receipt reports record width, plan-descriptor bits and counter bits
separately, then their summed carrier units and the corresponding quadratic
tariff units. These are an argument for an O(1) multiple, **not measured
binary transitions for the scalar macros**. Source-production macros and
the numerical consumer's arithmetic bill are separate.

The reference archive is prepared once per group and reused. Write
`T_ref` for its complete separately priced source production and
quantization. The whole joined generic transaction has the bill

\[
 T_{\rm ref}+O\!\left(M(P+B)+w^2\left[
 C_B+R_{\rm rect}gG+
 \sum_r C_r\sum_i(J_is_i+K_r+1)\right]\right).
 \tag{2}
\]

The first term inside brackets includes full-key transport sort, sparse
codec, return sort, and cleanup, using `K_B=2B+3g+1=O(w)` and `Q<=C_B`.
Every rectangle has at least one saved record, so `R_rect<=C_B`. The term
`R_rect g G` keeps the full one/two archive scans per rectangle/axis; it is
not silently treated as a local polynomial. For unequal halos do not
replace `C_B` by the smaller `sum C_r`: their ratio can grow with dimension.

The retained space includes both dense input/output roles, all common-b
saved/return bodies, historical bucket extents, the largest consumer
rectangle/page, the archive, and source-production scratch. One bound is

\[
 O(MP+C_Bw+G(q+2)+\max_{r,i} d_{r,i}s_i(q+2)+w)
   +S_{\rm ref}.
 \tag{3}
\]

There are 30 transport roles, eight local consumer roles, one archive and
one reusable temporary table role, plus a fixed number of scalar/control
roles. Their count does not grow with axes or rectangles. Historical blank
backing remains paid after erasure. Clears traverse current live bodies,
so a long rectangle does not impose its old extent on every later short
face. The actual fixture explicitly clears the archive after its final
use; source-cache erasure has the separately proved producer tariff.

## 6. Conditional source-budget substitution

For #4100's retained balanced-group regime, the pinned consumer proof
establishes eventual `w=O(p)`, `J_i=16p^4`, `W_i<p`, and
`b_i<16p^5`. Keep `A=ceil(p^48)` and
`L=2^ceil(400 log2 p)` and choose a common `max b_i<=b<A`.
The known copy bound is

\[
 C_B\le6M(gA/L)(1+2A/L)^{g-1}=O(MgA/L)
\]

when `gA/L` is bounded. It controls the full common-b volume independently
of how much is later cropped.

The consumer proof uses balanced groups of size between `floor(g/2)` and
g, with `g=Theta(p^beta)`, `d=Theta(p^epsilon)`,
`beta>1-epsilon`, and the other retained strict inequalities. The many
long sides of a rectangle then absorb repeated full archive scans. That
absorption is conditional on those growing-group inequalities; generic
fixed-dimensional calls retain the term in (2). Offline source production
is separately `2^o(p)=o(V)` for full bit volume `V=MP`.

Across `O(d/g)` balanced groups, dense gather/return costs `O(Vd/g)`.
Transport and codec's sparse charge is `O(VdAp/L)`, while the complete
consumer charge is `O(VdgAp^6/L)`. Thus the combined additional charge is

\[
 O(Vd/g+VdgAp^6/L)+2^{o(p)},
\]

inside the inherited conservative sparse halo allowance. With `A=p^48`
and `L>=p^400`, the second exponent is at most
`epsilon+beta+54-400<0`. This does not improve κ or establish the core,
all-column maps, full precision interface, compiler or outer recovery.
It replaces two named sparse-interface implementation premises with a
concrete composition and a complete conditional bill.

## 7. Executed evidence and its limits

The source-bound fixture is the retained original
`Reference(61,3,2,1,8,32)`, with period 64. The separate oracle checks all
4,096 original H entries, a certified gap `6255/8192`, cyclic bandwidth 4,
identity-hole rows 11/32/53, and nonzero across-period entries `(0,63)` and
`(63,0)`. Plans use `J=2`, `q=28`, `R=1`, and normalizer 2. Transport uses
`L=32`, `A=5`, `b=4`: four rectangles, 52 saved inputs, 20 targets.

Three distinct numerical checks are retained. The streamed codec output
matches a separately loaded rectangle consumer bit for bit. A separately
written whole-grid recurrence, with independent toward-zero arithmetic and
global axis indexing, matches all target bits. Finally, exact Gaussian
elimination solves the original `Hy=x/2` with both complex components and
checks every residual; the actual target error is below the consumer bound.
The bound is deliberately loose for J=2, so it alone would not be an adequate
codec corruption control; exact bit equality is also required.

Independent signed fixtures additionally cover a spectator coordinate,
two axes with unequal halos `(1,0)` and `(1,2)`, partial crops, irregular
identity holes and real wrap interactions. During codec/merge/erase the
independent review disables tape constructors and diagnostic `inspect`/
`snapshot` calls. It checks the same fixed roles, current and historical
erasure invariants, and the unchanged protected archive. Raw negative
zero and a changed canonical source suffix are rejected.

The joined controls also reject offset corruption, omitted wrap handling,
a missing saved input and a wrong return key. A payload-magnitude mutation
that remains within the fixture's radius is detected by exact delivery
comparison. Source pins, normal/optimized replays and the independent
review are reproducibility evidence. They do not constitute independent
human or formal proof-kernel acceptance. All five selected assumptions
remain; **No new κ**.
