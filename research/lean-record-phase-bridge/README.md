# Signed record phases to the selected tensor action

This package composes PR2378's separate signed-word and coordinate theorems:
every Gaussian coefficient field in a record receives the selected phase, and
the decoded result is the full-array tensor action. It takes the explicit
[record/encoding handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2378)
at `5816f94741709e8082e06a2cc9a114ff87411f3d`.

The new contribution is the **quantified formal composition**, including a
common exact grid scale and a guarded decoded inverse. PR2378 already tests
packed phase words and two-field full arrays. Those tests and its arithmetic
proofs are credited predecessors, not missing coverage discovered here.

## Exact proposition

The unchanged recipe is residual `0:1000.right`: its 22-gate word implements
the affine map `sigma(x) = Lx XOR 245` on nine-bit addresses. Its constant
phase is 2 and its strict-upper polynomial is `q`. All literals, source hashes
and prior proofs are retained unchanged.

Let `decode : P ≃ S × (Fin f → Fin 512)`, where `S` contains the spectators.
Let `h : P → C → WordPair` be any encoded coefficient array; `C` indexes every
Gaussian coefficient field in each record. Each real and imaginary word is
LSB-first two's complement, of width `w+1`. Write

```
k(p) = 2*f + sum_j q((decode p).2 j).
```

For every address and field, require `Fits w (phaseOfNat k(p)) (h p c)`.
This checks both widths and the exact phase-specific signed guard: the
most-negative real component is excluded only when it is negated, and likewise
for the imaginary component. `ForwardFits` quantifies this over **all fields**.

`decode_scan` proves that the list traversal multiplies every decoded field
by `i^k`; `serialized_scan_length` proves exact preservation of the concatenated
record extent, `number_of_fields * 2*(w+1)` bits. No first-field shortcut is used.

Assume also PR2378's `CompletedPrimitive decode step`: every completed address
gate implements its specified column action and restores spectators. Then
`forward_tensor` says that applying encoded phase, followed by the literal
address word, decodes to

```
coordinates ∘ PiTensorProduct.map (selected unary monomial) ∘ coordinates.symm
```

for every field and spectator slice. `scaled_forward_tensor` gives the same
identity after multiplying each decoded Gaussian integer by any common complex
scale, including an exact dyadic grid unit. The array may be arbitrarily
correlated across fields, columns and spectators **within this encoding and
its signed guards**. The proof does not assume pure tensors or clean spectators.

`backward_refines` undoes the address word before inverse phasing at the
recovered input address. `decoded_roundtrip` proves decoded restoration under
the forward and backward guards. Formal `f=0` and one-bit widths are allowed;
the retained Python implementation has the narrower `f>=1`, width>=2 domain.

## Remaining boundary

This closes the signed payload composition in the staged Lean model. Actual
Compact/digit endpoints still supply `CompletedPrimitive`. Record transport is
modeled by address pullback; the sequential Python/tape machine and the
translation into Lean are not formally verified. The theorem about serialized
length is not a proof of the interpreter's tape head, time, storage or scratch
behavior. The finite replay checks concrete execution of that interpreter.

The caller must still establish coefficient widths, every-field headroom,
the common grid, and its completed physical gates. Complete selected hosting,
restoration, precision bounds and outer multiplication remain outside this
package. No selected source or exponent is changed.

## Verification

`KERNEL.json` records a fresh Lean 4.33.0-rc1 build at commit
`62eed1db4d67327ec8120be05f1a1b0847d74561`, with pinned Mathlib
`55b7917b472489c7c56a0fa6393af05cfd536599`. All 46 actual axiom probes
(31 retained roots and 15 new ones) use only `propext`, `Classical.choice` and
`Quot.sound`, or no axioms. Three false proofs fail after valid imports:
skipping later fields, dropping headroom, and using a single constant phase.

`FINITE.json` is a separate implementation-binding receipt. Its oracle uses
integer 2-by-2 rotation matrices and direct affine/parity arithmetic, while
executing the unchanged PR2250 streams, Compact and monomial modules. It uses
the target's layout encoding; it is not an independent physical layout proof.
The literal Lean recipe is compared with the source recipe and compiled word.

| Evidence | Coverage |
|---|---|
| Signed phase census | 33,280 cases at widths 3 and 6, four phases and both directions; 32,708 signed exact and 572 outside headroom |
| Complete execution | Three 4,096-record arrays, with 1/3/5 coefficient fields at widths 3/5/7; all eight dirty spectator combinations; exact forward oracle and inverse restoration |
| Semantic controls | Only first field phased despite consuming all bytes; later-field overflow despite byte restoration; missing repeated constant; malformed record extent; truncated input; inverse phase at wrong address |
| Package controls | Nine groups covering source hashes, proof escapes, inventories, actual axiom report parsing, strict JSON, receipt corruption and explicit execution mode |

The repeated-constant check includes the proper two-column phase as a positive
control. Complete physical fixtures have one nine-bit column; the theorem
quantifies over every finite `f`. Finite patterns do not enumerate every possible
payload. These are local verification results; hosted CI and maintainer review
are separate.

## Reproduce

The registered Python replay checks source/receipt binding, finite execution
and failure controls. Its output explicitly says `kernel_checked=false`:

```sh
python3.12 -B scripts/research_package.py --package research/lean-record-phase-bridge
```

To perform an actual fresh kernel build, supply the pinned Lean executable and
an unused directory. This may fetch the exact dependencies and their cache:

```sh
python3.12 -I -O -B research/lean-record-phase-bridge/verify.py \
  --lake /absolute/path/to/lean-4.33.0-rc1-linux/bin/lake \
  --work-dir /tmp/record-phase-fresh-build --fetch-cache \
  --out /tmp/record-phase-kernel.json
```

An existing exact dependency checkout may instead be passed with
`--packages /absolute/path/to/.lake/packages`. Every dependency Git head and
tracked source is checked. Local proof objects are always built afresh. The
dedicated workflow performs this kernel command; the generic package runner
does not. The verifier refuses existing output/build destinations. A fresh
kernel run can bootstrap an absent historical receipt; the default replay
requires it. `PROOF-SOURCES.json` inventories all Lean and retained sources;
`PREDECESSOR.json` adds exact upstream paths and Git blobs.

Attribution and substantial AI assistance are detailed in [NOTICE.md](NOTICE.md).

## Open next questions

- Discharge `CompletedPrimitive` for an actual completed Compact/digit ADD.
  Start with one retained PR2250 endpoint, proving record transport and dirty
  spectator restoration. A formal tape semantics and its source binding remain
  prerequisites.
- Connect the actual selected caller's precision ledger to `ForwardFits` and
  `BackwardFits`. Start with one whole invocation on its fixed grid. The scale
  theorem supplies the algebra; it does not supply the caller's bounds.
