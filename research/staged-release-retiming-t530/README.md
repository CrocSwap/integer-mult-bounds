# Two commuting release retimings: a conditional T530 improvement

The two staged suppliers from [PR3605](https://github.com/CrocSwap/integer-mult-bounds/pull/3605) admit an exact change of gate order and frame itinerary. In each invocation it replaces `2H1 + 2H2` by `2H3`, while preserving the operator, helper identities, entrance/final frames and width inventory. Applying that change to the actual 4,770-call allocation of [PR3626](https://github.com/CrocSwap/integer-mult-bounds/pull/3626) gives

```text
κ = 0.001730394391813963415120 − 10^-46 − 10^-70
```

The improvement over that pinned direct predecessor is **0.00000032252710818353258**, or about **0.0186424%**. This is an achieved *conditional finite construction and transfer certificate*, subject to the inherited hypotheses below. It is not an unconditional multiplication theorem, an independently reviewed result, or a global-best/priority claim. This package does not update the selected frontier.

[PROOF.md](PROOF.md) gives the exact edits, commuting argument, legal nested frames, complete paid profile, rational root enclosure and transfer dependency chain. [CREDITS.md](CREDITS.md) identifies inherited and parallel work.

## Source and scope

| Source | Exact pin | Role |
| --- | --- | --- |
| Canonical main | `20ecf2891d80b5acf18d980b2164fb44ea7faa90` | Native, allocation and admission infrastructure |
| PR3605 | `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb` | Both original staged suppliers |
| PR3626 | `659fd5e7064d9466b668d7188cbb013b333a415a` | T530 allocation and complete release driver |
| PR3633 | `46c5aaca40117a4ca90a3316771ae52cf9a6801e` | Comparison only; its T488 allocation is not used |

The direct predecessor endpoint is `0.001730071864705779882540 − 10^-46 − 10^-70`. PR3633 subsequently attained the old fixed-inventory ceiling at `0.001730096363528623534230 − 10^-46 − 10^-70`. Our result changes the local bill underlying that ceiling; no untested composition with PR3633 contributes to the claimed value. The larger difference from selected main's `0.001672660197076918` includes inherited improvements and is not attributed to this work.

This was user-directed research. `TASK.json` retrospectively classifies it under the nearest `scalar-to-moment` card, with refined scope; it is not a claim that the task picker assigned this experiment. An overlap refresh on 2026-10-18 covered 348 open PRs and 2,454 discussions, plus local records; this search does not certify novelty.

## Reproduce the bounded public checks

From the repository root, with Python 3.12 and NumPy 2.5.4 installed:

```sh
python3 -B scripts/research_package.py --package research/staged-release-retiming-t530 --check-only
python3 -B scripts/research_package.py --package research/staged-release-retiming-t530
```

The publication run passed all five stages in about 24.2 seconds, with no package writes; see [PUBLIC-VALIDATION.json](PUBLIC-VALIDATION.json). This is bounded local verification, not hosted CI.

The second command invokes `verify.py`, which creates a fresh temporary output directory outside the package and performs the following checks. Each component can also be run separately using its README.

| Component | Freshly checked by the bounded command | Retained evidence / limit |
| --- | --- | --- |
| [local-audit](local-audit/README.md) | Minimal commuting/frame proof, both complete free-operator words, 632 arbitrary input columns, both orientations, 91 zero buffers and negative controls | Complete native receipts are authenticated, not rerun here |
| [owner-audit](owner-audit/README.md) | Reconstruct 1,946,160 literal roles; independently check ownership, windows, families, chronological prefixes, capacities and full invoice; five rejection controls | Native frame tables are authenticated inputs |
| [numerics](numerics/README.md) | Two rational root engines; 63 strict transfer inequalities, 17 rejection controls and independent balance derivation | Arithmetic alone does not prove the physical circuit |
| [packing-cap](packing-cap/README.md) | All 2,551 fixed-inventory patterns, exact dual and ceiling interval | A scoped relaxation bound, not a higher achieved κ |
| [full-admission](full-admission/README.md) | Public-file integrity and cross-bound recorded-summary checks | Does not rerun or reauthenticate the omitted complete runtime archive |

The registered dependency closure includes the 13 pinned main files actually used by the bounded owner replay. Self-contained components authenticate their vendored inputs. The longer full replay has a separately pinned closure in `full-admission/MAIN-INPUTS.json`; it is not the bounded CI command.

## Full scientific replay and recorded results

The original scientific run freshly checked both changed native providers and completed all seven admission stages with exit code 0. Terminal statuses were `PASS_RELEASE` and `PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE`. The stages took approximately 23.31, 47.11, 4.60, 483.59, 0.11, 0.02 and 661.05 seconds (about 20.3 minutes total, excluding the earlier native checks). Two unchanged native chains and the retained parent chain were authenticated and reused. The newly checked native results were reused within the admission run through authenticated caches.

The complete run checks 4,770 calls, 1,946,160 roles, 474,880 live registers and 475,389 physical registers. Its global prefix bound is 1,479 bits; 1,512 reserve bits are required, within the 2,048-bit paid payload. The outer release independently replays 19 exact obligations. The release also reports 139 admission, 12 BIT, 15 controller, 8 independent-owner, 6 geometry and 8 reconstruction rejection controls. See the component receipts for their exact scope rather than interpreting every PASS as independent proof of the whole theorem.

The public reproduction wrapper reconstructs the same **654-file source manifest**:

```text
fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0
```

Its materialization path was tested. The seven scientific stages were executed separately on that identical manifest; the newly packaged all-in-one wrapper has not been rerun end-to-end. [full-admission/README.md](full-admission/README.md) gives exact installation, materialization and complete replay commands. Expect a long run outside generic CI, with enough RAM and disk for regenerated runtime files.

To keep the public contribution small, it omits regenerated source/runtime/cache archives and the large generated literal fill. Actual non-main dependencies needed for reconstruction are vendored with pins and notices. Public command metadata replaces this session's private execution prefix with `$RESEARCH_WORKSPACE`; original-to-public SHA256 maps make those adapters explicit. The original full release receipt SHA256 was `80e1f422359d7c553493c1e0f2a1b4c4de230f8eb74690e1471a14d65169d110`. A normalized public summary is a publication derivative, not that original byte-level receipt chain. Reproduction regenerates the full chain; the quick summary checker makes only the narrower claims stated above.

## Remaining assumptions

All inherited all-size dispatch/compiler and recursive rounding arguments remain hypotheses. So do common-label and mutable-source realization, whole-call hosting, SCALAR/COPY/CLEAR and zero-allocation contracts, uniform coefficient/stock bounds, bootstrap, precision, tape/recovery, and the analytic/BIT H1–H5 premises. The finite symbolic and integer checks certify their stated finite instances and implications; they do not discharge those general premises. No formal-kernel proof or independent human review is claimed. The supplier-only endpoint `0.001727405299371541` in an inherited intermediate receipt is a different layer; the final source-bound modern outer certificate uses the κ displayed above.

## Open next questions

1. **Compose the retimed suppliers with PR3633's T488 allocation.** This may close some of the remaining fixed-inventory gap. First bind these exact words into its pinned release, regenerate all ownership/invoice artifacts, and rerun native/controller/outer admission. Blocker: this composition has not been tested; do not quote its predicted endpoint as achieved.
2. **Find another legal operator/order or helper-inventory change.** The present fixed-inventory relaxed root lies in `(0.001730418899766071163804, 0.001730418899766071163805)`, only about `2.4507952e-8` above the actual T530 root. First enumerate further adjacent commuting opportunities and derive their complete frame itineraries. Blocker: scalar savings alone do not change the paid profile.
3. **Discharge an inherited all-size obligation.** An improved finite certificate remains conditional. First isolate one compiler/common-label or rounded-precision implication and provide an independently checkable general proof. Blocker: current finite native and arithmetic checks are not that general proof.
