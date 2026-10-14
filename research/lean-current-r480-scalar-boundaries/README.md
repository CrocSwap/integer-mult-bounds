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

`MANIFEST.json` classifies 12 reachable local modules: six included new sources and six retained PR590 dependencies. It lists exact source identities, import order and expected probes. The public checker takes a successful PR590 build, verifies its six required outputs, retains those objects, and compiles only the six new sources in isolated output paths. The two historical selected Fin729 adapters are not dependencies of this current closure.

`DEPENDENCIES.json` records the concrete accepted public-prefix identities and portable validation boundary. The predecessor's runtime timestamps may differ in a separate reproduction. Its actual logs must match their PASS receipts and exact probes; generic XOR has three known source-path-only warning substitutions that require explicit normalization when comparing raw logs.

The exact 317-module official Lean 4.21.0 core closure is supplied in `OFFICIAL_CORE_MANIFEST.json`; no Mathlib installation is needed. `ACCEPTED_CHECKS.json` is immutable prior evidence. The sole mutable new reproduction outcome is `REPLAY_SUMMARY.json`.

Attribution, licenses, literal/source trust boundary and static author check are in `NOTICE`, `SUPPLIER_NOTICE.md`, `LICENSE`, `PROVENANCE.json`, `SOURCE_BINDING.json` and `AUTHOR_CHECK.json`. No upstream supplier program or historical full word is executed by the Lean check.

## Offline checker usage

Use the official Linux x86-64 Lean 4.21.0 distribution named by `lean-toolchain`, with both `src/lean` and `lib/lean` intact. The checker rehashes its exact 317 source/object pairs and executable; it does not fetch dependencies. Python 3 on Linux with `/proc` is required. Run Python without `-O`.

First obtain the exact historical package `research/lean-selected-bit-scalar-boundaries` from PR590 and a successful build made by its checker. Pass that package and build to this checker; it validates the six required source/object pairs, complete probes, actual raw-log/receipt bindings and predecessor PASS result before creating any output. A predecessor receipt can have different timestamps. Only the three known generic-XOR warning source paths may normalize; all other log bytes are exact.

```sh
python3 check.py \
  --lean /path/to/lean-4.21.0-linux/bin/lean \
  --prefix-package /path/to/research/lean-selected-bit-scalar-boundaries \
  --prefix-build /path/to/successful-pr590-build \
  --build-dir /path/to/new-current-r480-build
```

The new build directory must not exist. The checker copies six validated retained objects and stages twelve exact source files in the new directory. Only the six included current sources are compiled, in the manifest's dependency order. It writes untouched compiler logs, object files, per-module receipts and one build-local `REPLAY_RESULT.json`. Successful retained and fresh objects are rechecked between jobs. The repository's `REPLAY_SUMMARY.json` separately records this publication's one observed reproduction.

`--guard-only` verifies the complete input boundary and fresh output absence without creating the build or running a proof compiler. `--require-observed-prefix` additionally requires this package's exact recorded local predecessor result/receipt/raw-log hashes; omit it for an independently produced compatible predecessor build. `--slot-service /path/to/existing_service.py` uses an existing shared FIFO service exposing `acquire()`. The publication reproduction uses that shared service.

Each fresh compiler has a 60-second and 4-GiB hard bound and a 45-second / 3.5-GiB review threshold. The sequence stops at the first failure or review event and retains its evidence. Source/prefix checks occur again after FIFO acquisition; their time, compiler time and FIFO time are reported separately. No predecessor proof is recompiled by this command, no supplier program is executed, and no full A/C theorem is inferred from this bounded reproduction.
