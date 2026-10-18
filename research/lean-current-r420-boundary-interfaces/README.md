# Current R420 boundary and B-XOR interfaces

Author-checked selected context: κ = 16127213726553 / 10000000000000000 = 0.0016127213726553 at main `5996f9043c27bafa90b23e1c937de92a738f1a76`. The selected bit supplier is PR543, commit `2065fe4f72a914d907f1046603f5a36f17018535`. This is a conditional source context, not a proved κ or integer-multiplication theorem.

## What is checked

Seven new source files consume four byte-exact public PR590 dependencies. The complete closure is 317 official Lean 4.21.0 core modules plus 11 local modules. Mathlib is not required. No PR597 module or unpublished generic helper is imported.

- `CurrentR420BoundaryData`: current ordered literal data, a bound-carrying frame-table permutation, and fresh Fin660/Fin661 interfaces.
- `CurrentR420FrameIndexCheck`: three shape/index facts. A finite `isPerm` certificate and public list theorems derive the original sorted-equality interface without evaluating merge sort.
- `CurrentR420FrameBoundaryCheck`: seven frame/entrance/final/retained-host facts. Frame-row bounds reuse the accepted historical table symbolically.
- `CurrentR420BBandCheck`: eleven facts for the exact 120/597/120 B bands, all 837 gates and 1,077 ordered operand occurrences.
- `CurrentR420ScatterFacts`: six finite facts for 120 scatter rows, 568 retained indices, nine helpers and temporary index 660 in Fin661.
- `CurrentR420BoundaryCheck`: import-only restoration of all 27 original public facts. It evaluates no theorem body or finite predicate.
- `CurrentR420PhaseBXor`: exact ordered Boolean decoding, helper preservation and target-translation semantics for B.

There are 61 printed probe records for the new files, representing 34 distinct declarations: the import-only wrapper deliberately prints the 27 finite facts again. The four retained dependencies contribute 14 additional probe records. Every recorded axiom set is standard-only; no rejected or partial module is accepted.

## The semantic boundary

Original registers are Fin660: sources 0–119, targets 120–239 and helpers 240–659. The middle 597 B gates write source registers. Their operands consist of 477 source reads followed by 120 helper reads. The last 120 gates contain 120 source and 240 helper operand occurrences.

The scalar interpreter retains gate and operand order, multiplicity and frame IDs. It applies sequential Boolean XOR updates. For arbitrary original input bits, B preserves every helper bit. Each output target equals its initial target bit XOR the contribution computed from the same state with targets erased. That contribution is independent of the initial target bits and need not be zero. Source registers are allowed to change.

The scalar interpreter carries frame metadata but does not prove physical frame transport. The Fin661 temporary facts are only domain/exclusion facts. No current COPY/ERASE lifecycle or restoration of an initially dirty temporary is claimed here.

## Source binding and reuse

The current source is `research/e8-bit-r420/data/bitE8mut-r420.json.gz`, compressed SHA256 `9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784`; its decoded SHA256 is `e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2`. All 49 selected R420 package files agree between the original 9594 snapshot and selected 5996. The current 672-frame order is proved to permute the accepted old table; the current typed domains and endpoint/host facts are checked afresh.

The required PR590 modules are `SelectedBitCarrierBoundaryData`, `SelectedBitCarrierBoundaryCheck`, `SelectedBitCarrierPhaseBData` and `BitXorTargetTranslation`. Their source/object identities and public probe/log requirements are in `DEPENDENCIES.json`. A successful predecessor build supplies these four accepted objects. They are retained rather than compiled again. No historical R489/R480 typed theorem is renamed into a current instance.

`MANIFEST.json` lists every origin, exact source hash, import and ordered probe. `ACCEPTED_CHECKS.json` records the immutable local and public-prefix kernel evidence. `REPLAY_SUMMARY.json` owns the single mutable reproduction result. The standalone retained-prefix checker and its concrete offline instructions are supplied in the reviewed publication completion.

## Preserved failures and costs

The original combined 27-fact module failed allocation at 25.649962 seconds and 4,272,771,072 bytes VM, without an accepted object. Three later index attempts failed on kernel sort reduction or import syntax. Their exact evidence remains preserved. The successful recovery uses separate roots and a symbolic permutation proof, retaining the original public statements. It is not an equivalent whole-check speedup measurement.

The seven included source modules have independently reviewed local passes totaling 32.303836 compiler seconds; the largest observed VM was 1,260,244,992 bytes. These are prior research measurements, not a prediction of a public replay. Compiler, FIFO and post-slot guard times remain separately recorded. The intended bounds remain 60 seconds / 4 GiB hard and 45 seconds / 3.5 GiB review per root, stopping on the first failure or review event.

## Still open

- Actual full A/C typed bindings and the selected cleanup composition
- D parity/compensation equality
- The current 661-register COPY/scatter lifecycle instance
- Physical/common-frame transport, provider and hosting conditions, and all-size multiplication transfer

Generic reversal/chunk/two-level cleanup results are separate and are not needed by this package. This completed boundary does not wait on those remaining source-specific instances.

## Attribution

Apache-2.0. The R420 supplier was prepared by eumemic with substantial Anthropic Claude assistance. Complete current and carrier-ancestry notices are preserved in `SUPPLIER_NOTICE.md` and `PR493_NOTICE.md`. These Lean certificates were prepared with OpenAI assistance, reusing the exact public PR590 proofs and official Lean core APIs.

## Offline retained-prefix reproduction

Use the exact PR590 package and a successful eight-root PR590 public build. This checker validates four required source/object/probe records and preserves all eight predecessor roots, including the four that are not imported here. It compiles only the seven included sources in the manifest's order.

With the existing official Lean 4.21.0 Linux distribution, run from this package:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --prefix-package /path/to/lean-selected-bit-scalar-boundaries \
  --prefix-build /path/to/successful-pr590-build \
  --build-dir /path/to/fresh-r420-build
```

The 317 official core source/object pairs, exact import closure, PR590 manifest, source bytes, retained objects and full axiom-probe records are checked before compilation. No installation, download, Mathlib or scientific supplier execution is required. The new output directory must not exist. `--guard-only` verifies these inputs and output absence without compiling. `--require-observed-prefix` additionally pins the exact local PR590 result, receipts and raw logs recorded here. A portable prefix may have different receipt timestamps; its sources, objects and full probes must still match. Only the three recorded generic XOR warning source paths, at lines 96, 110 and 127, may normalize in the retained log.

The optional `--slot-service /path/to/lean_check.py` uses an independently reviewed existing FIFO compiler service. That service is an executable trust boundary. Our bounded reproduction uses the pinned shared service with one serial client. Each root has a 60-second and 4-GiB hard limit, with review stops above 45 seconds or 3.5 GiB peak virtual memory. A compiler failure, review threshold or preservation failure stops the sequence and retains earlier successful artifacts. Actual compiler, FIFO wait, post-slot guard and post-compiler guard times are separate receipt fields.

The seven fresh modules print 61 probe records covering 34 distinct declarations, because the import-only wrapper repeats 27 imported facts. The four retained modules contribute 14 records, for 75 reachable printed records. The raw result and individual receipts are written in the chosen build directory; REPLAY_SUMMARY.json is this package's sole mutable reproduction summary. Selected source applicability, conditional semantic scope and the explicit author-checked current kappa remain as stated above.
