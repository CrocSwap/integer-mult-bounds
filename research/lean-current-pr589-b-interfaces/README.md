# Current PR589 B scalar interfaces

Author-checked source context: main `f567884aeb8851b6e794af1184119a3bfbe1e631`, conditional κ = **1661634653669567/10^18 = 0.001661634653669567**. This is the exact selected-result/ASSEMBLY value. The following Lean boundary does not itself establish that exponent or a full integer-multiplication theorem.

## Checked scope

Three unchanged Lean modules certify the selected PR589 B word on **661 Boolean registers**: 111 source registers, 111 target registers and 439 helpers. They bind **712 gates and 934 ordered operand occurrences** to the tuned input at PR589 `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.

The exact chronological bands contain 102 target gates, 499 off-target unary gates and 111 final target gates. The middle band includes 483 source writes and **16 helper writes on registers 465, 466 and 468**. Every other helper retains its arbitrary original Boolean value. Source preservation and preservation of those three helpers are not asserted.

No operand reads a target register. Under the actual sequential XOR semantics, perturbing the initial target bits perturbs the output by the same bits. Each output target is its original bit XOR a contribution independent of all initial target bits; that contribution is not assumed to vanish. The decoder preserves operand order, multiplicity and frame IDs without default reads. Frame IDs are metadata for this scalar interpreter.

## Minimal proof package

- `CurrentPR589BData`: exact ordered B literals and dimension constants
- `CurrentPR589BCheck`: 12 finite facts, with 11 kernel decisions
- `CurrentPR589PhaseBXor`: seven ordered-decoder and scalar semantic facts
- One retained public dependency: `BitXorTargetTranslation` from [PR590](https://github.com/CrocSwap/integer-mult-bounds/pull/590), with four printed generic probes

There are **19 new printed probes and 19 distinct new declarations**, plus four retained probes. The manifest lists all four local modules, with three fresh and one retained. The runtime uses the complete **317-module official Lean 4.21.0 core** and no Mathlib. The public prefix is checked and retained rather than rebuilt. No PR597 or PR612 finite source is imported or duplicated.

The existing research check passed all three roots in 7.181425992 compiler seconds, peak virtual memory 842,321,920 bytes. Actual FIFO waiting was 0.001374081 seconds; 8.328078750 seconds of post-slot guards is recorded separately. These are owner research measurements. The sole mutable public reproduction outcome is `REPLAY_SUMMARY.json`; concrete offline checker instructions are added with its separately reviewed checker.

## Source identity and reuse

`SOURCE_BINDING.json` pins the selected tuned gzip, decoded bytes and supplier/tuning files. Lean data projects only v, R, frame count and the ordered B list. External hash-reviewed correspondence is separate from kernel acceptance of the embedded literals. The checker does not execute an original supplier, regenerate the input or install packages.

`DEPENDENCIES.json` pins the one required accepted PR590 output and its complete probes. Portable predecessor receipts may differ in timestamps; source/object identities and complete log/probe checks remain mandatory. Only the previously reviewed three generic-XOR warning source-path substitutions may normalize. All other log content remains exact.

`ACCEPTED_CHECKS.json` records immutable prior checks; `AUTHOR_CHECK.json` records the static source and κ readback. `PROVENANCE.json` points to the single mutable replay receipt. The earlier R420 results and their preserved allocation/index failures retain their historical source context.

## Remaining obligations

The full A/C word and exact whole-list reversal, actual two-level middle-map hypotheses, D parity compensation, selected COPY/scatter lifecycle, frame geometry and physical execution remain separate. In the new dimensions, the temporary is register 661 in a 662-register model; this package proves no temporary lifecycle. A future overwrite/CLEAR proof must distinguish disposable or initially-zero temporary use from restoration of an arbitrary dirty temporary. Supplier/profile/recurrence and all-size multiplication assumptions remain open.

## Attribution

The selected punctured/tuned package is from eumemic with substantial Anthropic Claude assistance. Its complete Apache-2.0 notice is included as `SUPPLIER_NOTICE.md`, with carrier ancestry in `PR493_NOTICE.md`. The Lean source-specific work uses OpenAI assistance and reuses the unchanged PR590 generic XOR API. Official Lean core retains its distribution licenses.

## Offline retained-prefix reproduction

Use the exact PR590 package and its successful eight-root public build. This checker imports only the generic BitXorTargetTranslation source/object/probe record, while preserving all eight predecessor roots. It compiles only the three included sources in manifest order.

With the installed official Lean 4.21.0 Linux distribution, run from this package:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --prefix-package /path/to/lean-selected-bit-scalar-boundaries \
  --prefix-build /path/to/successful-pr590-build \
  --build-dir /path/to/fresh-pr589-b-build
```

The 317 official core source/object pairs, exact import closure, PR590 manifest, source bytes, retained objects and complete axiom-probe records are checked before compilation. No installation, download, Mathlib or supplier execution is required. The output directory must be absent. `--guard-only` verifies inputs and output absence without compiling. `--require-observed-prefix` additionally pins the exact recorded local result, receipts and raw logs. Portable receipt timestamps may differ while source/object/probe identities remain exact. Only the three previously reviewed generic XOR warning source paths, at lines96,110 and127, may normalize in the retained log.

The optional `--slot-service /path/to/lean_check.py` uses an independently reviewed existing FIFO compiler service, an executable trust boundary. The recorded reproduction uses one serial client of the pinned shared service. Each root has 60-second/4-GiB hard limits and 45-second/3.5-GiB review limits. Compiler, review-threshold or preservation failure stops the sequence, retaining earlier successful outputs. Compiler time, FIFO wait, post-slot guards and post-compiler guards are separate receipt fields.

The three fresh sources print19 complete records; the one retained generic source contributes4, for23 reachable records. Raw results, receipts and logs remain in the chosen build directory. REPLAY_SUMMARY.json is the sole mutable reproduction summary. The helper-write exceptions465,466,468, the selected-source binding and explicit author-checked current kappa remain as stated above; this reproduction adds no A/C/D, scatter, physical or full-construction theorem.
