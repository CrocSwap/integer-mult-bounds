# Exact polynomial right-vector cost

Work over K=F2, R=F2[t], with two data roles and no scratch roles.
A paid factor is P(u,y)=I+u y^T, u in R^2 and y in K^2.
Every GL2(K) map is free anywhere. Cost counts paid factors.
All words below are written in algebraic product order.

## Statement

For each nonzero binary row y=(a,b), put v_y=(b,a)^T and
N_y=v_y y. For f in t F2[t], write T_y(f)=I+f N_y.
Every invertible target has a unique expression

    T_(y1)(f1) ... T_(yr)(fr) S,

where S is in GL2(F2), every f_i is nonzero with zero constant term,
and consecutive directions y_i differ. Its exact paid cost is r.
In particular, with U=T_(0,1)(t), L=T_(1,0)(t),

    M = U L U L = [[1+t^2+t^4, t^3], [t^3, 1+t^2]]

has cost 4. More generally (UL)^k has cost 2k for every k>=1.
Thus there is no uniform finite cost bound over all K-algebras, even
for two-role invertible targets over a commutative integral domain.
For k>=1, delta((UL)^k)=2, so the gap from the column lower bound
is unbounded too.

This is the right-vector cost consequence of classical polynomial-matrix
normal forms, not a claim to a new group-theoretic normal-form theorem.
Nagao, *On GL(2,K[x])* (1959), Theorem 2 and its degree argument,
provides the classical structural context:
https://www.i-repository.net/contents/osakacu/sugaku/DB-M-010-02-04.pdf .
The proof below is self-contained for this binary cost statement.

## 1. An invertible word only uses invertible paid factors

Since R is commutative, det of a product is the product of determinants.
The only unit of F2[t] is 1. If a word has invertible endpoint, each
factor has determinant 1. For P(u,y), det P=1+y^T u. If y is nonzero,
invertibility therefore forces y^T u=0. The solution space of that
equation is u=f v_y for a unique polynomial f, including f=0.
Hence every usable paid factor is T_y(f). The case y=0 is identity.
Singular factors cannot evade this reduction.

We have N_y^2=0 and T_y(f)T_y(g)=T_y(f+g). Split
f=f(0)+(f+f(0)); the constant part T_y(f(0)) is free. For any free S,
conjugation S T_y(f) S^-1 is T_z(f) for another nonzero binary row z.
Indeed the conjugated nonzero nilpotent has image equal to kernel,
and over F2 there is exactly one nonzero rank-one nilpotent with each
of the three kernel lines. This also follows directly from z=y S^-1
and S v_y=v_z, since every invertible binary 2x2 determinant is 1.

Move all free factors to the right, split off all constant parts,
and merge adjacent equal directions, deleting zero coefficients.
Every finite invertible word thus has the stated form with at most
as many nonconstant factors as its original paid count. Evaluation at
t=0 shows the final free matrix is necessarily S=M(0).

## 2. A reduced nonempty word cannot be constant

For distinct nonzero binary rows y,z,

    y v_z = a d + b c = 1

when y=(a,b), z=(c,d). Consequently

    N_(y1) ... N_(yr) = v_(y1) y_r != 0

whenever adjacent directions differ. Let d_i=deg f_i>=1. In the
expansion of a reduced product, the term choosing f_i N_(yi) from
every factor has degree D=sum d_i and nonzero leading coefficient
v_(y1) y_r. Every term omitting at least one factor has smaller degree.
Thus the degree of the matrix product, defined as the maximum entry
degree, is exactly D>0. Multiplication by an invertible constant S
preserves this degree because its leading matrix remains nonzero.

This proves the degree test for arbitrary polynomial coefficients,
without any degree cap or finite search assumption.

## 3. Uniqueness and exact cost

Suppose two reduced products are equal. Their free endpoints agree by
evaluation at zero, so cancel them. Multiply the inverse of one product
by the other. Since each T_y(f) is its own inverse, cancel the common
initial factors at the middle of this concatenation. At the first
mismatch, either the directions differ, or their nonzero coefficients
sum to a nonzero polynomial in tF2[t]. In the latter case merge that
pair. The remaining concatenation is reduced and nonempty unless the
original products agreed factor by factor. A nonempty reduced product
has positive degree by Section 2, so cannot be identity. This proves
uniqueness.

Now a target with reduced length r has a literal r-paid-factor word.
Any other word with q paid factors reduces to the same unique expression
and the reduction does not increase the number of paid factors. Hence
q>=r, proving cost=r.

For completeness every GL2(F2[t]) target is reachable. Euclidean row
reduction on its first column uses row swaps and shears adding a
polynomial multiple of one row to the other. The swaps are free and
the shears are paid factors. The first-column gcd is 1 because the
determinant is 1. After it is changed to (1,0)^T, the remaining matrix
is [[1,b],[0,1]], also a paid factor. The usual polynomial division
strictly decreases the nonzero remainder degree, so this process
terminates. Reversing these invertible operations gives a finite word.
This existence argument is not needed for the four-factor lower bound.

## 4. The first counterexample and its corollary

U,L have different directions and coefficient t. Their alternating
word of length 2k is already reduced, so costs exactly 2k. Direct
multiplication at k=2 gives the displayed M. In particular a third
factor never suffices for M. This answers Open next question 1 of
Nick Petalas's #4276 negatively. The proof covers arbitrary polynomial
left coefficients and all insertions of free binary maps, rather than
only words in U and L.

By the column lower bound and one-factor criterion of #4243/#4276,
delta<=1 would imply cost<=1. Delta is at most two for two roles,
so every (UL)^k with k>=1 has delta=2. This is predecessor use, not
an independent re-verification of that criterion.

## Scope

This is a scoped algebraic proof, with a finite corroborating census.
The algebra F2[t] is not semilocal: its distinct irreducible polynomials
give infinitely many maximal ideals. It lies outside #4749's hypothesis.
No contradiction with the semilocal three-factor theorem follows.
The polynomial t here is an algebra coefficient, not a free change of
basis. Allowing GL2(F2[t]) for free would change the question.
No native preparation, conversion, precision, routing, restoration,
stock, supplier admission or multiplication theorem is proved.
