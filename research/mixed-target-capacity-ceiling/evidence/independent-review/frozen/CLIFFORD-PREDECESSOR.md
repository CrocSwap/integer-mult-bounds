# A source-bound obstruction for the explicit Clifford control class

Status: local derivation awaiting separate review. No public theorem, solver,
native/emitter/compiler/Lean replay, complete caller, or new kappa is claimed.

This answers a precise part of Dillon's released two-FULL/one-query handoff,
Discussion 4930 comment 19143357. The new bounded investigation is rooted at
comment 19143614. The public handoff is a sufficient construction target; no
successful t0 was supplied. Its physical FREE class is not fully enumerated.
The theorem below explicitly restricts that class to fixed finite columnwise
monomial Clifford words and scalar owner programs. It does not silently replace
physical FREE by parity-even operators or by every unit of an abstract algebra.

## Pinned input

The scientific source is canonical commit
`4c0a359d88f22f05189d51f48387750b801a45d4`, package
`research/coded-native-caller`. Exact retained files and hashes are in
`SOURCES.json` and `frozen/`. Governing guidance was read at canonical
`20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`.

There are 112 owners. The real scalar code A is invertible, has zero diagonal,
and has 52 nonzero entries in every row and column. Each source normalizer is
K_i = Z_(z_i) P_(G_i), with G_i an orthogonal binary 9 by 9 matrix and
G_i e_q = q_i. The 112 vectors q_i are distinct, of weight 3 or 7. These exact
properties were checked directly from CODE.json and NORMALIZERS.json; the
check did not invoke the source operator evaluator.

Embed one copy K_(1,i) on the central axis q and the eight first-stage axes U,
and another K_(3,i) on q and the eight third-stage axes W. The full address
space has exactly 17 axes. The sets {q}, U, W are disjoint. G rows are used as
rows, not columns. Every operator is lifted columnwise; scalar owner matrices
are applied once, rather than tensoring an owner sum.

Let Q be the central Gaussian, D3 the product of the eight third-stage
Gaussians, and

    C_s[i,j] = A[i,j] K_(s,i)^-1 K_(s,j).

Dillon's four required controls are

    t0, Q^-1 t0 Q, t = D3 t0 D3^-1,
    E = Q^-1 C3 t C1 Q^-1,

including their explicitly implementable inverses. The main endpoint is

    F3 J(t0) F1 = [[0,t],[-E,0]] diag(G,G),
    G = D1 D3 Q.

## Exact scope of the obstruction

Let H be the projective group of monomial Clifford operators on the actual
17 one-column address bits. A control in the tested class is a fixed finite
scalar owner program in columnwise lifts h^(tensor f), h in H. Owned copies,
temporary fields and clears are allowed as long as the resulting main block
has such a finite linear expansion. Coefficients may depend on f; the set of
letters is fixed independently of f. Projective phases are absorbed into the
scalar coefficients, including their correct f dependence.

This is a generous algebraic model of the source's explicit P/D/X/phase
Clifford words and owner ADD programs. It gives no automatic physical tariff
or inverse implementation to an arbitrary algebra element. The completed
obstruction needs neither tariff nor inverse sufficiency: it rules out every
nonzero t0 in this declared class satisfying the four memberships at all
sufficiently large f. Section 4 also gives a direct scalar-owner proof which
does not require the transported-class argument.

It does not cover arbitrary nonlinear monomial address maps, general
non-Clifford phases, or a number/alphabet of letters growing with f. It also
does not cover a changed FULL controller, extra paid calls, extra axes, a
different productive endpoint, or a different source code.

## 1. Why all-width membership becomes support membership

For any finite collection of pairwise nonproportional nonzero operator
vectors v_1,...,v_m, their tensor powers are linearly independent for every
f >= m-1. For each i and j != i choose a linear functional ell_(i,j) that
kills v_j but not v_i. The tensor product of these m-1 functionals kills
every v_j^(tensor(m-1)) except i. Additional factors nonzero on v_i extend
the argument to any larger f. This elementary argument also allows
width-dependent scalar coefficients.

Apply the lemma to the finite projective Clifford alphabet containing all
letters in the fixed proposed programs and their conjugates. If t0 and its
Q and D3 conjugates are all represented by monomial Clifford programs at
every positive width, then at sufficiently large width every surviving
letter of t0 lies in

    H0 = H intersect Q H Q^-1 intersect D3^-1 H D3.

Conjugate t0 by D3. Its support is in Ht = D3 H0 D3^-1. The following
observations do not identify Ht with H0:

* t is monomial by hypothesis;
* D3^-1 t D3 = t0 is monomial, and conjugation by D3^2 shows that
  D3 t D3^-1 is monomial as well;
* Q^-1 t Q = D3 (Q^-1 t0 Q) D3^-1 is not automatically monomial from
  those statements alone.

The last bullet is an essential warning: it cannot be inferred merely from
the three displayed controls. Consequently, the proof below uses the exact
support class for t, not an unjustified assertion that t is again in H0.

Define instead

    Ht = D3 H0 D3^-1.

Every surviving letter of t lies in Ht. The next section derives the actual
invariants of this transported class directly.

## 2. Lagrangian invariants, including the D3 transport

Use binary symplectic coordinates (x,z), with the computational Lagrangian
L0 = {(0,z)}. Let Lq = Q L0 and Lw = D3 L0. Their X projections are
span(e_q) and W respectively. Q and D3 have order two on binary symplectic
space even though their operator squares retain phases/Paulis.

A monomial Clifford h has symplectic form

    x' = R x,
    z' = S x + R^-T z,

where R is invertible. For h in H0, it preserves L0, Lq and Lw.
Therefore R e_q = e_q and R W = W. This is the source-fixed flag constraint;
it does not identify every parity-even word with a physical free operation.

For a transported letter k = D3 h D3^-1 in Ht:

* k preserves L0 because h preserves Lw;
* k preserves Lw because h preserves L0 and D3^2 L0 = L0;
* k preserves Lqw = D3 Q L0 because h preserves Lq.

Thus its invertible X block R_k preserves W. The X projection of Lqw is
span(e_q) plus W. Hence R_k preserves span(e_q) plus W as well. On the
quotient by W, R_k therefore fixes the nonzero central class [e_q].
This is weaker than R_k e_q=e_q, and is exactly the distinction required
by the released warning about transport through D3.

For nonzero v in span(e_q) plus U and nonzero w in span(e_q) plus W, define the rank-one
Gaussian chart L(v) = {(v v^T z,z)}. If k L(v) = L(w), its X projections
give R_k v = w. Passing to the quotient by W and using invertibility and
the fixed central class implies v=e_q. It does NOT imply w=e_q: w may
equal e_q plus a vector in W.

This one-sided conclusion is sufficient for a useful obstruction below.

## 3. No monomial endpoint component

Expand an endpoint block E[i,j]. Every term is a scalar multiple of

    Q^-1 K_(3,i)^-1 K_(3,r) k K_(1,s)^-1 K_(1,j) Q^-1,
    k in Ht,

with scalar A[i,r] b[r,s,k] A[s,j], where b are the coefficients of t.

For this word to be monomial, k must carry

    L(G_(1,s)^-1 q_j) to L(G_(3,r)^-1 q_i).

Section 2 forces G_(1,s)^-1 q_j=e_q, so s=j by distinctness of the source
q vectors. But A[j,j]=0. Every term with a nonzero source coefficient is
therefore outside H. This conclusion does not require r=i.

No uniqueness assertion for different intermediate owners is needed.
Group together any projectively equal nonmonomial terms. Their sum still
has support outside H; cancellation can remove classes but cannot create
a class in H. At all sufficiently large widths, section 1 makes the span
of these remaining nonmonomial classes disjoint from the span of the
finite monomial alphabet in any proposed FREE implementation of E.

Consequently, if E is also FREE, E=0 at every such width. The exact source
codes C1,C3 and Q are invertible, so E=Q^-1 C3 t C1 Q^-1=0 implies t=0,
then t0=0. In particular the handoff's required invertible t0 cannot exist
inside this fixed finite columnwise monomial-Clifford control class.

This result does not mistake Ht for H0. In fact Ht permits R_k e_q=e_q+w
with nonzero w in W. The proof needs only the induced quotient action and
the resulting one-sided equality s=j. It also does not need a uniform
inverse bound: the source code inverses are exact, and all four requested
inverse programs are rendered moot by the forward obstruction.

For arbitrary width-dependent scalar coefficients, the exact conclusion
is t0_f=0 at every sufficiently large width satisfying the four
memberships. A family nonzero only at finitely many small widths is not
excluded, but cannot satisfy the all-width invertibility contract.

## 4. Completed scoped theorem: scalar owner interleavers

For t0 = B tensor I, all first three controls equal B tensor I and t=t0.
Its inverses, when supplied by an explicit scalar program, are physically
legal in the same scalar class. Each term of E[i,j] is now

    A[i,r] B[r,s] A[s,j]
    * Q^-1 K_(3,i)^-1 K_(3,r) K_(1,s)^-1 K_(1,j) Q^-1.

The signed linear permutation between the two Q^-1 factors has binary map

    M = G_(3,i)^-1 G_(3,r) G_(1,s)^-1 G_(1,j).

For a signed orthogonal permutation M, Q^-1 M Q^-1 is monomial exactly
when M e_q=e_q. If the directions differ, the two central Gaussian factors
produce four distinct translations, all with nonzero coefficient; if they
agree, their equal or opposite signs give a single monomial. This includes
absolute-sign choices and does not tensor a scalar sum.

Here M e_q=e_q is equivalent to

    G_(3,r) G_(1,s)^-1 q_j = q_i.

The first-stage component can vanish only if G_(1,s)^-1 q_j=e_q,
so s=j; then distinct third-stage q vectors force r=i. Both source diagonal
entries are zero. Thus every nonzero term is nonmonomial.

For fixed i,j, terms indexed by distinct pairs (r,s) are projectively
distinct. Equality would imply

    G_(3,r')^-1 G_(3,r) = G_(1,s')^-1 G_(1,s).

The left map is supported on q+W and the right on q+U. Their intersection
contains only the identity binary linear map: both must fix U and W, and
an invertible map on the single common bit fixes q. Distinct q vectors then
give r=r' and s=s'. Conjugating by the fixed outside factors preserves
projective distinctness. Signed phases cannot change this argument.

For any nonzero B[r,s], choose i with A[i,r] nonzero and j with A[s,j]
nonzero (there are 52 choices each). The corresponding nonmonomial term has
nonzero coefficient and cannot cancel. Uniform tensor separation against
any proposed fixed finite columnwise monomial alphabet rules out a FREE
representation of E at all sufficiently large widths.

Hence no fixed nonzero scalar owner matrix B, including a dense one,
satisfies the fourth condition uniformly in that model. If coefficients
depend on f, the precise conclusion is B_f=0 at every sufficiently large
width where the endpoint belongs to the declared monomial span. This
excludes every all-width invertible family B_f; it does not exclude a family
supported only at finitely many small widths.
This theorem does not rely on classifying the whole physical FREE algebra.

## Credit and open next question

Credit Dillon for the released construction equations, the real normalizers
and their charged recoding; Dugongue/mdumitrean for PR4929 and A; Cao Yifan
for the native word; Cinna Davis, zxv, Jacob Alan Sussman, Ryanson Jonathan,
and the full retained native/helper/Clifford/compiler lineage. The elementary
uniform tensor-separation device is already used in the preceding projective
operator work; it is not claimed as a new theorem. New local analysis has
substantial OpenAI Codex assistance and no independent human or kernel
acceptance.

The useful continuation must change at least one declared hypothesis:
the fixed columnwise monomial-Clifford control class, the sufficient four
FREE conditions (replacing some with an explicitly paid and affordable
operator), the source code, the productive target, or the controller.
Merely adding more Clifford owner/address couplings cannot create a
monomial component. A test that assumes R_k e_q=e_q after D3 transport
repeats the released error and must be rejected.
