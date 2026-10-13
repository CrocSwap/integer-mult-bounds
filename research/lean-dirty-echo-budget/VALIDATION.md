# Executed validation

Local validation on Linux x86-64, 2026-10-13. Formal toolchain:
Lean 4.21.0, commit `6741444a63ee`, official Release binary. Python versions:
3.14.4 and 3.12.3. The official Linux archive was checked against its release
SHA256, `455c6df09d5bd54d2a51b137939c47e2dda816d512ac789c4b3642c9bf98bde8`.
Only core and bundled Std are imported. The toolchain is installed externally;
compiler/library binaries are not included in the patch.

## Formal and source checks

```sh
lean -DwarningAsError=true EchoBudget.lean
python3 -B -I verify.py --lean /path/to/lean-4.21.0/bin/lean
```

Both pass. The complete verifier compiles fresh temporary objects, treating
warnings as errors, with explicit recursion/heartbeat limits. It audits eight
public statements and the generated aggregates that reach all finite proofs.
The admitted transitive axioms are exactly drawn from `propext`,
`Classical.choice`, and `Quot.sound`; individual lists are in the receipt.
Every proof is kernel-checked. No native evaluation oracle or proof placeholder
is admitted.

Exact completed coverage:

| Evidence | Count |
|---|---:|
| Ordered trees, all arities, one through eight factors | 5,440 |
| Equality-band optimizer outputs, budgets 2..6 | 36 |
| Distinct constructor proofs including optimizer subtrees | 5,474 |
| Source forward/inverse words checked | 10,952 |
| Literal leaf instructions checked | 1,429,954 |
| Largest scratch footprint in this finite domain | 7 |
| Compiler rejection controls | 6 |
| Disallowed-axiom audit controls | 3 |

The deterministic generated Lean source has SHA256
`d0f2ad2b636e174d9773115765e52fd73e0b7dc76434643b81e2825579857497`.
Its profile-list SHA256 is
`65aeebdfc33e244cc636992a11c682c6e3a2d6878b5596a92b3055ee9cfafc3b`.
`--emit-cases /new/ModelCases.lean` exports the complete source for inspection.
Reproduction compares canonical JSON for every proof-relevant receipt field;
host paths, elapsed time, and binary-container hashes do not define equality.

## Portability and failure detection

The normal isolated Python 3.14.4 invocation reproduced `EXPECTED.json`.
A copy containing only this package, outside the Git checkout, in a path
containing spaces, passed under isolated Python 3.12.3. All copied package
files and directories were read-only, and every byte was unchanged afterward.
This second full run took about 110 seconds on the test host, including all
nine negative controls; it is a reproducibility observation, not a speed claim.

Additional package checks exercise rejection of:

- A modified pinned `schedule.py`, before importing it.
- A missing pinned `schedule.py`.
- A changed receipt replacing integer `1` with JSON `true`; strict canonical
  comparison rejects it even though Python's ordinary equality conflates them.
- An existing receipt output, preserving its bytes.
- An existing generated-case output, preserving its bytes.

Each compiler control starts from the accepted proof and changes one resource
obligation. Endpoint price 2→1, interior price 4→2, one omitted reserved array,
minimum 2304→2303, an equality band beyond capacity, and a wrong source-derived
profile all fail Lean compilation. Audit input containing `sorryAx`,
`Lean.ofReduceBool`, or a custom assumption is rejected. These are failure
controls, not new mathematical findings.

## Repository scope and publication boundary

`make selected-record-check` passed, retaining the selected exact
κ=`1661634653669567/10^18`. Whitespace and file-scope checks cover this package.
No producer, selected supplier, selected certificate, or `upstream/` source
is edited; global regenerating suites and selected-supplier cold replay are
outside this isolated formalization's validation claim.

The pre-submission queue refresh covered 678 open PRs through #886. Main
remained `f567884aeb8851b6e794af1184119a3bfbe1e631`; PR784 remained at the
consumed head. New #878 concerns selected XOR boundaries and #885 native Real
moments. Neither formalizes this reserved-scratch resource theorem. No pinned
coordination issue exists; the local claim records the result and final PR.

Hosted workflow status is a separate publication result, not part of this
local verification claim. The universal theorem is about `Fits`; the bridge
to Python is the stated finite evidence. There is no claim of formal operator
semantics, rounded accuracy, the whole Python optimizer, or the complete
integer-multiplication theorem.
