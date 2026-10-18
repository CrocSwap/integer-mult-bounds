# Conditional kappa 0.001676938111022438: pivot554 signed restoration

**Completed finite construction and local full admission.** This is
`838469055511219/500000000000000000`, with complex endpoint
`335950991225108904267/200000000000000000000000`. It exceeds PR1625's
`0.0016768966690212993077507...` by more than 4.1442e-8. The concurrent PR1644
refines PR1625's digits but not its word; it remains below this result.
No selected result is edited or claimed accepted by maintainers.

## Change

The two PR1625 pivot566 words receive one additional pivot554 kernel. Six
ADDs replace one, with all old frames and whole-owner widths preserved.
The last restoring read uses **minus the initial dirty pivot**. Consequently
the closing DATA74 gate has the same minus sign as its opening gate; the
usual positive-restoration assumption gives the wrong circuit. See PROOF.md
and the exact original-index recipe in RECIPE.json.

Each complete call changes H1 +1, H2 -2, H3 +1. At the unchanged 249/417 T74
dispatch, the global profile is
`{1:1560432,2:336336,3:278724,4:84912,5:54612,8:5328,48:22748}`.
Rank mass, child count, 74 replicas, 666 invocations, 319680 whole-helper
roles, owner map, dispatch, pending axes and idle remainder are unchanged.
No cross-family axis transfer or clean-workspace assumption is used.

## Reproduce

Python 3.12+ and standard library, from the repository root:

```sh
python3 -I -B research/t74-p554-signed-restoration/check.py
python3 -I -B research/t74-p554-signed-restoration/test_package.py
```

Expected final marker:
`PASS_P554_CONSTRUCTION_AND_PRICE kappa=0.001676938111022438`.
These bounded commands check the local construction, exact price and package
controls. **They do not replace the full physical admission command below.**
`verify.py` itself supports -O; `price.py` explicitly rejects -O because the
retained outer engine contains proof-relevant assertions. `check.py` removes
inherited PYTHONOPTIMIZE and launches nonoptimized children deliberately.

Full native and T74 replay requires Python 3.14, SymPy, C++17 and Boost. Export
PR1319's exact dependency into a separate directory; no moving branch is used:

```sh
git fetch origin 603defe58aac018c6a8457840481390a15846fe4
mkdir ../p554-deps
git archive 603defe58aac018c6a8457840481390a15846fe4 \
  research/global-mixed-t74-exact-fill | tar -x -C ../p554-deps
python3 -B research/t74-p554-signed-restoration/replay_full.py \
  --deps ../p554-deps --work ../p554-new-output
```

The output path must not exist. The pinned 149-file PR1319 manifest is checked
before execution. Default operation rebuilds both original providers, admits
the parent, then freshly runs both changed providers. Optional
`--parent-replay`, `--native-gauge44`, `--native-extra` explicitly reuse completed
matching-word stages and record that fact. The release ran all four native
words freshly in this session, then the wrapper reused those just-completed
results and performed fresh discovery, frozen-spec strict T74 admission and
geometry controls. It is not a fresh reconstruction of the original paper or
bit operator: the predecessor's declared geometry ancestry and PR589 bit
supplier remain inherited.

Expected full marker:
`PASS_T74_P554_SIGNED_RESTORATION_COMPLETE_FINITE_ADMISSION 0.001676938111022438`.

## Observed verification

Both new words pass all 704 rational columns in both orientations, full
B-plus-early matrix equality and signed boundary checks. Both also pass fresh
native transport, emitted ledgers, scalar replay, wrappers and exact phases.
The T74 replay checks all 319680 roles and 11142 actual 73-axis charts. It
recounts prefix1441 with2048 charged bits and row19545 below20161. The finite
invoice charges the additional scalar work; no scalar cost is silently dropped.

Rejections: 22 local semantic/frame/accounting controls, 114 admission,
12 bit, 15 controller, eight independent owner and six geometry controls.
Both native-complex and conservative-complex moment brackets and their 47
strict outer inequalities pass; each has four outer parameter controls.
Five focused tests pass, including an independent direct-column dirty-only
wrong-sign counterexample, source and recipe corruptions, read-only optimized
relocation and output-preservation checks. Twenty repository research tests
pass with one existing Python3.12-only skip on the Python3.14 test host.

The initial discovery ends at an expected stale-value freeze mismatch after
bind/emit/audit/invoice/assembly pass. Only values just recomputed in its
WITNESS-RECORD are reset through the credited PR1186 helper. An unchanged
freeze followed by a fresh strict replay accepts the new certificate. No
mathematical guard is removed. RESULT.json records source and output hashes;
full replay regenerates the complete raw receipts and logs in the new work
folder. Execution-specific hashes may differ across paths/timing environments.

## Pins, scope and credit

Actual upstream base: `0a201997097b8a89b638f3a2afcb35db4184c8b2`.
Local construction parent: PR1625 `62092e96d2cb8f5751ce7d81b1ca774a0dd3827f`.
T74 physical dependency: PR1319 `603defe58aac018c6a8457840481390a15846fe4`.
Tooling provenance: PR1186 `9254a3cc610a72e9c4600da089d5cdbcab996b9c`.
Source pins and copied original notices are included. Original assignment
seed57 is retained for this user-directed continuation; no fresh random draw
is claimed. Posting a narrow overlap note to PR1625 returned403, so the claim
is recorded in TASK.json. A new source/frame interface, not a rerun of the
closed two-shock search, supplies the gain. SEARCH.json states the bounded
nomination domain and stop at the first gain; no global optimum is claimed.

The inherited all-size compiler, common-label/mutable-source realization,
whole-call correlated-dirty hosting, precision/tape, exact recovery, analytic
transfer, PR559 correction and PR589 H1-H5 conditions remain. No unconditional
multiplication theorem, Lean formalization, independent human review or hosted
CI success is claimed. Full `make verify`, selected-frontier cold replay and
a second OS were not run. Attribution and substantial AI disclosure are in
NOTICE.md; predecessor construction credit remains with its authors.

## Open next questions

Can another written pivot admit a useful negative or dyadic returned-dirt
row while preserving the full frame and owner interfaces? First establish
that exact row, then price one bounded candidate; no further candidate was
searched after this gain. Independent human review of this finite
construction and the inherited all-size interfaces remains valuable.
