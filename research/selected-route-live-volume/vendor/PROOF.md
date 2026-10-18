# First internal selected BIT node

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
We work in the retained stream model and use the pinned written predecessor
refinements. Maintainer admission and formal-kernel verification remain open.

## Statement and input contract

Fix an odd prime q, m=64, w>=1 and M=q^w. Put

    N=|GL_64(F_q)|, H=q^(4096(w-1)), W=28416, P=28425,
    lcm(W,P)=269241600, lcm(W,P)/W=9475.

Choose 64<=n<128 and delta=n-64. Supply a well-formed generated parent program
of final width n and depth h, using this package's complete fixed-q source
vocabulary from its creation. Supply its C>=1 physical frozen prefixes in
their original order, including repetitions. Each prefix contains exactly h
raw fields and determines incoming units A_0,...,A_(n-1) in Z/M.
The parent grammar reads these frozen fields only. In particular, the incoming
weights do not depend on the new family, current low/high header, unused row
coordinate, body address or external spectators.

Supply fresh row cardinality K, a positive multiple of 269241600*N*H, and
positive cardinalities B,G,S. Use canonical unbounded binary cardinalities
and index/residue words with the retained margin/encoding contracts. Set
U=K/(W*N*H), so 9475 divides U. Use the following physical input order:

    [old prefix][K fresh rows][B][H_n][G][D_n][S].

We interpret fresh rows lexicographically as
`[family][low GL class][raw high matrix][U]`. We use the incoming ordinal
without identifying or discarding repeated frozen prefixes. A caller may
supply arbitrary dirty, correlated payload bits. The original input, parent
program and frozen directory remain read-only; the node owns fresh output,
staging, private and arithmetic work.

**Refinement proposition.** Under the source identities and primitive
refinements pinned in SOURCES.json, we construct a finite stream program for
this node whose output, at each frozen prefix, has address permutation

    H_i' = A_i D_(n-1-i),
    D_(n-1-i)' = A_i^-1 H_i               (0<=i<n).

We denote this involution by F_A. We preserve the old-prefix ordinal, original
fresh-row ordinal, B/G/S coordinates and incoming program. We return one
owned output with its head reset and erase the node's temporary payload,
private, directory and arithmetic work. We do not require zero entry in any
live family. Only private/staging work has blank entry.

For the retained root coupling, we give a constructive bound
`C_q V(n+w)` for the complete node, where `V=C*K*B*G*S*M^(2n)`.
We include the completed child leaves in that bound. We leave a numerical
reserve constant, larger recursive return and all-size transfer open.
Without the coupling, retain the explicit directory/control terms below.

## Ring and weighted-address lift

The retained PR589 hosting proof states an ideal finite-field/orthogonal-group
contract. PR2195 supplies its ring/GL extension. We recall the argument over
Z/M and all invertible raw headers before using the chronological induction.

Write C0 for tail reversal and A for the diagonal matrix of incoming units.
Conjugate the ordinary partial swap D_P by the invertible coordinate change
`(H,D) -> (A^-1 H,C0 D)`. In the original coordinates we obtain

    v=P(C0 D-A^-1 H),
    T_A(P)(H,D)=(H+A v,D-C0 v).

For an idempotent P, direct multiplication gives `T_A(P)^2=I`. For nested
idempotents P,Q with PQ=QP=P, we obtain
`T_A(P) T_A(Q)=T_A(Q-P)`; for PQ=QP=0 we obtain `T_A(P+Q)`.
These are polynomial matrix identities over a commutative ring. We require
neither a field nor symmetry after conjugation. The selected rational base
projectors and owner charts have dyadic entries, so their authenticated
identities specialize to Z/M for odd q. For each raw invertible header g,
simultaneous conjugation by g preserves nesting and disjointness. We use
the source's same fixed charts and support identities in that conjugation.

Reduction modulo q identifies invertible raw matrices with the disjoint
union of N low classes, each with H high matrices. Right multiplication by
an invertible owner chart sigma permutes this full set; at a fixed common
low it permutes the complete matching high fibres. The route refinement
implements that permutation. Distinct source charts remain distinct modulo q
by their disjoint nonzero support columns, so the within-invocation ownership
argument also survives this extension.

The local symbolic-column proof uses XOR on Boolean functions and these
address permutations. Its cancellation, dirty-helper independence and
transported-source identities therefore hold on the finite address set over
Z/M. The hosting chronology only uses those complete-call identities and
the disjoint-projector products above. This gives the ring/GL version of
the retained argument, with the same frozen A throughout a physical prefix.

## Source catalogue and caller geometry

We adapt PR2234's provider enumeration, preserving its ordered record digest
`f5a4fb124709adc4b56376a3146e3609e91c0f4d3ed1931a61785a5d99bf8ee7`.
We enumerate 28278 canonical requests: 26199 MOVE, 81 COPY and 1998 IDLE.
With 32 replicas we obtain 904896 paid requests. We retain 541 base labels,
1235 chart labels and 81 canonical transported ERASE guards. We bind each
MOVE/COPY to its literal position, stage, role, source family and chart.
For COPY we reserve canonical family 28416 as private metadata; we use the
call's actual owner family for the payload source.

We compile the fixed vocabulary from (q,request,view,low). At q=3 we need 6507
bits per code. Authors of older two-request fixtures used 6494 bits; we do not reinterpret
those encoded programs. Low-class enumeration, rational matrix compilation
and specification caches depend only on q and fixed source labels. Runtime
precision, raw high fields, parent widths and incoming coefficients remain
on tapes. Lazy fixed-q compilation implements a finite table, with no claim
of a small practical table.

For local calls we gather a native owner header g and route d=g sigma into
common coordinates. We then compile the base projector with chart I and
preparation B0. The actual projector is d P0 d^-1. We do not apply sigma
again. For native idle requests we retain the actual family chart A_port and
preparation A_port B0. Those requests require the native view. The source
checker binds both views to the actual coefficient/serialized-child consumer;
the proofs use the inherited source and normal-form refinements.

We obtain paid ranks at most 42. Since floor(n/64)=1, we use child width equal
to the rank in the good branch, and width one in the fallback branch.
We expand them through PR2501's completed leaves. We introduce no opaque
recursive callee in this range.

## Original-offset peel and independent gap

Before decoding fresh rows, we apply the weighted exchange on each pair

    (head coordinate 64+i, tail coordinate delta-1-i), 0<=i<delta.

In absolute two-bank atom indices this is
`(64+i,n+delta-1-i)`. We read A_(64+i) from the original frozen-only parent
callback. We append no child record or dummy current field. The eight
retained leaf primitives use coefficients A_(64+i), -A_(64+i)^-1 and
A_(64+i), interspersed with atom swaps and a sign. Their standard two-variable
factorization gives the stated weighted exchange. We leave the first 64 head
atoms and last 64 tail atoms for the core.

We keep G independent of the powers of M. Let the per-header before factor
be L=UB. For absolute atom positions a<b, the primitive extents are

    pre    = L M^a             * (G if a>=n else1),
    middle = M^(b-a-1)         * (G if a<n<=b else1),
    suffix = S M^(2n-1-b)      * (G if b<n else1).

For a single sign at a use the analogous pre and suffix. For the peel replace
L by KB. For the core embed logical atom a as a when a<64, and as a+2delta
otherwise. Thus the opaque core gap contains the peeled head chunk, G and
peeled tail chunk in their original order, with cardinality `M^delta G M^delta`.
Its preservation preserves the separate coordinates, because their mixed
radix encoding is injective. Merely checking the product of extents would
not establish this placement; we check each extent against these formulas.

Each core operation preserves the peeled coordinates. Each peeled pair
uses the same frozen weights and disjoint atoms. Therefore the complete
core F_(A_0,...,A_63) and the peel compose to F_A on n atoms.

## Fresh rows and whole-packet child return

We divide K by W, N and the 4096 high-coordinate powers using unbounded
binary cardinalities. We reject a nonzero remainder and require 9475|U.
We never substitute the physical inventory P for logical W. We split the
peeled payload into W family streams, retaining `[old prefix][low][high]`
order inside each and treating `[U][B][body][G][body][S]` as one fibre.
The inverse merge restores the exact original ordinal.

For a residual we produce the serialized current directory from all C old
prefixes and all H high matrices. At a primitive event we traverse that
directory in payload order, evaluate the coefficient from its actual raw
prefix and execute the retained stream primitive on the complete fibre.
We do not evaluate a numeric page at one high header and reuse it elsewhere.

We keep child ENTER/RETURN outside the physical-prefix loop. We compare the
parent identity, source code, field, orientation, half, width, coordinates
and depth at return. Inside that interval we expand the completed leaf over
the whole packet. We release its program/arithmetic work before the parent
continuation. We preserve the parent's encoded program and directory bytes.
These facts give the same whole-packet child semantics as PR2501, with the
additional physical gap and original n-atom embedding.

## Whole local word and private lifetime

Fix one stage, replica and common low d0. For each of the 661 roles we obtain
the native low `g0=d0 sigma^-1`, gather its complete high packet and perform
the binary stable owner route. Within this invocation, distinct roles on
the same family own distinct native low packets: equality would force equal
charts modulo q, contradicting their disjoint authenticated helper supports.
The driver also checks uniqueness of `(family,g0)` before execution.

We stage all 661 roles and execute the complete authenticated local word.
MOVE calls the actual common-view residual. At ADD the finite controller
requires equal frames; we XOR the aligned common packets. In characteristic
two both literal signs use XOR. At COPY we clone the current source into
fresh private work and apply its actual residual. We preserve the source
and private version through the ensuing ADD interval. At ERASE we require
the same source version and transported private frame before clearing it.
This is the transported-source guard, including the distinct forward and
reverse literal rank fields. It does not require private payload to equal
the untransported source.

We inverse-route and scatter all 661 roles, including helpers whose physical
frames advanced. For repeated families we scatter into the latest family
state. Distinct packets within this invocation then preserve each other's
updates. We finish the invocation before gathering the next common low.
Across different common lows a family can receive overlapping owner updates;
the next invocation must therefore read the returned state. These two
invariants establish by induction that the physical caller refines the
retained chronological local-word semantics on arbitrary live functions.

We replay 7843392 literal events across 288 calls, including 6999840 ADD,
838368 MOVE, 2592 COPY and 2592 ERASE events. We also check the retained
symbolic-column and chronological ownership certificates.
We do not infer the unbounded stream proposition from event counts alone.

## Global endpoint

We execute the authenticated 29-event schedule in its stated order:
replicas then complete low-class calls in each local sweep, native idle
residuals, equal-frame bridges and terminal exchange. We use the original
hosting certificate to preserve dirty owners outside each requested local
window and to assign the unused idle supports. Idle 9 has zero residual rank
and emits no request.

The retained local/hosting identities establish the prescribed frame advance
on each live family. We check source/target levels at each local or idle
boundary. For a bridge we require equal endpoint levels and execute

    X_dst <- X_dst XOR X_src,
    Y_src <- Y_src XOR Y_dst.

We complete the preceding scatters before the bridge reads either family.
At the final level 8 boundary we exchange the X/Y family streams. We do not
apply an extra body-half exchange: the endpoint frame interpretation already
supplies the required body action. The retained selected global identity,
local frame identities and this chronological refinement give core F_A for
each native row. We also replay the eight-family scalar identity and show
that omission of any single one of its 18 bridge shears changes that endpoint.

For the endpoint gauges, let P_t be the port-line projector in the first
eight coordinates, let E_s project onto coordinates 8 through 7+7s, and put
E_0=0 and K_s=E_[0,8)+E_s. Initially we use gauge P_t on X and zero on Y. At level s>=0
we use K_s on X and K_s-P_t on Y. Thus level 8 has gauges I_64 and I_64-P_t.
Conjugate these by the native raw g and apply T_A. After the terminal family
exchange, the original X label has final gauge T_A(I-gP_tg^-1), while the
original Y label has T_A(I). The source scalar identity restores their
decoded values. Relative to the initial gauges, the physical endpoints are

    X: T_A(I-gP_tg^-1) T_A(gP_tg^-1)=T_A(I)=F_A,
    Y: T_A(I) T_A(0)=F_A.

We use PR2195's explicit gauge convention here. Applying another body
exchange after the family exchange would change this endpoint.

More explicitly, decode a physical function by `c_i=f_i compose Gamma_i`.
MOVE and idle preserve c_i; an aligned ADD performs decoded XOR. The complete
scalar schedule returns c_i, hence
`f_i_out=f_i_in compose Gamma_i_in compose inverse(Gamma_i_out)`.
The complementary factors in the X calculation commute, so either displayed
order gives F_A. We carry the frame label with each exchanged family value.

## Complete charge and ownership ledger

Let v=C H R be one staged packet volume, with
`R=UBGS M^(2n)` and V=W N v. Let I be the supplied index-word extent and D
the serialized current directory size. Before using root coupling, retain

    D=O_q(CH(h+1)(w+1)),
    T_directory_setup=O_q(w^3+w log(C+1)),
    T_route=O_q(Jv+CH(poly(w)+J^2)), J=O_q(w).

We use ywz65's PR2590 correction for the cubic setup term. Each fresh radix
traversal performs w full-width unsigned divisions. For canonical counts,
`w^2<=q^w<=qH` and `log2(C+1)<=C` absorb setup into D. We charge the output
directory/Count disposal separately. If an h countdown uses padded index
extent I, retain its scans until the root coupling gives I=O(w).

For arbitrary B,G,S,U we form products through binary doubling/addition.
Their setup costs a fixed polynomial in the bit lengths of those factors
and the index/residue words. Positive complete multiplicities absorb the
cardinality terms; the factor `M^(2n)` absorbs fixed precision polynomials.
For fresh-row division we count 4096(w-1) small divisions, their actual quotient
lengths and the cubic radix reconstruction. We count the context's initial
H production even though the API receives a context. Its immutable q-only
compilation and source parsing contribute a finite q-dependent constant.

Under the retained generated-root coupling

    w=ceil(e^(17/10000)), n<=e, 2^(h+1)<=8e^2,

we have h=O(log w), I=O(log e)=O(w), and D=O_q(v). The inherited coefficient
allowance `O_q(e^3 w^3)` per source site is at most a fixed polynomial in w
(the retained coarse bound is w^1800). For n>=64 the complete body fibre
`q^(2nw)` absorbs that polynomial. This also pays repeated prefix reads,
normal-form preparation and restored program scans. For unrelated arbitrary
h or padded index words we claim the unabsorbed ledger, not this bound.

| Component | Complete charge and status |
| --- | --- |
| Retained ADD, atom swap, sign and leaf expansion | Written primitive bounds, with independent PR2566 audit: ADD O_q(v), swaps/signs O_q(wv), including preparation, count reads, suffix and cleanup. The first-range traces have fixed-q many events. |
| Original-offset peel | At most 63 weighted pairs on volume V; we count coefficient work and all 8 primitives per pair, giving O_q((n+w)V) in this bounded range. |
| Fresh-row split/merge, clones, native XOR and final family return | A fixed-q number of complete sequential passes, plus the binary setup above. We count both temporary output and disposal of the replaced stream. |
| Owner gather/route/inverse/scatter and directories | A fixed-q number of charged routes and full family scans, including decoration, keys, directory production and erasure. Hence O_q(wV) under coupling. |
| Local staging and live storage | We retain the protected input, peeled output when present, all W live families, 661 role packets, one private packet, transient primitive/scatter outputs, directories and arithmetic words. We bound their sum by C_q V under coupling. |
| Completed children and return | All children fit the completed below64 leaves. We count their full bodies, metadata preparation, reset and erasure, with no unpaid recursive call. |
| Larger recursion and numerical reserve | Unknown for this implementation. We do not reuse the older V+4v or 5V+19v parking constants. |

The numbers of stages, replicas, local events, low classes and finite labels
depend only on q and the fixed source. Summing these complete charges gives
`C_q V(n+w)` time and `C_q V` occupied work for this first-range node. We
include the potentially huge fixed-q compiler in C_q. We do not present these
constants as practical or as numerical reserve admission. The implementation
retains the original input and erases replaced owned streams; adding the
protected input only changes this displayed constant.

For this per-role implementation we use the following exact invocation counts:

| Operation | Count |
| --- | --- |
| Local MOVE / COPY residuals |838368N /2592N |
| Native idle residuals |63936N |
| Local XORs |6999840N |
| Local gather and local scatter |190368N each |
| Idle gather and idle scatter |63936N each |
| Owner/common routes |380736N |
| Whole-family bridge XORs |63936 |
| Terminal handle exchanges |14208 |

We therefore pay for 508608N full-family gather/scatter scans. PR2475's
coalesced scan count does not apply to this implementation. Before absorption,
we bound source/peeled/family/merged copies by 4V, staged/private work by
662v, route/residual/scatter temporaries by O_q(v)+O(V/W), and retain D plus
the old directory, numerical pages and canonical counters. This inventory
accounts for temporary copies as well as live logical data.

## Evidence boundaries and further obligations

We authenticate the entire selected catalogue, literal controller and hosting
sources. We probe actual selected common/native coefficient junctions and
check 130 address columns for a generated width 65 remainder whose last weight
differs from weight 0. We execute complete Boolean endpoints in a separate
four-family GL2 model and in a gapped three-atom model, using actual source
routes, bit primitives and expanded leaves. We check linear origins for
arbitrary dirty input columns, including COPY and ADD. We separately execute
two distinct high fields at w=2; that test samples the high cube.

We leave full GL64 Boolean payload execution open. The mathematical claim
uses the stated source/primitive refinements; the finite executions check
specific implementation implications. Larger recursive parking, a numerical
reserve inequality, complex-side transfer and formal compilation remain
separate obligations. We leave the selected exponent unchanged.
