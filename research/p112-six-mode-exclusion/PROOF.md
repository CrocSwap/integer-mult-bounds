# The selected bilateral six-mode family costs at least 297

## 1. Statement and fixed architecture

Use the 112 physical ports and binary group spaces
`E_0,...,E_37` specified by [CANDIDATE.json](CANDIDATE.json) and its
authenticated source data. Group 0 has one payload coordinate; every other
group has three. For physical group sets `A,B`, write

    rho(A,B) = rank_F2 of the pairing between sum_(g in A) E_g
                                      and sum_(h in B) E_h.

A rational vector touches a group when at least one of that group's payload
coordinates is nonzero. The charge of `u v^T` is `rho(supp(u),supp(v))`, using
the COMPLETE physical group spaces. It is not the rank of just the active
individual label rows. Decoder coefficients and the factorization below are
over Q; only this physical tariff is computed over F2.

There are 18 matched pairs `(G_(2i+1),G_(2i+2))`, indexed by `0 <= i < 18`,
and the final triad `G_37`. Let a canonical coordinate vector consist of
`z_i in Q^3` for these 18 pairs and `z_J in Q^3`. Define the injective
112-by-57 map `R` by

    (Rz)_(2i+1) = (Rz)_(2i+2) = z_i,
    (Rz)_37 = z_J,
    (Rz)_0 = (z_7)_2.

Payload coordinates in this note are numbered 1,2,3. Thus the residual line
uses coordinate 2 of groups 15 and 16. Fix the endpoint

    K = R R^T,              rank(K) = 57.

Its diagonal blocks are identities, and its nonzero cross blocks are allowed
by the pinned physical mask. In particular this is one specified fitting
matrix, not an arbitrary assignment of its free blocks.

Assign the paired roles to six modes by

    sigma = [1,2,0,2,3,0,0,4,5,5,4,2,4,3,1,5,3,1].

For `j=0,...,5`, define `e_j` to be the physical vector whose coordinate 1
in even group `G_(2i+2)` is 1 when `sigma_i=j`, with all other entries zero.
In particular these six vectors have zero odd, residual, and final-triad
entries. The common source and reader space is

    S = col(R) + span_Q(e_0,...,e_5),             dim(S) = 63.

The sum is direct, because restricting to the odd groups and `G_37` recovers
the 57 canonical coordinates and each mode has a nonempty even support.
The canonical retraction is

    pi(Rz + sum_j alpha_j e_j) = Rz.

**Theorem.** For every finite rational factorization

    K = sum_(t=1)^m u_t v_t^T,       u_t,v_t in S,

the total whole-group charge is at least 297.

There is no restriction on the original term count, rational denominators,
factor ranks, or mixing of the three payload coordinates within S. Zero
outer products may be discarded. The conclusion concerns these specified
aligned spaces and this fixed K. Other partitions, other exterior spaces,
relative source/reader geometries, and other fitting matrices are not covered.
No construction attaining 297, decoder costing at most 296, or improved
multiplication exponent is asserted.

## 2. The canonical invoice, with its high-price excess retained

First consider any nonzero-term decomposition of K whose sources and
readers lie in `col(R)`. Restricting to the odd coordinates and `G_37`
gives a rank-one decomposition of `I_57`.

Put `H_i=E_(2i+1)+E_(2i+2)` and `J=E_37`. A nonzero canonical component
on role i touches both complete physical triads, so its support contains
`H_i`. Ignoring the residual can only lower a tariff. The registered
verifiers regenerate the following geometric premises:

* `rho(J,J)=rho(J,H_i)=rho(H_i,J)=3`;
* every `rho(H_i,H_j)` is at least 4;
* every `rho(J+H_i,J+H_j)` is at least 6;
* the join closure of the 19 component spaces has 40 spans, including zero.

For each span, membership means ALL component spaces contained in it, not
just a convenient generating subset. The complete cheap-rectangle census is

| Pairing rank | Maximal left/right component counts | Ordered rectangles |
|---|---|---:|
| 4 | 1 by 1 | 20 |
| 5 | 1 by 1 | 178 |
| 5 | 1 by 2 or 2 by 1 | 66 |
| 5 | 1 by 3 or 3 by 1 | 8 |

These 272 rectangles have disjoint component supports. Both sides contain
an ordinary paired component. The same support/probability bounds remain
valid after deleting J.

Let n be the number of nonzero canonical terms and p the number with a
side confined to J. Such pure terms cost exactly 3. Let `L_4,L_5` count
nonpure terms of actual canonical tariff 4 and 5, and define

    D = 2 L_4 + L_5,
    E = sum_(nonpure terms) max(canonical tariff - 6, 0).

Thus the exact invoice is `C_can = 6n - 3p - D + E`.

Order the 19 components uniformly at random. Select a cheap nonpure term
when all its source components precede all its reader components. The
displayed census gives probability at least 1/2 for tariff 4 and at least
1/4 for tariff 5. This remains true if the actual tariff includes residual
cost: removing the residual only decreases the underlying tariff.
The selected sum is strictly block triangular, so its subtraction from
`I_57` has rank 57. The remaining terms must therefore number at least 57.
Taking expectations gives `D <= 4(n-57)`.

Repeat after deleting J, leaving `I_54`. Exactly the p pure terms disappear.
Every other term has a nonzero ordinary component on both sides. The same
actual `L_4,L_5` terms have at least the preceding selection probabilities,
so `D <= 4(n-p-54)`. One quarter of the first inequality plus three
quarters of the second yields

    D <= 4n - 3p - 219,
    C_can >= 2n + 219 + E.                         (1)

The residual unit has not yet been added to this bound. In particular,
replacing 219 by 220 while retaining the same E without a further argument
would count the same excess twice.

## 3. Complete support catalogues and effective loss

The binary join closure of the 38 physical group spaces has 2,213 elements.
For each W, let `A(W)` contain every physical group wholly contained in W.
Solve the rational linear equations requiring a vector in S to vanish
outside `A(W)`. This produces the full support intersection `S_W`.
The union of the supports of a basis is its generic support; similarly
record the generic support of its canonical projection. Deduplicating gives
80 nonzero ambient support intersections.

This is a complete bound for individual vectors, not an assumption that
every vector is generic. For a given nonzero u, take W to be the binary span
of its actual group support. The generic actual support of `S_W` spans
exactly W: it contains the support of u and is itself contained in W. Its
projected support contains the actual support of `pi(u)`. Hence the actual
tariff is unchanged by using the generic actual spans, while the projected
tariff may only increase. The resulting effective loss is an upper bound
for that individual factor.

For a term whose two canonical projections are nonzero, set

    delta = min(canonical projected tariff, 6) - actual tariff.

The exact 80-by-80 census verifies that every positive delta is at most 2.
For each side, the kernel of pi consists of the combinations of the six
disjoint even-half mode vectors. Its nonzero physical supports are precisely
the 63 nonempty mode unions. Pricing these supports against all 80 opposite
strata gives minimum 3. Thus every original term killed by the canonical
projection costs at least 3; the weaker bound 2 will suffice below.

The actual minimum over the whole family is 1. Consequently the preceding
projection-zero bound must not be applied to an unrelated compression or
to arbitrary terms.

Apply pi on both sides of a factorization of K. The endpoint remains K.
For its n surviving terms, subtracting E from (1) and then accounting for
their deltas gives

    C >= 2m + 219 - sum_(surviving terms) delta.     (2)

Here the terms discarded by pi supplied at least 2 each. This argument
allows any number of original or projected terms.

### The mandatory negative-loss term

Since `K_00=1`, some term has both residual coefficients nonzero. On each
side, coordinate 2 in both groups 15 and 16 equals that residual coefficient;
the added modes affect only coordinate 1. The term therefore touches
groups `{0,15,16}` on both sides. Their exactly checked self-tariff is 7.
This term survives pi and has delta at most `6-7=-1`.

Let `N_1,N_2` count surviving terms with delta at least 1 and at least 2.
Retaining this one negative delta in (2) gives

    C >= 2m + 220 - N_1 - N_2.                    (3)

The extra unit comes from an actual negative loss after E has been removed;
it is not a second addition of the projected high-price excess. The direct
57-column R decomposition has invoice 334 and checks this distinction.

## 4. Joint subspace covers and proportional coalescence

Consider any source subspace L and reader subspace M that cover a set of
factor types: each covered term has its source in L or its reader in M.
Let their canonical intersections, expressed in the dual retained
57-coordinate system, be C and D. Put

    a = dim(C),  b = dim(D),
    kappa = a + b - rank_Q(C^T D).

The notation `C^T D` uses column bases for these subspaces; the rank does
not depend on the bases. Quotienting the source and reader ambient spaces
by L and M kills every covered term. The endpoint after quotienting has
rank `57-kappa`: the identity pairing restricted to the two quotient maps
has this rank. Equivalently, the kernel of the source quotient has dimension
a, and its intersection with the image of the reader quotient has dimension
`a-rank(C^T D)`.
Thus the number of covered terms is at most

    m - 57 + kappa.                               (4)

This uses no independence or minimal-term hypothesis. Pairing the physical
112-coordinate vectors instead of the dual canonical coordinates would
not justify (4).

The ambient threshold-1 certificate is a symmetric joint cover with
canonical intersection dimension 39. Its pairing rank is also 39, hence

    N_1 <= m - 18.                                (5)

For threshold 2 the certificate lists four source lines and four reader
lines. Each is an actual one-dimensional rational support intersection.
On either side, their nonzero quotient coordinates are the four distinct
axes

    F = {0,2,3,5}.                                (6)

The verifiers check both the line dimensions and coverage of every positive
threshold-2 rectangle.

If two sources are proportional, absorb the scalars into their readers and
replace the two terms by the common source times the reader sum. The new
reader support is contained in the union. Pairing rank is subadditive on
such unions, so total cost cannot increase. This preserves S and the
endpoint. The transposed operation applies to proportional readers; zero
sums are dropped. Alternating these operations terminates, because each
operation strictly decreases the finite term count.

We may therefore work with a representative having no repeated source line
and no repeated reader line. At most one term can use each of the certified
lines on a given side. This is valid simultaneously for both line covers.

**Coalescence can lower the opposite factor rank.** All ranks and term
counts from this point concern the coalesced representative. A full rank
in the original factorization must not be transferred to it without proof.

## 5. A target invoice leaves at most one quotient defect

The endpoint inclusion implies `col(K) subset col(U)` and
`row(K) subset col(V)`. Since `S=col(R) direct-sum span(e_j)`, the actual
coalesced factor spans are

    col(U) = col(R) + H_s,       col(V) = col(R) + H_t,

for quotient subspaces `H_s,H_t` in `Q^6`. Write their dimensions as s,t.
Let a,b count the coordinate axes in F that belong to these actual
quotient spaces. A certified loss-2 line can occur only when its quotient
axis belongs to the corresponding H. Coalescence therefore gives
`N_2 <= a+b`.

Sylvester's inequality gives `m >= 57+s+t`. Write
`e=m-57-s-t`, a nonnegative integer. Combining (3) and (5),

    C >= m + 238 - a - b
      = 295 + (s-a) + (t-b) + e.                  (7)

The last three summands are nonnegative integers. Under the contradiction
hypothesis `C <= 296`, their sum is at most 1. Hence both quotient spaces
are coordinate spans of subsets of F, except that at most one side can
have one additional rational direction. In that latter case e is zero.
For the entirely coordinate case e can be 0 or 1.

## 6. A support-preserving gauge removes continuous parameters

Transpose if necessary so that the possible extra direction is on the
source side. This preserves S, K, and the symmetric physical tariff.
The source quotient is `span(A,v)`, where `A subset F` is a set of
coordinate axes. Subtract v's components on A, and let its remaining
nonempty support be `J subset {0,...,5} \ A`. The reader quotient is
the coordinate span of `B subset F`.

For each original mode j in J, scale payload coordinate 1 in BOTH halves
of every role assigned to that mode by `1/v_j` on the source side and
by `v_j` on the reader side. Use scale 1 elsewhere. These invertible
within-group maps preserve every complete-group zero pattern and tariff.
They preserve K because the paired blocks use matching dual scalings;
the residual uses coordinate 2 and the final triad is untouched. They
also preserve the ambient S, since the scaling is uniform within each
original mode.

On the quotient, v becomes the indicator of J. A and the opposite
coordinate space B remain invariant. Canonical components are absorbed
into `col(R)`. Consequently all rational amplitudes in the extra line are
covered by the finite source space which retains the A modes separately,
merges the J modes into one mode, and drops all other modes. The reader
retains B separately. Nonuniform scaling within one original mode is not
used and would not justify this reduction.

## 7. Complete finite certificate and contradiction

Enumerate

    A,B subset F,
    nonempty J subset {0,...,5} \ A.

There are

    16 * sum_(A subset F) (2^(6-|A|)-1)
      = 16 * (4*3^4 - 16) = 4,928

ordered families. A singleton J in F represents an entirely coordinate
source space, for which both `e=0` and `e=1` are retained. Every other J
uses the one available quotient defect and requires `e=0`. These choices
give 5,440 admissible family/term-count cases. The source-zero,
reader-nonzero cases occur after transposition. If both quotients are
zero, (1) and the mandatory residual unit already give cost at least 334.

For every family, the verifiers reconstruct its complete source and reader
support intersections and every ordered effective-loss threshold. Reusing
the ambient catalogue is sufficient: each restricted space is a subspace
of S, and all coordinates that vanish identically on an ambient support
intersection also vanish on its restricted intersection.

[CERTIFICATE.json](CERTIFICATE.json) stores physical support masks for each
joint cover and, where used, for its source/reader line cover. It does not
ask the verifier to trust a claimed floor. The checks reconstruct the
corresponding rational subspaces, verify every threshold edge is covered,
compute the exact canonical intersection and pairing ranks, and verify
that every line used by a line cap is one-dimensional. A cover need not
be optimal to prove its inequality.

Let `kappa_j` be a checked joint-cover constant at threshold j and let
`b_j` be a checked line cap when supplied. For each admissible m the
verified lower bound is

    2m + 220
      - sum_(positive thresholds j) min(m, m-57+kappa_j, b_j),             (8)

omitting `b_j` when no line cap is used. Both independently implemented
registered replays check the full finite domain and recompute (8).

| Finite obligation | Verified value |
|---|---:|
| Quotient families | 4,928 |
| Admissible term-count cases | 5,440 |
| Smallest bound in (8) | 297 |
| Cases with a bound at most 296 | 0 |

Every putative cost-at-most-296 factorization has a coalesced, gauged
representative in this complete domain. Equation (8) contradicts its
invoice. Since all tariffs, and hence the total invoice, are integers,
the theorem follows: every factorization in the stated family costs at
least 297.

The finite certificate verifies exact geometric inequalities needed by
the algebraic proof. It is not an exhaustive enumeration of rational
coefficients and does not claim that the lower bound is attained.

## 8. Provenance and remaining scope

The physical cover and rank tariff are the pinned PR2757 predecessor data;
the exact archive, member and candidate identities are recorded in
[SOURCES.json](SOURCES.json). The canonical acyclic accounting is included
above rather than relying on an unpublished scratch computation. The new
steps are the selected bilateral support cover, retained negative residual
loss, quotient-defect reduction, support-preserving finite gauge, and
complete checked cover certificate.

The proof leaves other partitions, other two-sided exterior spaces, and
other fitting matrices open. It provides no target decoder, full supplier
invoice, or selected-bound update. Further constructive research lies
outside this contribution.

Prepared with OpenAI Codex assistance and independent agent checks.
Those checks are not human mathematical review or a proof-assistant
formalization. The package follows the repository's Apache-2.0 license.
