# Packed Word RAM multiplication transfer

**Positive result:** a complete fixed multitape algorithm taking T(n) steps has a uniform bounded-word RAM implementation taking

    O((T(n)+n+m)/log(n+2) + (n+2)^(1/16) log(n+2))

operations, with explicitly packed binary input, output cap m, paid generated lookup tables, sufficient logarithmic word width and a fixed polynomial address envelope. Thus a supplied conditional integer-multiplication theorem T(n)=O(n(log n)^(1-kappa)) gives **O(n/(log n)^kappa)** RAM operations, including setup and IO. This is a genuine asymptotic improvement over the constant-overhead RAM backend in PR #4538.

**No improved TM kappa is claimed.** The exponent kappa is inherited from the supplied TM theorem; its assumptions are not discharged. The current selected value is 0.0023 (#4359). Pending #4535 claims 0.003020165 using #4532/#4470; its arithmetic audit #4536 is not a complete proof audit. Neither selected-result files nor their suppliers are changed. No best-known unconditional RAM record, practical speedup or historical priority is asserted.

## What changed and why it matters

The previous PR gave constant overhead per TM step and packed storage. This package tabulates Theta(log n) consecutive TM steps and applies each generated row to a constant number of packed words. Crucially, a second generated codec avoids losing that gain in a linear bit-per-word input/output scan. The full native multiplication algorithm can therefore be transferred as an entire fixed TM, rather than requiring every analytic or recursive component to be rewritten before any target-model time gain is available.

The target is the Problem 1.8 RamStd instruction semantics used in #4538: finite bounded words and addresses, zero-initialized memory, shared register/data semantics and successful-instruction cost. Algorithms use ADD, monus SUB, Boolean operations, shifts, loads/stores, branches and word IO. Word multiplication/division and exact complex-cell arithmetic are not used. The methods and proof are informal; the operational models are not complete emitted RamStd programs or Lean formalizations.

## Review and reproduce

Start with [PROOF.md](PROOF.md) for the complete construction, hypotheses, address proof and multiplication corollary. [PACKED-IO.md](PACKED-IO.md) proves binary expansion, reversed/capped output and padding. [TABULATED-MULTIPLY.md](TABULATED-MULTIPLY.md) provides a supplementary constructive word-MUL elimination lemma; the main simulation does not rely on it. [OVERLAP.md](OVERLAP.md) compares actual primary and project sources.

From the repository root, Python 3.12 and standard library only:

```sh
python3 scripts/research_package.py --package research/packed-ram-speedup --check-only
python3 scripts/research_package.py --package research/packed-ram-speedup
```

A Git-free extracted package can run `python3 -I -O -B verify.py`. The verifier authenticates the exact package inventory and every listed source before launching isolated optimized checks. The composed fixture also authenticates and directly compiles dependency source bytes, avoiding cached bytecode. No network, GitHub access, native compiler, GPU or Lean installation is required for the finite replays.

The generic `run_packed` entry point computes its epoch and polynomial origin from the declared total length, generates all tables anew, and composes the codecs with the TM simulation without any supplied runtime fuel. Its caller supplies a fixed machine and proves the stated polynomial envelope. The composed checker includes one fresh invocation of that generic runner.

The main model actually constructs every row of each finite test table and compares macro state, signed heads and every potentially affected tape cell against a separate literal TM interpreter. Controls include early/epoch-boundary halt, nonhalting prefixes, arbitrary dirty window neighbors, corrupted table rows and insufficient width. The codec checks partial chunks, leading zeros, blank termination, dirty post-terminator cells and seven actual decoder mutations. The composed positive fixture is one fixed 144-state machine multiplying all pairs of 2-bit integers through the entire packed codec/window/table/output chain. It is **not an all-length multiplier** or a claim that the huge frontier TM has been materialized.

## Frontier work and remaining scope

Three workers and the root also investigated changed native contact graphs, general Clifford frames, whole-prefix retiming and deferred helper compensation. No completely paid cheaper Fourier-rank profile was obtained. A faster free monomial wrapper or an entrance-only deletion with unaccounted prefix contacts cannot justify a larger TM kappa. These local attempts are not packaged as the research result: the positive complete-model transfer above is the result.

The implementation is a finite operational model with an informal universal proof, not a kernel certificate. Fully emitting and refining the parametric RamStd code remains a concrete implementation task. Literal primitive-operation counts in model reports are not exact emitted instruction counts. All standard fixed-loop/control lowering contributes only machine-dependent constants to the proved asymptotic bound. Tests ran on Windows with portable Python; Linux-hosted execution is not claimed.

## Open next questions

- **Emit the whole parametric backend.** Why: makes the complete all-length uniform RAM program executable against RamStd.step. First step: lower table generation and the two-word window merge to finite labels, preserving source hashes and the fixed polynomial origin. Blocker: current executable is the operational model, not a serialized full program.
- **Bind a published complete TM instance.** Why: turns the generic corollary into a fully source-bound application. First step: select either #4359's admitted conditional supplier or #4535's stronger pending supplier and carry its whole source/assumption manifest into the transfer. Blocker: their enormous algorithm-defined transition machine is not materialized here; finite arithmetic audits do not prove those antecedents.
- **Change an actually paid native profile.** Why: a better TM kappa requires a new productive/paid moment, beyond free-wrapper savings. First step: construct one exact all-input coupled-contact rewrite and serialize every owned transport and prefix observation before scoring it. Blocker: no such cheaper complete invoice was established in this session.
- **Measure crossover and practical memory.** Why: machine-dependent table constants can be enormous. First step: report table rows, setup, steady-state work and memory separately for a real bounded machine. Blocker: finite tiny fixtures do not predict a useful threshold for the theoretical multiplier.

## Credit

Prepared for Dugongue with substantial OpenAI Codex assistance and three parallel agents. The logarithmic simulation/tabulation method is classical: credit John Hopcroft, Wolfgang Paul and Leslie Valiant (1975), Section 4. Martin Fuerer's 2014 log-RAM model and linear-time multiplication results are model-comparison precedents, not displaced unconditional results. Preserve the existing Problem 1.8 RAM/IMP/compiler and tensor/frame source credits through #4538, and Szymon Torunczyk/GPT's compositional-polytime lineage.

The conditional multiplication antecedent retains the original OpenAI manuscript, Dillon's #4532, hexapode's #4535, Cinna Davis's #4470 and native/controller lineage, zxv's compiler and flow work, Jacob Alan Sussman's mixed-target recursion, Ryanson Jonathan's mirror/audit work, Dugongue's compact consumer/Word RAM work, and all physical, precision, prime, analytic and recovery contributors. PRs #647/#956 already construct exact-scalar RAM providers in their own models; this package does not relabel them as finite-word bit algorithms. Source-specific notices remain authoritative. New work is Apache-2.0; no independent human peer review is claimed.
