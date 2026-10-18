# Normal-45 extraction with fourteen paid gate rewrites

Status: exact words, native phases, four complete owner assignments and independent moments pass; full outer release is pending. The moment nomination is κ ≈ 0.0017240352247481. It must not yet be described as a complete release.

This combines Marius-Paul Dumitrean’s four paired extractions ([PR #2942](https://github.com/CrocSwap/integer-mult-bounds/pull/2942)) with Jeremy Kothe’s fourteen paid gate rewrites ([PR #2957](https://github.com/CrocSwap/integer-mult-bounds/pull/2957), extending [#2948](https://github.com/CrocSwap/integer-mult-bounds/pull/2948)). The new contribution is their proved compatibility, exact composition and literal T370 realization. The constituent mechanisms retain their authors’ credit. Our first retiming pair duplicates two of Kothe’s published moves and is applied only once.

| Actual complete construction | Directed complex endpoint |
| --- | --- |
| Common #2930 anchor | [0.00172249990644327456435700, 0.00172249990644327456435701] |
| Normal 45 only, explicit cap fill | [0.00172281727074284952090995, 0.00172281727074284952090996] |
| Fourteen rewrites only | [0.00172371741507073817097131, 0.00172371741507073817097132] |
| Both mechanisms | [0.00172403522474810487855052, 0.00172403522474810487855053] |

The normal-45 and fourteen-rewrite leave-one-out effects exceed 20.69% and 79.32% of the joint gain over the common anchor. The five added swaps alone contribute a marginal above 23.51%; they are a subset of the rewrite block. Marginal effects are not an additive partition. The tiny packing closure is disclosed separately.

Both words have local profile {1:2430, 2:628, 3:282, 4:110, 5:26, 8:8}, 408 ordered helpers and 86 restored private buffers. The literal schedule has 370 replicas, 3,330 calls, 1,358,640 roles and 332,024 physical registers. Its complete profile is {1:8178480, 2:2091240, 3:968364, 4:366300, 5:117660, 8:26640, 48:136456}. Actual words and literal owners establish these invoices; a fractional relaxation is not a schedule.

Read [the informal proof](PROOF.md), [operator composition](COMPOSITION-PROOF.md), [independent arithmetic](INDEPENDENT-ARITHMETIC.md), [validation scope](VALIDATION.md), [frontier](FRONTIER.md), [four-worker techniques](TECHNIQUES.md) and [credits](CREDITS.md). Most new trial transfers had no recursive gain. No claim that eight broad methods were previously unused is made.

## Replay

The standard-library command `python -B verify.py --work FRESH_WORK` freshly regenerates eight scenario words, checks all forward/dual columns, four complete owner assignments, two exact moment engines and ablations, and records a finite-only receipt. This candidate package defaults to finite verification. `--bind-release` is reserved for a later package with completed admission and outer receipts; those receipts are not present or claimed here.

`python -B reproduce.py --repo LOCAL_REPOSITORY --work FRESH_FULL_WORK --jobs 2` authenticates the exact predecessor Git exports, builds the source and allocation, runs two fresh changed-word native chains and complete admission/outer release. Required predecessor heads are in [SOURCES.json](SOURCES.json). `--retained DIRECTORY` explicitly reuses an authenticated bootstrap; the changed-word native chains still run freshly. `--dry-run` checks exports and the plan only.

Full replay uses Python 3.13 and [requirements.txt](requirements.txt); the bounded verifier uses the standard library only. On Windows, inherited generators require LF serialization for exact manifest pins. `python tools/create_runtime.py --out FRESH_RUNTIME` creates a separate virtual environment with that local rule; install the requirements into that new environment. Existing Python/Git configuration and commit identities are not changed. Linux/macOS already use LF. Assertions must remain enabled.

## Open next questions

Try an explicit source-dependent carrier transport with dyadic synthesis and a better complete frame bill, or a new endpoint extraction compatible with the actual cut/warp interface. Start from the delivered words and reprice all consumers and owners. The fixed single-accumulator boundary in #2952 is not a general impossibility theorem. The scalar CSE and diagonal-gauge screens tested here leave H unchanged and supply no κ gain.

All-size/compiler, common-label and mutable-source realization, hosting, precision/tape, exact recovery, analytic, recurrence and bit-supplier assumptions remain conditional. No unconditional multiplication theorem, Lean formalization, measured runtime gain, global optimum, selected-frontier update or independent human review is claimed. Apache-2.0; retained notices apply.
