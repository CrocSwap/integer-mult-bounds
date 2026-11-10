# Sharp uniform margins for the ADDRESS coefficient-bit tariff

This contribution was produced by Nick Petalas. Apache-2.0.

## Fixed contract

Use Wentao Li's PR3702 ADDRESS lowering and its coefficient-bit tariff.
For a reduced rational number x=u/v with v>0, write

```text
ell(n) = bit_length(|n|), including ell(0)=0,
c(x) = ell(u) + ell(v).
```

The ten unit coefficients cost 20. For a=k/4, the six other coefficients
are a, 1+a, -a, -a, -1/a and 1/a-1. Thus the cited word contract is

```text
T(k) = 20 + 4 c(a) + c(1+a) + c(1/a-1),   k != 0.
F(q,j) = 2 T(q 2^j) + T(q 2^(j+1)),
B(q,j) = 4 T(q 2^j).
```

Here c(1/a)=c(a). These are coefficient-table proxy bills. They do not
include native execution, routing, restoration or physical storage costs.
We take the predecessor's lowering and tariff as definitions, without
replaying its implementation or auditing its finite comparison.

## Theorem

For every odd integer q>=3 and every integer j>=0, the following are sharp
lower bounds on the excess over the corresponding q=1 bill.

```text
                         j=0    j=1    j>=2
T(q 2^j)-T(2^j)             4      6       8
F(q,j)-F(1,j)              14     20      24
B(q,j)-B(1,j)              16     24      32
```

In every cell, equality holds exactly when q=3. Consequently q=3 is the
unique cheapest non-dyadic odd kernel at each fixed exponent. The global
minimum excesses are 14 for F and 16 for B, both attained only at (q,j)=(3,0).
The same bills hold after reversing the sign of each query power.

## Word formula

Let a=u/v>0 be reduced. The fractions (u+v)/v and (v-u)/u are reduced,
because gcd(u,v)=1. This includes a=1: the zero coefficient is 0/1 and
costs one under the stated tariff. Direct substitution gives

```text
T(k) = 20 + 5[ell(u)+ell(v)] + ell(u+v) + ell(|u-v|).
```

Changing a to -a swaps the final two numerator lengths, so T(-k)=T(k).
Put b=ell(q), with q positive and odd. Reducing q 2^j/4 yields

```text
T(q)     = 35 + 5b + ell(q+4) + ell(|q-4|),
T(2q)    = 30 + 5b + ell(q+2) + ell(|q-2|),
T(4q)    = 25 + 5b + ell(q+1) + ell(q-1).
```

For q>=3 odd, q is not a power of two, so ell(q-1)=b. Also
ell(q+1)=b+epsilon, where epsilon=1 if q=2^b-1 and zero otherwise. Hence

```text
T(4q) = 25 + 7b + epsilon.
```

For j>=3 put x=q 2^(j-2). When q>=3, x is an even non-power of two.
Both x-1 and x+1 have bit length b+j-2. Therefore

```text
T(q 2^j) = 7j + 7b + 11,   q>=3, j>=3.
```

For q=1 the exact values are T(1)=45, T(2)=38 and T(4)=32. For j>=3,
x=2^(j-2) has ell(x-1)=ell(x)-1 and ell(x+1)=ell(x), giving

```text
T(2^j) = 7j + 17,   j>=3.
```

## Sharp word margins

For q=3 the four formulas give excess 4 at j=0, 6 at j=1 and 8 at every
j>=2. To establish uniqueness it remains to exclude q>=5. Then b>=3.

At j=0, ell(q+4)>=b and ell(|q-4|)>=1, so
T(q)>=36+6b>=54>49=T(3). At j=1, ell(q+2)>=b and ell(q-2)>=2,
so T(2q)>=32+6b>=50>44=T(6). The comparisons subtract the same dyadic
reference at each fixed j.

At j=2 the excess is 7(b-1)+epsilon, which is at least 14 when q>=5,
strictly exceeding the attained value 8 at q=3. At every j>=3 the excess
is 7b-6, at least 15 when q>=5 and exactly 8 when q=3. This proves the
word row and its unique minimizer for all parameters.

## Program margins

Write d(q,j)=T(q 2^j)-T(2^j). By definition,

```text
F(q,j)-F(1,j) = 2 d(q,j) + d(q,j+1),
B(q,j)-B(1,j) = 4 d(q,j).
```

The word row gives respectively 2*4+6=14, 2*6+8=20 and 2*8+8=24 for F.
It gives 16, 24 and 32 for B. Kernel 3 attains every bound. Every larger
odd kernel has a strictly larger word excess at every exponent, so none
attains any program bound. The increasing three-case bounds locate the
unique global minimizers at (3,0). This completes the proof.

## Scope of the improvement

PR3702 proves its comparison on five non-dyadic kernels and exponents
0 through 32. James Reed's PR3704 and PR3752 retain that finite range.
The new theorem removes both cutoffs and gives the exact minimum and
unique minimizer at every exponent. It rules out a cheaper odd kernel
anywhere in this particular tariff, even though T(k) is not monotone in k.
No search over further q or j is needed for that comparison.

The proof does not order kernels under a changed tariff, prove an optimal
ADDRESS lowering, or exclude a different fully charged supplier. No
selected assumption or multiplication theorem follows from it.
