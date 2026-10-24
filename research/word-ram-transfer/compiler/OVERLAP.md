# Provenance and overlap for the finite compiler

This simulation is classical. Its useful local contribution is an actual
finite-program construction against the existing Problem 1.8 `RamStd` semantics,
a complete logarithmic-word sufficient theorem with signed head positions and
no supplied time horizon, and an executable semantic comparison. It claims no
new multiplication exponent or first-ever RAM realization.

## Existing local proofs reused as precedents

The target machine is the house standard `RamStd20261007.lean`, built on the
Problem 1.8 `Lax13.Ram` definitions. It has shared register/data memory, modular
addresses and values, and natural monus subtraction. We inspected source bytes;
we have not freshly checked those files or this new compiler in Lean. Exact
source hashes are in `SOURCES.json`.

`Problem18StructuredTMCompiler20260930.lean` explicitly retains Szymon Torunczyk
and GPT's compositional-polytime proof implementation at
`7fadbfd005b359a66ccc1165b2d1becddb2906b8`, Apache-2.0. It treats finite local
operations, finite-control loops and actual contract implementations; a mere
iteration bound is not an implementation. Our theorem follows the same
principle by emitting actual finite target instructions, rather than placing
a whole TM step inside one unexplained unit-cost operation.

`Problem18TM2OperationalBridge20260930.lean` has exact deterministic terminal-run
transfer lemmas (`deterministic_reaches_terminal`, `deterministic_outputs`). Its
scope distinguishes terminal semantics from arbitrary totalized iteration. Our
compiler analogously reaches an actual `halt`, rather than just stabilizing
under a totalized transition. We do not import that module or assert its theorem
instantiates this separate compiler automatically.

`MultitapeFrameRule20261014.lean` supplies bounded-footprint lockstep and terminal
preservation principles (`step_lockstep`, `FootprintedRuns.completed_lockstep`,
`completed_runs_finite_frame`). They support the finite-envelope invariant used
here: only visited and requested output cells need representation; no injection
of all integers into finite-word memory is asserted. Again this is a conceptual
reuse of source-inspected proved statements, not a new kernel derivation.

## Public exact-RAM work already exists

We fetched and inspected the following actual proof files at pinned public heads,
not just their PR titles. Digests are in `SOURCES.json`.

- [PR #956 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/fa4df77c9dfdbac93368d95dcb361e69b3b65464/research/pr390-heterogeneous-provider-closure/PROOF.md),
  especially its model section and Section 5, already gives constructive native
  Gaussian/Walsh realization and charged recurrence in an exact scalar/index
  RAM. Its scalar heights are explicitly unrestricted. This is stronger than
  a pseudocode-only provider in its declared model, but not a bounded-word bit
  RAM multiplication theorem. Credit Dugongue's PR #390 and retained lineage,
  Jacob Sussman's frame/bank/RAM/Fourier formalizations and P193 supplier,
  PR #363/#373/#375/#377/#381/#397 bridge work, PR #401 normalization and
  PR #430's interface audit, together with the OpenAI/math transfer sources.
- [PR #647 provider proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3b3fda9c602fbe4b45d02d1ead0b757b3c94f52c/research/e8-paid-copy-ram-20261013/PROVIDER-PROOF.md),
  especially Section 10, already constructs uniform exact-arithmetic RAM
  programs, charges address maps and tables, and proves recursive private
  workspace separation. It uses exact complex cells and explicitly leaves
  finite-alphabet/bit multiplication outside the model. Its companion cyclic
  corollary uses separately credited transfer machinery; the provider proof's
  earlier scope paragraph must not be used to deny that companion result.
  Preserve its Pro provider attribution, Sussman/P193 and E8 antecedents,
  dirty-response and bridge contributors, imported OpenAI compiler sources,
  and substantial OpenAI Pro/Codex assistance.

These packages address native scalar realization. The present compiler instead
starts from a fixed finite-alphabet multitape machine and preserves its bit
execution at bounded logarithmic word width. The approaches are complementary.
We do not silently turn their exact-complex primitives into constant-time
bounded-word operations, and do not claim those prior packages are erroneous
merely because they intentionally use a different model.

## Frontier provenance

Canonical main was refreshed and pinned at
`f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`. Its selected record still identifies
conditional kappa 23/10000 from PR #4359; merged PR #4470 gives a stronger
conditional claim 0.00302015 with joint helper boundaries. At this inspection
PR #4535 newly claims 0.003020165 through critical-root transfer. This package
neither adjudicates that pending claim nor changes any selected-result pointer.
Its transfer corollary quantifies over every complete conditional fixed-machine
multiplication theorem, so no numerical frontier assertion is required.

For every application, preserve the full pinned antecedent's source manifest
and author notices, including native/controller work by zxv, Jacob Alan Sussman's
mixed-target recursion, Cinna Davis's query/helper improvements and all retained
physical, precision, prime, tape and outer-analysis suppliers. Passing our finite
compiler checks does not independently validate any of those upstream claims.

Prepared by Dugongue with substantial OpenAI Codex assistance. New material is
Apache-2.0. No independent human peer review or Lean certification is claimed.
