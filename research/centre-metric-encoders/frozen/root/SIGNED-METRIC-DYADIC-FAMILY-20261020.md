# A dyadic centre code for a family of signed metrics

This note gives a scalar construction for every n=4+2^r, where r
is a nonnegative integer. One output holds the centre reader.
The other outputs hold its metric-orthogonal complement. The code,
its inverse, and its diagonal metric have only dyadic coefficients.
No extra field or division by an odd integer is needed.

The bridge review lane supplied the orthogonal basis. The root
lane combined two adjacent ADDs, gave the word below, and checked
the word with a separate Fraction engine. AI assistance was used.

This is a common-frame scalar theorem. A native implementation
also needs a physical row assignment, admissible transfer support,
frame access, and a full caller. The actual six-mode and eight-mode
codes are separate packets. The basis below is not asserted to
have their ordinary zero diagonals.

## Metric and reader

Put k=2^r and n=k+4. Use coordinates

```text
(a_0,...,a_(k-1),x,y,b,c).
```

The input Gram matrix, response, and reader are

```text
K = diag(1^(k+2),-k,-k),
u = (1^(k+2),k,0)^T,
l = (-1^(k+2),1,0),
R = I+u l.
```

All diagonal entries of K are dyadic units. Also

```text
l u=-2,       R^2=I,
K l^T=-u,     l K l^T=2.
```

Thus R preserves J=K^-1. A code with first designated row l and
other rows orthogonal to l under K diagonalizes R.

## Construction

Let S be the sum of the first k coordinates. Apply the unnormalized
Walsh matrix H_k to those coordinates. Retain its k-1 contrast rows.
Set T=x+y and d=x-y. Define

```text
l = -S-T+b,
v = S-b,
w = (k/2)T-b,
w' = w+((k-2)/4)v.
```

Here l denotes the value of the same reader defined above. Use the
output rows in this order:

```text
(v+w', H_k contrasts, l, d, v-w', c).
```

Call this square matrix C. The designated centre is output k.

The contrast rows have Gram matrix k I and are orthogonal to S.
They are also orthogonal to the other displayed rows. The vector
d has norm2 and is orthogonal to T. The final c row has norm-k
and is orthogonal to all other rows.

For the remaining rows, direct calculation gives

```text
<l,l>_K=2,
<l,v>_K=<l,w'>_K=0,
<v,v>_K=<w',w'>_K=0,
<v,w'>_K=-k.
```

Therefore

```text
C K C^T = G
        = diag(-2k, k^(k-1), 2, 2, 2k, -k).
```

Every entry of G is a dyadic unit. This proves that C is invertible
over the dyadic rationals, with

```text
C^-1 = K C^T G^-1,
C^-T = G^-1 C K.
```

Every ordinary row annihilates u. The designated centre sends u
to -2. Hence

```text
C R = Z C,
Z = diag(1,...,1,-1,1,1,1),
```

where the only negative entry is at output k. In particular,
C R C^-1=Z. The determinant has the exact square

```text
det(C)^2 = det(G)/det(K) = 16 k^k.
```

These equations prove the result for all r. A finite replay is
not used to infer the general statement.

## Complete in-place word

The butterfly on two fields a,b is

```text
a += b
b *= -2
b += a
```

It produces (old a+old b, old a-old b). Apply the usual r
Walsh stages to the first k fields. Apply one butterfly to x,y.
At this point the named physical fields hold S,T,d,b,c.

Apply these six instructions:

```text
S -= b
T += S
T *= -1
b += (k/2) T
b += ((k+2)/4) S
b *= -1
```

The S,T,b fields now hold v,l,w', respectively. One final
butterfly on S,b gives the stated C output order. The c field
is unchanged. Every input can have arbitrary content.

Reverse the word and invert each instruction to obtain C^-1.
All scales are signed powers of two. Every ADD coefficient is
dyadic. No pivot, zero target, or scratch field is assumed.

## Exact scalar cost and prefix bounds

For a nonzero dyadic coefficient a/b in lowest terms, the
inherited complex-field ADD tariff is

```text
2*(1+bit_length(|a|)+popcount(|a|)+bit_length(b)).
```

A signed power-of-two scale costs twice its absolute binary
exponent, plus2 if its sign is negative. The factor2 accounts
for the two real components. These are the same primitive costs
used by the actual supplier's scalar words.

A butterfly costs20. The Walsh part costs10kr. The two other
butterflies cost40. The six-instruction block costs20 plus the
two nonunit ADD prices. Thus the complete forward and inverse
prices are equal and are exactly

```text
86                         if r=0,
96                         if r=1,
10kr+76+4r                 if r>=2.
```

The instruction count is 3kr/2+12. In particular, n=6 costs96
and n=8 costs164, before a physical pair code or output
reassignment. This count is for this basis only.

The prefix row one-norm is at most4(k+1)max(k,2) forward and
2(k+5) in reverse. To see these bounds, first separate the
Walsh and x,y blocks, whose forward prefix norms are at most
max(k,2). In the three-field block, the S and T rows have
norm at most2 and3. The b row has norm at most2k+2 after the
two ADDs. The final butterfly has prefix norm at most4k+4.
In reverse order, the three-field prefix norm is at mostk+5.
The remaining inverse butterflies have prefix norm at most2;
their completed row one-norm is1. They act on disjoint blocks.

Forward binary denominator height is at most2. The inverse
three-field block has height at most3. The remaining inverse
Walsh and x,y words add at most max(r,1). Thus inverse height
is at most max(r,1)+3. These bounds cover the literal scalar
word. They do not cover recursive children or rounding.

## Verification and scope

`check_signed_metric_family.py` imports no producer code. It
constructs C directly from its displayed row coefficients and
compares it with the literal word. It checks both inverse
orders, the full Gram identity, the reader, response
diagonalization, determinant, price, and prefix bounds for
k=1,2,4,8,16,32,64. Four extra arbitrary fields are included
and remain unchanged. A deleted first instruction must fail.

Normal and optimized Python produced identical receipts with
SHA256

```text
3a4e4e27835be8431a68051e9c58a64cb22ec53e89beaac6f58fba4a945a0d37
```

Reproduce into two new output files:

```sh
python3 check_signed_metric_family.py --out new-normal.json
python3 -O check_signed_metric_family.py --out new-optimized.json
```

Independent proof review is pending. This theorem provides a
general dyadic scalar completion. It does not prove a native
supplier or an improvement to the complete kappa calculation.

Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
No publication is authorized.
