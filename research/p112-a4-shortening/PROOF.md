# Five-vertex shortening after deleting two pieces

Let K have characteristic zero. Let P be the 112 nonframe E8 root lines
in the declared data, with doubled representatives r_t of norm squared
eight. Write

```
C = {c_h : c_h(t) = <r_t,h>, h in K^8}.
```

## Support26 shortening theorem

Suppose `a_1,...,a_k,q_0,...,q_4` are collectively independent vectors in
`K^112`. Let S be the union of the a_j supports. If `|S|<=26` and each q_i
has support at most twenty, their span T satisfies

```
dim(T intersect C) <= 3.
```

This is a five-endpoint statement. The recent support29/support30 theorems
use six endpoints and bound the intersection by four. They do not directly
supply this conclusion after two pieces are deleted.

## Retained geometric premises

The unchanged geometry source reconstructs the roots, puncture and binary
labels from simple-root coordinates modulo two, with a leading one. The
replay binds their ordered bytes to the declared data and checks:

* The live Gram sum is `112 I`, so evaluation is injective.
* Every nonzero codeword has support at least 53. A codeword with support
  strictly below seventy is a scalar multiple of a root codeword.
* A rational plane through two different root lines has either those two
  lines or three A2 lines. The third line's coefficients have ratio `+1`
  or `-1` in norm-two root coordinates.
* A binary label space of dimension five or six contains at most twelve
  or twenty live coordinates, respectively. Dimension at most four gives
  at most eight from the leading-one coordinate.

For completeness, the classification uses the standard Weyl-chamber
theorem. In a closed chamber, the 28 six-node faces contain at most 36
root lines. The eight seven-node faces contain
`42,28,22,14,16,23,37,63` lines. Only the 63-line E7 face can supply the at
least 43 perpendicular live lines required by support below seventy.
Its normal is a root. Root directions have live supports 53 or 56, which
also proves distance 53. All 960 simple reflections and all 7,140 root
planes are checked.

This applies over K, not only over the reals. Perpendicular rational roots
have rational rank at most seven. Rank at most six would let a generic
real normal to their span contradict the 36-line bound. Thus the rational
kernel is one-dimensional and the K-valued direction is proportional to
its rational generator. Apply the real Weyl argument to that generator.
The standard Weyl-chamber theorem is a written mathematical dependency,
not a statement formalized by this package.

## Normalize five quotient images

Assume `D=T intersect C` has dimension at least four. Then `T/D` has
dimension at most `k+1`. The images of all k small pieces and any one q_i
are independent: a nonzero relation would give a nonzero codeword supported
on at most `26+20=46<53` coordinates. Collective independence excludes the
zero vector as an alternative. Hence `dim(T/D)=k+1` and `dim D=4`.

Modulo the small images, the five q_i have nonzero images in a single
dimension. Rescale them to agree there. This changes neither support nor
independence. With suitable combinations s_i of the a_j, set

```
c_0=0,   c_i=q_i-q_0-s_i in D, i=1,...,4.
```

The c_i are independent, by their distinct unit coefficients on the q_i.
Injectivity gives independent direction vectors h_i, with h_0=0. Every
edge has support at most `26+20+20=66<70`, so every edge is a root direction.

The A2 plane fact forces a common scale on these root directions. More
explicitly, write `h_i=b_i alpha_i` with norm-two rational roots alpha_i.
A nonsingular rational two-by-two minor shows that the rational third
root line in the K-span of two alpha_i is already in their rational span.
Its coefficient ratio forces `b_i/b_j=+1` or `-1`. Absorb signs into the
alpha_i. All h_i then equal `b alpha_i` for one nonzero b. Since their
differences are roots after this normalization, distinct alpha_i have
inner product one. The vertices `0,alpha_1,...,alpha_4` form an A4 simplex.

## Complete A4 coverage and its cost

The replay partitions extensions of an ordered star by reflections in
roots perpendicular to every earlier vertex. These reflections fix the
prefix pointwise. The generated subgroup need not be the full stabilizer:
retaining one representative of every subgroup orbit cannot omit a full
stabilizer orbit. Induction therefore covers every ordered star.

The four extension inventories each form one orbit, of sizes
`240,56,27,16`. Thus every A4 star has the same full 120-line spectrum.
For each coordinate evaluate the five vertices and charge

```
k(v) = 5 - max_z #{i : v_i=z}.
```

This is exactly the smallest possible number of nonzero endpoint values
after a common coordinate shift. Common nonzero K-scaling preserves all
equalities. The complete spectrum is

```
cost 0: 10 lines
cost 1: 50 lines
cost 2: 60 lines
sum:    170
```

A separate explicit star `0,e0+e1,...,e0+e4`, an independently generated
root inventory, literal shift minimization and a 0/1 deletion dynamic
program reproduce this spectrum and all reported support bounds. The
orbit proof supplies completeness; the explicit fixture alone would not.

Outside S, the five q_i values equal the five vertex values plus a common
shift. Relax the actual orthogonal puncture to any eight root lines, and
relax S to any 26 more coordinates. Each removed coordinate saves at most
two incidences. The five endpoints therefore require at least

```
170 - 2*(8+26) = 102 > 5*20 = 100
```

support incidences. This contradiction proves the theorem. For support
caps twenty and twenty-four the lower bounds are 114 and 106. At twenty-
seven the relaxed bound is exactly 100, so this proof stops there. That
boundary is not a counterexample or a sharpness claim for the theorem.

## Two actual historical profiles

Consider nine independent pieces spanning T, with
`dim(T intersect C)>=6`. Delete any two basis pieces and let T' be the
span of the other seven. The projection onto the two deleted coefficients
has rank at most two on `T intersect C`. Its kernel is `T' intersect C`,
so that intersection has dimension at least four. This is deletion of
pieces, not deletion of evaluation coordinates.

For each profile below, delete its two weight-seven pieces. Piece weight
means the binary rank of the labels of its support. The retained capacity
checks then give:

| Original profile | Retained pieces | Small pieces | Common support cap | Five endpoint allowance | Required support |
|---|---|---|---:|---:|---:|
| `3,6^6,7^2` | `3,6^6` | `3,6` | 24 | 100 | 106 |
| `4,5,6^5,7^2` | `4,5,6^5` | `4,5` | 20 | 100 | 114 |

The respective quotient-basis support caps are 44 and 40, below 53. Edge
support caps are 64 and 60, below seventy. The shortening theorem
contradicts the four surviving code dimensions in both cases. In fact,
the deleted pieces may have arbitrary weights and supports.

Both profiles belong to the original seventeen TWOSIDE `(b,t)=(6,3)`
survivors. Their excesses are 35, strictly below 36. An independent filter
transcription and the exact retained predecessor program agree on the
seventeen-member count. All weight-certified original three-piece bases
need at least four or eight paid cuts, respectively, when packed into two
six-flats. Thus the earlier two-cut R7 result does not directly settle
these rows by that weight-only cover. The fourteen-cut rank-six result
cannot simply treat the original nonbasis weight-seven pieces as rank six.
These comparisons do not exclude useful actual support overlaps or claim
a complete survey of all implications of earlier work.

## Limits

This establishes two named profile exclusions and the general five-endpoint
support26 contract. It does not close all C5 cells, the complete P112
decoder floor or the other conjectures of DreamingOfClouds/PR3154. No
physical supplier, complete multiplication theorem or improved kappa is
claimed. The selected frontier and frozen inputs remain unchanged.
