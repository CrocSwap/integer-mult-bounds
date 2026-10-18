# A mixed-edge P112 simplex obstruction

## Statement

Use the pinned 112 E8 root-line representatives `r_t`, binary labels
`ell(t)` and characteristic-zero field `K`. Define

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

There are no twelve independent pieces spanning `T` with
`dim(T intersect C) >= 8` and respective weight upper bounds

```
4,5,5,6,6,6,6,6,6,6,6,6.
```

This excludes one actual profile in PR3154's TWOSIDE `(b,t)=(8,4)` residue.
It is not a full cell closure, C5, `C(P112)>=64`, a supplier or a kappa result.
The new ingredient is a finite mixed-edge simplex lemma at support cutoff 72.
The predecessor root-only lemma requires support below 70 and cannot be used
at this cutoff.

## Retained geometry

The pinned [root-simplex proof](vendor/ROOT-SIMPLEX-PROOF.md) gives the following
facts, with its exact finite quantities replayed here:

- Weight bounds `4,5,6` give support bounds `8,12,20`.
- The code has dimension eight and minimum support 53.
- On all 120 E8 root lines, a subspace of dimension at most six contains at
  most 36 root lines.
- Seven-node chamber faces have `42,28,22,14,16,23,37,63` root lines.
  The face with 63 lines has a root normal. The face with 42 has a D7 normal.
- If independent scalar root directions have scalar-root pair differences,
  they have one common scale and oriented norm-two roots with pairwise
  inner product one.

The last statement follows from the A2 classification of root planes.
The replay checks all 7,140 root-line pairs and all 960 simple reflections.
It also enumerates all 4,097,782 binary five-/six-flat kernels for the support
capacities. The general perpendicular-root classification uses the standard
Weyl-chamber theorem. These finite tests do not formalize that theorem.

## Complete alphabet at support 72

A codeword supported on at most 72 live lines has at least 40 perpendicular
live root lines. Their rational span has rank at least seven, by the
36-line bound. Its rank is at most seven because the direction is nonzero.
Its rational perpendicular kernel is therefore one-dimensional. This also
works over `K`: the direction is a `K`-scalar multiple of a rational vector.

For a real generator of that rational line, move into a closed Weyl chamber.
At least seven simple roots vanish. Of the eight seven-node faces, only the
42-line D7 face and the 63-line E7 face can contain 40 perpendicular roots.
Thus the direction is a root or a Weyl transform of the D7 chamber normal.

The executable doubles roots, so their squared norm is eight. Sums and
differences of perpendicular doubled roots give 1,080 projective norm-four
lines, of squared norm 16 in these coordinates. This inventory contains the
D7 chamber normal and is closed under every simple reflection. It therefore
contains its full Weyl orbit. Direct evaluation on the fixed P112 puncture
has the following exact distribution:

| Live support | Number of projective non-root directions |
|---|---:|
| 70 | 128 |
| 73 | 896 |
| 76 | 56 |

Consequently all directions of support at most 72 lie in the 248-line alphabet
consisting of 120 root lines and 128 D7-normal lines. Every listed line really
has support at most 72.

In primitive coordinates the 128 extra lines have one nonzero entry, equal
to `+1` or `-1`, in each pair `(0,1),(2,3),(4,5),(6,7)`, up to common sign.
They form one orbit under symmetries preserving the actual puncture. Swap
within each pair to move its nonzero entry to the even position. Change signs
to make those four entries positive. If this requires an odd number of sign
changes, also change one unused zero position. The resulting even signed
permutation preserves E8 and the deleted orthogonal frame, and maps the line
to

```
a = (1,0,1,0,1,0,1,0).
```

The replay checks all 128 such transformations against every root and frame
line. No unrestricted change of puncture is used in the mixed branch.

## Finite mixed-edge simplex lemma

Consider nine affinely independent vertices in `K^8`, every pair difference
having live support at most 72. Suppose at least one edge is not a root
direction. Translate one endpoint to zero, apply the frame-preserving symmetry
above and divide by one common nonzero scalar. The other endpoint becomes `a`.
Translation and common scaling preserve equality multiplicities at every
coordinate.

Each of the seven other vertices `x` lies on an allowed projective line `u`,
and `a-x` lies on an allowed line `v`. The lines are distinct, since affine
independence excludes vertices collinear with `0,a`. Thus

```
a = s*u + t*v,    x=s*u,    s,t nonzero.
```

For each of the `binom(248,2)=30,628` pairs, solve this equation by one nonzero
rational two-by-two minor and check all eight coordinates. Its unique solution
is rational even if originally solved over `K`. Both endpoint choices give
exactly 58 possible further vertices. Every coordinate is half-integral.
The graph joins two candidates exactly when their difference belongs to the
248-line alphabet. It has 595 edges.

Every mixed simplex gives an increasing seven-clique of that graph. Conversely,
any seven-clique spanning rank eight together with `a` is an eligible simplex.
Complete enumeration gives:

| Rational rank together with `a` | Seven-cliques |
|---|---:|
| 5 | 840 |
| 6 | 5,040 |
| 7 | 4,032 |
| 8 | 608 |

For nine coordinate values `v_0,...,v_8`, an arbitrary common shift leaves at
least

```
9 - max_z #{i : v_i=z}
```

nonzero values. Only one equality class can become zero; choosing the largest
class attains the bound. Compute these 112 nonnegative costs for each of the
608 independent configurations. Removing at most 32 arbitrary live coordinates
can delete at most its 32 largest costs. The resulting sums have this exact
histogram:

| Surviving support sum | Configurations |
|---|---:|
| 182 | 112 |
| 184 | 16 |
| 190 | 112 |
| 191 | 128 |
| 194 | 128 |
| 199 | 112 |

Hence the mixed branch requires at least 182 nonzero endpoint incidences outside
any 32 deleted live lines, even allowing an arbitrary coordinate-dependent
common shift. `RESULT.json` gives an eight-dimensional witness attaining 182
in this relaxed model. Its live cost spectrum is `1:1,2:56,3:24,5:31`; delete
the 31 costs of five and one cost of three. The remaining sum is
`1+56*2+23*3=182`. One additional arbitrary cut lowers this witness to 179,
so the 32-line budget is substantive. This witness is not a realization of
the small-piece supports in the application.

The separately written check uses Gram-system intersections instead of a
coordinate minor, a three-clique/four-clique join instead of the primary
bounded stack, integer row elimination instead of rational elimination, and
explicit equality counts instead of a frequency map. It reproduces all 10,520
cliques, 608 full-rank cases and the support histogram. The two programs share
the pinned E8 reconstruction and written classification premises.

## All-root branch

If every edge is a root direction, the retained root-plane argument identifies
the nine vertices with an affine root A8 simplex, up to a common scalar.
Complete ordered-star coverage proceeds by extending each prefix by every
root with the required inner products, and taking all orbits under reflections
perpendicular to the prefix. This subgroup fixes the prefix pointwise. Taking
all its orbits suffices even if it is smaller than the full stabilizer.

The orbit sizes through prefix ranks zero to six are
`240;56;27;16;10;6;(2,1)`. The two rank-seven branches have respectively one
and zero extensions. Thus rank eight has one retained representative. Its
120-line minimum-nonzero spectrum is `2:36,3:84`.

Relax the eight deleted frame lines and at most 32 small-support lines to any
40 root coordinates. The 80 smallest remaining costs sum to

```
36*2 + 44*3 = 204.
```

This lower bound is sufficient; no claim of sharpness for the fixed frame is
needed. It applies over `K` because nonzero common scaling changes no equality
class.

## Apply the lemma to the actual twelve-piece profile

Take the three small pieces of weights `4,5,5`. Their support union `S` has
size at most `8+12+12=32`. Let the other nine pieces be `q_0,...,q_8`, each
supported on at most 20 lines. Write `D=T intersect C` and `lambda:T -> T/D`.
The quotient dimension is at most four.

The three small pieces and any one `q_i` have support union at most
`32+20=52<53`. Their quotient images are independent. Otherwise their nonzero
combination would be a codeword supported on fewer than 53 lines, since the
original pieces are independent. Hence the quotient dimension is exactly four.
Modulo the small images, every `q_i` has a nonzero image in a one-dimensional
quotient. Rescale them to the same image and subtract suitable small-piece
combinations `s_i` to obtain

```
c_0=0,    c_i=q_i-q_0-s_i in D,    i=1,...,8.
```

The `c_i` are independent by their distinct coefficients on `q_1,...,q_8`.
The map `h -> c_h` is injective, so these give nine affinely independent
vertices in `K^8`. Every edge is supported on at most `32+20+20=72` lines.
Outside `S` the nine endpoint values differ from these vertex evaluations by
one common shift. Thus their total support outside `S` is at least 182 in
the mixed case, or 204 in the all-root case. But all nine endpoints together
have support sum at most `9*20=180`. Both cases contradict that allowance.
This proves the stated profile exclusion, with margin at least two.

## Original residue, overlap and limits

The unmodified pinned `bk2b.py` reprints all 24 original cell counts. A separate
transcription reproduces the 251 `(8,4)` survivors and includes this profile.
The original decoder reduction remains an inherited dependency.

The only four-piece quotient-basis weight multiset certified by capacities
alone is `4,5,5,6`, of support cap 52. Packing these into two six-flats with
paid cuts requires at least 20 cuts by those weight capacities. No remaining
piece is a rank-four anchor. Thus the earlier eight-/ten-cut and twelve-cut
rank-four-anchor bounds do not certify this profile by that weight-only route.
The root-only predecessors also cannot assume edges below 70 here. These are
applicability checks, not a lower bound on actual support-overlap savings or a
claim that every other possible argument has been excluded.

The proof is author-checked with two local finite algorithms, not independent
human review or proof-kernel verification. The Weyl-chamber theorem and retained
root-plane argument are explicit mathematical dependencies. No full C5 census,
physical implementation, complete multiplication theorem or selected-frontier
change is claimed.
