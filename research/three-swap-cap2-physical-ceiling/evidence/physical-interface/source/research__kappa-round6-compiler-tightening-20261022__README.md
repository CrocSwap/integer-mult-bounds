# Conditional kappa 0.0030217758: a smaller finite compiler reserve

TL;DR: the same admitted native word and complete p16 profile support
**kappa = 15108879/5000000000 = 0.0030217758**, an increase of
**0.0000000158** over PR4610's frozen 0.00302176 checkpoint. This is a
numerical/compiler tightening. The native construction and its raw moment
crossing have not improved. The complete conditional claim still depends on
the predecessor native, compiler, tape, precision and recovery hypotheses.

Cao Yifan, with substantial OpenAI Codex assistance. Apache-2.0; predecessor
notices and attribution are retained.

## What changes

The tested saving is **0.00302177581**, strictly greater than the claimed
kappa. The contraction reserve decreases from `1e-9` to `1e-11`. The existing
power 1024, cutoff 20, completion floor 21, tail offset 1/5, tail coefficient
97/100, complement factor 63/64 and logarithm power 1000 are retained.

Two exact interval implementations place the unchanged raw crossing in
`(0.00302177587077, 0.00302177587078)`. This crossing is not the claimed
compiler saving. At the new tested saving the paid/target ratio is below
`0.999999999936687383304469699480`, leaving more than the new reserve.
The real contraction proof separately includes that reserve.

The complete controller still has **64,404 paid calls** and **10,928 productive
fields**. Its local paid profile is `{1:2201,2:412,3:510,4:127,5:40,8:8}`;
the complete helper census is `{4:28,7:7,8:47,9:326}`. The numerical proof's
literal complete profiles are checked against this controller. The aggregate
Lean theorem binds them to the actual finite native census and helper endpoints.

The strict outer gap is `1/700000000000`. Recomputing the whole finite compiler
gives `j=55099`, `H=38569300000000000` and `N=2^38569300000000000`.
Lean checks `(H+1)^1000 < 2^55099`; the preceding integer fails the corresponding
test. The expanded algorithmic word is not materialized. Its uniform saving is
`1057621533/350000000000`, still strictly greater than the claimed kappa.

`arithmetic.py` is a readable four-replacement derivative of the frozen exact
engine, recorded in `ARITHMETIC-SOURCE-PATCH.json`. Its inherited status/scope
strings use the predecessor's "changed profile" wording; in this package the
profile is unchanged. `ARITHMETIC.json` records full recomputation, both charged
tails, capacity, all 54 strict outer predicates and four functional predicates.
No paid call, completion or routing charge is removed.

## Proof and audit boundaries

The four fresh modules are `TightenedNumerical`, `TightenedArithmetic`,
`TightenedCapacity` and `TightenedVerification`. They expose 31 axiom reports.
The authority for their completed replay is status
`PASS_TIGHTENED_SCOPED_LEAN_CERTIFICATES` in `LEAN-VERIFICATION.json`, genuine
logs and their source/object hashes. The replay uses Lean 4.21.0 and mathlib
`308445d7985027f538e281e18df29ca16ede2ba3`, checks source syntax and admits
only `propext`, `Classical.choice` and `Quot.sound` in printed axiom reports.
The larger integer test uses a 256 MiB Lean thread stack; kernel checking is
retained.

Native and strict-concavity modules are **explicitly reused** from the frozen
round3 proof package. Their actual source, log, object and dependency hashes,
compile commands, axiom reports, 49 external input pins and runtime are checked.
The new receipt lists this reuse separately from the four fresh compilations.
It does not claim another fresh replay of the native word. The payload remains
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.

`audit/` supplies a separately implemented AI arithmetic audit. It reconstructs
the controller from the admitted native counts, checks exact interval signs,
tails, compiler capacity, the finite integer threshold and source outer
formulas. It is not independent human attestation.

These are scoped Lean certificates, not an end-to-end Lean theorem about
integer multiplication. JSON transcription, native amplitudes, absolute phases
and free-group endpoint semantics remain explicit Python/proof boundaries.
Whole-job normalization, permitted owned erasure, physical fixed-tape execution,
precision, stock, analytic decomposition, prime avoidance and exact recovery
retain the predecessor hypotheses. The new arithmetic does not establish a
new physical admission lemma or a practical speedup.

## Reproduce

Use global Python 3.14 and the pinned Lean/mathlib setup documented in
`../kappa-round3-warp-lean-20261022/README.md`. From the repository root:

```powershell
py -3.14 -B research/kappa-round6-compiler-tightening-20261022/arithmetic.py --native research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json --kappa .0030217758 --out research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json
py -3.14 -B research/kappa-round6-compiler-tightening-20261022/prepare.py
py -3.14 -B research/kappa-round6-compiler-tightening-20261022/verify_lean.py
```

On this Windows host, invoke
`C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe` in place of
`py -3.14`; the installed launcher does not find that interpreter. On other
systems use the actual global Python 3.14 executable.

The replay pins the Windows Lean executable used for these receipts. Checking
the sources with a compiler for another platform requires an explicit runtime
pin adaptation and a separate receipt.

Compiled objects and toolchains are not committed. In a clean checkout first
compile the native dependency closure, without overwriting its published receipt:

```powershell
py -3.14 -B research/kappa-round3-warp-lean-20261022/replay.py --only Native AnalyticGain --receipt LOCAL-NATIVE-REPLAY.json
py -3.14 -B research/kappa-round6-compiler-tightening-20261022/verify_lean.py --native-receipt research/kappa-round3-warp-lean-20261022/LOCAL-NATIVE-REPLAY.json
```

The first command rechecks the frozen native/phase inputs and generates a
partial native receipt; the second validates exactly that dependency closure
before compiling all four new modules. Runtime pins must match. Do not
regenerate source receipts concurrently with replay. Regeneration of unchanged
native receipts changes timing metadata and their hashes; preserve the frozen
receipts when reproducing this package.

## Attribution

This tightening uses Cao Yifan's already published PR4610 native word and
compiler certificates. It adds no new native supplier. Cinna Davis's PR4470,
Dugongue's transported frames, zxv's native/compiler work, Jacob Alan Sussman's
mixed-target recursion, Pierre-Loic Doulcet's concurrent helper-interface work
and their credited predecessors retain their original attribution. The earlier
0.00302152 and 0.00302176 packages remain frozen.

Signed-off-by: Cao Yifan. Substantial OpenAI Codex assistance.

## Open next questions

- Can a changed scalar word or recursive interface increase the raw crossing?
  Start with a concrete emitted word and its full arbitrary-helper contract.
  The current paid profile and retained paired path are the limiting inputs;
  numerical tightening alone cannot move their crossing.
- Can the complete compiler implication be formalized in Lean? First add the
  native amplitude/absolute-phase semantics and a precise physical execution
  contract, then connect them to the existing finite frame certificates.
  The universal tape, precision and recovery premises remain external here.
- How close can this finite compiler approach the same raw crossing? First
  balance contraction reserve against the charged completion term and improve
  numerical enclosure precision if necessary. Every new choice needs fresh
  tails, capacity, finite threshold and outer-formula checks; it would still
  be a compiler refinement of the same native construction.
