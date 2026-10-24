# The exceptional mixed Pappus frame has no characteristic-two realization

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Statement and exact contract

Use Sagar Thakrar's exceptional identity frame from
[#2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274), with
`a=(0,1,-1), b=(0,-15,15)`. The nine integer point rows P and nine integer
line rows L are reproduced in `verify.py`, in the orders

```text
A0 A1 A2 B0 B1 B2 C0 C1 C2
l  m  pap A0B1 A0B2 A1B0 A1B2 A2B0 A2B1
```

A frame-universal realization over a field K consists of nonzero vectors
X_i,Y_j in K^3 such that

1. supp X_i is contained in supp P_i, and supp Y_j in supp L_j;
2. X_i dot Y_j = 0 if and only if P_i dot L_j = 0 over the integers.

Coordinates inside an allowed support may vanish. No injectivity or
nondegeneracy is silently added to this definition.

**Theorem.** This frame admits a frame-universal realization over K if and
only if char K is different from two. In particular no finite extension
of F2, nor any infinite field of characteristic two, can repair the
predecessor's finite certificate-search failure.

The obstruction is to one shared assignment for the entire frame. It
does not exclude an instance-specific CR2 assignment for a list of pairs.
It proves no pairing-cost bound or failure of the decoder conjecture.

## The geometric normalization is valid even with smaller supports

Interpret X_i as a projective point and Y_j as a line covector. The exact
incidence requirement distinguishes every two named points and every two
named lines: their incidence signatures in the displayed Pappus pattern
are different. Thus none can coincide projectively in a realization.

The support zeros force A0, B0 and C0 onto the coordinate line x=0. They
also force l, m and pap through O=(1,0,0), because the first coordinate of
each of their covectors is zero. O is outside x=0. The incidences are
A0 on l, B0 on m and C0 on pap. The three points are distinct, as are the
three lines. These conclusions do not require any additional coordinate
to remain nonzero.

Choose representatives of A0 and B0 as a basis of the plane x=0. The
coordinates of C0 in that basis are both nonzero, since C0 differs from
both. Rescale the basis vectors so C0 is their sum, and append a
representative of O to obtain an invertible basis of K^3. The resulting
projective change of coordinates gives

```text
O  = (1,0,0)   A0 = (0,0,1)   B0  = (0,1,0)   C0 = (0,1,1)
l  = (0,1,0)   m  = (0,0,1)   pap = (0,1,-1).
```

This change need not preserve all original supports. They have already
supplied the two geometric constraints used by the remainder of the proof.
Incidences and nonincidences are invariant under the dual point/line maps.

## The forced pairing

A1 and A2 lie on l and not on m. Normalize their third coordinates to one:

```text
A1=(a,0,1),    A2=(c,0,1).
```

They differ from A0, so a and c are nonzero. B2 lies on m and not on l;
normalize it to B2=(d,1,0). It differs from B0, so d is nonzero.
The joins of these distinct points give the actual line covectors

```text
A0B2=(1,-d,0),    A2B0=(1,0,-c),    A1B2=(1,-d,-a).
```

C1 lies on pap and not on l, so it has a representative (u,1,1).
Its incidence with A0B2 gives u=d. Its incidence with A2B0 then gives

```text
d-c=0.                                             (1)
```

C0=(0,1,1) lies on A1B2, giving

```text
-(a+d)=0.                                          (2)
```

But A1 does not lie on A2B0 in the required pattern. Its required nonzero
pairing is

```text
N = a-c = 2a + (-(a+d)) + (d-c) = 2a.              (3)
```

In characteristic two this is zero, a contradiction. Equation (3) is an
integer polynomial identity; the proof uses only field arithmetic and
nonzero normalizations justified above. It therefore covers all fields
of characteristic two, not just a finite tested list.

## The characteristic hypothesis is sharp

The following integer vectors fit inside the original supports:

```text
A0=(0,0,1)   A1=(1,0,1)   A2=(-1,0,1)
B0=(0,1,0)   B1=(1,1,0)   B2=(-1,1,0)
C0=(0,1,1)   C1=(-1,1,1)  C2=(1,1,1)

l=(0,1,0)       m=(0,0,1)       pap=(0,1,-1)
A0B1=(1,-1,0)   A0B2=(1,1,0)    A1B0=(1,0,-1)
A1B2=(1,1,-1)   A2B0=(1,0,1)    A2B1=(1,-1,1).
```

Their 81 integer pairings have exactly the required zero pattern. Each
nonzero pairing is in {-2,-1,1,2}. Consequently they remain an exact
frame-universal realization over every field of characteristic different
from two. The verifier checks every pairing and support inclusion.

## A single support-zero relaxation escapes the obstruction

For a boundary control, allow the first coordinate of pap alone to be
nonzero. The fixed GF4 witness `RELAXED_POINTS, RELAXED_LINES` in `verify.py`
satisfies every required incidence and nonincidence and every other
original support zero. GF4 is F2[w]/(w^2+w+1), encoded as 0,1,2=w,3=w+1.
Its pap is (1,1,3), so its three named lines need not concur at O.
The original support checker rejects it and the one-coordinate-relaxed
checker accepts it. This is a new explicit control, not an imported
predecessor search or a claim about arbitrary coordinate frames.

Dropping the required nonincidence in (3) also removes the contradiction:
the normalized two-equation core has a=c=d=1 over F2. This is a control
for that core only, not a realization of the complete Pappus pattern.

## Evidence and remaining obligations

The universal argument above is a written proof. The standalone checker
corroborates its integer identity, literal normalized core over seven
finite fields, the all-odd integer witness, the single-zero GF4 control,
and mutations of its support, incidence and nonzero-vector contracts.
It does not rerun #2274's field searches or pairing minima.

No formal proof-kernel or independent human review is claimed. Lemma CR2
is context, not a theorem premise of this obstruction. Nothing here
settles the 70 larger pairing-cost instances left open by #2274, supplies
a physical decoder, changes the selected supplier or improves kappa.
