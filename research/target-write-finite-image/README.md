# Target-write finite-image successor

For a full-register restoring XOR word with `m > 0` target writes, the actual image of `I XOR projected` injects into `Fin (2^(m-1))`. With no target writes, that image is exactly the singleton zero vector. The locally kernel-checked Lean source extends [PR1598](https://github.com/CrocSwap/integer-mult-bounds/pull/1598)'s concrete donor-row certificate; it preserves all dirty input coordinates, chronological gates, feedback and repeated donor occurrences.

The positive-case statement is:

```lean
theorem restored_positive_image_bound {n : Nat}
    (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hpos : 0 < targetCount y w) :
    ∃ code : ActualImage (projectedDefect y w) →
        Fin (2 ^ (targetCount y w - 1)),
      ∀ a b, code a = code b → a = b
```

`M r c` means input column `c` contributes to output row `r`. `ActualImage` consists of full output vectors with input witnesses for the literal matrix-vector action. Witness selection uses `Classical.choose`; equal-output inputs need not have equal measurement codes. The combined statement handles zero target writes using truncated natural subtraction.

This is an explicit finite-ordinal injection. A conventional numeric rank or dimension bridge, helper-cycle necessity, finite-register reduction, BFS, 13-gate optimum and physical supplier/frontier consequences remain outside scope. [PROOF_NOTES.md](PROOF_NOTES.md) is the unchanged original producer explanation: its source-only and unrun-fixture language records the producer's historical status. The repaired source header likewise retains that status. The separate local kernel acceptance is recorded below and in [REPLAY.json](REPLAY.json). [A separate Pro semantic review](REVIEW.md) found no material mathematical or statement flaw and recommended no source repair. Its own bounded checker passed local normal and optimized Python 3.12 runs: 256 models, 1,024 inputs, all 916 preimage choices, six words and ten rejected alternatives. It did not run Lean or inspect the producer Python checker; local kernel evidence is separately attributed. No human review is claimed.

## Reproduction and evidence boundaries

With Python 3.12 and an installed Lean 4.30.0 at commit `d024af099ca4bf2c86f649261ebf59565dc8c622`, run from this package:

```sh
LEAN=/absolute/path/to/lean-4.30.0/bin/lean python3.12 -I -B replay.py
```

The dedicated wrapper authenticates both Lean sources and theorem inventories, compiles the unchanged 34,181-byte dependency, requests all 78 predecessor reports, and compiles the repaired successor with all 43 reports. Fresh temporary outputs, zero exit codes and complete reports are required. Only `propext`, `Classical.choice` and `Quot.sound` are allowed; any error or `sorryAx` fails. The complete local dedicated replay passed in 5.014 seconds, with all 121 reports accepted and the stated three-axiom union. The exact repair was supplied by GPT-6 Pro at four proof sites without changing statements or definitions. The original failed candidate is retained only as historical evidence in the receipt.

The generic [VERIFY.json](VERIFY.json) hook is separate. It runs the unchanged finite Python checker and eight reused report-parser controls, under Python 3.12 in optimized mode. The registered metadata and generic commands passed. The third command runs the separately authored reviewer controls. Separate altered-source and mismatched-approval controls were rejected before compilation. It does not compile Lean. Local normal and optimized finite runs matched: 297 factorization models, 1,137 full-input evaluations, 511 bit lists, six restoring-word fixtures and five semantic controls. The complete result matches the producer's output after excluding only the Python-version field, 3.13.5 versus local 3.12.14.

Exact source bindings are in [SOURCES.json](SOURCES.json). Package base is fresh main `418e40eb2572d930b58c1cf9b82b41c0fc7ee08d`, priority revision 3; [the existing claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1548#discussioncomment-18915295) retains its earlier source base. The pinned PR1598 dependency is pending upstream work, separately identified from main. Only its needed unchanged Lean source and small reporting controls are included.

## Open next questions

[TASK.json](TASK.json) specifies the remaining conventional rank/dimension bridge: choose a library and connect its exact matrix action and image to this injection theorem, without changing coordinate or restoration hypotheses.

## Credit

Andrey Mas, with substantial GPT-6 Pro assistance through ChatGPT, supplied the mathematics, Lean source, proof notes and repair. Codex supplied source coordination, execution audit, mechanical replay and packaging. Credit [PR1546](https://github.com/CrocSwap/integer-mult-bounds/pull/1546)'s written lemma, [PR1598](https://github.com/CrocSwap/integer-mult-bounds/pull/1598)'s coefficient certificate, Gareth Davidson / @bitplane's [PR1420](https://github.com/CrocSwap/integer-mult-bounds/pull/1420) lineage and @woklerx's [PR1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105) feedback work. No novelty is claimed for the prose lemma. Apache-2.0; original source headers preserved.
