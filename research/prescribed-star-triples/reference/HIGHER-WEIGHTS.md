# The third generalized weight and a five-weight boundary prefix

**Exact higher-target thresholds; no new κ.** This note determines the
third generalized Hamming weight of both signed proper-star codes for every
`k>=2` and `q=p-k>=2`. At `q=2`, it also determines the first five weights
for every `k>=4`. For `q>=3` it also determines the exact gap above minimum
weight and classifies every optimal three-dimensional subcode.
These are scalar linear-information statements; the
attaining subcodes are explicit, but no paid supplier or complete
multiplication construction is asserted.

## Results and scope

Use the signed-port model and notation of [MINIMUM-WORDS.md](MINIMUM-WORDS.md).
A port chooses one signed coordinate from each of k different original
pairs among p pairs. The star `m_L` indicates containment of the signed
partial port L. The binary code `C^+_{p,k}` spans the stars of degrees
`0<=|L|<k`; `C^-_{p,k}` omits the empty star. For either code C, `d_r(C)` is
the smallest union support of an r-dimensional subcode.

For all `k>=2` and `q>=2`,

```text
d_3(C^-_{k+q,k}) = d_3(C^+_{k+q,k}) =
    15,       q=2 and k in {2,3},
    14,       q=2 and k>=4,
    6q+3,     q>=3.
```

For every `k>=4` at `q=2`, the first five generalized weights of both codes
are exactly

```text
(d_1,d_2,d_3,d_4,d_5) = (6,11,14,15,16).
```

At power-of-two k, the original overlap-class corrections lie in the
nonempty proper-star code. The usual information-set argument therefore
turns `d_r-r` into the minimum number of deletions for **some selectable
set of r retained targets**. Thus three selectable targets need exactly
`6q` deletions for `q>=3`. At `q=2,k>=4`, three, four, and five selectable
targets each need exactly eleven deletions. The exact budget for a
prescribed larger target set can be different.
For `q>=3`, we additionally classify every optimal three-dimensional
subcode and give an exact criterion for a prescribed triple to attain
`6q` deletions. The [pair classification](EQUALITY-PAIR.md) gives the
separate exact result for every prescribed pair.

## Inputs and attribution

We use the minimum distance `d_1=2q+2`, minimum-word rigidity for `q>=2`,
`d_2=4q+3`, and the classification of optimal two-dimensional subcodes as
spans of adjacent `(k-1)`-stars. Their proofs and credited inputs are in
[MINIMUM-WORDS.md](MINIMUM-WORDS.md) and [EQUALITY-PAIR.md](EQUALITY-PAIR.md).
In particular, two distinct minimum stars meet in at most one port; three
distinct minimum stars are independent, since the sum of two has weight
at least `4q+2>2q+2`.

Luke Mansoor's [PR #732](https://github.com/CrocSwap/integer-mult-bounds/pull/732),
inspected at `80431a74c31e807581f5c2258c87abe2084caacd`, supplies the uniform
minimum-distance and generalized-cube arguments. We use its even-face
consequence: a binary function whose every face fixing at most t signs has
even parity is either zero or has weight at least `2^(t+1)`. If t reaches
the number of sign variables, singleton faces force the function to vanish.
Generalized cubes have k slots, each containing two distinct coordinates.
The original pair indices used by different slots must be disjoint, so
all `2^k` choices are valid ports. Every proper star has even parity on
such a cube. Ordinary cubes partition the ports, so all codeword weights
are even.

The [complete k=2 hierarchy](HIGHER-GRAPH.md) supplies the graph-code boundary
used below. The formulas here extend beyond that graph case and beyond
the all-target rank calculation of
[PR #772](https://github.com/CrocSwap/integer-mult-bounds/pull/772), inspected
at `02b59e553649c333072b5dd4dfb97e43942efa14`.

In lower bounds we work in the larger code `C^+`. All attaining constructions
belong to `C^-`, so equality follows for both spaces. Avoiding an original
pair restricts a codeword to `C^+_{p-1,k}`, replacing q by `q-1`. A pair is
*universal* for a word or subcode if every port in its support uses that
pair. Its *degree* in a support union is the number of ports using it.

## Two boundary lemmas at q=2

First, every three-dimensional subcode has support at least fourteen.
Its seven planes each have support at least eleven. Every occupied
coordinate belongs to the support of six of these planes, so 6n>=77,
hence n>=13. If n=13, the seven plane supports sum to 78, forcing six
planes of support eleven and one of support twelve. Each optimal plane
contains exactly two minimum words. A word lies in three planes, so there
are at least four distinct minimum words. Any three distinct minimum stars
are independent: the sum of two has weight at least ten, not six. Their
support union is at least 3*6-3=15 because pairwise intersections have size
at most one. This contradicts n=13.

Second, a three-dimensional subcode containing a minimum word has support
at least fifteen. Suppose n<=14 and fix its minimum word f, of support A
and weight six. There cannot be three minimum words, by the preceding
three-star observation, so there are at most two. Restrict the subcode
outside A. Its kernel is exactly <f>, since a nonzero word supported on A
must equal f. The image is two-dimensional; its three nonzero supports
are the supports outside A of the three planes through f. A plane with
support eleven must contain two minimum words. Thus at most one of the
three planes has support eleven, and the other two have support at least
twelve. Their outside-A support sizes are therefore at least 5,6,6. But
the three nonzero words of a binary two-dimensional code have total weight
twice their union size. Consequently 2(n-6)>=17, impossible for n<=14.

In particular, every three-dimensional support-fourteen subcode at q=2
has no minimum word. All seven of its nonzero words then have weight eight,
since their weights sum to 4*14=56.

## Small common-core lemma

Suppose q>=3, a subcode V is supported on ports containing a fixed set K
of k-1 original pair indices, and every residual-pair block of its support
union has at most six ports. Then the union has size at least

    2(q+1) dim V.

Choose a basis and label each port by its vector of basis evaluations.
For a residual pair r and signs a on K, denote the two vector labels by
F_r^+(a), F_r^-(a). Their sum H_r(a) has even parity on every face fixing
at most q signs of K: replace each fixed core slot by that sign versus a
coordinate from a distinct other residual pair, keep r ordinary, and
apply generalized-cube parity. Every branch using a replacement omits a
universal core pair and vanishes. Each scalar component of H_r has weight
at most six. The even-face lemma would force a nonzero component to have
weight at least 2^(q+1)>6, or rules it out directly by singleton faces.
Thus F_r^+=F_r^-=F_r. Its vector-valued support has at most three points.

For residual pairs r,s, the vector function F_r+F_s has even parity on
every face fixing at most q-1 core signs. Use a mixed slot with one chosen
coordinate from r and one from s, and replace the fixed core slots using
distinct residual pairs other than r,s. There are q-1 available pairs.
Its scalar components have weight at most six, whereas the even-face
bound is 2^q>=8. Hence F_r=F_s. All q+1 residual blocks have the same
vector labels on the same core-sign positions, each repeated twice.
If there are m such positions, the whole evaluation matrix has at most
m distinct nonzero column labels. Therefore dim V<=m and its support
union has size 2(q+1)m, proving the lemma.

## The complete gap above minimum weight for q>=3

For every `q>=3`, the second smallest nonzero weight in either code is
exactly `4q+2`: no word has weight strictly between `2q+2` and `4q+2`.
The sum of two adjacent minimum stars has weight `4q+2`, so it suffices
to prove the exclusion in `C^+`.

### A small nonminimum word cannot restrict to a minimum star

Suppose a nonminimum word w has weight `b<4q+2`, and avoiding an original
pair r gives a minimum word. At `q-1>=2`, minimum-word rigidity makes this
restriction a star `m_J` of weight `2q`. Let F be the same star in the full
p-pair space. It has weight `2q+2` and exactly two extensions using r.
The word `h=w+F` vanishes away from r. Write t for the number of those two
extensions also in w. Then

```text
wt(h) = b-2q+2-2t <= 2q+2,
```

because evenness gives `b<=4q`. The word h is nonzero, since w is not the
minimum word F. Minimum distance forces equality throughout: `b=4q`,
`t=0`, and h is another minimum star. But F and h then share both
r-extensions of F. Distinct minimum stars meet in at most one port, a
contradiction. Therefore every nonzero avoidance restriction of w is
nonminimum.

### Induction on q

At `q=3`, the only weights to exclude are ten and twelve. The preceding
observation makes every nonzero avoidance restriction a nonminimum word
at `q=2`, hence of weight at least eight. If c pairs are universal for w
and `t=k-c`, each of the remaining `t+3` pairs has degree at most `b-8`.
Counting incidences gives

```text
t b <= (t+3)(b-8),    hence    8t <= 3(b-8).
```

For `b=10` this forces `t=0`; for `b=12` it forces `t<=1`. A word with
`t=0` lies in one ordinary cube and has weight at least sixteen by the
even-face bound, or is zero when singleton faces apply. If `t=1`, all
residual blocks have size at most four. The common-core lemma's proof
shows more than its stated bound: all residual signs are paired and all
four residual blocks have identical labels. The total weight is therefore
a multiple of eight, which cannot be twelve. This proves the q=3 case.

For `q>=4`, assume the asserted gap at `q-1`. A hypothetical nonminimum
word with `b<4q+2` has `b>=2q+4`. Every nonzero avoidance restriction is
nonminimum and therefore has weight at least `4q-2` by induction. Every
nonuniversal pair consequently has degree at most

```text
b-(4q-2) <= 2.
```

Again let t count the nonuniversal slots of a support port. Incidence
counting gives `t b<=2(t+q)`, or `t(b-2)<=2q`. Since `b-2>=2q+2`, this
forces `t=0`. The support lies in one ordinary cube; the even-face bound
then gives `b>=2^(q+1)>4q`, or singleton faces force it to vanish. Both
contradict the assumed weight. This completes the induction and proves
the exact second nonzero weight for both codes.

## Third-weight equality and its complete classification for q>=3

Let V have dimension three and union support size `n<=6q+3`. Its seven
nonzero words have total weight `4n`, because each occupied coordinate
appears in exactly four words. If at most two words were minimum, the
spectral gap would give

```text
4n >= 2(2q+2) + 5(4q+2) = 24q+14 > 4(6q+3),
```

an impossibility. Hence V contains at least three distinct minimum stars.
These are independent. Each has size `d=2q+2`, and pairwise intersections
have size at most one, so their union has size at least `3d-3=6q+3`.
This proves `d_3>=6q+3`.

At equality, the three pairwise intersections must be distinct singleton
ports and the triple intersection must be empty. To identify the possible
faces, let `J_1,J_2,J_3` be their signed `(k-1)`-faces. Pairwise adjacency
means any two differ by replacing one coordinate, with compatible signs.
Write `J_1=K+a` and `J_2=K+b`, where `|K|=k-2`. If `J_3` contains K, then
it is `K+c` for a third signed coordinate c, and a,b,c lie in distinct
original pairs. If `J_3` omits a coordinate i of K, adjacency to both
`J_1,J_2` forces

```text
J_3 = (K without i) union {a,b}.
```

In the latter case all three faces lie in the same k-port `K union {a,b}`,
so their three stars have a common support point, contrary to equality.
Thus every optimal subcode is exactly the span of

```text
m_(K+a), m_(K+b), m_(K+c),
```

for a signed `(k-2)`-core K and three signed coordinates from distinct
outside original pairs. Conversely these three stars have union `6q+3`,
so every such triangle is optimal.

The three pairwise sums have weight `4q+2`, and their triple sum has weight
`6q`; both exceed `2q+2` for `q>=3`. Thus the triangle's three generators
are its only minimum words. They uniquely recover K and the unordered
three signed coordinates. The exact number of optimal three-dimensional
subcodes is consequently

```text
2^(k+1) binom(p,k-2) binom(q+2,3).
```

### Which prescribed triples attain the minimum deletion budget?

For `q>=3`, under proper-star observations, three distinct prescribed
targets `T_1,T_2,T_3` attain the minimum `6q` deletions if and only if some
triangle above has an invertible
three-by-three evaluation matrix

```text
A_ij = 1[K union {a_i} is contained in T_j],
(a_1,a_2,a_3) = (a,b,c),
```

over `F_2`. At power-of-two k it also applies to the original overlap-class
model. This is a finite structural criterion, not an assertion that
all triples attain the same budget. It is enough to enumerate signed
`(k-2)`-subsets K of `T_1 intersect T_2 intersect T_3`, and three residual
signed coordinates from different original pairs: invertibility forces
each target to lie in the triangle support, hence to contain K.

For sufficiency, multiply the three star rows by `A^(-1)` so that their
restrictions to the prescribed targets are unit rows. Delete the other
`6q` support ports. For necessity, three unit decoders after exactly `6q`
deletions span a subcode with support at most `6q+3`. It must be optimal,
hence a triangle by the classification, and its target columns must be
independent. A triple failing the criterion requires at least `6q+1`
deletions. No exact larger budget for such a triple is claimed here.

## The exceptional boundary k=3, q=2

The three-star triangle gives the upper bound 15. Suppose a three-dimensional
subcode V of C-plus has union support 14. The preceding q=2 lemmas show that
all seven nonzero words have weight eight. We prove a contradiction.

### A common original pair

For an original pair i, let s_i be the dimension of the subcode of V
supported entirely on ports using i. Dimension two is impossible: that
kernel needs at least d_2(C^+_{5,3})=11 ports, while its nonzero avoidance
image needs at least d_1(C^+_{4,3})=4 disjoint ports. Thus s_i is 0, 1, or 3.

More generally, at q=2 a weight-eight word has at least k-2 universal original
pairs. Indeed every nonuniversal pair occurs at most four times, since its
avoidance leaves a nonzero word of weight at least four. If c(w) is the
universal-pair count, 8k<=8c(w)+4(p-c(w)) gives c(w)>=k-2.

Let c be the number of pairs universal for the whole V, equivalently s_i=3.
Double-count universal incidences across the seven nonzero words. Each of
these c pairs contributes seven incidences and each remaining pair at most
one, so

    7(k-2) <= 7c+(p-c) = 6c+k+2.

Since c is integral, c>=k-2. For k=3 there is a common original pair i.
All codewords vanish on ports avoiding i.

### The two sign slices

There are four residual original pairs. Let C be their k=2 code with the
empty star allowed. It has dimension eight, minimum distance six, and
third generalized weight fifteen, by [HIGHER-GRAPH.md](HIGHER-GRAPH.md). Let B be the
six-dimensional space of functions constant on each unsigned residual
pair block (each block consists of its four sign choices), and set

    E = C+B.

We establish two facts about restricting a degree-at-most-two polynomial
that vanishes on all three-ports avoiding i:

1. Each of its two i-sign slices belongs to E.
2. Those slices have the same image in E/C.

Here are details to avoid assuming a shortening theorem. For each original
pair j let z_j be its occupancy indicator (the sum of its two coordinate
variables) and x_j one chosen sign variable. On paired ports, x_j z_j=x_j
and x_j^2=x_j, so any degree-at-most-two evaluation can be expressed as

    A(z) + sum_j x_j B_j(z) + sum_(j<l) c_jl x_j x_l,

where A has degree at most two, B_j is affine in occupancies other than
z_j, and the c_jl are scalars.

Restrict to any three of the four residual pairs, avoiding i. The selected
signs are independent bits. The zero evaluation therefore forces c_jl=0
for every two residual indices j,l. For each residual j, it also forces
B_j to vanish whenever precisely two of the other three residual indices
are occupied, with z_i=0. Write the constant term of B_j as b and those
three coefficients as u,v,w. The equations

    b+u+v = b+u+w = b+v+w = 0

give u=v=w and b=0. On an i-containing port, exactly one residual index
besides j is occupied. Thus B_j evaluates to a constant independent of
that second residual index. Terms c_ij x_i x_j add another constant
coefficient of x_j on each fixed i-sign slice. These are vertex-star
functions in C.

The term x_i B_i(z), on a fixed i-sign slice, is an affine combination of
residual occupancy indicators and the constant function, also in C.
Finally A(z), with z_i=1, is an arbitrary function of the unsigned residual
pair block and is identical on the two i-sign slices. This proves both
claims.

### A small quotient and its weight-four words

Every function of E can be written as an arbitrary unsigned block function
plus sum_j a_j x_j over the four residual indices. If any a_j is nonzero,
the function is nonconstant in the j-sign on all three blocks incident to
j. It therefore has exactly two nonzero values in each such four-point
block, and total weight at least six. If all a_j vanish, weights are
multiples of four. Consequently E has minimum distance four, and its
weight-four words are exactly the individual unsigned block indicators.
Distinct such words have disjoint supports.

An element of C is unsigned precisely when its residual sign coefficients
vanish; its remaining expression is a constant plus a linear combination
of residual occupancies. These functions have dimension four: the four
occupancy rows have their one relation sum_j z_j=0 on two-ports, and the
constant is independent of them (the pair graph K4 has triangles).
Hence

    dim(E/C) = dim B - dim(B intersect C) = 6-4 = 2.

### The quotient contradiction

Map V to E/C using the common class of its two slices. Its kernel K_0 has
dimension at least one. A nonzero word in K_0 has both slices in C. Since
C has minimum distance six and the whole word has weight eight, precisely
one slice is nonzero, of weight eight. All nonzero words of K_0 use the
same i-sign: two using opposite signs would sum to weight sixteen. Call
that sign plus.

K_0 cannot be all V, because V would then embed in the plus copy of C with
support fourteen, contrary to d_3(C)=15. For any h outside K_0, both its
slices have nonzero quotient class and hence are nonzero in E. Their
minimum weights are four and their sum is eight, so both have weight four.
For every nonzero f in K_0, the word h+f also lies outside K_0. Therefore
its plus slice has weight four. Since h-plus has weight four and f-plus
has weight eight, this forces supp(h-plus) to be contained in supp(f-plus).

If dim K_0>=2, take independent f_1,f_2 in it. The supports of f_1, f_2,
and f_1+f_2 have empty triple intersection, contradicting containment of
the nonempty h-plus support in all three. Hence dim K_0=1.

The minus-slice projection now embeds the two-dimensional quotient V/K_0
in E, and each of its three nonzero words has weight four. But any two
distinct weight-four words of E are disjoint unsigned block indicators,
whose sum has weight eight. This is the final contradiction.

Thus d_3(C-plus)>=15. The three nonempty-star triangle attains fifteen,
so the same exact value holds for C-minus.

## Attainment, lifting, and the five-weight prefix

### Three-star construction

Choose a signed `(k-2)`-core K and signed coordinates a,b,c from three
different outside pairs. The three nonempty stars `K+a`, `K+b`, `K+c` are
independent: a fourth outside pair supplies a port private to each star.
Each star has weight `d=2q+2`, their three pairwise intersections are
distinct single ports, and their triple intersection is empty. Their
union has size `3d-3=6q+3`. This proves the upper bound for both codes,
and attains the exact third weight for `q>=3` and for `q=2,k in {2,3}`.

### A cube subcode at q=2

For `q=2,k>=4`, fix `k-4` signed coordinates and four more original pairs Q.
Let a,b be the two pairs outside the resulting ordinary k-pair cube. Write
`z_a,z_b` for their occupancy indicators and set

```text
M = m_fixed (1+z_a)(1+z_b).
```

This selector has degree `k-2` and is supported on exactly sixteen ports:
the fixed signs on the fixed core, and all signs on Q. Choose four sign
variables `x_1,...,x_4` on Q. The rows `M x_1,...,M x_r` are independent;
for `r=3,4`, their common zero set inside the selected cube has size
`2^(4-r)`. They give dimensions three and four with support sizes fourteen
and fifteen, respectively. Adding M to the four rows gives dimension five
and support sixteen. Every generator has degree less than k.

For `k>4`, every expanded monomial is a nonempty star. At `k=4,p=6`, the
empty star is redundant. Indeed, for any three original pairs a,b,c, every
four-pair port meets that set, so `(1+z_a)(1+z_b)(1+z_c)=0`. Equivalently,

```text
1 = (z_a+z_b+z_c) + (z_a z_b+z_a z_c+z_b z_c) + z_a z_b z_c.
```

The right side expands into nonempty stars of degree at most three.
Thus these witnesses also lie in `C^-` at the smallest k.

Generalized weights are strictly increasing. To see this without invoking
a separate theorem, take any `(r+1)`-dimensional subcode and any coordinate
occupied by it. The kernel of evaluation at that coordinate has dimension
r and loses at least that coordinate from its support. Applying this to
an optimal `(r+1)`-dimensional subcode gives `d_r<=d_(r+1)-1`.
The lower bound `d_3>=14` at q=2 and the three cube witnesses therefore
force `d_3,d_4,d_5=(14,15,16)`. Together with the known first two weights,
this proves the claimed five-weight prefix.

### Signed-face lifting

There is also a general way to transport explicit subcodes to higher k
without changing q. Start with a subcode of `C^+_{q+k_0,k_0}`. Add `k-k_0`
new pairs, fix one signed coordinate in each, and multiply every generator
by their joint star. A nonzero resulting evaluation occurs exactly on a
port containing this fixed signed face, with its remaining `k_0`
coordinates forming an original port. Hence support sizes, dimensions,
and information sets are preserved. Degrees increase from at most `k_0-1`
to at most `k-1`; if `k>k_0`, all resulting stars are nonempty.

Consequently every explicit hierarchy witness in
[HIGHER-GRAPH.md](HIGHER-GRAPH.md) gives an upper bound at the same q and
higher k. The bounds need not be sharp: the cube construction gives
`d_3=14` at `q=2,k>=4`, whereas the graph witness has support fifteen.

## From subcode witnesses to simultaneous targets

For completeness, an r-dimensional subcode with support W has an
information set T of r coordinates: select r independent columns of an
evaluation matrix. Change its row basis so that restriction to T is the
identity. Deleting `D=W\T` then makes these rows unit decoders for all
r retained targets. Conversely, r simultaneous unit decoders supported
on `D union T` are independent and span an r-dimensional subcode, so
`|D|+r>=d_r`. This proves the selectable-target equality `|D|_min=d_r-r`.

The explicit star and cube rows above make these information sets finite,
ordinary linear-algebra choices. This establishes the precise scalar
threshold; it does not charge for acquiring the required star totals,
synthesize a complete paid supplier, or improve κ.

Prepared by Sam Sung with substantial OpenAI Codex assistance; Apache-2.0.
