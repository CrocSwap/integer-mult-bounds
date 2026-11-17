# Sharp budgets from a common acyclic interaction support

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and notation

Let D_1,...,D_K be real or complex n by n matrices. Their union support is
the directed graph having an edge c to r whenever some (D_i)_(r,c) is
nonzero. Assume this graph is acyclic and every directed path has at most h
edges, with 0<=h<=n-1. Fix any induced matrix norm and bounds
d_i>=||D_i||. The d_i may be zero and need not be small.

For a list d=(d_1,...,d_j), define

    e_r(d) = sum_{1<=i_1<...<i_r<=j} d_i1 ... d_ir,
    H_r(d) = sum_{a_1+...+a_j=r, a_i>=0} d_1^a1 ... d_j^aj,
    E_h(d) = sum_{r=0}^h e_r(d),
    C_h(d) = sum_{r=0}^h H_r(d).

Both degree-zero polynomials are one. For the empty list, all positive
degree polynomials vanish. These are the classical elementary symmetric
and complete homogeneous symmetric polynomials, respectively.

Write R_j=(I+D_j)...(I+D_1), with R_0=I. Then

    ||R_j||       <= E_h(d_1,...,d_j),
    ||R_j-I||     <= E_h(d_1,...,d_j)-1,
    ||R_j^-1||    <= C_h(d_1,...,d_j),
    ||R_j^-1-I||  <= C_h(d_1,...,d_j)-1.

Every R_j is invertible. All four envelopes are sharp over the stated
class in the induced infinity norm, separately for forward and inverse
quantities, for every finite nonnegative list d and every h. A witness has
dimension h+1. Sharpness also holds in any larger dimension by adding zero
coordinates to the errors. A particular graph or an extra rank restriction
can have smaller optimal envelopes.

## Vanishing products and the upper bounds

An entry of a product of r supported matrices is a sum over directed walks
of length r in the union graph. A directed walk in an acyclic graph cannot
repeat a vertex, so it is a path. Thus every product of h+1 matrices chosen
from the D_i, with arbitrary repetition and order, is zero. This statement
is stronger than each individual D_i being nilpotent.

Expand R_j in its chronological order. Its terms of degree r choose r
distinct factor indices. Submultiplicativity bounds the sum of their norms
by e_r(d). Every term of degree greater than h vanishes. Keeping the
constant term proves the first bound; removing it proves the second.

Since D_i^(h+1)=0, the exact inverse of I+D_i is the finite sum

    I-D_i+D_i^2-...+(-D_i)^h.

The inverse R_j^-1 is the product of these inverse factors in reverse
order, namely (I+D_1)^-1...(I+D_j)^-1. Expanding and grouping by total
degree r gives one term for each nonnegative exponent tuple summing to r.
The norm sum is at most H_r(d). Terms above degree h vanish, even when
they use different factors. This proves both inverse bounds. No infinite
series, commuting-error hypothesis or small-error limit is used.

## Exact attaining families

Let S be the (h+1)-dimensional matrix with ones just above the diagonal
and zeros elsewhere. Its norm is one when h>=1, and S^(h+1)=0. Its union
support is one directed path of length h. For h=0 use the zero 1 by 1
matrix. Take D_i=d_i S. All factors commute in this example, and direct
polynomial multiplication gives

    R_j = sum_{r=0}^h e_r(d) S^r.

The first row has one entry e_r(d) in each column r+1. Every other row
has a shorter nonnegative sum. Consequently its maximum absolute row sum
is exactly E_h(d), and removing I gives exactly E_h(d)-1.

For the inverse bounds instead take D_i=-d_i S. Its inverse product is

    R_j^-1 = sum_{r=0}^h H_r(d) S^r.

The same first-row argument gives C_h(d) and C_h(d)-1. These witnesses
satisfy the prescribed upper bounds on individual norms, with equality
when h>=1. The h=0 class necessarily has zero errors, and both envelopes
are one regardless of any looser prescribed d_i.

These are different sign choices. No simultaneous attainment of the
forward and inverse maxima by one error sequence is asserted. If the
positive d_i fail to use every edge, the union graph can have depth less
than h. The witness still belongs to the class of support depth at most h,
and a zero budget has the same sharp value one in either depth class.

## Arithmetic noise and the original precision interface

For z_0=x and z_i=(I+D_i)z_(i-1)+v_i, finite expansion gives

    ||z_j-x|| <= (E_h(d_1,...,d_j)-1)||x||
                 + sum_{i=1}^j E_h(d_(i+1),...,d_j)||v_i||.

Each noise term meets only the later factors. The proof above applies to
that suffix, whose support depth is at most h. This bound is sharp in the
same class in the infinity norm. Use D_i=d_i S, x=M times the all-ones
vector, and v_i=eta_i times that vector, with M,eta_i>=0. Every contribution
is nonnegative and its first-row sum attains the displayed bound. This
also covers h=0 and empty suffixes.

For exact gates A_i with F_i=A_i...A_1 and perturbed gates A_i+Delta_i,
y_i=(A_i+Delta_i)y_(i-1)+u_i, the interaction identity of ywz65's PR2701 is

    D_i=F_i^-1 Delta_i F_(i-1),
    z_i=F_i^-1 y_i,
    v_i=F_i^-1 u_i.

If these actual D_i satisfy the common acyclic hypothesis, the preceding
bounds apply. In particular, for ||F_i||,||F_i^-1||<=B,

    ||Q_j|| <= B E_h(d_1,...,d_j),
    ||Q_j^-1|| <= B C_h(d_1,...,d_j),
    ||Q_j-F_j|| <= B(E_h(d_1,...,d_j)-1),
    ||Q_j^-1-F_j^-1|| <= B(C_h(d_1,...,d_j)-1).

The physical trajectory bound is ||F_j|| times the preceding noise formula
with ||v_i||=||F_i^-1 u_i||. The B factors are sufficient; their optimality
for arbitrary prescribed physical frames is not claimed. For data-dependent
errors, apply the inequalities to the realized sequence and its stated
norm bounds. Inverting that realized linear product is not an inverse for
a nonlinear rounded execution.

## A strict improvement and its boundary

At depth h=1, both exact envelopes are

    1+sum_i d_i.

All interactions are then mutually annihilating, which is stronger than
the separate square-zero condition in Ali Romman's PR5288. Whenever two
d_i are positive, this is strictly below its sufficient product
product_i(1+d_i). That earlier theorem is cited, not replayed. Twenty
errors of norm 1/10 have exact envelope 3, instead of (11/10)^20.

The higher-depth contract also allows individual errors with D_i^2!=0.
For h=2 and the same twenty norms, the exact forward envelope is 49/10
and the exact inverse envelope is 51/10. Their total norm budget is two;
the general small-total-error criterion in PR2701 is unavailable.

Common acyclicity is essential for truncation at h. In dimension two,
D_1=D_3=E_12 and D_2=E_21 are individually square-zero, but their union
has a directed two-cycle. Their product (I+D_3)(I+D_2)(I+D_1) has infinity
norm five, exceeding the invalid depth-one prediction four.

Physical gate supports do not establish the hypothesis in interaction
coordinates. For example, with physical Delta_2=E_12, exact A_1=I+E_21
and A_2=I, one gets D_2=A_1^-1 E_12 A_1, which has nonzero diagonal
entries. Thus even a triangular physical perturbation can lose the
coordinate-support certificate after conjugation.

## Scope

This is a scoped mathematical precision-interface theorem. The norm and
support of an actual selected interaction word remain to be supplied.
No actual selected caller, coefficient storage policy, bounded arithmetic
kernel, physical inverse, overflow margin, tape/storage invoice, native
operation, supplier admission or exponent improvement is proved here.
All five selected framework assumptions remain. Finite rational checks
corroborate the written universal argument; they are not its quantifier
proof or independent human or formal proof-kernel acceptance.
