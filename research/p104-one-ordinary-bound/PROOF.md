# One ordinary-work inequality for the PR6353 word

## Statement

Let the source word be `research/p104-native-input-lifting/WORD.json.gz` at
base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Let the supplier word be the
PR6353 payload whose SHA256 is
`0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928`.
The two words differ in `final`, `frames` and `program`. The 104 ports are
unchanged, and port 0 remains 11. Frames `0..1093` are unchanged. Frame 1094
is `[7, 9, 35, 66, 400]`. The nine changed public finals are

| Roles | New frame |
|---:|---:|
| 226, 297, 393, 484, 485, 707 | 246 |
| 361, 451 | 245 |
| 703 | 1094 |

## Charge walk

For a program event, the allowance used here is:

- `MOVE` from frame `a` to frame `b` contributes one paid job of rank
  `|dim b - dim a|`, where dimension is the length of the stored basis.
- `INIT` and `CLEAR` each contribute 2 to the scalar allowance. An `INIT`
  opens an owned label and a `CLEAR` closes it. The lifetime count is the
  number of `INIT` events. The peak is the maximum number of labels open
  at once.
- `SCALE` by a dyadic unit `q = ± 2^k` contributes
  `2(|bitlength(numerator) - bitlength(denominator)| + 1_{q<0})`.
- `ADD` and `COPY` by a nonzero dyadic `q = n/d` contribute
  `2(3 + bitlength(|n|) - 1 + popcount(|n|) + bitlength(d) - 1)`.

A second walk buckets those same increments by opcode and sums the buckets.
The two walks agree on both words. A `SCALE` by `3` is rejected.

Helper rank of a non-main public role is `dim(final) - dim(initial)`. The
main roles are the 104 live ports and those ports shifted by 112.

## Measured inventory

| Quantity | Source | Supplier |
|---|---:|---:|
| Scalar allowance | 127088 | 128694 |
| Paid calls | 3450 | 3456 |
| Paid rank mass | 5946 | 5934 |
| Helper rank mass | 4226 | 4214 |
| Helper count | 562 | 562 |
| Owned lifetimes | 32 | 41 |
| Peak open labels | 13 | 13 |

The paid difference is `14 H1 - 4 H2 - 3 H3 + 4 H4 - 5 H5`.
The productive difference is `H5 + 8 H8 - 9 H9`.
The nine extra lifetimes are one additional `INIT`/`CLEAR` pair on each
label `770, 771, ..., 778`. The set of owned labels stays inside
`770..798`, and `owned_fields` stays 29.

## The inequality

Write `P` for the supplier’s paid-call count, `L` for its lifetime count,
`S` for its scalar allowance, `n = 770` public roles and `m = 104` live
ports. The declared local route allowance is

```text
1000 * (P + 2(n - 2m) + 2m + 4m + 4L)
  = 1000 * (3456 + 1124 + 208 + 416 + 164)
  = 5368000.
```

The local ordinary total is `S + 5368000 = 5496694`. This is strictly less
than `10^7`. The slack is `4503306`. Adding that slack makes the comparison
fail, so the inequality is strict.

The declared complete raw expression, on a caller with `E` events, is

```text
19*10^7 + 16*1664 + 34*104*E + 34*104*(26 + 1000).
```

The pinned caller has `E = 353`, `34` roles and `19` stages. The value is
`194902768`, strictly less than `10^9`. This expression charges each of the
19 local calls at the full `10^7` cap. It reads the caller event count.
The supplier program has `17657` events; substituting that length produces
`256089712`, which is not the published figure.

## Boundary

The walk counts the declared allowance. It does not replay scalar rows, native
phases, absolute-phase contacts, or the 19-fold tree invoice. Those
histograms and the scalar endpoints agree with the figures already stated for
this word; the recursive moment margin remains the separate recount in
PR6359. Compiler thresholds, the 54 outer predicates, LOCAL stages 2 through
19, and any new kappa remain open. The five framework assumptions remain.
Selected kappa stays `781451/250000000`.
