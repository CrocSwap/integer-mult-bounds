# Streaming Gaussian phase tariff

**Local algorithmic improvement; no new kappa.** Use direct streaming for
even Gaussian phases and one real-half scratch tape for odd phases. The
complete payload bill is `9V+(9/2)V_odd+h`, instead of the retained source's
`18V+h`. Here h is the initial head offset and V_odd is the volume with an
odd phase. From origin, this saves 25 to 50 percent of phase payload work.

The [proof](PROOF.md) covers all valid complete record layouts and coefficient
widths. The unchanged phase polynomial, affine word and compact interpreter
are composed in [phase.py](phase.py). No frozen source file is changed.
The actual event8814 right and left phase passes each save 37.5 percent:
589824 to 368640 transitions. [RESULT.json](RESULT.json) records these values.
This is a component tape invoice, not an end-to-end runtime or kappa gain.

## Replay

Use CPython 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/streaming-gaussian-phase-tariff
```

Expected status: `PASS_STREAMING_GAUSSIAN_PHASE_TARIFF_NO_NEW_KAPPA`.
The registered hook runs normal and optimized modes and checks source hashes
and a typed exact receipt. Evidence includes 21824 coefficient/phase cases,
768 tensor phase patterns, four actual complete monomial cases, two compact
tensor round trips, three arithmetic discriminators and three input rejections.
Every new result agrees with the unchanged predecessor and an independent
integer phase oracle. All source ordinary calls and control evaluations are
retained. The official export permits a Git-free replay.

No full supplier, native catalogue replay, encoded-control lowering, Lean,
Docker or selected cold replay was run. Human and formal-kernel review are
unclaimed. The written scan proof supplies the uniform result. The complete
caller, recursive child, precision and supplier budget remain separate.

## Attribution and scope

Base `7c472563474e60185e6ca101a17622133d047e56`, priority revision 7.
[SOURCES.json](SOURCES.json) pins consumed files; selected-result and catalogue
files are historical provenance. Jose Manuel/jmbarrancoml supplied the source
scan, affine/compact routines and proof in
[PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250).
Douglas Colkitt's compact construction remains credited there. JoyboyBrian's
[PR #5327](https://github.com/CrocSwap/integer-mult-bounds/pull/5327)
binds the actual event8814 fixture to Cinna Davis's mixed caller and retained
native/Clifford lineage. The Word RAM phase work in
[PR #4538](https://github.com/CrocSwap/integer-mult-bounds/pull/4538)
and Gaussian normalization in
[PR #3127](https://github.com/CrocSwap/integer-mult-bounds/pull/3127)
are related work with different operations and cost models, not consumed
implementations or new results claimed here.

Prepared by Ali Romman with substantial OpenAI Codex assistance. New code and
proof: Apache-2.0. Existing source notices remain unchanged.

## Open next questions

Lower this scan onto the encoded physical coefficient/Count interface and
charge the phase controls there. Use the exact component bill and preserved
ordinary-call inventory as comparison points. The full caller and recursive
child are required before any complete supplier gain can be claimed.
