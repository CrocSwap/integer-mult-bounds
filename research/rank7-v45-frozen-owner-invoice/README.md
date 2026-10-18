# V45 needs a changed owner assignment

Lowering all four V45 endpoints on PR2942's existing owner-bin assignment
**increases** the complete recursive moment for every positive saving parameter.
The same holds for all 16 endpoint subsets with the V45 partner frames fixed.
This is a scoped obstruction to retaining that assignment, not a defect in
PR2979, which supplies a different allocation and additional word changes.

The new result closes a specific gap between [PR2993][2993]'s local symbolic
invoice and an actual idle bill. It complements [PR2987][2987]'s analysis of
the different final pattern mix. It does not repeat the frame-only audit or
claim a new supplier, exponent or selected-frontier change.

## Exact result

The reference is PR2942's literal T74 fill, retained on scientific base main
`836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision 6.
The changed frame record is [PR2979][2979] at
`be191346391661f4d35fc0d1508d0a6029572576`.
All ten live inputs have SHA256 and Git-blob pins in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance, not live inputs.

Keep each role's call, owner replica, child and port fixed. Grant free
compaction of offsets within each bin, preserving the role order. Bill one
idle child for the complete remaining capacity, including empty bins.
This is favorable to the changed word. It does not charge movement or prove
that the changed native program can execute physically.

Both providers independently recount the V45 local difference for `k` lowered
endpoints, with all 61 V45 gate-frame edits retained:

```text
Delta_local(k) = (2-k) H1 + 10 H2 + 6 H3 - 10 H4.
```

`Hr` denotes one rank-r recursive child. There are 666 actual calls, 250 base
and 416 extra. The four helpers have ordered indices 25, 27, 41 and 43 among
the 408 live helpers. The checker derives those indices from original role
names 249, 251, 265 and 267, rather than assuming original and compact names
coincide.

For the joint change, all 2,664 freed width units land in previously full bins:

| Freed capacity per touched bin | Bins | New idle bill |
|---:|---:|---:|
| 1 | 2,370 | 2,370 H1 |
| 2 | 147 | 147 H2 |

The unchanged parent idle bill is
`17316 H1 + 5861 H3 + 6215 H5 + H14 + 27291 H48`.
All 149,184 bins, 271,728 role placements and source availability windows
are checked, including those unaffected by the change. Adding the actual idle
difference to 666 copies of the local difference gives

```text
Delta_complete(4) = 1038 H1 + 6807 H2 + 3996 H3 - 6660 H4.
```

This is a complete recursive-histogram difference under the fixed assignment.
The role counts, 86 private cleanup names, eight centres and nominal source
stock of 66,808 remain unchanged. Counting those names is not physical storage
or cleanup-semantic admission.

## Proof of the strict sign

The signed rank mass is exactly zero:

```text
1038*1 + 6807*2 + 3996*3 = 6660*4 = 26640.
```

In the retained moment, a rank-r tariff is proportional to `r^(1-a)`.
For every `a > 0` and `r < 4`, `r^(-a) > 4^(-a)`.
Replace each positive term `n_r r^(1-a)` by
`n_r r * 4^(-a)`. Every replacement strictly decreases the sum, and the
rank-mass equality makes the resulting signed sum zero. The original
complete difference is therefore strictly positive. The common normalization
`73^(a-1)/(896*74)` preserves its sign.

The checker certifies the same sign pattern and rank-mass identity separately
for every endpoint subset, including the fixed-partner zero-endpoint control.
For example, any singleton has complete difference
`1264 H1 + 6694 H2 + 3996 H3 - 6660 H4`.
No floating-point prices, approximate idle tariffs or root estimates are used.

For the usual `0 < a < 1`, splitting a bin's idle remainder into several
positive-rank children cannot lower this bill, since `x^(1-a)` is subadditive.
Thus the obstruction also covers such splits with fixed role-to-bin placement.
It does not cover moving roles between bins, changing the word's partner
frames, using different endpoint paths or changing the coverage contract.

PR2979's positive surrogate guide used a width tariff near `H48/48`.
The frozen parent fill actually produces new H1/H2 children. This result
explains why that guide cannot establish a saving on this unchanged fill.
It neither prices nor invalidates PR2979's different final allocation.

## Reproduce and evidence

The checker uses only the Python standard library and executes no predecessor
code. It writes no repository files during verification and needs no network.

```sh
python3.12 -B scripts/research_package.py --package research/rank7-v45-frozen-owner-invoice
python3.12 -O -Werror -B research/rank7-v45-frozen-owner-invoice/verify.py
python3.12 -Werror -B research/rank7-v45-frozen-owner-invoice/test_verify.py
```

`verify.py --emit` prints deterministic evidence. [RESULT.json](RESULT.json)
contains the independently recounted parent invoice, both providers' frame
profiles for every subset, complete idle and recursive histograms, touched-bin
counts and digests of the rebound rows. The default command compares fresh
evidence with that committed result. [TASK.json](TASK.json) records the scope
refinement, overlap coverage and source heads. [decisions.tsv](decisions.tsv)
records the bounded investigation.

Seven behavioral test groups check genuine source geometry and reject missing
or duplicated roles, capacity violations, unavailable source windows, unbound
providers, noncompact source prefixes, invalid frame endpoints, omitted frame
edits, unpaid idle children, false sign claims, duplicate JSON keys and corrupt
source exports. A subprocess checks the real optimized CLI. All acceptance
conditions use exceptions and remain enabled under Python `-O`.

## Limits

This proves a finite invoice obstruction for one frozen assignment. The
Clifford/native semantics, arbitrary dirty-state restoration, physical movement,
precision/tape, selected stock coefficients, full supplier and outer release,
and all-size/compiler implications were not replayed. It does not generalize
to PR2979's shipped final allocation or to all rank-seven mechanisms.

## Open next questions

The useful continuation is to join the already published changed packing and
native event evidence to an independently checked physical invoice. Start with
PR2987's actual final fill and [PR3008][3008]'s named helper/private-buffer event
inventory. The remaining native dependency closure, physical ownership and
precision costs block admission. Another unchanged-parent packing calculation
is unnecessary. This session stops at the fixed-assignment theorem.

## Credit and engineering constraints

Nick Petalas. Apache-2.0. Marius-Paul Dumitrean supplied PR2942's words/fill and
PR2979's joint mechanism. Jeremy Kothe supplied the frame/cleanup conventions;
Mason Hale and Jeremy Diviney supplied the paired-extraction chain. Ross
Richardson supplied the complementary packing audits. The source-window and
family conventions retain Tekalign's owner-checker lineage. Retain Yiyang Lu,
Dugongue, icekylinx, Sagar Thakrar, themilkman216 and the geometry/native/owner
contributors credited by the source packages. No predecessor code is copied,
modified or imported here. No independent human or formal-kernel review is claimed.

Build the Lever determined the rerunnable integer certificate. Prove It Works
required reading every actual role placement and idle bin. Test Behavior, Not
Implementation determined the semantic failure controls. Unslop shaped the prose.

Power of Ten inspection covers the four Python files. Loop bounds come from
ten authenticated inputs, 704 word slots, nine binary axes, at most 10,000
gates per section, 480 warps, 666 calls, 408 helpers, 18 idle children per
replica, 112 ports and 16 subsets. File reads stop at 16 MiB raw and 64 MiB
decoded; the immutable span cache has 4,096 entries. No recursion or dynamic
code loading is used. Source authentication runs before decoding and again
after replay. Ruff and warning-as-error execution check the new code.

Rule 3 deviation: Python allocates managed objects during the bounded recount.
The fixed domains and file/cache caps bound live state; no resident service is
introduced. A service accepting larger inputs would need fixed-capacity storage
and a separate allocation audit. Rules 8/9 deviation: `lru_cache`, the strict
JSON object hook and unittest callbacks use standard-library dispatch. Their
targets are fixed local functions; the cache is bounded and contains immutable
sets. Boundary, optimized CLI and corruption tests exercise these paths.

[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
[2987]: https://github.com/CrocSwap/integer-mult-bounds/pull/2987
[2993]: https://github.com/CrocSwap/integer-mult-bounds/pull/2993
[3008]: https://github.com/CrocSwap/integer-mult-bounds/pull/3008
