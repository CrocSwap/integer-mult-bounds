# Which word is selected in the PR1042 replay?

The retained package file `research/gauge44-slots-t16/evidence/local/FULL-WORD.json.gz`
is an **R492 predecessor**, not the selected R480 seven-slot word. Its canonical
contents match `base/cold44/FULL-WORD.json.gz` in the maintainer's selected replay.
The selected word is the archive member **`slots/local/FULL-WORD.json.gz`**.
Five archive members contain that same canonical word. This package provides an
executable inventory and rejects confusing the retained evidence, the pre-slot
R480 word, or a compressed-container digest with the selected word.

No selected mathematical input was found to be wrong. The original README
already requires freshly built `--local` output, and the selected orchestrator
passes that output explicitly. This is a provenance reconciliation with concrete
rejection controls, not a correction of the accepted conditional bound.

## Three distinctions checked

| Object | Retained evidence | Selected archive word |
|---|---:|---:|
| Helper count | 492 | 480 |
| B operations | 1918 | 1846 |
| A operations | 3738 | 3451 |
| Cleanup operations | 28150 | 6796 |

The selected decoded payload is already compact sorted JSON. Its payload and
canonical SHA-256 both equal the original slot pin
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
Its committed gzip container SHA-256 is instead
`49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289`.
Both are correct in their respective domains. The verifier accepts recompressed
and reformatted copies when every parsed word field remains identical. It keeps
exact raw hashes for the frozen source archive and its recorded artifact receipts.

The selected word's own report retains the stage-local status
`EXACT_CLEAN_OWN_Y_EARLY_CENTER_WORD_NOT_ADMITTED`. The later composition receipt
is `PASS_COMPLETE_PR1042_COMPOSITION`. They describe different stages and are
not contradictory. The old PR799 wording in the assembly scope similarly
describes inherited lineage; the explicit selected pointers, T16 receipt and
source-bound profile identify the PR1042 composition. This note does not turn a
stage-local claim into full admission by renaming it.

## Exact evidence

The command checks all files listed in the pinned selected-source manifest,
all **458 regular unique archive members**, the **457 artifact digests** in the
producer receipt, all ten recorded construction stages and their source/log
digests, and the selected assembly's identical archived and retained bytes.
It inventories every **35 FULL-WORD member**, including duplicate stages, using
container, decompressed-payload and canonical digests separately. Five aliases
match the selected slot pin; the retained R492 file matches only the historical
`base/cold44` member.

An additional arithmetic bridge checks the local profile
`{1:2412,2:418,3:432,4:142,5:82,8:8}`, its local rank mass 5586, and its helper-width
inventory. Multiplying that profile by 144 whole invocations and adding the
recorded T16 idle profile reproduces the independent receipt, T16 replay and
assembly profile exactly, with total rank mass **1041408**. The assembly retains
PR589 on the bit side and conditional kappa `1672188119205421/10^18`.

The complete word inventory, equality classes and exact values are in
`EXPECTED.json`. Eight controls reject the R492 word, the pre-slot R480 word,
an omitted operation, changed idle profile, omitted whole call, false helper
count, wrong digest domain and duplicate JSON. The archive is read in memory;
no tar paths are extracted or executed.

## Reproduce

From the repository root, Python 3.10+ standard library:

```sh
python -I -O -B research/selected1042-lineage-resolution98/verify.py
```

Expected: `PASS_SELECTED1042_LINEAGE selected_R=480 retained_R=492 words=35 aliases=5 controls=8`.
The default command writes nothing. `--write-certificate` writes only when no
certificate exists. Every check remains active under `-O`.

## Scope and provenance

Base `ba82555c64e1879e4b7decce28186f208fcb8262`, assigned seed98 without reroll.
The selected snapshot is frozen for reproducibility. Later selected frontiers
are outside this investigation. This command checks provenance consistency and
profile arithmetic; it **does not rerun the original native construction**, all
controls, moment engines or outer inequalities, authenticate historical
execution, or prove the full multiplication theorem. It does not prove that a
different word with the same profile is correct. Source hashes and the exact
canonical word pin prevent substituting such a word here.

The selected construction, source manifests and replay are credited to Jeremy
Kothe, Rohan Arun, Hao Yan and the credited compiler/supplier lineage, with
Douglas Colkitt's maintainer orchestration. The gzip distinction follows the
repository's existing reproducibility policy and Maxime Fleury's earlier audit;
no new general hashing principle is claimed. Concurrent local analysis of the
mutable-leaver cores first noticed the retained R492 evidence path; this package
adds the complete archive reconciliation and profile binding, not that core
optimality result. Prepared for @woklerx with substantial OpenAI Codex assistance.
Apache-2.0; algorithmic crosschecks and AI review are not independent human review.

Fresh PR1112 independently checks the selected finite invoice, guards and outer
slacks. This package does not repeat that audit; it identifies exact word
artifacts and verifies their provenance and profile linkage.
