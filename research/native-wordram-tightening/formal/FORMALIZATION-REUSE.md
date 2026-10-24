# Exact reusable formal interfaces and their evidence

This is discovery and source inspection, not a fresh Lean compilation or axiom audit. The active canonical modules and DAG are unchanged. The source hashes in PUBLIC-SOURCE-PINS.json identify the inspected bytes; new proofs in this directory are informal.

## 1. Direct bounded IMP-to-native Word RAM compilation

Source: Mathproof/Meta/Problem18RAMLax13ProofsSimulation20261001.lean.

Theorem `Lax13Proofs.Simulation.compile_correct` at line 544 takes a bounded terminating semantic run `BigStepB B c sigma sigma' k`, `Com.Ok L c`, input boundedness, a machine state representing sigma, code at its actual program counter, and `L.FitsWords B w`. It yields a run of the literal native compiled code, the representing final state, the next program counter, and an instruction count at most `L.const*k`. The caller can supply an arbitrary represented initial environment; this is the appropriate local contract for arbitrary dirty helpers. The whole-program `compileProgram_runsTo` at line 896 also establishes genuine halt and tape output from clean machine initialization.

`Layout.FitsWords`, in Problem18RAMLax13ProofsCompile20261001.lean at line 107, requires `1 < B`, `B <= 2^w`, and `L.span B <= 2^w`. Here `L.span B = temps+2+scalar_count+array_count*B`. For array index i and array a, physical address is `temps+2+scalar_count+idxOf(a)+array_count*i`; `arrAddr_inj` proves disjointness. This is a fixed strided ABI, not a promise that all array metadata allocation is free.

Important limitation: the convenience wrapper `Problem18IMPUniformCompiler20261001.compileProgram_runs_polynomial` is a polynomial-time computability theorem. Its word-width lower bound adds total input bitSize and a polynomial in bitSize. It must not be used as evidence of standard logarithmic word width. For the native multiplication application, prove FitsWords directly at the actual word width using the lower-level theorem. No RAM-to-Turing compilation is needed.

## 2. Framed scalar and field macros

Source: Mathproof/Meta/Problem18Claude/Problem18ClaudeFieldMacros20261001.lean.

`MacroInput` requires valid register names, encoded field degree and prime, arithmetic and inversion word bounds, actual input/output slice fits, output disjoint from input and modulus slices, and canonical coordinates. `BinarySpec` quantifies over every B and initial environment satisfying these obligations, then gives an actual Run, the exact decoded output, canonical output and `MacroFrame`. `MacroFrame` preserves all unrelated scalar variables, unrelated arrays, memory outside the output slice, array lengths, and input/output tapes. Its `BinarySpec.call` theorem additionally charges argument installation: `3 + a.size + b.size + o.size + cost`.

This is a reusable compositional ownership discipline. It supports a real caller-state proof instead of assuming clean helpers, and distinguishes output from scratch. The instantiated finite-field macros should not be treated as native complex arithmetic without a representation and ring-homomorphism proof; they are precedents for the contract, not magic Gaussian operations.

## 3. Cross-machine bridge as a model audit precedent

Source: Mathproof/LibraryBridges/Claude/ThreeSumRamSimulation_20261007.lean.

The existing bridge compiles the 3SUM/APSP EndStatement RAM to Lax13 and gives an explicit bound `12 + 12*input_length + 35*t`. It uses one extra word bit and an arena offset, and states `CellsFit` for literal cell names. Its separate `sim` theorem exposes the final memory. This is concrete precedent that model conversion can have a real address-bit and I/O charge, which must be kept when claiming a transferred exponent. It is not a theorem that any RAM model or arbitrary word width automatically preserves every asymptotic claim.

## 4. Public formal packing sources inspected

- Jan Dreier and Claude Fable 5: Lax13 Word RAM and verified compiler pipeline. Current successor source: https://github.com/lax-archive/lax-submissions/tree/9394e531cc51cb67a0214bca3f9264dfe97ba5c7/word-ram . The archive landing page https://laxarchive.org/lax-13/index.html explicitly distinguishes machine definitions from downstream proof obligations. Its old v4.30.0 environment is superseded by v4.33.0; do not silently mix imports.
- `Hex.ZPoly.natAbs_mulCoeff_le_min` in https://github.com/leanprover/hex-poly-z/blob/main/HexPolyZ/Kronecker.lean at lines 188-195 proves the asymmetric coefficient bound `abs(coeff_n(p*q)) <= min(p.size,q.size)*A*C`. The current source already contains it, although SPEC prose describes a related refinement as unspent. It is therefore not a new result of this session. `kronecker_identity` at line 551 proves signed recovery under an explicit coefficient budget; `mulKroneckerAt_eq` at line 664 and `mulKronecker_eq` at line 724 discharge runtime branch/width choices. This is algebraic correctness, not a native w-bit instruction-cost proof.
- https://github.com/teorth/sendov/blob/master/Sendov/FiniteRange/Pack.lean: `unpackN_pow` at line 163, `unpackZ_pevZ` at line 227. These are direct polynomial-digit recovery precedents; their large-Nat performance does not establish one-word packing or an asymptotic integer multiplier.
- https://github.com/anthropics/formal-math/blob/main/3sum-apsp/docs/MACHINE.md describes a separate native RAM compiler and polynomial-limit word-size slopes. The exact generous model assumptions in that guide remain part of its claims.

The retrieved external Lean files are retained privately as discovery snapshots with original notices; they are not dependencies of the new informal lemmas. No external theorem has been independently rebuilt in this session. No exhaustive negative novelty claim is made: bounded web searches and registered lexical queries can identify mechanisms, but cannot prove nobody has applied them.

## Reproducible evidence in this directory

`check_lanes.py` passes 195102 exact finite identities using modular word arithmetic, natural-number monus and exact integer division, including odd divisors. `check_relocation.py` checks 1200 seeded native programs: 20593 step-or-halt correspondences, including 19696 completed source steps, with arbitrary dirty exterior preserved. Both run successfully with `python -I -O -B`; their checks use explicit exceptions and remain active under optimization. These are regression controls, not proofs of the universal lemmas, whose informal proofs are written separately.
