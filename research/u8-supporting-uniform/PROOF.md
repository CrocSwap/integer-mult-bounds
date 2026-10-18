# A uniform supporting inequality for the U8 owner relaxation

This is an independently checkable extension of the pointwise signed-dual
argument in `research/complex-t37-owners/ALL-T-PROOF.md` (PR942). For every real
`0 < b <= 1/3`, the same formal residual profile is a lower bound on the idle
moment for every positive integer replica count. A quantitative inequality
also bounds the number of positive residuals having ranks other than 1 or 48.
This result supplies no new kappa, owner construction, or unconditional
multiplication theorem.

## Model and inherited ledger

One replica has nine calls. Each call supplies whole helpers of widths
`(4,5,7,8,9)` with multiplicities `(80,32,54,122,216)`. The bin inventory per
replica consists of 672 capacity-8 bins and 448 bins of each capacity 16, 32,
and 48. A helper occupies its complete width in one bin. The residual rank of
a bin is its unused capacity. Timing, identities, owner geometry, and execution
constraints are relaxed.

The signed helper prices and bin bonuses are inherited from chafreaky's PR795
and PR890:

```
width:     4   5   7   8   9
price:    -1 -20  -8  -2   4

capacity:  8  16  32  48
bonus:     2   4   8 -13
```

For each attainable residual rank r, let u(r) be the maximum bonus plus helper
price among legal fills leaving r. Enumeration gives 1,163 legal width-count
vectors over the four capacities, with attainable ranks

```
0,1,...,41,43,44,48.
```

In particular, `u(0)=0`, `u(1)=19`, and `u(48)=-13`. Let
`v(r)=48*u(r)+13*r`; thus `v(0)=v(48)=0` and `v(1)=925`.

For T replicas, write n_r for the number of bins with residual rank r.
The inventory fixes the residual mass and actual signed price:

```
sum r*n_r = 14382*T,
sum u(r)*n_r >= -3892*T.
```

The second inequality follows because u(r) bounds each actual bin's signed
price from above. Combining these two statements gives

```
C := sum v(r)*n_r >= 150*T.
```

The count of rank-zero bins does not affect these inequalities or the moment.
The theorem below also applies directly to nonnegative real n_r satisfying
these ledger constraints; actual whole-helper packings form a smaller class.

## Monotonicity reduces the continuum to one algebraic endpoint

For b>0, define

```
phi_b(r) = r*(73/r)^b                         (r>0),
c_b(r)   = 48*phi_b(r)-r*phi_b(48),
q_b(r)   = c_b(r)/c_b(1)
         = r*((48/r)^b-1)/(48^b-1)            (0<r<48).
```

All these c_b(r) are positive for 0<r<48. At r=1, q_b(1)=1.
For 1<r<48, set `a=log(48/r)` and `d=log(48)`, so `0<a<d`.
Differentiating the logarithm of q gives

```
d/db log(q_b(r)) = a/(1-exp(-a*b))-d/(1-exp(-d*b)).
```

For fixed b>0, the function `h_b(x)=x/(1-exp(-b*x))` is strictly increasing
on x>0. Its derivative has the sign of

```
1-(1+b*x)*exp(-b*x),
```

which is positive because `exp(t)>1+t` for t>0. Thus q_b(r) is strictly
decreasing in b whenever 1<r<48. Consequently

```
q_b(r) >= q_(1/3)(r)       for 0<b<=1/3.
```

This proves the interval reduction without exponent sampling, a root-count
argument, or numerical logarithm and exponential bounds.

## Exact endpoint certificate

At b=1/3 the quotient has the algebraic form

```
q_(1/3)(r) = (cuberoot(48*r^2)-r)/(cuberoot(48)-1).
```

The certificate establishes the following deliberately rounded-down bound at
each of the 42 attainable ranks other than 0, 1, and 48:

```
q_(1/3)(r)-v(r)/925 > 554/925.                 (1)
```

Here is the exact integer recipe reproduced by `independent_check.py` for
checking (1). The primary verifier uses the equivalent expression
`r*(cuberoot(48/r)-1)/(cuberoot(48)-1)` and stores its rational lower bounds
in `CERTIFICATE.json`. Neither checker imports the other or a retained moment
engine. Set `D=10^12`, and define

```
A   = 3634241185665,
L_r = floor(cuberoot(48*r^2*D^3)).
```

Check the integer cube inequalities

```
(A-1)^3 <= 48*D^3 < A^3,
L_r^3 <= 48*r^2*D^3 < (L_r+1)^3.
```

Then `cuberoot(48)<A/D` and `cuberoot(48*r^2)>=L_r/D`. Each
`L_r-r*D` is positive, so

```
q_(1/3)(r) > (L_r-r*D)/(A-D).
```

For every relevant rank, the certificate verifies the strictly positive integer

```
E_r = 925*(L_r-r*D)-(v(r)+554)*(A-D).
```

The least such integer is

```
E_44 = 1794386594565 > 0.
```

Therefore (1) follows by division by the positive integer `925*(A-D)`.
This calculation treats negative v(r) correctly: v(r) is subtracted exactly,
and no signed coefficient is multiplied by an incorrectly directed interval.

Combining (1) with monotonicity proves, uniformly for 0<b<=1/3,

```
c_b(1) = (v(1)/925)*c_b(1),
c_b(r) > ((v(r)+554)/925)*c_b(1)
          for every attainable r other than 0,1,48.                (2)
```

At r=48 both the excess cost and v are zero. Rank zero contributes zero by
definition. Thus the unstrengthened supporting inequality
`c_b(r)>=v(r)*c_b(1)/925` holds at every rank, with equality only at 0, 1,
and 48.

## The all-replica lower envelope and quantitative residual bound

Let `K=sum_(r not in {0,1,48}) n_r`. Sum (2), using its weaker non-strict
version, and use the definition of C:

```
sum c_b(r)*n_r >= (c_b(1)/925)*(C+554*K).
```

The mass identity gives

```
sum phi_b(r)*n_r
  = (14382*T/48)*phi_b(48) + (1/48)*sum c_b(r)*n_r.
```

Define the formal lower envelope

```
F_b(T) = (T/37)*(6*phi_b(1)+11086*phi_b(48)).
```

The coefficients have total residual mass `14382*T`, and their credit is
`150*T`, since `925*(6/37)=150`. Subtraction yields the quantitative bound

```
sum phi_b(r)*n_r - F_b(T)
  >= c_b(1)/(48*925) * (C-150*T+554*K)
  >= (554*c_b(1)/(48*925))*K.                                  (3)
```

In particular, F_b(T) is a lower bound for every positive integer T, uniformly
on the entire stated exponent interval. If an idle moment is at most
`F_b(T)+epsilon` for epsilon>=0, then (3) gives

```
K <= 48*925*epsilon/(554*c_b(1)).
```

The analogous per-replica estimate is obtained by dividing both epsilon and K
by T. This is a bound in the unnormalized idle moment; a complete normalized
moment has its own positive normalization factor.

Equality with F_b(T) requires K=0 and C=150*T. The only positive residual
ranks are then 1 and 48, and the ledger equations force

```
n_1  = 6*T/37,
n_48 = 11086*T/37.
```

Conversely, these residual counts attain equality in this relaxation. For
integer counts and positive integer T, equality therefore requires T to be
a positive multiple of 37. This divisibility condition and these formal
counts do not by themselves establish a realizable owner assignment.

Any fixed local paid profile adds the same moment contribution to every
owner assignment being compared. A positive normalization also preserves
the inequality. Hence this idle lower envelope transfers to those moment
comparisons, without certifying any changed local circuit or full recurrence.

## Relationship to the earlier results and limits

PR795 and PR890 supply the signed prices, bonuses, and fixed inventory
ledger. PR942's retained `ALL-T-PROOF.md` establishes the rank-one supporting
inequality at one certified saving endpoint and derives the all-T relaxation
bound there. The present result verifies that supporting inequality over the
whole interval 0<b<=1/3 and supplies (3). It does not improve PR942's kappa.

The separate PR850 package, `research/owner-profile-uniform`, proves an exact
integer-profile optimum for the fixed 72-call inventory, with profile
`{48:2396,44:1,3:1,1:1}`, over the same exponent interval. Its inventory is the
T=8 instance of the present family. Its proof uses additional integer
exclusions and concavity, with separate continuum certificates. The present
all-T fractional lower envelope does not replace that stronger T=8 integer
optimum and does not claim a new fixed-72-call optimum.

This proof covers only the stated width inventory, capacities, signed ledger,
whole-helper residual model, and exponent interval. It certifies neither
changed inventories nor split helpers, compiler admission, common-label or
mutable-source realization, whole-call hosting, finite precision, tape,
analytic transfer, bit-side hypotheses, or a fresh native execution. Retained
constructions and numerical outer-transfer results remain separate evidence.

The interval restriction is substantive. At b=1, the unstrengthened scaled
margin for rank 32 is exactly
`925*(48-32)/47-v(32) = -22800/47 < 0`. This is a counterexample to extending
the same supporting line through b=1; it does not locate its exact first
failure or claim that 1/3 is the largest valid endpoint.

Prepared with substantial OpenAI Codex assistance. Independent arithmetic
cross-checks in this package are computational checks, not independent human
peer review or a proof-assistant formalization.
