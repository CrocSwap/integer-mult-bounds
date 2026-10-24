# Source geometry of the eight structured centre queries

All eight structured centre rows have source directions of binary rank
seven. The missing six rank-seven captures in the retained source word
are not forced to have rank eight by their source support alone.
There are only four distinct rank-seven support spaces. Each contains
the supports of two centre rows.

This note uses the actual port directions from the fresh native packet
and the actual centre rows from the structured response packet. The
checker pins both decompressed payloads. It does not change either input.

Let `q_p` be the source direction of port `p`. For centre row `K_j`, put

```text
U_j = span_F2 {q_p : K_jp != 0}.
```

Each row has twelve nonzero coefficients. Direct binary elimination gives
the following complete lists of nonzero vectors in the annihilators.
The integers encode binary vectors in the pinned nine-axis chart.

| Centre rows | Nonzero annihilator vectors | Support rank |
| --- | --- | ---: |
| 0, 5 | 7, 42, 45 | 7 |
| 1, 6 | 25, 45, 52 | 7 |
| 2, 7 | 45, 82, 127 | 7 |
| 3, 4 | 45, 76, 97 | 7 |

Different spaces in this table intersect in rank six. Their sum is the
common rank-eight hyperplane `45^perp`. The intersection of all four
spaces has rank five.

Each of the 48 physical ports occurs in exactly two centre rows. The
incidence graph on the eight rows is the complete four-partite graph
with parts `{0,5}`, `{1,6}`, `{2,7}`, and `{3,4}`. Each graph edge has
two physical ports. Thus two centres have a common source port exactly
when their support spaces are different.

## A limit for a specific direct capture schedule

Assume all of the following for a proposed source schedule:

1. Each original source value has one carrier. Its frame subspaces form
   an increasing chain.
2. A direct capture of `K_j x` reads the unwarped source values with their
   stated scalar coefficients in a common subspace that contains `U_j`.
3. There is one such capture per centre row. No stored partial query,
   additional carrier, or operator-valued source code supplies a term.

A rank-seven capture of row `j` must then use `U_j` itself. If rows `i`
and `j` share a port, that port's increasing chain would have to contain
both `U_i` and `U_j`. They are distinct rank-seven spaces and neither
contains the other. This is impossible in an increasing chain.

The rank-seven captured rows must therefore form an independent set in
the incidence graph. The largest such set has size two. Its four
possible values are precisely the pairs in the table. All eight query
supports have rank seven, so under the stated assumptions the sum of
the eight capture ranks is at least

```text
2*7 + 6*8 = 62.
```

This is a conditional lower bound, not a construction at rank 62. In
particular, this note does not emit the six rank-eight captures or prove
their scalar cost. The retained source word's two known rank-seven
captures use rows 0 and 5, which attain the largest possible set in this
restricted model.

A changed source code, another carrier, partial queries, or a path that
does not increase monotonically is outside the proof. A native monomial
frame change can change logical source values. It must not be counted
as an unwarped step under assumption 1 without a separate proof.

## Exact check

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/root/check_centre_support_geometry_20261018.py
```

Expected output is `PASS_CENTRE_SUPPORT_GEOMETRY`. The checker computes
all annihilators by exhaustive enumeration of the 511 nonzero binary
vectors. It checks the 48 source incidences and all 256 vertex subsets.
All operations are exact. The native and physical phase claims remain
in their separate packets. Independent review of this conditional
schedule consequence is recorded separately.

This AI-assisted work uses the structured centre rows from the
controller-followthrough lane and the actual port chart from the
history-encoding lane. It makes no supplier or kappa claim.
