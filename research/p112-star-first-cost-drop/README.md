# P112 root-star trims: frame change at 4, first copy-cost drop at 20

**Scoped structural result and exact census. No decoder construction or new kappa.**

This answers the first-rank-drop portion of the further-trim question in PR1242. On fixed P112, the original C/N root-star family has 7,616 tagged cost-seven atoms. Arbitrary additional row and column support trims need **20 or 22 total deletions** before their copy price falls. Every such rank drop removes at least **560 constrained even-pair positions** from the atom's support. A frame-hit change is possible after **four** deletions while the copy price remains seven. One extra trim changes neither price nor frame coverage.

The [proof](PROOF.md) reduces every arbitrary erasure set to a nonzero codeword, then uses a rank-factorization lemma to handle simultaneous cuts on both sides. Two engines agree on all 967,232 nonzero codewords and every atom's threshold, witness, minimizer count and code digest. This changes the exact-support premise of PR1236 and leaves its original theorem intact.

## Reproduce

From the repository root, standard-library Python:

```sh
python3 -I -O -B research/p112-star-first-cost-drop/verify.py
python3 -I -O -B research/p112-star-first-cost-drop/independent.py
```

Expected markers:

```text
PASS_P112_STAR_FIRST_COST_DROP atoms=7616 codewords=967232 copy_drop=20 frame_change=4 even_loss=560
PASS_INDEPENDENT_P112_STAR_TRIMS atoms=7616 codewords=967232 copy_drop=20 frame_change=4 even_loss=560
```

`generated/THRESHOLDS.jsonl` has one row per tagged cost-seven atom. Columns are `[left_tag, right_tag, minimum_rows, minimum_even_loss, row_cut_hex, even_loss_cut_hex, row_minimizer_count, loss_minimizer_count, codeword_sha256]`. A tag is `2*normal_line + self_trimmed`, with false/true encoded as 0/1. Bit positions in the cut masks are original root-line IDs, not positions in the shortened live list. Transposing the tags supplies the column threshold; the joint minimum is the smaller of the two one-axis thresholds.

`generated/CERTIFICATE.json` records the aggregate distributions and witnesses. `generated/MODEL.json` fixes every coordinate and live label. The main verifier rederives the complete model and table; its explicit `--write-directory NEW_DIRECTORY` option refuses an existing destination. The independent engine imports no primary engine or predecessor code. It reconstructs roots by Weyl reflections and enumerates dual functionals in independently obtained row coordinates.

`test_package.py` supplies seven mathematical/package tests. Its independent small-matrix oracle checks all 4,096 binary 3-by-4 matrices and 524,160 joint-cut cases on the nonzero matrices, including both cardinality and constrained-position loss. It also rejects source/model/table corruptions, refuses receipt overwrite, and replays both engines under optimized Python after relocation. These finite tests check implementation; the erasure lemmas establish the all-subset scope.

All seven tests pass locally on Python 3.14.7. The complete registered replay passes on Python 3.12.15, including the final all-parent frame guard. Runtime and validation details are in `VALIDATION.json`; remote CI and selected cold replay are separate.

## Result and limits

| First joint copy-price drop | Tagged pairs |
|---:|---:|
| 20 support deletions | 5,376 |
| 22 support deletions | 2,240 |

The constrained-position loss floors are 560 (5,376 pairs), 624 (448), and 656 (1,792). Deleting the same root from both factors counts as two support deletions. The loss counts the union of original constrained positions removed from this one atom; it is not a count of extra paid operations or repair terms.

This is a necessary geometry and copy-rank audit. A term-level saving does not supply a decoder: coefficients, all even entries, helpers, source access, frame changes, dirty restoration, shared copies, hosting and the complete recursive invoice still require a construction. Cost-eight/nine parent atoms with further trims and unrestricted support families are outside this census. No selected cold replay or full native admission is implied.

## Open next questions

Can the recorded cost-six atoms support a masked decoder below cost 64 after complete realization costs? A feasible first step is to calculate live-frame coverage for their minimum cuts and solve a fully explicit covering relaxation before coefficient synthesis. The blocker is that a first copy saving sacrifices at least 560 constrained support positions, which free odd-entry corrections cannot restore; a favorable relaxation is necessary but would still need an exact identity and physical cost ledger. `TASK.json` records this question.

## Provenance and credit

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Fresh OS assignment seed **46**, retained despite matching an earlier draw. The earlier PR1187 concerns global P104 punctures preserving frame lines; this result concerns internal support cuts on fixed P112. Coordination: [discussion 1301](https://github.com/CrocSwap/integer-mult-bounds/discussions/1301).

Navinor (@navinor), [PR1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226), head `8b10989e4e45f0f9ce41004d7898a21a32f87e11`, supplies the model and parent census. David Arias (@DavidAriasC), [PR1236](https://github.com/CrocSwap/integer-mult-bounds/pull/1236), and Hanson Sun (@bbMisk), [PR1242](https://github.com/CrocSwap/integer-mult-bounds/pull/1242), supply the exact-star assembly floor and the further-trim question. DreamingOfClouds/PR717 and the PR968 geometry retain their attribution in the frozen notice. Input archives, Git blobs, source heads and the original catalogue/selected-record provenance are in `SOURCES.json`.

New work by **Cinna Davis (@1337isnot1337)** with substantial **OpenAI Codex assistance** in proof analysis, code, experiments, checks and writing. Both engines belong to this contribution; no independent human review or full formal verification is claimed. Apache-2.0; `LICENSE` and the unchanged predecessor notice are included.
