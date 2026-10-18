# Optimal two-target decoders and the exact prescribed-pair threshold

**Uniform equality classification for `q=p-k>=2`; no new κ.** In either
proper-star code, every two-dimensional subcode attaining the second
generalized Hamming weight `4q+3` is the span of two `(k-1)`-stars whose
supports intersect in one port. Consequently, for power-of-two k and every
prescribed pair of distinct retained targets `T,T'`, the exact number of
deletions needed to decode both is

```text
4q+1,  if |T intersect T'| >= k-2;
4q+2,  if |T intersect T'| <  k-2.                      (1)
```

The intersection in (1) counts identical signed coordinates, not merely
original pair indices. Every other port remains an independent nuisance
input. The theorem concerns scalar identities with arbitrary global proper
stars and the permitted uniform overlap corrections. It does not price a
physical implementation or assert simultaneous decoding of every survivor.

## Prerequisites and notation

Use `C^+_{p,k}` and `C^-_{p,k}` from
[MINIMUM-WORDS.md](MINIMUM-WORDS.md): the binary evaluation spans of all
proper stars, with and without the empty star. We use three results proved
there, for `k>=2` and `q=p-k>=2`:

1. The minimum distance is `d=2q+2`.
2. Every minimum word is exactly one signed `(k-1)`-star `m_J`.
3. The second generalized Hamming weight is `d_2=4q+3`.

The first result and the generalized-cube parity argument are credited to
Luke Mansoor's [PR #732](https://github.com/CrocSwap/integer-mult-bounds/pull/732),
at `80431a74c31e807581f5c2258c87abe2084caacd`. The second and third are the
uniform extensions proved in this package. The finite one-target
classification in Alishan Ladhani's
[PR #747](https://github.com/CrocSwap/integer-mult-bounds/pull/747), and the
uniform rank and all-target threshold in ellipsi2's
[PR #772](https://github.com/CrocSwap/integer-mult-bounds/pull/772), remain
distinct credited results; neither supplies the prescribed-pair statement
proved here. Exact predecessor pins are recorded in MINIMUM-WORDS.md.

For a two-dimensional subcode V, write U for its support union and
`n=|U|`. Its three nonzero words f,g,h=f+g satisfy

```text
wt(f)+wt(g)+wt(h)=2n.                                  (2)
```

We first prove the equality classification in the larger code `C^+`.
All attaining generators are nonempty stars, so the result then holds for
`C^-` as well.

## A parity lemma for small blocks

Suppose every port of U contains a fixed set K of k-1 original pair indices.
For a pair r outside K, let `U_r` be the block using precisely `K union {r}`.
If every block has at most four ports, every block has even cardinality.

Ordinary sign-cube parity says that the three words each have even weight
on `U_r`. A one-point block is therefore impossible. If a block has three
points, their three nonzero evaluation labels in `F_2^2` must be distinct:
their sum is zero, and the only way three nonzero binary two-vectors sum to
zero is to use all three. Each nonzero word consequently has weight two on
that block.

Fix i in K and choose a pair s outside `K union {r}`. Replace the i slot
of the ordinary cube on `K union {r}` by the choices `i^a,s^b`, and keep
ordinary sign choices in all other slots. Its s half omits universal pair
i, so has zero evaluations. Generalized-cube parity therefore says that
each word has even weight on the i=a face of `U_r`. Its two support points
must agree at i. Doing this for every i and every nonzero word forces each
pair of the three block points to agree on all of K. But only two ports
have any specified signs on K and use r, one for each sign of r. Three
distinct points are impossible. Thus block sizes are only zero, two, or
four, proving the lemma.

## Theorem: every optimum is a span of two intersecting stars

For every q>=2, the optimal two-dimensional subcodes are exactly the spans
of two `(k-1)`-stars whose supports meet in one port. The boundary q=2
needs a separate argument because the second-weight formula used in the
inductive range starts at q=2.

### The boundary q=2

Here n=11 and the minimum weight is six. By (2), evenness, and the minimum
distance, the three nonzero weights are either `(6,6,10)` or `(6,8,8)`.
The first pattern already supplies two minimum stars. Suppose the second
occurs, with `f=m_J` of weight six and g,h of weight eight. Put L for J's
k-1 original pair indices. Both g and h intersect f in exactly three ports.

A nonuniversal pair for a weight-eight word occurs in at most four support
ports: avoiding it leaves a nonzero word at unused-pair count one, hence
weight at least four. If c pairs are universal, incidence counting gives

```text
8k <= 8c+4(p-c),    hence c>=k-2,    since p=k+2.        (3)
```

No pair outside L can be universal for g or h: each meets f in three
ports, whereas f uses such a pair in only two ports. On a pair in L, f
vanishes on all avoiding ports, so the avoiding restrictions of g and h
are identical. Thus g and h have the same universal-pair set K, contained
in L, with size either k-2 or k-1.

If `|K|=k-2`, each word uses exactly two of the four pairs outside K in
each support port. Its sixteen incidences on those four pairs saturate
their individual upper bounds of four, so every such pair occurs exactly
four times. For each residual pair r outside L, the restrictions to ports
using r consequently have weights two, four, and four for f,g,h. Since
h=f+g, f and g intersect in exactly one port using r. On the ordinary
cube with pair set `L union {r}`, g therefore has at least one nonzero
evaluation, and cube parity requires another. This holds for all three
residual pairs. All six of these distinct ports use the one pair in
`L\K`, contradicting that pair's degree four in g.

If `K=L`, every support port contains L. Consider g or h separately and,
for a residual pair r, define the function on signs of L

```text
b_r(a) = w(a,r^+) + w(a,r^-),    where w is g or h.
```

Its weight is at most four, since the word uses r in at most four ports.
Every face fixing at most two signs of L has even b_r parity. To see this,
use the ordinary two-sign slot for r, replace each fixed core slot by its
fixed sign versus a coordinate of a distinct other residual pair, and
keep all remaining slots ordinary. There are two other residual pairs.
Every replacement branch omits a universal pair of L and has zero word
value, so generalized-cube parity gives the asserted even-face condition.
The even-face lemma forces a nonzero b_r to have weight at least eight,
or rules it out directly by singleton faces when `|L|<=2`. Hence b_r=0.
Both independent word values repeat across the two signs of r at each
fixed a. Every residual block of their support union is therefore even,
contradicting n=11. The pattern `(6,8,8)` is impossible.

Thus the q=2 optimum also contains two minimum stars, whose intersection
has size `6+6-11=1`.

### The range q>=3

Assume `q>=3`, and let V have `n=4q+3`. For a pair r, let `d_r` count
ports of U using r. If restriction to ports avoiding r is injective on V,
its image is a two-dimensional subcode with unused-pair count q-1. The
second-weight theorem at q-1 therefore gives

```text
n-d_r >= 4(q-1)+3 = 4q-1,    so d_r <= 4.               (4)
```

**There is a minimum word in V.** Suppose otherwise. Each nonzero word has
even weight at least `2q+4`. If a pair is universal for one word f but not
another word g, then g restricted to ports avoiding that pair is nonzero,
has weight at least `2q`, and has support disjoint from f. This would give

```text
n >= (2q+4)+2q = 4q+4,
```

a contradiction. Thus all three nonzero words have the same set K of
universal pair indices. Put `c=|K|` and `t=k-c`. Every pair outside K has
injective avoidance restriction, since all three nonzero words survive it.
Counting pair incidences and applying (4) gives

```text
k n <= c n+4(p-c),    or t(n-4) <= 4q.
```

Since `n-4=4q-1`, we have t<=1. If t=0, U lies in one ordinary sign cube.
The generalized-face argument in MINIMUM-WORDS.md forces each nonzero word
to have weight at least `2^(q+1)>4q+3` for q>=3, or forces zero support
directly when q>=k. Both alternatives are impossible. If t=1, all blocks
on `K union {r}` have size at most four by (4). The small-block lemma makes
their sum n even, contradicting `n=4q+3`. A minimum word must exist.

**There are two minimum words in V.** Let `f=m_J` be a minimum word, let A
be its support, and suppose the other two words g,h are not minimum.
Their weights are at least `2q+4`. Since any two nonzero words have support
union U, both intersections with A have size at least three:

```text
|A intersect supp(g)| = wt(f)+wt(g)-n >= 3,
|A intersect supp(h)| = wt(f)+wt(h)-n >= 3.              (5)
```

There are q+1 residual pairs outside J's k-1 pair indices. The star f uses
each residual pair in exactly two ports. Therefore avoiding any residual
pair leaves all three words nonzero, by (5), and (4) applies. At most two
ports of `B=U\A` use each residual pair. But

```text
|B| = (4q+3)-(2q+2) = 2q+1,
sum_(residual r) |{S in B: S uses r}| <= 2(q+1)=|B|+1.
```

Every port of B uses at least one residual pair, so there are only two
possibilities. If all use exactly one, every port of U contains J's k-1
pair indices. Each residual block has at most four ports, and the
small-block lemma again contradicts odd n.

Otherwise exactly one port E of B uses two residual pairs, and every other
port of B uses one. The port E omits exactly one of J's pair indices. Its
ordinary sign cube contains no other port of U: all other ports contain
all of J's pair indices. Some word of V is nonzero at E, so that word has
odd parity on this cube, a contradiction. A second minimum word exists.

By minimum-word rigidity, these two words are `m_{J_1},m_{J_2}`. Each has
weight `2q+2`, and their union has size `4q+3`, so their intersection has
exactly one port. Equivalently, their defining signed faces are distinct,
their intersection has size k-2, and `J_1 union J_2` is an admissible k-port.
Conversely, any such two stars attain `4q+3`. This completes the equality
classification.

There are exactly

```text
2^k binom(p,k) binom(k,2)
```

optimal two-dimensional subcodes. Choose their unique shared k-port W and
the two different coordinates omitted to obtain `J_1,J_2`. This counts
each subcode once: its two generating stars are its only minimum words,
because their sum has weight `4q+2>2q+2`.

## Exact threshold for every prescribed target pair

With proper-star observations alone, formula (1) holds for every k>=2.
The extra power-of-two hypothesis in the decoder statement is needed only
to absorb the permitted overlap corrections into the same observation span.

Now assume additionally that k is a power of two. The permitted overlap
corrections belong to `C^-`, as shown in MINIMUM-WORDS.md. If distinct
retained targets T,T' can both be decoded after deleting D, their two unit
vectors lift to independent full-family codewords supported in
`D union {T,T'}`. Thus `|D|>=d_2-2=4q+1`.

If equality holds, their subcode has optimal support `D union {T,T'}` and
is spanned by two intersecting stars. Every port in that union contains
their common signed `(k-2)`-face. In particular, T and T' share at least
k-2 signed coordinates. This proves necessity in the first line of (1).

For sufficiency, first suppose `|T intersect T'|=k-2`, and put
`A=T intersect T'`. Choose `a in T\T'` and `b in T'\T` from different
original pairs. Such a choice exists because each difference contains two
coordinates from distinct pairs. The faces `J_1=A union {a}` and
`J_2=A union {b}` are compatible and their union is a k-port. T belongs
only to the first star and T' only to the second. Delete their union of
supports except T,T'. Exactly `4q+1` ports are deleted, and the two stars
on the surviving family give the two target symbols directly.

If `|T intersect T'|=k-1`, let `J_1=T intersect T'`, choose `a in J_1`, and
put `J_2=T\{a}`. The two star supports intersect at T. Their values at
`(T,T')` are `(1,1)` and `(1,0)`, respectively. After deleting the other
`4q+1` ports in their union, use `m_{J_2}` for T and
`m_{J_1}+m_{J_2}` for T'. Distinct k-ports cannot intersect in k
coordinates, so this exhausts the first line of (1).

Finally suppose `|T intersect T'|<k-2`. Equality at `4q+1` is impossible
by the classification, so at least `4q+2` deletions are required. Choose
any `(k-1)`-face J of T and any `(k-1)`-face J' of T'. Their union has size
at least k+1, so no k-port extends both and their star supports are
disjoint. Neither target lies in the other star. Delete the two supports
except T,T', using exactly `2(2q+2)-2=4q+2` deletions. The two surviving
stars isolate T and T', proving the second line of (1).

All witnesses use nonempty proper stars. Granting the empty star therefore
changes none of these conclusions. Arbitrary nonlinear postprocessing of
the same linear observations changes no exact-recovery threshold, by the
kernel argument in MINIMUM-WORDS.md. Additional observables, other port
geometries, restricted inputs, and approximate recovery are outside scope.

Prepared by Sam Sung with substantial OpenAI Codex assistance; Apache-2.0.
