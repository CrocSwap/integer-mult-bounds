# Invert the eight-mode coupled native provider

This package gives an exact native inverse of
[PR #5402](https://github.com/CrocSwap/integer-mult-bounds/pull/5402) at
`3348fccea855082786d5f0fc5558b73d4974e745`. All 632 original input directions
are retained and all nine owned fields return zero. The inverse uses the same
paid profile: `{1:2193,2:412,3:510,4:127,5:40}`. It adds no Gaussian child.

The construction removes the unused C0 accumulator, reverses the remaining
native operations, and uncomputes the eight retained copies by subtraction.
The complete physical boundary is reversed with its exact phase. Positive
Gaussian implementations of the inverse children need at most 3,282 additional
ordinary bit translations. These operations are explicit costs.

**This does not increase kappa.** The eight mode outputs remain coupled.
A profitable complete caller, full compiler/precision bill and outer admission
remain open. Reversing a source operation also reverses its D factor; it does
not supply an independent fresh-D call by itself. The selected frontier is
unchanged.

[PROOF.md](PROOF.md) gives the ordered physical inverse, all-width argument,
chronological schedule and local bill. [RESULT.json](RESULT.json) records the
exact replay receipt. The verifier runs the pinned predecessor replay, checks
both compositions on all original columns, checks a separate inverse formula,
and rejects changes to COPY sign, zero-retag input and boundary phase.
It checks 464 boundary adjoints and the phase-correct inverse-child identity
for ranks 1 through 9. No independent human or formal-kernel review is claimed.

## Reproduce

Python 3.12 and its standard library suffice for mathematical replay.
The optional source-history preflight also needs full Git history. From the
repository root:

```sh
python3.12 -B scripts/research_package.py --package research/native-coupled-inverse
python3.12 -I -O -B research/native-coupled-inverse/verify.py
python3.12 -B scripts/check_research_commit.py --package research/native-coupled-inverse --check-source-history
```

Expected final token: `PASS_SAME_PAID_NATIVE_TWO_SIDED_INVERSE`.
The default verifier is read-only. `--emit` writes RESULT.json for authors.
[VALIDATION.md](VALIDATION.md) records executed checks and unrun obligations.

## Sources and credit

Dillon supplies the coupled provider, its all-input basis and physical boundary
in [PR #5402](https://github.com/CrocSwap/integer-mult-bounds/pull/5402).
The [source proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3348fccea855082786d5f0fc5558b73d4974e745/research/native-rank8-helper-provider/PROOF.md)
and [attribution](https://github.com/CrocSwap/integer-mult-bounds/blob/3348fccea855082786d5f0fc5558b73d4974e745/research/native-rank8-helper-provider/ATTRIBUTION.md)
remain part of the review. SOURCE.zip contains the exact source files needed
to replay that pending construction without a network or an unmerged Git
object. ORIGINS.json records their source paths, Git blobs and byte hashes.
The archive retains the original README, proof and attribution. It is unpacked
only to a private temporary directory. No predecessor code is changed.

Ali Romman's [PR #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383)
supplies the eight cached-center identities consumed by that provider.
Cao Yifan supplies the actual native word, Dugongue supplies the center-free
code, and Cinna Davis supplies the retained-cache/helper/controller lineage.
Retain zxv's native and Clifford work, Jacob Alan Sussman's mixed-target
recursion, Ryanson Jonathan's controller checks and the full source notices.
Yiyang's [PR #4966](https://github.com/CrocSwap/integer-mult-bounds/pull/4966)
already constructs owned-center inverses for the original word by recomputation.
This result uses the new retained-cache interface and its eight zero outputs;
it does not claim the first native inverse or the general idea of uncomputation.

Canonical base: `1ec1119972c9aefe42525172d07b332fcff81cb4`, priority revision 7.
The [caller claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19156336)
takes Dillon's released handoff. The broader breakthrough goal is not complete.
New inverse construction, proof and checks prepared for Ali Romman with
substantial OpenAI Codex assistance. No subagents. Apache-2.0.

## Open next questions

Use the exact inverse to close one chronological caller that preserves useful
progress in the eight mode fields. First give every original endpoint and the
full paid/ordinary invoice. Only then run compiler, precision and outer
admission. [TASK.json](TASK.json) records this question and its open obligations.
