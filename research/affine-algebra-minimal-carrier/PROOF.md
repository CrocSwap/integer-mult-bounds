# A smallest faithful affine group-algebra carrier

This result was produced by Nick Petalas. New material is Apache-2.0.
Claim type: scoped written proof, with finite exact corroboration.

## 1. Statement and boundary

Let F be a finite field of order q and characteristic p, and let H be a
subgroup of F* of order h. Write G = F semidirect H, with elements (a,b),
a in H and b in F, and multiplication

    (a,b)(c,d) = (ac, b+ad).

Let K be any field of characteristic different from p. Characteristic zero
is allowed; the characteristic may divide h. A carrier means a finite
dimensional unital K-linear representation of the entire algebra K[G].
Faithful means injective on all formal K-linear combinations, rather than
only injective on the group elements.

**Theorem.** The smallest dimension of a faithful carrier is exactly

    d_min = q+h-1.

An explicit attainer is W direct-sum Q. Here W is the sum-zero subspace of
the natural q-dimensional affine permutation module, and Q is the
h-dimensional left regular module of the quotient H. The kernel of the
natural permutation module has dimension exactly h-1. Every formal
coefficient can be recovered from the attainer by the formulas below.

The regular group carrier has dimension qh, so the reduction is
(q-1)(h-1). For h=1 there is no reduction. No claim is made about the
smallest *permutation* carrier or a physically implementable native address
action. W uses differences of coordinate vectors. Arithmetic, encoding,
source acquisition, restoration, precision, routing and complete supplier
costs are outside this algebraic statement. The selected frontier is unchanged.

## 2. Explicit coefficient inverse

Use the natural column convention P_(a,b)e_x = e_(ax+b). For

    u = sum_(a in H,b in F) c_(a,b) [(a,b)],
    M = sum c_(a,b) P_(a,b),
    s_a = sum_b c_(a,b),       C = sum_a s_a,

every row and column sum of M is C. For fixed a,b define its affine line sum

    L_(a,b) = sum_(x in F) M_(ax+b,x).

Expanding this sum yields the exact identity

    L_(a,b) = q c_(a,b) + sum_(t != a) s_t.

Indeed, the t=a contribution repeats c_(a,b) exactly q times. For t!=a,
the index (a-t)x+b visits every element of F exactly once, so that
contribution is s_t. Consequently

    c_(a,b) = (L_(a,b) - C + s_a)/q.                 (1)

Only q is inverted. This proves that the natural action together with the
quotient regular action is faithful: the first column of the latter gives
each s_a, and (1) recovers all c_(a,b). In particular the conclusion remains
valid when the characteristic of K divides h.

## 3. Remove the redundant constant direction

Let 1 denote the vector with all q entries equal to one. Since q is
invertible in K,

    K^F = K 1 direct-sum W,
    W = {v: sum_x v_x = 0}.

The action on K 1 is the scalar C, already obtainable from Q. Removing
this one-dimensional summand preserves faithfulness and gives dimension
(q-1)+h. Here is a literal inverse in the basis

    w_x = e_x-e_0,        x in F minus {0}.

Let B be the W block of the supplied carrier matrix. Define columns d_x
of length q by d_0=0 and, for x!=0,

    (d_x)_y = B_(y,x) for y!=0,
    (d_x)_0 = -sum_(y!=0) B_(y,x).

Then d_x=M e_x-M e_0. The row sums of M give

    M e_0 = (C 1 - sum_(x!=0) d_x)/q,
    M e_x = M e_0+d_x.                               (2)

Recover s_a from Q, recover M using (2), then use (1). These formulas
give a linear left inverse of the carrier map. They do not assert that
an arbitrary block matrix belongs to its image. The executable decoder
re-encodes the recovered coefficients and rejects a matrix outside that image.

For the natural action alone, M=0 implies C=0. Equation (1) then makes
c_(a,b)=s_a/q independent of b. Conversely put

    Z_a = sum_(b in F) [(a,b)].

Every Z_a acts as the same all-ones q-by-q matrix. Thus the complete kernel is

    {sum_a t_a Z_a : sum_a t_a=0},

with basis Z_a-Z_1 for a!=1 and dimension h-1. This is a complete kernel
classification, not an inference from finding a single alias. On W the
kernel is the full h-dimensional span of the Z_a.

## 4. Matching lower bound for every coefficient field

Let rho:K[G] -> End_K(V) be any faithful unital representation. Put

    e = (1/q) sum_(b in F) [(1,b)].

The translation subgroup is normal, so e is a central idempotent. The
elements e[(a,0)] for a in H are linearly independent and multiply as H.
Hence eK[G] is isomorphic to K[H]. Also

    V = eV direct-sum (1-e)V.

The restriction to eV must be faithful on eK[G], because that ideal acts
as zero on (1-e)V. A finite multiplicative subgroup of a field is cyclic.
For completeness, its exponent d is attained by an element: combine
elements attaining the largest prime-power orders in this finite abelian
group. All h elements solve X^d=1, so the polynomial root bound gives h<=d;
Lagrange gives d<=h. Thus d=h.

Choose a generator a of H. Then K[H] is K[T]/(T^h-1). Faithfulness on eV
requires the minimal polynomial of rho(e[(a,0)]) restricted to eV to be
exactly T^h-1. Otherwise a nonzero class of degree below h acts as zero.
Cayley-Hamilton therefore gives

    dim_K(eV) >= h.                                  (3)

This reasoning permits repeated roots in T^h-1. Replacing it by its
squarefree part would lose the modular case.

To bound the other summand, extend scalars to an algebraic closure L of K.
An injective linear map remains injective under a field extension, and
dimensions of the two summands do not change. The additive group of F is
an elementary abelian p-group of order q. Since char K != p, L contains
q distinct additive characters chi. Their Fourier idempotents are

    e_chi = (1/q) sum_(b in F) chi(-b) [(1,b)].

Character orthogonality gives q nonzero pairwise orthogonal idempotents
with sum one. One is e, for the trivial character. These facts follow by
summing the nontrivial pth-root geometric series in any one coordinate of
the additive F_p-vector space. In a faithful representation each e_chi
has nonzero image. The q-1 nontrivial images lie in (1-e)(L tensor_K V)
and are linearly independent summands. Therefore

    dim_K((1-e)V) >= q-1.                            (4)

Adding (3) and (4) proves dim V>=q+h-1. Section 3 attains this bound.
The Fourier and minimal-polynomial arguments are classical. Their use
here, together with the explicit coefficient inverse, establishes the
stated exact carrier size. No general representation-theory priority is claimed.

## 5. Formal-identity consequence

For any number r of scalar roles, applying the carrier entrywise gives an
injective algebra map

    Mat_r(K[G]) -> Mat_(r(q+h-1))(K).

Thus exact equality on every column of this smaller carrier is equivalent
to coefficientwise equality of the formal endpoint matrices. All relevant
matrices must actually be tested; a natural action, a sample of vectors,
floating-point equality or group-element faithfulness alone does not imply
this equivalence. This is a verifier interface, not a native implementation.

## 6. Finite evidence and scope

The executable builds F2,F3,F4,F5,F7,F8,F9, every subgroup of their
multiplicative groups, and coefficient fields F2,F3,F5,F7 of different
characteristic from the address field. It checks every group product in
the integer carrier, ranks the natural/augmentation/hybrid algebra maps,
reconstructs every formal basis vector and mixed vectors, and checks the
entire displayed natural-kernel basis. A separate rational line-sum
calculation uses literal natural matrices. These checks corroborate the
written proof rather than replace its all-parameter quantifiers.

In the excluded characteristic, the F3 affine group with h=2 has hybrid
algebra rank three instead of six over F3. The executable checks this
boundary as a rejection control. It is not a theorem about the smallest
carrier in that characteristic.

No predecessor scientific verifier, selected cold replay, native program,
Lean, Docker or formal proof kernel is run. Independent human and formal
proof-kernel review are unclaimed. The five selected framework assumptions
remain unresolved by this result.
