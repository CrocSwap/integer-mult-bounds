# PR64 receipt transport for the automatic-width counter

This three-source supplement connects the published PR64 fixed-direction arithmetic bound to the concrete automatic-width binary counter from PR519. It reuses the original potential proof and the previously checked machine; it adds the exact receipt correspondence between their interfaces.

## Checked result

For every finite Boolean word of length n, CurrentMain.BinaryCountReceiptAmortization.count_run_linear gives an elapsed t <= 12*n+4 at which the existing ten-state, two-tape machine reaches its exact final configuration.

The input head starts at the represented right blank after the whole word: <word.reverse.map bitSymbol, blank, []>. The counter tape starts pristine. The final state is 9, the final input tape is <word.reverse.map bitSymbol ++ [blank], blank, []>, and the counter is the width-n marked-home representation of the inherited n-step pass from n zero bits. PR519's accepted endpoint theorems give stored value exactly n and terminal halting. Empty input is included. The theorem does not identify first completion or a canonical short output record.

The receipt equality is exact for every width and starting word: current pass reads = CounterArithmetic.totalSteps true n bits + 2*n. PR64's 4*n+2*width bound therefore yields current pass reads <= 6*n+2*width. PR519 supplies allocation/controller overhead 4*n+4, giving 12*n+4 at width n. Wraparound and width zero remain covered in the general receipt statements; the automatic-width counter separately stores the exact input length.

## What is included

- RippleCounterListData.lean extracts PR64's five unchanged list definitions, with the original RippleCounter namespace.
- CounterArithmeticPure.lean retains all original CounterArithmetic declaration and proof bodies and 23 probes. Its import is retargeted to the extraction, two installed-core theorems are registered locally, and Elab.async=false is selected inside a local section. This public copy adds a prominent modification notice to the accepted adapted source.
- BinaryCountReceiptAmortization.lean proves seven interface facts, culminating in the 12*n+4 endpoint theorem.

PR64 already proves richer generic counter results, including both directions, arbitrary exterior tape, first completion and fixed-direction amortization. This package claims no new generic counter algorithm or potential proof and no simulation of PR64's complete tape machine. PR519's source and published unamortized pass.reads+4*n+4 theorem stay unchanged.

## Exact external proof dependencies

Use the recorded sources from three separate worktrees; no merged status is assumed:

- PR519, ffd3c48a80ba8b579dc300e785e387fe8acddfef, research/lean-automatic-width-count: BinaryCountDispatcherMarkedInput, BinaryCounterZeroAllocation, BinaryAutomaticWidthCount.
- PR511, 79f7c03c7f820ab89955b75ef239cbaccc627e6e, research/lean-binary-count-dispatcher: CarryTape, CarryTapePass, BinaryCarryIncrement, BinaryCountDispatcher.
- PR488, edd3102b415df5b9d6f633ac0a4dedcf69c58525, research/lean-binary-input-preparation: IntegerConvolution and FixedTapeMachine.

All nine dependency source hashes are pinned in the package provenance/manifest. The PR511 source pin above is intentional; its later CI-provenance repair head is a separate artifact.

## Runtime and reproduction boundary

This is a Lean 4.21.0 package with Mathlib revision 308445d7985027f538e281e18df29ca16ede2ba3. It is not core-only. The Mathlib entry imports are Mathlib.Algebra.Group.Nat.Defs and Mathlib.Tactic.SplitIfs; the exact accepted source/object dependency closure is required for offline reproduction. No download, installation or broader import is implied. The original physical TapeStack, RippleCounter and CounterArithmetic modules are excluded. Do not jointly import their original declaration-defining modules with these namespace-preserving extractions.

The exact public twelve-source reproduction is complete, with all 79 expected standard-only probes matching. It used 17.7186 compiler seconds and 0.00557 FIFO seconds across ten retained verified checks and a separately guarded two-root suffix; peak VM was 3,074,072,576 bytes. The first public notice used a module-doc opener before an import and was rejected; the one-byte ordinary-comment correction and failed evidence are retained. Eleven object hashes match research; the public arithmetic copy has a distinct accepted object, with the same scientific body and 23 probes. REPLAY_SUMMARY.json records the full resumed sequence. Hard limits remain 60 seconds and 4 GiB per root, with review at 40 seconds or 3.5 GiB.

## Attribution and license

PR64 is the source of the five literal definitions and complete arithmetic proof bodies. Preserve the upstream hashes and source correspondence in PROVENANCE.json. The package carries Apache-2.0 LICENSE, the applicable repository NOTICE, and explicit extraction/import/control-change notices. The existing repository's separate RaD CC0 exception does not apply to these counter files.

## Author-checked conditional project context

At current-main base 12a4934d15006e8c10f9b2264f13f8f341be802b, certificates/selected-result.json records kappa = 90446448750933/125000000000000000 = 0.000723571590007464 and links the retained PR279 certificate by its exact SHA-256. The rational/decimal equality and selected-result/certificate linkage were checked. This is the source's conditional project parameter. These generic counter and receipt-transport modules prove no multiplication or kappa theorem.

Compact record normalization/copy, the actual input-preparation-to-counter finite-control composition, the selected source caller and Plan/carry construction, and the whole Gaussian represented-list Budget remain separate. The retained all-size compiler, chart/routing, prime supply, precision/recovery, complex symbolic correctness and analytic-transfer conditions are not discharged by this package.

## Offline reproduction

Use Linux, Python 3, the official Lean 4.21.0 distribution, and an already prepared Mathlib checkout at the revision above with its existing package caches. The checker does not download or build Mathlib. EXTERNAL_OBJECTS.json lists all 1,300 official-core and 66 noncore source/object hashes used by this closure; hash or first-match path differences stop before compilation.

Provide the three exact source worktrees described above. From this flat package directory, run:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --mathlib-root /path/to/mathlib4 \
  --input-foundation-root /path/to/PR488/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/PR511/research/lean-binary-count-dispatcher \
  --automatic-width-root /path/to/PR519/research/lean-automatic-width-count \
  --build-dir /path/to/new-empty-reproduction-directory
```

The build directory must not exist. The checker copies only the twelve verified source files into a new source directory, compiles into a separate fresh object directory, and supplies only that output plus the eight explicit cache paths. It ignores inherited Lean search/sysroot settings. Every local source, all dependency identities and all79 complete axiom probes are checked; logs and per-root receipts are retained. A failure or review threshold stops the remaining sequence. The optional --slot-service argument reuses an existing FIFO admission service; it changes no Lean input.
