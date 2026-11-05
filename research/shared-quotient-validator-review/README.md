# External review of the shared dispatcher certificate

This is a written proof-to-code review of Nick Petalas’s [PR #6124](https://github.com/CrocSwap/integer-mult-bounds/pull/6124), original head `9ae1d82f4e248dd830e32c4d2a0330b62cddc1dd`. It asks whether the actual refinement, sorted partition certificate, quotient homomorphism and reachability checks establish the stated ordered-coin behavior and counted-state minimum. The source proof and implementation are unchanged at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

The source owns its quotient, numerical partition, 22,482 internal states, 84,578-byte packed payload and finite control outcomes. This review does not compute those values again. Classical Moore minimization is credited as a method. The earlier single-sampler probability/phase/expected-bit review in PR #6747 addresses a different implication.

## Review and evidence

Read [REVIEW.md](REVIEW.md), then the exact [source proof](inputs/PROOF.md), [dispatcher](inputs/dispatcher.py.txt) and [certificate validator](inputs/verify.py.txt). Executable originals have an inert `.txt` suffix. [SOURCE-PINS.json](SOURCE-PINS.json) binds all six retained source objects; [SOURCES.json](SOURCES.json) records the canonical guidance and source provenance. The original [README](inputs/README.md), root [NOTICE](inputs/NOTICE) and [license](inputs/LICENSE) are retained exactly.

Separately sealed first drafts, their exposure records, subsequent cross-review and the assembled-version check are retained in this directory. The abstract derivation knew the target proposition but did not read source proof/code or the code-review draft before sealing. The code reviewer read the source first and disclosed earlier scouting. The coordinator had read that scout and source PR body before claiming, then the actual source. These are AI-assisted written roles, without a claim of blindness, human review or kernel acceptance.

The scope is the actual internally generated, finite, genuine-integer graph/certificate path. It includes empty-word observations; monotonic refinement despite omission of the previous own-color; equality of consecutive class counts despite class-ID renaming; sorted-group consistency and the global distinct-used-class count; complete roots, output labels and edges; reachability before stopping; all finite first-stop behavior and infinite nontermination; and the requirement to count every behavior-relevant residual datum.

Written weakening controls are **UNEXECUTED**. No source import, constructor, validator, minimizer, packing, source mutation or tape catalogue was run. There is no scientific `VERIFY.json` hook. Reading the proof and inert sources is the reproduction procedure for this written result. Byte/metadata/export checks and repository helper CI are separate evidence, never a scientific replay or mathematical acceptance.

## Scope and remaining obligations

The original `formal-interface-lemma` card is retained in full in [TASK.json](TASK.json), with scope explicitly **changed** to written review. Its formal/kernel acceptance gate remains unmet. Numeric partition history, the depth-nine witness, 36,864 tapes and the five source corruptions are inherited source evidence and were not rerun. Low-level validator functions do not independently validate every hostile shape/type; the actual generated path supplies their array and integer invariants.

The state lower bound fixes every ordered-coin function, terminal labels and first stopping depth, and counts all residual information after entry. It is not a minimum over samplers sharing only a probability law, a minimum ROM encoding, Python memory usage, or a physical controller-bit lower bound with uncounted parameters, clocks, histories or tape positions. Absorbing output loops are proof devices; a stopped sampler does not execute or store them as pending transitions.

The shared quotient does not inherit the predecessor-unique reversal or cleanup contracts of PRs #6102/#6127. Physical selection, lookup, access, random-tape movement and freshness, owned stopping records, restoration/cleanup, complete invoice/error, native all-columns, owned erasure, compiler, precision/tape, analytic recovery, outer assembly and full supplier remain obligations. All five selected assumptions remain. No multiplication theorem, runtime improvement, κ/frontier/adoption change or merge follows.

## Selection, overlap and credit

Canonical main and eight guidance bindings were refreshed at the round checkpoint. Selected record #6030, κ `781451/250000000`, takes precedence over stale prose referring to #5599. The baseline check is source bindings only. The latest handoff hub and Discussion index, all 698 open/draft PR bodies and heads across seven complete pages, targeted all-state searches for the exact package/#6124/state count, actual source PR and empty source-comment timeline were checked before the [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19428792). Sparse local notes, hidden Discussion history and unindexed work remain unknown; an empty search is not proof of novelty.

The prior 99 PRs and B13 results #6745–#6748 are excluded from this result count. Source #6124 is merged predecessor work, not this review’s new construction. The first overlap helper used system Python 3.9 and rejected the UTC timestamp; that unusable output is preserved outside the package. The unchanged cache was accepted with the required Python 3.12. No scientific input or result changed.

Nick Petalas supplied PR #6124’s exact quotient, complete certificate and packing. zxv supplied PR #6072’s ordered graphs, sampling law and expected-bit optimum, with its disclosed Codex assistance. Classical Moore refinement and the residual-behavior lower bound retain their original credit. JoyboyBrian’s #6096/#6102 caller and reversal work, Nick Petalas’s #6127 stopping-counter cleanup, and the earlier native/compiler lineage remain distinct predecessors. ToikY prepared this review with substantial OpenAI Codex assistance and separate abstract, code, metadata and byte-review roles. Original notices and licenses remain in force; no predecessor endorsement is implied.

## Open next questions

1. Can the exact sorted-certificate/refinement/homomorphism implication be formalized with literal source bindings? Start with observations and the global cardinality lemma; the written review does not supply a proof kernel.
2. Can one actual shared dispatcher’s complete physical caller be priced, including the retained discriminator needed for reversal? Bind selector, access, tape, stopping and owned restoration first. Logical payload bytes do not answer that question.

These follow-ons are unreserved. Publication requires maintainer edits and auto-merge to be disabled; the actual PR settings receipt is separate from these frozen files. No selected-frontier file is changed.
