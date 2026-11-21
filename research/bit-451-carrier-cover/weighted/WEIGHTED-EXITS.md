# A paid-log-moment compiler bound

The largest paid rank need not determine the logarithmic power. The
separated integer compiler has an exact exit distribution: its exits are
the chronological paid word raised to the power `G+1`. This permits an
average logarithmic contraction, certified by a finite list of rational
polynomial coefficients.

The construction, native premises, source complement recurrence and moment
cancellation are inherited from Jacob Alan Sussman's separated lockstep
compiler as retained in PR4359 and the logarithmic compiler of PR4411 and
PR4433. Only the bound on its normalized leaves changes here. There is no
new routing operation, fractional job, or independent productive credit.

## Exact exits of the separated compiler

Let the fixed mixed unit have ambient rank `m`, productive minimum `k_min`,
and a chronological paid inventory `P_r`, with

```
1 <= r_max < k_min <= m.
```

At top rank `n>=m`, put

```
G = floor(log_(k_min)(n/m)).
```

The inherited construction has one class for every paid-round path of
length `d<=G`, and degree `G-d` in that class. Separation consumes all
parent paid jobs, so there are no premature exits. At depth `G`, a path
has column multiplier `rho<=r_max^G<k_min^G<=n/m` when `G>0`; for `G=0`,
the single root has multiplier one and `m<=n`. Consequently the degree-zero
point is present in every depth-`G` class, with its exact integer weight
`u(0)=1`.

Each such leaf unit issues its complete chronological paid word. Therefore
the complete exit multiset is exactly

```
{ r_1*...*r_(G+1) : each position chooses one actual paid call },
```

including all multiplicities. The statement uses the compiler's complete
class construction, including child classes whose missing inputs are top
sources. A missing parent point does not omit the corresponding child
class. Chronological paths are not matched across different paid positions.

For `0<t<1`, set

```
Q_t = sum_r P_r*r^t.
```

For the proof only, choose independent random paid ranks with probability
`P_r*r^t/Q_t`. The exact weighted exit moment is `Q_t^(G+1)`, and its
normalized logarithmic distribution is the sum of `G+1` independent log
ranks under this probability law. This probabilistic notation describes a
finite integer inventory; the native program still uses whole jobs.

## General finite coefficient certificate

Choose `J>=r_max`, with `J>1`, and let

```
X = ln(r)/ln(J) in [0,1],
E[X] <= q,       0<=q<=1.
```

Take an integer power `p>=1` and a positive natural-log shift `a`. Choose
positive rational bounds `A_bar`, `B_under`, `beta` satisfying

```
a/ln(J) <= A_bar,
(a+ln(m))/ln(J) >= B_under,
ln(k_min)/ln(J) >= beta.
```

Let `S(i,j)` be the Stirling numbers of the second kind, with
`S(0,0)=1`, zero outside `0<=j<=i`, and

```
S(i+1,j) = j*S(i,j)+S(i,j-1).
```

For `0<=j<=p`, form the nonnegative numerator coefficients and positive
denominator coefficients

```
C_j = q^j * sum_(i=j..p) binom(p,i)*S(i,j)
                  * [q*(A_bar+1)^(p-i)+(1-q)*A_bar^(p-i)],
D_j = sum_(i=j..p) binom(p,i)*S(i,j)
                  * B_under^(p-i)*beta^i.
```

If every `C_j<=lambda*D_j`, then for every integer top rank `n>=m`,

```
E[(a+ln(exit))^p] <= lambda*(a+ln(n))^p.             (1)
```

Here the expectation uses the exact `t`-weighted exit inventory above.
The certificate has only `p+1` rational comparisons; it does not enumerate
the product paid histogram or the compiler flow at unbounded ranks.

### Proof by convex order

For a convex function `f` on `[0,1]`, the chord inequality gives
`f(x)<=(1-x)f(0)+x*f(1)`. For an increasing convex function, taking the
expectation and using `E[X]<=q` bounds it by the Bernoulli-`q` expectation.
Applying this one variable at a time to
`(A_bar+x_1+...+x_(G+1))^p` proves

```
E[(a/ln(J)+sum X_i)^p]
    <= E[(A_bar+Binomial(G+1,q))^p].
```

Write `u=G` and split the binomial as `Binomial(u,q)+Z`, with `Z` an
independent Bernoulli-`q` variable. The identity

```
E[Binomial(u,q)^i] = sum_(j=0..i) S(i,j)*q^j*(u)_j
```

uses the falling factorial `(u)_j=u*(u-1)*...*(u-j+1)`, with `(u)_0=1`.
Expanding the previous display gives exactly `sum_j C_j*(u)_j`.
The same power-to-falling-factorial identity expands
`(B_under+beta*u)^p` as `sum_j D_j*(u)_j`.

For every integer `u>=0`, all `(u)_j` are nonnegative (and vanish when
`j>u`). Coefficient domination therefore proves

```
E[(A_bar+Binomial(u+1,q))^p]
    <= lambda*(B_under+beta*u)^p.
```

Finally `ln(n)>=ln(m)+G*ln(k_min)`, so
`(a+ln(n))/ln(J)>=B_under+beta*u`. Multiplication by `ln(J)^p` proves (1).
The coefficient condition is sufficient; its failure is not a theorem
about the compiler's true optimum.

## Closing the source-complement induction

Retain the exact compiler recurrence and moment inequality from
[SHIFTED-LOG.md](SHIFTED-LOG.md). Set

```
A(n) = (1+ln(n)/a)^p,
eta = t*m^(t-1).
```

If the finite coefficient certificate has `lambda<eta`, then exact exit
moments and cancellation give

```
sum_e x_e*e^t*A(e)
    <= lambda*A(n)*sum_e x_e*e^t
    <= lambda*A(n)*sum_s w_s*s^t.
```

The complement-capacity bound is unchanged:

```
n^t*A(n)-sum_s w_s*(n-s)^t*A(n-s)
    >= eta*A(n)*sum_s w_s*s^t.
```

It is enough to check the same endpoint base guard

```
m^(1-t) <= (1+ln(m)/a)^p.
```

The monotonicity argument in SHIFTED-LOG.md then covers every ordinary base
rank, and strong induction proves `L(n)<=n^t*A(n)`. The earlier pointwise
shift guard is not required when it is replaced by this averaged exit
certificate. The final sufficient-rank check remains

```
(h+H)^p < h^p*2^((z-t)*H),  where a=h*ln(2), N=2^H.
```

This still requires the stated native compiler and strict mixed-unit
superpotential. It does not establish a compiler for overlapping ranks.

## Bounding the paid log mean after splitting and completion

The mean premise can be checked without emitting the completed histogram.
For a raw paid inventory with moment `P_t`, put

```
mu_raw = sum_r P_r*r^t*ln(r) / P_t,
A_raw = P_t^v,
J = c^v.
```

Suppose `E_split` bounds the **increase** in original-paid `t`-moment from
splitting, and `F_completion` bounds the **full paid `t`-moment** of all
split completion calls. Define `E=E_split+F_completion`. In particular,
`F_completion` must not subtract productive target-completion credit. A net
completion tax suitable for proving a superpotential cannot replace this
full paid charge in the mean bound.

An original call `R>J` has split paid moment `Q_R>=R^t`, and every split
rank is at most `J`. Thus

```
sum_(split r) r^t*ln(r)-R^t*ln(R)
    <= (Q_R-R^t)*ln(J).
```

Calls `R<=J` are unchanged. Every completion call also has split ranks at
most `J`, so its weighted log sum is at most its full paid moment times
`ln(J)`. The completed paid moment is at least `A_raw`, because splitting
increases a sublinear positive moment and completion adds nonnegative paid
calls. Consequently its normalized log mean obeys

```
E[X] <= mu_raw/ln(c) + E/A_raw.                     (2)
```

For example, certifying `mu_raw/ln(c)<=179/200` and
`E/A_raw<=1/200` gives `q=9/10`. Equation (2) is deliberately conservative;
the actual completed paid moment can give a sharper denominator.

## A small rational specialization

For a completed native4453 unit with

```
m=153^v,  J=18^v,  k_min>=22^v,  h=4*v,
```

the integer comparisons

```
18^19 < 2^80,    2^4 < 18,
18^26 < 153^15,  18^16 < 22^15
```

give `19/20<=a/ln(J)<=1`,
`(a+ln(m))/ln(J)>=19/20+26/15=161/60`, and
`ln(k_min)/ln(J)>=16/15`. Hence one may use

```
A_bar=1, B_under=161/60, beta=16/15, q=9/10.
```

At `p=60`, all 61 rational coefficient ratios are strictly below
`17/25000=0.00068`; the largest is at `j=16`, approximately
`0.0006795228122899847`. Thus any instance with `eta>3/4000=0.00075` passes
the exit guard, provided the paid-mean and base obligations also pass.
With the same bounds, `p=58` fails this coefficient guard. Setting `q=1`
also fails at `p=60`, so the certificate uses distribution information that
the largest-rank estimate omits.

These are exact finite polynomial comparisons; displayed decimal values
are explanatory. The package verifier must bind the actual raw profile,
full completion bill, exponent, power, scale, all inequalities and final
rank before treating a concrete specialization as certified. This note
does not select a new frontier or independently admit a native supplier.

Prepared with substantial OpenAI Codex assistance. New material is
Apache-2.0. The source compiler and prior logarithmic arguments retain the
attribution stated above and in the package provenance.
