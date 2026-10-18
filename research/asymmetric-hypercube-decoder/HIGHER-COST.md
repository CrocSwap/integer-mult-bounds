# What the higher-target witnesses cost, and what remains unpriced

The new cube mechanism changes the support geometry of simultaneous decoding.
At `q=2,k>=4`, a three-dimensional subcode on fourteen ports beats every span
of three minimum stars, whose union has at least fifteen ports. The ambient proper-star codes have first
five generalized weights `(6,11,14,15,16)`, so three, four, and five
selectable targets share the same optimal eleven-deletion count.

This is a scalar observation-span result. It is not a supplier improvement.
We have not found a complete physical supplier interface that turns the
support improvement into a favorable recursive invoice.

## Explicit scalar accounting

Use the selector `M=m_fixed(1+z_a)(1+z_b)` from
[HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md). Choose the basis rows

```text
M*x_1, M*x_2, M*x_3, M*x_4, M*x_4-opposite.
```

The last two rows sum to M on the selected cube. Each row expands into nine
nonempty proper stars; their degrees are at most `k-1`. Thus no free empty
star is needed, even at k=4. The first r rows give the r-target witness.
The exact information set and basis change are committed in
[CUBE-RESULTS.json](CUBE-RESULTS.json).

For these particular information sets, evaluate each distinct star total
independently on the surviving family, evaluate each cached basis row once,
and then XOR cached rows to obtain the unit decoders. The following are
ordinary binary scalar additions, assuming input access and cached storage
are available. They are explicit costs of this naive schedule, not minima.

| Targets r | Distinct star totals | Input contributions to those totals | XORs forming totals | XORs forming basis rows | XORs changing basis | Total scalar XORs |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 27 | 583 | 556 | 24 | 4 | 584 |
| 4 | 36 | 781 | 745 | 32 | 5 | 782 |
| 5 | 45 | 977 | 932 | 40 | 9 | 981 |

The table is the same for every checked `k=4,...,8`, because fixing an
additional signed coordinate lifts the identical residual six-pair problem.
The mathematical lifting argument extends that fact to every k>=4.
Without cached basis-row reuse, directly summing the expanded unit decoders
would take 60, 77, or 121 XORs after the star totals are available. Neither
schedule is asserted to be XOR-optimal, and the counts do not price copying
or preserving mutable operands. An even more favorable model could treat
existing star totals as supplied; that still leaves their upstream invoice
and interfaces to establish.

## Why no κ follows

A usable multiplication supplier would need an explicit physical word and
recursive interfaces that account for all of the following:

- Producing each required star total from permitted sources, including access
  multiplicity and any recursive children that supply those totals.
- Copying or preserving operands, their readable frames, and their live widths.
- Restoring helpers and sources, including any work hidden by a cached sum.
- Hosting the chosen deletion pattern and targets in a complete supplier, then
  checking the other supplier and all assembly constraints.

The present row identities do not provide those objects or prove they can be
free. Replacing the current supplier's invoice with the deletion count eleven
would therefore be invalid. The scalar counts above also cannot be inserted
as physical gate counts in the selected construction's cost model.

The current selected frontier remains the maintainer-reviewed conditional
PR799 construction, with PR741 and PR589; the exact context snapshot is in
[HIGHER-CLAIM.json](HIGHER-CLAIM.json). We make no claim to have re-audited that
unrelated physical construction. The contribution here is the exact new
hierarchy, its exceptional optimizer, and reproducible decoder certificates.

Prepared by Sam Sung with substantial OpenAI Codex assistance; Apache-2.0.
