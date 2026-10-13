# A binary ceiling-log parameter on explicit tapes

This package adds two unchanged accepted Lean sources, `BinaryCeilLogTokens.lean` and `BinaryParameterCount.lean`. A five-state, two-tape machine scans a binary word into zero tokens. A concrete fifteen-state, three-tape machine then counts those tokens into an actual binary record. On normalized input the stored number is the least natural exponent whose power of two bounds the represented value. Fourteen external sources retain their immutable PR origins.

## Exact physical and numeric contracts

For an arbitrary finite Boolean word w, let m=w.length and

b=w.dropLast.length + indicator(w.dropLast.any id).

The token machine starts with canonical Tape.ofWord w and one pristine blank tape. In exactly m+1 elapsed transitions it reaches halted state 4 with input <w.reverse.map bitSymbol,blank,[]> and token tape <replicate b zero,blank,[]>. The output head is at the represented right blank. This exact elapsed identity does not assert first completion.

The binary-parameter machine starts with canonical Tape.ofWord w on slot 0 and pristine Tape.blank on slots 1 and 2. One actual tape-preserving bridge joins the scan to the unchanged automatic-width counter. At some t<=13m+6 it reaches halted state 14. Let u=replicate b false and r=(CarryTape.pass b (replicate b false)).1. The complete final tapes are:

- Slot 0: <w.reverse.map bitSymbol,blank,[]>.
- Slot 1: <u.reverse.map bitSymbol ++ [blank],blank,[]>.
- Slot 2: <[],blank,r.map bitSymbol ++ [blank]>.

The counter bits satisfy r.length=b and wordValue r=b. This is a marked width-b binary record with the head at its home blank, not a canonical compact representation of b. The source ends at its right blank; the token tape also ends at its right blank, retaining the additional represented left blank. The record's home and end blanks are distinct represented cells, including b=0. The theorem gives an existential elapsed upper bound; no first-halting-time claim is made.

Numeric identification uses w=compact bits and v=wordValue bits. The accepted facts identify the stored value with ceilLog2 v and prove, for every natural k,

b<=k if and only if v<=2^k.

The explicit definition is ceilLog2 0=0; for positive v it is v.log2 plus zero when v=2^(v.log2), and one otherwise. Thus zero and one produce b=0, powers of two have their exact exponent, and other positive values use the next exponent. Positive canonical bit length is not silently substituted for this ceiling parameter. The physical theorems hold for arbitrary words; the ceiling identification is only for normalized input. For example the noncanonical word [false,false] emits one token although its numeric value is zero.

For empty input, slot 0 remains the canonical blank, while slot 1 is <[blank],blank,[]> and slot 2 is <[],blank,[blank]>. A normalized one also produces the width-zero marked record. No singleton-zero output encoding is introduced.

## Reuse and verification boundary

The sixteen-source scientific closure has 122 complete standard-only axiom probes, with 28 in the two included sources. The accepted token check took 3.619026548 compiler seconds and 1,730,854,912 bytes peak VM. The binary-parameter machine passed its first check in 3.545301435 seconds with 1,774,333,952 bytes peak VM. These are historical research checks. The token module's preserved initial ordinary elaboration failure is not accepted evidence.

The public reproduction passed after verifying and retaining PR526's twelve exact public outputs, PR565's physical-copy output and PR566's numeric-normalization output, then freshly checking only these two new sources. The two fresh checks used 4.468479126 compiler seconds and 0.001146350 FIFO seconds, with peak VM 1,774,305,280 bytes. All sixteen reference objects and full logs match exactly, and all 122 complete probes pass. REPLAY_SUMMARY.json records this fourteen-retained/two-fresh measurement; its accumulated records are not one fresh sixteen-source replay.

PR488 supplies the two explicit-model foundations; PR511 supplies the carry/dispatcher interfaces; PR519 supplies automatic width allocation/counting; PR526 supplies the PR64 arithmetic transport and accepted 12n+4 counter bound. PR565 already proves the physical compact copy. PR566 already proves numeric compact normalization and the six-tape preparation/count/copy composition. This package consumes only PR566's normalization module. It does not include or republish BinaryPreparedCompactCount, BinaryPreparedInputCount, BinaryInputPreparation or BinaryWordReversal. Its new contribution is the actual lookahead-token table and the token-to-binary-counter handoff. No new generic counter, potential or logarithm theory is asserted.

Immutable dependencies include PR565 at b5766e15ab1c9f5c86e994aa7754a7750c6af76c and PR566 at 86d39f3247a5a1df4f040ed71d8251bed77b91ec. Repaired branch heads are not substituted, and no merger is assumed. DEPENDENCIES.json gives all six source-package origins and exact paths.

The public arithmetic dependency is PR526's reviewed CounterArithmeticPure public variant, with a 1,092-byte attribution/modification comment relative to the research source. Its public object is separately accepted and differs from the research object. The public reproduction retained that exact public artifact and independently measured both new objects against their research references. PR64 attribution, Apache-2.0 LICENSE and applicable NOTICE remain explicit through the unchanged dependencies.

EXTERNAL_OBJECTS_REFERENCE.json points directly to PR526's exact 797,008-byte runtime inventory; this package does not duplicate it or require PR530 solely for that inventory. The unchanged external closure has 1,366 nodes: 1,300 official Lean core modules and 66 cached Mathlib/dependency nodes. No download, import expansion or dependency rebuild is proposed. Central reproduction tooling must retain the established 60-second/4-GiB hard limits and 40-second/3.5-GiB review stops.

The separately accepted Nat.clog equality is outside this package. Including it would add one API fact and expand the combined closure by 256 external nodes, without changing the physical endpoint. The wider literal Real.logb ceiling bridge and the 48-state/eight-tape two-operand composition are also separate. This package begins with one canonical record and two pristine work tapes; it does not claim the selected one-string x#y caller, physical p=6b setup, source-specific parameter-record/head layout, compact-b output, radix/carry Plan, represented-list Gaussian Budget or a multiplier theorem.

## Author-checked conditional project context

At pinned selected-result context f19cb621be2caf3a7291a37c343c1c55afe935e0, certificates/selected-result.json reports

kappa = 1517760977820331 / 1000000000000000000 = 0.001517760977820331.

The author checked this exact rational/decimal equality and the selected-result-to-research/community-pr531-audit/direct-ASSEMBLY.json hash linkage. The intended publication-base pin is db0e57bc7f36b5ac0fc844ad7ce1396165ee6647, as reported by the publisher. The f19 selected record and delivered proof/review packet retain all-size/compiler, common-label/mutable-basis, normalized residual realization, correlated whole-owner hosting, restored-row, precision/tape and analytic-transfer interfaces. Reported finite-package replays are source-attributed; they are not a local replay or proof of the selected construction. The delivered text does not supply a selected scalar caller/parameter-record/head layout.

Both generic modules are independent of kappa and establish no multiplier or kappa theorem. This explicit parameter is conditional project context only. The prior 12a/4d source contexts and accepted research history remain preserved; no later selected hypothesis is imported into these proofs.

## Repository checks and AI disclosure

Substantial AI assistance was used to develop and check this contribution. Exact accepted sources, full axiom probes, predecessor attribution and independent reviews are retained. These two sources and their dependency bytes are unchanged; this packet adds no upstream source, generator or certificate repair.

The affected public Lean measurement passed the guarded 14-retained/2-fresh sequence described above. Current CONTRIBUTING requirements also include make verify and make gen4-bank-verify. Their exact new-publication-head results must be recorded separately. Historical research checks and predecessor reproductions are not fresh repository-wide aggregate results; no aggregate PASS is claimed here.

## Offline reproduction

The supported fresh sixteen-source command requires the six exact dependency packages in DEPENDENCIES.json, official Lean 4.21.0 and an already-built Mathlib checkout at 308445d7985027f538e281e18df29ca16ede2ba3. From this flat package directory:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --mathlib-root /path/to/mathlib4 \
  --input-foundation-root /path/to/PR488/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/PR511/research/lean-binary-count-dispatcher \
  --automatic-width-root /path/to/PR519/research/lean-automatic-width-count \
  --amortization-root /path/to/PR526/research/lean-count-receipt-amortization \
  --compact-copy-root /path/to/PR565/research/lean-compact-counter-copy \
  --prepared-compact-root /path/to/PR566/research/lean-prepared-compact-count \
  --build-dir /path/to/new-empty-reproduction-directory
```

The build directory must not exist. The checker validates the exact PR526 runtime-manifest reference, its 797,008 bytes and all 1,366 runtime source/object/import rows with first-match resolution. It validates all sixteen proof source hashes, sizes and imports, copies sources into a fresh isolated directory, and permits only its fresh object directory plus eight validated cache paths in Lean's search path. No dependency download or rebuild is performed. Inherited Lean paths/sysroot are ignored. Every receipt/full log and all 122 expected standard-only probes are retained. Hard caps are 60 seconds/4 GiB per root, with review stops at 40 seconds/3.5 GiB. An optional existing --slot-service supplies FIFO admission without changing proof inputs.

The approved measurement instead retains and verifies PR526's twelve public outputs, PR565's compact-copy output and PR566's normalization output, then checks only BinaryCeilLogTokens followed by BinaryParameterCount. That fourteen-retained/two-fresh sequence passed, with complete source/object/receipt/log identities and the shared runtime inventory verified before and after the two fresh checks. Its accumulated reference records are distinct from running the supported fresh sixteen-source command above.
