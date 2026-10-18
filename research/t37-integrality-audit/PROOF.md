# The slack lattice and residue certificate

All claims below concern the exact fixed-U8 arithmetic relaxation in
PR942's `ALL-T-PROOF.md`, at its upper endpoint
`z=0.001664727258740678855773`. They do not assert realizability of an
arbitrary relaxed profile.

## 1. Necessary conditions and a stronger divisibility statement

Let `u(r)` be the largest signed bin price among all legal count vectors
leaving rank `r`, as in the inherited proof. The four bin capacities have
bonuses `(2,4,8,-13)` at `(8,16,32,48)`, and helper widths `(4,5,7,8,9)`
have prices `(-1,-20,-8,-2,4)`. There are exactly 1,163 legal count vectors.
The primary DFS and independent unbounded-fill computation reconstruct the
same table, including `u(0)=0`, `u(1)=19`, `u(2)=13`, and `u(48)=-13`.

For nonnegative integer counts `n_r`, the retained necessary conditions are

```
sum_r r*n_r = 14382*T,
sum_r u(r)*n_r >= -3892*T.
```

Put `v(r)=48*u(r)+13*r`. For any particular bin with capacity `a`, bonus
`b`, and helper multiplicities `h_j`, its corresponding credit is

```
48*b + 13*a + sum_j (48*price_j - 13*width_j)*h_j.
```

The four constants are `(200,400,800,0)` and the five helper coefficients
are `(-100,-1025,-475,-200,75)`. All are divisible by 25. Taking the maximum
over bins with the same remainder therefore preserves divisibility:
`25 | v(r)` for every attainable `r`. This is a statement about all legal
bin patterns, including those with negative signed credit.

Define the credit slack

```
E = sum_(0<r<48) v(r)*n_r - 150*T.
```

Because `v(0)=v(48)=0` and rank balance holds,

```
E = 48*(sum_r u(r)*n_r + 3892*T) >= 0.
```

Thus `48 | E`. Also `25 | E`, because `25 | v(r)` and `25 | 150`.
Since 25 and 48 are coprime, **E=1200*k for an integer k>=0**.
This implication uses integral counts and exact rank balance.

## 2. A sharp penalty outside multiples of 37

Use `phi`, `c` and `lambda` as defined in the README. Set
`delta(r)=c(r)-lambda*v(r)` for attainable `r` other than 0, 1 and 48.
The retained supporting inequality says that all these deltas are positive.
The new checker recomputes exact rational intervals and additionally checks

```
0 < delta(2) < delta(r)  for every such r != 2,
delta(2) < 1200*lambda.
```

The exact excess over the formal continuous optimum is

```
Delta = sum_(0<r<48) c(r)*n_r - 150*T*lambda
      = 1200*k*lambda + sum_(r not in {0,1,48}) delta(r)*n_r.
```

If `37 ∤ T`, either `k>=1` or some off-support count is positive. Otherwise
`925*n1=150*T`, hence `37*n1=6*T`, which implies `37 | T`.
Every term is nonnegative, so `Delta>=delta(2)` follows.

At `T=29`, the integer profile `{1:4,2:1,48:8689}` has mass `417078`
and signed price `-112868`, exactly `14382*29` and `-3892*29`.
It has `k=0` and one rank-2 remainder, so `Delta=delta(2)`.
Since `v(2)=650`, this exact constant is `c(2)-(26/37)*c(1)`.
It is therefore a sharp uniform *numerator* bound in this relaxation.

The normalized moment denominator is `73*896*T`. Eliminating rank 48
contributes an additional factor 48, giving

```
M_T(z)-M_formal_T37(z) = Delta/(48*73*896*T)
                      = Delta/(3139584*T).
```

No positive uniform normalized gap as `T -> infinity` follows. In particular,
this audit does not improve the selected root or kappa grid.

## 3. All residue classes with a finite graph

Write `w(r)=v(r)/25`. Removing rank one from the slack equation gives

```
37*n1 + sum_off w(r)*n_r = 6*T + 48*k.
```

Every feasible profile therefore supplies a path in the additive group
`Z/37Z`, starting at zero and ending at `6*T mod37`, with the following
edge types:

| Type | Increment modulo 37 | True cost |
| --- | --- | --- |
| One off-support rank r | w(r) | delta(r) |
| One slack unit | -48 | 1200*lambda |

The sum of its edge costs is exactly `Delta`. Order is immaterial here;
this graph is an arithmetic relaxation, not an execution schedule.

For each edge, the certificate uses an integer `L_e` such that
`L_e/10^24 <= true_cost(e)`, obtained by outward rational rounding.
For the 37 integer potentials `d(a)`, it checks

```
d(0)=0,
d(a+step(e)) <= d(a)+L_e
```

for every state and every edge: **37*43=1591 inequalities**. Telescoping
along the path of any feasible profile proves

```
Delta >= d(6*T mod37)/10^24.
```

This implication does not require trusting the shortest-path generator.
The primary generator uses Dijkstra; the independent check uses a separate
computation. Completeness requires the slack edge and all attainable
off-support ranks, including negative-credit ones.

## 4. Explicit upper witnesses and extension to every positive T

For a recorded path with off-support multiplicities `m_r` and `k` slack
edges, reconstruct

```
n1 = (6*T + 48*k - sum_off w(r)*m_r)/37,
n48 = (14382*T - n1 - sum_off r*m_r)/48.
```

The first is integral by the path endpoint. Also
`w(r) == 37*r (mod48)`, because `25*w(r)=48*u(r)+13*r` and 25 is its own
inverse modulo 48. Multiplying the second numerator by 37 therefore shows
it is divisible by 48; `gcd(37,48)=1` finishes the argument.

The certificate checks nonnegative integer counts, exact mass and exact
credit for each first positive representative `T=1,...,37`. All 37 recorded
witnesses happen to have `k=0`. Replacing `T` by `T+37` increases `n1` by
6 and `n48` by 11086, preserving both equations and all off-support counts.
Consequently the same certificate covers every positive integer replica
count, not just those first 37.

The sum of outward-rounded edge *upper* bounds for each path is an upper
bound for the witness's true excess. Each differs from its certified lower
bound by at most `10/10^24=10^-23`. This sandwiches the integer relaxation's
infimum without claiming that rounded shortest paths establish exact
transcendental minimizers. Individual bin capacities and owner geometry
are still relaxed.

## 5. Premise-removal witnesses

- Without integral counts, the smallest positive `T=1` admits equality
  with `n1=6/37`, `n48=11086/37`.
- Without the credit inequality, `T=8`, `n48=2397` has the correct integer
  mass but zero credit rather than the required 1200.
- Without rank balance, `T=1`, `n1=1`, `n48=299` meets credit but has mass
  14353 rather than 14382. Its apparent slack 775 is not divisible by 1200.
- Without strict off-support penalties, falsely allowing `delta(30)=0`
  makes `{30:1,48:299}` at `T=1` an equality profile despite correct integer
  mass and credit. The actual certified rank-30 penalty is positive.

These are concrete counterexamples to weakened implications, not bugs
reported in the inherited theorem. The checkers reject the corresponding
malformed inputs/certificates and preserve the full inherited scope.

Prepared for woklerx with substantial OpenAI Codex assistance; Apache-2.0.
Predecessor attribution and unresolved physical assumptions are in README.md.
