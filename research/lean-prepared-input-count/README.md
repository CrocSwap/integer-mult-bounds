# Concrete prepared-input counting in linear time

This one-source addition composes the checked input-preparation machine from PR488 with the automatic-width counter from PR519 and its PR526 amortized receipt bound. It supplies an actual finite transition table and a complete tape-level handoff, rather than assuming compatible intermediate representations.

## Checked contract

For arbitrary finite Boolean lists x and y, let n = max(x.length, y.length), px = pad n x, and py = pad n y, where pad appends false bits to the shorter little-endian input. The initial configuration has canonical Tape.ofWord x and Tape.ofWord y on slots 0 and 1, and pristine Tape.blank on slots 2, 3 and 4. There is no extra arbitrary spectator tape in this five-tape public contract.

CurrentMain.BinaryPreparedInputCount.prepare_count_run proves that some elapsed t <= 18*n+12 reaches the exact finalConfiguration. The machine has 24 states. States 0 through 13 reproduce input preparation, including its live state-13 seek loop. One tape-preserving transition intercepts the preparation halt and enters state 14. States 14 through 23 reproduce the ten-state automatic-width counter on prepared slot 2 and pristine counter slot 4; slots 0, 1 and 3 retain their preparation footprints during this phase. The bound combines preparation <= 6*n+7, that one bridge transition, and counting <= 12*n+4.

The final state is 23 and is halted. In the explicit tape notation <left, head, right>, where left lists the nearest cells first, the five final tapes are:

- Slot 0: BinaryWordReversal.finalInput px.
- Slot 1: BinaryWordReversal.finalInput py.
- Slot 2: <px.map bitSymbol ++ [blank], blank, []>.
- Slot 3: BinaryWordReversal.endTape (py.map bitSymbol), namely <py.map bitSymbol, blank, []>.
- Slot 4: BinaryCarryIncrement.homeTape bits, where bits = (CarryTape.pass n (List.replicate n false)).1. This is <[], blank, bits.map bitSymbol ++ [blank]>.

The inherited counter facts prove bits.length = n and wordValue bits = n. Empty and unequal-length inputs are included, with all represented boundary blanks retained. The counting input parameter is px.reverse, so its initial right-blank representation matches prepared slot 2 exactly. The original-input finalInput footprints and both prepared work endpoints are not identified with a canonical short output tape.

The theorem gives an elapsed upper bound, not first completion or equality of the runtime to 18*n+12. The counter remains a width-n marked record. Compact-record copying, the complete selected mathematical source caller, radix/carry Plan construction and the whole Gaussian represented-list Budget remain separate.

## Exact sources and reuse

Only BinaryPreparedInputCount.lean is included, byte-identical to its accepted research source 2794c5633694d119f46efb1053e353e6bd122c3b93117ced4a3ed8a75feefa4b. The fourteen external proof sources are pinned in DEPENDENCIES.json:

- PR526, e7d6dc6e474f8690d72ef8b841290948028f66f3, research/lean-count-receipt-amortization: RippleCounterListData, CounterArithmeticPure and BinaryCountReceiptAmortization.
- PR519, ffd3c48a80ba8b579dc300e785e387fe8acddfef, research/lean-automatic-width-count: BinaryCountDispatcherMarkedInput, BinaryCounterZeroAllocation and BinaryAutomaticWidthCount.
- PR511, 79f7c03c7f820ab89955b75ef239cbaccc627e6e, research/lean-binary-count-dispatcher: CarryTape, CarryTapePass, BinaryCarryIncrement and BinaryCountDispatcher.
- PR488, edd3102b415df5b9d6f633ac0a4dedcf69c58525, research/lean-binary-input-preparation/Lean: IntegerConvolution, FixedTapeMachine, BinaryWordReversal and BinaryInputPreparation.

No merged status is assumed. The PR511 source commit is distinct from its later CI-provenance repair head. The external arithmetic copy is PR526's public source 7fea5026, with its prominent ordinary-comment notice and separately validated public object fbeef132. Its 1,092-byte notice is the only difference from research source 1ad26524. The research variant is not silently substituted for that public dependency.

PR64 supplies the existing fixed-direction potential argument, reused through PR526's exact receipt transport. PR64 already contains richer generic counter results, including both directions and first completion. This addition claims the concrete preparation/count transition composition and endpoint, not a new generic counting algorithm, potential proof or simulation of the complete PR64 tape machine. Preserve Apache-2.0 LICENSE, the applicable NOTICE and the upstream attribution/modification notices in the external packages.

## Verification boundary

The accepted research root used 4.6331 compiler seconds and 1,775,390,720 bytes peak VM. Its fourteen complete axiom probes and all 102 probes in the fifteen-source local closure use only the standard propext, Classical.choice and Quot.sound axioms as recorded. Two rejected proof-elaboration attempts are preserved separately; no rejected probe is counted as acceptance.

Reproduction uses Lean 4.21.0 and the already accepted Mathlib revision 308445d7985027f538e281e18df29ca16ede2ba3, including the exact 1,366 cached core/external source-object rows. It is not core-only. The new module explicitly sets Elab.async=false; this does not change kernel checking or runtime limits. The original physical TapeStack and RippleCounter modules are outside the graph. Their declaration-defining modules must not be jointly imported with PR526's namespace-preserving list/arithmetic extractions.

The exact public fifteen-source closure is reproduced by a guarded twelve-output prefix plus three fresh compiler checks. The fresh suffix used 10.0393 compiler seconds and 0.00221 FIFO seconds; the complete recorded closure totals 27.7579 compiler seconds. Peak VM was 3,407,740,928 bytes. All 102 expected complete standard-only probes and all fifteen reference object hashes match. Fourteen full logs match exactly; BinaryInputPreparation differs only in warning source-path presentation. REPLAY_SUMMARY.json distinguishes the twelve retained PR526 outputs from the three new checks. Hard limits stay 60 seconds and 4 GiB per root, with review stops at 40 seconds or 3.5 GiB.

## Author-checked conditional project context

At current-main base 12a4934d15006e8c10f9b2264f13f8f341be802b, certificates/selected-result.json records kappa = 90446448750933/125000000000000000 = 0.000723571590007464 and links the retained PR279 certificate by its exact SHA-256. The rational/decimal equality and selected-result/certificate linkage were author-checked. This is the source's conditional project parameter; this generic preparation/count module proves no multiplication or kappa theorem.

The retained all-size compiler, chart/routing, prime-supply, precision/recovery, complex symbolic correctness and analytic-transfer conditions are not discharged by this package.

## Offline reproduction

The fresh full fifteen-source checker requires the four exact source worktrees above, the official Lean 4.21.0 runtime and an already-built Mathlib checkout at 308445d7985027f538e281e18df29ca16ede2ba3. No download or Mathlib build is performed. From this flat package directory:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --mathlib-root /path/to/mathlib4 \
  --input-foundation-root /path/to/PR488/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/PR511/research/lean-binary-count-dispatcher \
  --automatic-width-root /path/to/PR519/research/lean-automatic-width-count \
  --amortization-root /path/to/PR526/research/lean-count-receipt-amortization \
  --build-dir /path/to/new-empty-reproduction-directory
```

The build directory must not exist. The checker verifies every source and all 1,366 existing runtime source/object pairs, copies the fifteen exact sources into a fresh directory and compiles into a separate fresh object directory. Only that output and eight explicit cache paths enter the search path. It ignores inherited Lean paths/sysroot, expects all 102 complete standard-only axiom probes and retains every receipt/full log. Hard caps are 60 seconds/4 GiB per root; review stops are 40 seconds/3.5 GiB. The optional --slot-service uses an existing FIFO admission service without changing Lean inputs.

The recorded guarded reproduction retained and verified twelve exact public PR526 outputs and freshly checked the three additional roots. This completed twelve-retained/three-fresh measurement is distinct from the supported full fifteen-source command above.
