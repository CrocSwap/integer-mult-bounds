# SOURCE87 parent fibres

The selected conditional exponent stays `60403/20000000`. This note does not
admit the R437 carrier and does not change that exponent.

## Pinned call

`research/r437-carrier-integration/physical.py` evaluates
`Layout.child_extents` on the SOURCE87 good plan with

```text
columns = 1, parent_size = 64, q = 3,
before = 2, gap = 3, suffix = 2,
first = 0, second = 126, width = 2.
```

The same file requires the returned triple to be `(2, 3 * 3^124, 2)` and
requires `B * G * S * 3^4 = 12 * 3^128`. The executed child is the 972-bit
fibre `2 * 3 * 2 * 3^4`. The unused-row count on that handoff is the literal
`9475`, and the displayed parent volume is `9475 * 12 * 3^128`. Both arms use
these arguments. The plan is good of rank 2.

`layout.py` multiplies the external gap into exactly one of the three
spectator regions: the prefix when the first chunk starts at or after
`parent_size`, the suffix when the second chunk ends at or before
`parent_size`, and the middle otherwise. `plan.py` sets the plan dimension
`m` to the low-projector length and requires `1 <= rank < m <= 64`. A good
plan stores that length as its dimension. `Layout` sets

```text
core = columns * m, remaining = parent_size - core,
extra = 2 * remaining, total = 2 * parent_size.
```

A position below `core` stays put. A position at or above `core` moves by
`extra`. At ring precision `w`, each address step scales a count by `q^w`.
The published triple uses powers of `3`, so the fixture atom size is `3`.
That is `w = 1`. The same triple is not the `w = 2` value.

## Dimension 64

Assume `w = 1` and the call above. For `m = 64`, `core = 64`, `extra = 0`
and `total = 128`, so the physical map is the identity. The chunks are the
address intervals `[0, 2)` and `[126, 128)`. They are ordered, disjoint,
inside the body, contiguous, and on opposite sides of the external gap at
`64`. The prefix exponent is `0`, the middle exponent is `124`, and the
suffix exponent is `0`. The gap falls in the middle, once. Therefore

```text
B = 2, G = 3 * 3^124 = 3^125, S = 2.
```

The product test in the caller becomes

```text
2 * 3^125 * 2 * 3^4 = 12 * 3^128.
```

For every `m` with `1 <= m <= 63`, the same call either violates chunk
placement or returns a different triple. In particular `m = 63` pushes the
second chunk to address `128` and past `total = 128`. Thus, among the
dimensions `plan.py` allows, the published assertion holds exactly at
`m = 64`. The rank-2 constraint `2 < m` is compatible with that value.

## Fibre count

The executed fibre has volume

```text
972 = 2 * 3 * 2 * 3^4.
```

The parent volume displayed by the caller is `9475 * 12 * 3^128`. Hence the
parent packet is exactly

```text
M = 9475 * 3^124
```

copies of that fibre:

```text
M * 972 = 9475 * 12 * 3^128.
```

The factor `3^124` is `G / gap`. The factor `9475` is the pinned unused-row
literal. It is also `269241600 / 28416`, the integer appearing in the
carrier's stock formula, but this note does not re-execute stock admission.
A schedule that performs one common per-fibre action vector `v` on every
copy, and nothing else, pays `M v` on this entry.

## C and D

The compiler receipt gives both arms two SOURCE87 records. Each record has
rank `2` and the same chart digest. The four request identifiers differ, so
these are not the same request objects. The extent arguments in `physical.py`
do not depend on the arm. The leaf-scan bill of this entry is therefore the
same number `M v` on C and on D, and its difference is zero.

The same receipt's request profile changes by

```text
rank 1: +288, rank 2: -576, rank 3: +288,
```

and by zero at every other recorded rank. The rank-mass change is

```text
1*288 + 2*(-576) + 3*288 = 0,
```

and both arms have rank mass `1808352`. Net request count is also unchanged.
The rank-2 count moves by `-576`, far more than the two SOURCE87 records, so
other requests still differ. Equality of this entry is not equality of the
sum over the profile.

## What this does not price

Inter-fibre gather, routing, parking, blank-return, source-table
construction, and the leaf scan of every request outside this entry remain
unpriced. The zero difference removes one term from the integration's
whole-construction comparison. It does not show that the comparison holds,
and it does not produce a new selected exponent.
