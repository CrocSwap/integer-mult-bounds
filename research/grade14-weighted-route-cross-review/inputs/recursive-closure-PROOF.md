# Recursive closure of the selected BIT interchange

We give a written construction on a fixed number of finite-alphabet multitape
streams. We retain the sequential stream model of `02-streams.tex`: complete
address ranges, arbitrary Boolean payload, charged scans, counters, rewinds and
scratch erasure. We prove an ordinary binary chunk-interchange bound

    O(V E^(1-a)),  a = 169711/100000000 = 0.00169711,

for two complete E-bit address chunks and arbitrary complete spectators, where
V counts payload bits. The machine restores spectators and clears its work.
We fix one odd prime q>2^80 throughout; constants and the fixed tape count may
depend on q and the selected word. We make no practical runtime claim.

We supply a mathematical algorithm and finite interface checks. We have not
translated the entire recursive machine into transition tables or a proof
assistant. Reviewers must assess the composition argument below. The selected
finite certificate and the multiplication theorem have further interfaces,
including the complex supplier and analytic transfer; we leave their status
unchanged.

## 1. Sources and the recursive contract

We use DreamingOfClouds' selected PR589 word, building on eumemic's PR555 word,
and alephnan's PR1627 literal/chronological proof. We reuse the GL local-ring
packet integration of PR2195, the good adapters of PR2171, the fallback word
of PR2159/PR2207, and commdata2338's PR2188 weight grammar. Source527 already
gives the weighted factorization and outer borrowing method. PR1379 supplies
the unequal-buffer parking boundary. `SOURCES.json` pins the executable inputs;
`NOTICE.md` identifies the pending source commits and mathematical reuse.

Fix an original radix-q width e, c=17/10000, and w=ceil(e^c). Put B=q^w and
R=Z/B. We keep w fixed throughout one coarse recursion. Let C_n reverse n
atom positions. For a diagonal unit vector A, we construct

    F_A(H,D) = (A C_n D, C_n A^-1 H).

We quantify over any two ordered complete n-atom chunks, with arbitrary
complete preceding, intervening and following fields. This includes two
subchunks of one former bank, which we need for fallback reversals. We allow
arbitrary correlated dirty payload values.

We generate A from a constant unit by the Good and FallbackPair expressions
below. A may read earlier frozen matrix fields; it may not read this node's
fresh family, matrix or unused stock. A unit child starts a new constant
expression but retains its global generation depth. We bound that depth by
the original root width, including after such a reset.

At return we require the specified address permutation on I/O, pointwise
restoration of row and spectator coordinates, empty local work and restored
head positions. For a parking top h, we visit no cell below h-1 and write no
cell below h. We require a time bound uniform in parked contents and h.

## 2. Actual residuals and full-ring preparation

PR1627 reconstructs 636 rational frame projectors and proves the nesting
identities used by both selected literal programs. Their entries lie in
Z[1/2]. For an idempotent P0 of rational rank r, its characteristic polynomial
is T^(64-r)(T-1)^r. Reduction modulo an odd q preserves this identity and
idempotent diagonalizability, hence rank r, including when q divides r.

Choose independent image columns of P0 and kernel columns of I-P0 modulo q.
Their lifts form a unit matrix B0 over R and satisfy

    P0 = B0 diag(I_r,0) B0^-1.

We compute this identity in control arithmetic. We do not move payload through
B0. For the actual owner chart sigma and raw physical header g, the provider
passes g sigma B0 to the retained coordinate normalizer. It therefore computes
exactly P=g sigma P0 sigma^-1 g^-1.

For MOVE, we use the positive nested frame difference and the actual owner
sigma. The common stage projector cancels. The reflected orientation gives
the same positive residual. For COPY, we first copy and align the source
packet to d=g sigma. Its private header is d and its projector label is P0;
we set its additional chart to I. Applying sigma again would change the
operator. ERASE retains the literal transported-source equality guard.

For an idle remainder, we subtract the actual hosted slots from its pending
axes and use the fixed family chart. We skip the zero remainder. The provider
binds 28,278 canonical requests and 32 replicas, giving

    H_1=381024, H_2=400416, H_3=22752, H_4=26880,
    H_5=29376, H_6=17376, H_7=26784, H_42=288.

We obtain 541 distinct base labels and 1,235 assembled charts. The finite
checks verify image/kernel bases over Z/9 and Z/25 for each label, and 120
full 128-coordinate operators from selected MOVE, COPY and idle requests.
These cases supplement the identities; they do not enumerate GL64(R).

## 3. One schedule per complete low packet

Write g=g0+qG with g0 in GL64(F_q) and G in [q^(w-1)]^4096. For a fixed
request, call g0 good when the first r northeast pivots of PC are units.
Equivalently, require the leading k principal minors of P to be nonzero
modulo q for 1<=k<=r. Unit tests depend only on g0. The full coefficients
still depend on G.

For each k, multiply its minor by det(g)^k to obtain a polynomial of degree
at most 64k in the entries of g. Conjugating the fixed split rank-r projector
to diag(I_r,0) gives a nonzero witness. The union of these zero sets has
fraction at most 64r(r+1)/(2q) in all matrices. Since

    |GL64(F_q)|/q^4096 = product_(i=1)^64 (1-q^-i) > 1/2,

the bad fraction for this request is at most 2*64^3/q<10^-16. We use this
bound separately for each paid edge. We do not require one matrix to be good
for every label or multiply the bound by the number of labels.

On a good packet, unweighted northeast elimination gives unit-lower matrices
L,R0 and a pivot vector delta. Split rank and a unit rank-r minor force the
remaining Schur block to vanish over R itself. We retain q-multiples in the
arithmetic; reduction modulo q alone would not establish that conclusion.
The normal-form factorization in source527/PR2171 uses ordered head, tail
and cross ADDs, one weighted child, and the inverse adapters. For n=64f,

    A_child[k f+j] = A[k f+j] delta_k,  0<=k<r, 0<=j<f.

The child has rf atoms. Both adapter halves contain
2f(r(127-r)+4096) later-target ADD slots. We retain zero slots, so the schedule
is common across high lifts and columns. We use no ordinary body interchange
inside these adapters.

On a bad packet, perform the retained 128-row unnormalized elimination with
the first available unit pivot. If pi_t tracks original row labels and
B_j=diag(A[0f+j],...,A[63f+j],1,...,1), the weighted state is

    M_t^weighted = B_(pi_t,j) M_t B_j^-1.

Thus the pivot itinerary equals the unweighted itinerary. A shear i<-i+c k
uses c*b_(pi_t(i),j)/b_(pi_t(k),j). Row swaps remain unit swaps and advance pi.
Diagonal pairs use the final pi. We reconstruct in inverse chronology, with
each shear's own snapshot, as PR2207 does. We retain zero shear slots.

Replace an upper shear by a unit interchange, a later-target shear, and a
unit interchange. A physical same-orientation interchange uses a reversal
of the later field, a reversed weighted child, and the same reversal again.
We implement each reversal by a unit child on its two halves, omitting the
middle atom when its width is odd. Weighted pair children have width f;
orientation children have width floor(f/2). We can bound the number directly:
there are at most 127 elimination swaps, 254 diagonal-pair swaps and twice
8128 upper-shear brackets. Each swap needs at most three reversed children,
so 3*(127+254+16256)=49911<32*64^2. We retain the larger source allowance.
The final sign is a sequential fixed-sign pass.

The branch, slot positions and child widths therefore depend on the fixed
request and g0, not on G or the incoming unit values. We execute each child
once on the complete high packet. We never dispatch one child for each G.

## 4. Symbolic ancestry and the completed leaf

`Expression` stores fixed request IDs, low matrices, atom widths, chronological
field slots and Good/FallbackPair nodes. An evaluator substitutes the values
of older high fields from its current I/O prefix. A Good node evaluates the
formula above. A FallbackPair node evaluates

    d_i * b_(pi_final(i),j) / b_(i,j),

with the physical reversal of j when its first field lies in the tail bank.
The first-unit elimination plan depends only on the stored low matrix; the
evaluator recomputes the full-ring coefficients from that field's high value.
Every denominator is a unit. An inductive expression therefore defines unit
weights on its whole prefix domain.

When entering a child, we append a reference to the current parent field and
its exact request/low metadata. We freeze that field after the relevant row
route and preserve it through the child. The child takes its own fresh matrix
from the unused stock. `FrozenFields` rejects a future field, a changed low
matrix, or a reference out of chronological order. The evaluator has no unused
stock argument. One expression serves all high lifts; a numeric matrix from
one test point cannot stand in for that expression.

For n<64, handle each pair (H_i,D_(n-1-i)) with unit a=A_i. Let J exchange the
two atoms and L(c) send D to D+cH. In chronological order execute

    J, L(a), J, L(-a^-1), J, L(a), J, D<- -D.

Multiplication gives (H,D)<-(aD,a^-1H), the source527 weighted factorization.
For J, interchange each of the w corresponding radix-q digit positions.
For one digit pair, split by its values (x,y) into q^2 sequential buckets,
then merge in (y,x) order, retaining intervening and suffix fields. Erase the
buckets and rewind. This uses O_q(V) time per digit and a fixed q^2 tape
inventory. We use four ordinary atom exchanges, three ordered shifts and one
sign per pair, hence O(Vw) at a stopped leaf. We require no recursive callee
there. The n=0 case is identity.

An ordered shift with coefficient c(prefix) rotates a complete B-block target
fibre by c*x. Split at B-(c*x mod B), merge the two parts in reverse order,
then erase and reset scratch. This works for zero and nonunit c. A fixed sign
retains target block zero and reverses the order of the other blocks while
preserving their internal bits. We retain the PR2171/PR2207 sequential loops.

## 5. Closed header routes and whole-call interpretation

PR2157 gives fixed dyadic words for the selected data/helper charts. Our
checker replays their inverse words to the actual provider charts. Their
coefficient alphabet is contained in {+-1/4,+-1/2,+-1,+-2,+-4}. For a fixed
integer multiplier, split into its fixed number of monotone pieces. For a
dyadic affine operation, retain the low-digit carry and compose integer
scaling, an ordered high-field shift, and inverse scaling. A reversed pair
of header fields uses two elementary high-field interchanges from section 4.
We charge O(Vw) per fixed route. At w=1 the high fields disappear, but we
still permute the low classes.

During an individual entry update a work header can have a singular low
matrix. We interpret that step on the complete high cube. Only at the end
of the complete column factor do we use the GL header again. We do not invoke
a residual callee on a partial chart. The complete route is an invertible
right multiplication and preserves the GL domain. We use the 111 family
charts only in idle-projector control arithmetic, without routing their
payload. We never use an arbitrary ancestor-dependent unit as a number of
monotone-piece tapes.

We now define a complete internal node. Write n=64f+delta. First execute the
leaf on the last delta head atoms and first delta tail atoms, with weight
offset 64f. Keep the first 64f head atoms and last 64f tail atoms as the core;
the peeled fields join its gap. This preserves the existing flat-index rule.

Decode the fresh rows as in section 6. Interpret the pinned global schedule
in order. At a local sweep, visit its 32 replicas and common low classes;
finish the whole literal local program before advancing to another low
class. For each role use its actual complete owned packet. Interpret:

* MOVE: select the owned packet, execute its bound residual by section 3,
  and replace that packet in its family.
* ADD: select copies of target and source, route both to the common header,
  XOR their Boolean payloads, route the target back, and replace only the
  target packet. Keep the original source. Erase the work copies.
* COPY: select and align a source copy into fresh private work, then execute
  the bound rank-seven transport. Keep its common header through the private
  lifetime. The selected program uses it as a source and never MOVEs it.
* ERASE: use the matching transported-source guard proved in the literal
  replay. Erase the equal private work and restore its head.

For a source or target on the private stream, use its common header directly.
Same-family ADDs still select separate complete low packets. The explicit
helper completions distinguish them modulo every odd q; pointwise distinction
of two high matrices alone would not suffice. PR2195 proves this stronger
low-packet property and the restricted-fibre procedure.

Execute global bridges as family XORs, idle remainders as their bound residuals,
and the terminal exchange as a fixed family-stream permutation. These are
the same chronological endpoints as the PR1627/PR2195 whole-call argument.
At fixed common d, the decoded-frame induction handles correlated dirty
helpers and the private equality guard. Write the completed low-class
endpoint as S_d times a product of unary helper permutations R_(j,d).
The retained local endpoint leaves no helper/data cross terms. The 222 data
families are distinct, disjoint from helper families, and have matching paired
source/target routes. Each data route bijects low classes. Consequently
different common low classes affect disjoint data packets.

Only unary helper endpoints can overlap. For a fixed physical header g,
helper j appears at precisely the common low class g0 sigma_j. Its endpoint
preserves g and acts through the projector
g A_port E_(S_j) A_port^-1 g^-1. The selected supports S_j are disjoint where
the hosting argument combines them. Their unary permutations commute, and
the local endpoint identity accepts the previously transformed dirty inputs.
This proves the whole local sweep. To move endpoints across different global
calls, we still use the verified untouched hosting intervals; commutation
alone does not permit crossing an intervening data shear.

For incoming A, conjugate the entire address argument by Q_A=diag(A,I).
We use the same A across the current family and cover coordinates. It
commutes with current-header routes and common-frame scalar XOR operations.
The provider implements the conjugated residuals; the equality guards and
dirty-helper cancellation carry through. We obtain F_A on every live family.
We restore the decoded row field and merge the original row order.

`recursive_plan.caller` binds every paid residual to this chronology and
checks the private-source restrictions. It is a macroplan checker. We do
not describe its digest as execution of the enormous selected payload.

## 6. Fresh stock, parking and strong induction

Let W=28416 live families, P=28425 physical slots, M=lcm(W,P)=269241600,
N=|GL64(F_q)|, H=q^(4096(w-1)), and K=MNH. Define

    D(n)=0 for n<64; D(n)=1+D(42 floor(n/64)) otherwise.

For row count t K^D(n), decode [W] x [N] x [H] x [U], where

    U=t*9475*K^(D(n)-1).

Allocate private and selector copies as work, not arbitrary input rows to
clear. A fixed family/low packet has volume v=V/(WN); we retain all H and U.
For each child n'<=42 floor(n/64), D(n')<=D(n)-1 and K^D(n') divides U.
The child receives complete fresh stock for each old high value. It preserves
the old high field as a spectator. The same argument covers f and floor(f/2)
fallback children.

Use W live stream tapes and four packet buffers for private, source, target
and route output. Close split scratch before a child and finish a full-family
replacement before invoking another child. At a recursive boundary the
occupied volume is at most V+4v. With B0=W+4 role slots, PR1379's unequal-size
wrapper costs at most

    5(V+4v)-v+9B0-2 = 5V+19v+9B0-2,

excluding the child. We charge descriptor copies, dispatch and markers too.
We do not use the equal-volume 14V corollary for these unequal buffers.

Before the child, copy its finite descriptor and control state onto local
control tapes. Park the inactive payload buffers and caller state above the
entry delimiter. Move the active complete packet to child I/O. The child
reads ancestor values from its I/O prefix counters, never from buried parking
records. It uses relative tape origins, stops at its own delimiters and
erases only its own visited work. On return restore the inactive buffers and
caller state. The tape inventory remains fixed: recursive calls reuse the
same role, bucket, arithmetic and control tapes after parking them.

We prove endpoint, row restoration, scratch closure and locality together by
strong induction on n. Section 4 supplies the leaves. At an internal node
the peeled leaf closes; each child width is positive and strictly smaller
than n and receives the stock and expression contract just proved. Apply
the induction hypothesis at each parked boundary. The ordered adapters,
routes, selection and XOR loops close their scratch. Section 5 then proves
the parent endpoint. PR1379's trace proof composes the delimiter bounds.
This closes the completed weighted-child premise; we do not assume the
ordinary supplier whose saving we derive in section 8.

## 7. Uniform time and the stopped recurrence

We account for control work as well as payload movement. Schoolbook ring
arithmetic, fixed-size elimination and sequential access to the local
descriptor have polynomial cost in w, log e and the generation depth d.
A pair descriptor can branch into two parent evaluations; recomputation
therefore costs at most 2^d times a fixed polynomial, with an additional
polynomial factor in the root atom count if we prepare a literal vector.
Since d<=D(e)<=2 ceil(log2(max(2,e))) and e<=w^(1/c), this cost is polynomial
in w on the stated root-coupled domain.

For an atom ADD, each coefficient preparation accompanies at least q^w
target blocks. For a header pass the complete high target contributes
q^(w-1) blocks. Every fixed polynomial divided by either quantity has a
finite supremum over w>=1. Recompute on split and merge rather than retaining
an array indexed by the high fibre. Ripple counters have amortized linear
movement cost; initialize them once per scan and do not reread unrelated
spectator counters per fibre. Fixed low tables and finite labels depend on
q, not e. Thus these scans have the stated uniform bounds. For independently
chosen n,w,d, retain the preparation quotient instead of this absorption.

The selected word has fixed length. Good and bad bodies use O(n) ordered
atom passes; header routes use O(Vw) each; selections, XORs, erasure and
parking use O(V) each. We include their finite q-dependent multiplicities
in a constant C. The local nonrecursive charge is C V(n+w), including the
remainder leaf. This is an asymptotic accounting, not an explicit optimized
finite invoice for the selected multiplier. PR2212 prices the separate
same-family route inventory and leaves further whole-invocation charges.

Normalize by logical volume and bound the worst generated call by T(n,w).
For positive widths below 64, T<=Cw. The bad fraction is at most epsilon=10^-16
for each request, and each fallback has at most 32*64^2 children of width at
most f=floor(n/64). We may overcount good calls on bad classes, obtaining

    T(n,w) <= sum_r (H_r/W) T(r f,w)
              + epsilon F/W * max_(1<=j<=f) T(j,w) + C(n+w),
    F=32*64^2*sum_r H_r=118606528512.

We prove a monotone upper bound, so the maximum causes no extra factor.
Define mu_t=(sum H_r(r/64)^t + epsilon F(1/64)^t)/W. The two retained outward
rational engines independently give

    mu_1 = 2874298095721977/2890625000000000 < 199/200,
    mu_(1-c) < 9999/10000.

Induct on n and use f<=n/64. Increasing C to cover the leaf constants gives

    T(n,w) <= 200 C n + 10000 C n^(1-c) w.

Indeed the first term leaves at least Cn after the recursive linear mass,
and the second leaves at least C n^(1-c)w>=Cw. We treat n=0 separately.
The resulting constants are independent of ancestor contents, stack top,
row multiplicity and original e.

## 8. Internal borrowing and binary interchange

Choose the sufficient stock S=K(w)^D(e) from the original width e, before
choosing a body width. Since M<q, N<q^4096 and H=q^(4096(w-1)),

    log_q K < 4096w+1 <=4097w.

Borrow k=ceil(log_q S)=O(w log e) leading digits from the earlier chunk.
Eventually k<e/2. The physical order is

    H_hi, H_body, gap, D_hi, D_body.

Use the complete H_hi range as preceding rows; retain D_hi in the gap.
Pad only that row range to ceil(q^k/S)S, by a factor below two. Split each
body into whole w-digit atoms and fewer than w remainder digits. Handle
the remainder by elementary digit interchanges, retaining the other fields.

On the atom bodies use the chronological ordinary wrapper from source527:

    D<-D-H; F_I; D<-D+H; F_I; D<-H-D.

Direct substitution yields (H,D)<-(D,H). The three updates use ordered atom
passes; the two F_I calls reuse the same restored row stock. Their constant
multiplicity stays outside the coarse recurrence. Remove the row padding
after this completed endpoint, then interchange H_hi and D_hi by k elementary
digit passes. The result is the full ordinary radix-q chunk interchange.

With n<=e/w and w=ceil(e^c), its time is

    O(V [e^(1-c) + e^(1-c+c^2) + e^c log e])
      = O(V e^(1-c(1-c))).

The first exponent lies below the middle by c^2; the borrowing exponent lies
below it by (1-c)^2. For the bounded set of small widths where borrowing
does not fit, use the elementary whole-chunk interchange. Absorb that finite
set into the same constant. We claim no useful numerical cutoff.

Finally embed each complete binary range [2^E] into
[q^ceil(E/log2(q))]. Pad both ranges, increasing volume by less than q^2.
Execute the completed ordinary radix-q interchange and remove padding.
Its endpoint preserves the genuine rectangle, even though intermediate
address operations can mix genuine and padded positions. Fixed q preserves
the exponent and the number of tapes. We obtain the stated binary bound.

## 9. Evidence and remaining limits

We check all source-bound base labels, selected full operators, symbolic
temporal controls, physical leaves, fixed header routes, low/full plan
compatibility, chronological request coverage and exact coarse moments.
The negative controls exercise same-rank label substitution, double owner
alignment, high-to-low coefficient truncation, wrong inverse, omitted digit
movement and future-field capture. `RESULT.json` records their scope.

We have not run the entire selected payload, enumerated GL64, produced a
transition-table compiler, or formalized this proof. Our Python tapes measure
the specified payload adapters; the written argument accounts for arithmetic
and recursive control. We prepared the argument and code with substantial
OpenAI Codex assistance. Independent mathematical review remains necessary.
We do not infer a multiplication exponent or alter the selected frontier.
