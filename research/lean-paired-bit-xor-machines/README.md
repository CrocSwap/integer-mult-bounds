# Sequential XOR machines

## Result and coverage

Author-checked pinned context: upstream main 0b1cccf86e2f5132ed286a26ef0a681a495740ea, kappa = 836330098538459/500000000000000000 = 0.001672660197076918. This package changes no numerical bound.

Two reusable finite-word XOR implementations have checked first-halt and restoration properties:
- Boundary-observing zipper model: exactly 5n+2 transitions.
- Explicit seven-symbol marked tape: exactly 5n+4 transitions, including entry, rewind and marker handling. The controller observes the current symbol. Every prefix occupies n+2 cells, including both markers.

Both preserve source bits, return the head and clean scratch, and decode to Nat XOR. The marked result reuses the accepted zipper semantics. Empty inputs are covered.

Finite coverage: arbitrary finite paired Boolean words, without selected literal tables.
Conditional-interface coverage: paired input representation, installed markers and prescribed control/scratch entrance state are explicit. Layout construction, initialization and representation refinements still need charged implementations. A transition is a local finite-alphabet machine step; no optimality claim is made.
Full-theorem coverage: no selected physical executor, arbitrary dirty-history restoration, integer multiplication theorem or final multiplication runtime bound.

## Checked evidence and reproduction

Exact accepted sources: PairedBitXorScan SHA256 33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed; MarkedBitXorScan SHA256 f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3. Native compiler times were 1.235545627 and 1.312516520 seconds. All 13 probes and four full printed types passed independent review with no warnings. Original failed preimages are preserved in owner history. Included receipts are existing evidence, not a new relocated replay.

Lean 4.21.0, Init-only. Compile the zipper first, then the marked source with the local object directory on LEAN_PATH; README gives commands. No Mathlib or private retained objects are needed. No additional local CI preflight was performed for publication; candidate CI is checked after submission. Generic repository checks alone do not establish a fresh Lean replay.

## Attribution and bounded comparison

James Chang with OpenAI assistance, repository Apache-2.0. Lean core List/Nat bitwise APIs retain their upstream attribution, including Lean FRO and Joe Hendrix; core code is not vendored here. Existing PR612/878 and PR590 provide selected/register-level XOR semantics and generic XOR algebra. The bounded exact-source comparison found no equivalent head-moving implementation with these first-halt and prefix-footprint theorems. We claim the operational component, not novelty of XOR algebra or first-ever implementation.

## Reproduce

With the pinned Lean toolchain already installed, run from this directory:

```sh
mkdir -p build
lean -j1 -o build/PairedBitXorScan.olean PairedBitXorScan.lean
LEAN_PATH="$PWD/build" lean -j1 -o build/MarkedBitXorScan.olean MarkedBitXorScan.lean
```

Keep the full output and inspect all existing axiom probes. Historical paths in evidence are provenance only.
