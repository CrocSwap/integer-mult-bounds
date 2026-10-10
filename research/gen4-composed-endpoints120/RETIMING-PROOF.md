# PR279 retiming composed with dirty-target sinks and helper kernels

## Claim and provenance

This is a concrete composition of PR279's 880 source-source frame retimings with the separately checked GEN4 word, terminal-sink elimination, and helper-kernel entrance changes. It does not claim a new source-source retiming invention. The new work here is the exact rebasing and independent admission of all 880 moves on the changed word, preserving the sink and kernel gains in one priced construction.

The imported selection is from CrocSwap/integer-mult-bounds PR279, commit `2e2a38ba3f48edbda2152ed86691c75ff326b254`, file `research/five-stage-gen4-banks/descent-selection.json`. Original author and upstream licence/attribution notices remain applicable. PR279's latest commit checked in this round is `4d8c31eec7ae618645cb058101cb4e72a97268d3`. Its only changes are `prime_check.py` and the corresponding manifest hash; the construction and selection are unchanged. It retains determinant obligations for producer frames no longer executed after retiming.

The original GEN4 raw record hash used to bind the selection is SHA-256 `60830cb24fbdd5a26942c4aa897d0ae30738ca5772ab83d6c57be666ddc95f7a`. The 722477-record original word is pinned separately from the transformed word. `bind279.py` checks every original scalar gate, old-frame dimension, and old-basis SHA-256, then stores the exact old basis in the portable selection. The native retimer checks that exact basis again against its actual input frame table. Original record numbers are provenance, never rewrite offsets on a changed word.

## Sufficient local identity

A source register carries a linear combination of original source patterns chi_s. If all these patterns lie in a nondegenerate frame F, an ADD between two such registers may be executed in F after moving both registers to F. The represented linear map is unchanged: it is the same signed ADD on the same two data registers. A target's support immediately before an ADD is contained in the union of its support immediately after the ADD and the control's support, so checking the latter two supports suffices for both sides of the event.

This admission requires actual source support, not just a nested pair of geometric frames. The checker therefore replays exact signed integer coefficients from one independent variable for *every* initial data register, including every dirty helper and dirty target. At each selected source-source gate it rejects any surviving dependence on a nonsource input. It checks each nonzero source pattern against every annihilator row of the chosen F using arbitrary-precision integer dot products. Original source patterns are recovered from their rank-one initial bases, and the relation `3 chi_s - 1 = source_covector_s` is checked entry by entry against the exporter.

Every chosen frame is an existing baseline rank-22 common delivery frame. Its Gram matrix for the actual form `G = I - J/9` is checked invertible over the rationals. No positive-definite or Hermitian-form assumption is made. Replacement-frame inverses and determinants pass the finite coefficient guards. Initial/final frame identities are not changed.

## Rebinding, chronology, and controls

A selection entry is matched to the current word by its signed scalar tuple `(target, control, multiplier, category)` and its exact old frame. Nonunique or absent occurrences are rejected, never guessed. On the selected 16-sink plus 741-kernel word all 880 occurrences match uniquely. Source roles are below 1760 and are not renumbered by helper compaction.

The implementation discards and reconstructs only MOVE records from the actual scalar/COPY event sequence. Every required containment is tested using arbitrary-precision integer products of the actual basis and annihilator matrices. It preserves all 24 COPY windows and their frame endpoints, the original initial/final frames, and the complete ordered signed scalar/COPY projection. Thus it does not inherit an obsolete schedule or use source-copy renaming.

There are 880 deliberately undersized-frame controls: replacing the proposed common frame by the receiving source's initial rank-one frame fails for at least one actual source pattern at each selected gate. This rejects vacuous support checks. The final receipt explicitly records all dirty inputs replayed and source-purity admission.

## Actual recursive census

For 16 sinks and 741 kernel entrances, the unchanged rank mass is 423806. Retiming removes exactly 880 recursive calls, changing the local histogram by

    rank 1:  -1760
    rank 2:   +880
    rank 20:  -880
    rank 21: +1760
    rank 22:  -880

The call count is 95025 before and 94145 after. The same delta holds on the 11-sink plus 746-kernel alternative; its unchanged rank mass is 423875. These are actual regenerated MOVE/COPY counts, not added percentage estimates.

For a recurrence exponent p strictly between zero and one, the per-move change is `2^p + 2*21^p - 2 - 20^p - 22^p`. It is negative: the discrete concavity defect `2 f(x+1)-f(x)-f(x+2)` of `f(t)=t^p` strictly decreases with x, so its value at 20 is less than its value at zero, which is `2-2^p`. Thus this histogram strictly improves the local moment while conserving rank mass. The full admissible kappa still comes only from repricing the entire composed construction and every finite/outer constraint.

## Finite-field coverage

The portable package first replays the original PR276 package, including its prime checker, before any sink/kernel/retiming transform. That retains the producer-frame obligations which PR279's latest patch protects. Every retiming replacement basis already exists in that original frame table. Kernel-specific charts receive their own exact finite-field admission. Together these checks cover both original producer bases and all bases actually consumed in the composed word; retiming introduces no additional basis requiring an unprovided prime certificate.

## Portable files and invocation

Compile `retime279.cpp` with `retime-support.hpp` in the same directory and the inherited JSON/Boost headers on the include path. The support file is a header to prevent an accidental second standalone compilation of its inherited bank-checker entry point.

    retime279 BASE_EXPORT CURRENT_KERNEL_LEAD inputs/retiming.json OUT_DIR

The output consists of `RETIMING279.json`, `COHORT249-RECORDS.bin`, `COHORT249-REPLAY.json`, `COHORT249-FRAMES.json`, `COHORT249-INITIAL.json`, and `COHORT249-SELECTION.json`. The first receipt contains occurrence bindings, all 880 exact source checks and controls, rational Gram guards, chronological containment counts, and the histogram delta.

The native retimer's claim is local exact source/geometry/projection correctness. The separate package driver must still replay full forward/inverse columns, all bank/finite invoices, and the final constraint engine. Those independent audits, not a discovery estimate, determine the published conditional bound. Nothing here is a Lean certificate or an unconditional sub-n-log-n integer multiplication result.