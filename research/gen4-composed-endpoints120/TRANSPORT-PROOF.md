# Transported entrances after sinks and response kernels

The mechanism and the sixty proposed entrance bases are from PR280 by utcorvusvolat-dotcom, prepared with substantial OpenAI Codex assistance, at commit `f063aab8d6e514188e53db57218515df9cdd186e`. See the preserved `UPSTREAM-NOTICE.md`. The new work here is the native C++ port, compaction-aware filtering, revised legal insertion cut, and actual composition with sixteen terminal sinks, 741 response-kernel gauges and 880 common-frame retimings. It is not an independent invention of dirty-read transport.

## Sufficient signed transformation

Consider an elementary shear t += c*h, where h is a helper and t is a target. To move it later through a scalar instruction u += a*w it is sufficient that u != h and w != t. Under these conditions the two shear matrices commute over every commutative coefficient ring, with no assumption on clean data. A COPY that does not read t also commutes; the emitter conservatively excludes any COPY of h before the cut as well. This gives a universal sufficient identity, not only a successful sampled replay.

For each retained helper, the native emitter verifies all of the following on the actual compacted source word:

1. The public physical helper ID maps to a present role with the same virtual identity, ZERO initial frame and FULL24 final frame.
2. Up to the chosen cut, that helper is never written or copied. Its only scalar uses are exactly four signed initial helper-to-target reads at ZERO, with unit coefficient magnitude and the exact public target set.
3. None of those four targets is read as a scalar source or COPY source in the interval beginning at the first moved read and ending at the cut.
4. All moved reads retain their coefficient, source and destination, and preserve their original chronological order.

Thus each retained read commutes through every crossed instruction. Different moved reads commute with each other because their sources are helper roles and destinations target roles. Removing the original reads and inserting them at the cut therefore preserves the entire signed scalar transformation for arbitrary initial input and dirt. The rest of the scalar/COPY stream is retained in order.

## The cut must change after terminal sinks

The public insertion cut immediately follows the final copied-center discard. On the combined word, the sinks install extra target-to-target setup shears at ZERO immediately afterwards. Inserting the new reads before these would force some targets to descend from the new entrance frame back to ZERO, which is illegal. The first native geometry attempt detected that conflict.

The accepted cut is instead the last of: any copied-center discard, and any ZERO-frame scalar operation involving a target. The signed commutation contract is rechecked through this later cut. This rejects four candidates whose target outputs are sources in the sink setup. It is a concrete composition repair, not a relaxation of legality.

Of the sixty public entries, eight helper roles have been removed by sinks, nineteen helpers are written before the extended cut by the existing response machinery, and four have the target-source conflict above. Twenty-nine survive; all have entrance rank 18 and residual rank 6. No existing initially gauged helper is modified.

## Address geometry and verification

For each surviving public basis B, the native emitter recomputes rank, an exact integer annihilator A, and the nonzero determinant of B*(I-J/9)*B^T over exact rationals. It reconstructs every MOVE from the actual current frames, checks each new connector by exact basis/annihilator containment, keeps every endpoint, and checks COPY/ERASE lifetimes. The unchanged connectors inherit the already audited source word.

Each of the 29 transported independent helper columns is replayed over arbitrary-precision integers in the original and new words and compared exactly. All 19914 independent formal columns are also checked forward and inverse over F2 against the actual decoder. An omission control deletes all relocated dirty reads and must change the result. These are distinct from the signed commutation proof: the latter proves the transformation universally; the finite replays check its concrete implementation and bindings.

The unchanged root word has 16,394 helper roles. The transport raises total entrance rank by 522 and lowers paid local rank mass by exactly 522, from 423806 to 423284. Its literal local histogram delta is

    {1:+29, 2:+76, 3:+40, 18:+116, 19:-29, 20:-76, 21:-40}.

There are 116 relocated scalar reads. This preserves the old 741 kernel gauges and introduces 29 additional rank-18 entrances. The individual transport receipt is not an end-to-end kappa certificate: independent bank/chart, global-column, signed prefix, finite invoice and strict assembly audits must bind the final word, including any subsequent early-restoration or target-prefix transformation.

## Reproduction

Compile `transport.cpp` as C++17 with Boost headers and nlohmann JSON. Execute:

```
transport BASE_SINK_EXPORT ACTUAL_RETIMED_COHORT OLD_TO_NEW_JSON inputs/entrances60.json OUTPUT_DIRECTORY
```

The source cohort is read-only. The output directory is created explicitly. The successful actual cut is record 557202. Output binary SHA256 is `9b4d8755f3a11325e535d4fdf2772eb3d6e65062834b4b06523570168fecf12f`. All new source and output paths are supplied as arguments; no machine-specific path is embedded in the emitter.
