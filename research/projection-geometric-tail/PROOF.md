# Four exact modes and sharp geometric convergence of the projection recurrence

Prepared by Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.

This is a theorem about the **unstrengthened arithmetic recurrence** below.
Jacob Alan Sussman (#4628) supplies its engine interpretation and seed;
Maximilian Lutz (#4643) independently derived the projection counts and checked
a finite prefix plus a conservative tail. Nick Petalas (#5151) proved the exact
limit. We use that credited limit theorem. The new contribution is the exact
four-mode representation and a two-sided geometric error estimate. During this
work JoyboyBrian's #5184 independently established strict monotonicity and the
sharp infimum by a weighted-order proof; those shared conclusions are credited
corollaries here, not claimed as a newly unresolved result.
The hook ranks and representation/engine hypotheses are not re-audited here.

## 1. Statement and inherited limit

Start with

```
a_4 = (0, 27456, 48576, 68320, 86592).
```

For integers k >= 5, define a_k(r), 0 <= r <= k, by

```
a_k(r) = N_k(r,r) a_(k-1)(r)
       + N_k(r,r-1) a_(k-1)(r-1)
       + N_k(r,r-2) a_(k-1)(r-2),

N_k(r,r)   = 2^(k-r)-1 + 4^k-2^(k+r),
N_k(r,r-1) = 2(2^k-2^(k-r)) + (2^r-1)2^(k-1),
N_k(r,r-2) = (2^r-1)(2^(r-1)-1)2^(k-r).
```

Omit out-of-range terms; the third coefficient is zero for r < 2.
Write T_m = a_m(m)/a_m(1). No triangle/max strengthening is applied.

**Theorem.** The normalized profile has the four-mode representation (2.3), and

```
2^(-m) < T_m - L < 2^(1-m)             for every m >= 5,
L = 439277/149175.
```

Thus the error has order 2^(-m). The proof also independently yields
T_(m+1)<T_m for every m>=4 and the unattained infimum L, as established
concurrently by #5184. It does not assert that every nonnegative seed is monotone.

The equality lim T_m = L is Petalas's theorem at
`e6c8e945a47dcc4a6f08974682090fc7f5e221a3`,
`research/projection-recursion-limit/PROOF.md`, Sections 1--4. Its general formula
specializes to

```
L = (11/10) (30 + 280*(48576/27456)
                  + 960*(68320/27456) + 1024*(86592/27456)) / 2295.
```

This source's SHA256 is
`83843a1460d8d5ccca4c312268e3a138f5dddc8197986ba63955392a3da0da33`.
The exact rational simplification is checked locally. Reusing this limit is
explicit: a finite prefix alone would not justify the displayed infimum.

## 2. A fixed triangular operator and four exact modes

Put x=2^k and y=2^r. On sequences f(0)=0, the raw row operator is
`N_k = d_k I + x H`, where

```
d_k = (2^(k-1)-1)(2^(k+1)+1),
(Hf)(r) = h_r f(r) + B_r f(r-1) + C_r f(r-2),
h_r = 3/2 + 2^(-r) - 2^r,
B_r = 2^(r-1) + 3/2 - 2^(1-r),
C_r = 2^(r-1) - 3/2 + 2^(-r).
```

Terms below zero are omitted. At r=1, h_1=0; hence a_k(1)=d_k a_(k-1)(1).
The normalized profile therefore evolves by `I + (2^k/d_k) H`.
The same H works at every k. At the new endpoint r=k the coefficient
N_k(k,k)=0, so no value of the old profile outside its range is needed.

The numbers h_r strictly decrease for r>=1. For j=1,2,3,4 define the sequence
e_j by e_j(r)=0 for r<j, e_j(j)=1, and, for r>j,

```
e_j(r) = (B_r e_j(r-1) + C_r e_j(r-2)) / (h_j-h_r).       (2.1)
```

It satisfies H e_j = h_j e_j on every positive row. This follows immediately
from (2.1), including the zero rows below j. The unit lower triangular seed
matrix e_j(r), 1<=j,r<=4, uniquely gives

```
(c_1,c_2,c_3,c_4) = (1, 17/39, 6181/14586, 99085/239811),
a_4(r)/a_4(1) = sum_(j=1)^4 c_j e_j(r),  0<=r<=4.       (2.2)
```

All four coefficients are positive. Define, for m>=4,

```
lambda_(k,j) = (2^(k-j)-1)(2^(k+j)+1) = d_k + 2^k h_j,
p_(m,j) = product_(k=5)^m lambda_(k,j)/d_k,
u_(m,j) = p_(m,j) e_j(m).
```

The empty product is one. All factors in these products are positive.
Induction on m, using H e_j=h_j e_j and N_m(m,m)=0 at the new row, proves

```
a_m(r)/a_m(1) = sum_(j=1)^4 c_j p_(m,j) e_j(r),
T_m = sum_(j=1)^4 c_j u_(m,j).                           (2.3)
```

Thus only four modes are required; this is an exact representation, not a
numerically fitted formula. The e_j are still defined by a second-order
recurrence; no elementary closed form for them is claimed.

For m>=6, apply the eigenvector identity to row r=m at block m, and multiply
by p_(m-1,j)/d_m. It gives the scalar second-order recurrence

```
u_m = alpha(x) u_(m-1) + beta_h(x) u_(m-2),   x=2^m,
alpha(x) = (x-1)(x+4) / ((x-2)(2x+1)),
beta_h(x) = (x-1)/(2x+1) * (1 + 2xh/((x-4)(x+1))),       (2.4)
```

where h=h_j. Initial values u_4,u_5 come from (2.1)--(2.3).

## 3. An involution controls the entire tail

Set z_m=2^m(u_m-u_(m-1)), v_m=(u_m,z_m)^t, and

```
F_h(x) = x*(alpha(x)+beta_h(x)-1),
A_h(x) = [[1+F_h(x)/x, -2 beta_h(x)/x],
          [F_h(x),     -2 beta_h(x)  ]],
J_h = [[1,0],[h+3/2,-1]].
```

Equation (2.4) is exactly v_m=A_h(2^m)v_(m-1), and J_h^2=I.
Use the maximum vector norm and its induced row-sum matrix norm.

**Uniform bound.** If -15<=h<=0 and x>=64, then

```
||J_h|| <= 16,
||A_h(x)-J_h|| <= 128/x,
||A_h(2x) A_h(x)-I|| <= 4096/x.                         (3.1)
```

Here are explicit elementary bounds proving every quantifier in (3.1).
In beta_h the parenthesized factor is between 1/2 and 1, because
`|2xh/((x-4)(x+1))| <= 30/(x-4) <= 1/2`. Consequently 0<=beta_h<=1/2,
and

```
0 <= 1-2 beta_h(x) <= 3/(2x) + 30/(x-4) <= 40/x.
```

Direct expansion gives

```
F_h(x)-(h+3/2)
 = ((6h+9)x^3 + (10h-21)x^2 - (36h+54)x - (16h+24))
   / (2(x-4)(x-2)(x+1)(2x+1)).                         (3.2)
```

The absolute numerator is at most `99x^3+171x^2+594x+264 <= 104x^3`;
the denominator is at least `3x^4`. Thus the absolute difference is <64/x,
and |F_h(x)|<15. The first row of A_h-J_h has norm at most 16/x, and the
second at most 104/x, proving the second bound in (3.1).
Writing A_h=J_h+E_h proves the third:

```
||J_h E_h(x) + E_h(2x) J_h + E_h(2x) E_h(x)||
 <= 3072/x + 8192/x^2 <= 3200/x <= 4096/x.
```

All four h_j lie in [-15,0]. From (3.1), the two-step update from v_m to
v_(m+2), for m>=5, differs from I by at most 2048*2^(-m).
Fix a parity starting at M, and put

```
S_M = sum_(i>=0) 2048*2^(-M-2i) = 8192/(3*2^M).
```

If S_M<1, every finite product of these two-step matrices differs from I
by at most S_M/(1-S_M). Indeed its norm difference is bounded by the product
of (1+2048*2^(-M-2i)) minus one. Expanding that product and bounding its
degree-n elementary symmetric sum by S_M^n gives the claimed geometric bound.
This argument needs no commutativity, diagonalization, or convergence assumption.
For every m>=M of the same parity,

```
||v_m-v_M|| <= S_M/(1-S_M) * max(|u_M|,|z_M|).           (3.3)
```

## 4. The finite exact certificate and strict monotonicity

The standalone verifier obtains u_(M,j),z_(M,j) from the four modes with
Fraction arithmetic. It independently constructs the original integer
triangle through block 48 and compares the whole normalized profile, not just
the top values. The actual infinite-tail certificate uses only M=32 and 33.
Let

```
Z_M = sum_j c_j z_(M,j) = 2^M(T_M-T_(M-1)),
R_M = S_M/(1-S_M) * sum_j |c_j| max(|u_(M,j)|,|z_(M,j)|).
```

The following are exact rational enclosures checked by integer comparisons:

| M | enclosure for Z_M | strict upper bound for R_M |
|---|---|---|
| 32 | (-858261/10^6, -858260/10^6) | 3/10^6 |
| 33 | (-1873709/10^6, -1873708/10^6) | 2/10^6 |

By (2.3) and (3.3), the same-parity scaled differences are contained in
(Z_M-R_M,Z_M+R_M). In particular, for every m>=32,

```
-9/10 < 2^m(T_m-T_(m-1)) < -4/5      if m is even,
-2    < 2^m(T_m-T_(m-1)) < -9/5      if m is odd.         (4.1)
```

These are negative intervals with substantial exact slack. The original
integer recurrence also verifies T_m<T_(m-1) for 5<=m<=33. Thus strict
monotonicity holds for every block, not just the finite checked prefix.
For calibration, T_4=41/13, T_5=834241/278850, T_6=1188222/399685.

Using the credited limit L, sum the adjacent differences in (4.1). The weights
of odd and even positions in the tail are respectively 2/3 and 1/3. Hence

```
22/15 < 2^m(T_m-L) < 49/30       for even m>=32,
17/15 < 2^m(T_m-L) < 19/15       for odd  m>=33.
```

Both intervals lie inside (1,2). Exact checks of `1 < 2^m(T_m-L) < 2`
for 5<=m<=31 supply the finite prefix. This proves the stated geometric
estimate, strict nonattainment, and exact infimum.

## 5. Scope and remaining obligations

The written operator and tail inequalities supply the universal quantifiers;
the finite exact certificate supplies the two initial tail states and finite
prefix. Automated execution alone is not a proof-kernel or independent human
review. The credited #5151 limit theorem remains a mathematical dependency.
The same proof does not establish monotonicity for every seed: the seed
(0,1,1,1,1) already increases at the next block and is a rejection control.

No hook rank, engine embedding, physical circuit, dirty-state restoration,
complete recursive price, supplier admission, multiplication exponent, or
selected frontier is established or modified. A characterization of all seeds
with monotone top ratios and elementary closed forms for the mode sequences
remain open. The optional triangle/max strengthening is a different recurrence.
