# A shared pencil with an absolute payload-space coefficient

Status: **proved scheduling component; independently reviewed by B** in
[review-uniform-payload-pencil.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/route-b/review-uniform-payload-pencil.md). This
refines the memory schedule of the source shared pencil. It does not by itself
prove a varying-arity interchanger, numerical Walsh transform or multiplication
bound.

Pins: programme start `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math
`3344da59991ed94f9ba711217b29c1d760badfa6`. Source: the complete shared-application
subsection of the tape manuscript `build/interchange.tex`, especially its
label-map identity, delivery by rectangles and delivery at low rank. Local
dependencies are B's [succinct-factor.md](succinct-factor.md), [explicit-dyadic-geometry.md](explicit-dyadic-geometry.md), and
[compact-interchange.md](compact-interchange.md). A and B independently identified the two-pass
schedule below; A supplies this detailed proof and finite algebraic replay.

## 1. Interface and exact claim

There are N labels, R independent scalar rows at each label, and a common
complete physical address range Omega. Let V be the **encoded bit volume** of
these N R arrays; a scalar encoding has h bits. Extra outer prefixes are
processed sequentially. For each query j in [m] there are invertible source
and destination address maps S_(v,j), T_(v,j), with

    T_(v,j)^(-1) S_(v,j)=Q_j.

Scalar R-by-R operators A_j are independent of labels and physical addresses.
They commute with address maps, but need not commute with one another. The
desired pencil is A_0+sum_j A_j Q_j, independently at every label.

Let the scalar label matrix P have diagonal one and a disjoint directed
rectangle decomposition

    P=I+sum_(L,K) 1_K 1_L^T.                            (UP1)

Each label has at most lambda incidences on either side. Let r=rank(P), and
choose row and column bases I,J for which P_IJ is invertible. Assume the
occupancy condition

    m r <= N.                                           (UP2)

The local physical premises, all supplied in the intended compact family,
are these:

1. Each rectangle endpoint has a reserve-only preparation independent of j;
   after preparation, all query-dependent maps to its common rectangle
   layout are lower triangular. Preparation and inverse preparation use
   at most c D spatial swaps per row for an absolute c.
2. Each rectangle/singleton common-layout conversion to or from a fixed
   layout costs at most c D spatial swaps per row. The remaining operations
   have polynomial(m) passes and additive polynomial(m,log(V+2)) workspace.
3. A_j and scalar label transfer matrices are applied by repeated aligned
   scans with a fixed number of input/output/work arrays. B1 supplies this
   for succinct module slices; an explicitly listed polynomial-size label
   matrix uses one output accumulator at a time.
4. Labels, rectangles, rank bases and local operation lists have total
   description and generation cost polynomial(m). In particular the number
   of rectangles is at most N lambda, hence polynomial(m), in this family.

Here and below every polynomial has an absolute degree. No hypothesis gives
unit-cost random access, a variable tape count or free regrouping.

**Theorem UP.** The pencil has a fixed-tape execution whose nonrecursive work
is

    V polynomial(m)+polynomial(m,log(V+2)),

and whose locally parked payload and ordinary work regions occupy at most

    C V+polynomial(m,log(V+2))                            (UP3)

visited cells, for one absolute C. Its total spatial-call volume, divided by
V, is at most

    C' D(1+lambda)(1+m r/N),                              (UP4)

for an absolute effective C'. Every single grouped spatial call still acts
on at most one label or one rank intermediate vector, so has volume at most
V/N. The bound concerns local memory while such a child is active; the
child's own workspace is added recursively by its caller.

Relative to the source schedule, the only additional spatial work is a
second inverse preparation of each rectangle destination. Thus a factor
two enlargement of any valid complete source endpoint invoice suffices.
For B's deliberately loose current `Cg=2^20`, taking `Cg=2^22` is safe after
this scheduling substitution. A constructor may instead count the actual
elementary lists. The exponent or incidence dependence is unchanged.

## 2. Arrays retained between phases

Retain immutable original input X and a zero-initialized original-layout
output Y. Initialize one common-layout accumulator G_(j,i) for every query
j and row-basis label i in I. Their **combined** encoded volume is

    m r R |Omega| h = (m r/N) V <= V.                    (UP5)

The common layout for query j may differ from the layout for j'; each
accumulator carries its own small descriptor. For fixed j all i use the
same layout, as required by the rank matrix multiplication. There is no
requirement to transpose j into the module index.

Access to a particular accumulator is by a charged scan of this at-most-V
region. Polynomially many passes are permitted. No (log V)-bit address tag
is appended to every scalar. Copies and head returns are included in the
ordinary work invoice.

## 3. First pass: negative deliveries and the entire rank gather

Process the rectangles one at a time. For the current rectangle (L,K):

1. Extract source copies indexed by L from X and perform their shared
   reserve preparation once. Their combined volume is at most V. Keep
   these copies for every j of this rectangle.
2. Initialize a destination accumulator for each w in K, in its prepared
   endpoint layout. Their combined volume is at most V. They contain zero,
   so no spatial call is needed to prepare their initial contents.
3. For each j, apply the source lower triangular maps and add the resulting
   streams in the actual common rectangle layout. This produces X_(L,j).
   At most one original, temporary and accumulated rectangle sum is needed.
4. Apply A_j to this common sum. Send its negative through the destination
   lower triangular maps and add it to the prepared destination
   accumulators. Keep the unscaled X_(L,j) until the next step is complete;
   A_j may be singular, so recovering it from A_j X_(L,j) is not assumed.
5. For each i in I intersect K, convert a copy of the unscaled X_(L,j) to
   the fixed common layout for j and add it immediately into G_(j,i).
   Complete one conversion and addition before beginning the next.
6. After all j, inverse-prepare the rectangle's destination accumulators
   once and add them into Y in ordinary physical order. Release every
   rectangle-local array, including the prepared source copies.

Finally add the singleton X_i(S_(i,j)^(-1) z) into G_(j,i), using its charged
full conversion, for every (j,i). Their total number is m r. The source
identity now gives exactly

    G_(j,i)(z)=sum_v P_(i,v) X_v(S_(v,j)^(-1)z).          (UP6)

The singleton can instead be added before the rectangle pass. Neither order
requires keeping a rectangle sum beyond its own processing interval.

At this point Y contains exactly the negative rectangle part of the pencil.
It contains no positive low-rank delivery yet. This postponement is valid
because all contributions are linear additions in the final ordinary
layout.

## 4. Middle matrices and second pass

For each j apply the scalar inverse P_IJ^(-1) to the i coordinate of G and
apply A_j to its R row coordinate. Store the result as F_(j,k), k in J.
These operations commute with each other because they act on separate
indices, but no commutation with a different query is used. Retaining old
and new arrays costs at most 2V by (UP5). Release G after this stage.

Process rectangles again, one at a time. For (L,K), initialize the prepared
destination accumulators, just as in the first pass. For each j, and each
k in J intersect L, convert F_(j,k) from its fixed common layout to this
rectangle's common layout. Add these vectors there before distributing
their sum to the destinations. The destination lower triangular maps add
the j contribution to every prepared endpoint accumulator. After all j,
inverse-prepare once and add to Y. Release the rectangle-local storage.

Also deliver F_(j,k) to its singleton destination k by its charged full
destination conversion, and add A_0 X to Y. For fixed j the positive
contribution in common coordinates is precisely

    P_:J P_IJ^(-1) P_I: = P.                             (UP7)

Combining (UP1), (UP6), (UP7) and the negative deliveries therefore leaves
only the identity label map. At each surviving label the address action is
T_(v,j)^(-1) S_(v,j)=Q_j. The final result is the desired pencil on every
independent input row.

## 5. Spatial call invoice

The first pass prepares each source incidence once. It inverse-prepares
each negative destination incidence once. The second pass inverse-prepares
each positive destination incidence once. Initialization of zero prepared
accumulators is an ordinary scan. Thus there are at most 3 R N lambda
endpoint operations, each costing c D spatial calls per row. The source
schedule already paid for source and destination endpoint changes; the
extra destination pass is an absolute multiplicative increase.

Each query has at most r(1+lambda) gather conversions and r(1+lambda)
scatter conversions, including the singletons. Each costs c D per row.
These contribute at most 2 c D m R r(1+lambda) calls. Together these bounds
give (UP4), including an added harmless constant for an empty rectangle
family. In particular no endpoint preparation is repeated separately for
each j, and no rectangle contribution is recomputed after its first pass
merely to recover a low-rank input.

Coarse grouping is exactly the source grouping: all R independent rows at
one endpoint or one rank intermediate vector form spectator prefixes of
the same physical interchange. It has volume V/N. Processing that group
requires neither agreement among the R rows nor a permutation inside its
exponentially wide module. All coefficient work remains outside spatial
calls.

## 6. Tape memory and uniformity

At any point there are only the following kinds of full-volume region:
original X; accumulated Y; the combined G or F rank arrays (two during
middle conversion); current rectangle source subset; current rectangle
destination subset; one common sum and its scalar-transform scratch; and
the fixed number of copy/rotation regions used by one B1 scalar slice or
one elementary address operation. Every listed region is at most V. Their
number is absolute, independent of m,N,lambda,R and the scalar-field
degree. A region for one endpoint or one rank conversion is at most V/N.

All loops over query, label, rectangle, rank index and coefficient slice
have polynomial(m) range. Scalar grade counters use polynomial(m) bits.
Long prefix and complete physical-range counters are advanced by amortized
scans; only descriptor arithmetic uses polynomial(log(V+2)) workspace.
Every head return and scan over a selected region can be charged a full
parent scan without exceeding V polynomial(m). Reusing the same fixed
regions after each rectangle and phase gives the visited-cell bound (UP3),
not only a peak-live allocation claim.

This proof measures actual encoded bits. It is compatible with a full-rate
F2 basis descent of the scalar field, but does not itself supply that
packing operation. It also does not eliminate spectral comparison tags;
the repair-table executor needs a separate uniform-payload proof. Occupied
reserved fields remain part of every full array and are restored by the
completed address maps.
