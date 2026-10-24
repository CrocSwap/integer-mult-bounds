# The coordinate-frame puncture has exact COPY cost 71

This is a scoped proof with exhaustive finite binary lemmas. All row-shift
parameters are arbitrary complex numbers. Zero terms are allowed. The theorem
concerns this fixed normal family and this fixed puncture only.

## Model and exact row solutions

Take the 120 unoriented E8 root lines represented by
`e_i +/- e_j` and half-sign vectors with an even number of minus signs.
Choose the representative whose first nonzero entry is positive. Remove

```text
e0 +/- e1, e2 +/- e3, e4 +/- e5, e6 +/- e7.
```

These eight lines are an orthogonal frame. Write the remaining doubled roots
as `x_i=2r_i`, so `x_i.x_i=8`. The nine fixed reader normals are

```text
b_k = e_k - (1/8)1, k=0,...,7;       a=(1/2)1.
```

These are the canonical A7+A1 normals of Adam Gall's
[PR2062](https://github.com/CrocSwap/integer-mult-bounds/pull/2062), which
binds them to joaqcoo's [PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224).
That source identification is cited predecessor work, not a replay claim.

Put `T_ik=<r_i,b_k>` and `T_i8=<r_i,a>`. The all-pairs identity is
`D T^transpose = 2G`, with `G_ij=<r_i,r_j>` and ordinary transpose. The live
roots span eight-space. Since the only normal dependency is `sum b_k=0`,
the complete row solution is

```text
D_ik = x_ik + t_i, k<8;       D_i8 = sum_k x_ik / 4;       t_i in C.
```

For completeness, subtracting the mean of `x_i` in the eight `b_k` terms
and adding the displayed A1 term gives exactly `x_i=2r_i`. Conversely,
equality against every live root forces that vector equation. Its kernel
is exactly the stated one-dimensional dependency. The remaining D8 roots
alone span eight-space: for each coordinate, choose a coordinate in another
pair and add/subtract the two retained signed roots.

Define the binary pairing `B_ij=(G_ij+1) mod 2`. For actual nonzero row and
reader supports `X_k,Y_k`, the separate-term bill is

```text
COPY(D) = sum_(k=0)^8 rank_F2 B[X_k,Y_k].
```

No simultaneous or shared physical-copy discount is included.

## New finite lemmas after puncturing

The standalone checker rebuilds the punctured geometry. Its pairing has
rank nine. Choose a basis of its row space and let `l_i in F2^9` be its
evaluation column at root i. All nine reader supports span the label space;
the fixed A1 row support also spans it. Thus the A1 term costs nine.

Because B is symmetric of rank nine, it has a factorization
`B=L Omega L^transpose`, where the rows of L are the labels and Omega is
invertible. A reader support of full label rank makes
`rank B[X,Y] = dim span{l_i:i in X}`. This justifies using label ranks for
each term. The attaining witness is additionally priced by literal pairing
submatrices, independently of this shortcut.

For a character w write `s(w)={i:w.l_i=1}`. For k=1,...,7 let

```text
C_k = {i:x_i0 != x_ik},
F_k(z) = span{l_i:i in C_k intersect s(z)},
H_k(U) = {z:s(z) intersect C_k intersect union_(u in U)s(u) is empty}.
```

H_k(U) is a binary annihilator space. If `U=<u,v>`, the union of character
supports is `s(u) union s(v)`. The checker enumerates every binary plane
exactly once using `0<u<v<u xor v`, and verifies:

1. On all 43,435 planes U, `dim H_1(U)<=2`, and `dim H_k(U)<=1` for k=2,...,7.
2. Among all 511 nonzero z, `rank F_1(z)` has histogram
   `{0:1,7:508,8:2}`.
3. For each k=2,...,7 the corresponding histogram is
   `{1:1,7:254,8:255,9:1}`. The unique rank-one case is exactly the span of
   `q_k=l_(e0-e_k)`.
4. The six labels q_2,...,q_7 are independent.

The plane enumeration performs 304,045 comparisons between two descriptions
of H: intersection of complete character compatibility masks, and direct
binary elimination of the forbidden labels. It finds 254 planes with
`dim H_1(U)=2`. Therefore the old P120 dimension-one premise cannot simply
be transferred to this puncture. The seven reverse-rank histograms enumerate
all nonzero characters, not sampled coefficients or subspaces.

Coordinate pair rotations and swaps within a pair preserve the puncture,
the normal family, and the binary pairing. They act transitively on the eight
mutable columns. The checker verifies generating symmetries. Consequently
any chosen mutable column may be the anchor called zero, with its paired
coordinate called one.

## Uniform deficiency bound

For each mutable term let K_k be the characters annihilating its actual row
support and put `delta_k=dim K_k`. The total bill is

```text
COPY(D) = 81 - sum_(k=0)^7 delta_k.
```

If `u in K_0` and `z in K_k`, a root in both character supports forces
`D_i0=D_ik=0`, hence `x_i0=x_ik`. Thus `K_k subset H_k(U)` whenever
`U subset K_0`, and `K_0 subset F_k(z)^perp` for every `z in K_k`.
These implications use exact zero equalities and hold over C without any
finite restriction on the t_i.

If every delta is at most one, their sum is at most eight. Otherwise use the
puncture symmetry to choose an anchor with `delta_0>=2`, and choose a plane
in K_0. Lemma 1 bounds `delta_1<=2` and every other delta by one.
If `delta_0=2`, the sum is at most `2+2+6=10`.

Suppose instead `delta_0>=3`. For every nonzero `z in K_k`, containment in
`F_k(z)^perp` implies `rank F_k(z)<=6`. Lemma 2 permits only one nonzero
character in K_1, so `delta_1<=1`. For k>=2, Lemma 3 permits only the unique
rank-one exception. Let J be the set of such k with K_k nonzero. Each has
delta one and forces K_0 to annihilate q_k. Lemma 4 gives |J| independent
conditions, so

```text
delta_0 <= 9-|J|,
sum delta_k <= (9-|J|) + 1 + |J| = 10.
```

This exhausts all cases. Therefore every complex-shift decoder in this
family has `COPY(D)>=71`.

## Attainment and consequence

Set `t_i=-x_i0` on every live line. The actual support-pair ranks are

```text
(0,8,9,9,9,9,9,9,9),      total 71.
```

The checker verifies all 12,544 all-pairs equations and prices all nine
support submatrices. Thus 71 is the exact minimum, with zero terms allowed.
This theorem does not determine the optimum with every term active.

The result answers this specified-puncture branch of PR2062's first open
question. It also excludes beating the ordinary P112 separate COPY bill
64 through these normals and this puncture. It is an algebraic obstruction
for the declared billing model. No physical supplier, full recursive moment,
new kappa, or complete multiplication theorem follows.
