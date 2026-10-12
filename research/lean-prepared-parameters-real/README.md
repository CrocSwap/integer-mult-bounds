# Prepared binary parameters with a real-ceiling identity

This package adds four unchanged accepted Lean sources. `BinaryPreparedParameters.lean` supplies the actual forty-eight-state, eight-tape composition of the previously published preparation/compact-count and binary-parameter machines. `BinaryCeilLogNatBinding.lean`, `BinaryCeilLogRealBinding.lean` and `BinaryPreparedParametersRealBinding.lean` reuse installed logarithm APIs and attach their identities to that same execution. Twenty public predecessor sources retain their immutable origins; none is republished here.

## Entry, full endpoint and time bound

Let x and y be arbitrary finite Boolean operand words, n=max(x.length,y.length), w=widthBits x y, m=w.length and b=ceilLog2 n. Bits are little-endian under the explicit model's wordValue. Entry is canonical Tape.ofWord x on slot0, Tape.ofWord y on slot1, and pristine Tape.blank on slots2 through7. No arbitrary initial work-tape contents are admitted.

The machine starts in state0. The accepted six-tape prepared compact count runs on slots0 through5; one actual halt-interception transition then runs the accepted three-tape binary-parameter machine on slots5 through7. Slots0 through4 are preserved during this second phase with their actual first-phase endpoint footprints. They are not asserted to remain equal to their original entry tapes.

At some elapsed t<=22*n+13*m+24<=35*n+24 the machine reaches the exact finalConfiguration x y, halted in state47. These are existential elapsed upper bounds, not a first-completion or exact elapsed-count claim.

Write L=leftPad x y and R=rightPad x y for the accepted equal-length zero-padded operand lists, and r=parameterBits x y. Using <left,head,right> for the explicit finite tape, the complete final slots are:

- Slot0: BinaryWordReversal.finalInput L.
- Slot1: BinaryWordReversal.finalInput R.
- Slot2: <L.map bitSymbol ++ [blank],blank,[]>.
- Slot3: <R.map bitSymbol,blank,[]>.
- Slot4: <[],blank,w.map bitSymbol ++ replicate (n-m+1) blank>.
- Slot5: <w.reverse.map bitSymbol,blank,[]>.
- Slot6: <(replicate b false).reverse.map bitSymbol ++ [blank],blank,[]>.
- Slot7: <[],blank,r.map bitSymbol ++ [blank]>.

The reversal's finalInput definition fixes the represented boundary cells on slots0/1; no quotient by trailing blanks is used. The normalized n record w has value n, is empty when n=0, and otherwise has length n.log2+1. Its length is at most n. In the final configuration its head has been scanned to the right blank on slot5. The parameter record r has both length b and value b. It is a marked-home width-b binary record, not a compact binary-b output. Both its home and end blanks are represented, including b=0. The retained slot4 footprint is not shrunk by clearing cells.

For x=y=[], w=[] and r=[]. Visited blanks on the other tapes are retained exactly by the endpoint definitions; this is not a claim that all eight tapes are canonical blanks. Width one also gives b=0. No singleton-zero word is introduced.

## Exact logarithm interface

The published PR570 token theorem already supplies the least-power characterization. The new Nat adapter reuses the installed Mathlib theorem to identify tokenCount(compact bits) with Nat.clog 2 (wordValue bits), without a new logarithm induction or numeric hypothesis.

The Real adapter then reuses Real.natCeil_logb_natCast. For every width n, the stored b equals the natural ceiling of Real.logb (2 : Nat) (n : Real), under the library's explicit zero extension. For 0<n, the stored b cast to Int equals the integer ceiling of that same real logarithm. Zero and one are explicitly recorded as b=0. At powers of two the exact exponent is used; positive binary length is not substituted for the ceiling.

The final two run theorems conjoin the exact existing physical endpoint and t<=35*n+24 with, respectively, the totalized natural-ceiling identity or the integer-ceiling identity under the explicit premise 0<n. The three adapter sources do not alter the machine, entry, endpoint, assumptions on work tapes, or time bound. The positive hypothesis belongs to the integer-ceiling statement; it is not silently added to the underlying physical run.

## New contribution and predecessor overlap

PR565 already publishes the physical compact-copy helper. PR566 already publishes compact value/length normalization and the six-tape prepared compact-n count. PR570 already publishes the five-state token scan/least-power certificate and fifteen-state binary-b machine. This package reuses those bytes as exact external dependencies. Its new physical contribution is their real eight-tape handoff from two operands plus six pristine tapes. Its remaining three sources provide the thin Nat.clog/Real.logb API transport and the full physical/Real identity join.

PR488 supplies reversal, input preparation and the two explicit-model foundations; PR511 supplies carry/dispatcher interfaces; PR519 supplies width allocation/counting; PR526 supplies the PR64 arithmetic transport and 12n+4 count bound; PR530 supplies the five-tape prepared count. All eight immutable source-package origins are listed in DEPENDENCIES.json. In particular PR565 remains pinned to b5766e15ab1c9f5c86e994aa7754a7750c6af76c, PR566 to 86d39f3247a5a1df4f040ed71d8251bed77b91ec, and PR570 to 9278e39baec4f23267336c7d212306d0c0003d08. Later repaired branch heads are not substituted and no merger is assumed.

The public arithmetic dependency is PR526's already reviewed CounterArithmeticPure variant 7fea5026, whose 1,092-byte attribution/modification notice differs from the accepted research source 1ad26524. Its public object fbeef132 and research object 3d3ef802 are intentionally distinct. The retained public prefix uses the public object; all four newly included roots have now passed their isolated reproduction against that exact prefix, with object bytes identical to their research references. No new generic counter, amortization potential, normalization or real-logarithm theory is claimed. Apache-2.0 LICENSE and applicable NOTICE, including predecessor attribution, are retained.

## Exact source and verification boundary

The complete closure contains 24 proof sources, 256,978 source bytes and 194 complete standard-only axiom probes. These four included files total 27,934 bytes and 33 probes. The 20 public reference outputs contribute 161 probes. The accepted research passes used only propext, Classical.choice and Quot.sound, with some facts axiom-free. The Nat adapter's first name-resolution failure is preserved in development evidence and is not accepted evidence; the included file is the accepted repaired source.

Guarded public reproduction passed. The measured run verified and retained PR566's 18 public outputs plus PR570's 2 outputs, then freshly checked only the 4 included sources. All 24 reference objects and full raw logs match, and all 194 complete probes are standard-only. The four fresh checks used 17.477078325 compiler seconds and 0.002274750 FIFO seconds, with peak VM 2,784,276,480 bytes. REPLAY_SUMMARY.json records the exact receipts and pins. This was not a fresh 24-source run; accumulated closure totals include historical retained receipts.

The existing installed runtime has 3,160 external modules: 1,341 official Lean/Std modules and 1,819 cached Mathlib/package modules. EXTERNAL_OBJECTS_REFERENCE.json pins PR526's unchanged 1,366-row, 797,008-byte base manifest; EXTERNAL_OBJECTS_EXTENSION.json supplies only the disjoint 1,794-row extension already used by the accepted research closure. Their union must be validated by source/object hashes, import closure and first-match resolution. No download or dependency rebuild is proposed. The 2,013,325,312-byte external object sum is an inventory measurement, not a runtime-fit guarantee. Reproduction must retain 60-second/4-GiB hard caps and 40-second/3.5-GiB review stops per root, with the existing shared FIFO admission.

This is a two-operand explicit-tape setup result. It does not supply the selected one-string MSB x#y splitter/controller, a selected source alphabet or parameter-record/head-layout correspondence, physical p=6b setup, compact b output, or remaining scalar-call parameter setup. It does not instantiate a radix/carry Plan, a represented-list Gaussian Budget or a multiplier theorem.

## Author-checked conditional project context

At pinned selected-result context f19cb621be2caf3a7291a37c343c1c55afe935e0, certificates/selected-result.json reports

kappa = 1517760977820331 / 1000000000000000000 = 0.001517760977820331.

The author checked that exact rational/decimal equality in both the selected record and research/community-pr531-audit/direct-ASSEMBLY.json, and verified the selected-result-to-certificate SHA256 link. The planned publication base is db0e57bc7f36b5ac0fc844ad7ce1396165ee6647, as authorized by the publisher; f19 remains the separately attributed source context.

The delivered selected record and approved proof/review packet retain all-size/compiler, common-label/mutable-basis, normalized residual realization, correlated whole-owner hosting, restored-row, precision/tape and analytic-transfer interfaces. Finite-package replay claims remain attributed to those sources. Their text does not identify the selected all-size scalar caller or its parameter-record/head layout. This package neither adds assumptions to close that gap nor treats these four generic Lean modules as a proof of the selected construction.

All four modules are independent of kappa and prove no multiplier or kappa theorem. The explicit parameter above is conditional project context only. Historical accepted-source and earlier project-context evidence is preserved.

## Repository checks and AI disclosure

Substantial AI assistance was used to develop and check this contribution. Exact accepted source bytes, complete axiom probes, predecessor attribution and independent reviews are retained. This package introduces no generator, upstream proof modification or certificate repair.

The four-root public measurement passed as described above. Current CONTRIBUTING requirements also include make verify and make gen4-bank-verify; exact results for a future publication head must be recorded separately. Candidate 9278's successful Python 3.13.5 verify-research run is predecessor evidence and does not certify these later additions. No fresh repository-wide aggregate PASS is claimed for this package.

## Offline reproduction command

`check.py` supports a fresh isolated replay of all 24 sources. Supply the eight exact predecessor package roots from DEPENDENCIES.json and an existing Lean 4.21.0/Mathlib cache matching the referenced base and included extension. For example:

```sh
python3 check.py \
  --lean /path/to/lean-4.21.0-linux/bin/lean \
  --input-foundation-root /path/to/pr488 \
  --dispatcher-foundation-root /path/to/pr511 \
  --automatic-width-root /path/to/pr519 \
  --amortization-root /path/to/pr526 \
  --prepared-input-root /path/to/pr530 \
  --compact-copy-root /path/to/pr565 \
  --prepared-compact-root /path/to/pr566 \
  --binary-parameter-root /path/to/pr570 \
  --mathlib-root /path/to/mathlib4 \
  --build-dir /path/to/new-empty-build-location
```

Each package root is the directory containing that dependency's public MANIFEST.json; PR488 also contains its Lean/ source directory. The checker reads PR526's exact 797,008-byte EXTERNAL_OBJECTS.json and this package's exact 1,111,760-byte EXTERNAL_OBJECTS_EXTENSION.json. It rejects overlap, changed source/object bytes, unresolved imports or shadowed first-match objects across their 3,160-row union. It does not download dependencies or build the cache.

The command requires Linux /proc for measured memory review. It uses one Lean thread argument, a 64-MiB stack and MIMALLOC_ARENA_RESERVE=64MiB, with 60-second/4-GiB hard bounds and 40-second/3.5-GiB review stops per source. An optional --slot-service path supplies the existing shared FIFO acquire() interface. The inherited service label is only a queue label; each request includes its actual module name. The checker expects all 194 complete probes and accepts only standard axioms.

The supported fresh 24-source command is distinct from the completed development measurement: 20 byte-verified retained public outputs followed by exactly four fresh roots. That retained-prefix measurement passed with its own receipts, full logs, reference-object comparisons and actual resource use in REPLAY_SUMMARY.json. The source/runtime inputs and all retained output bytes were verified again after the four checks.
