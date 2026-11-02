# Exact characteristic-two Desargues parameters

Work over a field K of characteristic two. An **exact** labelled Desargues
configuration has ten distinct projective points and ten distinct lines, with
exactly the thirty designated incidences. Extra point-line incidences are
forbidden. This is the frame-universal interface of Sagar Thakrar's
[PR2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274), not a
definition of every Desargues configuration used in the literature.

## The normalized interface

The labels are O, A0, A1, A2, B0, B1, B2, C01, C02, C12. The designated
lines are the three O Ai Bi lines, the three Ai Aj Cij lines, the three
Bi Bj Cij lines, and the C01 C02 C12 axis.

In an exact configuration, O, A0, A1, A2 form a projective frame. Indeed,
any collinear triple among them would put an additional point on one of
the designated lines. There is a unique projectivity taking this ordered
frame to e1, e2, e3, (1,1,1). After applying it, write

```
O  = (1,0,0)       A0 = (0,1,0)
A1 = (0,0,1)       A2 = (1,1,1)
B0 = (u,1,0)       B1 = (v,0,1)       B2 = (1+w,1,1).
```

These forms for Bi follow from collinearity with O and Ai and from Bi != O.
Distinctness from Ai forces u,v,w nonzero. The remaining points and all line
covectors, up to nonzero projective rescaling, are forced as follows.

| Point | Coordinates | Line | Covector |
| --- | --- | --- | --- |
| C01 | (0,v,u) | O A0 B0 | (0,0,1) |
| C02 | (u,u+w,u) | O A1 B1 | (0,1,0) |
| C12 | (v,v,v+w) | O A2 B2 | (0,1,1) |
| | | A0 A1 C01 | (1,0,0) |
| | | A0 A2 C02 | (1,0,1) |
| | | A1 A2 C12 | (1,1,0) |
| | | B0 B1 C01 | (1,u,v) |
| | | B0 B2 C02 | (1,u,1+u+w) |
| | | B1 B2 C12 | (1,1+v+w,v) |
| | | axis | (u+v+w,u,v) |

Taking cross products gives these formulas. The axis covector annihilates
all three Cij and is nonzero when u and v are nonzero. Thus these formulas
also construct the whole candidate from any parameters u,v,w.

## The criterion

**Theorem.** The normalized candidate is exact if and only if 1,u,v,w are
linearly independent over F2.

Define the fourteen nonconstant affine forms

```
u, v, w,
a=1+u, b=1+v, c=1+w,
d=u+v, e=u+w, f=v+w,
g=1+u+v, h=1+u+w, i=1+v+w,
j=u+v+w, k=1+u+v+w.
```

Here is the complete point-line dot-product table. The columns follow the
line order in the preceding table. Juxtaposition denotes multiplication.

| | O0 | O1 | O2 | A01 | A02 | A12 | B01 | B02 | B12 | axis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | j |
| A0 | 0 | 1 | 1 | 0 | 0 | 1 | u | u | i | u |
| A1 | 1 | 0 | 1 | 0 | 1 | 0 | v | h | v | v |
| A2 | 1 | 1 | 0 | 1 | 0 | 0 | g | w | w | w |
| B0 | 0 | 1 | 1 | u | u | a | 0 | 0 | k | uk |
| B1 | 1 | 0 | 1 | v | b | v | 0 | k | 0 | vk |
| B2 | 1 | 1 | 0 | c | w | w | k | 0 | 0 | wk |
| C01 | u | v | d | 0 | u | v | 0 | uk | vk | 0 |
| C02 | u | e | w | u | 0 | w | uk | 0 | wk | 0 |
| C12 | f | v | w | v | w | 0 | vk | wk | 0 | 0 |

The thirty zero entries are precisely the designated incidences. Every
other entry is 1, one of the fourteen forms, or a product of two of them.
Every form occurs by itself. Consequently all seventy required
nonincidences hold exactly when all fourteen forms are nonzero. This says
exactly that no nonzero binary combination of 1,u,v,w vanishes, since the
remaining combination is the constant 1.

Under this condition every point and line is nonzero. Their incidence
rows and columns are distinct, so no two points or two lines can be
projectively equal. Thus the condition is sufficient for exactness as well
as necessary. The unique projective-frame normalization proves the same
criterion for every exact labelled realization after normalization. QED.

## Count, field threshold and direct construction

For K=Fq, q=2^h, the number of normalized labelled candidates is

```
N(q) = (q-2)(q-4)(q-8).
```

Choose u outside span{1}, v outside span{1,u}, and w outside span{1,u,v}.
These spans have respectively 2,4,8 elements. If h<4, no such four
independent elements exist and the displayed product is zero. Otherwise
the three successive choices count each normalized labelled candidate
once. These are not counts of unlabelled configurations.

Over any characteristic-two field, exactness is possible if and only if
its binary vector-space dimension is at least four. Extend 1 to four
independent elements and use the displayed coordinates. In a supplied
binary basis beginning with 1, the next three basis elements directly
give u,v,w. No search over projective points or incidence assignments is
needed. An element alpha of degree at least four supplies the alternative
choice u=alpha, v=alpha^2, w=alpha^3.

In particular, F32 admits the interface despite having no subfield F16.
The field threshold concerns binary dimension, not containment of a
particular smallest witness field. The verifier checks all 32^3 triples
over F32 and independently constructs one degree-four witness.

## Scope and prior work

Theorem statements above concern the exact normalized incidence interface.
They do not prove a decoder-cost bound, a physical native implementation,
or a new multiplication theorem. The finite checks corroborate the written
proof; they are not its universal quantifier.

The simplex-section interpretation is classical. Bruen, Bruen and
McQuillan, [arXiv:2007.09175](https://arxiv.org/abs/2007.09175), Theorem 3.2,
give that correspondence. Their general nondegenerate configurations may
have extra incidences, discussed in Theorem 4.3 and Section 10. Their
reference 14 points to earlier strict characteristic-two/three enumeration
by Puystjens and Thas. No literature-wide embedding or enumeration priority
is claimed here. The contribution is the explicit normalized parameter
criterion, direct construction, and complete polynomial certificate
answering the repository's open interface question.
