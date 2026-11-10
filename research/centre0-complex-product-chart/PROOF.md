# A common complex product chart for the actual centre0 pair

This scoped construction was produced by Nick Petalas. Apache-2.0.

## Statement

Let G be the 112 by 112 rational centre0 code specified in Chris R /
Clear1nsight's PR5101 and used in JoyboyBrian's PR5130. For any integer
N >= 112, put A = G direct-sum I_(N-112) and B = G^T direct-sum I_(N-112).
Let H_N = C[y]/(y^N+1), identified with its N coefficient coordinates.
There is an explicit common invertible complex-linear chart S such that,
for every x,z in H_N,

```text
(S A S^-1 x)(S B S^-1 z) = (S B S^-1)(xz).                 (1)
```

Thus the invertible output map can be chosen to be S B S^-1 itself.
In particular this answers PR5130's complex-chart question for every
power-of-two padding N >= 128. The same identity holds for the product
normalized by 1/N, by linearity of the output map.

The chart is algebraic. Its entries belong to
Q(sqrt(6097), zeta_(2N)), where zeta_(2N) is a primitive 2N-th root of unity.
Neither the chart nor its inverse is asserted Gaussian-rational, unitary,
native, cheap, or compatible with the physical normalizers.

## The source and the seven planes

Use the predecessor's actual R, selected set J and code specification.
R has eight rows r_i^T. Put K = R^T/4, let P agree with K on J and vanish
elsewhere, and put U = K-12P. Its columns are u_i. The inherited identities
are RR^T = 56 I_8, RP = I_8, RU = 2 I_8, and

```text
G = I - sum_(i=1..7) u_i r_i^T.
```

These specify the input code; the contribution does not re-audit its
producer or predecessor verifier. We need the following additional Gram
calculation to construct the new chart. Since P is the row restriction of K,

```text
K^T K = 7 I_8/2,
K^T P = P^T K = P^T P = I_8/4,
U^T U = (7/2 - 6 + 36) I_8 = 67 I_8/2.
```

For each i=1,...,7 the plane V_i = span_Q(u_i,r_i) therefore has Gram
matrix [[67/2,2],[2,56]], with determinant 1872. The seven planes are
mutually orthogonal. Their direct sum has dimension fourteen. Its rational
orthogonal complement Z has dimension 98. Both G and G^T fix Z pointwise.

On V_i, in the ordered basis (u_i,r_i), their matrices are

```text
A_i = [[-1,-56],[0,1]],
B_i = [[1,0],[-67/2,-1]],
A_i B_i = [[1875,56],[-67/2,-1]].
```

The last matrix has characteristic polynomial X^2-1874X+1. Write

```text
lambda = 937+12 sqrt(6097),
h      = 937-12 sqrt(6097) = lambda^-1,
t      = -(1+h)/56.
```

Indeed 937^2-144*6097=1. The two roots are distinct, lambda>1 and
0<h<1. Thus t and 1-h are nonzero.

## The common weighted-swap basis

Set v_i = u_i+t r_i and w_i = h u_i+t r_i. Direct substitution gives

```text
G v_i = w_i,        G w_i = v_i,
G^T v_i = lambda w_i,   G^T w_i = h v_i.                 (2)
```

For example -1-56t=h and (lambda+1)t=-67/2. The remaining two
equalities follow from h*lambda=1 and h^2-1874h+1=0. The determinant
of the two new columns in (u_i,r_i) coordinates is t(1-h), so they form
a basis of V_i over Q(sqrt(6097)).

Choose any rational basis z_1,...,z_98 of Z. Let W have columns

```text
v_1,w_1, ..., v_7,w_7, z_1,...,z_98.
```

This is an invertible matrix. The executable chooses the free-coordinate
nullspace basis of the fourteen rational constraints r_i^T z=u_i^T z=0.
It also constructs W^-1 without a quadratic-field elimination. For an
arbitrary owner vector x the coefficients of u_i,r_i in its orthogonal
projection onto V_i are

```text
alpha_i(x) = (56 u_i^T x - 2 r_i^T x)/1872,
beta_i(x)  = (-2 u_i^T x + (67/2) r_i^T x)/1872.
```

Its coefficients in (v_i,w_i) are

```text
c_i = (alpha_i - h beta_i/t)/(1-h),
d_i = (-alpha_i + beta_i/t)/(1-h).
```

After subtracting all fourteen projected components, the remaining
vector is in Z. Its free coordinates are exactly its coefficients in
the chosen nullspace basis. These formulas specify every row of W^-1.

Pad W by the identity to W_N. Let p swap each of the seven initial
coordinate pairs and fix every other coordinate. Let M_p be its permutation
matrix. Let D be diagonal with entries (h,lambda) on each pair and one
elsewhere. Equation (2) says

```text
W_N^-1 A W_N = M_p,
W_N^-1 B W_N = D M_p.                                   (3)
```

For coordinatewise multiplication, a common permutation satisfies

```text
(M_p a) .* (D M_p b) = D M_p (a .* b)                    (4)
```

for every pair of vectors a,b. This is the entire bilinear identity,
including the fixed complement and every padded coordinate.

## Transfer to negacyclic multiplication

Take the distinct roots rho_j=zeta_(2N)^(2j+1) of y^N+1. Evaluation gives
the algebra isomorphism

```text
E_N : H_N -> C^N,    f -> (f(rho_0),...,f(rho_(N-1))).
```

The inverse is explicit. For evaluation values a_j, its coefficient k is
N^-1 sum_j a_j rho_j^(-k), for 0<=k<N. To check it, the inner geometric
sum is N when the two coefficient indices coincide and zero otherwise.
The distinct roots also prove invertibility directly. Evaluation carries
negacyclic multiplication to coordinatewise multiplication.

Define S = E_N^-1 W_N^-1. By (3), conjugating A and B by S gives
E_N^-1 M_p E_N and E_N^-1 D M_p E_N. Apply E_N to both sides of (1).
Its left side becomes (M_p E_N x) .* (D M_p E_N z), which by (4) is
D M_p E_N(xz), the evaluation of the right side. Injectivity of E_N
proves (1). All entries of W_N and its inverse lie in Q(sqrt(6097));
all entries of E_N and its inverse lie in Q(zeta_(2N)). This also proves
the stated coefficient-field containment. No transcendental coefficient
or limit argument is required.

## Scope and evidence

PR5130's exclusion over Q(i) is unchanged. Its multiplication-rank gap
does not hold in the split complex algebra, and S is permitted to leave
Q(i). The new construction answers the complex algebraic question only.
It does not commute the actual native K_i normalizers through a product,
emit the changed producer, identify independent Gaussian jobs, or give a
complete paid or productive invoice. All five selected framework
assumptions retain their status. No kappa or frontier change follows.

The written argument proves the quantified statement. The executable
emits W and W^-1 and checks both inverse orders and both source endpoints
on every basis column with exact quadratic arithmetic. It separately checks
all 112^2 split basis products. Finite-field literal negacyclic products
at N=128,256,512 corroborate evaluation order, inverse normalization,
padding and wrap signs. These finite fields are test fixtures, not a
substitute for the proof over C. Source, chart and output-map controls
address ways the implementation could certify a different identity.

Credit JoyboyBrian's PR5130 for the open question and common-Q(i) chart
obstruction, Chris R / Clear1nsight's PR5101 for the actual code, David Ganz /
Dugongue and mdumitrean's PR4948/4929, Cao Yifan/intqwq, Cinna Davis and
the retained native, analytic, precision and compiler contributors. Product
isotopy, two-involution reduction and polynomial evaluation are classical.
No general literature-priority or independent human/proof-kernel review
is claimed.
