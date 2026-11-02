# Publication description

Publication was authorized on 2026-11-02. The title and body below are
prepared for the contribution PR. Hosted CI status is updated in the PR;
local validation records retain the status at their stated commits.

Proposed title:

**Mixed-query root: conditional κ = 0.00328621476572836015146308 (+4.28455% over #6375)**

---

## Change and result

A new six-field query caller raises **conditional κ from 0.00315120 to 0.00328621476572836015146308**, a **4.28455% increase over [PR6375](https://github.com/CrocSwap/integer-mult-bounds/pull/6375)** with the same pinned native source. The resulting conditional time bound is `O(n (log n)^(1−κ))`. The selected frontier is unchanged.

The improvement comes from a different way to combine recursive suppliers. The caller uses four binary children of sizes **7,2,2,7**, with full-stage projector ranks **2,3,3,2**. It pays two additional whole idles and obtains six independent outputs with stage products `ABCD, AB, CD, empty, B, C`; every output also contains the central transform. The complete caller uses **18 native calls**, **67,150 paid jobs** and **13,652 productive fields**, with rank-mass surplus **760**.

Two steps make this possible:

1. **Normalize the complete field.** An ordinary translation-based map turns the native central query into an involution, then restores the required Gaussian outputs. Its scalar coefficients stay outside tensor powers. All normalization and basis-change work is charged.
2. **Permit paid higher-rank stage projectors.** The six-field root combines full and thin queries in a pattern unavailable to the preceding binary root. The literal 570-event caller charges every native call, helper debit, query, idle, adapter, owned lifetime and route.

The final composition includes [PR6353](https://github.com/CrocSwap/integer-mult-bounds/pull/6353), [PR6372](https://github.com/CrocSwap/integer-mult-bounds/pull/6372) and PR6375, with each source change and productive debit applied at all 18 calls. Those native mechanisms retain their original credit. The final refinement of completion/compiler parameters adds only **0.000449325%** over the local 0.00328620 checkpoint; the **4.28455%** comparison is the complete caller improvement over pinned PR6375.

## Proof and how far the method goes

The package proves the **exact raw funding limit** for the fixed source and classified root family:

```text
0.00328621476572836015146309 < κ* < 0.00328621476572836015146310
```

The complete claim is less than `2 × 10^-26` below this limit. The proof covers all positive binary child sizes and tree shapes. An exact recurrence, comparisons of all eleven seven-leaf tree histograms, and a concave infinite-tail bound establish the optimum. A direct rational comparison proves that the selected profile dominates throughout the crossing interval.

The family has six arbitrary fields, seven square-zero queries, four independent forward full stages and at most two extra whole idles. All outputs contain the central involution; scalar bases are independent of it and of the stage variables. The bound concerns the recursive invoice; the chosen word has its own complete ordinary-work budget. **This is a family-specific limit. Equality at κ* is not certified by the strict completion argument.**

Supplementary research includes the all-width normalization proof, the minimum-idle classification, a separate reverse caller, an active-space reduction for extra central-free outputs, and all-size price exclusions for seven specified fifth-stage extensions. It also preserves a helper-consuming module and a five-call reflection border. The border has two nonzero errors and no complete recovery/precision construction, so its favorable formal price is **not a κ result**.

## Review map

| Read | Purpose |
| --- | --- |
| [Root proof](../mixed-projector-query-root/PROOF.md) and [literal caller](../mixed-projector-query-root/CONTROLLER.json) | New construction, whole-field normalization and exact endpoint |
| [Final composition proof](PROOF.md), [receipt](RESULT.json) and [source manifest](SOURCES.json) | Native binding, all source changes and the complete invoice |
| [Family proof](../mixed-projector-root-headroom/PROOF.md) and [exact optimum](OPTIMALITY.md) | Quantified scope, all-size exclusion and strict approach to the limit |
| [Research map](RESEARCH-MAP.md), [boundary modules](../mixed-projector-root-headroom/BOUNDARY-MODULES.md) and [author review](REVIEW.md) | Earlier advances, useful negative results, repaired proof gaps and remaining questions |

Four scoped packages are added. The PR6353 intermediate composition retains the executable source closure. Earlier published results and nine exact null-witness rejections are documented with their scope and attribution; they are not counted as new gains here.

## Verification

Local registered normal/optimized replays pass on CPython 3.12.13. Checks cover **799 native columns, 638,401 reverse coefficients, 7,488 physical caller contacts**, two rational moment engines, completion/compiler bounds, ordinary costs, and **54 strict plus four functional outer predicates**. The separate reverse caller checks 4,624 formal polynomials. Source and semantic rejection controls, committed-byte/source-pin checks, and isolated read-only exports pass. The new dominance guard rejects a deliberately invalid bound under optimized Python. [Exact evidence and limits](VALIDATION.md).

```sh
python3.12 -B scripts/research_package.py --package research/mixed-root-contact-composition
python3.12 -B scripts/research_package.py --package research/mixed-projector-root-headroom
```

Hosted CI is pending at opening; its exact-head result will be recorded here.

The five inherited assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. The constants are theoretical; the uniform word and rounded multiplier are not materialized. Independent scientific review and formal-kernel acceptance remain open. The earlier [PR6376 scalar audit](https://github.com/CrocSwap/integer-mult-bounds/pull/6376) does not discharge physical erasure. No practical speedup or unconditional multiplication theorem is claimed.

## Task, overlap and credit

Task: `joint-query-controller`, refined to a new mixed-projector root. Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. Native source: PR6375 at `247b5c319b9f58fe9ee61dbf80697f8a9a429831`; all other exact dependencies are in the manifests. Main, recent open PRs and active Discussions were refreshed before publication.

Nick Petalas's [PR6380](https://github.com/CrocSwap/integer-mult-bounds/pull/6380) studies the older nineteen-leaf binary topology; this PR changes the root and uses eighteen native calls. His [PR6391](https://github.com/CrocSwap/integer-mult-bounds/pull/6391) prices a different three-stage overlap proposal. The [active PR6375 scalar audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19359707) remains separate. [Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19209322).

New root, normalization, composition, proofs and author checks: **Ali Romman with substantial OpenAI Codex assistance; no subagents**. DreamingOfClouds supplied PR6375 with Claude Opus 5.5 via Claude Code. PR6348 supplies the binary module; PR6349 and its predecessors supply the native lineage. Credit Cinna Davis for the query/caller interfaces, Jacob Alan Sussman for productive recursion, and zxv and Cao Yifan for the interval/compiler lineage. All native, helper, geometry, BIT and analytic notices are retained. Apache-2.0.

## Open next questions

Independent review should check the normalization, classification and complete native-to-caller bill. A larger raw gain must change a stated source or root hypothesis; a border extension first needs an affordable recovery and recursive precision proof. [Concrete follow-ups](README.md#open-next-questions).

This PR changes only the four research packages. It requests neither a merge nor a selected-frontier update.
