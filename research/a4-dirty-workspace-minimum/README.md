# The A4 eight-call floor survives arbitrary dirty workspace

For every finite `r>=4`, the formal endpoint
`diag([a],[b],[aba^-1b^-1],[ab],1,...,1)` over `F2[A4]` has exact paid-call
minimum **eight**, with arbitrary restored dirty roles, rank-one idempotent
couplings, positive a/b calls and free binary scalar mixing.

The new result is a **scoped written workspace-compression proof** with
finite exact corroboration. Any hypothetical six-call word compresses to
the original four target roles. The minimum-eight corollary uses Cinna
Davis's [#2116](https://github.com/CrocSwap/integer-mult-bounds/pull/2116)
finite four-role exclusion and Sagar Thakrar's
[#4032](https://github.com/CrocSwap/integer-mult-bounds/pull/4032) all-role
radical-rank and determinant bounds as cited premises. Their searches and
proof checks are not replayed or audited here. This does not replace the
finite six-call exclusion with a wholly written proof.

No new kappa, selected-frontier change or physical supplier is claimed.

## The new step

[PROOF.md](PROOF.md) gives the model and full argument. At six calls, both
letters must attain their inherited rank-three floors. The augmentation
of every semisimple suffix is identity, so equality forces each b-call's
original binary output column into coordinates 2,3,4, and each a-call's
column into coordinates 1,3,4. Every factor consequently has the form

```text
[ four-role paid factor    arbitrary dirty-input reads ]
[          0                         I                ].
```

Restricting to the first four roles preserves the nonzero rank-one
idempotent contract and commutes with multiplication. The restricted
six-call word would realize the four-role target excluded by #2116/#4032.
Their all-role lower bounds already exclude every other length below eight.
The inherited direct eight-call word extends by identity on extra roles.

This answers the restored-workspace gap in #4032's scope. A coefficient
search on more roles cannot rescue a six-call word for this endpoint.
The rank-saturation step is essential: the checker includes four nonzero
rank-one summands of a rank-three target whose dirty output columns cancel.
Thus a version of the argument with slack in the call count would fail.

## Evidence and reproduction

From the repository root, use standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a4-dirty-workspace-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/a4-dirty-workspace-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a4-dirty-workspace-minimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a4-dirty-workspace-minimum --check-source-history
```

Any installed CPython 3.12 may replace that interpreter path. The standalone
verifier also works in a Git-free export. Expected markers are
`PASS_A4_DIRTY_WORKSPACE_MINIMUM` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Normal and optimized replay run the same explicit checks.

The checker enumerates all 29,791 ordered triples of nonzero binary columns
in five dimensions. Of these, 26,040 are independent. For each independent
triple and both diagonal support patterns, F4 augmented-matrix elimination
agrees with a separate oracle enumerating the binary column span. Exactly
336 triple/support pairs are compatible, and every compatible triple lies
in the required coordinate support. These are new rank-saturation fixtures,
not a census of predecessor words.

The literal A4 regular action checks all 3,600 admitted single factors whose
output columns lie in the first four coordinates, across role counts 4..7.
An additional 256 deterministic words have lengths 2..8. The resulting
3,856 word fixtures check 287,616 complete role/address basis columns,
including every extra-role input column. Their lower blocks are identity
and their upper-left blocks equal the products of the restricted factors.
Dirty inputs may feed target outputs; no clean-input assumption is made.
The direct eight-call upper bound checks a further 264 basis columns at
role counts 4..7. Seven malformed field/coupling inputs reject, and the
rank-slack counterexample passes as a boundary control. A separate positive
fixture requires an extra dirty input to contribute to a target output.
Field arithmetic
also checks the defining polynomial, associativity and distributivity.

Each run generates a receipt binding all six package files by SHA256 and
prints it to stdout. `--emit` prints only that generated receipt. There is
no handwritten or frozen receipt and no default filesystem output. The
finite tests corroborate the new linear-algebra implication; universal
coverage comes from the written proof. Hosted replay and scientific
acceptance are separate from these checks.

## Scope, sources and costs

The scientific base is canonical main
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
[SOURCES.json](SOURCES.json) pins the predecessor READMEs and #2116's
RESULT.json as historical mathematical premises. They are not runtime
inputs. No predecessor executable, generated search output or numerical
count is imported by this verifier. Frozen predecessor files stay intact.

[TASK.json](TASK.json) records a changed `bit-new-register-model` scope.
This is a formal-model side result rather than a new native alphabet.
The card's current first-step substitute, `research_selected_baseline.py`,
passed its source-binding orientation check. That is not evidence for this
theorem. The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145499)
precedes the proof and finite corroboration. Entry overlap coverage includes
live PRs, recent handoffs, active Discussions, merged A4/workspace searches
and all-main README terms. Sparse cached local coverage and unpublished
work remain limitations; search absence is not a novelty certificate.

Every role in this formal contract has arbitrary data and must satisfy the
full endpoint. There are no extra preparation or restoration calls in the
coordinate upper bound. Native implementation, frames, ownership, routing,
hosting, precision/tape, stock, recursive child ranks, compiler and outer
admission remain unpriced and unproved. Unknown costs are not zero.
No physical expansion round is proposed. Nilpotent couplings, other fields,
other targets or alphabets are outside the theorem. Lean, Docker, selected
cold replay and independent human or proof-kernel review are unrun.

## Engineering constraints

Build the Lever supplies a rerunnable exact checker. Prove It Works requires
full literal operator columns for restriction, including dirty inputs.
Power of Ten bounds all code loops by fixed domains, at most seven roles,
eight factors, 84 regular coordinates and matrices of shape at most 8 by 8.
Every function is below 60 physical lines. Acceptance uses explicit
exceptions that remain active under optimization. There is no recursion,
subprocess, dynamic import, shared mutable state or runtime code generation.
Managed Python allocation is a bounded rule-3 deviation; allocator internals
are not inspected. Each local file read is capped at 128 KiB. Warning-strict
normal and optimized registered checks provide recurring diagnostics.

## Open next questions

Can the original four-role six-call exclusion be replaced by a wholly written
contradiction? This would remove the finite-certificate dependency from the
all-workspace theorem. Start with compatibility of the two tight rank-three
decompositions on the four target coordinates, or their second radical-layer
coefficients. The missing compatibility argument is the blocker. This package
does not reserve that question. Its structured form is in TASK.json.

## Credit

This contribution is produced by Nick Petalas. Sagar Thakrar #4032 supplies
the radical-rank identities, all-role floors and determinant congruence.
Cinna Davis #2116 supplies the alphabet, endpoint, coordinate word and
finite four-role exclusion. Retain Cinna Davis #2047/#2248/#2085,
juper997 #1478, woklerx #1443, Gareth Davidson #1333, commdata2338 #1414,
eumemic #288, Ali Romman #468 and the retained register-model lineage.
The new step is tight-rank workspace compression, not the predecessor
four-role optimum. The underlying rank and restriction facts are classical.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
