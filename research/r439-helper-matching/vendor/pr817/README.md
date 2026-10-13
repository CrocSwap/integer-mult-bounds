# An exact target-pair optimum for the composed R420 word

This is a finite bit-circuit improvement and a restricted optimality certificate.
It replaces the greedy target matching in Alluri's pending PR681 composition
with 58 pairs that attain the exact optimum for that matching class.

The complete local word falls from **18,378 to 18,362 binary ADDs**. Both positive
prefix maxima remain exactly **253,149 forward and 4,334,338 reverse**. The
payload bound remains
`64 * 253149^3 * 4334338^2 = 19505369118995241654063407203584 < 2^104`.
There is **no new kappa** and no global circuit-optimality claim.

The new optimum saves **eight ADDs beyond PR733's existing pairing applied to
the same PR681 body**, whose complete cost is 18,370. The 16-ADD comparison is
against the actually published PR681 word, which uses a different greedy
matching. Both baselines are explicit in the verifier.

The main contribution is the closed optimization gap. The fixed PR694 helper
basis permits at most **1,442** further ADD savings from disjoint target-pair
substitutions. The two pending greedy constructions attain 1,426 and 1,434.
`OPTIMUM.json` supplies an attaining matching and 120 nonnegative integer
prices. A solver-free checker verifies all 7,140 edge inequalities and equality
of the primal and dual totals. A separate column-incidence implementation
checks the same certificate without importing the first checker.

## Exact comparisons

All figures count preparation, helper reads, target mixing and restoration.
These are counts of scalar operations, not measured multiplication runtimes.

| Construction | D ADDs | Complete local ADDs | Local payload bits |
| --- | ---: | ---: | ---: |
| Selected PR543 R420 | 19,922 | 26,916 | 100 |
| PR694 helper pairs | 12,988 | 19,982 | 102 |
| PR733 two-sided composition | 11,554 | 18,548 | 103 |
| PR681 composed word | 11,562 | 18,378 | 104 |
| PR733's existing matching on the same PR681 body | 11,554 | 18,370 | 104 |
| This matching on the PR681 body | 11,546 | 18,362 | 104 |

The improvement over the actually published PR681 word is **16**; the gain
beyond the strongest prior fixed-KQ matching on the same body is **eight**.
The 8,554 figure is the cumulative reduction
from PR543 and includes all predecessors. Applying the same matching to PR733's
unchanged body gives a local count of 18,540, only eight below that predecessor.
The submitted native and hosted replay uses the PR681 body. No pending selected
frontier proposal is promoted or displaced.
The 18,370 same-body comparator is reconstructed from PR733's pinned 57-pair
recipe, with the identical helper-recipe hash, exact full endpoints, frame
paths and both prefix bounds checked. It has not received a separate third
hosted replay; the fresh native/hosted runs compare published PR681 with the
submitted word.

Fresh hosted replay gives **6,144,768 -> 6,140,160 emitted local-invocation
events**, a further 4,608 reduction across 288 expanded calls. This counter
excludes separately charged bridge and schedule work, including 69,120 bridge
ADDs. Those charges are unchanged; no complete-machine instruction total is
claimed. Both versions need 196 raw prefix bits,
charged at **256**, and 432 two-level bits, charged at **512**. Those are
PR681's enlarged charges; this result does not recover the selected word's
192-bit prefix allocation.

The final overlap refresh through PR799 found
[PR794](https://github.com/CrocSwap/integer-mult-bounds/pull/794) at
`6be7364e0245c5a1c931cb1c43b3da991b755850`. Its successive target-basis
factorization reports 19,037 local ADDs with a **192-bit** hosted prefix charge.
That is a different operation-count/precision tradeoff and a larger target
circuit class. This certificate does not supersede it. PR789/790 change other
phase-B blocks; they are not composed here. PR799's larger conditional kappa
uses different complex and bit suppliers and is outside this fixed R420 class.

The PR681 baseline is reconstructed from its exact component recipes. Its
entire local bit receipt, including the canonical word, scalar stream, native
record digest, both prefix maxima and the complete paid profile, must equal
the original committed PR681 receipt before this checker accepts the comparison.

## Reproduce

From the repository root, Python 3.10 or later with the standard library:

```sh
python3 -I -B research/r420-optimal-composed-pairs/verify.py
python3 -I -B research/r420-optimal-composed-pairs/independent_check.py
```

Expected final lines:

```text
PASS_R420_OPTIMAL_COMPOSED_PAIRS optimum=1442 pairs=58 edges=7140 ADDs=18378->18362 payload_bits=104 columns=660 controls=13 no_new_kappa
PASS_R420_COLUMN_MATCHING optimum=1442 coefficients=50400 edges=7140 boolean_columns=540 D_ADDs=11546 controls=4
```

`--out /absolute/fresh/directory` retains both words, original-exporter records
and `LOCAL.json`. Existing output directories are refused. Normal commands
compare the entire deterministic receipt with `CERTIFICATE.json`. The authoring
option `--record /fresh/file.json` writes a candidate receipt and deliberately
does not print a certificate PASS.

For fresh unchanged C++17/Boost cohort checks, append `--native`. For the complete
nine-stage parent, hosted and invoice replay, use:

```sh
BOOST_INCLUDE=/directory/containing/boost python3 -I -B research/r420-optimal-composed-pairs/verify.py --hosted --out /absolute/fresh/output
```

The hosted command also needs NumPy, SciPy and SymPy, as the retained PR543 chain
does. `native.py` and `hosted.py` are byte-for-byte PR681 drivers, credited there
to Alluri and Ali Romman. They compile the original checkers and consume the
actual new word. They do not substitute stored predecessor outputs.
The caller compares every deterministic native/hosted receipt field with the
shipped receipts, excluding only runtime seconds. It also rejects a missing
helper restoration with each of the three native column checkers. The hosted
driver's PR484 outer calculation is a historical arithmetic control, not a
fresh selected PR626 complex-supplier or outer-assembly replay.

## The exact class and proof

Write the accepted helper-to-target matrix as `K`. Fix all 201 oriented,
disjoint helper pairs from Greer Guthrie's PR694 recipe. Their temporary helper
change is `Q`, with `Q^-1 = Q`. The matrix read during the middle becomes
`M = KQ`. Preparing and restoring these helpers costs 402 ADDs. The direct
middle costs 12,586 ADDs, so the helper-only D cost is 12,988.

For two distinct targets `a,b`, prepare `y_b += y_a`, inject `M_a` into target
`a` and `M_a XOR M_b` into target `b`, then restore `y_b += y_a`. Arbitrary
initial target values are preserved and the result adds `M_a,M_b` as required.
If `w_i` is the number of nonzero helper coefficients in row `i`, the net
saving in orientation `a -> b` is

```text
g(a,b) = w_b - weight(M_a XOR M_b) - 2.
```

The two operations subtracted are the target preparation and restoration.
Disjoint target pairs do not alter one another's rows. Thus a pairing has
exactly the sum of its oriented savings. For each unordered edge define
`w_ab = max(0, g(a,b), g(b,a))`.

Let the supplied integer prices be `q_i`. The checker verifies
`q_a + q_b >= 2*w_ab` on every one of the 7,140 unordered pairs, `q_i >= 0`,
and `sum(q_i) = 2,884`. For any disjoint matching, summing its inequalities
counts each price at most once, so its saving is at most `2,884/2 = 1,442`.
The 58 supplied oriented pairs attain 1,442. This proves the optimum even
when unmatched targets and either orientation are allowed. It is an exact
finite mathematical certificate, independent of a solver's reported gap.

The charged new D cost is
`201 + 58 + 11028 + 58 + 201 = 11546`.
The middle is `PKQ`; keeping `PK` from an untransformed matrix is invalid.
The verifier executes the full D operator on arbitrary target and helper
inputs, then checks all 660 inputs of the whole word in both directions.
The independent checker builds columns, counts pair incidences and runs every
one of the 540 literal Boolean target/helper input columns of D separately.
The remaining 120 source inputs are untouched by D.

The class fixes `Q`, the non-D circuit, direct middle-row injection and the
disjoint-pair recipe. It excludes different helper bases, overlapping pairs,
target trees, general XOR synthesis and changed frames or copied totals.
The dual bound ignores precision constraints, but the attaining word passes
the existing precision cap. Consequently it is also optimal in this exact
fixed-body pairing class subject to that cap. No optimum is claimed outside
that class or for the choice of the helper basis itself.

## Scope, controls and provenance

The temporary target/helper bases violate literal H2's helper-only D syntax.
The original H2 guard and literal K extractor still reject them. The canonical
body with the original D passes every H1-H5 hypothesis; exact equality of the
complete D boundary map supplies the semantic substitution. No predecessor
checker is edited or weakened. All frame paths, 420 helpers, nine COPY/ERASE
lifecycles and paid rank mass 5,112 are retained.

Controls omit helper or target preparation/restoration, remove a middle read,
move D off frame zero, corrupt the dual or pair scores, reuse an original-K
certificate, and omit cleanup. A neutral pair is accepted as an endpoint but
charged two ADDs. The second checker separately rejects four certificate
mutations. Detailed native/hosted results and package-integrity tests are in
`VALIDATION.md`.

Exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected assembly
remains PR626, `660de893d27bb7abd1d5b01b1640207528a5c851`, conditional kappa
`0.001635527380375392`, using PR543
`2065fe4f72a914d907f1046603f5a36f17018535`.
The immediate composed source is PR681
`e536f6fc8aad65adef8ac4682d13625598a5c3f9`; PR733 is
`dfe84e09298abc5c5e0074afda59a821e10abfb4`.
`SOURCES.json` pins the imported bytes and Git blobs and the inherited replay
files. Compressed main inputs are compared by decompressed payload.

Assignment seed **11** came from one OS-random draw. `CLAIM.json` records the
three candidate scopes and overlap scan. SciPy/HiGHS nominated one matching
after seed-11 edge ordering, and a linear program nominated the vertex prices.
These floating computations are discovery only. The frozen integer certificate
checks the complete stated domain, with no search-based impossibility claim.
One earlier unseeded target probe and one helper-matching probe were discarded
before selecting the final artifact. The helper probe's solver optimum is not
certified or asserted here. There was no pinned coordination issue.

The inherited all-size/compiler/common-label/mutable-basis, physical hosting,
precision/tape/exact-recovery and analytic assumptions remain. A finite replay
does not prove the full multiplication theorem. Full repository regeneration,
selected-frontier cold replay, Lean and remote CI are not claimed. The selected
frontier and `upstream/` are unchanged.

## Credit

Prepared for **Sagar Thakrar / @thakrarsagar**, with substantial **OpenAI Codex
assistance** in implementation, proof analysis, verification and writing.
There is no independent human-review claim. Apache-2.0 applies to the additions.

This extends Alluri's [PR681](https://github.com/CrocSwap/integer-mult-bounds/pull/681)
composition. The helper basis is Greer Guthrie's
[PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694), following
PR686. The two-sided composition is Scott Woolsey Biggart's
[PR733](https://github.com/CrocSwap/integer-mult-bounds/pull/733), following his
PR713 target factoring and the earlier PR476/450 lineage. Sagar Thakrar's
[PR716](https://github.com/CrocSwap/integer-mult-bounds/pull/716) supplied the
vertex-price certificate method for the different original-K pairing problem.
No priority for these mechanisms or the certificate method is claimed.

The fixed body retains yongjae321's PR670, x0hu's PR674, Ali Romman's PR688,
mtpsl's PR691 and Sagar Thakrar's PR708. The accepted supplier is eumemic's
PR543/493, with Dylan Crow's exporter/checker lineage, DreamingOfClouds' retained
totals and hosting chain, Zhihao Chen's scalar interface, and all contributors
credited in the original PR681 notice, retained unchanged under `vendor/`.
Concurrent PR754 cleanup synthesis and PR759/774 target forests concern larger
or different classes and are neither imported nor superseded.
