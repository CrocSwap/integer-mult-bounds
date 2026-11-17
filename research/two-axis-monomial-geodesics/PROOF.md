# Exact two-axis record distances

## Model and statement

An address is x=(x0,x1) in F2^2, ordered by x0+2x1. Retain the
affine-quadratic monomial normal form of Cao Yifan / intqwq #4610:

```text
U |x> = i^(a+c0*x0+c1*x1+2*q*x0*x1) |A*x+b>,
A in GL(2,F2), b in F2^2, a,c0,c1 in Z/4, q in F2.
```

Each of the following eight directed records has cost one:

```text
C01: x1 <- x1+x0        C10: x0 <- x0+x1
X0:  x0 <- x0+1         X1:  x1 <- x1+1
S0:  multiply by i^x0   S1:  multiply by i^x1
CZ:  multiply by (-1)^(x0*x1)
omega: multiply by i.
```

Every exponent uses the current address. Words below are chronological,
with the leftmost record executed first. In particular S_j^-1 and
omega^-1 each require three unit records; they are not additional
cost-one generators. All absolute phases are retained.

**Finite certificate theorem.** This directed Cayley graph has 3,072
vertices and diameter eight. Its numbers of vertices at distances zero
through eight from identity are

```text
1, 8, 42, 162, 467, 884, 940, 475, 93.
```

The n=2 extremizer of unpaidmoon #7286 has exact distance six, attained by

```text
C01, X1, C10, S1, omega, omega.
```

This answers its first open question negatively at the requested first
example: sixteen is the length of that elimination, not a lower bound on
all recipes. The claims of shortestness and diameter use the exhaustive
certificate checks below. They are not a proof-kernel formalization.

## Complete and unique inventory

There are six binary invertible two-by-two matrices, because their rows
are distinct members of {01,10,11}. There are four translations and
4*4*4*2=128 phase choices, giving 6*4*128=3,072 normal forms.
They are distinct as literal monomials. The four output addresses
recover b and both columns of A. If p(x) is the phase exponent, then

```text
a = p(0),  c0 = p(e0)-p(0),  c1 = p(e1)-p(0),
2q = p(e0+e1)-p(e0)-p(e1)+p(0) modulo 4.
```

Thus these evaluations recover every phase parameter too. The independent
checker enumerates exactly this Cartesian product and checks 3,072 distinct
literal actions. Its closed-form polynomial gate updates are checked on
all four addresses of every normal form for every one of the eight gates.
This accounts for all 24,576 labeled edges, including loops or repeated
endpoints if any occur; no assumed group presentation substitutes for an
edge check. The enumeration and edge closure bind the computational domain
to the stated group. The primary search reaches every member.

For example, an affine bit y=b+u*x0+v*x1 over F2 has the Z/4 polynomial

```text
y = b+(1-2b)*(u*x0+v*x1-2*u*v*x0*x1).
```

This gives the S updates. For CZ, expand 2*y0*y1 using arithmetic in F2
inside the product, and reduce x_j^2 to x_j. CNOT and X only change A,b.
These formulas are implemented independently of the primary basis-action
updates. Gate matrices are also stored literally in the independent check.

## The distance certificate

Code each monomial as eight decimal digits: its four output addresses
followed by its four exponents, in the above address order. A certificate
assigns an integer d(v) between zero and eight to every code. The checker
verifies all of the following:

1. The inventory equals the complete normal-form inventory.
2. Identity has label zero, and it is the only zero label.
3. Every labeled edge u -> v satisfies d(v) <= d(u)+1.
4. Every nonidentity v has an incoming edge u -> v with d(u)=d(v)-1.

For any length-L word from identity to v, condition 3 telescopes to
d(v)<=L. Condition 4 repeatedly decreases a nonnegative integer until
the unique zero vertex is reached. Reversing these incoming edges gives
a word of length d(v). Hence d(v) is the exact directed distance. The
maximum label is therefore the diameter.
Right multiplication preserves every left-generator edge, so the maximum
distance from identity is also the maximum over all ordered vertex pairs.

The primary program builds the labels by literal-action breadth-first
search and replays an attaining shortest word for every vertex. The
independent program can consume the exported table, or generate its own
labels by eight bounded normal-form layers before checking the conditions.
Both report the same SHA256 of the sorted complete table. The proof uses
the edge and predecessor checks, rather than trusting the search algorithm
to establish optimality. Three modified certificates must fail, with their
specific rejection reasons checked.

## Explicit attaining words

The six-record word has output

```text
(x1+1, x0+x1+1)
```

over F2. Its exponent is

```text
2+(1-(x0 xor x1)) = 3-x0-x1+2*x0*x1 modulo 4.
```

Consequently it is precisely the #7286 witness with

```text
A = [[0,1],[1,1]], b=(1,1), a=c0=c1=3, q=1.
```

Its literal code is 31023223 and its certified distance is six. This
hand calculation establishes the claimed identity without running the
predecessor's elimination.

A diameter witness has code 02133322 and normal form

```text
U |x0,x1> = i^(3+3*x1) |x1,x0>.
```

It is attained by

```text
C01, C10, C01, X0, S0, X0, omega, omega.
```

The first three records swap the bits. The X0,S0,X0 block contributes
1-x1 to the phase and restores the output address. The final two records
add two. Its certified distance is eight. There are 93 distance-eight
elements in the complete census.

## Boundary of the conclusion

This is a one-column optimum in exactly the eight-record alphabet, with
absolute phase and unit record prices. If a physical API prices inverse
phases as one record, identifies global phases, permits extra axes or
dirty workspace, or adds other gates, this distance theorem does not
apply to that different optimization problem. Tensor-lifting the displayed
identities gives equal operators at every positive column count, but
shortestness at larger column counts is not claimed. For example scalar
phases can disappear under an even tensor power.

The retained physical movement, restoration and tape hypotheses still
govern implementation of the records. This package supplies no physical
caller, new kappa, uniform n-axis optimum or multiplication theorem.
