# The all-field two-request law

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and predecessor

Let K be any finite field of order q, let m >= 2, and let U,V be rank-one
idempotents on K^m with UV=VU=0. Set P=I-U and Q=I-V. A complete header
G in GL_m(K) passes R if every leading principal minor of GRG^-1 of orders
1 through rank(R) is nonzero. Weight all complete headers equally.

Write n=m-1 and

```text
alpha = (q^2-q+1)^2,
beta  = q^3-q+1,
gamma = q^3-q^2+1.
```

The exact joint passing fraction is

```text
     (q-1)^2 [alpha^n - 2 beta^n + gamma^n]
J = ------------------------------------------------- .
     q^2 (q^m-1)(q^m-q) q^(2m-4)
```

This is a scoped counting proof, with finite corroboration. It supplies the
all-field closed form left open by Nick Petalas's #4261 and extends the
binary and ternary closed forms in #4261 and #4273. Those results are cited
as predecessors, not re-audited. The retained request context is due to
Cinna Davis; source527, commdata2338 and Jose Manuel retain the normalizer
lineage credit.

## The cited transfer, in complementary coordinates

Use #4261's normalized-pair and equal-header-fiber theorem. In its partial
Gram coordinates A, safe states have A_11,A_22 != 1, the initial state is
A=0, and the terminal weight is w(I-A). Substitute B=I-A. Let S consist
of the 2 by 2 matrices B with both diagonal entries nonzero. Define

```text
w(H) = 2q^2-1 if H=0; q-1 if rank(H)=1; 0 otherwise,
(Tf)(B) = sum_(C in S) w(B-C) f(C),
h(B) = w(B) = (q-1) 1_(det B=0).
```

Negation preserves w, so this substitution preserves the transfer. The
passing-pair numerator is c_n=(T^n h)(I). The total normalized-pair count
is D=(q^m-1)(q^m-q)q^(2m-4), so J=c_n/D. Every pair has exactly
|GL_(m-2)(K)| header completions. This package's new proof concerns c_n.

## Three invariant functions

Put z(B)=1_(B_12=0)+1_(B_21=0) and a=(q-1)^2(q^2-3q+4). Then

```text
T 1 = alpha 1,
T z = 2(q-1)^3 1 + beta z,
T h = a 1 - (q-1)^2 z + gamma h.                 (1)
```

These identities hold over every finite field, without a prime-field
assumption. They reduce the transfer from q^2(q-1)^2 states to three
functions.

For T1, enumerate the rank-one increment yx. Its two diagonal restrictions
are y_i x_i != B_ii. For each nonzero B_ii there are q^2-(q-1)=q^2-q+1
choices of (y_i,x_i). The two coordinates are independent. Thus T1=alpha.
This also accounts for all 2q^2-1 factorizations of the zero increment.

For the first off-diagonal zero indicator, impose y_1 x_2=B_12. If
B_12 != 0, there are q-1 choices of (y_1,x_2), and each of x_1,y_2
has q-1 choices after its diagonal exclusion. The total is (q-1)^3.
If B_12=0, inclusion-exclusion on y_1=0 or x_2=0 gives

```text
2q(q^2-q+1)-q^2 = (q-1)^3 + beta.
```

Apply the same argument to B_21 and add. This proves Tz.

For Th, sum over singular C in S. Diagonal row and column scalings
preserve S, rank differences, off-diagonal zeros and singularity. They
normalize B's diagonal to (1,1). Transposition and residual scaling reduce
its off-diagonal pattern to one of the following. In the last row, t is
any field element other than 0,1.

| Type | B | (Th)(B) |
|---|---|---|
| Z | [[1,0],[0,1]] | (q-2)(q-1)^3 |
| L | [[1,1],[0,1]] | (q-1)^2(q^2-3q+3) |
| R | [[1,1],[1,1]] | (q-1)(2q^2-1)+(q-1)^2((q-1)(2q-3)-1) |
| N | [[1,1],[t,1]] | (q-1)^2(q^2-3q+4) |

Here is a direct count of each row, rather than extrapolation from a
finite collection of fields. Write C=[[r,s],[u,v]], with r,v != 0 and
su=rv. In particular s,u != 0.

For Z, det(B-C)=0 says r+v=1. There are q-2 choices of r and q-1
choices of s, giving (q-2)(q-1) targets. Multiply by (q-1)^2 for the
transition weight and h(C).

For L, det(B-C)=0 says u=r+v-1. Among the (q-1)^2 choices of r,v,
exactly q-2 have r+v=1. Each remaining choice determines nonzero u
and s=rv/u. This gives q^2-3q+3 targets.

For R, det(B-C)=0 says s+u=r+v. Together with su=rv, this means
{s,u}={r,v}, with multiplicity one if r=v and two otherwise. There are
(q-1)(2q-3) targets. One is C=B, whose transition weight is 2q^2-1;
the others have transition weight q-1. This proves the displayed R row.

For N, eliminate u from the two determinant conditions to get

```text
(r-s)(v-s) = (1-t)s(s-1).
```

When s=1, there are 2q-3 choices of nonzero r,v. For each s != 0,1,
the right side is nonzero. There are q-1 choices of nonzero r-s before
excluding r=0 and v=0. Those exclusions coincide precisely when
s=1-1/t, a unique permitted s. Thus the total number of targets is

```text
(2q-3) + (q-2)(q-3) + 1 = q^2-3q+4.
```

The N case is absent for q=2. No division by 2 or characteristic-specific
step was used. Substituting z=2,1,0,0 and h=0,0,q-1,0 respectively in
these four rows proves the third identity in (1).

## Closing the scalar recurrence

Equation (1) implies

```text
(T-alpha)(T-beta)(T-gamma) h = 0.
```

Therefore c_n satisfies the cubic recurrence with characteristic
polynomial (X-alpha)(X-beta)(X-gamma). Its initial values are

```text
c_0 = 0,
c_1 = (q-1)^3(q-2),
c_2 = a alpha - (q-1)^2[2(q-1)^3+2 beta] + gamma c_1.
```

The candidate d_n=((q-1)^2/q^2)(alpha^n-2 beta^n+gamma^n) satisfies
the same recurrence. Direct polynomial expansion gives d_0=0,
d_1=c_1 and d_2=c_2. Induction proves c_n=d_n for every n>=0, hence
the stated formula for every m>=2. This is an all-field written proof.

For example q=5 gives

```text
c_n = (16/25)(441^n - 2*121^n + 101^n),
c_1 = 192, c_2 = 112256, J_(m=2) = 2/5.
```

At q=2 and q=3 the three bases specialize to (9,7,5) and (49,25,19),
respectively, and the coefficients to 1/4 and 4/9, exactly the cited
predecessor formulas. No new result is claimed for those specializations.

## Evidence and limits

The self-contained verifier enumerates literal rank-one factorizations,
checks (1) by exact field arithmetic, and compares the new formula to a
separately implemented full-state transfer. Its generated receipt states
every finite domain and binds the six package files by SHA256. These checks
corroborate the proof; they do not replace its quantified argument.

Only two fixed orthogonal rank-one kernels and complete uniform headers
are covered. Nonorthogonal kernels, restricted header sets and k>=3 remain
outside this formula. Header selection, emission, dispatch, restoration,
stock and physical costs remain unpriced. No supplier admission, new kappa,
selected-frontier change or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
