# Literal local costs and bounds

The scalar unit is the source model's real primitive tariff. A unit
complex ADD costs eight. A complex sign costs two; a double or half
costs two more when present. A monomial map count is not a finite price.
Native mass is sum r H_r. Recursive cost depends on the full histogram,
not only its mass.

Define the two shared profiles:

```text
P9 = 1392 H1 + 64 H2 + 48 H3 + 16 H9;
P8 = 1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

Both have 1520 children. Their masses are 1808 and 1792.

| Complete local word | Real scalars | Profile | Input views | Output views | Native side-map upper bound |
| --- | ---: | --- | ---: | ---: | ---: |
| Row formation, direct FULL | 11640 | P9 | 112 | 96 | 3008 |
| Same-reader line-entry reuse | 9880 | P8 | 128 | 96 | 3040 |
| Clean exchange, I entry | 8600 | P9 | 112 | 96 | 3008 |
| Clean exchange, Q entry | 8600 | P8 | 128 | 96 | 3040 |
| Clean Q inverse-adjoint or selected conjugate | 8600 | P8 | 128 | 96 | 3040 |
| A native forward or backward | 9416 | P9 | 112 | 96 | 3008 |
| A^T native forward or backward | 8936 | P9 | 112 | 96 | 3008 |
| Complete D25 fixed-reader forward or dual | 14896 | P8 | 128 | 96 | 3040 |
| Route32 raw forward or backward | 4312 | 944 H1 + 48 H3 + 64 H5 + 64 H6 | 112 | 112 | 2240 |
| Direct Fsimple or Bcustom | 2912 | 96 H1 + 128 H8 + 96 H9 | 0 | 0 | 448 |

The route32 raw word has 1120 children and mass 1792. The direct clean
word has 320 children and mass 1984. The direct word changes the old
native paths; it is not a cheaper scalar suffix with the old profile.

The D25 row also has 448 DATA maps and 672 query maps. Its complete
map-call bound is 448+224+3040+672=4384. The local rows above contain no
implicit DATA charge. The generic formation before the direct-FULL
refinement has 3040 side maps; the refinement removes the 32 identity
maps on its sixteen H9 children. H8 side maps remain charged.

The main scalar splits are:

```text
formation:        6456 retained + 1760 precode + 3424 query = 11640;
line entry:       6456 retained + 3424 query = 9880;
clean exchange:   6456 retained + 1760 source code + 384 exchange = 8600;
A native:         6456 retained + 2960 late query = 9416;
A^T native:       6952 retained + 1984 late query = 8936;
D25 reader:       6456 carrier + 8440 routed query = 14896;
direct clean:     768 self ADDs + 1760 source code + 384 exchange = 2912.
```

The separate common-frame A and A^T words each cost 3276 scalars. They
are used twice in the complete fixed-reader query. Route32's pivot code
and inverse each cost 1870; its reflection capture code and inverse each
cost 2486. These code costs are not included in its raw native bill.
The literal route32 entry adds 112 explicit Q^2 translation maps.

| Emitted word | Maximum content row one-norm | Additional binary denominator height |
| --- | ---: | ---: |
| Formation | 132 | 1 |
| Line-entry reuse | 112 | 1 |
| Clean exchange | 22 | 1 |
| Clean dual or selected conjugate | 12 | 2 |
| A native forward / backward | 70 / 22 | 1 |
| A^T native forward / backward | 30 / 62 | 1 |
| Complete D25 forward | 202 | 2 |
| Complete D25 dual | 40 | 2 |
| Route32 raw, either direction | 14 | Not reported in the native review |
| Route32 pivot code / inverse | 8 / 4 | 0 / 3 |
| Route32 reflection code / inverse | 8 / 4 | 1 / 2 |
| Direct Fsimple / Bcustom | 22 / 4 | 1 |

These are ideal content bounds at emitted operation boundaries. They do
not bound scalar primitive interiors, recursive child interiors, or the
full roundoff error. For the routed reader, the complete dual prefix has
norm 12 and its isolated late query has norm 30; the complete word reaches
40. The forward routed query reaches 202 on the stated regular cover.

All native rows preserve 416 arbitrary outside values. A scalar code on
X alone preserves the other 528 fields. Neither statement creates a
recursive parking schedule or gives productive progress to those values.
