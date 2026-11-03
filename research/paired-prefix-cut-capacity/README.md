# One crossing paired scalar ADD changes cut capacity by at most one

This contribution was produced by Nick Petalas.

At a fixed dyadic helper cut, insert an elementary update immediately
before the cut and its inverse immediately after it. Keep both supports
and the complete dirty endpoint fixed. The exact unit-channel capacity
changes by at most one if the update crosses the cut's eligible coordinate
support. An update within either side preserves capacity exactly.

```text
T = I + a e_i e_j^t,  i != j,  nonzero a in Z[1/2]
A' = T A,  B' = B T^-1,  B'A' = BA

exactly one of i,j in F:   |capacity' - capacity| <= 1
both or neither in F:      capacity' = capacity
```

The bound is sharp. For every d, an explicit 2d-field identity word gains
exactly d unit channels using d crossing prefix-side edits and their d
matched suffix edits. The original word uses 2d scalar ADDs; the edited
word uses 4d and restores every arbitrary dirty field. No extra storage
is allocated. Reversing an edit attains a decrease of one as well.

Claim type: scoped written mathematical proof with exact finite
corroboration. No new kappa or selected-frontier change is claimed.
[PROOF.md](PROOF.md) proves the result over arbitrary finite dimensions.
It takes the changed-prefix opening in zxv's
[PR6064](https://github.com/CrocSwap/integer-mult-bounds/pull/6064).
That predecessor enlarges the cut support while keeping the program fixed;
this result keeps the supports fixed and changes the program.

## Evidence and reproduction

The new standalone checker imports no predecessor executable. It solves
full integer kernels in dimension at most three, localizes them at two,
and computes dyadic unit capacity by enumerating every minor gcd.
Normal and optimized warning-strict modes check:

- 12,928 paired edits on 80 prefix instances, with every nonempty proper
  cut/helper support in their two- and three-dimensional fixtures.
  There are 4,032 same-side and 8,896 crossing edits. The capacity deltas
  are -1 in 1,276 cases, zero in 11,625 and +1 in 27.
- All 52 determinant-one two-by-two matrices with entries in -2..2,
  plus the 28 explicitly generated three-coordinate prefix instances
  listed by `prefixes(3)`. Each edit uses coefficient -1/2 or +1/2.
- The sharp d=1,2,3,4 family, full module equations and unit witnesses,
  with literal scalar execution on all 7,380 declared signed dirty states.
- Six invalid ADD rejections and six algebraic controls, including odd
  nonunits, joint unit extraction, full kernel generation, a falsely
  zero-change bound and the wrong inverse sign.

From the worktree root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/paired-prefix-cut-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/paired-prefix-cut-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/paired-prefix-cut-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/paired-prefix-cut-capacity --check-source-history
```

Substitute another CPython 3.12 interpreter path elsewhere. Direct checks
write nothing and emit `PASS_PAIRED_PREFIX_CUT_CAPACITY` in a generated
JSON receipt bound to all six package files and both declared source files.
There is no hand-written receipt. The registered hook runs both direct
commands separately with 60-second limits.

## Scope and limitations

The update must be elementary in the physical coordinates of the nominated
cut. An update inserted earlier inside the prefix generally becomes a dense
conjugate there; the one-channel statement does not cover that case.
Matched inverse suffix edits, fixed helper/cut supports and the full dirty
endpoint are essential hypotheses. Capacity is the algebraic unit-block
capacity of the full saturated modules, not rational rank alone.

This changes `coverage-law-change` to a scalar algebraic side result. No
selected-word edit, common native chart, delivery, independent productive
Gaussian target, precision/growth, storage, ownership, compiler or complete
paid/target invoice is supplied. A scalar ADD is not a paid recursive child,
so this result supplies no kappa ceiling or supplier admission. All five
selected framework assumptions remain. Selected cold replay, Lean and Docker
were not run. Independent human and formal proof-kernel review are unclaimed.

The selected binding orientation passed at conditional kappa .003125804.
Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. [SOURCES.json](SOURCES.json) pins the two mathematical sources
and records selected/catalogue provenance. Existing source notices and bytes
are unchanged. Live PRs, latest handoffs, local reservations, current-main
object/formula searches, merged searches and recent account bodies were
checked. The initial cached local corpus was sparse; Git-tree searches and
materialized relevant sources supplemented it. Unpublished work and arbitrary
historical diffs remain outside coverage. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362888)
precedes the mathematical checks.

## Open next questions

1. What is the sharp capacity change for a dense conjugate of one earlier
   prefix update? First pin the transport to the cut and compute both full
   modules. The present elementary-update proof does not cover that change.
2. Can an actual native helper use a crossing paired update at a profitable
   complete signed invoice? First extract one legal cut and prove its charts,
   timing, dirty endpoints and delivery costs. Algebraic capacity supplies
   none of those missing productive-target obligations.

## Credit

Credit zxv / PR6064 for the changed-prefix question and support-enlargement
predecessor, and Ali Romman / PR5615 for saturated cut-pairing capacity,
PR5602/5611/5599 and their retained P104/helper/native/controller lineage.
The related PR6054 pure-product result and Nick Petalas's earlier tensor,
parallel-bank and fixed-reader results leave this paired-edit contract open.
PR6308 changes only the predecessor determinant evaluator's runtime.
No predecessor theorem or numerical result is an audit deliverable here.
Module splitting, coordinate kernels, minor ideals and Bezout identities
are classical; no literature-wide priority is claimed for them. New work
is Apache-2.0.

## Verifier constraints

All functions are shorter than sixty physical lines. There is no recursion,
dynamic code loading, subprocess or network call. Matrices have order at
most eight, full kernel/minor calculations have order at most three,
prefix constructor words have at most four updates, sharp identity words
have at most sixteen, and source/package reads have a one-MiB cap.
Euclid has a 64-bit input cap and 192-iteration budget.
Every loop ranges over these fixed finite domains. Explicit exceptions
keep acceptance checks enabled under optimization.

Power-of-ten rule 3 deviation: CPython allocates integers, Fractions and
containers during checking. The fixed fixture sizes bound live collections;
no static-allocation claim is made. Rule 9 uses ordinary fixed standard-library
iteration and local direct function calls. Warning-strict normal/optimized
replay and in-memory syntax compilation provide the local diagnostics;
no additional static analyzer or formal proof kernel is claimed.
