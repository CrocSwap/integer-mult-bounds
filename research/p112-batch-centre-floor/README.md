# Independent P112 batches cannot amortize the root-code copy bill

**Scoped mathematical result with exact finite premises. No new supplier or kappa.**

For **every number k of independent standard P112 all-pairs demands**, scalar
coding across calls cannot reduce the copied-pairing-rank bill below **64k**
when both factors stay in the direct-sum root code. This allows any finite
number of terms, arbitrary complex coefficients and cross-call mixing. It
even prices a shared term only once on its **union of labels across calls**,
without a separate charge for each call it touches.

The exact charge is **8m+b**: m is the number of active terms, and b counts
terms whose reader and source columns both mix root-coordinate directions.
An optimal decoder has the minimum term count and at least one
coordinate-aligned side in every term. Cross-call mixing within one root
coordinate is allowed and can attain equality; it does not lower the bill.

For a factorization with the minimum **8k terms**, the root-code restriction
is automatic. Changing the complete basis of a minimum-size batched decoder
therefore cannot evade the bound. Every additional active root-code term
costs at least another eight units.

More generally, for a rectangular call-coupling matrix C, the minimum in this
model is **64 rank(C)** for the requested matrix `C tensor (X X^T)`. X is
the fixed norm-four 112-by-8 P112 root matrix. For two independent demands
C=I2, the minimum is 128. For C=all-ones(2,2), it is 64, but **both output
blocks then request the image of the sum of the two inputs**. These are
different endpoints. Attainment is a decoder identity, not an implemented
shared centre or a complete physical cost claim.

## Why this is useful

The selected complex supplier's 64-per-call centre charge is a central
bottleneck. The [existing lever screen](../complex-local-word-ceiling/README.md)
prices ideal two-call sharing at about 1.90 times the current primitive-saving
ceiling, replacing 128 centre-rank units by 64. The present theorem rules
out that replacement by root-code scalar mixing of independent P112 demands,
even before positive preparation, restoration, routing, hosting or precision
charges.

Under the further interface that each scalar total pays one child at its
pairing rank, at unchanged parent width and volume, the centre moment cannot
improve either: at least 8k terms each have rank at least eight. Every
nonnegative increasing per-child price remains at least `8k * price(8)`.
This comparison does not install a replacement coverage law or claim that
every physical circuit has this separate-total accounting.

The new result is the **all-batch coupling-rank law**, including the
unrestricted minimum-term corollary and a quantitative necessary budget for
outside-code escapes. The one-call support census belongs to **Mihir
Srivastava's PR845**, independently corroborated by **Adam Gall's PR1098**.
The one-call arbitrary-term factor-linear floor belongs to **woklerx's
PR1180**. We recheck their finite premises by two separate implementations;
we do not claim their census or support lemma as new. This fixed-P112 proof
does not require the more general Weyl-flat classification used elsewhere.

## Exact model and evidence

[PROOF.md](PROOF.md) proves the result for every complex C. Transpose is
ordinary transpose, not conjugate transpose. All calls retain the **same**
P112 puncture, binary label embedding and pairing. A term's reader and
source supports are unions over its nonzero output/input blocks. Its cost
is the F2 rank of their label-pairing matrix. For overcomplete factorizations,
both factors must be in their respective block-root codes. Exactness is
required on **all** pairs, including the cross-call blocks.

| Rechecked finite premise | Result |
|---|---|
| All 511 nonzero binary label functionals: rational rank of roots outside their hyperplane | 503 have rank 8; eight have rank 7 |
| Eight deficient complements | Their nullspaces are the eight removed frame directions |
| Live support of each exceptional direction | 56 roots; binary label span 8 |
| Ordered exceptional support pairs | All 64 have F2 rank 8 |

The rank-seven nullspaces remain one-dimensional over C. Thus any nonzero
complex root-code column has full label span nine or one of those eight
exceptional supports. Every support pair costs at least eight. Unions cannot
lower a submatrix rank. Matrix rank forces at least `8 rank(C)` terms, and
a rank factorization of C with the coordinate decoder attains the bound.

## Reproduce

Python 3.12, its standard library, and Git with the pinned base commit
available suffice. From the repository root:

```sh
python3.12 -I -O -B research/p112-batch-centre-floor/verify.py
python3.12 -I -O -B research/p112-batch-centre-floor/audit.py
python3.12 -I -O -B research/p112-batch-centre-floor/test_package.py
python3.12 scripts/research_package.py --package research/p112-batch-centre-floor
```

The primary checker reconstructs the Hamming geometry and exact integer
minor witnesses. The separate auditor reconstructs standard doubled E8
roots, uses set-based binary elimination, and proves rational ranks using
modular lower bounds plus exact integer null-vector upper bounds. Neither
imports a predecessor checker as an oracle. Both check the same canonical
finite receipt [RESULT.json](RESULT.json). Default replay writes nothing;
semantic checks remain active under `-O`.

Eight independent-call fixtures check 451,584 entries, including 250,880
off-diagonal call entries. Shared-column examples attain 128/192 for two/three
calls; a 17-term root-code example costs 136. A strict mixing example costs 65.
A rectangular three-output/two-input rank-two demand checks another 75,264
entries and costs 128. Controls include an exact outside-code cost-129 example
with a cost-one term, changed correlated endpoints, ordinary-versus-Hermitian
transpose, and cross-call crosstalk invisible to diagonal-block checks.

[VERIFY.json](VERIFY.json) registers bounded replay. [SOURCES.json](SOURCES.json)
pins exact source blobs and hashes, and [TASK.json](TASK.json) records the
assignment and next questions. Selected record and catalogue pins are
historical provenance. Finite batch fixtures are regression evidence; the
all-size conclusion is the written proof, not an enumeration of all k.

Validation on 2026-10-14 used Windows, CPython 3.12.2 and only the standard
library. All three registered commands passed under isolated, optimized
Python (`-I -O -B`), including the renamed-package positive replay and five
rejections from four on-disk corruption groups. The primary checker has ten
semantic controls; the separate finite-geometry auditor has seven. The
auditor does not independently check the batch fixtures or certify the
written all-size argument. The complete package replay also passed through
the repository's registered-package runner.

## Scope and overlap

The `centre-path-sharing` card is refined to its copied-information
lower-bound method. One selector draw was used, nonce
`afb2871f5b82a11465a83416a203340b`, on main
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The ceiling control and lever
screen passed. Selected source-binding checks passed using Windows extended
paths; ordinary paths hid seven files beyond MAX_PATH. All 1,579 source
files and 51 proof supplements matched. This was not the selected cold replay.

Entry overlap covered 382 open PRs including drafts and 333 Discussion
records, complete pagination, fetched at 07:04:07 and 07:05:18 UTC on
2026-10-14; local notes and the ledger were also searched. Coverage excludes
arbitrary code diffs. Claim:
[Discussion1691](https://github.com/CrocSwap/integer-mult-bounds/discussions/1691).

The pre-submission refresh covered 396 open PRs and 352 Discussion records,
with complete pagination at 07:29:35 and 07:30:48 UTC. Main was still the
pinned base. All six direct predecessor heads and the contextual PR1633/1689
heads were rechecked. No equivalent batch coupling-rank result was identified
in that coverage; this is not a literature-priority or novelty certificate.

- PR845/1098: the finite support lemma; PR968/1077: eight-term punctured E8
  floors; PR1180: arbitrary finite root-code term counts for one call.
- PR765: tensor products of a binary full-E8 code. Here the field is C,
  the puncture is P112, and the construction is a direct sum of calls.
- ctoth's [Discussion1516](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516)
  and PR1643/1664/1684: fixed-word descent trees and dirty-host transport.
  Here decoder columns may change across calls, under a different explicit
  algebraic price model.
- [Discussion1636](https://github.com/CrocSwap/integer-mult-bounds/discussions/1636)
  changes the spectral demand and reports a routing obstruction; that is
  outside the independent all-pairs endpoint here.
- PR1671 fixes the selected scalar word and optimizes its gate frames;
  this package does neither that census nor a frame-optimality claim.
- Hanson Sun / bbMisk's PR1633 proves sharp outside-code excess-rank budgets
  for one-call overcomplete decoders, extending joaqcoo / PR1224. It is
  complementary algebraic guidance for the escape question; its code and
  witnesses are not imported or represented as this package's results.
- Denis / just-mn's PR1689 studies a two-coordinate masked-Walsh family
  outside the root code, with one-call 72/77 bounds. That family and its
  finite census are not covered or reused here.
- The [shared-source two-panel claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18918111)
  explicitly assumes identical centre source signals in both calls. It
  changes the independent-input premise, so the present theorem does not
  exclude its proposed fanout mechanism.

## Open next questions

1. **Can an outside-code overcomplete batch beat the floor?** For k=2 the
   first possible case has at least 17 active terms. Cost at most 127 requires
   `sum_j (8-rho_j) >= 8*(m-16)+1`: at 17 terms, at least nine net units of
   rank saving relative to rank eight. First test one specified 17-term
   family by exact full-matrix replay and support pricing. The blocker is
   an actual exact outside-code family; failed search is not exclusion.
2. **Does an actual caller request a rank-deficient separable C?** Such a
   caller has algebraic headroom. First derive its literal block matrix,
   retaining independent input variables and cross-call obligations. The
   blocker is a realized caller with compatible labels and a complete paid
   restoration/hosting/precision budget.
3. **Can changing cross-call label charts help?** First specify two legal
   maps, calculate cross-support pair ranks and price all map conversions.
   The blocker is a valid new interface; no free relabeling is admitted.

Masked identities, changed charts, temporal source relations, interacting
delivery and outside-code overcomplete factors remain outside the theorem.
No selected cold replay, native/compiler implementation, owner admission,
precision/tape analysis, all-size physical realization, analytic transfer,
Lean proof or independent human review is claimed. The selected frontier,
frozen archives and predecessor packages remain unchanged.

## Credit

**Mihir Srivastava / mihir-s-05 (PR845)** owns the support reduction and
original rank census; **Adam Gall / adamgall (PR1098)** independently
rechecked it with Gram spectra. **themilkman216 (PR968)** supplies frame-pair
geometry and eight-term floors; **woklerx (PR1077/1180)** supplies complex
coefficients and the arbitrary-term root-code extension. **Douglas Colkitt
(PR1240)** supplies the packing ceiling and centre-sharing motivation.

Retain **DreamingOfClouds / PR717**, **Joel Pulikkan / GamingPuzzled / PR620**,
PR595 format geometry, **icekylinx**, and the E8/compiler lineage named in
the predecessor notices. **Mister-Meeseeks / PR765**, with GamingPuzzled and
**Chi Zhao / PR631**, supplies the related tensor-code precedent. ctoth's
disclosed model reviewers, **Dennis / antunishdPursuit**, **Andrey Mas / an664**,
and **Cinna Davis / 1337isnot1337** have complementary fixed-word audits.
Selected construction credit stays with **Rohan Arun, Jeremy Kothe,
Hao Yan** and the complete lineage in the selected review.

Prepared for **alephnan** with substantial **OpenAI Codex assistance** in
proof, programming, separate algorithmic checks and adversarial review.
No generic rank-factorization or geometry literature-priority claim is made.
New work is Apache-2.0 under the repository license. Separate AI checks are
not human peer review or proof-assistant certification.
