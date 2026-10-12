# Prepared inputs and a canonical compact width record

This package adds two unchanged accepted Lean sources: `BinaryCounterCompactValue.lean` and `BinaryPreparedCompactCount.lean`. The first proves numeric normalization for the separately packaged physical compact-copy routine. The second is an actual 33-state, six-tape composition of input preparation/counting and compact copying. Sixteen external sources retain their immutable PR origins. The compact-copy dependency is PR565 at immutable source head b5766e15ab1c9f5c86e994aa7754a7750c6af76c, under research/lean-compact-counter-copy; no merger is assumed.

## Exact checked endpoint

For arbitrary finite Boolean input lists x,y, let n=max(length x,length y), px=pad n x and py=pad n y. The first two tapes initially contain canonical Tape.ofWord x and Tape.ofWord y. Tapes 2, 3, 4, 5 must be pristine blank. The machine has a concrete finite transition table, one explicit halt-interception bridge, and reaches halted state 32 at some t<=22n+17.

Let r=(CarryTape.pass n (replicate n false)).1 and p=compact r. The complete final tapes are:

- Slot 0: BinaryWordReversal.finalInput px.
- Slot 1: BinaryWordReversal.finalInput py.
- Slot 2: <px.map bitSymbol ++ [blank], blank, []>.
- Slot 3: BinaryWordReversal.endTape(py.map bitSymbol).
- Slot 4: <[], blank, p.map bitSymbol ++ replicate(n-p.length+1) blank>.
- Slot 5: canonical Tape.ofWord p, with the first-digit head when nonempty.

The first four are the actual visited preparation/count footprints, preserved during the compact phase. Slot4 retains its original n+2 represented cells. Slot5 is a physically separate compact finite representation; clearing high cells on slot4 alone is not treated as compaction.

The proved output value is exactly n. Output is empty for n=0; when n>0 its length is exactly floor(log2 n)+1. The normalization adapter also proves compact bits=[] iff wordValue bits=0 and preserves wordValue for arbitrary bit lists. These zero conventions are explicit, including empty and unequal-length input cases. The cost theorem gives an existential elapsed index with a halted endpoint, not first completion.

## Reuse and verification boundary

The current 18-source scientific closure has 133 complete standard-only axiom probes, 22 from the two included sources. The normalization check took 2.157461708 compiler seconds, peak 1,554,382,848 bytes VM. The composition passed its first check in 5.660375353 seconds, peak 1,776,836,608 bytes VM; its harmless unused-change warning is retained with the accepted bytes.

This is a follow-on to PR530's 15-source public closure at source head 5a21a91d083fc73a1f48bf22d89da768dcf2696a and PR565's physical compact copy at source head b5766e15ab1c9f5c86e994aa7754a7750c6af76c. The completed guarded public reproduction retained those 16 exact public outputs and freshly checked only the two new sources, in that order. The two checks used 7.015937066 compiler seconds and 0.000873518 FIFO seconds, with peak VM 1,776,807,936 bytes. All eighteen object hashes and 133 complete standard-only probes match their reference records. Seventeen full logs match exactly; the composition log differs only in warning source-path spelling. REPLAY_SUMMARY.json records the individual results and distinguishes accumulated historical receipts from these two fresh checks. The dependency manifest distinguishes immutable source origins from reused artifact locations. Repaired branch heads are not substituted for original source commits, and no full eighteen-source rebuild is requested.

The development arithmetic uses the accepted research source. Public reproduction must use PR526's explicitly reviewed comment-only CounterArithmeticPure public variant and validated public object, as already consumed by the PR530 public closure. Its hash difference is disclosed in PROVENANCE; source positions and object equality are never assumed. The accepted 1,366-node external closure contains 1,300 official Lean core modules and 66 cached Mathlib/dependency nodes. No downloads or import expansion are proposed.

PR488 supplies the actual input preparation, PR511 the explicit counter/dispatcher, PR519 automatic width allocation/counting, PR526 the PR64 receipt/potential transport, PR530 the actual five-tape prelude, and PR565 the physical compact copy. PR530 already proves preparation/counting with an 18n+12 bound; PR565 already proves the marked-home-to-canonical physical copy and its 4n+4 bound. The only two included sources add value/zero/logarithmic-length normalization and the literal six-tape handoff with its 22n+17 bound. No source from those predecessor packages is republished here, and no new generic counter or amortization theorem is asserted. Apache-2.0 licensing, applicable NOTICE and PR64 attribution remain explicit.

## Author-checked conditional project context

At pinned selected-result context f19cb621be2caf3a7291a37c343c1c55afe935e0, certificates/selected-result.json reports the conditional finite-construction project parameter

kappa = 1517760977820331 / 1000000000000000000 = 0.001517760977820331.

The author checked this exact rational/decimal equality and the selected-result-to-research/community-pr531-audit/direct-ASSEMBLY.json hash linkage. The publication-base pin is db0e57bc7f36b5ac0fc844ad7ce1396165ee6647. The publisher reports the selected result, certificate, licensing, existing Lean sources and toolchain unchanged from the pinned f19 context. The earlier 12a4934 acceptance and intermediate 4d18ff5 context are retained as history.

The selected record reports finite-package replays while retaining conditional all-size/compiler, common-label/mutable-basis, normalized residual realization, correlated whole-owner hosting, restored-row, precision/tape and analytic-transfer interfaces. Historical research ceilings are not independently certified by that integration. The linked assembly reprices the pinned PR493 bit profile/operator without reconstructing that operator. These are source-attributed facts from the delivered record/certificate, not local replay or proof of the new selected construction. The delivered selected-result/certificate, changed-path and licensing evidence and the now-approved proof/review packet support this context readback. Reading the selected proof text confirms that all-size caller, tape/precision and analytic-transfer interfaces remain inherited; it supplies no selected scalar parameter-record/head layout.

Both generic modules and all immutable PR dependencies are unchanged and establish no multiplier or kappa theorem. The earlier 4d18-to-f19 changed-path comparison contains no Lean-source changes and preserves LICENSE/NOTICE. For the later f19-to-db0 base update, the publisher reports existing/pinned Lean sources and toolchain unchanged; unrelated added Lean packages are outside this closure. No new selected source assumption is substituted into either theorem.

The literal one-string x#y caller entry, source b=ceil(log2 n) setup, any required zero-digit adapter, radix grouping/carry Plan and Gaussian represented-list Budget are outside this two-source package. Separate later research on b does not enlarge the claims here. In particular the positive output bit length is not silently renamed ceil(log2 n), since powers of two distinguish them.

## Repository checks and AI disclosure

Substantial AI assistance was used to develop and check this contribution. Exact accepted Lean bytes, complete axiom probes, source origins and independent reviews are retained. This package changes no upstream source, generator or root certificate.

The affected public Lean reproduction passed through the guarded 16-retained/2-fresh sequence above. Current CONTRIBUTING requirements also include make verify and make gen4-bank-verify; their exact new-publication-head results must be recorded separately. Historical owner checks and predecessor package reproductions are not fresh repository-wide aggregate results. No new aggregate result is claimed.

## Offline reproduction

The supported fresh eighteen-source command requires the six exact dependency packages in DEPENDENCIES.json, the official Lean 4.21.0 runtime and an already-built Mathlib checkout at 308445d7985027f538e281e18df29ca16ede2ba3. From this flat package directory:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --mathlib-root /path/to/mathlib4 \
  --input-foundation-root /path/to/PR488/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/PR511/research/lean-binary-count-dispatcher \
  --automatic-width-root /path/to/PR519/research/lean-automatic-width-count \
  --amortization-root /path/to/PR526/research/lean-count-receipt-amortization \
  --prepared-input-root /path/to/PR530/research/lean-prepared-input-count \
  --compact-copy-root /path/to/PR565/research/lean-compact-counter-copy \
  --build-dir /path/to/new-empty-reproduction-directory
```

The build directory must not exist. EXTERNAL_OBJECTS_REFERENCE.json refers to PR530's unchanged 797,008-byte EXTERNAL_OBJECTS.json by exact hash, source commit and path; this package does not duplicate that inventory. The checker validates the reference, its exact bytes and all 1,366 runtime source/object/import rows and first-match resolution before compiling. Every one of the eighteen proof sources is checked by hash, size and imports. Only the fresh isolated object directory and eight validated cache paths enter Lean's search path. No dependency is downloaded or rebuilt. Inherited Lean paths/sysroot are ignored; every full log, receipt and all 133 expected standard-only probes are retained. Hard caps are 60 seconds/4 GiB per root; review stops are 40 seconds/3.5 GiB. An optional existing --slot-service supplies FIFO admission without changing proof inputs.

The approved measurement instead verifies and retains PR530's fifteen public outputs plus PR565's compact output, and checks only BinaryCounterCompactValue followed by BinaryPreparedCompactCount. This measurement completed successfully, with the retained outputs verified before and after the two checks. Its accumulated eighteen-record compiler total is 38.513856365 seconds, including historical checks; the peak across those records is 3,407,740,928 bytes VM. This sixteen-retained/two-fresh sequence remains distinct from running the supported fresh eighteen-source command above.
