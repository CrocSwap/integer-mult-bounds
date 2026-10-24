# A color-cut obstruction for one direct scalar encoder

The proposed direct encoder `H = P T M` has no ascending canonical-chart
ADD/SCALE realization on its 24 registers with the entry and exit charts
specified below. This statement permits arbitrary rational coefficients,
arbitrary intermediate charts and arbitrary interleavings. It assumes no
particular preparation, cold basis, Schur factorization or compensation prefix.

This is a scoped obstruction to a scalar encoder. It is not a lower bound for
general multiplication, a tariff optimum, or an improvement to the selected
bound. In particular, nonascending transports, changed external charts, native
operations inside the interval and a different direct target remain outside
the main claim.

## 1. Exact source and proposed target

The immutable input is the adjacent package's
[`COMBINED-WORD.json.gz`](../productive-helper-fusion-certificate/COMBINED-WORD.json.gz):

- compressed-byte SHA256:
  `6caa29e474375298847fac8a53508f65037dc45e64d2ea0125ece9faf32b2ce4`;
- canonical JSON SHA256, using sorted keys and compact separators:
  `aa4a8241da76abd2c06e6576a3ac09e77781321deaac3ad7d3ce4519342a36e6`.

Delete `climb` records from its forward program. The half-open interval
`[9961, 10111)` contains 150 invertible scalar instructions and exactly the
registers

```text
13, 16, 43, 44, 51, 78, 99, 104, 416, 417, ..., 431.
```

Let `M` be its exact rational 24-by-24 matrix, acting on a column of register
values. All 24 input values are independent and arbitrary. A zero chart never
means a zero register value.

Define `T` on output registers 417 and 419 by

```text
T = [[1/2, -1],
     [1/2,  1]].
```

Chronologically, this is `419 += 417/2; 417 -= 419`. Let `P` swap output
registers 416 and 417. The target is `H = P T M`. The checker reconstructs `M`
from every scalar instruction, applies these two row additions and the row
swap, and checks both inverse products of `M` and `H` exactly. In particular,

```text
H output416 = input13 + input416.
```

The candidate was motivated by the source's exactly equal native maps 34 and
35 on registers 417 and 419. Their equality is checked, but the obstruction
does not depend on assuming that equal maps alone make a changed encoder cheap.

The source entry charts are eight binary lines and sixteen zero subspaces:

| Input role | Binary line generator |
|---|---:|
| 13 | 73 |
| 51 | 100 |
| 78 | 506 |
| 99 | 471 |
| 16 | 49 |
| 44 | 28 |
| 43 | 386 |
| 104 | 431 |
| 416 through 431 | zero subspace |

These charts are reconstructed by replaying the prefix's chart annotations;
they are not supplied as a generated matrix certificate. Adapter records in
the prefix are checked to preserve their current canonical chart.

The fixed output charts are the original local exit charts, with the output
416/417 permutation, except that output416 is required to use line73. This
is the intended one-port native input. The full list is in `RESULT.json`.
Nine of these outputs have the following charts:

| Output roles | Chart basis | Color |
|---|---|---:|
| 13, 51 | 45, 73 | 1 |
| 78, 99 | 45, 471 | 2 |
| 427, 429 | 28, 45 | 3 |
| 425, 431 | 45, 386 | 4 |
| 416 | 73 | 1 |

Each two-dimensional chart contains the two input lines of its color and no
input line of another color. For example, `73 XOR 100 = 45`. The checker
enumerates these small binary spans and verifies all nine assertions. No
statement about maximal relaxed suffix charts is required.

The ordinary two-sided support tests nevertheless pass: whenever `H[j,i]`
or `H^-1[i,j]` is nonzero, input chart `i` is contained in fixed output chart
`j`. Each register's own entry chart is also contained in its exit chart.
The checker verifies all of these statements exactly. The obstruction below
therefore detects something that these entry/exit support tests do not.

## 2. Circuit model and the general color-cut lemma

A canonical chart is a binary linear subspace of `F_2^9`. Each register has
a chart, and an ADD can act on two registers only at a common chart. Nonzero
scalar SCALE gates act on one register. Chart transitions act as identities
on logical register values. A circuit is **ascending** when each register's
chart can only grow by subspace inclusion. There are no native maps, resets,
owned-copy centers, or additional registers inside the main claim's interval.

Partition the eight nonzero input lines into four groups:

```text
{13,51}, {78,99}, {16,44}, {43,104}.
```

The color set of a chart consists of the groups for which it contains at
least one of those input lines. Call a scalar gate monochrome if its common
chart has at most one color, and mixed if that chart has at least two colors.
Zero-color gates count as monochrome.

**Forward support fact.** If the current logical value on a register has a
nonzero coefficient of a hot input, its chart contains that input's initial
line. Initially this holds by construction. At an ADD, both input values are
at the common chart, so it remains true for their linear combination; a
nonzero scale preserves it. Ascending transitions preserve every already
contained line. Cancellation of a coefficient can only remove an obligation.

**No-return commutation lemma.** Every earlier mixed gate and later
monochrome gate are disjoint in their register sets.

Indeed, if they shared a register, that register's chart at the later gate
would contain its chart at the earlier gate. It would therefore still have
at least two colors, contrary to the later gate being monochrome. It follows
that any out-of-order adjacent mixed/monochrome pair commutes as an exact
linear operation on arbitrary input values. Repeatedly exchanging such pairs
puts every monochrome scalar gate before every mixed scalar gate, without
changing the order of gates on any one register or the logical matrix.

The argument is algebraic: it does not claim that this reordering preserves
an invoice. Chart transitions can be retained in their per-register order,
or omitted while proving the matrix identity. Before the first mixed scalar
gate on any wire, its last monochrome gate has produced a value whose hot
support belongs to at most one group. A wire with no preceding gate retains
its original value and has the same property. Any unused chart promotions
between those gates change no logical coefficients.

Suppose a set of final registers is constrained to monochrome output caps.
No mixed gate can ever touch any of these registers: an ascending chart could
not subsequently fit its final cap. Thus, in the reordered circuit, the mixed
suffix acts invertibly only on the remaining registers.

Let `G` be the target matrix restricted to those remaining output rows and
the eight hot input columns. Let `B` be the corresponding hot block after the
monochrome prefix, and let `R` be the mixed suffix's invertible matrix on the
remaining registers. Then

```text
G = R B,                 rowspace(G) = rowspace(B).
```

Every row of `B` is supported within one hot-input group, by the forward
support fact. Consequently:

> The rowspace of `G` must be spanned by its vectors supported within single
> color groups.

No assertion that the monochrome outputs depend only on hot inputs is needed.
In this application output416 also contains its independent dirty input.
There is likewise no requirement that a particular cold subblock of the
prefix be invertible; only the actual scalar suffix `R` is used.

## 3. Source-specific contradiction

For `H`, the nine monochrome output roles are

```text
13, 51, 78, 99, 427, 429, 425, 431, 416.
```

The other fifteen output roles, in the order used by the receipt, are

```text
16,43,44,104,417,418,419,420,421,422,423,424,426,428,430.
```

The checker extracts their hot-input block `G` directly from `H`. Its exact
rank is 7. In the hot-column order

```text
13,16,43,44,51,78,99,104,
```

its unique column relation, with the stated normalization, is

```text
2 G[:,13] - G[:,43] - G[:,78] - G[:,99] + G[:,104] = 0.
```

In particular, every row vector `beta` in `rowspace(G)` obeys

```text
2 beta13 - beta43 - beta78 - beta99 + beta104 = 0.
```

If `beta` is supported in color group `{13,51}`, the relation forces
`beta13 = 0`. A vector supported in any other color group already has
`beta13 = 0`. Hence every one-color vector in `rowspace(G)` has zero
13-coordinate, as does their span. But the source-reconstructed target has

```text
G[output43, input13] = 1.
```

The necessary color-cut condition is therefore false. This proves the main
claim for all ascending scalar factorizations of the direct target with the
specified boundary charts, including arbitrary temporary uses of register416.

For a fuller exact census, the dimensions of the four single-color
intersections of `rowspace(G)` are `1,1,2,1`. Their supports are disjoint, so
their sum has dimension 5, strictly smaller than 7. The map `w -> wG` from
15 coefficient coordinates has kernel dimension 8. Thus the preimages of all
single-color subspaces together span dimension `8+5=13`, not 15.

`RESULT.json` records complete exact nullspace bases for the 13 masks
(empty, eight singletons and four pairs), and two common annihilators in the
15 remaining-output coordinates. These data provide independently checkable
rank certificates. The shorter column-relation contradiction above is already
sufficient for the theorem.

## 4. Positive and mutation controls

The original 150-instruction source is a nontrivial positive control. Its
charts are ascending. The checker classifies 40 gates as monochrome and 110
as mixed, verifies all 72 mixed-before-monochrome inversions are disjoint,
and checks the exact 24-input matrix identity after their stable partition.
There are only eight required monochrome outputs in the original source:
register416 retains its original larger chart. Its remaining 16-row hot block
has rank 8, and its four single-color intersections have dimensions `2,2,2,2`.
It therefore passes the necessary condition, as a legal source must.

Corruption controls reject changed source bytes, a changed target coefficient,
a wrong column-relation sign and a cross-color enlargement of a required
monochrome cap. Scope controls permit particular cross-pair capture masks:
one increases the preimage span rank to 14, and two increase it to 15. These
are checks that the restriction matters, not constructions of a legal circuit.

The exact checker uses explicit failures rather than Python `assert`, so its
checks remain active under `python -O`. It uses only standard-library rational
arithmetic and binary-space enumeration, with no numerical optimizer.

## 5. Scope and next questions

The theorem addresses this exact `P T M`, this local region and these output
contracts. It does not rule out a larger encoder region, a different suffix
that permits a multicolor output416, an internal native operation, or a
nonascending circuit whose extra costs are paid elsewhere. It makes no claim
that a rank-feasible capture scheme necessarily has a legal or cheap circuit.

The same proof gives a limited workspace corollary: adding finitely many
independent zero-chart registers that must return their exact original values
does not help. A returned auxiliary with a monochrome final cap joins the
excluded output set; a returned auxiliary that can be mixed appends a zero
hot row to `G`. Either way the obstructed rowspace is unchanged. This does
not cover productive auxiliaries with changed final values.

A useful next question is whether an additional productive, multicolor
output can retain the missing hot direction without consuming the full
physical saving. For example, an auxiliary final value `aux + input13`
would enlarge the hot rowspace, but this is only an algebraic escape. It
requires a complete admissible word, native interfaces, helper credits and
paid invoice; no favorable construction is supplied here.

The Schur/preconditioning motivation was informed by Cameron, Fairbairn and
Gadouleau, *Computing in matrix groups without memory*,
[arXiv:1310.6009](https://arxiv.org/abs/1310.6009), and Dumas and Grenet,
*In-place accumulation of fast multiplication formulae*,
[arXiv:2307.12712](https://arxiv.org/abs/2307.12712). Their instruction and
cost models do not supply this chart-constrained conclusion. The color-cut
lemma and source-specific obstruction are derived above; source/package
provenance and predecessor attribution are recorded separately in this
package's source manifest.
