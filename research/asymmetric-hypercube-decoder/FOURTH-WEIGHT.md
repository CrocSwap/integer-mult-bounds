# The fourth generalized weight and all optimal four-target subcodes

**Exact scalar thresholds; no new κ.** For every `k>=2` and `q=p-k>=3`, this
note determines the fourth generalized Hamming weight of both signed
proper-star codes and classifies every attaining subcode:

```text
d_4(C^-_{p,k}) = d_4(C^+_{p,k}) = 8q+2.
```

Every optimum is the span of four minimum stars whose defining faces share a
signed `(k-2)`-face and add four signed coordinates from four distinct
original pairs. The exact number of optimal subcodes is

```text
2^(k+2) binom(p,k-2) binom(q+2,4).
```

Four selectable targets therefore require exactly `8q-2` deletions in the
scalar star-information model. Four prescribed targets attain that budget
precisely when one of these four-star evaluation matrices is invertible on
the target set. The final section makes this criterion and its decoding
construction explicit.

## Notation, inputs, and attribution

A port chooses one signed coordinate from each of k distinct original pairs
among p pairs. For a signed partial port L, the star `m_L` indicates
containment of L. The binary code `C^+_{p,k}` spans the stars with
`0<=|L|<k`; `C^-_{p,k}` omits the empty star. For a binary code C, `d_r(C)`
is the minimum support union of an r-dimensional subcode. All dimensions and
linear combinations are over `F_2`.

We prove lower bounds in `C^+` and construct witnesses in `C^-`, so the
results hold for both. Put `d=2q+2` and `s=4q+2`. We use these previously
proved results:

- [MINIMUM-WORDS.md](MINIMUM-WORDS.md) gives minimum distance d and the
  classification of minimum words as `(k-1)`-stars for `q>=2`.
- [EQUALITY-PAIR.md](EQUALITY-PAIR.md) gives `d_2=4q+3` and classifies
  optimal planes as spans of two adjacent minimum stars. Distinct
  minimum stars intersect in at most one port.
- [HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md) gives the complete spectral gap:
  every nonminimum nonzero word has weight at least s for `q>=3`.
  It also gives `d_3=6q+3` for `q>=3`; at `q=2`, it gives `d_3>=14`,
  improved to fifteen for a subcode containing a minimum word.
  Strict monotonicity consequently gives `d_4>=15` at `q=2`.
- [HIGHER-GRAPH.md](HIGHER-GRAPH.md) gives the complete `k=2` hierarchy
  and the retained-graph rank formula used in the boundary proofs.

The generalized-cube and even-face parity arguments originate in Luke
Mansoor's [PR
#732](https://github.com/CrocSwap/integer-mult-bounds/pull/732), inspected
at `80431a74c31e807581f5c2258c87abe2084caacd`; the earlier notes record the
other credited inputs. A generalized cube has k slots, each containing two
distinct signed coordinates, and original pair indices used by different
slots are disjoint. All its choices are therefore valid ports. Every proper
star has even parity on this cube. A binary function whose every face fixing
at most t signs has even parity is either zero or has weight at least
`2^(t+1)`. If t reaches the number of sign variables, singleton faces force
the function to vanish. Ordinary cubes partition the port set, so every
codeword has even weight.

Avoiding an original pair restricts the code to `C^+_{p-1,k}` and decreases
q by one. A pair is *universal* for a word or subcode when every port in its
support uses that pair. Its *degree* in a support union is the number of
those ports using it. Label each port by the vector of basis evaluations of
a subcode; vector parity means parity in every component.

Every binary r-dimensional subcode has sum of nonzero word weights `2^(r-1)`
times its union size. If a subcode of dimension r has support A, an affine
coset of it has total weight

```text
2^(r-1)|A| + 2^r wt(the common restriction outside A).
```

These averaging identities will also be used for restriction images.

## The attaining construction

Fix a signed face K of size `k-2`, and four signed coordinates `a,b,c,e`
from distinct original pairs outside K. The four stars defined by `K+a`,
`K+b`, `K+c`, and `K+e` have support union

```text
4(2q+2) - binom(4,2) = 8q+2.
```

Each pair meets in one distinct port, and no three meet. There are `q+2>=5`
residual original pairs; an unused pair supplies a private port for each
generator. The four rows are therefore independent and belong to `C^-`. This
proves the upper bound.

## Preliminary lemmas

### Signed-face shortening

For any word w, the signed derivative at an original pair i is

    Delta_i w(R) = w(R union {i+}) + w(R union {i-}).

It lies in C-plus_(p-1,k-1): monomials avoiding i cancel, and monomials
containing one sign of i lose that coordinate and have degree at most k-2.
If every port in the support of w contains one fixed signed coordinate i+,
its minus slice is zero, so its plus slice equals this derivative. Iteration
shows that shortening to a fixed signed face of size c is exactly the lifted
code C-plus_(p-c,k-c). Inclusion one way follows from derivatives, and
multiplication by the fixed face gives the converse.

### Small residual blocks with a common original core

The [small common-core proof](HIGHER-WEIGHTS.md#small-common-core-lemma)
uses residual sign-sum functions H_r and collapsed block functions F_r. We
need two immediate extensions. If q>=3 and V has a universal original core K
of size k-1, with each residual-pair block of its union of size at most
seven, then

    |supp(V)| >= 2(q+1) dim V.

Indeed the sign-sum H_r in that proof has each scalar component of weight at
most seven, below 2^(q+1). Hence the two residual signs have equal vector
labels. Every block has even size, so is actually at most six, and the cited
common-core lemma applies.

For q=3 we also use a weaker statement with blocks at most ten: their
sign-sum still vanishes, since ten<16. Thus all blocks, and their total
union, have even size; identical labels across different blocks are not
asserted at this larger size.

### Shortening to the fifteen-port q=2 triangle

Consider the union of three minimum stars having a common signed (k-2)-core
and three signed residual coordinates from distinct pairs, at q=2. Its size
is fifteen. The full C-plus code shortened to this union has dimension
exactly three.

By signed-face shortening, reduce to the k=2 code on four original pairs,
whose graph has eight vertices and omits the four matched edges. The
triangle union is all edges incident to the three selected vertices. Every
C-plus row is c plus a graph cut (vertex potential sum). To vanish outside
the union, its restriction to the graph induced by the other five vertices
is zero. That graph is connected and has a triangle. The triangle forces
c=0; connectivity forces all five unselected vertex potentials equal. Modulo
the global constant potential, only the three selected potentials remain.
This proves the asserted shortening dimension.

## Universal pair-kernel exclusions

Suppose V has dimension four and union U of size n<=8q+1. For each original
pair r, let L_r be the kernel of restriction to ports avoiding r. Its
support uses r; its image avoids r, so their supports are disjoint.

A two-dimensional kernel would give

    n >= d_2(q)+d_2(q-1) = (4q+3)+(4q-1) = 8q+2.

A three-dimensional kernel would give

    n >= d_3(q)+d_1(q-1) = (6q+3)+2q = 8q+3.

A one-dimensional kernel generated by a nonminimum word has weight at least
4q+2. For q=3 its three-dimensional image has support at least 14, giving
n>=28>25. For q>=4 its image has support at least 6q-3, giving
n>=10q-1>8q+1. Therefore every pair restriction has kernel zero, the span of
a minimum star, or all V.

At most three minimum words lie in V: any four would have union at least
4d-6=8q+2, by pair intersections at most one. If a pair is universal for two
minimum words, its kernel has dimension at least two and hence is all V. In
particular it is universal for every minimum word in V.

## Base q=3, by induction on k

At k=2 the complete graph-code hierarchy gives d_4=26. Assume the result for
smaller k when needed below. Suppose n<=25. Minimum words have weight 8 and
other words at least 14. If V had at most one minimum word, its fifteen
nonzero weights would sum to at least 8+14*14=204>8*25. Thus V has either
two or three minimum words.

### Exactly two minimum words

Call them f,g. Their weights contribute 16, and the other thirteen words
contribute at least 182. Hence n>=ceil(198/8)=25, so n=25. Exactly one word
v has weight 16 and the other twelve nonminimum words have weight 14.

We first prove v=f+g and determine the column multiplicities. Choose a basis
of V, identifying coefficient vectors with F_2^4, and write m_a for the
number of columns with a nonzero evaluation label a. For a nonzero a,
Fourier inversion of the word weights gives

    8m_a = 14 + 6(-1)^(f.a) + 6(-1)^(g.a) - 2(-1)^(v.a).

Integrality forces the three signs on the right to have product +1: after
dividing by two and reducing modulo four, their sum must be 3 modulo 4. Thus
(-1)^(v.a)=(-1)^((f+g).a) for every a, proving v=f+g. In particular, f and g
have disjoint supports A_f,A_g, each of size 8.

Use f,g as the first two basis vectors. The same formula gives m_a=3 when
(a_f,a_g)=(0,0), m_a=2 when exactly one of these bits is 1, and m_a=0 when
both are 1. (The zero label is excluded.) Thus the remaining set B=U without
(A_f union A_g) has size 9. On either eight-point minimum-star support, each
of the four possible remaining two-bit labels appears exactly twice.
Consequently any word of V restricts to that support with weight zero, four,
or eight.

Let K_f,K_g be the original-pair cores of the two stars.

If K_f=K_g, those k-1 pairs are universal for all V by the kernel
exclusions. Every outside pair has injective avoidance restriction, whose
four-dimensional q=2 image has support at least 15. Its degree in U is
therefore at most 10. The weaker common-core sign-pairing observation makes
n even, contradicting n=25.

Otherwise put c=|K_f intersect K_g| and u=k-1-c>=1. A pair a in K_f without
K_g has degree at least 8+2=10 in U. Its kernel is <f>, and its
three-dimensional q=2 image contains the restriction of g, a minimum word of
weight 6, so has support at least 15. Thus its degree is exactly 10, all
accounted for by f and g. The set B avoids a. The same argument applies to
every pair in the symmetric difference of the two cores.

The c common pairs are universal for V. Hence each B-port must use u+1
further pairs while avoiding the 2u pairs in the core symmetric difference.
There are only 4-u available pairs outside both cores. Since B is nonempty,

    u+1 <= 4-u,

which forces u=1. Write the common original-pair core as K, of size k-2, and
the two differing pairs as a,b. The signed faces defining f,g therefore have
the form K(signs 1)+a and K(signs 2)+b. Their supports are disjoint, so some
i in K has opposite prescribed signs in the two faces.

Apply Delta_i to V. Pair i is universal for all V, so its image union has
size at most 25. We claim Delta_i is injective. If w lies in its kernel, its
values on each two-port i-sign fiber agree. For a port of A_f, the
opposite-i port cannot lie in A_f. It cannot lie in B either, because B
avoids pair a. It can lie in A_g at at most one port: the f-port must extend
by g's prescribed signed b-coordinate, and all the other core signs must
agree. Thus w restricts to A_f with weight at most one. The column-label
calculation above forces that restriction to be zero. Similarly it is zero
on A_g. A nonzero such w would therefore be supported on B of size 9; it is
neither minimum word f nor g, contrary to the gap 14.

The derivative is consequently a four-dimensional subcode of
C-plus_(p-1,k-1), still at q=3, with support at most 25. This contradicts
the induction on k. (This subcase automatically has k>=3 because i exists.)

### Exactly three minimum words

Let their original-pair cores have common intersection K of size c. No pair
can occur in exactly two of the three cores, by the kernel exclusions. Thus
each core consists of K plus a disjoint set of u=k-1-c private original
pairs, with all three private sets of the same size.

If u=0, all three stars have the same original-pair core and different
signed cores, so their supports are disjoint and have total size 24. All
outside-pair avoidance maps are injective, giving block degrees at most 10.
Sign-pairing makes n even. Since 24<=n<=25, n=24 and the union is exactly
the three stars. Every residual block then has size 6. The common-core lemma
would require n>=8*4=32, a contradiction.

Suppose u>=1 and choose a pair r private to the first star f. Its avoidance
image has dimension three and contains either other minimum star, so the q=2
conditional bound gives degree_r(U)<=n-15<=10. The first star supplies 8
ports using r; each other star supplies 2. Their mutual intersection cannot
use r, because r is in neither defining face. Each can overlap f in at most
one port. Hence the union degree is at least 10, with equality only when f
intersects both other stars. Repeating for private pairs of the other stars
shows all three are pairwise adjacent. This forces u=1, a common signed
(k-2)-core, and three distinct residual signed coordinates a,b,c. (The
alternative common-k-port configuration would have some original pair in
exactly two cores, already excluded.)

Their union A is the triangle of size 21, and each selected residual pair
has degree 10 in A. The preceding bound forces n=25 and no extra port in B=U
without A to use any of a,b,c. All U ports contain K's original pair
indices, so each of the four extra ports uses both of the other two residual
pairs d,e.

Avoiding d is injective: its kernel contains no minimum word, and all other
nonzero proper kernel types were excluded. The image has dimension four, but
is supported on the fifteen-port q=2 triangle A restricted away from d. That
shortening has dimension three by the preliminary lemma. This final
contradiction proves the q=3 base for every k.

## Induction step q>=4

Assume d_4(q-1)=8q-6 for every k>=2. An injective pair-avoidance map now
gives degree_r(U)<=n-(8q-6)<=7. A pair whose kernel is generated by a
minimum star has degree at most n-d_3(q-1)<=8q+1-(6q-3)=d+2. Let m be the
number of minimum words in V, between zero and three.

### m=0

Every pair is either universal for all V or has injective avoidance map. Let
c be the number of universal pairs and t=k-c. The fifteen nonzero weights
are each at least s, so n>=ceil(15s/8). Incidence counting gives

    t(n-7) <= 7q.

The lower bound on n implies 2(n-7)>7q, so t<=1. If t=0, all support lies in
one ordinary cube. Every nonzero word has weight at least 2^(q+1), or
singleton faces force it zero. Averaging gives n>=15*2^(q-2)>8q+1 for q>=4.
If t=1, all residual blocks have size at most 7. The extended common-core
lemma gives n>=4d=8q+8, also impossible.

### m=1

Let f be the unique minimum star, A its support, and B=U without A. The
restriction of V outside A has kernel <f>, hence dimension three. Each
nonzero outside word comes from a coset {h,h+f}, both nonminimum. The coset
sum identity gives

    2s <= 2 wt(h outside A)+d,

so every such image word has weight at least 3q+1. Summing its seven words,

    |B| >= ceil(7(3q+1)/4).

Let K be the c original pairs universal for all V, and t=k-c. They are among
the k-1 core pairs of f. Each of the other t-1 core pairs has kernel <f>,
and therefore degree at most 2 in B. Each of the q+1 pairs outside f's core
has injective avoidance, and has degree at most 7-2=5 in B. Counting the t
remaining pair incidences of every B-port gives

    t|B| <= 2(t-1)+5(q+1),
    t(|B|-2) <= 5q+3.

The lower bound on |B| forces t<=1, because 2(|B|-2)>5q+3. Thus t=1, all
f-core pairs are universal for V, and the residual blocks have size at most
7. The extended common-core lemma again gives n>=4d>8q+1.

### m=2

Let the minimum words be f,g, with supports meeting in e in {0,1} points.
Their union A has size 2d-e. Put B=U without A. The subcode <f,g> is the
full kernel of restriction outside A: any independent word supported there
would form a three-dimensional subcode supported on A, but
|A|<=4q+4<d_3(q)=6q+3 for q>=3. Thus the outside image has dimension two.
Each of its three nonzero words comes from four nonminimum words. The coset
identity gives its weight at least

    s-|A|/2 = 2q+e/2,

hence at least 2q+e. Their three weights sum to 2|B|, so

    |B| >= 3q+2e.

If the two original-pair cores coincide, they are universal for V and the
outside blocks have degree at most 7; common-core contradiction applies.
Otherwise let their intersection size be c=k-1-u, with u>=1. These c pairs
are universal for V. For each of the 2u core-symmetric-difference pairs, the
minimum-star kernel bound is d+2, while A already has d+2-e ports using it.
Its degree in B is at most e. For each of the q+1-u pairs outside both
cores, A has degree 4 and U has degree at most 7, so B has degree at most 3.
Every B-port has u+1 slots outside the common core. Therefore

    (u+1)|B| <= 2u e + 3(q+1-u).

If e=0, the left side is at least 6q while the right is at most 3q. If e=1,
the stars are adjacent, so u=1; the left side is at least 6q+4 while the
right is 3q+2. Both cases are impossible.

### m=3

As in the q=3 base, a pair belongs to zero, one, or all three minimum-star
cores. Write their common original core as K, and each private core size as
u. If u=0, common-core contradiction applies directly.

If u>=1, a pair private to one minimum star has union degree at most d+2,
while that star contributes d and the other two contribute 2 each. The
latter two cannot intersect on that pair. Thus equality forces the first
star to intersect each of the other two. Consequently all three stars are
pairwise adjacent, u=1, and they have a common signed (k-2)-core with three
distinct signed residual coordinates a,b,c. Their support A is the triangle
of size 3d-3=6q+3. The selected residual-pair degrees are exactly d+2, so
B=U without A uses none of a,b,c.

For every one of the q-1 other residual pairs, A has degree 6 while U has
degree at most 7. Hence B has degree at most 1 there. Every B-port uses two
of those pairs, giving 2|B| <= q-1.

On the other hand, the single coset of the three-dimensional triangle
subcode outside it contains eight nonminimum words, each of weight at least
s. Its total weight is 4|A|+8|B|, so

    |B| >= ceil(s-|A|/2) = q+1.

This is incompatible with the incidence bound. All four cases are excluded,
completing the induction and the fourth-weight proof.

## Equality: pair kernels at support N=8q+2

At support N=8q+2, a three-dimensional avoidance kernel is still impossible,
since d_3(q)+d_1(q-1)=8q+3. A one-dimensional nonminimum kernel is
impossible since its support plus the three-dimensional image has size at
least 28 when q=3, and at least (4q+2)+(6q-3)=10q-1>N when q>=4. Thus kernel
dimensions are 0,1,2,4, with a one-dimensional kernel generated by a minimum
star.

Suppose some pair r has a two-dimensional kernel L. The kernel and image
lower bounds sum exactly to N:

    d_2(q)+d_2(q-1)=(4q+3)+(4q-1)=N.

Therefore both are optimal planes and every occupied port using r lies in
supp(L). The two minimum stars in L contribute two minimum words of V. The
avoidance image has two distinct minimum words, each of weight 2q. For
either such image word, its four lifts form a coset of L. Their sum of
weights is 2(4q+3)+4(2q)=16q+6.

If all four lifts were nonminimum, the gap would give at least
4(4q+2)=16q+8. Hence each image minimum word has a minimum lift. These two
lifts are independent modulo L. Consequently V contains four independent
minimum stars.

## Equality for q>=4: excluding fewer than four minimum words

For the rest of this section assume q>=4 and that no pair has a
two-dimensional kernel. An injective avoidance map has union degree at most
N-d_4(q-1)=8. A minimum-star kernel gives degree at most N-d_3(q-1)=d+3.

A common original core of size k-1 with residual blocks at most 8 is again
rigid when q>=4. Sign sums have weight at most 8<2^(q+1), so signs pair;
collapsed blocks have at most 4 positions. Differences of two collapsed
blocks have weight at most 8<2^q, hence vanish by even-face parity. All
blocks are identical and support has size at least d*dim(V)=4d>N.

If there are no minimum words, the gap gives n=N>=ceil(15s/8), while the
incidence inequality for t nonuniversal slots is t(N-8)<=8q. It forces t<=1
for q>=4. The t=0 single-cube alternative is excluded by the same averaged
even-face lower bound as before; t=1 is excluded by the preceding
common-core rigidity.

If there is one minimum star, the outside support B still has size at least
ceil(7(3q+1)/4). The global-core incidence inequality becomes

    t(|B|-3) <= 6q+3,

because nonglobal core pairs have B-degree at most 3 and the q+1 outside
pairs at most 6. This forces t<=1, hence common-core rigidity excludes it.

If there are two minimum stars intersecting in e in {0,1}, the same coset
argument gives |B|>=3q+2e outside their union. Coincident original cores are
excluded by common-core rigidity. Otherwise use core difference u>=1. The
symmetric-difference pairs now have B-degree at most 1+e; the outside pairs
at most 4. Thus

    (u+1)|B| <= 2u(1+e)+4(q+1-u)
              = 4q+4+2u(e-1).

For e=0, the left is at least 6q and the right at most 4q+2. For e=1, u=1,
and the left is at least 6q+4 while the right is 4q+4. Both are impossible.

If there are three minimum stars, each original pair belongs to zero, one,
or all three defining cores. Let the common core have size c and private
core sizes u=k-1-c. If u=0, common-core rigidity excludes it. If u>=1, the
degree bound d+3 means each minimum star must intersect at least one other:
its private pair has union degree

    d+4-(number of its intersections with the other two stars).

An intersection forces u=1, because the private original-pair sets are
disjoint. Then every core has the same k-2 original pairs plus one distinct
private pair. Two stars intersect precisely when their common-core signs
agree. Thus their intersection graph is a disjoint union of cliques. A
three-vertex graph with no isolated vertex must be a triangle, so all three
stars share the same signed core.

Their union A has size 6q+3. The nontrivial coset of their span still forces
|B|>=q+1. Each of the three selected residual pairs has degree d+2 in A and
at most d+3 in V, giving B-degree at most 1. Each of the q-1 other residual
pairs has A-degree 6 and V-degree at most 8, giving B-degree at most 2.
Every B-port uses two residual pairs, so

    2|B| <= 3+2(q-1)=2q+1,

contradicting |B|>=q+1. This excludes all cases with at most three minima.

## Equality at q=3, by induction on k

It remains to exclude optimal subcodes with fewer than four minimum words at
q=3. We use induction on k.

### Base k=2

Here p=5 and the paired graph has ten vertices and forty edges. A subcode of
dimension four with support 26 leaves a retained graph H with 14 edges. The
graph-code rank calculation requires either at least five components, or a
bipartite graph with at least four components. The bipartite option has at
most floor(7^2/4)=12 edges, so is impossible. For p=5, a set of v vertices
induces at most `f(v)=binom(v,2)-max(0,v-5)` edges. The component
concentration bound in HIGHER-GRAPH.md shows that at least six components
would have at most f(5)=10 edges. With five components and two nonsingleton
components, it gives at most f(5)+f(2)=11 edges. Thus the components must
have sizes 6,1,1,1,1. The large component has fourteen edges, so is an
induced six-vertex paired graph with precisely one missing matched edge.
Consequently the four isolates lie in distinct original pairs. The full
shortening on the deleted edges has dimension four and is exactly their four
singleton-star span. This proves the base.

### Preliminary reductions at n=26

The dimension-two pair-kernel argument in the preceding equality section
also works at q=3: its optimal kernel and image supply four independent
minimum stars by the same four-lift weight average. Hence assume there is no
such pair kernel. Dimensions three and one-nonminimum remain excluded. Every
pair has kernel zero, one minimum-star span, or all V.

Injective avoidance has four-dimensional q=2 image of support at least 15,
so its degree is at most 11. A minimum-star kernel has three-dimensional q=2
image of support at least 14, hence degree at most 12. If another minimum
word survives that avoidance, the conditional bound 15 improves the degree
to at most 11.

At most four minimum words occur in V. Four already imply the desired
four-star geometry by the argument in the next section. No minima is
impossible because 15*14>8*26. Thus it suffices to exclude one, two, or
three minimum words.

### A common-core parity observation at support 26

Suppose all V has a universal original core of size k-1 and contains at
least one minimum star. Each residual block has size at most 11, since
outside-core avoidance is injective. Its sign sum vanishes by the q=3
even-face bound 16. Each block therefore has even size at most 10. Collapse
its residual sign pairs to a vector function F_r on core signs. The four
collapsed support sizes sum 13, so a smallest one has size at most 3 and all
others have size at most 5.

All blocks contain the core-sign point of the fixed minimum star. The union
of a smallest support and any other therefore has size at most 3+5-1=7. The
difference F_r+F_s has even parity on every face fixing at most two core
signs, and a nonzero scalar component would need weight 8. Thus each block
equals the smallest block. Their four sizes would sum to a multiple of four,
contrary to 13. This excludes such a common core.

### One minimum word

Call the minimum word f, of weight 8. The other fourteen words have weight
at least 14. Their total weight is 208, so the excess above 8+14*14=204 is
4. There are only two possible spectra: one word of weight 18 with the rest
14, or two words of weight 16 with the rest 14.

For any nonzero column label a, Fourier inversion in the first case gives

    8m_a=14+6(-1)^(f.a)-4(-1)^(v.a).

Whenever f.a=1, the numerator is 4 or 12, contradicting integrality. In the
second case, with weight 16 words v,w, inversion gives

    8m_a=14+6(-1)^(f.a)-2(-1)^(v.a)-2(-1)^(w.a).

For f.a=0, integrality forces the last two signs equal; for f.a=1, it forces
them opposite. Thus v+w=f. Moreover every one of the eight labels with f.a=1
occurs exactly once. The eight columns on A=supp(f) are therefore all the
points of one affine hyperplane in F_2^4 and span the full dual space. In
particular they are distinct, and a word vanishing on A is zero. The
remaining support B has size 18.

Let c be the number of global universal original pairs and t=k-c. Each of
the t-1 nonglobal core pairs of f has B-degree at most 12-8=4. Each of the
four pairs outside f's core has B-degree at most 11-2=9. Therefore

    18t <= 4(t-1)+4*9,    or    14t<=32.

Thus t is one or two. The common-core observation excludes t=1. If t=2, let
K be the global original core of size k-2, and write f's defining face as
one fixed signed K plus coordinate a. The pair a has degree at most 12, so
at most four B-ports use a. Its four ordinary cubes K+a+r each contain two
A-ports with distinct vector labels. Vector ordinary-cube parity requires at
least one B-port in each, so there is exactly one in each.

Those four B-ports have the same signed K as f. Indeed, for any i in K,
core-face parity in the corresponding block would fail if its lone B-port
had the other i-sign: the two A-labels have nonzero sum. To obtain this
face parity, replace the opposite choice in the i-slot by a coordinate
from an unused residual pair. The branch taking that coordinate omits the
universal core pair i and is zero, so generalized-cube parity gives the
claimed fixed-sign parity. Thus no opposite-i
mate of an A-port lies in U, for any i in K. If k=2 the base already
applies; otherwise choose such an i. A word in ker(Delta_i) must vanish on
A, hence is zero because A's columns span all four dimensions. The
derivative is injective.

Its four-dimensional image at the same q=3 and k-1 has support at most 26,
so the scalar theorem makes that support exactly 26. No occupied i-sign
fiber can then contain two ports, since collapsing two occupied ports would
strictly reduce union size. Therefore all word weights are preserved. The
induction hypothesis gives four minimum words in the image, contrary to the
single minimum word in V.

### Two minimum words

Call them f,g, with intersection size e in {0,1}. Their union A has size
16-e and B=U without A has size 10+e. The outside-A image has dimension two,
since d_3(q=3)=21>|A| excludes a larger kernel than <f,g>. Every nonzero
image word comes from four nonminimum words. The coset identity gives its
weight at least 14-|A|/2=6+e/2,

hence at least 6+e. The three image weights sum 2|B|=20+2e, so each is at
most 8. This upper bound is important for the derivative argument.

Coincident original-pair cores are excluded by the common-core observation.
Otherwise let their intersection have size c=k-1-u, u>=1. A symmetric-
difference core pair has a minimum-star kernel and its image contains the
other restricted minimum star, so its union degree is at most 11. It has
A-degree 10-e, hence B-degree at most 1+e. A pair outside both cores has
A-degree 4 and union degree at most 11, hence B-degree at most 7. Thus

    (u+1)(10+e) <= 2u(1+e)+7(4-u).

For e=0 this forces u<=1. For e=1 adjacency already gives u=1. In either
case there is a common original core K of size k-2 and distinct private
pairs a,b.

If e=1, the signed K agrees for both stars. Choose any i in K. For a word in
ker(Delta_i), every nonzero A-position must have an opposite-i mate in B.
Such a mate uses a or b. There are at most two B-ports using each of those
pairs, so the word's restriction to A has weight at most 4.

If e=0, the two prescribed sign patterns on K differ. Choose a conflicting
i. An A_f position can have an opposite-i mate in A_g in at most one case,
namely f's extension by g's prescribed b-coordinate. It can have a mate in B
at at most one position, since B-degree_a<=1. Hence a derivative- kernel
word has weight at most 2 on A_f, and similarly at most 2 on A_g. Again its
restriction to A has weight at most 4.

In either case a kernel word with nonzero outside-A projection has total
weight at most 4+8=12, contradicting the nonminimum gap 14. The derivatives
of f,g are distinct minimum stars, so their span contains no derivative-
kernel word either. Delta_i is injective. As before, scalar d_4 forces
support 26 in the image, all occupied fibers are singletons, and all word
weights are preserved. The induction hypothesis's four minimum words
contradict the presence of only two here. If K is empty, k=2 and the base
already supplies the contradiction.

### Three minimum words

By the pair-kernel exclusions, original pairs occur in zero, one, or all
three defining cores. Let their common core have size c and each private set
have size u=k-1-c. The u=0 case is excluded by the common-core observation.

For u>=1, a private pair has union degree at most 11 because its avoidance
image contains another restricted minimum word. Its degree in the union of
the three stars is 12 minus the number of intersections of its own star with
the other two. Thus every star intersects at least one other. As in the
preceding q>=4 classification, this forces u=1, and the intersection graph
is a union of cliques indexed by the signed common core. With three vertices
and no isolates it must be a triangle.

The triangle's signed core K has size k-2 and its union A has size 21. There
are only five points in B=U without A. If k>=3, choose any i in K. All
A-points have the same i-sign, so any nonzero two-sign fiber of a word in
ker(Delta_i) must use at least one B-point. Its total weight is therefore at
most 2|B|=10. A nonzero such word cannot be one of the three minimum stars,
whose derivatives are nonzero, and cannot be nonminimum by the gap 14. Thus
Delta_i is injective. The same support and weight preservation argument
contradicts the induction hypothesis's four minimum words. The k=2 case was
handled by the graph base.

All cases with fewer than four minimum stars are excluded. This completes
the equality argument at q=3.

## Four-star geometry and the count

There cannot be five minimum stars: their union would have size at least
5d-10=10q>N for q>=3. Thus every optimal subcode has exactly four minimum
stars, and they are independent. Indeed any sum of two is nonzero; three are
independent by prior rigidity; a sum of three cannot be a fourth minimum
word since its weight is at least 3d-6=6q>d.

The union of four stars has size at least 4d-6=N. Equality in this two-term
inclusion-exclusion bound forces all six pair intersections to be single
ports and no port to lie in three or more stars. Any first three therefore
form a triangle with common signed core K of size k-2. A fourth face
adjacent to all three must contain K: if it omitted one coordinate of K,
adjacency to the first two would force their two private coordinates,
leaving intersection too small with the third face. Thus it is K plus a
fourth signed coordinate, from a fourth original pair by compatibility. This
proves the asserted geometric classification.

The four generators are the only minimum words: their pair, triple, and
quadruple sums have weights 4q+2,6q,8q-4 respectively, all larger than d.
The subcode therefore uniquely recovers its signed core and its unordered
four residual signed coordinates. Counting these choices gives
2^(k-2)*binom(p,k-2)*16*binom(q+2,4), as asserted, for every q>=3.

## Prescribed four targets and explicit decoders

Let `T={T_1,T_2,T_3,T_4}` be four distinct prescribed ports. Choose a signed
`(k-2)`-face K and four residual signed coordinates `a_1,...,a_4` from four
distinct original pairs. Define the binary matrix

```text
E_ij = 1[K union {a_i} is contained in T_j].
```

Exactly `8q-2` deletions suffice for T **if and only if** some such E is
invertible. This is a finite geometric criterion, with no assertion that
every prescribed quadruple satisfies it.

For sufficiency, take the four star rows f and their support union W. If E
is invertible, every target lies in W. Replace the column of rows f by
`E^(-1) f`; their restriction to T is the identity matrix. Delete `D=W \ T`.
The four transformed rows are simultaneous unit decoders, and `|D|=8q-2`.

Conversely, four unit decoders supported on `D union T` are independent.
Their span has support at least `d_4=8q+2`. If `|D|=8q-2`, it is an optimal
subcode and hence one of the four-star spans classified above. Its
restriction to T has rank four, so the associated E is invertible. If no
such E exists, the deletion budget is at least `8q-1`; this note does not
determine the exact larger budget in that case.

For selectable targets, private ports from an unused residual pair give an
identity evaluation matrix immediately. Thus `d_4-4=8q-2` is attained. At
power-of-two k the original overlap-class corrections lie in the nonempty
proper-star span, so these statements apply to that corrected scalar decoder
as well. Acquiring the required star totals, synthesizing a complete paid
supplier, and improving κ are separate obligations; none is asserted here.

Prepared by Sam Sung with substantial OpenAI Codex assistance; Apache-2.0.
