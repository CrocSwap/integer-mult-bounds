# Retaining concentration of the paid tensor's log ranks

The mean-only certificate in [WEIGHTED-EXITS.md](WEIGHTED-EXITS.md) replaces
one completed unit's log rank by a Bernoulli random variable. A tensor unit
has substantially more structure: before splitting, its normalized log rank
is an average of independent raw log ranks. The following finite rational
certificate retains that concentration, bounds the effect of every paid
completion, and uses the same inherited integer compiler.

This is a bound on normalized paid rank-one leaves, conditional on the
source native and finite compiler contracts. No new native operation,
unpaid completion, overlapping-rank compiler or selected-frontier change
is asserted. All probability laws below describe finite weighted
inventories; they do not replace whole integer jobs by fractional inputs.

## Raw tensor moments

Fix `0<t<1`, `c>1`, a positive integer `v`, a positive support bound `L`,
and a raw paid inventory with positive `t`-moment `P_t`. Under its
probability law `P_r*r^t/P_t`, put

```
Y = ln(r)/ln(c),
0<=Y<=L,       E[Y]<=q0,       0<=q0<=L.
```

For a chronological `v`-fold product, let `J=c^v`. The normalized raw
tensor log rank is exactly

```
X_raw = ln(R)/ln(J) = (Y_1+...+Y_v)/v,
```

with independent copies of the raw law. The raw product's paid `t`-moment
is `A_raw=P_t^v`.

The convex chord bound replaces each `Y_i` by `L` times a Bernoulli random
variable of mean `q0/L`. For every positive integer `i`, this gives

```
E[X_raw^i] <= M_i,
M_i = (L/v)^i * sum_(j=0..i) S(i,j)*(q0/L)^j*(v)_j. (1)
```

Here `S(i,j)` are Stirling numbers of the second kind, and `(v)_j` are
integer falling factorials, zero for `j>v`. Equation (1) follows either by
expanding the binomial moment or by applying convex order one variable at
a time to the nonnegative convex function `x^i`. When `L,q0` are rational,
all `M_i` are rational.

## Splitting, full paid completion and normalization

Split every original paid rank above `J`, and also split every paid
completion into positive ranks at most `J`. Let the final paid `t`-moment
be `Q_t`. Define its actual excess by

```
E_actual = Q_t-A_raw >= 0,
x = E_actual/A_raw.
```

The excess contains the increase in original-paid moment from splitting
**plus the full paid moment of completion calls**. It does not subtract
productive target-completion credit. Suppose a proved paid bound gives

```
0<=x<=epsilon.
```

For the final completed paid law, put `X=ln(r)/ln(J)`, so `0<=X<=1`.
Its `i`-th moment has the rational upper bound

```
E[X^i] <= mu_i := min(1, (M_i+epsilon)/(1+epsilon)), (2)
mu_0 := 1.
```

The denominator in (2) needs a capped reference law. It is not justified
merely by overcounting an unnormalized numerator. For an original tensor
call `R>J`, use the reference value
`min(ln(R)/ln(J),1)^i=1`. If its split paid moment is `Q_R`, the split
weighted `i`-moment is at most `Q_R`, so its increase over this capped
reference is at most `Q_R-R^t`. For `R<=J`, the original call is unchanged.
Each full completion contributes at most its full paid moment, because
its final log ranks also lie in `[0,1]`. Thus, with

```
m_i = E[min(X_raw,1)^i] <= min(1,M_i),
```

the final weighted numerator is at most `A_raw*m_i+E_actual`.
Dividing by the actual total `A_raw+E_actual` gives
`E[X^i]<=(m_i+x)/(1+x)`. For `m_i<=1`, this expression increases with
`x`, since its derivative is `(1-m_i)/(1+x)^2>=0`. Substitution of
`x<=epsilon` and `m_i<=min(1,M_i)` proves (2). The cap is an auxiliary
proof device, not a change to the native program.

A convenient paid excess bound from this package is

```
epsilon >= (splitting_coefficient*gamma_u^v + 2*delta^v)/alpha^v.
```

The second term is the predecessor's full completion bound. A sharper
proved full completion bound may replace it. The net completion tax used
to prove a superpotential cannot replace it.

## Bell-polynomial exit certificate

The separated compiler's exact exit law is proved in WEIGHTED-EXITS.md:
at height `G`, it consists of `G+1` independent copies of the completed
paid log law. Take a positive integer `p`, positive scale `a=h*ln(2)`,
and rational bounds

```
a/ln(J) <= A_bar,
(a+ln(m))/ln(J) >= B_under,
ln(k_min)/ln(J) >= beta > 0.
```

Require `B_under>0` as well.

The ambient `m` and productive minimum `k_min` in these displays belong
to the **completed tensor unit**, not the raw unit.

For `0<=k<=n<=p`, construct partial exponential Bell polynomials from
the upper moments in (2):

```
Bell(0,0) = 1,
Bell(n,0) = 0 for n>0,
Bell(0,k) = 0 for k>0,
Bell(n,k) = sum_(i=1..n-k+1)
              binom(n-1,i-1)*mu_i*Bell(n-i,k-1).
```

They have nonnegative coefficients in the `mu_i`. Also set

```
Shift(r) = sum_(i=0..r) binom(r,i)*A_bar^(r-i)*mu_i.
```

For `0<=j<=p`, form

```
C_j = sum_(i=j..p) binom(p,i)*Shift(p-i)*Bell(i,j),
D_j = sum_(i=j..p) binom(p,i)*S(i,j)*B_under^(p-i)*beta^i.
```

All `D_j` are positive. If `C_j<=lambda*D_j` for every `j`, then

```
E[(a+ln(exit))^p] <= lambda*(a+ln(n))^p             (3)
```

at every integer compiler rank `n>=m`.

To prove (3), write `u=G`, separate one completed paid variable `X_0`,
and expand the moments of the other `u` independent variables. For their
actual moments, the standard finite identity is

```
E[(X_1+...+X_u)^i]
    = sum_(j=0..i) (u)_j*Bell_actual(i,j).
```

It follows directly by grouping the indices in the expanded power by
their equality partition; each occupied index contributes its corresponding
moment. Replacing actual moments by the upper bounds `mu_i` preserves the
inequality because all coefficients are nonnegative. Expanding
`(A_bar+X_0+...+X_u)^p` therefore gives at most
`sum_j C_j*(u)_j`. Expanding `(B_under+beta*u)^p` gives exactly
`sum_j D_j*(u)_j`.

The falling factorials are nonnegative for every integer `u>=0`.
Coefficient domination proves the desired polynomial comparison.
Finally, `ln(n)>=ln(m)+G*ln(k_min)` implies
`(a+ln(n))/ln(J)>=B_under+beta*u`, completing the proof.

This general coefficient test also accepts other rigorously proved upper
log moments; the raw chord bound (1) is one reusable source of them.

## Uniform-rank consequence

As in WEIGHTED-EXITS.md, it is enough that

```
lambda < eta := t*m^(t-1),
m^(1-t) <= (1+ln(m)/a)^p.
```

The first inequality pays exits by source complements. The second covers
the entire ordinary base range by the monotone endpoint argument in
SHIFTED-LOG.md. Strong induction gives

```
L(n) <= n^t*(1+ln(n)/a)^p.
```

For `N=2^H` and desired exponent `z>t`, the final exact guard is

```
(h+H)^p < h^p*2^((z-t)*H).
```

Neither the pointwise maximum-exit contraction nor the Bernoulli
mean-only certificate is needed when (3) is used instead.

## Balanced native4453 diagnostic

The package's balanced construction uses the unchanged raw paid profile
and the exact parameters

```
C=90037/30000000, t=1-C,
v=260, c=20, b=21, u=171/1000,
m=153^260, J=20^260, k_min>=21^260.
```

A rational log-moment witness is

```
q0=431/500, L=3/2, epsilon=1/100000,
p=24, h=3900=15*v,
A_bar=139/40,
B_under=347/100+1679/1000=5149/1000,
beta=127/125.
```

The raw maximum 72 satisfies `72^2<20^3`, proving `Y<=3/2`. The raw
mean and full paid excess need their separate profile-bound interval
checks. The full paid relative excess is below
`0.000001447491519<epsilon`. The scale and ambient/minimum log bounds use
the same rational enclosure method as the mean-only witness, with its
`h=3*v` scale bounds multiplied by five.

For this witness, all 25 rational coefficient ratios are strictly below
`39/2000=0.0195`; their maximum is at `j=24`, approximately
`0.01935272277469461`. The source complement capacity is greater than
`0.019675906372710418`. The same moment witness at `p=23` fails the
coefficient capacity condition. These are finite certificate comparisons,
not an optimality result for all potentials.

At target `kappa=0.00300120`, the package's outer allocation gives
`z-t=(C-kappa)/7=1/210000000`. The integer rank witness is

```
H=125790000000,
(3900+125790000000)^24 < 3900^24*2^599.
```

The preceding grid point `H=125580000000` fails its comparison with
`2^598`. Relative to PR4453's specified `H=2299850000000`, this is about
an 18.28-fold reduction in the sufficient rank exponent. It combines the
net-tax construction, changed exponent allocation and moment compiler;
it is not a physical runtime factor. The package verifier must certify
the net tax, raw mean, full excess, log guards, base range, coefficients,
final rank and its binding to the complete outer consumer before accepting
this diagnostic as a concrete conditional result. The package retains the
predecessor's outer point and authenticates its receipt; a stronger supplied
uniform saving meets that point by monotonicity. This does not replay the
native or outer producer proof engines.

## Open next questions

1. **Sharpen moments or shift scales only when they change a certified
   construction.** Exact raw log moments can replace the chord bound in
   (1), and a proved smaller full completion bill can reduce epsilon.
   Start by checking whether a smaller integer power or larger logarithmic
   scale actually passes all coefficients; higher numerical precision alone
   is not a new construction.
2. **Control physical and precision constants of the new finite word.**
   These leaf-count bounds retain the inherited finite-list prescriptions.
   The complete productive width, physical adapter expansion, stock and
   recovery thresholds remain separate obligations.
3. **Independent scientific review.** The Bell and cap arguments are
   finite algebraic inequalities, not a formal proof of the inherited
   all-column native, analytic or multiplication theorem.

Prepared with substantial OpenAI Codex assistance. New material is
Apache-2.0. The integer compiler is Jacob Alan Sussman's construction,
retained through PR4359. The logarithmic predecessors are zxv's PR4411 and
PR4433; native4453 retains the source and contributor attribution in this
package's provenance.
