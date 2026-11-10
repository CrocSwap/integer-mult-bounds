# Seven-source connectors must repeat a normalized source axis

This contribution was produced by Nick Petalas. Apache-2.0.

A universal seven-source connector with four arbitrary dirty roots cannot
assign seven distinct normalized axes to its twice-called source maps. This
is a scoped obstruction with an exhaustive finite certificate. It excludes
an axis-diversity route toward Mason Hale's open transfer-cost question,
without changing the selected frontier or kappa.

The complete reduced domain contains thirty affine-cube codes and 5,040
source orders. Every one of the 151,200 pairs misses at least 22 of its 57
mandatory masks. The minimum deficit 22 is attained by four pairs. It is
sharp for this necessary-condition census, not an exact total-output capacity.
If the all-ones output is supplied, at most 105 nonzero masks pass the test.

[PROOF.md](PROOF.md) gives the arbitrary-input reduction, complete domain and
an attaining deficit witness. The program grants arbitrarily many scalar
binary root frames and every physical read port, so unpaid frame restrictions
do not cause the exclusion. Every source and output map must occur exactly
twice; sources and roots restore and outputs remain unobserved.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/seven-source-distinct-axis-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/seven-source-distinct-axis-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/seven-source-distinct-axis-obstruction --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. Direct replay
prints a generated JSON receipt with status
`PASS_SEVEN_SOURCE_DISTINCT_AXIS_OBSTRUCTION`, the full deficit histogram,
minimum witness, census digest and hashes of every package file. It writes
nothing. Normal and optimized modes are registered.

Two separately implemented code generators, mandatory-set constructions and
word-difference engines agree on every missing-mask bitset. The secondary
code generator examines all 11,811 three-dimensional binary RREF spaces.
Controls cover fourteen cyclic rotations, all 21 coordinate transpositions,
the repeated-axis star positive case, two invalid-word rejections and four
false-variant boundaries.
The two cited main-tree documents are hash authenticated before enumeration.
These are two implementations by one contributor, not independent review.

The current selected binding control and the card's 945-pairing positive
control pass. No predecessor scientific census is replayed as this result.

## Source, scope and credit

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8;
selected conditional kappa remains 0.003125804. Exact document pins are in
[SOURCES.json](SOURCES.json). The original card and changed scope are in
[TASK.json](TASK.json).

- Mason Hale / [PR2282](https://github.com/CrocSwap/integer-mult-bounds/pull/2282)
  poses the four-root transfer question and proves the seven-source root minimum.
- Arham Tahir / [PR2795](https://github.com/CrocSwap/integer-mult-bounds/pull/2795)
  supplies the code formulation, mandatory masks and all-ones interval reduction.
  Its eight-source exclusion and seven-source three-root calibration are different
  finite domains from the four-root distinct-axis domain here.
- conorholds / [PR2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182)
  supplies normalized axes, the dirty-root contract and the 56-X attaining star.
  Ross Richardson / PR934/943, Douglas Colkitt / PR1185 and their retained
  connector, common-factor and compiler lineage retain credit.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372499)
aimed for fewer transfers. The [finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372766)
records the delivered narrower obstruction. No shorter word or global transfer
minimum was established. Construction search stopped at this first proved step.

The main/merged/open searches used the source object, distinct normalized axes,
affine-cube codes and mandatory-mask deficits. The overlap cache covered 550
open PRs and 6,574 Discussion records; sparse local notes and unpublished work
remain limits. No global literature-priority claim is made for classical
binary code geometry or the credited reductions.

## Open next questions

- Can a repeated-axis four-root program use fewer than 56 paid XORs while
  retaining all minimum map incidences? First choose one repeated-axis code
  and emit its complete frame/source/readout itinerary. A cheaper legal word
  and its complete physical port bill remain missing.
- Can a structural argument replace this 151,200-case distinct-axis census?
  Start with the 57 mandatory supports and a double-permutation source word.
  A uniform interval argument, rather than sampled orders, is needed.

No new supplier, physical caller, complete multiplication theorem, independent
human review or formal-kernel proof is claimed. Native, compiler, ownership,
stock, precision/tape and analytic transfer obligations remain open.

## Implementation bounds

Every loop is bounded by a fixed finite domain: seven coordinates, sixteen
codewords, 128 masks, 5,040 orders, thirty codes or the 11,811 RREF spaces.
Functions are under sixty lines; checks use exceptions and survive `-O`.
There is no recursion, solver, runtime network call or generated executable.
The two census lists have exactly 151,200 integers of at most 128 bits each.

Power-of-Ten rule 3 has a managed-runtime deviation for Python allocation in
these bounded lists, sets and exact integers. The interpreter allocator is not
inspected. Fixed domain sizes bound live mathematical storage; both lists are
released on process exit. A fixed-capacity implementation would be needed
before reuse in a long-lived service. Warning-strict normal and optimized
commands provide the applicable interpreted-code diagnostics.
