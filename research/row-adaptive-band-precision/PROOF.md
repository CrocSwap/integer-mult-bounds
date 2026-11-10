# Row-dependent precision in cyclic-band elimination

This contribution was produced by Nick Petalas. Apache-2.0.

## Claim and predecessor boundary

This is a scoped written mathematical proof, with finite exact corroboration.
It changes the precision allocation in Ali Romman's
[PR5284](https://github.com/CrocSwap/integer-mult-bounds/pull/5284),
[cyclic-band proof](../cyclic-band-gap-solver/PROOF.md). That predecessor supplies
one-round fixed-integer elimination, the cyclic fill pattern, variable-gap
stability and its common-grid solve. Its row residual uses `N K h` in every
row. The new step permits monotone, unequal row grids and replaces that
residual by a row-support bound. The arithmetic method and classical
row-dominance estimates retain their predecessor credit.

Let A be a real N by N dyadic matrix on the p-bit fractional grid. Suppose

    a_ii - sum_(j != i) |a_ij| >= delta > 0,
    max_i sum_j |a_ij| <= M,
    a_ij = 0 when min(|i-j|, N-|i-j|) > W,    0 <= W < N.

No symmetry or sign condition on off-diagonal entries is required. Let b be
real or complex on a supplied dyadic grid. In the complex case use the norm
`max_i (|Re b_i| + |Im b_i|)` and assume it is at most Y>0. Choose a desired
absolute solution error t>0. Input formation and final-grid errors are outside
this contract.

Take a symmetric symbolic elimination pattern containing the cyclic band,
closed under natural-order Schur updates. Let m_i count the strictly lower
factor positions and the diagonal/upper positions in row i, including positions
whose numerical value is zero. Write

    K = max(1,2M),
    p <= q_0 <= ... <= q_(N-1),       S_i = 2^q_i,
    h_i = 1/S_i,                    e = max_i m_i K h_i.

The following construction gives factors B=LU with `||B-A||_infinity <= e`.
If e<=delta/2, all its pivots are positive and

    ||U|| <= 3M/2,     gap(U) >= delta/2,
    ||L|| <= 2M/delta, ||B^-1|| <= 2/delta,
    ||L^-1|| <= 3M/delta.

Every norm on a real matrix is its absolute row-sum norm.

## Exact mixed-grid construction

Store unfinished Schur row i at scale S_i squared. Initialize
`C_ij = a_ij S_i^2`, exactly. At pivot k perform

    U_int[k,j] = trunc(C[k,j]/S_k),                         j>=k,
    L_int[i,k] = trunc(C[i,k]/(U_int[k,k] 2^(q_i-q_k))),    i>k,
    C[i,j] -= L_int[i,k] U_int[k,j] 2^(q_i-q_k),           i,j>k.

Visit the declared symbolic positions only. Here trunc rounds toward zero,
`U[k,j]=U_int[k,j]/S_k`, `L[i,k]=L_int[i,k]/S_i`, and L has unit diagonal.
The nonnegative exponent `q_i-q_k` is essential. It lets each update be an
exact integer subtraction on the row-i grid without increasing that grid.
It also makes the lower formula precisely rounding `C_real[i,k]/U[k,k]`
to row i's factor grid. No multiplication or Schur update is rounded.

Expanding row i's exact updates shows that a completed upper position has
residual less than h_i, and a completed lower position has residual less than
`h_i |U[j,j]|`. The same identities apply to a partial factorization: put
these residuals at completed positions of A and zero at unfinished positions.
Its completed factors are exact factors of this partially perturbed matrix.
Outside the symbolic factor pattern the residual is zero, since the pattern
is closed under elimination. Consequently a partial row residual is at most
`m_i K h_i` whenever completed pivots have magnitude at most 2M.

For completeness, the needed classical exact row-dominance facts are as
follows. Eliminating multiplier l from a row of a positive-diagonal matrix
with row gap g and row norm R increases the surviving row gap by at least
`|l| g` and decreases its absolute row sum by at least `|l| g`. Pivots stay
positive. If s is the accumulated absolute multiplier sum in one row, its
final gap is at least `g(1+s)` while its final row norm is at most `R-gs`.
Thus `||L|| <= (R+g)/(2g)`, `||U||<=R`, `gap(U)>=g`, and
`||B^-1||<=1/g`. These are the estimates used in PR5284, cited here as
predecessor mathematics rather than an audit target.

Apply these facts to each partially perturbed matrix with
`R=M+e`, `g=delta-e`. Since e<=delta/2<=M/2, a newly completed pivot has
magnitude at most `M+e<=3M/2<2M` and is at least delta/2. This closes the
induction from the first pivot, proves every division is defined and proves
the factor residual claim. The L bound follows from
`(M+delta)/(2(delta-e))<=2M/delta`. Finally
`L^-1=U B^-1` gives `||L^-1||<=3M/delta`. The same arguments hold for every
leading principal factor pair, since deleting columns cannot decrease a
row-dominance margin.

## An independently chosen solve grid

Choose a common solve grid step `h_s=2^(-q_s)` containing b's input grid.
Accumulate each triangular dot product exactly, then round the solved
coordinate once. A lower or upper row-i product has grid `S_i 2^q_s`, so the
mixed factor grids introduce no extra numerical rounding. Execute separately
on the real and imaginary components. The triangular equations obey

    L z = b + f,       ||f|| <= 2 h_s,
    U x = z + g,       ||g|| <= 3 M h_s.

Hence `B x=b+r`, with

    ||r|| <= R_s = 2 h_s (1+3M^2/delta).

The factor two is a sufficient common bound for the complex component norm;
a real solve is covered too. The resolvent identity and `||A^-1||<=1/delta`
give

    ||x-A^-1 b|| <= (eY + delta R_s)/(delta(delta-e)).

In particular it suffices to choose

    e <= min(delta/2, t delta^2/(4Y)),
    h_s <= t delta^2/(8delta+24M^2).

The first contribution is at most `2eY/delta^2<=t/2`, and the second is at
most `2R_s/delta<=t/2`. Factor precision and solution precision can therefore
be chosen separately. If b has a finer input grid, increase q_s to include it.

## The cyclic-band improvement

For N>2W put the last W indices in the border. Natural-order elimination of
a bulk index connects only its next W bulk indices and the W border indices.
A bulk row has at most W earlier bulk neighbors and at most 2W later
neighbors. Therefore

    m_i <= min(N,3W+1)   for i<N-W,
    m_i <= N            for i>=N-W.

This is also the usual fill argument in PR5284, now used to price residuals
row by row. If N<=2W, use the dense count N everywhere. The formulas above
then still give the same safe allocation because `min(N,3W+1)=N`. If W=0,
every row has one position and no border is needed.

For a funded e-budget define

    q_bulk = max(p, ceil(log2(min(N,3W+1) K / e_budget))),
    q_high = max(p, ceil(log2(N K / e_budget))).

Assign q_bulk to the first N-W rows and q_high to the final W rows. These
precisions are nondecreasing, so the mixed-grid theorem applies. The full
length enters only the border factor precision. For fixed W, delta, M, Y,
p and t, the required precision on every bulk factor row is independent of N.
This removes a logarithmic length term from those rows' sufficient guards.
The common-grid allocation using the same e-budget requires q_high on every
row. No assertion is made that either sufficient allocation is optimal.

The arithmetic schedule still has at most `4 N W^2` factor products and
`8 N W` products per complex solve. There are at most `(4W+1)N` stored factor
positions. The new shifts are exact rescalings, not additional oracle calls.
This is an arithmetic/precision statement; it does not certify a native
instruction tariff, variable-record tape layout, wall-time gain or complete
recursive bill. A machine choosing one common word width still pays its
maximum required width.

## Integer ranges

One can retain the predecessor's dimension-free magnitude bounds. Put

    L_0=2M/delta, U_0=3M/2,
    Z=(3M/delta)(Y+2h_s), X=(2/delta)(Y+R_s),
    C=max(1,M+L_0 U_0,Y+L_0 Z,Z+U_0 X,L_0,U_0,Y,Z,X).

Absolute partial dot sums are bounded by their row sums. Thus factor row i's
Schur entries, update products and division numerators need magnitude at
most `C S_i^2`. Its divisor `U_int[k,k] 2^(q_i-q_k)` has magnitude at most
`U_0 S_i`. A signed width `2q_i+ceil(log2 C)+2` suffices for factor work.
Solve row i's accumulators need at most `C S_i 2^q_s`, so width
`q_i+q_s+ceil(log2 C)+2` suffices there. Forward prefixes use the leading
principal estimates above. Backward intermediates are already coordinates
of the final x, so the final bound covers them. Finite Python execution uses
unbounded integers; these are written sufficient range bounds, not an emitted
bounded-word implementation certificate.

## First strict fixture and finite evidence

Take N=65, W=1, diagonal 1, and cyclic adjacent entries -63/128. Its row gap
is delta=1/64. Use M=2, Y=1, alternating right-hand side 1,-1, and target
`t=2^-16`. The chosen e-budget is `2^-30`. The allocation is

    factor rows 0..63: q=34,   factor row 64: q=39,
    common solve grid: q_s=35, matched common factor grid: q=39.

There are 319 symbolic factor positions, 254 in bulk rows. Their declared
fraction-bit total falls from 12,441 to 11,171, a saving of 1,270. This counts
fractional precision per symbolic factor position, including zeros; it is
not a measurement of Python memory or a physical encoded representation.
The constructor performs 253 factor update products. The exact original-
matrix residual is `1443/4398046511104`, and the general sufficient error
bound is `1793/268435440 < 2^-16`. Independently, residual divided by delta
also certifies the requested solution accuracy.

The verifier additionally checks the support bounds on 1,125 symbolic patterns
with 1,171,245 row positions, and checks 252 signed and unsigned, generally
nonsymmetric small dyadic systems against an independent pivoted rational
solver. These are finite corroboration of the written all-size result, not a
replacement for it. No predecessor scientific suite is replayed. Complex
vectors are covered by the written two-real-solve argument; the executable
fixtures use real right-hand sides.
