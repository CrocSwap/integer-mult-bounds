# Independent local audit of the two coupled carrier folds

**PR3133's two folds pass a separately implemented exact local audit.** Both
source variants preserve forward and dual dirty-input maps, chronological binary
frames, restoration and inverse cleanup. Each fold contributes exactly
`+6 H2 - 2 H3 - 3 H4 + H5` to the local histogram. No new construction, physical
supplier admission or kappa is claimed. The selected record stays
`0.001672660197076918`.

Audited source: dcharb78's [PR3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133),
head `51eb9c4ee9e4722010d308aa3309e039d3940cc2`, package
`research/rank7-coupled-586-588-carrier-fold`. This contribution starts at main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
[SOURCES.json](SOURCES.json) identifies original paths, Git blob IDs and SHA256s
of five byte-preserved data snapshots. Replay needs neither that pending branch
nor its code. Source bytes were compared against fetched Git objects during
preparation; standalone replay checks their recorded digests. Generic metadata
pins the original catalogue/selected record; the verifier authenticates its
package-local snapshots separately.

## Result and controls

For each of `base` and `extra`, independently splice declared source intervals
and check four words: the `R1_E42`/`R2_E7` restore control, helper 586 alone,
helper 588 alone, and both folds. The last word must equal the shipped candidate
in every field except independently reconstructed cleanup and independently
checked report; both are separately compared against their shipped counterparts.

| Quantity | Restore control | Both folds |
|---|---:|---:|
| Local histogram | `1:2433, 2:712, 3:232, 4:108, 5:18, 8:8` | `1:2433, 2:724, 3:228, 4:102, 5:20, 8:8` |
| Local rank mass | 5,139 | 5,137 |
| Helper width inventory | `4:26, 5:2, 6:16, 7:52, 8:99, 9:213` | `4:26, 5:2, 6:18, 7:50, 8:99, 9:213` |
| Helper width mass | 3,283 | 3,281 |
| Independent dirty inputs, each orientation | 632 | 632 |
| Restored helpers / private zero buffers | 91 / 91 | 91 / 91 |

Both groups' deltas add exactly. [RESULT.json](RESULT.json) records every affected
register's bill, including carriers 438/440, consumers and helpers 586/588.
Centre COPY/ERASE and final climbs are included in the local histogram.

Two controls separate the coupled premises. Lowering either terminal frame in
the unchanged restore-control word fails chronological containment. Keeping
the old terminal frames on the changed word is legal, but adds two rank-one
children in total and restores the old inventory. These are controls of the
literal words, not optimality claims over resynthesized frames or other words.

## Independent method and proof scope

`verify.py` imports only the standard library: no predecessor evaluator, frame
solver, cleanup generator, invoice engine or producer. The predecessor's formats
and mathematical contracts were read; its mechanism is credited, not rediscovered.

- Enumerate binary subspaces as vector sets, independently of canonical-basis
  elimination. Check actual containment and charge dimension differences.
  Derive warp positions through an old-cut/new-cut map when splicing source hunks.
- Enumerate all 512 images of each of 72 binary warps. Check invertibility,
  symplectic pairings of 18 generators, and complete 512-point frame sets for
  zero, full and declared frames. Check prelude/chronological entries against
  the declared operator and lender.
- Propagate exact rational rows with monomials consisting of an independent
  input and a reduced word of invertible free operators. Require
  `Y_i -> Y_i + X_i`; before cleanup each restored helper equals its own
  arbitrary input and appears in no other row. Independently reconstruct
  inverse-reverse cleanup on ordinary non-target actions, using private zero
  buffers for low-ended helpers. At return all non-target inputs are preserved
  and every private buffer is zero.
- Replay the contragredient circuit separately: reverse an ADD's direction and
  sign, invert scales, and use independent `K^(-T)` symbols. Require
  `X_i -> X_i - Y_i` and the same clean-buffer obligation.

Exact symbolic coefficient equality proves these named finite linear identities
for arbitrary independent dirty inputs; it is not a random numerical test.
The free-operator proof uses inverse cancellation, so applies to the specified
actual invertible operators. The binary-frame check does **not** certify native
Clifford/Gaussian phases or a zero-cost physical realization. Owner legality,
whole-call timing, idle packing, adapters, moment/cap roots, precision, stock,
all-size execution and the outer theorem are outside this audit. The claimant's
full-admission receipts are not independently endorsed. Smaller local rank mass
alone does not establish a better complete moment.

## Reproduce

Python 3.12 or later, standard library, from the repository root:

```sh
python3 -I -B research/coupled-carrier-independent-audit/verify.py
python3 -I -B research/coupled-carrier-independent-audit/test_controls.py
python3 scripts/research_package.py --package research/coupled-carrier-independent-audit
```

Expected: `PASS_INDEPENDENT_COUPLED_CARRIER_LOCAL_AUDIT`, 13 passing behavioral
groups, and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. Each
registered command has a 120-second limit. `verify.py --write` explicitly
regenerates the deterministic receipt; normal replay is read-only. Cleanup/word
comparisons use parsed payloads, not regenerated gzip streams.

Controls cover wrong edit preimages, coefficient faults in both folds, stale
warp positions, terminal frames, stale cleanup, wrong restoration, unrelated
and restored dirty columns, singular/wrong warp maps, and a dual-only private
buffer fault invisible on the forward zero-buffer domain. Explicit exception
checks stay enabled under `-O`.

The registered replay passed on native Windows CPython 3.12.10; both commands
also passed on CPython 3.14.6 under `-I -O -B`. [VALIDATION.json](VALIDATION.json)
records commands and the sandbox-specific temporary-directory adjustment.

## Coordination

Draw: `046bacb787024754f8871d3c2953d9a9`, `complex-new-helper-inventory`.
[TASK.json](TASK.json) records the changed scope: audit a live changed-inventory
proposal instead of designing another helper or repeating PR3125 moment screens.
Entry overlap covered all 258 open PRs and 1,889 discussion records at
2026-10-17 07:06 UTC, plus sparse local notes. No PR3133-specific discussion claim
was found; the added value is independent local coverage of its author-checked
mechanism. This is not a novelty certificate. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18990991)
records the claim and outcome.

The pre-submission refresh at 07:14 UTC covered 259 open PRs and 1,892 discussion
records. It found a [concurrent audit claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18991086)
on the same two helpers, also under Arham Tahir's account, posted after the entry
snapshot. That claim had no separate result artifact in the snapshot. This
package supplies its own checked implementation and failure controls; it claims
neither exclusive novelty nor a comparison with unpublished concurrent code.
PR3133's head and canonical main were unchanged.

## Open next questions

Does the complete native/physical construction preserve this local contract and
realize the changed bill? Pin the audited head and independently check its
phase/wrapper and T74 owner/adapter boundary before relying on complete moment
or kappa claims. The blocker is the separately bounded complete-admission review;
this local audit supplies neither that review nor another lowering search.
Structured details are in `TASK.json`.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance; no independent human
mathematical review claimed. New checker/tests: Apache-2.0.

The coupled folds are dcharb78's PR3133; restore-control skips are dcharb78's
PR3042. Retain Marius-Paul Dumitrean's PR2979 words/joint end frames, Jeremy
Kothe's PR3015 edit framework and scalar rewrites, Mason Hale's paired-extension
chronology, Jeremy Diviney's paired-extraction/adapter work, and the full supplier
lineage. [Source credits](SOURCE-CREDITS.md) and [source notice](SOURCE-NOTICE)
are retained verbatim; their inventories describe the predecessor, not code
imported here. Douglas Colkitt's procedure/packing ceiling supplied orientation,
not an acceptance calculation for this audit.
