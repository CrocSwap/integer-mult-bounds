# The exact integer optimal face

## Fixed model and strict support

Use PR2863 at `34328b1d5e5bebac62d5cabec993dfbfd7b2123f`, exported in
`source/`. For positive integer T the bin inventory is T times

`B_8=672, B_16=B_32=B_48=448`.

The width inventory is `9T` times `{4:26,5:2,7:62,8:84,9:234}`.
A pattern contains a multiset of those widths whose sum is at most its
capacity c. The remaining rank is `r=c-sum(widths)`. Its cost is `H_r=r^(1-a)`,
with `H_0=0`. Fixed native costs are additional and unchanged.

This is an abstract allocation model. Chronology, family separation and
source windows impose additional physical restrictions. Every physical
packing covered by this contract induces a feasible abstract packing;
the converse is not assumed.

PR2863 supplies dual prices lambda_c, mu_w such that

`s(c,items)=H_r-lambda_c-sum(mu_w) >= 0`.

The independent verifier reconstructs these symbolic prices, authenticates
their correspondence with the source, and checks all 1,163 patterns. Uniformly
on `[0.001720100805416885927944,0.001720100805416885927945]`, exactly the eleven
patterns below have zero slack as identities; **every other slack is >1/250**.
The directed power bounds proving that strict assertion are described below.
The source's fractional feasible point has the dual objective value, also
rechecked symbolically. Thus the excess cost of any feasible pattern vector x is

`cost(x)-T*opt_idle = sum_patterns x_pattern*s_pattern`.

All x are nonnegative. Equality holds exactly when every non-tight pattern
has multiplicity zero. In particular any integer packing using a non-tight
pattern has excess >1/250. This is a statement about the unnormalized idle
numerator, not the normalized moment or kappa.

## Eliminate the inventory equations

Let a,...,k now denote pattern multiplicities (the saving exponent above is
fixed while solving these equations):

| Variable | Capacity | Helpers | Remainder |
|---|---:|---|---:|
| a | 8 | 8 | 0 |
| b | 16 | 8,8 | 0 |
| c | 16 | 7,9 | 0 |
| d | 32 | 9,9,9 | 5 |
| e | 32 | 8,8,8,8 | 0 |
| f | 32 | 7,8,8,9 | 0 |
| g | 32 | 7,7,9,9 | 0 |
| h | 32 | 5,9,9,9 | 0 |
| i | 32 | 4,9,9,9 | 1 |
| j | 48 | empty | 48 |
| k | 48 | 9,9,9,9,9 | 3 |

The bin equations give

`a=672T, b+c=448T, d+e+f+g+h+i=448T, j+k=448T`.

Width four and five give `i=234T, h=18T`. Width eight, after subtracting a,
gives `b+2e+f=42T`. Width seven gives `c+f+2g=558T`. Consequently

`c=448T-b, e=21T-(b+f)/2, g=55T+(b-f)/2`.

Substituting these expressions into the capacity-32 equation gives `d=120T`.
The width-nine equation is

`c+3d+f+2g+3h+3i+5k=2106T`.

Use `c+f+2g=558T`, `3h+3i=756T`, and `d=120T` to get

`5k=432T, k=432T/5, j=1808T/5`.

This hand elimination is separately checked by rational row reduction of all
nine inventory equations; the matrix has rank nine and two free variables b,f.

## All integer points, and no others

Since gcd(432,5)=1, integer k requires **5 divides T**. When it does, let

`u=(b+f)/2, v=(b-f)/2`.

Integrality of e forces b+f even, which also makes b-f even. Nonnegativity
of b,f,e is exactly

`u,v integers; 0 <= u <= 21T; -u <= v <= u`.

Every remaining variable is then nonnegative automatically: in particular
`c=448T-u-v >=406T`, `g=55T+v >=34T`. The complete family is

```text
a=672T         b=u+v              c=448T-u-v
d=120T         e=21T-u            f=u-v
g=55T+v        h=18T              i=234T
j=1808T/5      k=432T/5
```

Conversely every pair in that domain satisfies all nine inventories and uses
only tight patterns, so it attains the fractional minimum. This proves both
directions for **every positive integer T**, not only tested values.

For fixed u there are 2u+1 values of v. The number of distinct multiplicity
vectors is therefore `sum_(u=0)^(21T)(2u+1)=(21T+1)^2`. The coordinates b,f
recover u,v, so no two parameter pairs give the same vector. This counts
unlabelled pattern multiplicities, not assignments of actual helpers to owners.

Only d,i,j,k have nonzero remainders. Thus every optimum has idle profile

`{1:234T,3:432T/5,5:120T,48:1808T/5}`

and complete paid profile

`T*{1:21780,2:5778,3:12402/5,4:1152,5:354,8:72,48:1808/5}`.

The source T185 profile is checked against this identity. Different members
of this face cannot improve that cost; their physical realizability may differ.
The existence and cost of PR2863's actual schedule remain predecessor results.

## Nonmultiples of five are feasible but cannot attain the bound

There is a simple abstract feasible packing at every positive integer T.
Use the above family with b=f=0 outside capacity 48. Put

`432T=5q+s, 0<=s<5`.

At capacity 48 use q full five-nine bins; when s>0 use one bin with s nines;
leave the other `448T-q-[s>0]` bins empty. These counts are nonnegative,
integral and satisfy every inventory. For s=0 this is the optimum u=v=0.
For s>0 the exact excess over the fractional value is

`H_(48-9s) - (s/5)H_3 - ((5-s)/5)H_48`.

It is positive by strict concavity, since `48-9s` is the indicated strict
convex combination of 3 and 48. It is also directly enclosed by the verifier.
This gives a feasible upper bound on the nonmultiple's integrality gap;
**it is not claimed to be its minimum**. The earlier slack certificate gives
the independent universal lower bound >1/250. In particular T37 is not
declared infeasible: only exact fractional attainment at T37 is excluded.

## Independent directed arithmetic

For integer n>=2 set `z=1-1/n`. For `0<a<1`, the binomial series is

```text
1-(1-z)^a = sum_(k>=1) t_k
t_1=a*z,   t_(k+1)=t_k*z*(k-a)/(k+1).
```

All terms are positive and each ratio is less than z. After K terms the
tail lies between zero and `t_(K+1)/(1-z)=n*t_(K+1)`. Therefore

```text
n*(1-partial_sum-n*t_(K+1)) <= n^(1-a) <= n*(1-partial_sum).
```

The implementation rounds the recurrence down and up on the integer scale
`2^384` and uses K=8192. All sums and the final tail bound preserve outward
rounding. For uniform slack bounds it uses the upper saving endpoint for
lower powers and the lower endpoint for upper powers. Positive and negative
symbolic coefficients choose the appropriate endpoint. The eleven zero
slacks are recognized as exact symbolic identities rather than numerical zeros.

The same independently derived intervals reproduce both source root signs.
At a=1/2, positive interval endpoints are calibrated by exact integer squaring
against sqrt(n), including short K=1,4 runs where the tail matters. Omitting
the tail would already give the false lower bound 3/2 for sqrt(2).

The all-T argument is the elimination proof above; the 11,236 T5 vectors,
larger boundary fixtures and 200 rounded witnesses are finite implementation
controls. This package supplies no formal-kernel proof or additional native,
physical, all-size, precision/tape, recursion or outer-transfer theorem.
