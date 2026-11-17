# The autonomous row forces a unique two-edge feedback pair

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
For the unchanged saved-bank interface of
[unpaidmoon's #6961](https://github.com/CrocSwap/integer-mult-bounds/pull/6961),
the only two feedback operators attaining its autonomous four-input row are
`F1=Q` and `F2=C1 Q`. Both operators may vary arbitrarily in the predecessor's
algebra. The known pair itself is credited to #6961. The new result is its
uniqueness, which the predecessor explicitly left unproved.

The sum of the first and third output columns eliminates F1 and forces F2.
The zero second column then forces F1. [PROOF.md](PROOF.md) proves the result
over every associative unital ring with the declared units and commutation
relation. It uses no search bound or faithful representation assumption.
Any quotient preserving those interface equations has the same unique pair
of operator values. This closes further two-edge tuning within that interface.

No new κ, complete caller, native construction, physical tariff or selected
frontier change is claimed. The row still contains two input jobs in one bank.
The existing pair's separate ordinary bill and final-bank question belong to
[#7077](https://github.com/CrocSwap/integer-mult-bounds/pull/7077); they are cited,
not reverified. New saved sources, different insertion points and different
decoder or target contracts remain outside this theorem.

## Reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-edge-feedback-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-edge-feedback-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-edge-feedback-rigidity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-edge-feedback-rigidity --check-source-history
```

CPython 3.12 and its standard library suffice. The direct verifier is also
Git-free and reads only the six authored files in this directory. It prints
`PASS_TWO_EDGE_FEEDBACK_RIGIDITY`, exact enumerated coverage and source hashes.
Add `--receipt /absolute/new/path.json` to save that generated receipt outside
the package. It refuses to overwrite an existing file. Default replay writes
no artifacts. The registered normal and optimized checks have 120-second
timeouts. Provenance validation uses full Git history separately.

The matrix census checks 97,090 operator pairs on 75 fixtures, with exactly
one solution per fixture. These include all 72 binary unit triples satisfying
the reduced hypotheses, two specified ternary triples and one Z/4 triple.
It includes singular candidate feedback operators. The independent scalar
evaluator checks all 78,658 inputs of the latter three fixtures. Three semantic
controls and six invalid-fixture controls also pass. The finite fixtures
corroborate the new abstract theorem; they do not replay the predecessor's
physical word or certify its native premises.

## Open next questions

- Can a different chronological saved source replace one of these edges with
  a favorable complete bill? Start by changing one of K or L and deriving its
  four independent input columns. The unchanged pair is rigid; source
  availability, full endpoint restoration and physical costs remain blockers.
- Can a consumer use the unique row without separately decoding its two jobs?
  Start with an explicit producer/consumer boundary and include the complete
  ordinary and recursive invoice. No such consumer is supplied here.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit and limits

Credit unpaidmoon #6961 for the one-edge obstructions, the saved-bank identities
and the attaining pair; Cinna Davis #5220 for the active schedule and operator
algebra; Dugongue / David Ganz #4948 and Dillon #4933 for the retained chronology
and normalizers; Chris R / Clear1nsight for passive-caller packaging; and their
retained native, compiler and precision lineage. The new simultaneous
classification, abstract proof and reduced-interface verifier were produced by
Nick Petalas. Apache-2.0.

The original `joint-query-controller` card has changed scope to a local
classification at a fixed interface. It supplies no favorable full caller bill.
`SOURCES.json` pins predecessor documents as provenance only. No predecessor
scientific code, selected cold replay, native, Lean or Docker suite is run.
All five selected assumptions remain. Independent human and formal proof-kernel
review are unclaimed. CPython's bounded dynamic-allocation deviation is recorded
in PROOF.md.
