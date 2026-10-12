# Canonical compact-counter copy in an explicit tape model

This package contains one unchanged accepted Lean source, `BinaryCounterCompactCopy.lean`, for a concrete nine-state, two-tape machine. Five exact external source dependencies come from PR488 and PR511; `DEPENDENCIES.json` gives their commits, original paths and hashes. No merger is assumed.

## Checked contract

Let `bits` be any finite Boolean list in little-endian order, let `n = bits.length`, and let `p = compact bits` be the list obtained by deleting its high, trailing false bits. Write `m = p.length`.

Input tape 0 starts at the represented blank immediately before the whole word, in the exact marked-home shape `⟨[], blank, bits.map bitSymbol ++ [blank]⟩`. Tape 1 must be pristine `Tape.blank`. There are exactly two tapes, with no arbitrary spectator parameter in the public contract.

`compact_run_exact` reaches halted state 8 with these exact tapes:

- Tape 0 is `⟨[], blank, p.map bitSymbol ++ replicate (n - m + 1) blank⟩`. It retains the original `n + 2` represented cells, including the marked boundaries and the blanked high-zero cells.
- Tape 1 is canonical `Tape.ofWord p`, with its head at the first retained bit when `p` is nonempty. The buffered copy never allocates an extra output blank.

The advertised run index is `2*n + 3` when `p` is empty and `2*n + 2*m + 4` otherwise; `elapsed_bound` proves it is at most `4*n + 4`. Empty input takes three transitions. Every all-zero input leaves the output exactly `Tape.blank`. The theorem supplies this run index and a halted endpoint; it does not assert first completion.

The source proves the physical/list-level endpoint. Numeric value preservation, a logarithmic-length theorem, and adaptation to a caller that represents zero by a digit remain separate obligations. Clearing the source's high cells alone is not treated as a canonical compact output: the theorem includes the actual copy onto the pristine tape.

## Provenance and scope

The package reuses PR488's explicit fixed-tape semantics and PR511's marked-home counter representation. It adds a physical compact-copy routine, not a new generic increment or counter amortization proof. PR64's richer counter theory and the PR526 arithmetic transport are not imported here. No complete prepared-input caller, six-tape composition, radix/carry Plan, Gaussian represented-list Budget, or multiplication theorem is claimed.

The six-source core-only closure has 41 complete standard-axiom probes, including nine in the new source. The accepted owner check took 5.227754931 seconds and peaked at 1,729,949,696 bytes virtual memory. The exact source includes a module-local `Elab.async false`; kernel checks and the 60-second/4-GiB hard and 40-second/3.5-GiB review limits were retained. The guarded public reproduction is complete: five verified public prerequisite outputs were retained and only this new root was checked, using 3.7400 compiler seconds and 0.000447 FIFO seconds. Fresh-root peak VM was 1,729,921,024 bytes. All 41 complete standard-only probes and all six reference objects match. All six full logs match the reference bytes. The five retained outputs were checked in the PR526 reproduction; their source origins remain PR488 and PR511. REPLAY_SUMMARY.json records the retained and fresh measurements separately.

## Author-checked conditional project context

At the pinned selected-result context commit `f19cb621be2caf3a7291a37c343c1c55afe935e0`, `certificates/selected-result.json` reports the conditional finite-construction parameter

`kappa = 1517760977820331 / 1000000000000000000 = 0.001517760977820331`.

The author checked this exact rational/decimal equality and the selected-result-to-`research/community-pr531-audit/direct-ASSEMBLY.json` hash linkage. The publication branch base is `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`; the publisher's exact Git comparison reports the selected result, linked certificate, licensing, existing Lean sources and toolchain unchanged from that pinned context. This is the new PR531/523/493-family source context; the earlier PR279 context at `12a4934` and the intermediate `4d18ff5` author readbacks remain preserved in the research provenance.

The selected record reports finite-package replays while retaining conditional all-size/compiler, common-label/mutable-basis, normalized residual realization, correlated whole-owner hosting, restored-row, precision/tape and analytic-transfer interfaces. Its historical research ceilings are not independently certified by that integration. This compact-copy package neither replays those finite packages nor proves their construction-specific interfaces, and it establishes no multiplier or kappa theorem.

The generic physical theorem, five immutable PR source dependencies, official Lean core and accepted public reproduction remain unchanged. The delivered earlier `4d18ff5` to `f19cb62` comparison contains no Lean-source changes, and LICENSE/NOTICE are unchanged. For the later `f19cb62` to `db0e57bc` base update, the publisher reports the pinned dependencies, existing Lean sources and toolchain unchanged; unrelated new Lean packages are outside this closure. Adopting the new conditional context does not substitute any new selected construction for the checked tape model. `PROVENANCE.json` records both current and historical context pins.

Repository Apache-2.0 licensing and applicable NOTICE/attribution accompany the public package.

## Offline reproduction

Use the official Lean 4.21.0 installation identified by `EXTERNAL_OBJECTS.json`. Its 1,300 source/object pairs are checked before compilation; Mathlib and downloads are unnecessary. Supply local worktrees at the exact commits in `DEPENDENCIES.json`.

From this package directory, the supported fresh six-source command is:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --input-foundation-root /path/to/PR488/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/PR511/research/lean-binary-count-dispatcher \
  --build-dir /absolute/path/to/new-empty-build
```

The build path must not already exist. The checker stages exact source bytes and uses only the fresh output directory in `LEAN_PATH`, with official core imports supplied by that Lean installation. It checks all 41 complete theorem/axiom outputs, stops on the first error or review-limit breach, and records full logs, receipts and object hashes. An optional `--slot-service` accepts an existing shared runner exposing `acquire()`.

The coordinator's authorized measurement is a guarded five-retained/one-fresh sequence: five exact public source/object/receipt/full-log sets from the completed PR526 reproduction are compared with current core-only accepted objects, copied into a fresh output tree, and only `BinaryCounterCompactCopy` is compiled. These five source files retain their original PR488/PR511 pins. This guarded five-retained/one-fresh sequence is complete and is distinct from executing the supported fresh six-source command above.

## Repository checks and disclosure

Substantial AI assistance was used to develop and check this contribution. The exact Lean source, bounded kernel receipts, complete axiom probes and independent readbacks are recorded in the accompanying evidence.

This change adds only this research package; it changes neither `upstream/` nor generator or root certificate files. The affected Lean reproduction is described above. Current `CONTRIBUTING.md` additionally requires `make verify` and `make gen4-bank-verify`; repository-wide results at the new publication head must be recorded separately from this package's completed isolated reproduction. No fresh aggregate result is claimed here. Historical links in the contribution guide do not replace the explicit selected-result pin or add proof assumptions.
