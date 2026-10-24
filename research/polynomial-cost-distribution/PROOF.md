# The joint degree-cost law over finite polynomial fields

Let K be a field, R=K[t], and use two data roles with no auxiliary roles.
A paid factor is I+u y^T, where u is in R^2 and y is in K^2.
Every matrix in GL2(K) is free, at any position in a word. Products are
written in algebraic order. For a nonzero polynomial matrix M, its entry
degree is the maximum degree of its entries. The cost c(M) is the smallest
number of paid factors in any such word for M.

## The result

For K=F_q, write g_q=(q^2-1)(q^2-q). For every D>=1 and 1<=r<=D,
the exact number of M in GL2(F_q[t]) having entry degree D and cost r is

    N_q(D,r) = g_q (q+1) (q-1)^r q^(D-1) binom(D-1,r-1).

There are no other costs at degree D. At degree zero there are g_q targets,
all with cost zero. Summing over r gives

    N_q(D) = g_q (q^2-1) q^(2D-2),
    #{M : degree(M)<=D} = g_q q^(2D).

Thus if M is uniform among the invertible targets of exact degree D,

    c(M)-1 ~ Binomial(D-1, (q-1)/q),
    E[c(M)] = 1+(D-1)(q-1)/q,
    Var[c(M)] = (D-1)(q-1)/q^2.

This is a scoped algebraic counting proof. It supplies no physical supplier
or multiplication exponent. The count and distribution extend the binary
degree-four census in Nick Petalas's #4763. The polynomial-matrix presentation
and degree method retain Hirosi Nagao's classical credit, *On GL(2,K[x])*,
1959, Theorem 2 and its proof. The following argument gives the needed cost
reduction explicitly rather than claiming a new group presentation.

## 1. Constant-free directional factors over an arbitrary field

Choose one representative y=(a,b) of each line in the projective row line
P^1(K), and put v_y=(-b,a)^T, N_y=v_y y^T. Then N_y^2=0. Define

    T_y(f)=I+f N_y,   f in tK[t].

Every nonidentity such matrix costs at most one. We first show that every
invertible paid factor reduces to one such factor and a free map.

Since K[t] is commutative, an invertible product has invertible factors.
The determinant of I+u y^T is 1+y^T u. The only units of K[t] are the
nonzero constants. For y!=0, normalize its projective representative by
rescaling u. Write u=u_0+w with u_0=u(0). Invertibility implies y^T w=0,
so w=f v_y for one f in tK[t]. Let F_0=I+u_0 y^T. It is a free map,
and F_0 v_y=v_y. Consequently

    I+u y^T = F_0 T_y(f).

The case y=0 is identity. If f=0 the entire factor is free. This also
shows why singular factors cannot yield a cheaper invertible target.

Conjugation by a free S sends N_y to a nonzero scalar multiple of N_z,
where z is the chosen representative of y^T S^-1. Both matrices have
the same one-dimensional image and kernel, so that scalar is in K^*.
It can be absorbed into f. The scalar need not be one when q>2.

Move free maps to the right, remove constant coefficients, and merge
adjacent factors with the same projective direction using
T_y(f)T_y(h)=T_y(f+h). Delete zero coefficients. Every invertible word
therefore reduces, without increasing its paid count, to

    T_(y1)(f1) ... T_(yr)(fr) S,

with S in GL2(K), each f_i nonzero in tK[t], and adjacent y_i distinct.

## 2. Degree, uniqueness and exact cost

For distinct directions y,z the scalar y^T v_z is nonzero. In the product
of a reduced sequence of N_y, all consecutive contractions are nonzero.
The product is a nonzero rank-one matrix. If d_i=deg f_i>=1, the unique
term of degree sum d_i in the expanded product of the T_y(f_i) is the
term taking f_i N_(yi) from every factor. Its leading matrix is nonzero.
Every other term has smaller degree. Right multiplication by S preserves
a nonzero leading matrix, so

    degree(T_(y1)(f1) ... T_(yr)(fr) S) = d_1+...+d_r.

In particular a nonempty reduced product cannot be constant. The endpoint
S is M(0). To compare two reduced expressions for the same M, cancel these
free endpoints and form the inverse of one product times the other.
Here T_y(f)^-1=T_y(-f). Cancel their common initial factors in the middle
of the concatenation. At the first mismatch, distinct directions stay
distinct, or equal directions merge to a nonzero coefficient. All adjacent
directions in the remaining sequence are distinct. Unless the expressions
agree completely, this gives a nonempty reduced word equal to identity,
contradicting the degree statement. The expression is unique.

Its length r is its exact paid cost: it is itself an r-factor word, and
every other word reduces to that unique expression without increasing
its number of paid factors. This excludes cheaper words of arbitrary
polynomial degrees, with arbitrary free maps inserted.

Every GL2(K[t]) matrix is reachable. Euclidean reduction of its first
column uses free swaps and paid polynomial shears. Its gcd is a nonzero
constant because the determinant is a unit. A free scaling then makes
that column (1,0)^T. The remaining invertible triangular matrix reduces
using a free diagonal map and a paid shear. Polynomial division decreases
the remainder degree, so this procedure terminates. This is the usual
classical generation argument, included to establish census completeness.

## 3. Count the unique expressions

There are q+1 choices of first direction and q choices at every later
factor. At length r this gives (q+1)q^(r-1) direction sequences.
The positive degrees d_1+...+d_r=D have binom(D-1,r-1) compositions.
For any fixed d_i, the number of zero-constant polynomials of degree
exactly d_i is (q-1)q^(d_i-1). Their product is (q-1)^r q^(D-r).
Finally there are g_q choices of free endpoint S.

Multiplying these independent choices proves N_q(D,r). Uniqueness ensures
that this counts targets rather than words with multiplicity. Every listed
word has exact degree D and exact cost r. The generation argument proves
that no invertible target is omitted.

The binomial theorem gives

    sum_(r=1)^D (q-1)^r binom(D-1,r-1) = (q-1)q^(D-1).

This proves the exact-degree total. Summing the resulting geometric
series over degrees zero through D gives g_q q^(2D). Dividing the joint
count by the exact-degree total gives

    Pr(c(M)=r) = binom(D-1,r-1) (q-1)^(r-1) / q^(D-1),

which is the stated binomial law, including D=1. Its expectation and
variance follow from that law. No independence assertion about a different
sampling measure, such as uniform paid words, is made.

## Attribution and scope

This contribution was produced by Nick Petalas. The new contribution is
the explicit all-q joint degree-cost count and its probability law. The
binary normal-form cost proof and finite census are credited to Nick
Petalas #4763; #4276/#4243 provide the preceding right-vector questions
and free-map normal form. Nagao's presentation and degree method are
classical inputs, with [the original paper](https://www.i-repository.net/contents/osakacu/sugaku/DB-M-010-02-04.pdf)
as the primary source. ToikY #4334 and Nick Petalas #4601/#4749 supply the
local-product and semilocal comparisons. Wentao Li #4099 following #2513
supplies the right-vector alphabet lineage. Those results are cited, not
audited here. No new classical group-presentation theorem is claimed.

Only two roles, one-variable polynomial coefficients and free base-field
maps are covered. Singular endpoints, multivariate algebras and restored
auxiliary roles are not classified. Preparation, conversion, control,
routing, precision, restoration, stock and a complete physical consumer
are unpriced. This is not supplier admission or a complete multiplication
theorem. Independent human and formal proof-kernel review are unclaimed.
