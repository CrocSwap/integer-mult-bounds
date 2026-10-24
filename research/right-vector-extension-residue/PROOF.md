# Rank-one lifts with a smaller base field

Let K=F_q be a subfield of L=F_Q. Let R be a finite-dimensional associative
unital L-algebra, with L central, Jacobson radical J, and canonical residue
R/J=L. Thus R=L direct-sum J as a K-vector space. Put z=|J|. Neither
commutativity nor J squared zero is assumed.

Use two roles. Paid factors are I+u v^T with u in R^2 and v in K^2.
Arbitrary GL_2(K) maps are free anywhere. The cost is the least number of
paid factors. Fix a rank-one matrix A in M_2(L), and consider all z^4
lifts M=A+N with N in M_2(J).

For a K-line D in K^2, call D eligible when A v belongs to K^2 minus {0}
for one, equivalently every, nonzero v in D. Let t(A) count these lines.

## Theorem

The eligible-line count belongs to {0,1,q}. For each fixed residue A,

```text
cost 1: C_A = 0                    if t(A)=0,
             1+t(A)*(z^2-1)        if t(A)>0;
cost 2: z^4-C_A.
```

There are no cost-zero targets in these fibers and none needs a third paid
factor. Among all rank-one residues in M_2(L), the exact counts by t are

```text
N_q = (q+1)*(q^2-1),
N_1 = (q+1)*(q^2-1)*(Q-q),
N_0 = (Q+1)*(Q^2-1) - N_q - N_1.
```

Consequently the complete rank-one-residue lift census has

```text
cost 1: N_q*(q*z^2-q+1) + N_1*z^2
      = (q+1)*(q^2-1)*(Q*z^2-q+1);
cost 2: (Q+1)*(Q^2-1)*z^4 - cost_1.
```

When Q=q this specializes to #4770. When Q>q, the cost distribution depends
on the residue. The new contribution is this extension-field classification
and its exact lift and residue counts. The one-factor criterion and unit-pivot
upper bound below are cited predecessor results, not new claims.

## The predecessor criteria

Nick Petalas's #4276, Theorems A and D, and the specialization in #4770 give

```text
cost(M)<=1 iff Mv=w for some nonzero v,w in K^2.
```

This criterion holds for any central K-algebra. Our R qualifies even though
its residue is larger than K. Reducing M=A+N modulo J shows that it becomes

```text
cost(M)<=1 iff some eligible v satisfies Nv=0.
```

The split decomposition is essential here: Av is in L^2 and Nv is in
J times J, so Mv lies in K^2 minus {0} exactly when Av lies there and Nv=0.

Every such M has a unit entry because A is nonzero. The unit-pivot two-factor
bound from #4276 therefore applies. A free GL_2(K) target has invertible
residue over L, so our rank-one residues exclude cost zero. These facts
give exact costs one and two after counting the one-factor lifts.

## Why only zero, one, or q lines occur

Write A=a r with nonzero column a in L^2 and nonzero row r over L.
If the L-image line La contains no nonzero K-vector, there is no eligible
line. Otherwise rescale a so a belongs to K^2 minus {0}. Then

```text
Av belongs to K^2  iff rv belongs to K.
```

Indeed one nonzero coordinate of a lies in K and can be inverted in K.
Let U={v in K^2:rv in K} and V={v in K^2:rv=0}. These are K-subspaces,
V is contained in U, and eligible lines are precisely the lines of U outside V.
Put k=dim_K U and h=dim_K V. Since r is nonzero, h<=1. The induced map
U/V into K is injective, so k-h<=1. The only positive possibilities are
(k,h)=(1,0) and (2,1), giving respectively

```text
t=(q^k-q^h)/(q-1)=1 or q.
```

If t=q, U=K^2, so both entries of r lie in K. Thus A itself has K entries
and rank one over K. Conversely every rank-one K-matrix has q eligible
lines. This proves the trichotomy and identifies the q-line class.

## Count the lifts above each residue

For each eligible line D, let E_D={N in M_2(J):Nv=0 for v in D}.
Choose a K-basis of K^2 beginning with v. The action of N on that first
basis vector is fixed at zero; its action on the second is arbitrary in
J times J. Hence |E_D|=z^2. If D and D' are distinct, they span K^2,
so E_D intersects E_D' only in N=0.

When t=0 the union is empty. When t>0 its size is 1+t*(z^2-1). The zero
noise belongs to every nonempty family of events but not to an empty one.
This proves C_A, including J=0. No radical multiplication enters the count.

## Count the three residue classes

Over a field of order s there are (s^2-1)^2/(s-1)=(s+1)*(s^2-1)
rank-one 2-by-2 matrices. Count their nonzero outer products and divide by
the s-1 rescalings of either factor. Applying this with s=q gives N_q.

Double-count pairs (A,D) with A rank one over L and D an eligible K-line.
Fix D and use a GL_2(K) change of input coordinates to make D=K e_1.
The first column w=Ae_1 may be any of the q^2-1 nonzero vectors in K^2.
Rank one over L then forces the second column to be c w for a unique
c in L, giving Q choices. There are q+1 input lines, so

```text
sum_A t(A) = (q+1)*(q^2-1)*Q = N_1 + q*N_q.
```

Solve for N_1 and subtract N_1+N_q from the total number of rank-one
L-matrices to obtain N_0. Multiplying by the per-fiber lift counts proves
the aggregate formula. The projective-line and finite-field counting tools
are classical; their application here is the stated scoped result.

## First example

Let K=F2, L=F4, and R=L[e]/e^2, so Q=4 and z=4. Of the 75 rank-one
residues, 9 have t=2, 18 have t=1 and 48 have t=0. Each such residue has
256 lifts. Their respective one-factor counts are 31,16,0. In total,
567 lifts cost one and 18,633 cost two.

If alpha belongs to F4 minus F2, the matrices

```text
[[1,0],[0,0]],  [[1,alpha],[0,0]],  [[alpha,0],[0,0]]
```

have t=2,1,0 respectively. With L-valued right vectors and GL_2(L) free
maps instead, #4770's formula gives 4,575 one-factor lifts over these same
75 residues. The smaller base field therefore changes a concrete cost count.

Produced by Nick Petalas. Predecessor credit and scope are in README.md.
