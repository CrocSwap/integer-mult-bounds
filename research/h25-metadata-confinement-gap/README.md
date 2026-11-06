# H25 artifact metadata confinement gap

The unchanged public full caller requires an artifact permission change before compilation. Linux v6.12 Landlock filesystem rules do not confine that class of metadata operation. Blanket metadata denial therefore breaks the positive caller; blanket allowance, together with generic seccomp rules, does not prove an artifact-only metadata boundary.

This is a source-based negative finding about that proposed boundary. It reports no observed GCC escape, current-kernel experiment, universal impossibility, completed sandbox implementation, full-caller execution, measured performance or mathematical improvement.

## Public evidence

The [full caller published by PR #6744](https://github.com/CrocSwap/integer-mult-bounds/blob/1ac58a84b725bd6f17eec66727edc877c49c7e66/research/h25-full-caller-readable-inputs/full-candidate.py.txt#L964-L971), exact head `1ac58a84b725bd6f17eec66727edc877c49c7e66`, first makes two fresh recursive copies and then calls `runtime.chmod(493)`. Decimal 493 is octal 0755. Its 104,276-byte source has SHA-256 `fa9f473320e9df3a2328bd8388f12eca4e7fc3eeed9289f7fdbf2eeb32a7452f`. The explicit permission change alone establishes the required positive metadata edge; no association between a reference CPython release and an installed distribution is needed for that conclusion.

The [Linux v6.12 Landlock UAPI limitation](https://github.com/torvalds/linux/blob/v6.12/include/uapi/linux/landlock.h#L236-L243) (Git blob `33745642f7875a17261fc584322a46f8c894b86f`) identifies chmod, chown, setxattr and utime among operations that its filesystem rules cannot restrict. This list does not imply that the caller requires chown. Selecting all filesystem rights does not add rights that the interface lacks.

A classic seccomp filter can inspect syscall argument values but cannot dereference a pathname pointer and safely resolve it to an artifact-owned object. A syscall-number allowance, caller-provided descriptor number or textual path prefix is not such an ownership proof. See the [kernel seccomp filter documentation](https://github.com/torvalds/linux/blob/v6.12/Documentation/userspace-api/seccomp_filter.rst). A notification followed by permission to continue the original syscall also leaves target substitution unresolved; see the [kernel seccomp notification warning](https://github.com/torvalds/linux/blob/v6.12/include/uapi/linux/seccomp.h#L75-L109).

## Open next questions

First decisive check: independently review one concrete target/effect contract against both a genuine owned artifact target and an out-of-scope alias, including actual errors, partial effects and death before sealing. No such implementation or check is claimed here.

A successor needs a concrete artifact-only metadata boundary, with independent source review before implementation qualification. Two possible directions are genuine target-and-effect mediation or a proved filesystem view that prevents out-of-scope mutation through every accessible alias. This packet selects neither implementation.

The interface must bind each bounded request to the actual owned artifact root, caller generation and a held kernel target identity. Resolution must cover dirfd and working-directory semantics, symlinks, magic links, hard links, renames, descriptor reuse and follow/no-follow flags. It must prevent substitution between validation and the real effect, intercept equivalent operation variants, and suppress the original unsafe operation when substituting an effect.

For permitted targets it must perform the real operation and preserve operation order, partial effects, actual return values and errno. Policy refusal must remain distinguishable from an ordinary permitted-target error even if caller code suppresses that errno. Caller or mediator death after effect entry requires retained actual state or an honest unknown result, without automatic replay.

Every mediator, channel, target handle, effect-capable alias and pending request must enter the real ownership and lifetime chain. Sealing must prevent new effects and establish completion or retained refusal/uncertainty for pending work; unknown effects or live mutation capabilities prevent seal. Existing retention ownership is a dependency for that integration, not an artifact metadata service.

## Lineage and scope

Coordinate through the [original investigation, PR #6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321), preserving the [original benchmark, PR #6029](https://github.com/CrocSwap/integer-mult-bounds/pull/6029). The readable caller in [#6744](https://github.com/CrocSwap/integer-mult-bounds/pull/6744) comes from [#6715](https://github.com/CrocSwap/integer-mult-bounds/pull/6715), head `dc34598c22e2ef43ae7e11fc1d8c14de3915cf89`. The distinct [capture/guardian/retention source in #6736](https://github.com/CrocSwap/integer-mult-bounds/pull/6736), head `0f2a86fa9ef0daf760b77c662a5b762e17848598`, supplies ownership components to preserve and integrate; it does not close this metadata boundary. No predecessor source is modified or duplicated here, and no broad novelty claim is made.

The caller's [owned compiler temporary directory](https://github.com/CrocSwap/integer-mult-bounds/blob/1ac58a84b725bd6f17eec66727edc877c49c7e66/research/h25-full-caller-readable-inputs/full-candidate.py.txt#L950-L953) remains a separate source fact. This finding does not reopen the previously resolved process-fallback or temporary-directory questions.

## Validation and credit

The package contains four inert documentation/metadata/license files. Preparation checks JSON syntax, the exact file inventory, non-executable ordinary-file modes, hashes and text scope. No candidate source, compiler, native control, kernel probe or scientific workload is executed, and no replay hook is registered. Hosted planning or skipped replay supplies no execution credit. Exact publication identities belong to the submitted commit and its external allowlist.

Chris R / Clear1nsight, original H25 and CrocSwap authors and reviewers, Douglas R. Colkitt, predecessor contributors and the cited Linux authors retain their credit. OpenAI Codex and ChatGPT Pro assisted the analysis; a distinct GPT-6.1-sol Max source review assessed the missing interface. AI source review is separate from human, proof-kernel and runtime acceptance. New text and metadata are Apache-2.0; cited external sources retain their own licenses and are not copied or relicensed.
