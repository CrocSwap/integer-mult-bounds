# Noncommuting neutral helper chains on a frozen bit word

## Statement and scope

On PR1062's frozen 11,500-ADD R439 word, the following exact class has minimum
complete scalar price **11,489**: one ordered pair of restored helper shears
`a ^= b; b ^= c`, using three distinct non-retained helpers from three distinct
connected components of the existing helper preparation, with both individual
complete gains nonpositive on the original middle columns. All remaining word
fields are fixed, and both inherited strict positive-prefix guards are imposed.

The scalar minimum is a computer-assisted finite result. The coverage reduction
is given below; two independently implemented complete censuses agree. This is
not an unrestricted circuit optimum, new recursive profile or new kappa.

The uniform identities and the support bound below are written algebraic
arguments; their finite tests are supporting implementation evidence. This is
not a formal verification of the integer-multiplication theorem.

## Ordered middle and exact complete cost

Let the original middle be `y += M h` over F2, in already prepared helper and
target coordinates. Write its three chosen columns as A,B,C, understood as
sets of target rows. Chronological preparation produces

    u_a = h_a + h_b, u_b = h_b + h_c, u_c = h_c.

Thus `h_a = u_a + u_b + u_c` and `h_b = u_b + u_c`. The new middle columns must
be **A, B XOR A, C XOR B XOR A**, in that order. Its output equals the original
middle on every arbitrary helper input. The correct restoration is
`b ^= c; a ^= b`, followed by the original parent's reverse helper preparation.
Target preparation/restoration is unchanged and acts on disjoint helper roles.
Consequently the complete D prefix preserves arbitrary helper and target dirt
and implements exactly the parent's compensation map, before A begins.

The two added shears do not commute. For `T_ab = I + e_a e_b^T` and
`T_bc = I + e_b e_c^T`, preparation is `H = T_bc T_ab`, whereas the inverse is
`T_ab T_bc`. In particular `H^2 = I + e_a e_c^T`. Using the same preparation
order for restoration leaves a nonzero rank-one helper defect. Parent conjugation
cannot remove it. Using commuting column updates instead omits the A contribution
to the last middle column and introduces the target defect `A h_c`.

With wt denoting support cardinality, the **complete** saving is

    G = wt(B) + wt(C) - wt(B XOR A) - wt(C XOR B XOR A) - 4.

The last four pays for both preparation gates and both restoration gates.
The fixed bill is

    5952 outside-D ADDs
    + 2 * 236 existing helper-basis ADDs
    + 2 * 306 target-basis ADDs
    + 4464 original middle ADDs
    = 11500.

After the chain it is `5952 + 2*238 + 2*306 + wt(M H^-1) = 11500-G`.
Every helper/source read is part of an explicit ADD; every macro source list is
lowered into its full single-source stream. Nine COPYs, nine ERASEs, 439 helper
roles, every frame MOVE and the unchanged A/scatter/B/C continuation remain paid.
No new zero-initialized role, clean helper or omitted undo is used.

## Why nonpositive individual moves can help together

The frozen unilateral gains are

    u = wt(B) - wt(B XOR A) - 2,
    v = wt(C) - wt(C XOR B) - 2.

The exact joint interaction is

    G = u + v + I,
    I = wt(B XOR C) - wt(A XOR B XOR C)
      = 2*wt(A intersection (B XOR C)) - wt(A).

The interaction is support-wide; it is not the two-by-two left/right interaction
of PR1449's one target and one helper move. Credit PR1449 for the neutral joint
move precedent. No new priority for the general idea of joint moves is claimed.

There is also a sharp uniform screen. Let r be the number of active rows in
`A union B union C`. On a single binary row define
`U=B-(B XOR A)`, `V=C-(C XOR B)` and
`Z=B+C-(B XOR A)-(A XOR B XOR C)` as integer quantities. For the eight patterns
000 through111, `2+2U+V-3Z` has nonnegative values
`2,2,4,0,6,0,0,2`. Sum over the r active rows; omitting000 rows preserves the
inequality. Since `sum U=u+2`, `sum V=v+2` and `sum Z=G+4`,

    3G <= 2r + 2u + v - 6.

Under u,v<=0 this gives `G <= floor((2r-6)/3)`, hence at most72 for111 rows.
The abstract111-row bound is sharp: 35 rows of pattern101, 37 of110 and 39
of011 have support sizes72,76,74, unilateral gains0,0 and joint gain72.
Those are an abstract support fixture, not columns claimed to occur in R439.

## Complete finite coverage and attained frozen-class maximum

The frozen preparation has236 edges and203 connected components among439
helpers. Exclude the nine retained COPY-total roles, leaving430 helper labels.
All78,953,160 ordered distinct triples are the initial domain. Of these,
78,191,280 use three distinct parent components. Exactly77,431,469 also obey
both nonpositive unilateral-gain restrictions. Every such triple is scored;
there is no sampled support size, coefficient bound, descent or restart.

The primary implementation uses packed binary columns. The second reconstructs
row-support sets and uses intersection cardinalities. Both hash every eligible
record, including negative and zero gains, in lexicographic helper-index order,
encoded as four little-endian signed32-bit integers `(a,b,c,G)`. Digest:

    142ad23bdd285011e5090ed40b57af69386e7a8c1f259548e83eba66f3f339f3

There are2265 positive triples and two maximizers at G=11. For the bounded
precision experiment, order positive triples by gain descending, then SHA256 of
the four little-endian integers `(17,a,b,c)` ascending. Fully price the first32;
all32 pass both guards. The first is helper indices128,21,348, physical registers
**350,243,570**. Thus one admitted maximizer attains the census upper bound;
pricing the remaining positive triples is unnecessary for this fixed-class
minimum. No minimum outside this declared class follows.

The winning columns have support sizes12,15,13, with five rows of pattern101,
seven of110 and eight of011. They have `u=0, v=-1, I=12`, so `G=11`.
New support sizes are12,13,0: fifteen middle reads disappear and four wrapper
ADDs are paid. There are20 active rows and the row inequality is tight:
`3*11 = 2*20 + 2*0 - 1 - 6`.

## Actual word invoice and remaining obligations

The literal full word and retained exporter agree on:

| Quantity | Frozen parent | Witness |
|---|---:|---:|
| Complete ADDs |11500|11489|
| D ADDs |5548|5537|
| Forward positive peak F |25717|25885|
| Reverse positive peak B |5911840|5977064|
| Sufficient local bits |95|96|
| Sufficient nine-stage bits |182|182|
| MOVEs / COPYs / ERASEs |2911 / 9 / 9|2911 / 9 / 9|

Unlike a free scalar improvement, the new positive prefixes grow. Both strict
integer comparisons still hold:

    64 F^3 B^2 < 2^104,
    2^18 F^5 B^4 < 2^192.

Both directions restore all439 arbitrary helper inputs and all target dirt;
the full661-column endpoint remains the additive bit map `y += x`.
The actual recursive histogram is unchanged:
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, rank mass5129. This does not
improve its moment or the selected exponent; the selected bit side is nonbinding.

As in the parent, the unchanged owning checker reports H2 and literal
`K_equals_D` false, with every other H/U/J/C predicate true. Exact semantic
D equality, actual geometry and positive bounds do not themselves adopt a
replacement supplier interface. PR1194/1311's semantic-D work is credited but
not imported or newly proved here. Native multistage/whole-hosted execution,
controller/provider and full outer invoices are not run. All-size/compiler,
common-label/mutable-source realization, physical hosting, precision/tape and
analytic transfer remain inherited obligations. The three-helper zero column
does not justify deleting a physical helper: it is still read by preparation
and restoration and used by the unchanged continuation.

PR1400's positive single-helper descent uses a different frozen word and its
chosen shears commute. PR1206's noncommuting R420 decoder chains act in A and
retained totals. PR965's GL3 candidates mix an existing PR926 pair with an unused
helper. Their techniques and evidence are credited; their savings are not added
to this witness. No frozen predecessor, selected record or upstream file changes.
