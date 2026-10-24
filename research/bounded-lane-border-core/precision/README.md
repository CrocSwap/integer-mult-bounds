# A fixed filtered endpoint contract gives a single exact grid

Status: conditional sufficient lemma and a counterexample to a weaker
hypothesis. This does not establish the contract for the two-full source, pay
for a boundary Gaussian provider, or improve the selected multiplication bound.

The useful distinction is between a compatible filtration of the **completed
recursive interfaces** and a grading of every raw gate. The former can suffice
even when temporary gates move data in both directions. Endpoint triangularity
by itself does not suffice.

`EXTRACTION.md` gives a simpler exact recovery wrapper: a fixed number of
outermost Walsh-sign averages removes inter-grade blocks without small-delta
input magnification. The graded height theorem below supplies its arithmetic
guard as well. The delta construction remains an alternative.

## 1. Fixed-template hypotheses

Fix, before the transform rank or requested precision grows:

* a uniform rank N >= 2 and a finite family of interfaces, including every
  forward and actual same-realization inverse interface that the program calls;
* grades 0,...,H on active interface fields, with one H independent of ordinary
  recursion depth; coordinate monomials and spectator embeddings do not add
  fields to this grade set;
* a finite raw local word with at most P completed child calls, each of rank
  f = floor(e/N), and bounded dyadic Gaussian-rational free coefficients;
* exact base programs for the finitely many ranks below N, an arbitrary-input
  contract, and explicit private-field initialization/restoration.

All scalar instructions are the fixed role word of the all-column lift. They
are not tensor-powered. The fewer than N remainder axes, free phase/address
maps, and every raw local prefix have fixed height charge g. A physical address
permutation has row norm one regardless of the number of coordinates.

For a completed interface M(e), write M_l(e) for its block component whose
output grade minus input grade is l. Require M_l=0 for l<0. Its degree-zero
component must be the exact intended Gaussian direct sum, with

    height(M_0(e)) <= c0 (e+1).

For standard forward/inverse Gaussian transforms c0 can be taken as a fixed
constant because entries are in 2^-e Z[i] and row sums are at most 2^e.
This must be an exact operator identity, not a floating-point observation.

The additional substantive hypothesis is **compatible endpoint expansion**:
for each positive degree l, the completed local endpoint has an exact
expression as a sum of at most J monomials in completed homogeneous child
components and fixed coefficient/adaptor maps. A monomial uses at most Q
child factors; the sum of their positive grades is at most l. Its free factors
have total height at most g. N,H,P,Q,J,g,c0 are uniform in e. Q is a semantic
expansion count and need not equal the raw execution count P.

This hypothesis can follow from a cancellation identity in a filtered operator
algebra. Individual raw gates need not preserve grades. A rank-dependent
expansion, a relabelling that resets composed grades, or a hidden unbounded
coefficient does not meet it. All called orientations must satisfy it together.

## 2. Exact denominator and row-norm recurrence

For a Gaussian dyadic matrix X define

    d(X) = min {d >= 0 : 2^d X has Gaussian-integer entries},
    h(X) = max(d(X), log2(max(1, ||X||_infinity))).

The norm is the induced maximum row-sum norm across all active fields, not the
maximum matrix entry. Thus

    h(XY) <= h(X)+h(Y),
    h(sum of j matrices) <= max h(summand)+log2 j.

These bounds already account for the growing physical matrix dimension. No
additional field-count factor is silently discarded. Set E=g+ceil(log2 J),
and let C_l(e) be the maximum h(M_l(e)) over the finite interface family.
For l>=1 the compatible expansion gives

    C_l(e) <= E + max_(j1+...+jq <= l) sum_(i=1)^q C_ji(f), q<=Q.

The degree-zero terms in this sum cost at most Q c0(f+1). At most l factors
have positive grade, and their grades sum to at most l. Suppose inductively
C_j(f)<=K j(f+1) for j>0. Then

    C_l(e) <= K l(f+1) + Q c0(f+1) + E.

Since e>=Nf and f>=1 at an internal node, this is at most K l(e+1) whenever

    K >= (2 Q c0 + E)/(N-1).

Enlarge K to cover the finitely many positive-degree base cases. This proves
C_l(e)<=K l(e+1). The e+1 convention covers zero-rank base maps without
pretending that they have zero height. Summing the H+1 homogeneous components
gives a fixed Kstar with

    h(M(e)) <= Kstar (e+1).

For example Kstar=max(c0,KH)+ceil(log2(H+1)) suffices; for H=0 retain c0.

Now let A(e) bound the height of every actual temporary map from the node's
incoming active data, including all private fields. A parent prefix before
the currently active child contains at most P completed children and a fixed
free word. Therefore

    A(e) <= A(f) + P Kstar(f+1) + g.

This gives A(e)<=Astar(e+1), after covering the finite base cases and choosing
Astar >= (2 P Kstar+g)/(N-1). The argument uses completed child semantics for
siblings and an execution prefix for the one active child. It does not infer
temporary bounds from the endpoint alone, and it does not multiply the
internal height of every completed child in a serial product.

## 3. One outer scaling and exact recovery

Let W_e=G_e+sum_(l=1)^H W_(e,l) be the completed filtered program, with G_e the
Gaussian degree-zero target. Choose a fixed Kbar such that

    sum_(l=1)^H ||W_(e,l)||_infinity <= 2^(Kbar(e+1)).

For delta=2^-s and D_delta=diag(delta^grade), one has exactly

    D_delta W_e D_delta^-1
      = G_e + sum_(l=1)^H delta^l W_(e,l).

Assume incoming complex coordinates lie on grid 2^-b, have magnitude at most
2^m, where b,m are nonnegative integers, and G_e has entries in 2^-e Z[i].
The exact Gaussian output lies on grid
2^-(b+e). Choosing

    s >= b + e + m + Kbar(e+1) + 3

makes the error at most one eighth of this mesh when s is an integer. Separate nearest-grid rounding
of real and imaginary parts therefore recovers G_e x exactly. For an absolute
error below 2^-k instead, s>=k+m+Kbar(e+1)+2 suffices.

The pre-scaling D_delta^-1 multiplies coordinates by integers. Hence it keeps
the incoming grid 2^-b valid and increases the magnitude exponent by at most
Hs. Execute **all levels exactly on one common grid**

    2^-(b+ceil(Astar(e+1))).

All intermediate numerators then fit in

    b + m + Hs + 2 ceil(Astar(e+1)) + O(1)
      = (H+1)b + (H+1)m + O(e+1)

bits per real component for exact recovery. The constants depend on the fixed
template and H. No child is rounded, rescales its precision budget, or adopts
a new grid upon return. Final D_delta scaling and nearest-grid recovery can
be performed directly by integer shifts and rounding; materializing an exact
output grid with every trailing zero is unnecessary.

This is an additive guard linear in e with a single constant multiplier on
the requested data precision. In a setting e<=c p^epsilon, epsilon<1, it is
O(p) word width. It does not establish native storage/movement or scalar bit
cost by itself. Those costs, finite row stock, and any boundary providers must
be supplied separately under the fixed-tape closure contract. It also does
not justify letting N or H grow with the eventual multiplication input.

## 4. Why completed height alone is insufficient

Let U(a)=I+aE12 on three roles. Let P cyclically permute basis vectors
1->2->3->1, and let Q swap 2 and 3. With [A,B]=ABA^-1B^-1 define

    Phi(A)=Q [A,PAP^-1] Q^-1.

Exact multiplication gives Phi(U(a))=U(a^2). Applying Phi twice uses sixteen
child/inverse calls and gives U(a^4). Set S_1=U(2) and
S_(2f)=Phi(Phi(S_f)). For e=2^d this yields S_e=U(2^(e^2)).

Every returned endpoint has identity Gaussian diagonal and a single
off-diagonal edge, admitting height one. Its coefficient nevertheless needs
e^2+1 numerator bits. Four positive child grades contribute to an output that
has been relabelled as degree one, violating the compatible expansion.

The accompanying independent review also gives a fixed rank-two 74-call
version with the full nontrivial Gaussian diagonal G_e, using the order-four
Gaussian and fixed dyadic shear-extraction conjugations. Thus the problem is
not an artifact of using identity targets. The example is deliberately
inefficient and is only a counterexample to an overbroad sufficiency claim.

## 5. Application gate and open next questions

The noncyclic-lane construction being checked in parallel has a promising
compatible algebraic endpoint. For lower-triangular lane A with equal diagonal
a0 and actual inverse B, let S be the forward partial shift, R its reverse,
P0 the first-lane projector, and

    T(B)=SBR+b0P0,  b0=a0^-1.

Then T is multiplicative on this algebra, T(A)S=SA, and

    E(A) = [[A,0],[S(I-B),T(B)]],
    E(A)^-1 = [[B,0],[S(B-I),T(A)]].

These are filtered polynomial endpoints although raw R lowers grade. They fit
the height theorem if all actual child calls and boundaries have the stated
uniform interface. This is not yet a complete recursive implementation.
In particular, abstractly iterating a core on V direct-sum V doubles its
payload at each step; it does not prove that one fixed finite native interface
family or one uniform N realizes that recursion.

In particular, an exact boundary b0 cannot be priced as a one-lane recursive
call merely because it is the diagonal of an L-lane recursive B. Running B on
a vector supported in the first lane still costs the whole L-lane program.
Packing or supplying those exact diagonal boundary jobs needs its own proved
arbitrary-input, storage, and paid-profile contract. A direct Gaussian fallback
can have a worse asymptotic cost even at a small fixed boundary density.

Open next questions:

* Prove the finite native caller and actual inverse satisfy compatible endpoint
  expansion on arbitrary inputs, including source complements, exits, frames,
  owned-center restoration, and fresh Gaussian factors.
* Price exact boundary Gaussian jobs without assuming access to a child's
  diagonal component at the cost of one ordinary scalar-lane child.
* Show the required common H is fixed through ordinary recursion and all
  allowed native interface changes; endpoint acyclicity is insufficient.
* Transport the one-grid representation through the explicit fixed-tape and
  integer-multiplication bit interfaces before asserting an improved bound.

## Sources, attribution, and verification

Repository base: f259dabc7d70e0db8d6d36bfda888f008bbfecc1.

This extends the exact-Gaussian semantic-height argument in
`research/higher-moment-strictification/vendor/FINITE-TEMPLATE-CLOSURE.md` and
respects the whole-job and fixed-template obligations in its neighboring
`FINITE-PRECOMPILATION.md`. It develops the one-time conjugation question in
the prior `border-interface-continuation/triangular-matching` checkpoint
9fec4899e332d8a2afc928dd4cfb59ee8925a096. None of those predecessor files is
modified. The partial-shift endpoint in Section 5 is credited to the parallel
lane-cut investigation; this note contributes the graded height/grid theorem
and the boundary-provider caveat.

The proof above is symbolic. `verify_counterexample.py` checks exact rational
instances of the shear word and its inverse, extraction conjugations, the
nontrivial order-four Gaussian factor in a 12-dimensional exact realification,
and growth through rank 64. Checks remain active under Python optimization.
`REVIEW.md` records a separate subagent's derivation
and its full-Gaussian-diagonal strengthening. These finite checks do not
replace the universal algebraic proofs or establish the missing application
contracts.

Prepared with OpenAI Codex assistance, October 23, 2026.
