# P112 A4 shortening and two profile exclusions

Over any characteristic-zero field, independent pieces consisting of a
common small-support family and five support-twenty endpoints meet the
P112 evaluation code in dimension at most three when the common support
has at most 26 coordinates. The proof normalizes an A4 simplex and gives
`102>100` endpoint support incidences.

Deleting two unrestricted pieces then excludes the actual historical
TWOSIDE `(6,3)` profiles `3,6^6,7^2` and `4,5,6^5,7^2`. Their contradictions
are **106>100** and **114>100**. [PROOF.md](PROOF.md) gives the quotient,
deleted-dimension argument and complete geometric dependencies.

The change from recent A5 results is substantive: five endpoints require
four surviving code dimensions, so two arbitrary pieces can be deleted
from these nine-piece profiles. No larger shortening range or additional
A5 result is claimed.

## Reproduce

Python 3.12+, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p112-a4-shortening --check-only
python3.12 -B scripts/research_package.py --package research/p112-a4-shortening
```

Set `TMPDIR` to your external scratch directory to keep runner and test
outputs outside the checkout. Direct commands also work in a Git-free
export containing this package and its two `VERIFY.json` inputs:

```sh
python3.12 -W error -B research/p112-a4-shortening/verify.py
python3.12 -O -W error -B research/p112-a4-shortening/test_verify.py
```

Expected marker:

```
PASS_A4_SHORTENING support=26 exclusions=2 margins=6,14 A4_orbits=1 flats=4097782
```

`verify.py --output /NEW/EXTERNAL/RESULT.json` reconstructs the receipt and
refuses an existing output or an output inside the checkout. The checked
[RESULT.json](RESULT.json) contains exact finite evidence, not timings or
compressed-container hashes. [CHECKS.json](CHECKS.json) records validation
and its limits.

## Evidence and scope

The replay checks all A4 stabilizer extension orbits, 4,097,782 binary
five-/six-flats, 7,140 root planes, 960 simple reflections and the original
24-cell table. A separate root description, literal common-shift oracle
and deletion dynamic program corroborate the A4 spectrum. Ten behavioral
groups test lost code dimensions, malformed stars, source/receipt
corruption, old cover budgets and the losing support27 boundary.

This is an author-checked proof with exact finite evidence, not independent
human or proof-kernel review. The standard Weyl-chamber theorem and the
original decoder reduction remain dependencies. Full C5, `C(P112)>=64`,
supplier admission, physical consumer/restoration and a new kappa remain
open or unchanged. No selected result is edited.

## Source credit and overlap

Nick Petalas. Apache-2.0. DreamingOfClouds/PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` supplies TWOSIDE, its original
filters and the retained E8/P112 decoder lineage, including joaqcoo's model.
The copied geometry is unchanged from Nick Petalas/PR3164 and its later
retention in PR3173. PR3175 supplies the stabilizer-subgroup support-spectrum
method. PR3195/3197 supply earlier one-piece deletion applications;
PR3203/3205 supply the separate six-endpoint shortening contracts.

[SOURCES.json](SOURCES.json) pins live inputs and retained bytes at canonical
main `463113d675af7410ac91d53a4fed51ec6494eb9a`. The original geometry header
and source credit are retained in `a4_geometry.py`. No predecessor package
or frozen source is modified. Development used substantial automated
assistance in proof drafting and checks.

The canonical investigation is [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156).
The entry overlap snapshot covered 253 open PRs, 2,630 closed/merged PRs and
2,017 Discussion records with complete pagination. It found no exact-profile
or A4-simplex result. That search does not prove novelty. [TASK.json](TASK.json)
records the changed scope and final freshness check.

## Open next questions

Bind another actual remaining profile to its dimension after deleting
pieces, common support and endpoint capacities before extending any
census. At support27 the relaxed A4 bound equals 100. Retaining the actual
orthogonal frame or actual support flats may strengthen it, but a failed
sufficient bound is not a construction. A new extension needs a named
caller that is not already excluded. The structured next question and
blocker are in [TASK.json](TASK.json).
