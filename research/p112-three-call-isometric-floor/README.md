# Three independently recharted P112 calls still pay 192

**Independent proof / scoped negative result. No new supplier or kappa.**

Three independent P112 all-pairs demands cannot share away their separate-total
copy bill by using different **isometric binary label charts**. For arbitrary
complex root-code factors, any finite number of terms, and free chart
conversions, the sharp total pairing-rank cost is **192 = 3 × 64**.
For every `0 < q <= 1`, the sharp separate-total power bill is `24 × 8^q`.
Thus this particular three-call sharing route also fails to reduce the
centre's recursive moment at fixed parent width and volume.

This changes the two-call premise of Sagar Thakrar's pending [PR2294](https://github.com/CrocSwap/integer-mult-bounds/pull/2294),
which explicitly leaves `k >= 3` open. It does **not** repeat its chart sample
or claim the one-call support census as new. The new ingredient is the
six-order triangular deletion lemma in [PROOF.md](PROOF.md), section 3.

**Concurrent overlap, discovered before submission:** DreamingOfClouds'
[PR2338](https://github.com/CrocSwap/integer-mult-bounds/pull/2338), head
`82700676e1d42acf98dc1921cb6ef82551620008`, states a broader all-batch theorem
for symmetric charts in section 3.4, using normal classes and an additional
frame lemma. The core proof and verifier here were completed before reading
that submission (retained in commit `9df32e528da547a1c1cb51cbd480f88f8b7d197e`).
This package supplies an **independent, frame-lemma-free proof for three
Gram-root-code calls**, an attained general counting bound, and direct
all-pairs/mutation evidence. Its scope and surplus bound are narrower than
the concurrent theorem's. No first-closure or stronger-floor claim is made;
the concurrent theorem and its full package have not been audited here.

## Statement and evidence

Let p count active terms whose nonzero reader and source calls are disjoint
("pure" cross-call terms), and n count all other terms. Exactness of the
three independent endpoints forces

    n + (2/3)p >= 24.

Within-call isometry gives each non-pure term price at least eight. A pure
term can cost seven, as the exact fixtures confirm. Therefore

    total rank >= 8n + 7p >= 192 + (5/3)p.

For q in `(0,1]`, replace eight and seven by their q-th powers; the surplus
coefficient `7^q - (2/3)8^q` stays positive. Twenty-four independent coordinate
terms attain both floors. Equality excludes pure terms.

The proof averages lower-block truncation over the six call orders. A pure
term occupies either one reader and one source call, or three calls with one
side occupying a single call. Its truncation remains rank zero or one, with
mean 1/2 or 2/3.
Triangularizing the non-pure sum leaves identity diagonal blocks and hence
rank 24. This argument applies to all complex coefficients and all three
isometric charts; it is **not** an inference from the finite examples.

The new standard-library verifier imports no predecessor executable. Its
deterministic [EXPECTED.json](EXPECTED.json) records:

- A reconstructed 120-line Hamming geometry, the 112 live lines and the
  nondegenerate nine-dimensional binary form.
- All 511 binary hyperplane complements: 503 exact rank-eight cases and
  eight rank-seven cases with the eight coordinate kernels. Modular lower
  bounds and exact nullspaces certify rational/complex ranks; the eight
  deficient cases are also checked by Fraction elimination.
- All 64 ordered within-call exceptional pairs (rank eight) and all 64
  pairs under a selected transvection (rank seven), with direct 56-by-56
  ranks checked against reduced-span pricing.
- All **12** disjoint three-call support patterns, each at all six orders
  (**72** exact truncation-rank checks).
- Four exact decoder fixtures, each replayed on all **112,896** live
  output/input pairs, including cross-call blocks. Their copy bills are
  **192, 199, 200 and 201**. The cost-199 example contains a genuine
  rank-seven pure term. The cost-200 example has the three-call support
  pattern attaining the deletion argument's mean 2/3. The cost-201 example
  has n=22, p=3 and attains `n + (2/3)p = 24` in every call order, proving
  sharpness of the counting lemma on an exact root-code identity.
- Seven internal mathematical controls, plus the separate package tests
  described below.

## Reproduce

Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
Python 3.12 and Git with this base available suffice; no third-party dependencies.
From the repository root:

```sh
python3.12 scripts/research_package.py --package research/p112-three-call-isometric-floor
```

Expected: the two registered checks end with
`PASS_P112_THREE_CALL_ISOMETRIC_FLOOR` and `PASS_THREE_CALL_PACKAGE_CONTROLS`,
then the runner prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
Direct read-only replay is also available:

```sh
python3.12 -I -O -B research/p112-three-call-isometric-floor/verify.py
```

The direct replay prints receipt SHA256
`c1278f0b9154e144fe67e85652c0b98c4bfd98b9c481a2680037a2b8efe08f09`
and `PASS_P112_THREE_CALL_ISOMETRIC_FLOOR`. Only the explicit `--write` option
regenerates this package's own `EXPECTED.json`; normal replay writes nothing.
Checks remain active under `-O`. [VERIFY.json](VERIFY.json) declares all live
inputs; [SOURCES.json](SOURCES.json) binds their exact SHA256/Git blobs.

Validation on macOS arm64 passed with CPython **3.12.13** (registered, optimized
and normal) and **3.14.5** (optimized). Direct outputs are byte-identical. The
registered check includes all five deliberate on-disk corruptions. No hosted
CI, proof-assistant run or independent human review is claimed.

## Controls and scope limits

Internal controls reject an invertible non-isometric chart, the false
common-chart per-term floor eight, an incorrect cancellation sign, an omitted
coordinate term, and cross-call crosstalk that passes diagonal-only endpoint
checks. Two controls prevent extending the three-call deletion lemma to four
calls: a pure 2-by-2 support pattern has truncation rank two in four orders
and mean rank **one** over 24 orders, exceeding 2/3.

`test_package.py` checks relocation and read-only replay, plus on-disk
corruptions of the receipt, source digest, chart-dependent pricing and the
three-call ordering count. Every rejection must name the intended failure.

The inherited model is PR1714's **separate-total union-price root-code**
objective. Both factors must stay in the respective block-root codes, and
each call uses the same isometry on its reader and source sides. The endpoint
is `C=I_3` on independent input blocks, with ordinary transpose. Charts are
granted free; no physical decoder is compiled or installed. Positive source
access, helper, frame-change, routing and restoration costs cannot reverse
this lower bound within that objective. A different cost/interface law needs
its own full invoice.

This is a written proof after inherited, rechecked finite premises. It is
not Lean formalization, a universal circuit lower bound, or a complete
multiplication theorem. Compiler/all-size, physical common-label realization,
whole-call hosting, precision/tape, exact recovery, analytic transfer and
bit H1–H5 obligations remain untouched. The selected result and `upstream/`
are unchanged. No selected cold replay is required for this isolated note.

## Sprint record and overlap

OS-random assignment seed **47** chose structural decoder research. It also
selects the two distinct fixture transvections (vectors 367 and 47 in the
verifier's explicitly reconstructed chart); it is not offered as a novelty
claim. This is a proof and fixed finite replay, not a candidate search.
Coverage ends at the declared three-call model, all 511 functionals, all
12 support patterns, 64 ordered pairs in each named pairing, and four
explicit endpoint fixtures. No failed search is called an impossibility theorem.

Three candidate tasks were considered: the P104 cut-2429 nested-frame contact price,
the noncommuting thirteen-call five-SWAP continuation of PR2317, and the
three-call chart question. The first had extensive live correction work;
the second lacked a promising completed budget in this session. The third
changes one explicit predecessor premise and admits a bounded proof check.

Entry overlap covered 546 open PRs including drafts and 1,049 Discussions
with complete pagination, no warnings, and 1,536 local package/ledger records
(2026-10-15 05:41 UTC). No matching three-call P112 chart result was identified
in that coverage. Closed PRs are covered only through local notes and the
ledger; arbitrary diffs are not searched. The canonical claim is
[Discussion1166 comment 18941767](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18941767).
The final refresh at 05:54 UTC covered **550 open PRs and 1,058 Discussions**
with complete pagination and no warnings. Main and PR2294's pinned head were
unchanged. Other three-mode matches concern coordinates within one call,
not three independent calls. A subsequent newest-PR check at 05:56 UTC found
PR2338; its batching proof was read before submission, and the independent
contribution and narrower scope are stated above.
Full task, stopping rule, final freshness and verification evidence are in
[TASK.json](TASK.json).

## Open next questions

1. **Four independent calls with independent isometric charts.** The present
   truncation argument loses its 2/3 coefficient on balanced 2-by-2 pure
   supports. First classify the prices of those supports jointly with the
   required cross-block cancellation, rather than assuming a sub-256 decoder
   exists. This determines whether the next batch size offers a real escape.
2. **Beyond the root-code separate-total interface.** A saving construction
   would need a different copied-total contract or outside-code factors.
   First specify one exact all-pairs endpoint and fully price its preparation,
   dirty restoration and recursive children. The blocker is an admitted
   physical interface, not this note's ordering census.

Structured relevance, first steps and blockers appear in TASK.json.

## Credit and disclosure

Sricharan Vagvala (@theon199), with **substantial OpenAI Codex assistance**:
the AI drafted the argument, implementation and documentation, followed by
author checks. No independent human review or proof-assistant check is claimed.
New material is Apache-2.0 under the repository license.

Credit alephnan / PR1714 for the batch root-code model and original common-chart
floor; Sagar Thakrar (@thakrarsagar) / PR2294 for the two-call isometric result,
rank-seven cross-term mechanism and explicit `k>=3` question; Mihir Srivastava
/ PR845 and Adam Gall / PR1098 for the support classification; woklerx /
PR1077 and PR1180 and themilkman216 / PR968 for the decoder-floor lineage;
Douglas Colkitt / PR1240 for the centre-sharing motivation and package tools.
The retained selected construction remains Rohan Arun's PR1094 on Jeremy
Kothe's PR1087 and the cumulative k8/T16 lineage, with the DreamingOfClouds
PR589 / eumemic PR555 bit supplier. No predecessor code or data is vendored.
DreamingOfClouds / concurrent PR2338 receives credit for the broader all-batch
symmetric-chart statement, independently developed using normal classes and
its frame lemma; the present argument does not use that result as a premise.
