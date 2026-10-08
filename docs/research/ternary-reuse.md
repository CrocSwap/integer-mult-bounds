# Fusing ternary gates with the same rational frame

These working notes describe a compiler refinement of Zhihao Chen's five-subset
`F3` construction in [PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7),
at commit `6725c6a17b17871a35353fd29157f4ed851bc114`.
It saves **65,772 auxiliary roles** at `h=28`, reducing the certified upper
bound from `11,840,940` to **11,775,168**, about **0.56%**. The center loss,
three tensor stages, source corrections, and endpoint identity stay the same.
The separate assembly certificate determines the resulting multiplication
witness; the role reduction alone is not a complete multiplication theorem.

The [complete assembly certificate](../../certificates/ternary-reuse-network.json)
supports `a_b=7543/10^12` and **`kappa=3769/10^12=3.769e-9`**, with minimum
margin `37697459/10^16` and gap `7459/10^16`. This retains PR #7's original
guard and complex constants. The [assembly checker](../../scripts/ternary_reuse_network.py)
recomputes this conditional arithmetic; the derivation and finite checks are
recorded below.

- [Full-size local checker](../../scripts/experiments/ternary_reuse_core2.py)
- [Exact compiler and small physical-network checks](../../scripts/experiments/ternary_reuse_plateaus.py)
- [Exact count certificate](../../certificates/ternary-reuse-core2.json)
- [Independent controls](../../tests/test_ternary_reuse.py)

This is a small improvement with a reusable mechanism. It does not supply the
many-order increase sought by the broader research effort.

## 1. An invertible gate for a whole region

Suppose several nodes of a linear producer have the same nondegenerate
rational frame `U`. Their scalar values need not have identical source
supports. Merge those nodes into one region. Let its distinct incoming
values number `p`, and its outgoing uses number `q`. An outgoing use is one
value for each distinct later region that consumes it, or one designated
output use. Multiple uses of the same incoming value *within* a region
need only one incoming role.

The internal producer defines a matrix `M` of size `q` by `p` over `F3`.
Let `r=rank_F3(M)`. There is an invertible scalar gate on

    p + q - r

roles whose outgoing values, when fresh roles start at zero, are `M x`.
It overlaps exactly `r` outgoing roles with incoming roles and allocates
`q-r` fresh ones. All remaining incoming roles become unused garbage roles.

Here is an explicit completion. Choose independent output rows `I` and
pivot input columns `J` such that `B=M[I,J]` is invertible. Replace the `r`
input slots indexed by `J` by the `r` values `M[I,:] x`, preserving the other
input slots. This is invertible because its missing original inputs can be
recovered using `B^-1`. For every remaining output row, express it as a
linear combination of the chosen output rows and add that combination into
one fresh slot. These additions are invertible, even when every fresh slot
starts dirty. Reversing the copies and then the first linear transformation
gives the inverse gate.

Thus the gate is a fixed invertible `F3` table. With the whole region framed
at `U`, arbitrary intermediate implementations of that table introduce no
edge rank: every internal incidence has the same frame. Its number of
scalar operations is a fixed constant in the interchange construction.

If `q_g,r_g` are the outgoing-use count and rank for every region, the total
number of auxiliary roles is

    R = v_input + sum_g (q_g - r_g).

For the original binary-addition DAG, each input or addition region has
rank one and the total outgoing-use count is `2c+q`. This reproduces
`R=c+q`. The new compiler saves roles by removing redundant uses inside a
region and by retaining its full boundary-map rank, rather than paying once
for every addition node.

The exact prototype includes a simple nontrivial control: the map
`(a,b,c) -> (a+b,a+c,b+c)` is invertible over `F3`. Three addition nodes and
three designated outputs ordinarily use six roles; one common-frame gate
uses three. This control also distinguishes characteristic three from two.

## 2. Larger frames inside one common-pair context

Fix a common pair `C` and put `n=h-2=26`. Its retained total spans the
positive-definite space `H_C` of dimension `n`. Restriction to coordinates
outside `C` identifies `H_C` with `Q^n`: for an outside vector `z`, both
coordinates on `C` equal `sum(z)/3`. Under the ambient rational form
`I-(2/25)J`, its squared norm is exactly

    sum_i z_i^2.

A local input is the indicator of a triple on these `n` points. A side output
indexed by an excluded triple `E` sums inputs avoiding `E`. On `H_C`, the
condition of orthogonality to its five-set target `C union E` is simply

    sum_{i in E} z_i = 0.

Call a local node eligible when the intersection of all its source triples
is empty. Equivalently, its full five-set source support has common
intersection *exactly* `C`. Keep the existing source-span frame for every
other node. At an eligible node `a`, let `R_a` be the rational span of the
indicators of all excluded triples `E` belonging to side outputs reachable
from `a`. Assign the larger frame

    U'_a = kernel(R_a)  inside H_C.

The retained total contributes no equation: its allowed frame is all of
`H_C`.

Every input in the source support of `a` avoids every such descendant
excluded triple. This follows from cancellation-free production and exact
output supports. Hence its source span lies in `U'_a`. Every new frame is
positive definite because it lies inside `H_C`.

Along an edge between eligible nodes, the earlier node has at least all
the descendant requirements of the later node, so its assigned frame is
contained in the later frame. An incoming edge from an ineligible node
also has nested frames by the same support argument. There is no edge from
an eligible node to an ineligible node: intersections of source supports
can only shrink when supports are united, and the fixed pair `C` remains
common throughout the context.

At a side output the new frame is a subspace of its target complement.
At the retained total it is exactly `H_C`. Therefore these larger frames
preserve every producer, injection and retained-scatter inclusion.

## 3. Merging the equal frames is legal

Partition eligible nodes by equality of `R_a`, equivalently equality of
`U'_a`. Merge all nodes in each class, even if they were disconnected in the
original DAG. All other nodes stay separate.

The quotient remains acyclic. Between distinct eligible classes, a directed
edge strictly increases frame dimension, since its frames are nested but
unequal. No path can return through an ineligible node, because the eligible
part is closed under successors. The original ineligible subgraph is still
acyclic. This gives a topological order for the merged scalar gates.

Compute each region's boundary matrix over `F3` from its original additions,
then use the invertible completion above. Each incoming physical role
reaches the same frame as before or a larger permitted frame; each outgoing
role continues into a containing frame. Retired roles can proceed to the
usual full cleanup frame. No additional decreasing edge is created.

For arbitrary initial scratch `z`, the new mixer `L` is invertible and has
the same desired output coefficient map on `Vx`. The retained-total wrapper
subtracts `(R0+J)Lz`, then adds `(R0+J)L(z+Vx)`. Its net data update is
`(R0+J)LVx=x`, and the inverse mixers and source copies restore `z` exactly.
This argument does not assume fresh roles are actually zero: zero fresh
roles are used only to specify the coefficient map of `LVx`.

In the inverse invocation, use orthogonal complements of the same producer
frames. The nested inclusions reverse correctly and remain nondegenerate.
The only returns are still the retained center outputs, each losing
`dim H_C=h-2`. Thus the total decreasing dimension remains

    3 v^2 C(h,2)(h-2).

The three-stage bank matching, negative source projections, and all-role
endpoint identity are unchanged. A role removed by the compiler also removes
its full baseline rank contribution; no hidden backward-rank charge is
being discarded.

## 4. Exact rational equality from one large modulus

The scalable checker computes the requirement row spaces modulo the fixed
prime

    P = 2^61 - 1 = 2305843009213693951.

This is **not** a probabilistic fingerprint and is not an inference from
rank equality alone.

Every original requirement row is a `0/1` triple indicator of Euclidean norm
`sqrt(3)`. Hadamard's inequality therefore bounds the absolute value of every
square minor, of any size at most 26, by

    B = 3^13 = 1594323.

This also applies after selecting columns, since doing so cannot increase
row norms. Since `P>B`, a nonzero rational-rank witness minor cannot vanish
modulo `P`. The ranks of all column prefixes are preserved, so the canonical
pivot positions are preserved as well.

For any row space, choose independent original rows and the canonical pivot
columns. The canonical reduced row matrix is `A[:,J]^-1 A`. By Cramer's
rule, every entry has the form `a/b` with integer `|a|<=B`, `0<|b|<=B`.
The denominator is invertible modulo `P`. Although elimination may form
larger intermediate numerators, the canonical entries themselves have these
small minor representations; the proof does not bound intermediate storage
by `B`.

If two canonical entries agree modulo `P`, then `P` divides
`a b' - a' b`. Its absolute value is at most `2B^2`, which is strictly less
than `P`. Therefore it is zero. The entries agree over `Q`.
Together with the preserved rank and pivot positions, this proves

    canonical row spaces equal modulo P
      if and only if
    the rational row spaces are equal.

Python dictionaries compare the full tuples of canonical modular entries
after hashing. No equality decision relies on a hash collision assumption.
The region boundary ranks are then computed separately and exactly over
`F3`, the scalar field. Rational frame rank and scalar circuit rank are
never interchanged.

## 5. Full `h=28` accounting and compatibility with PR7 sharing

The retained local `PairedTriple(26)` graph has 2,600 inputs, 41,439 additions
and 2,601 designated uses, including its retained total. Its ordinary local
role count is 44,040. There are 8,523 eligible nodes, grouped into 6,645 new
frame classes; 1,109 classes contain multiple nodes. Exact boundary ranks
reduce the local role count to 43,866, saving **174** roles.

Only actual-common-pair nodes are changed. Such a node belongs to exactly
one global common-pair context; PR7's inter-context identifications involve
common intersections of size three or four. Furthermore, a common-pair node
cannot occur inside a three- or four-point star, and none of its descendants
can return to such a star. Its local topology therefore survives the global
support identifications unchanged.

PR7's four-point-star resynthesis preserves every boundary value consumed
outside the star. The new gates consume those same boundary values. Repeated
deliveries of one such value into a newly merged region are now a single
incoming use; this change is already included in the boundary-port count.
A shared boundary value consumed in two different common-pair contexts still
has two different consumer regions. Consequently the changes in port counts
and boundary ranks add independently across all 378 contexts, even when
those contexts share three- or four-point input values.

All contexts are point permutations of the same local producer, including
the aligned ordering of intact pairs and leftover partners. Thus

    saved_roles = 378 * 174 = 65772,
    R_new <= 11840940 - 65772 = 11775168.

This is a full-size count supported by the locality argument, not an
extrapolation from the small prototypes. As in PR7, unused roles may be
removed or the result padded with untouched auxiliary roles if exact width
is desired. The center loss remains `378*26=9828` per invocation.

## 6. Controls and remaining scope

The full-size checker verifies all local output supports, the retained
total, every retained disjoint addition, canonical row spaces, and each
merged boundary rank. Its certificate includes a deterministic digest of
the boundary plan.

Independent tests compare modular canonical rows with `Fraction` elimination,
distinguish equal rank from equal span, and compare packed `F3` elimination
with a separate dense implementation. They include a matrix of rational
rank four but `F3` rank three. The small physical compiler checks every edge
in both frame directions, and the transparent wrapper on every input and
every dirty scratch basis symbol, including the corrected three-shear bank
exchange. The certificate also regenerates an independent positive local control on
ten outside points: 1,204 roles become 1,195. It checks every one of the
1,435 data-and-scratch basis symbols against that single context's actual
central-minus-side map, which is explicitly **not** the identity. Both
physical frame orientations have rank sum 17,000 and center loss ten.
Thus the fast automated control exercises an actual role-saving fusion,
without materializing the complete large network.

A separately run complete `h=12` prototype also reduced 54,604 roles to
54,010, exactly `66*9` fewer. Both physical frame orientations had rank sum
666,864 and center loss 660; every producer coefficient was checked. Its
large whole-bank dirty-basis stress test was explicitly omitted. This
four-minute control is supporting evidence, not part of routine certificate
regeneration.

Broader equal-frame fusion was also tested, including more source-core
sizes and direct target producers. Some small cases improve, but their
full-size shared-graph interactions have not been certified here. They are
not included in the 65,772-role claim.

Reproduce the included claim with:

```sh
python3 scripts/experiments/ternary_reuse_core2.py
python3 -m unittest discover -s tests -p test_ternary_reuse.py -v
```

The explicit full-frame prototype can also be run with:

```sh
python3 scripts/experiments/ternary_reuse_plateaus.py --h 8 10 --core2-only
```

The finite checks and written compiler argument are not formal verification
of the inherited transfer, resampling, or complete multiplication theorem.
