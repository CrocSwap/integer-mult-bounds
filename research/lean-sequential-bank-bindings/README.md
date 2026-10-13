# Lean: sequential completed banks and five-stage source bindings

This package proves a conditional composition theorem for completed local bank words and connects the selected five-stage bit source to its routing and chronological scheduling interfaces. It contains eight Lean modules and imports only Lean's standard library. The sources have been checked with Lean 4.21.0.

## What is proved

`SequentialCompleteBank.sequential_complete_bank` composes a chronological list of complete local words. Its local premise quantifies over every bank state and every remaining state:

- The bank output is the prescribed partial swap in one common, exact chart.
- The remaining output is a supplied function of the remaining state alone.
- The projectors, listed in the endpoint API's reverse order, are disjoint and sum to the identity.

Under those premises, the concatenated words perform the full bank swap in that chart and the specified chronological evolution of the remaining state. The theorem does not require clean helpers or an independence assumption on their initial contents. The universal local endpoint is still a premise that a concrete physical supplier must prove.

The list-order bridge is explicit. `FrameTransport.run` executes head-first; `BankEndpoints.runCompleted` applies tail-first. The proof reverses the endpoint list to match those conventions. This list reversal does not interpret an erased value as invertible or assert a physical backward-word identity.

`FiveStageBankAddress.address_factor` proves the literal source identity

```
route (d * tau) N = route d (N * tau⁻¹).
```

Here `route g H = g * H⁻¹`, and the supplied group laws are the only algebraic inputs. There is no commutation or involution premise. The inverse, unique-bank visitation, reduction and complete-fiber corollaries reuse `BankRouting`.

`FiveStageBankSource` records the selected source's active bank pairs, complemented stages, logical-family arithmetic, MOVE/ADD/COPY/ERASE lowering, operand-versus-frame metadata distinction, normalizer factor order, and phase schedule. Its structural theorem identifies the chronological, replica-major cover sweep. All 60 replicas are retained: allocation uses `role_index * 60 + replica`, so one replica alone generally does not fill a bank.

These definitions are tied by source review to the Python methods at the pin below. The Lean proofs do not certify an execution of Python or supply the actual local records, chart tables or complete cover enumeration.

## Source and κ context

The source pin is `12a4934d15006e8c10f9b2264f13f8f341be802b` in [CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds/tree/12a4934d15006e8c10f9b2264f13f8f341be802b). The literal bindings come from `research/five-stage-gen4-banks/bank_template.py` and `code/global_lowering.py`; the completed-bank argument is described in `BANK-PROOF.md`.

The author-checked value recorded by that pin's [`certificates/selected-result.json`](https://github.com/CrocSwap/integer-mult-bounds/blob/12a4934d15006e8c10f9b2264f13f8f341be802b/certificates/selected-result.json) is

**κ = 90446448750933 / 125000000000000000 = 0.000723571590007464.**

This is the selected source's conditional construction value. This package does not derive κ or prove an end-to-end multiplication bound. The selected result retains compiler, common-ancestor chart, restored-row, routing, prime-supply, precision/recovery, complex-correctness and analytic-transfer conditions. The pin is explicit; no claim about a later remote head is intended.

## What remains to connect

The concrete selected construction must still supply:

- The actual helper census and role-to-slot correspondence, complete cover and full GL120 reduction data.
- Exact evaluated normalizer matrices, chart inverses, denominator units and the required namespace separation.
- Complete forward and complemented-reverse physical words with the universal full-state endpoint and common chart used by the theorem.
- The actual full-bank partition across all 60 replicas, before removing independent completion instructions.
- Boundary projectors, final normalization, restored selectors and all-price costs.

No old bit72, complex66/1320 or O66 finite binding is transferred by changing a dimension name. The separate complex110 provider is outside this package.

## Modules and prior work

The five unchanged supporting modules are `BankRouting`, `SplitProjectors`, `CoordinatePartitions`, `ExactFrameTransport` and `BankEndpoints`. The three added modules are `SequentialCompleteBank`, `CurrentFiveStageBankAddressFactor` and `CurrentFiveStageBankSourceSchedule`.

The additions reuse the supporting group, routing, conjugation and partition results, plus standard list lemmas. They do not reprove a general group engine, generic all-K chain or generic parallel-stage theorem, and no novelty claim is made for those ingredients. The source construction credits the PR197/PR200 completed-bank work, Henry Grant / hcg890's PR234 lowering, and the retained source527 package by eumemic; the gen4 source notices and assistance credits remain applicable. See `PROVENANCE.md` for exact pins and the attribution boundary.

The Lean source is portable. A resource-audited replay checker using `/proc` requires Linux; repository-specific replay instructions and manifests accompany the packaged files.

## Reproduce the package

Use Linux, Python 3 and the official Lean 4.21.0 distribution. From this directory run:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --build-dir /tmp/sequential-bank-check
```

The build directory must not already exist. The checker validates every source hash and import order in `MANIFEST.json`, then checks exactly eight modules offline in a fresh output directory. Only that output directory and the installed core Lean library are on the search path; no Mathlib or network download is needed. Hard per-module limits are 60 seconds and 4 GiB address space. A successful check exceeding 45 seconds or 3.5 GiB stops for review. The checker uses Linux `/proc` to sample memory. No compiled objects are included.

`ACCEPTED_CHECKS.json` records the prior eight-module checks and all 77 printed axiom probes. The isolated eight-source package replay passed in 12.1047 compiler seconds and 0.00368 queue seconds, with peak virtual memory 2,266,423,296 bytes. All eight object hashes match the recorded accepted checks; all 77 complete theorem/axiom outputs match after whitespace normalization; see `REPLAY_SUMMARY.json`. The two named roots remain separate; no new import-only union is introduced.
