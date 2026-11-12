# Optimal three-query dyadic repair at arity 24

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The fixed reader and rational two-query comparison are due to Nick Petalas
(PR6200); the general-frame dyadic contract is apoursh's PR6212. This answers
the r=24 case of Nick Petalas's PR6653, Open next question 1.

## Contract

Work in R=Z[1/2], with arbitrary distinct incoming streams (Y,A,B) in the
exact-arithmetic contract of PR6212. Retain all 24 children, in order:

```
y += a^3
a += b
```

The eager comparator undoes the source shift after each child and ends at
(Y+24A^3,A,B). The deferred endpoint is
(Y+sum_{i=0}^{23}(A+iB)^3,A+24B,B). Only appended, input-independent dyadic
linear source changes and signed weighted cube queries are allowed. There
is no output feedback, intermediate observation, child-interior access,
nonlinear source change, output recoding or borrowed clean state. Reading
either named source a or b is allowed and separately priced. Every source
change below is an elementary shear in SL2(R).

**Theorem.** The exact minimum number of appended weighted cube queries at
r=24 is three. An attaining program uses five source shears, no scratch
registers, and restores both arbitrary incoming sources. Five is an upper
bound on shear count, not a shear-minimality claim. No physical cost saving
or new multiplication exponent is asserted.

## Exact identity

The output defect is

```
D24 = sum_{i=0}^{23}(A+iB)^3 - 24A^3
    = 828 A^2 B + 12972 A B^2 + 76176 B^3.
```

Here S1=276, S2=4324 and S3=76176=276^2. The new certificate is

```
D24 = -(23/1024)(11A+19B)^3
      +(1679/64)(A+9B)^3
      +(3749/1024)(A+25B)^3.                         (1)
```

Multiplying by 1024 gives an integer coefficient check:

| Monomial | -23(11A+19B)^3 | 26864(A+9B)^3 | 3749(A+25B)^3 | Sum |
|---|---:|---:|---:|---:|
| A^3 | -30613 | 26864 | 3749 | 0 |
| A^2 B | -158631 | 725328 | 281175 | 847872 |
| A B^2 | -273999 | 6527952 | 7029375 | 13283328 |
| B^3 | -157757 | 19583856 | 58578125 | 78004224 |

The last column is 1024 times the coefficient vector of D24. Thus (1) is
a polynomial identity, rather than a conclusion inferred from sample inputs.

The discovery uses PR6653's node condition
`e2(c)=((2r-1)/3)e1(c)-r(r-1)/2`. Taking c1=19/11 and c2=9 gives c3=25;
solving the coefficient equations and unnormalizing the first form gives
(1). The slope 19/11 is not dyadic, but the actual form 11A+19B and its
weight are dyadic. A projective slope is a ratio of row entries and need not
belong to R. This is the general-frame possibility excluded from PR6653's
integer-direction search, not a contradiction to that finite search. We do
not prove that every r=24 certificate must use a nonmonic form.

## Literal repair and dirty restoration

Starting from the actual deferred endpoint, append exactly:

```
a += b
y -= (3749/1024)*a^3
b -= (11/256)*a
y -= 376832*b^3
b += (11/256)*a
a -= 16*b
y -= (1679/64)*a^3
a -= 9*b
```

After the first shear a=A+25B. The next source change gives

```
b = B - (11/256)(A+25B) = -(11A+19B)/256.
```

Since `376832 = 23*256^3/1024`, the middle query adds
`+(23/1024)(11A+19B)^3`. The following shear restores b=B exactly while
a stays A+25B. The last two source shifts visit A+9B and then A.
Consequently the three queries subtract (1), and the final endpoint is
(Y+24A^3,A,B) for arbitrary dirty Y,A,B. In particular, b is restored before
its use in the final a shifts. No copy or initialization of either source
is needed. Each event is invertible by reversing its sign; no query writes
its source and no shear reads its own target in the added expression.

The nonmonic query is reached by an explicit legal frame, so primitive-row
completion or division by 11 is unnecessary. At that query the source matrix is

```
[    1          25    ]
[ -11/256    -19/256  ],
```

with determinant (-19+275)/256=1. All other source frames are also products
of the displayed determinant-one dyadic shears.

## Three queries are necessary

The following specializes the rational comparison from PR6200/PR6212, and
makes the r=24 lower bound self-contained. Any appended program with at most
two queries represents D24 by at most two rational weighted cubes, after
negating the query weights. General source frames merely change their two
linear forms; this argument allows all such forms, even ones not realizable
by a source frame.

A single cube cannot have zero A^3 coefficient but nonzero A^2 B coefficient.
Discard zero-weight terms; a single term was already excluded. With two
nonzero weights, both A coefficients must be nonzero: otherwise A^3
cancellation forces both A coefficients to vanish, contradicting A^2 B.
Normalize over Q. Cancellation of A^3 then gives

```
D24 = lambda*((A+tB)^3 - (A+sB)^3),
lambda*(t-s)=276,   t+s=4324/276=47/3,
t^2+t*s+s^2=76176/276=276.
```

The first equality forces t!=s. The last two give

```
(t-s)^2 = 4*276 - 3*(47/3)^2 = 1103/3.
```

This reduced fraction has denominator 3. A rational square in lowest terms
has a square denominator, so no rational t,s exist. Two rational queries are
therefore impossible, and in particular two dyadic queries are impossible.
Together with the explicit program this proves the exact minimum three.

## Complete event boundary and unpaid obligations

Let `La_k` price a shear a+=k*b, `Lb_k` a shear b+=k*a, and `Qa_k`, `Qb_k`
a weighted cube query into y on the named source. Each price must include
its actual coefficient, source access, private restoration and return under
one matched backend. The complete appended event inventory is

```
I24 = La_1 + Qa_(-3749/1024) + Lb_(-11/256) + Qb_(-376832)
      + Lb_(11/256) + La_(-16) + Qa_(-1679/64) + La_(-9).
```

The eager event bill is `24 Qa_1 + 24 La_1 + 24 La_(-1)`. The deferred bill
retains `24 Qa_1 + 24 La_1` and adds I24. Thus, after establishing matched
prices for the common events, a saving would require

```
I24 + Omega_deferred - Omega_eager < 24 La_(-1),
```

where the Omega terms include any remaining caller, routing, precision,
storage, dispatch or controller overhead not already included in the event
prices. These terms and the physical event prices are unknown, not zero.
In particular, the large middle weight and the query on b must be priced;
a backend exposing only a cannot treat that read as free. This is a local
coefficient/restoration result and a complete symbolic event inventory,
not a priced supplier, an asymptotic improvement or a selected-frontier change.
