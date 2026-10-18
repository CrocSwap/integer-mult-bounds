# R439 compensation with restored three-helper stars

**Finite bit-circuit construction; no new κ.** Allowing two helper basis
operations to share an accumulator saves **197 complete local ADDs beyond
PR926**, reducing its 11,980 to **11,783**. Preparation and restoration are
included. A disjoint-pair control using the same seed costs 11,983; the new
class saves 200 against that control.

The candidate changes only D in the selected PR589 word, using PR915's
frozen target basis. It has 64 three-helper stars and 93 single-edge
components. Every source, target and helper may start dirty. The explicit
program and exact finite identity are in [PROOF.md](PROOF.md).

| Complete local word | ADDs | D ADDs | Forward bound F | Reverse bound B |
|---|---:|---:|---:|---:|
| Selected PR589 | 24,305 | 18,085 | 49,347 | 1,113,070 |
| Frozen PR915 target basis | 13,208 | 6,988 | 49,347 | 9,534,616 |
| Incorporated PR926 disjoint pairs | 11,980 | 5,760 | 71,907 | 10,562,318 |
| Same-seed disjoint-pair control | 11,983 | 5,763 | 71,491 | 10,518,628 |
| Three-helper stars | **11,783** | **5,563** | **72,847** | **10,394,084** |

The complete D bill is **221 + 306 + 4,509 + 306 + 221 = 5,563**.
The other 6,220 ADDs, all 439 helpers, nine copied totals, frame paths and
paid rank mass 5,129 are retained. The saving against PR589 is 12,522;
these are alternative D circuits, not additive savings.

## Reproduce

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 -I -B research/r439-helper-stars-seed19/verify.py
```

Expected final line:

```text
PASS_R439_HELPER_STARS: 64 three-helper stars; ADDs 11980 -> 11783; 200 beyond same-seed pairs; 661 columns; 14 controls; no new kappa
```

This regenerates both complete bounded searches, compares the entire
candidate and certificates, reconstructs E K H independently using sets,
replays all 661 symbolic columns of five complete words in both directions,
checks the unchanged owning geometry/interface checker on baseline and
candidate, and compares the entire deterministic [receipt](EXPECTED.json).
It rejects 14 mathematical/accounting controls and accepts two meaningful
positive controls. Original assertion checks are kept enabled under `-O`.

To also compile and run the unchanged native checkers, use C++17 and Boost
headers and add `--native` to the command. `BOOST_INCLUDE` can point to a
nonstandard Boost directory and `CXX` can select a compiler. The native
receipt in [NATIVE.json](NATIVE.json) checks the baseline, PR915 and candidate
on 5/9/11 stages, covering 883/1,327/1,549 formal columns per word and rejecting
144 omitted-bridge controls. It checks every register's ordered MOVE path
and all COPY/ERASE records. `--output NEW_DIRECTORY` retains logs and records;
an existing output directory is refused.

Package admission tests:

```sh
python3 -I -B research/r439-helper-stars-seed19/test_package.py -v
```

Eight tests cover source/context mutation, certificate cost mutation, dirty-helper
mutation, duplicate/nonfinite JSON, recompression equivalence and output
preservation. Regenerated gzip containers are compared by every decoded
field, while immutable source inputs retain exact byte hashes.

## Search coverage and distinct contribution

The assignment seed **19** was drawn once using OS randomness. Its bit-track
claim, three candidate tasks and selection rationale are in [CLAIM.json](CLAIM.json).
The accepted source at the exact base
`007664306fff84fbb1c9a1b4053b69f439764034` is PR890's conditional
**κ = 0.001661957774647029**, retaining PR589's bit supplier.
That original selection is preserved verbatim in [BASE-SELECTION.json](BASE-SELECTION.json).
During verification, upstream advanced to PR942's conditional
κ = 0.001661960547713947 at `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
All 33 runtime/source pins are byte-identical across that update. The moving
root selection is not used as a runtime dependency of this historical circuit.

Both passes score all **439 × 438 = 192,282 ordered helper pairs** on the
same frozen 111 × 439 matrix E K. A seeded 64-bit tie key is drawn for
every ordered pair, including nonpositive ones. Each pass visits the same
2,298 positive candidates in descending gain, then tie-key order. The
degree-one control accepts 188 edges, skips 2,110 overlaps and rejects none
on precision. The degree-two pass accepts **221 edges**, skips **2,053**
overlaps and rejects **24** proposals on the exact complete precision bill.
The pass stops after its final candidate. There are no restarts or pivots.

[CERTIFICATE.json](CERTIFICATE.json) records each accepted/rejected proposal,
its complete F/B bounds, the census hash, costs and stopping rule.
[PAIR-CONTROL.json](PAIR-CONTROL.json) gives the matched control.
This is one completed greedy scan per class, not exhaustive optimization
over star forests, tie orders, larger components or general XOR circuits.

PR926 restricts helpers to disjoint pairs. Gareth Davidson's
[PR941](https://github.com/CrocSwap/integer-mult-bounds/pull/941), pinned at
`8af78333709a2eafd84463a7dc91467be5618b49`, reports an 11,948-ADD floor
for that restricted class. The shared centers here leave that class; this
does not contradict its floor. PR941's proof is not independently replayed
or imported. PR904/936/952 concern A/B preparation circuits, and PR917
concerns complex CK compensation. Their circuits and savings are not composed.

The final refresh also found **Ross Richardson's concurrent
[PR965](https://github.com/CrocSwap/integer-mult-bounds/pull/965)**, published
first at `6292e3774abd82f2d5202190b498f35cc1628c39`. It replaces 40 frozen
PR926 pairs plus unused helpers with general GL(3,2) bases, reaching 11,840
ADDs. This contribution independently selects the entire helper star forest
from the PR915 matrix, rather than extending that frozen matching. It reaches
**57 fewer ADDs**, with a tighter precision margin (99.996316% versus PR965's
reported 99.6193%). No PR965 code is imported; its finite checks are not
independently re-run here. Both contributions extend the pair class, and no
priority claim is made for using three helpers.

**Sagar Thakrar's PR753**, at `2b30b63789f6d9948233fc67d9d79bca6b185c5b`,
previously used restored helper stars in historical R420 phase-A decoder
totals. It is credited as a mechanism predecessor; this package applies the
star class to a different matrix, phase and precision invoice.

## Precision, interfaces and remaining work

The candidate satisfies the exact local 104-bit expression and the inherited
nine-stage 192-bit expression. The latter is
`2^18 F^5 B^4`, with the bridge exponent and charge checked against pinned
source. It uses **99.996316%** of its ceiling; the remaining margin is small
and is checked by integer comparison. No global repricing is inferred.

The original syntactic **H2 remains false**, as does literal `K_equals_D`,
exactly as for PR915/926. The unchanged checker reports these failures;
the new evidence proves the semantic D boundary instead. H1/H3/H4/H5 and
the other decomposed conclusions pass. Adoption requires acceptance of that
semantic substitution, changed whole-hosted emission/audit, complete finite
and precision invoices, and outer assembly.

The paid profile is unchanged. All-size/compiler, common-label/mutable-source,
hosting, precision/tape and analytic assumptions remain. Neither a new κ,
practical runtime improvement, unrestricted minimum, nor full formal
multiplication proof is claimed. The selected frontier and `upstream/`
are unchanged. [VALIDATION.json](VALIDATION.json) distinguishes completed
checks from the bounded repository-wide attempt and hosted CI.

## Attribution

Prepared for **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex
assistance** in research, mathematics, implementation, verification and
writing. One parent agent performed the work; no independent human review
or subagent review is claimed. Apache-2.0.

Credit **Gareth Davidson (@bitplane), PR915/926**, for the frozen target basis,
disjoint-pair method, prior circuit, I/O utilities and native harness;
**Scott Woolsey Biggart, PR733**, for two-sided basis composition;
**Greer Guthrie, PR694**, for simultaneous helper bases; **Mikhail R. Gadelha,
PR686**, for semantic D substitution; and **commdata2338, PR794**, for the
guarded target-basis method. **DreamingOfClouds, PR589**, tunes **eumemic's
PR555/543** supplier. The underlying native validation follows **Sagar
Thakrar**, **Dylan Crow**, **DaysSky** and **Zhihao Chen**. Full attribution,
AI disclosures and license pointers are in [NOTICE.md](NOTICE.md).
