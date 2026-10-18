# Multiplication preserving both operand tapes

One fixed finite **eight-tape** program multiplies every supplied pair `a,b < 2^n`, retains both original padded operand words literally, genuinely halts, and returns all eight heads to physical zero within **280n^2 + 284n + 74** transitions. The exact padded double-width MSB product remains on the core accumulator; the other five work tapes are globally blank. Width zero is included.

A concrete three-state, four-role table copies both LSB operand stacks into the six-tape arithmetic bank, preserving its sources and returning its four heads in exactly **2n+2** transitions. A real one-step scheduler handoff starts the prior origin-return multiplier. The full invoice is `(2n+2)+1+(280n^2+282n+71)`. No input-size counter, free head reset or hypothetical copying gadget is used.

## Formal interfaces

All names below have prefix `MultitapeToolkit`.

- `PairedInputCopy.exact_correct`: the literal finite paired-copy table, exact cost and actual halt for arbitrary equal-length bit lists.
- `IntegerMultiplicationPreserving.product_correct`: complete actual multiplication at the stated bound.
- `IntegerMultiplicationPreservingCertificate.exists_fixed_preserving_multiplier`: one fixed program quantified before all widths and operands, explicit operand equality, product bank, heads, halt and value.
- `IntegerMultiplicationPreservingApplications`: arbitrary-natural minimal-width padding, actual finite host-bank runs, whole-machine dirty-spectator preservation and core-stage protected-input preservation.

The protected heads move during copying and return by a charged rewind. Only the arithmetic-stage prefix theorem states they remain stationary; its boundary is the actual `coreInput`. Entirely extra host spectator heads and whole cell functions remain unchanged at every prefix of the complete embedded machine. Retaining operands costs two extra tapes. Supplied padding is an input representation, not a paid parser; this is not a signed parsing or modular truncation implementation.

## Reproduction and checked scope

Lean **4.34.1** and the Mathlib revision in `lean/lake-manifest.json` are pinned. Every proof imports only bundled source or pinned Mathlib/Lean. Run:

```sh
python3 -I -B verify.py
python3 -I -B replay.py --out /absolute/new/check --cache-project /path/to/pinned/cache --lean /path/to/lean
```

`verify.py` checks immutable inventory and independent finite operational/negative controls; it does not run Lean. Public `replay.py` cold-rebuilds all bundled modules and audits every defining-module declaration, including private and generated helpers, with four actual Lean ownership/axiom fixtures. Only `propext`, `Classical.choice` and `Quot.sound` are allowed; even unused package axioms are rejected. Mathlib cache artifacts are revision-checked, not independently rebuilt here.

This local release freshly checks the four new modules and aggregator, independently checks the unchanged frozen universal root, and freshly audits the complete declaration/transitive-axiom closure. The **59 unchanged dependency artifacts** are reused under exact previously checked source/artifact, closed-import, toolchain and dependency-revision guards; that chain is recorded in `PORTING.json` under `verified_reuse`. This local run is not claimed as a new full cold rebuild. `expected/AXIOMS.json` records the whole current declaration inventory and `MANIFEST.json` binds all distributed sources. Final local receipts bind the actual upload files. Hosted CI and human review are not claimed.

## Related work and attribution

Actual upstream main was refreshed to `6ca6f217708b075814de409ad693fea9a2aaa760`, with 30 recently updated PRs through #2780 inspected as a bounded inventory, not exhaustive novelty evidence. The direct predecessor is [PR2780](https://github.com/CrocSwap/integer-mult-bounds/pull/2780), whose actual sources already provide physical head return and spectator embeddings. Its arithmetic/compiler/serialization/parking lineage and source notices remain credited.

[PR2776](https://github.com/CrocSwap/integer-mult-bounds/pull/2776) already supplies source-preserving copying, paid rewinds and cleanup in a concrete 14-tape ordered-shear controller. Its machine, shear implementation and written proof were inspected, not independently replayed. Copying, preservation and head return are existing techniques. The focused contribution is their complete Lean-checked integration into this specific eight-tape multiplication ABI, with its charged bound and literal operand-preserving endpoint.

Dan Brown and Kenny Daniel's MIT-licensed [external development](https://github.com/platypii/integer-mult-bounds-lean/blob/4f40b5bc74235274835fe6952b9b90ac414786b0/IntegerMultBounds/MathlibTM2/Theorem.lean), linked by PR2411, already proves complete finite Mathlib-TM2 asymptotic multiplication through `MulInTime ((2^34 : Real)^-1)`. Its relevant sources were inspected in the preceding campaign, not independently replayed here. No external proof code is copied or imported. We claim no first multiplication/copying theorem, new exponent, selected kappa improvement or complete fast-algorithm caller.

Apache-2.0 and retained notices apply to the bundled lineage. Substantial OpenAI Codex assistance used one root and three parallel agents; no Jev.

## Open next questions

- Implement a charged serialized or signed parser into the supplied padded input ABI.
- Connect the preserved operands and returned product to actual marked-buffer recursive callers, with placement and routing charged.
- Develop charged variable-depth recursion; this concrete quadratic leaf does not prove the entire fast algorithm.
