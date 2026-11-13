# The exact linear information of one selected tensor phase

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Contract and result

Take the right monomial recipe in CubeJerry / Jerry Chen's
[#7426](https://github.com/CrocSwap/integer-mult-bounds/pull/7426), head
`172f4535ce8dcff79f626410af845f757c1563be`. Its unchanged factual recipe is
retained as PREDECESSOR-RECIPE.json. We study only its diagonal absolute
Gaussian phase, evaluated on the coordinates before the monomial's affine
address route. We cite the source's recipe binding; we do not replay that
binding or its literal tape program.

Let S={0,1,2,3,5,6}. In its strict-upper convention the source phase is

    q(x) = 1 + 3 sum_(i in S) x_i
             + 2 sum_(i<k, i,k in S) x_i x_k + 2 x_7 (mod 4).

The diagonal phase is i^q(x). Coordinates 4 and 8 are spectators. For f>=1,
the tensor phase on x in F2^(9f) is

    Q_f(x) = sum_(j=1..f) q(x^(j)) (mod 4).

A binary affine-linear observation is Lx+c in F2^k. An arbitrary decoder of
its output must recover Q_f(x) on every input. The observation and decoder
are fixed, with no auxiliary access to x. Observation count means the
rank of L; deleting dependent output bits always gives an equivalent
statistic. No bound on the decoder's computational cost is asserted.

**Theorem.** The exact minimum observation rank is f+1. An attaining linear
statistic is

    r_j = XOR_(i in S) x_(i,j),   j=1..f,
    b   = XOR_(j=1..f) x_(7,j).

Its decoder is

    Q_f(x) = f + 3 sum_j r_j + 2b (mod 4).                  (1)

In particular, fifteen quadratic pair terms per column disappear from
this phase description. Compared with retaining the two natural observations
r_j and x_(7,j) separately at every column, aggregating the latter saves
f-1 independent observation bits. The sharp bound is about binary linear
information. Q_f itself has only four possible values, so two nonlinear
output bits always suffice. That is a different observation contract.

## Contraction

For Boolean bits, the classical identity

    XOR_i x_i = sum_i x_i - 2 sum_(i<k) x_i x_k (mod 4)

follows by expanding (1-product_i(1-2x_i))/2. Every term of degree at
least three is divisible by four. Multiplying by 3 modulo four gives
coefficient 3 on each linear term and coefficient 2 on each pair. Thus

    q(x) = 1 + 3 r(x) + 2 x_7 (mod 4).

Summing over columns proves (1), because twice an integer depends modulo
four only on that integer's parity. This keeps the absolute constant f.
Replacing it by one would fail already at f=2. No phase is discarded as
an irrelevant scalar.

## All translation periods and the lower bound

For a function Q on a binary vector space define its translation-period
subgroup

    K = {a : Q(x+a)=Q(x) for every x}.

It is a vector subspace, since successive translations by periods preserve
Q. A statistic Lx+c determines Q if and only if ker L is contained in K.
For necessity, x and x+a have the same observation whenever a is in ker L.
For sufficiency, every observation fiber is one such coset and Q is
constant on it. Therefore every sufficient statistic has rank at least
codim K. Taking any linear quotient by K attains this bound. The affine
offset c does not affect the argument.

We compute K for Q_f, without appealing to a finite census. Write
t_j=r_j(a) and d_j=a_(7,j). For bits u,t,

    (u XOR t)-u = t-2ut as integers.

The contracted formula gives

    Q_f(x+a)-Q_f(x)
      = 3 sum_j t_j + 2 sum_j d_j + 2 sum_j r_j(x)t_j (mod 4).   (2)

The sign in the last term is positive since -6=2 modulo four. If t_j=1,
toggle only coordinate 0 in column j of x. The last term changes by two,
while every other term stays fixed. Hence (2) cannot be zero for every x.
Every period must have t_j=0 for each j. Under those conditions (2) is
zero exactly when sum_j d_j is even. Conversely these same conditions
make (2) zero on every x. Thus the complete period subgroup is

    K_f = {a : r_j(a)=0 for all j, sum_j a_(7,j)=0 in F2}.       (3)

The f+1 equations are linearly independent. Each r_j has its own
coordinate 0, and the last equation uses coordinate 7, absent from S.
Consequently dim K_f=8f-1, and codim K_f=f+1. The displayed statistic has
exactly this kernel and attains the lower bound. This proves the theorem
for every positive f, including arbitrary binary-linear mixing of columns.

## Scope and inherited work

The source-specific contraction, complete tensor period subgroup and sharp
linear-observation rank are the contribution. Parity expansion and the
quotient-by-periods principle are classical. Their general principles are
not claimed as new. The phase recipe, native source binding and physical
implementation belong to CubeJerry #7426, retaining Ali Romman #5375 and
the #7000 native/Gaussian lineage. Dennys / antunishdPursuit #6500 also
records parity expansion for a different contact-family verification.

No physical tape reduction follows from rank alone. A producer must acquire
the parities, retain or regenerate the f column bits, decode their weight
modulo four, restore any dirty workspace and satisfy the source's packed
layout and return contracts. Its complete time, historical backing and
recursive invoice remain unpriced. This proof changes neither the affine
address map nor the rank-one C tensor. It supplies no new kappa, supplier
admission, complete multiplication theorem or formal proof-kernel acceptance.
