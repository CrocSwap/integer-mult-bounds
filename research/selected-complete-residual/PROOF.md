# Refinement of a complete selected residual trace

We connect the retained residual normal forms to one symbolic trace, binary
coefficient evaluation and completed leaf streams. We retain the algebra
and source contracts of source527 and PR2159/2160/2188/2234/2310/2332/2405.
PR2449 supplies the binary word arithmetic. NOTICE.md records attribution.

## Domain and conclusion

Fix an odd prime q, M=q^w, a selected request and a raw low class in
GL64(F_q). Compile its rational source projector P0, owner chart sigma and
split basis B0, independently of w and the high digits. For each raw high
field G, define g=g0+qG and

    P = g sigma P0 sigma^-1 g^-1.

The source contract gives P0=B0 E_r B0^-1 with det(B0) a unit modulo q.
COPY uses its common-header chart. Runtime prepares the same P from
g sigma B0 with binary matrix arithmetic.

Let the current parent size be n, f=floor(n/64)>0 and let A be the incoming
generated unit vector. For a logical column j in [f], put
A_j=diag(A_(if+j)). We use C for reversal on the 64 coarse coordinates.
The required operator on the two active chunks is

    R_A(P) = [[I-A_j P A_j^-1, A_j P C],
              [C P A_j^-1,    I-C P C]].

We require valid encoded root/program/field inputs, the source vocabulary
and canonical word extents from PR2449. Every emitted child must have width
less than 64. Runtime rejects larger children; we do not supply their recursive
caller here. The same trace and primitive arguments apply to the fixed
two-dimensional test model with m=2 in place of 64.

**Conclusion.** On that domain, the shared trace executes R_A(P), preserves
the unused middle and arbitrary outer/within-block spectators, and restores
its raw prefix, incoming program and input heads. Each child extends the
original parent program by one chronological raw field and returns to that
parent. The stream interpreter invokes each child once over the complete
high packet. Its primitive implementation erases owned work after return.
Under the retained root coupling, the local cost is C_q V(n+w), where V is
the complete packet's Boolean volume. Constants may depend on the fixed
source vocabulary and dimension.

We prove a refinement at this interface. A caller must supply the coherent
raw-prefix directory in the physical packet order. PR2405 supplies the
canonical pullback argument; we do not implement a new selected GL64 directory
producer or the full family/owner/global caller. We also do not claim a new
formal-kernel or literal transition-table verification.

## Fixed-low itinerary and full-ring pages

The compiler receives only q, the raw low/source specification and fixed
matrix labels. For good classes it emits all row, column and cross slots.
For fallback it emits the first-unit-pivot reduction itinerary and its
original-row permutation snapshots. It retains zero shears.

Reduction modulo q commutes with the full-ring row operations because the
pivots are units. A residue is a unit modulo q^w exactly when its reduction
is nonzero modulo q. Thus the first unit pivot and the swap itinerary agree
for all high lifts in the same low class. Runtime checks that agreement.
The terminal determinant is ±1, and odd q distinguishes its two signs.

A numeric page belongs to one exact raw prefix. It contains binary full-ring
coefficients for that prefix; it supplies no constants to other high fields.
The trace contains symbolic references and binary coordinates. A stream pass
evaluates each reference from its own prefix, on split and again on merge.
Before an inverse adapter, the interpreter uses the same pointwise-restored
raw fields. The checker may retain one page while observing one fixed prefix's
complete address operator; that optimization is outside the packet execution.

## Good normal form and chronological coefficients

Let E contain the first r coordinate columns and F=CE. Binary elimination
constructs L,R0 and diagonal Delta with

    L P C R0 = E Delta F^T.

The implementation records each row and column coefficient when elimination
reaches that slot. Later slots cannot use the original entries of P. For
example, over F5 the rank-two projector

    [[2,1,2], [1,2,2], [1,1,3]]

has second-pivot coefficient 3 in row 2; the original-entry ratio gives 2.
The selected rank-seven fixture embeds a lift of this example over Z/25:
its later coefficient is 8, while the original-entry ratio gives 12.

Define

    alpha = -E^T L P L^-1,
    beta  = -R0^-1 C L^-1 E,
    K = -(beta+F Delta^-1) E^T
        + F Delta^-1 alpha (I-E E^T).

The implementation computes these full-ring blocks with binary multiplication
and unit inversion. Let

    U = [[L,0], [K L,R0^-1]],
    J = [[I-E E^T, E Delta F^T],
         [F Delta^-1 E^T, I-F F^T]].

We can check the retained identity without an address enumeration. Since the
image of LPL^-1 is span(E), alpha E=-I. The normalization equation then gives
F^T beta=-Delta^-1. Hence

    K E = -beta-F Delta^-1,
    F^T K = Delta^-1(alpha+E^T).

Substitute these two equations and LPC=E Delta F^T R0^-1 into the four blocks
of U R(P). They give U R(P)=J U. Therefore R(P)=U^-1 J U.

Conjugate by diag(A_j,I). A head row coefficient c becomes
c A_(if+j)/A_(kf+j); a retained tail coefficient changes sign as in R0^-1;
a cross coefficient becomes K_ik/A_(kf+j). The child weights become
A_(kf+j) Delta_kk. These are exactly the three adapter references and the
Good child reference in the implementation.

The trace emits all forward column adapters, one contiguous rf child, then
the reverse of the entire flattened adapter sequence with opposite scalars.
It reuses the forward symbolic sequence; it does not construct a second
independent inverse schedule or move the child inside the column loop.

## Fallback snapshots, diagonal pairs and orientation

Let b_i(j)=A_(if+j) for head fields and 1 for tail fields. During unweighted
elimination, let pi_t record the original row currently at each position.
The corresponding weighted matrix satisfies

    weighted_t = diag(b_(pi_t)) unweighted_t diag(b)^-1.

An ordinary row swap updates pi and needs an ordinary interchange. A shear
i<-i+c_t k uses c_t b_(pi_t(i))/b_(pi_t(k)). Thus its inverse uses the
negative of that scalar with the same intermediate snapshot.

At termination, the weighted diagonal entries are

    d_i b_(pi_final(i))/b_i.

For each i before the last field, an ordinary interchange followed by its
weighted interchange installs that diagonal entry and its reciprocal in the
last field. Their product is prod(d_i), since the permutation cancels the b
factors. A final sign on the last field supplies that ±1 product. The trace
then reverses the reductions.

For an upper shear, the interpreter brackets a lower shear by ordinary
interchanges. Its coefficient reference retains the original logical pair
(i,k), even though the lower instruction writes physical field k from i.
Substituting either the terminal permutation or those redirected operands
can change the operator; the checker has distinct numerical witnesses.

Physical positions obey

    phi(i,j)=if+j               for i<m,
    phi(i,j)=if+f-1-j           for i>=m.

The first tail field therefore supplies reversed physical child weights.
Opposite-orientation chunk pairs already match the reversal in a weighted
child. Same-orientation pairs require a unit reversal of the later chunk
before and after that child. The trace emits both reversals, including the
odd-f middle coordinate that remains fixed. A width floor(f/2) reversal uses
the unit-child half flag in the serialized program.

## Serialized children and completed leaves

The serializer copies the parent's root and chronological records, increments
the encoded depth, and appends the exact current request/raw-low code. It
computes the child size with binary division/multiplication. It does not
rewrite the parent or compact slots after a reset.

The leaf evaluator receives exactly those frozen fields. It has no fresh
current field and cannot call an internal head-coefficient routine. Good,
Pair and unit rules agree with the retained generated grammar. In particular,
Pair uses the physical reversal of j and the terminal permutation, while
the adapter shears use their intermediate snapshots. Sequential siblings
each extend the same original parent.

For a leaf pair with unit a, the shared primitive sequence is

    AtomSwap; ADD(a); AtomSwap; ADD(-a^-1);
    AtomSwap; ADD(a); AtomSwap; Sign(later).

Starting at (x,y), its final pair is (a y,a^-1 x). Runtime evaluates the
weights from binary words. It never substitutes a weighted-swap oracle for
this sequence. Child entry and return markers surround the complete leaf
word; the packet interpreter handles those markers outside its prefix loop.

## Binary cardinalities and opaque bit streams

Natural tapes store canonical little-endian binary cardinalities. Multiplying
by fixed q uses a carry in [q]; dividing by fixed q scans from the high bit
and keeps a remainder in [q]. Prefix invariants give the ordinary product
and quotient/remainder identities. The implementation trims high zeros and
erases the released representation. No numerical cardinality becomes a
native integer. Only fixed labels and finite carry/remainder states do so.

The layout builder multiplies spectator factors by M once per encoded atom
position. It preserves separate canonical spectator extents and rejects
padding borrowed from a larger unrelated context. It embeds the active two
chunks around the unused middle using binary offsets. Counter initialization
and decrement use the retained ripple bound O(N+log(N+1)+1).

For a digit transpose U×[q]×G×[q]×S, split into q² sequential buckets indexed
by the two finite digits. Merge bucket (b,a) in output digit order (a,b).
This swaps the digits while preserving U,G,S and within-block bit order.
To swap whole M-atoms, repeat for all w corresponding digit pairs. The
before cardinality multiplies by q, the suffix divides by q, and the middle
factor remains fixed. Runtime counts the digits by dividing encoded M by q.

An address sign first complements all radix-q digits, giving M-1-y, then
rotates by one, giving -y modulo M. The rotation and retained ADD split/merge
copy opaque Boolean bits. A one-bit-suffix branch recognizes only the fixed
encodings of 1; it changes no mathematical operation.

Individual digit exchanges need not be linear over Z/M. We therefore verify
complete bit streams and their source-bit origins in addition to address
columns. The whole AtomSwap macro, after its digit lowering, is the ordinary
atom interchange used by both backends.

For a complete high packet, the interpreter consumes a sequential raw-prefix
directory. Each primitive visits every prefix before the next trace event.
It copies one complete prefix fibre to local work, executes the primitive,
and appends the result in the same prefix order. A child thus has one entry
and return for the entire packet. Every numeric preparation reads that
prefix's raw fields; no sampled page serves the whole packet.

## Erasure, cost and remaining obligations

The residue and index banks retain the fixed capacities of PR2449. The full
Good tables and fallback reduction scalars add bounded-dimensional storage;
one page fits the reserved 65,536-role residue bank. Suspended ancestry lives
on encoded tapes. Each returned coefficient has one owner; the closed source
callback releases its page, program extension and numeric work. Successful
stream passes clear bucket, counter, cardinality and intermediate payload
tapes and preserve the source/directory heads.

For L=bitlength(M)+1, the unweighted page costs O_q(L³). Generated evaluation
has the same binary grammar and conservative root-coupled polynomial charge
as PR2449. With w=ceil(e^(17/10000)), proper descents give 2^(h+1)<=8e²;
the complete-vector allowance e³w³ fits w^1800. The factorial bound

    w^1800 / q^(w-1) <= 2^1800 * 1800!

charges preparation to complete target fibres. Directory access is sequential,
so it adds no quadratic scan in the number of prefixes.

Building cardinalities costs a polynomial in n,w and the spectator bit lengths.
For n>=2, the complete body volume M^(2n) absorbs the n,w polynomial; each
spectator factor absorbs its own logarithm. The layout work therefore costs
O_q(V). An ADD costs O_q(V); a full atom swap or sign costs O_q(wV).

There are O_m(n) residual adapter ADDs and O_m(1) child invocations. Each
admitted leaf has at most 63 pairs, so its primitive expansion contributes
O_m(1) atom swaps/signs per child. This gives C_q V(n+w), including framing,
cleanup and the explicit unit/orientation children. Larger children require
the remaining recursive caller; we do not charge an unimplemented callee as
if this package had executed it.

We have not executed the selected GL64 Boolean payload, supplied its canonical
directory producer, joined the full family/owner/global schedule, or formalized
these machines in Lean. Finite checks support the implementation; the stated
invariants and algebra give the scoped refinement. We retain the selected
frontier and claim no new multiplication exponent.
