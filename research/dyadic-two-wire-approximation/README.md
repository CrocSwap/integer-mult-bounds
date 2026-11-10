# Sharp exact-dyadic approximation floor for two-wire butterflies

This contribution was produced by Nick Petalas. New material is Apache-2.0.
Claim type: scoped written mathematical proof with exact finite corroboration.
No new kappa or supplier admission is claimed.

For every real 2 by 2 orthogonal matrix U, let m=max |U_ij|. The exact best
Gaussian-dyadic unitary approximation satisfies

    min_{V in U_2(Z[i,1/2])} ||V-U||_op^2 = 2(1-m).

A real signed permutation attains it. Any finite number of arbitrary dirty
helpers, returned exactly for every input, leaves this minimum unchanged.
The worst floor over real orthogonal targets is 2-sqrt(2), at a balanced
butterfly. The rational butterfly [[3/5,4/5],[4/5,-3/5]] already has sharp
squared error 2/5, regardless of requested precision or circuit length.
[PROOF.md](PROOF.md) supplies the all-real and arbitrary-helper arguments.

## The changed arithmetic interface

Jose Manuel's [PR4205](https://github.com/CrocSwap/integer-mult-bounds/pull/4205),
retained head `78c72e563173f3822fcb4efed9ceeccf05630258`, supplies exactly
unitary rational FFT coefficient gates and stored adjoint inverses. Its
real-phase butterfly family is the motivation for a self-posed question:
can exact Gaussian-dyadic unitaries remove those rational denominators at
the same restored two-coordinate boundary? The formula excludes an
arbitrarily accurate replacement of a nontrivial real butterfly in that
model. The predecessor's rational construction is a cited premise, not an
audit target, and is unchanged.

This is an arithmetic-interface side result under a changed
`joint-query-controller` card. It does not give a complete supplier invoice
or resolve the selected compiler/precision obligations. Nonunitary lifting,
rounded arithmetic and larger active joint boundaries remain possible.
The nonunitary dyadic matrix (5I+6J)/8, J=[[0,-1],[1,0]], is at squared
distance only 1/320 from (3I+4J)/5, but has norm square 61/64. Thus exact
unitarity is a substantive premise.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dyadic-two-wire-approximation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/dyadic-two-wire-approximation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-two-wire-approximation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-two-wire-approximation --check-source-history
```

Any CPython 3.12 path can replace the absolute interpreter path. Direct
replay prints `PASS_DYADIC_TWO_WIRE_APPROXIMATION` in a JSON receipt whose
hashes bind all six package files and the complete mathematical transcript.
It writes no files and imports no predecessor implementation. Both
warning-strict normal and optimized commands are registered in VERIFY.json.

The checker independently joins all possible first and second columns and
compares that join with the perpendicular-column construction. It then
compares every resulting unitary with every declared rational rotation and
reflection using exact integer Hermitian principal minors. There are no
floating-point eigenvalues. The target family uses p=-12..12, q=1..12 in
the rational circle parametrization, with repetitions removed, plus the
missing limiting point. The resulting 368 targets give 35,328 exact
target/unitary comparisons. The emitted receipt also reports the control
counts and a hash of the full sorted transcript.

One-helper controls exhaust the 96 unitary active blocks paired with each
of 24 nonzero possible unit-vector leakage columns. Every such leakage
fails exact unitarity, while each direct-sum identity helper passes. Six
other rejection controls cover a changed sharp threshold in both
directions, an empty candidate list, a nonpositive denominator, a
rectangular matrix and a nonunitary imaginary perturbation. The closer
nonunitary dyadic control verifies the importance of the hypothesis.

## Scope and credit

The finite group of 96 two-dimensional Gaussian-dyadic unitaries is
classical. Credit Alexis De Vos, Raphael Van Laer and Steven Vandenbrande,
[The Group of Dyadic Unitary Matrices, 2012, section 5](https://backoffice.biblio.ugent.be/download/2069554/2069555).
The new claim is the sharp distance formula and its restored-helper
interface consequence, with no worldwide literature-priority claim.

Credit Jose Manuel / jmbarrancoml for PR4205's rational-unitary child;
Vlado Vojdanovski for the retained FFT and Toeplitz schedules; Chafik
Boukhalfa for rational unit-phase construction; Mason Hale for the retained
interval arithmetic; Jeremy Kothe / IdeaOuter and Cinna Davis for the
credited Gaussian/caller lineage. Predecessor files and credit are unchanged.
MatShep's PR5549 studies tensor faithfulness of the same 96-element group;
this package does not repeat its tensor-rank result or scientific replay.

The scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. SOURCES.json pins the motivating source documents as provenance.
No source scientific checker is run. Live open/account PRs, active
Discussions, local reservations and main/merged searches for the object,
general dyadic-unitary form and formula preceded the
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373396).
The overlap helper was also run; its coverage and freshness are recorded
in the PR body. Sparse notes and bounded searches do not establish absence
of unpublished overlap. The selected result and all five framework assumptions remain.

This excludes only a linear, exactly unitary, Gaussian-dyadic replacement
at a restored two-active-coordinate boundary. It excludes no global FFT
approximation, large native operator, nonunitary lifting method or changed
helper-return contract. Exact coefficient unitarity and rounded data
restoration are separate claims. Physical coefficient delivery, tapes,
precision, stock, compilation and complete multiplication remain unproved.
Selected cold replay, Lean, Docker, independent human and formal
proof-kernel review are unrun or unclaimed.

## Open next questions

Can a nonunitary dyadic lifting replacement of one rational butterfly meet
its full composed error/restoration budget with a cheaper complete
coefficient-delivery bill? Start with the pinned PR4205 butterfly, an exact
dyadic shear factorization, explicit rounding sites and inverse, and bound
its intermediate norms. Stability, fixed-grid restoration and a favorable
physical invoice are missing. This result does not reserve that follow-up.
The structured question is in TASK.json.

## Implementation bounds

The fixed checker uses no recursion, external process, network access,
dynamic import or mutable global state. The target generator has at most
602 outputs; each has exactly 96 candidates. Matrix dimensions are at most
three. Integer target denominators are at most 288. The transcript has at
most 602 records. Package hashing reads six files, each capped at 1 MB.
Every function is shorter than 60 lines and executable contracts remain
enabled under optimized Python.

Power of Ten rule 3 has a managed-runtime deviation: Python integers,
tuples, sets and JSON allocate during execution inside the fixed finite
bounds above. Interpreter/library allocation is not statically controlled
or measured. Rule 9's rejection-test helper dispatches only to the two
named local check functions; its finite targets and call sites are explicit.
Warning-strict normal/optimized replay is the Python diagnostic check.
