# [Lean] Explicit-tape reversal and paired binary input preparation

This small standalone Lean 4.21.0 package contains two concrete finite-state machines and their complete configuration proofs. Its four source modules total 48,221 bytes and import only Lean itself.

## Completed statements

### Word reversal

`CurrentMain.BinaryWordReversal.reverse_run` starts a six-state, three-tape machine with a canonical Boolean word on input A, an arbitrary explicit spare tape, and a pristine output tape. Its complete halted endpoint contains exactly `Tape.ofWord bits.reverse` on the output, with no extra output cell. The entire spare tape is preserved. The input acquires the precisely specified visited-blank representation; it is not restored to its initial head position.

The proved elapsed run bound is one transition for the empty word and `3 * bits.length + 2` for a nonempty word. The output head is at the first bit. The theorem is a halted-run statement; no separate minimal first-halting theorem is claimed.

`input_value` proves the endian identity `sourceMSBValue bits.reverse = wordValue bits`, where `wordValue` is little-endian and `sourceMSBValue` is defined explicitly. Reversal is not asserted to preserve the little-endian value of the unchanged word.

### Paired input preparation

`CurrentMain.BinaryInputPreparation.prepare_run` starts a fourteen-state, four-tape machine on arbitrary finite Boolean words `x` and `y`, with two pristine work tapes. Let `n = max x.length y.length`. The machine pads the shorter input with high zeros, reuses the reversal machine twice, and seeks to both work words' right ends.

It proves a complete halted endpoint within `6*n + 7` transitions, including empty and unequal-length inputs. Each work tape has record `endTape (paddedInput.map bitSymbol)`: its head is the right blank, its right list is empty, and its nearest-head-first left list is the padded little-endian input. Read left-to-right, the work word is therefore MSB-first and has the original numeric value and length `n`.

The paired endpoint is deliberately not `Tape.ofWord` with a first-digit head. The paired theorem has exactly four tapes, two of them initially pristine; there is no additional arbitrary spectator tape in that public contract. The two original inputs also acquire their specified final representations. The `n` in the theorem is a proof-side length, not a runtime counter supplied to the finite transition table.

## Scope and reuse

The reusable contribution is a checked implementation in the explicit finite-list-tape model: exact tape records, heads, values, halting and concrete linear run bounds. Reversal, zero padding, convolution identities and finite-state-machine concepts are standard, and no priority claim is made for those generic ideas. The paired program directly reuses the accepted reversal proofs rather than a second reversal derivation.

These files do not implement the source's single `x#y` prelude, binary length counter, radix grouping, complete multiplication caller, `Plan`, `ModelFamily`, compiler builder or represented-error budget. They do not prove a multiplication exponent. Source-caller preconditions and accounting must be established before inserting these machines into an end-to-end construction.

The word “source-only” in the reversal file's introductory comment is retained historical staging text. The exact source bytes now have accepted kernel receipts; the comment is not a claim that the whole source program is implemented.

## Explicit project-context kappa

The retained project source at `3b6b66891c0ac888521cf591fe306c6286601d4f` records the conditional parameter

`kappa = 330942774629799 / 500000000000000000 = 0.000661885549259598`.

This value is the retained source’s conditional project parameter, subject to its analytic, uniform-recursion and fixed-tape interfaces. None of the four generic machine modules states or proves this multiplication bound. The precise machine statements and this limited historical attribution have been author-checked against the accepted sources and pinned certificate. See `AUTHOR_CHECK.json` and `PROVENANCE.json`. The exact package has also passed a fresh isolated replay; publication remains a separate step.

The newer upstream main observed at `12a4934d15006e8c10f9b2264f13f8f341be802b` reports `90446448750933 / 125000000000000000 = 0.000723571590007464`. That is a distinct target; this package makes no source-program reconciliation or bound claim about it.

## Reproduce

Use Linux with `/proc`, Python 3 and the official Lean 4.21.0 distribution selected by `lean-toolchain`:

```
python3 check.py --lean /path/to/lean-4.21.0/bin/lean --build-dir .build
```

The checker validates every exact source hash, import and compile order, then uses a fresh output directory with no previous objects or extra library paths. Each process has a 60-second / 4-GiB hard limit and stops for review above 40 seconds or 3.5 GiB. It records per-module source/object hashes, logs, printed axioms and separate queue/compiler measurements. The runner's resource measurements require Linux; the Lean sources have no Mathlib dependency. No installation or network access is performed.

All four historical source-matched checks passed. The 18 printed probes use only standard axioms; `Classical.choice` is explicitly reported for `prepare_run`. The fresh isolated replay on 2026-10-11 passed all four modules in 10.2832 compiler seconds, with 0.00547 seconds in the shared-slot queue. All four object hashes and all 18 printed axiom sets matched their historical accepted checks. See `REPLAY_SUMMARY.json` for exact measurements and per-module evidence. Compiled objects and private runtime paths are not included.
