# Reconstruction without primitive decomposition

## Statement and credit boundary

Let K be any field with exact arithmetic. Given an n by n by n tensor over K,
there is a deterministic O(n^7) field-operation test for isotopy to multiplication
in a commutative unital n-dimensional K-algebra. Acceptance returns the algebra
table and three invertible maps U,V,W satisfying

    t(Ua,Vb) = W mu(a,b).

The test uses linear algebra, ideal products and at most n coordinate probes
for each of two modules. It does not enumerate K, factor polynomials, compute
primitive idempotents or search all possible slices. The operation bound counts
exact field addition, multiplication, inversion and equality. It is not a
rational bit-complexity bound or a bound for constructing an input field.

Ali Romman's [PR5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540)
already gives the nucleus/regular-module reconstruction and a fixed-prime
polynomial algorithm using primitive components. Its reconstruction theorem
is a cited predecessor. The new repository step is this decomposition-free,
uniform field-operation implementation and bound, including the maximal cyclic
summand returned by the explicit saturation procedure below.

Deterministic cyclicity algorithms are established. In particular,
H. W. Lenstra Jr. and A. Silverberg,
[Determining cyclicity of finite modules](https://arxiv.org/abs/1501.00183v2),
2015, prove a stronger finite-ring cyclicity result. Their algorithm uses
annihilators and successive quotients. No priority is claimed here for deciding
cyclicity in polynomial time. The following proof specifies the particular
fixed-power quotient-annihilator procedure used in this package and its tensor
application. Artinian local structure and Nakayama's lemma are classical.

## 1. The saturated quotient annihilator

Let A be a commutative unital K-algebra of dimension a>=1 and M an A-module
of dimension d>=1. For v in M define

    Q(v) = Ann_A(M/Av) = {b in A : bM is contained in Av}.

This is an ideal. It is computed by linear equations: obtain a basis of the
linear functionals killing Av, and require each such functional to kill
b times every coordinate vector of M. There are at most d^2 equations in a
unknowns. In particular this is not Ann_A(v).

Use the classical decomposition A=product A_i into local Artinian algebras,
only in the proof. Write m_i for the maximal ideal of A_i and M_i for its
module component. Each m_i^a is zero. Indeed a nonzero step of its power
chain strictly decreases dimension, since equality of successive powers and
Nakayama would force that power to be zero.

The component Q(v)_i equals A_i exactly when A_i v_i=M_i. Otherwise it is a
proper ideal, so is contained in m_i. Consequently

    Q(v)^a = e(v) A,
    e(v)_i = 1 if A_i v_i=M_i, and 0 otherwise.             (1)

Thus Q(v)^a has its own identity e(v), an idempotent of A. Compute the power
by at most a-1 products and spans, starting with Q(v). Its identity is the
unique element e in that ideal satisfying e s=s for every ideal-basis vector
s. These are linear equations in the coordinates of e inside the ideal.
For the zero ideal the identity is zero. Equation (1) proves existence and
uniqueness; the implementation also checks the identity and e^2=e.

An early fixed point of the ideal-power chain is safe: if J^(k+1)=J^k, every
later power equals J^k. No unbounded stabilization loop is needed.

## 2. A bounded basis scan

Let w_1,...,w_d be any K-basis of M. Start with e=0,v=0. For each w_j set

    z = v + (1-e) w_j,
    e_new = identity of Q(z)^a,
    v_new = e_new z.

Replace e,v by e_new,v_new. Stop early when e=1, or after d probes.

Inductively v=e v and Av=eM. On a component already included in e, z=v,
so that component is still generated. Thus e e_new=e. On a new component,
z=w_j. Equation (1) includes that component exactly when w_j generates it.
Projecting z onto e_new removes its ungenerated components and preserves
Av_new=e_new M. This proves the invariant and monotonicity at every probe.

For a local component, put L_i=A_i/m_i. By Nakayama, M_i is cyclic exactly
when dim_(L_i)(M_i/m_i M_i)<=1. If the dimension is one, some projected
coordinate vector w_j has nonzero image in that top, since the w_j span M.
That vector generates M_i and the scan eventually includes this component.
If the dimension exceeds one, no vector generates M_i and the scan never
includes it. A zero module component is included on the first probe.

The final e is therefore the unique largest idempotent for which eM is cyclic,
and v generates eM. In particular M is cyclic if and only if e=1. Components
on which M is zero are included in this largest idempotent. No faithfulness
assumption is used. The zero-dimensional module is a separate trivial case
with e=1,v=0; the bounded reference interface requires d>=1.

For A=K^d acting on itself in its coordinate basis, the ranks after the probes
are exactly 1,2,...,d. Thus d probes is sharp for this specified basis-scan
procedure. This is not a lower bound on every cyclicity algorithm.

## 3. The tensor reconstruction

For t:U x V -> W, all dimensions n, compute

    B = {(X,Y) : t(Xu,v)=Y t(u,v) for all u,v}.

This is the left nucleus, a unital algebra under pairwise composition. Require
dim B=n, injectivity of both projections, commutativity of its image on W,
and zero right kernel of t. These are exactly the initial predecessor tests.
Injectivity identifies B with its W-image, gives its multiplication table by
linear solves, and gives faithful actions on U and W.

Apply the scan to U and W as B-modules. Reject unless both are cyclic. Let
their generators be u_0,w_0, and define

    alpha(b)=X_b u_0,   gamma(b)=Y_b w_0,
    Phi(v)=t(u_0,v).

The maps alpha and gamma are surjective and their dimensions match n, so
they are isomorphisms. If Phi(v)=0, the nucleus equation implies
t(alpha(b),v)=0 for every b. Since alpha is onto and the right kernel is zero,
v=0. Thus Phi is an isomorphism as well. Put beta=Phi^(-1) gamma. Then

    t(alpha(a),beta(b)) = Y_a gamma(b) = gamma(ab).

The three column matrices alpha,beta,gamma are the returned U,V,W.

Conversely, for ordinary commutative unital multiplication, a nucleus pair
satisfies X(u)v=Y(uv). Setting one argument at a time to the unit gives
X=Y=L_b for one algebra element b. Thus the nucleus is the original algebra,
both modules are regular, and all tests pass. Independent input/output basis
changes preserve this property and transport the certificates. This proves
necessity and sufficiency over every field, including fields too small to
separate all primitive factors with one element.

## 4. Uniform operation bound

The nucleus has n^3 equations and 2n^2 variables. Ordinary elimination costs
O(n^7) field operations. All subsequent matrix dimensions are polynomial in n.
For clarity, the following loose bounds already suffice for the same total.

For dimensions a,d<=n, computing Q(v) has at most d^2 equations in a variables.
One ideal product uses at most a^2 products of two a-coordinate algebra
elements, each with O(a^3) dense table arithmetic, followed by elimination on
at most a^2 rows of width a. Thus at most a ideal products cost O(a^6).
Finding its identity and the quotient-annihilator solve cost O(n^4).
There are at most d probes for each module, so both scans cost O(n^7).
Multiplication-table recovery, representation checks and the final three-map
construction have smaller polynomial bounds. No bound includes |K| as a
factor. Field representation, coefficient growth and the cost of one field
operation remain separate contracts.

The reference implementation validates prime characteristics only through
65537, algebra/module dimensions through eight and tensor dimensions through
four. Its bounded trial-division field validation is not the all-characteristic
algorithmic claim. The proof assumes a supplied exact field. The finite replay
corroborates this algorithm; it does not replace the quantified argument.

## 5. Scope of the new result

The independent certificate checker verifies the recovered algebra's unit,
associativity and commutativity, invertibility of all three maps, and every
transported basis product. It does not reconstruct a nucleus or trust the
producer's recognition decision. The module checker verifies Av=eM and
e^2=e; maximality is established by section 2, and is independently enumerated
on the tiny module domain in the replay.

The reconstruction recovers some commutative multiplication table and its
isotopy. It neither classifies arbitrary recovered algebras up to isomorphism
nor constructs a named polynomial presentation, primitive decomposition,
height list or special-linear orbit label. No such tasks are prerequisites
for the recovered certificate. No new cyclicity-theory priority, paid native
realization, compiler closure, multiplier or kappa follows from this result.
