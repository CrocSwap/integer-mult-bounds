# Exact R439 helper matching with a one-ADD precision gap

**Finite bit-circuit construction and exact restricted-class cost bound.**
The complete word uses **11,949 ADDs**, saving **31 beyond PR926** while
reducing both positive prefix maxima. An integer matching certificate proves
an **11,948-ADD floor** for disjoint helper pairs around the frozen PR915
target basis. The new circuit is within one ADD of that floor and satisfies
the existing precision ceilings. Whether an attaining optimum also meets
those ceilings remains open. No new κ is claimed.

| Quantity | Selected PR589 | PR915 | PR926 | New candidate | Floor calibration |
|---|---:|---:|---:|---:|---:|
| D ADDs | 18,085 | 6,988 | 5,760 | 5,729 | 5,728 |
| Complete ADDs | 24,305 | 13,208 | 11,980 | 11,949 | 11,948 |
| Native records | 27,234 | 16,137 | 14,909 | 14,878 | 14,877 |
| Forward bound F | 49,347 | 49,347 | 71,907 | 70,083 | 73,603 |
| Reverse bound B | 1,113,070 | 9,534,616 | 10,562,318 | 10,548,832 | 10,518,760 |
| Local payload bits | 93 | 100 | 102 | 101 | 102 |
| Nine-stage prefix bits | 177 | 189 | 192 | 192 | **193: rejected** |

The candidate has 199 disjoint helper pairs. Its complete D price is
**199 + 306 + 4,719 + 306 + 199 = 5,729 ADDs**. The remaining 6,220 ADDs,
all 439 helpers, nine rank-seven copied totals, every register's MOVE path,
all COPY/ERASE records and paid rank mass 5,129 are retained. Only D changes.
The complete saving against selected PR589 is 12,356 ADDs.

## Reproduce

The default verifier needs Python 3.12+, C++17 and Boost headers, with no
matching solver or network access:

```sh
python3 -I -B research/r439-helper-matching/verify.py
python3 -I -B research/r439-helper-matching/test_package.py
```

Set `BOOST_INCLUDE` or `CXX` for nonstandard installations. Expected final line:

```text
PASS_R439_HELPER_MATCHING: ADDs 11,980 -> 11,949; fixed-class floor 11,948; 601 budgeted words; one-ADD gap; no new kappa
```

`--output NEW_DIRECTORY` retains generated words, native records, commands and
logs. `--receipt NEW_FILE` saves the complete report; existing destinations
are refused. `--source-root ROOT` accepts the minimal closure enumerated by
[SOURCES.json](SOURCES.json). The entire report is compared with
[EXPECTED.json](EXPECTED.json). Regenerated gzip files are compared by full
canonical JSON payload. Optimized Python is supported; inherited subprocesses
run with assertions enabled.

Optional discovery reproduction uses NetworkX 3.6.1 and checks the exact
matching implementation source hash before running:

```sh
python3 -I -B research/r439-helper-matching/nominate.py --output /tmp/r439-new-nomination
```

Its expected marker is `PASS_R439_MATCHING_NOMINATION: three optima; 598
deletions; 601 priced words`. The solver nominates witnesses and dual prices;
the default verifier establishes the bound using integer arithmetic alone.

## What is certified

For the frozen 111 by 439 matrix R = EK from PR915, pairing helpers a and b
changes column b by column a and costs two helper ADDs. Its net saving is
`weight(R[:,b]) - weight(R[:,b] XOR R[:,a]) - 2`. Disjointness makes these
savings additive. Choosing the better orientation gives an undirected
maximum-weight matching problem with 439 vertices and 1,885 positive edges.

The independent checker recomputes both orientations of **all 96,141
unordered pairs** using sets. It verifies 439 nonnegative integer vertex
prices and 19 positive prices on odd vertex sets, of sizes three through
seven. Every edge's doubled saving is bounded by its endpoint prices plus
the prices of odd sets containing both endpoints. Their total matching
upper bound is 2,520 in doubled units. An explicit matching saves 1,260,
giving equality and the exact complete-word floor **13,208 - 1,260 = 11,948**.
[PROOF.md](PROOF.md) gives the elementary sum-of-inequalities argument.

The class fixes E, the non-D word, direct middle-matrix injections, and
disjoint helper transvections with both preparation and restoration paid.
It excludes changing E, overlapping helper shears, general XOR synthesis,
other frame schedules and cross-package composition. The floor ignores
precision. All three nominated optima fail the 192-bit nine-stage ceiling;
that does **not** show every optimum fails it. The precision-constrained
minimum in this class is either **11,948 or 11,949**.

## Bounded nomination and precision

OS assignment seed **4** selected this task from the three candidates in
[CLAIM.json](CLAIM.json). Three matching nominations are retained:
lexicographic insertion, seed-4 shuffled insertion, and the same shuffled
graph with a secondary objective reducing helper influence on one forward
coordinate. Each attains the certified arithmetic floor. The secondary
objective is a discovery proxy; no precision-optimality claim is made for it.

The declared search then checks every single-pair deletion of those three
matchings: **598 deletions and 601 complete words**, including the optima.
Seventeen meet both caps. Exact cost, then prefix bits, F, B and stable
nomination/deletion indices break ties. The selected circuit deletes helper
pair `(428, 150)` from the third optimum, paying one extra ADD overall and
reducing its forward maximum from 72,459 to 70,083. This stops the search;
there are no unreported restarts or broader constrained-optimality claim.

Every complete alternative is reconstructed and its positive bounds replayed
in both directions, including all copies and erasures: **14,390,692 literal
instructions**. The candidate satisfies

```text
64 F^3 B^2 = 2451471101600792727738016530432 < 2^104
2^18 F^5 B^4 = 5488085212775758317051376589272999430811861761916709896192 < 2^192
```

The nine-stage estimate uses about **87.43%** of its ceiling, versus 99.925%
for PR926. The source formula and its 18-bridge exponent are checked, and
the original 177-bit estimate and 192-bit charge are reproduced. This does
not recompute any other global invoice allocation.

## Circuit evidence and remaining integration

The generic two-sided construction applies H to helpers, E to targets,
injects E K H inverse, then restores E and H. Its complete boundary is
`(x,y,s) -> (x,y+Ks,s)` for arbitrary dirty helpers and targets. The verifier
checks all 48,729 coefficients of the four-term expansion, including 7,343
nonzero mixed-term entries, and all 661 input columns in both D directions
for all five words. The original full E8/frame/endpoint checks also pass.

Fresh unchanged C++ 5/9/11-stage checks cover 883/1,327/1,549 formal columns
per word and reject all 240 omitted-bridge controls. The floor calibration
passes these local 104-bit checks but fails the separately bound 192-bit
nine-stage invoice expression. Nineteen local controls cover dual prices,
disjointness, dirty preparation/restoration, mixed terms, illegal access,
undercharging and exact ceiling equality. A neutral helper pair is accepted
and charged two ADDs. Eight package tests cover pins, strict JSON, receipts,
output preservation and recompression.

The original syntactic H2 and literal K extraction remain false for all
four changed words; those predicates are unchanged. All other H1/H3/H4/H5
predicates and source conclusions pass. Integration still needs acceptance
of the semantic D-boundary contract, changed whole-hosted emission and audit,
complete finite/precision invoices, and outer assembly against the selected
complex supplier. The common-label realization and analytic assumptions
remain inherited. This finite result is not a proof of the full multiplication
theorem or a measured runtime improvement.

## Sources and credit

Research base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Publication base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
Selected PR589: `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
Frozen PR915: `e9daefe320a0043000bd9746664ed02c3287d056`.
Greedy comparator PR926: `0f216a345c37bc71cc0e22030ef11ec31b26a69e`.
Main advanced during validation to the reviewed PR890 frontier,
conditional κ = 0.001661957774647029, retaining PR589. All 14 consumed
source files are byte-identical after the rebase. This contribution adds
only its research package; it does not change that selected result or claim
credit for the intervening eighteen-PR integration.

**Sagar Thakrar's PR716/817** supply the prior exact fixed-basis pairing and
vertex-price certificate approach; the PR817 README is retained at
`3147cac35c659152d36db1e0e60b9ce4b152c008`. This result concerns a different
R439 helper graph and includes odd-set prices, an explicit budget failure
and a one-ADD feasible gap. **Scott Woolsey Biggart's PR733**, **Greer
Guthrie's PR694**, **Mikhail R. Gadelha's PR686**, **commdata2338's PR794**,
and the earlier target-basis lineage retain credit through the parent notices.
**DreamingOfClouds**, **eumemic** and the native verification contributors
retain the original source notices. See [NOTICE.md](NOTICE.md).

Prepared for **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance** in research, implementation, proof, verification and packaging.
Apache-2.0; no independent human review is claimed.
