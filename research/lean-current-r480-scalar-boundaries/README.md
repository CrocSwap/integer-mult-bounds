# Current R480 scalar boundaries

Author-checked selected conditional context at main `7dfa22b109996e48db68daac3706e7a49a43002b`: **κ = 1584931111785787/1000000000000000000 = 0.001584931111785787**. The exact selected-result and PR535 assembly hashes are in `SOURCE_BINDING.json`. This package does not prove a complete multiplier or κ theorem.

## Checked source-specific results

Six byte-preserved Lean sources add 62 public axiom probes, reusing six exact sources from the accepted historical PR590 package:

- Current R480 domains: 120 ports, 480 helpers, 720 original registers, 672 frame IDs and the nine changed retained hosts. The B/scatter literals and specified table fields are byte-identical to the historical supplier, while the new Fin720 domain and endpoints are proved freshly.
- Exact 240 B gates / 600 ordered operand occurrences. The sequential XOR interpreter preserves arbitrary source/helper bits. Each target is its initial bit XOR a contribution independent of initial target bits; that contribution is not claimed to vanish.
- Exact retained-major 9 COPY + 568 ADD + 9 ERASE scalar slice on 721 registers. Temporary register 720 can arrive dirty, is overwritten and finishes false. Original source/helper registers are preserved. Restoration of an arbitrary incoming temporary is not claimed.
- Generic XOR inverse/reversal laws and the exact changed-host boundary: last 20 A gates and first 20 C gates, 445 operands each, maximum arity 54. All nine changed hosts appear in source order. C is bound to reversed A with frame 1 before scalarization. This isolated 40-gate scalar word is an inverse on arbitrary 720-bit state; conditional cleanup across a target-only middle map preserves that middle map's target result.

## Still open

The other 2688 A gates and corresponding C suffix, arranged in 21 proposed 128-gate chunks, have not been admitted in this package. Complete A/C composition, D dirty-helper compensation, the complete scalar shear, physical frame/entrance transport, COPY-space allocation and ERASE legality, and the full inherited all-size/κ theorem remain separate. No physical interpretation of the frame metadata or dirty temporary restoration follows from these Boolean results.

## Retained-prefix reproduction

`MANIFEST.json` classifies 12 reachable local modules: six included new sources and six retained PR590 dependencies. It lists exact source identities, import order and expected probes. The proposed public reproduction takes a successful PR590 build, verifies its six required outputs, retains those objects, and compiles only the six new sources in isolated output paths. The two historical selected Fin729 adapters are not dependencies of this current closure.

`DEPENDENCIES.json` records the concrete accepted public-prefix identities and portable validation boundary. The predecessor's runtime timestamps may differ in a separate reproduction. Its actual logs must match their PASS receipts and exact probes; generic XOR has three known source-path-only warning substitutions that require explicit normalization when comparing raw logs.

The exact 317-module official Lean 4.21.0 core closure is supplied in `OFFICIAL_CORE_MANIFEST.json`; no Mathlib installation is needed. Central checker usage and offline runtime instructions will be added after independent runtime review. `ACCEPTED_CHECKS.json` is immutable prior evidence. The sole mutable new reproduction outcome is `REPLAY_SUMMARY.json`.

Attribution, licenses, literal/source trust boundary and static author check are in `NOTICE`, `SUPPLIER_NOTICE.md`, `LICENSE`, `PROVENANCE.json`, `SOURCE_BINDING.json` and `AUTHOR_CHECK.json`. No upstream supplier program or historical full word is executed by the Lean check.
