# Validation receipt

Executed 2026-10-14 on macOS 26.5.2, arm64. Scientific base is
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
The exact mathematical receipt SHA256 is
`c7aac8d4478afa4848b30fb3be8cc44701b729c5d4e3bbb14f0ca93da4d87341`.

## Completed checks

1. CPython 3.12.15 registered replay passed:

       python3.12 -B scripts/research_package.py --package research/unipotent-return-seed53

   This authenticates the originating card and historical source pins, then
   runs every mathematical check described in README.md. Output ends with
   `PASS_UNIPOTENT_RETURN ... total=2494->2234 ... controls=8 no_new_kappa`
   and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.

2. Standalone copies in paths containing spaces, with package files read-only,
   passed from `/tmp` on CPython 3.11.15 and 3.14.8:

       python3 -I -O -B /absolute/path/to/package/verify.py

   No Git checkout or predecessor executable was present in those copies.
   Optimized execution retains all verifier checks; it does not rely on assert.

3. Nine real file corruptions in disposable package copies were rejected on
   CPython 3.12.15 in isolated optimized mode. These changed the saved total,
   predecessor bytes, source SHA256 key, source Git-blob pin, child drift,
   SCALE invoice, output alignment, literal echo inverse, and terminal return
   sign. Each run had a nonzero exit and the expected pin, endpoint, invoice,
   or saved-receipt diagnostic. These supplementary controls were local tests,
   separate from the eight mathematical controls in the registered replay.

4. Selected-result bindings passed without a cold supplier replay:

       python3 -B scripts/research_baseline.py

   It reported `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, selected PR1094,
   complex binding, and the unchanged selected-record SHA256
   `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

5. All 25 existing selected-result tests passed:

       python3 -B -m unittest discover -s tests -p '*selected*'

6. Both new Python files parse with Python 3.10 grammar; all JSON parses.
   Full literal programs, word hashes and canonical RESULT.json agree across
   the tested runtimes. The registered check is repeatable and does not write
   generated artifacts into the repository.

7. Staged whitespace checks pass, and every added file is under this package.
   Refreshed origin/main still equals the research base. The final overlap
   snapshot covers 773 open PRs and 199 discussion records with complete
   pagination at 02:21:01 / 02:21:47 UTC, plus local notes and the review ledger.
   It found no matching infinite-order return claim. A direct latest-PR check
   through PR1532 additionally inspected PR1526/1522/1532; their different
   paid-scaling, BIT-source-tour and nonlinear-reader scopes are credited.
   PR1287's live head still matches its pinned source exactly.

The first attempted nonintertwiner control changed child zero, whose phase is
zero and therefore did not fail. The verifier caught that vacuous control. The
committed control changes child one at a nonzero phase and is rejected. This
was a control-fixture repair, not a changed construction or acceptance rule.

## Scope of verification

The written proofs cover exact power lowering, the declared all-k unit-power
obstruction, the equivariant canonical group and recursive dirty-state identity.
Finite replay is separate evidence, not proof-assistant formalization. The
saved prefix row and scalar sign witness attest each forward growth maximum.
All coordinates, including arbitrary dirty scratch, are included in the maps.

The 260-instruction saving is at equal ADD/SCALE prices and a common adequate
width. It does not establish a bit-operation or wall-clock saving. The nested
word increases address travel despite using fewer instructions, which is
preserved in RESULT.json. Its width also increases.

Not run: Linux/hosted CI, a full selected cold replay, Lean, native supplier
admission, physical routing or tape implementation, a rounded precision
contract, or independent human review. No all-size/compiler, common-label,
hosting or analytic transfer obligation is discharged. No selected supplier
implements the fixed child assumed by this package.
