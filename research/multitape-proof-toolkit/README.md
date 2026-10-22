# Verified multitape callers, stack anchors and multiplication output

Self-contained Lean proofs for contributors building physical multiplication
algorithms. The fixed finite machines, actual runs, halting, tape contents, head
positions and physical charges are proved. Imports are Mathlib, Lean and bundled
public modules; no personal Lean installation is required.

The seven new modules extend PR1641 with four reusable links:

- `Absolute.TapeEmbedding` places any fixed machine in a larger finite tape bank
  without changing its step count, preserving arbitrary extra tapes at every
  prefix. `Absolute.GenericParkingController.wrapper_correct` permits children
  to use extra work tapes and return an explicit changed workspace; its exact
  cost is `2|x| + 2|z| + 5|y| + 16 + t` for actual child time `t`.
- `Absolute.CleanBoundary.machine_correct` supplies actual marker installation,
  closed bit-flip call and removal. Its exact cost is `6|x| + 5|y| + 24`, including
  both additional handoffs. IO and temporary tapes are fully blank at entry and
  return; the inactive stream and arbitrary parking bank are restored literally.
  `Absolute.GenericParkingController.clean_machine_correct` embeds this in any larger
  finite bank with dirty spectators. The parking bank retains its existing
  boundary separator; operand/IO/temp buffers are unmarked.
- `TM2Compiler.Anchored.anchored_compile_run` strengthens compilation with fixed
  stack bottom anchors: every final head equals `anchor - final stack length`.
  It constructs the actual run at the existing overhead and preserves exact
  cells, including the real peek/pop scan phases. Stack lengths are proof data,
  never unbounded control registers or free head resets.
- `Absolute.StackOriginSerializer.serialize_correct` implements a five-state,
  three-symbol table. A padded LSB compiler stack at any head `h` becomes an MSB
  word starting at destination origin zero in exactly `3m + 4` steps. The source
  is fully erased, its head returns to `h`, destination head returns to zero,
  padded zeros are retained and dirty spectator tapes are unchanged.

`BinaryMultiplicationOriginABI.quadratic_origin_product` closes a concrete
arithmetic example. One fixed six-tape machine accepts two length-`n` LSB stack
operands at head zero (blank cell 0, operand bits in cells 1..n), with four
globally blank work tapes. For every
`a,b < 2^n`, it actually halts with the exact padded `2n` MSB product at origin
zero on `sumReverse`, erases the accumulator and takes at most
`280n² + 314n + 117 <= 400(n+1)²` physical transitions. Input loading, output
conversion and the handoff are charged. Width zero is included, with a proved
fully blank zero-output endpoint. The nonzero arithmetic endpoint retains its
explicit residual multiplicand and head positions; complete work-tape cleanup
and serialized operand input are separate interfaces.

The release retains the preceding compiler, heterogeneous alphabet, dirty-frame,
locality, exact trace, scheduler, footprint, canonical-output and asymptotic
proofs. It bundles the connected Problem1.8 arithmetic dependency closure under
public module names, preserving the proofs and source attribution.

This supplies reusable sufficient execution theorems and a verified quadratic
output ABI. Numerical supplier profiles and kappa are unchanged. The arithmetic
example's Option-Bool stack ABI and the caller's marked four-symbol IO ABI require
an actual input/alphabet/cleanup bridge before the example is a caller child.
The package does not assume that bridge or a recursive multiplication oracle.
Upstream already has serialization and output cleanup; this is direct compiler
ABI interoperability, not a claim of new serialization mathematics.

## Verification

Lean 4.34.1 and Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612 are pinned in
`lean/lean-toolchain` and `lean/lake-manifest.json`. From this package:

```sh
python3 -I -B verify.py
python3 -I -B replay.py --out /absolute/new/check --cache-project /path/to/pinned/cache --lean /path/to/lean
```

The first command checks immutable sources, finite operational controls and
corrupted-report rejection; it does not run Lean. The second rebuilds every
bundled module into a fresh external directory and audits all declarations by
their defining module, including private, global and generated helpers. Only
`propext`, `Classical.choice` and `Quot.sound` are allowed; package axioms are
rejected even when unused. Real Lean negative fixtures test these boundaries.
The dependency cache supplies pinned Mathlib/Lean libraries only; no existing
toolkit or personal proof artifacts can satisfy the fresh build.

`VALIDATION.json` binds the proof sources and checks. `MANIFEST.json` binds every
shipped file. Supporting finite table simulations include empty and unequal
words, negative heads, arbitrary parking backgrounds, full cell restoration and
a corrupt marker-removal rejection. Universal evidence is the fresh Lean check
and complete axiom audit, rather than these finite controls. Hosted CI and human
review are separate. `ci/formal.yml` supplies an optional formal workflow;
generic `VERIFY.json` runs Python only.

`API.md` gives theorem interfaces; `PROOF.md` explains assembly and costs;
`PORTING.json`, `REUSE.json`, `NOTICE.md` and `FRONTIER.json` record source reuse,
attribution and bounded current PR review. No platypii proof source is copied.

## Open next questions

The exact follow-ups in `TASK.json` are physical serialized-input/alphabet and
complete arithmetic-cleanup bridges, followed by on-tape dynamic recursion and
row routing. Start with the supplied anchored compiler, actual serializer and
literal arbitrary-bank caller contracts; charge each new transition.
