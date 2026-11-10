# The sharp inverse envelope for fractional column capacities

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
This extends Nick Petalas's integer-ratio theorem and explicit fractional-cap
question in PR6788. The sorted-column and transport argument below retains
that predecessor's method and credit. The split-row construction, its simultaneous
attainment for every real ratio, and the self-referential recurrence are the
extension. Classical Neumann comparison and transport are not new claims.

## Statement

Fix an integer n>=1, real 0<rho<1, and real beta>=1. Among all complex n-by-n
matrices E satisfying

    sum_j |E_ij| <= rho,       sum_i |E_ij| <= beta*rho,

the exact maximum of the induced 1-norm of (I-E)^-1 is U_n defined below.
Every inverse exists. No positivity, prescribed support, phase, symmetry or
row-concentration hypothesis is imposed on E.

Put U_0=0. If beta=1, put U_k=1/(1-rho) for every k>=1. If beta>1, for
k=1,...,n put q=floor(k/beta), delta=k-beta*q, and solve

    U_k = 1 + rho*((beta-delta)*U_q + delta*U_(q+1)).             (1)

A term with zero coefficient is absent. Equation(1) is an explicit triangular
recurrence: only previously defined values and possibly U_k itself occur;
its denominator in that case is positive. Thus the definition makes sense for
arbitrary real beta, without requiring a floating-point floor calculation.
The verifier specializes it to exact rational parameters.

The attaining matrix G is nonnegative and has entries

    G_ij = rho*length([i-1,i] intersect [beta*(j-1),beta*j]),       (2)

for 1<=i,j<=n. Endpoints have measure zero. Each row splits over at most two
adjacent columns. The integer case is exactly PR6788's parent routing.

## Positive comparison and the forced maximum

Let A_ij=|E_ij|. Since ||A||_infinity<=rho<1, the Neumann series converge and

    |(I-E)^-1| <= (I-A)^-1

entrywise. It suffices to bound each nonnegative column v=(I-A)^-1 e_r,
which satisfies v=e_r+A v. Its maximum M is positive, and cannot occur at
i!=r: that would give M<=rho*M. Therefore the forced coordinate r is first
in a decreasing ordering v_1>=...>=v_n>=0. Simultaneously permuting rows and
columns preserves both caps. Let S_k=v_1+...+v_k and S_0=0.

For the top k rows, their normalized aggregate column weights a_j satisfy

    0<=a_j<=beta,       sum_j a_j<=k,
    S_k=1+rho*sum_j a_j*v_j.

Moving weight to a larger coordinate until its capacity is full proves the
finite fractional transport bound

    S_k <= 1+rho*(beta*S_q+delta*v_(q+1))
        = 1+rho*((beta-delta)*S_q+delta*S_(q+1)),                 (3)

where q=floor(k/beta), delta=k-beta*q. When delta=0 its last term is absent,
including q=n at beta=1. If delta>0, q<n, so the indicated coordinate exists.
Both coefficients on the last line are nonnegative. This argument covers
diffuse rows and arbitrary complex E through the preceding comparison.

## Why the recurrence is well defined and bounds every column

For beta>1, q<k. If q+1<k, equation(1) uses only earlier indices. If q+1=k
and delta>0, then q=k-1 and

    delta=k-beta*(k-1)=1-(beta-1)*(k-1),       0<delta<=1.

Consequently 1-rho*delta>=1-rho>0, and(1) means

    U_k=(1+rho*(beta-delta)*U_q)/(1-rho*delta).                   (4)

For k=1, q=0 and delta=1, so U_1=1/(1-rho). When delta=0, the absent
term must not be evaluated as an unknown U_k. This also deals with exact
breakpoints beta=k/q. In all cases U_k exists uniquely and is nonnegative.

Induct on k in(3). Previously bounded partial sums have nonnegative
coefficients. In a self-referential case move rho*delta*S_k to the left and
divide by the positive denominator from(4). This gives S_k<=U_k. For
beta=1, the induced norm ||A||_1<=rho directly gives the bound1/(1-rho).
Thus every inverse column has sum at most U_n. Notice that delta is not
globally bounded by one; only the self-referential case has that property.

## One matrix attains all partial sums simultaneously

The column intervals in(2) partition[0,beta*n], which covers[0,n]. Hence
every row of G sums to rho. The intersection with[0,n] of a column interval
has length at most beta, so each column sums to at most beta*rho. These facts
establish admissibility, not an assumption about an emitted Gaussian matrix.

For a decreasing nonnegative vector x, define the decreasing staircase
f(t)=x_j on[beta*(j-1),beta*j] for0<=t<=n. Then

    (Gx)_i=rho*integral_(i-1)^i f(t) dt.

Integrals over successive unit intervals of a decreasing function decrease.
Thus G preserves the cone of decreasing nonnegative vectors. Starting from
e_1, every G^a e_1 lies in that cone; sums and limits remain in it. Row
contraction ensures h=(I-G)^-1 e_1=sum_(a>=0)G^a e_1 is well defined and
decreasing. This proves the ordering needed for attainment, rather than
assuming it from a proposed extremal shape.

For any k, the first k row intervals partition[0,k]. Their total overlap
with each column interval is beta on columns1,...,q, delta on column q+1,
and zero thereafter, with the same q and delta as(1). Summing h=e_1+Gh
therefore gives equality in(3) for every k simultaneously. Uniqueness of
the triangular recurrence implies sum_(i<=k)h_i=U_k. In particular the
first inverse column has sum U_n. The already proved universal upper bound
shows ||(I-G)^-1||_1=U_n and proves the theorem.

For beta=1, G=rho*I and its inverse norm is1/(1-rho). For beta>=n,
all row intervals lie in the first column interval, so the result reduces to
(1+(n-1)*rho)/(1-rho), the credited row-only full-support envelope.

## Exact three-coordinate illustration

At rho=1/2 and1<=b=beta<=2, the new envelope is

    U_3=(6*b^2-8*b+3)/(b*(b-1/2)),    1<=b<=3/2,
    U_3=5-3/b,                       3/2<=b<=2.

Both expressions equal3 at b=3/2. They give2 at b=1 and7/2 at b=2.
The first two rows of G are(1/2,0,0) and((b-1)/2,(2-b)/2,0).
Its third row is(0,b-1,3/2-b) on the first interval, and(0,1/2,0)
on the second. In particular fractional capacities require split rows and,
near b=1, nonroot self-loops. Rounding b upward gives a matrix outside the
allowed column cap; rounding downward generally loses sharpness.

For integer beta=m>=2, formula(2) is G_(i,ceil(i/m))=rho. Its first inverse
column is rho^ceil(log_m i)/(1-rho), with depth zero at i=1. This recovers
Petalas's credited exact integer theorem, not an additional new result.

## Evidence, attribution and remaining obligations

This is the all-size mathematical argument. Finite exact arithmetic tests
corroborate specified cases and controls; they do not prove the quantified
claim or certify it in a formal proof kernel. Separate AI reviews are not
independent human acceptance. Root derived the extension after reading the
predecessor's public body and named method; its actual proof was then acquired
and retained. The mathematical scout had already read that proof and supplied
the three-coordinate derivation. This is source-aware work, not a blind test.

Nick Petalas retains credit for PR6788's integer-ratio theorem, partial-sum
transport proof and explicit fractional-cap question. Ali Romman5255/5306,
Cinna Davis4100, James Reed4282, ToikY4209, and the retained conditioning,
support-envelope and Schur lineage retain their contributions. Original
source texts and notices remain unchanged. Literature-wide priority is unclaimed.

Unequal row budgets, fixed supports, forbidden diagonals and other additional
constraints define different extremal problems. No actual Gaussian coefficient
matrix is proved to satisfy these caps. Preparation, rounding, error grids,
tape movement, stock, native realization, ownership/restoration, compiler and
analytic recovery, complete supplier accounting and all five selected framework
assumptions remain open. No new kappa, supplier admission, selected-frontier
change, materialized multiplier, human review or proof-kernel acceptance follows.
