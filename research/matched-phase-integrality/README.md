# Matched phase-query floors of 140 and 556

This contribution was produced by Nick Petalas.

A Fourier integrality argument raises Jose Manuel's
[PR2070](https://github.com/CrocSwap/integer-mult-bounds/pull/2070)
commuting-phase lower bound from 139 to **140** single-array phase events
for one matched P112 bank, and from 555 to **556** for four independent
banks. Shared role-linear processing, COPY/CLEAR and private workspace
remain permitted under the predecessor's contract.

Claim type: scoped mathematical proof with exact finite corroboration.
The bounds are not claimed optimal. There is no new kappa, physical supplier
or selected-frontier change. This is a terminal-interface side result on
the centre-path-sharing card, rather than a completed current-caller change.

The new lemma says that an odd multiset of k nonzero binary polars with
at most (k+1)/2 active events in every character must consist of all nonzero
elements of a subspace, each once. Thus k+1 must be a power of two.
PR2070's cited rank inequality forces exactly this threshold at k=139 and
k=555; neither 140 nor 556 is a power of two. Read [PROOF.md](PROOF.md).

The predecessor's causal inequality, common Pauli-trivial character sector,
P112 span dimensions and defect-rank bound are mathematical premises.
They are not new results here, and no predecessor scientific executable
is imported, audited or replayed. [SOURCES.json](SOURCES.json) pins its
README as historical provenance at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/matched-phase-integrality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/matched-phase-integrality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/matched-phase-integrality
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/matched-phase-integrality --check-source-history
```

Elsewhere substitute a local CPython 3.12 path. The direct marker is
`PASS_MATCHED_PHASE_INTEGRALITY`. Direct runs generate a deterministic
receipt on stdout, bound to the SHA256 of all six package files. They write
no files. No hand-written receipt is committed.

The checker exhausts every odd-size nonzero-polar multiset of sizes 1 through
9 in dimensions 1 through 3, and sizes 1 through 5 in dimension 4. It checks
19,727 multisets, including repetitions. Exactly 70 satisfy the character
threshold; each is a subspace with zero omitted. Direct character evaluation
and a separate butterfly transform agree. Fourier inversion, exact multiset
counts and Gaussian-binomial subspace counts also agree. Thirteen invalid
domains are rejected. Five semantic control groups cover two simplex sizes,
repeated polars, the essential zero-polar exclusion and the exact threshold.
Normal and optimized modes keep all checks active.

These finite cases support the new lemma. They do not enumerate circuits
with 139 or 555 events, prove the predecessor premises, or replace the
all-dimension written argument.

## Limits

The proof requires fixed role-linear programs, nonzero commuting phase
polars and the complete common-character family. Noncommuting payload
adapters, nonlinear or data-dependent programs, changed endpoints and
new multirole child interfaces require other arguments. This package does
not strengthen the normalized nonuniform coherent-cover bound.

The selected record at the pinned base is PR6030, conditional
kappa 0.003125804. Its five framework assumptions remain. Native realization,
physical tariffs, routing, ownership/erasure, restoration implementation,
precision/tape, stock, compiler closure and complete supplier/outer bills
are unprovided. The selected scientific cold replay, Lean and Docker are
unrun. Independent human and formal proof-kernel review are unclaimed.

The checker has no recursion or subprocesses. Every enumerated domain has
an explicit bound. New functions are below 60 physical lines. Managed Python
allocation is a Power-of-Ten rule-3 deviation; live mathematical arrays have
at most 16 entries and each multiset has at most 9 entries. The 18 summary
rows and fixed package-file hashes are bounded. It does not claim a fixed
allocation runtime. Warnings are errors in both registered commands.

## Open next questions

- Can the 140-event or 556-event floor be attained in the exact matched
  alphabet? An explicit polar multiset satisfying the necessary per-character
  inequalities is a first step. It still needs a causal role-linear
  realization and complete endpoint proof. No such construction is supplied.
- Can one priced noncommuting payload adapter change the matched endpoint's
  complete cost? Start with its explicit tensor-valid action between two
  phase events. This is the predecessor's retained opening; the common
  character decomposition and a physical price are the blockers.

[TASK.json](TASK.json) records these questions, the scope change, live overlap
coverage and the advance claim.

## Credit

Jose Manuel / jmbarrancoml supplies PR2070's causal, character and P112
endpoint results. Credit eumemic / PR288 and Ali Romman / PR468 for the
compact-WY, image/row-span and character lineage; Ali Romman / PR1862/1969
for the source codes and phase conventions; Rohan Arun / PR1931 for source
continuation; and Douglas Colkitt for the predecessor's arithmetic lineage.
Their complete notices remain in the unmodified source package. Classical
finite-group Fourier inversion and positivity retain their credit; no
global priority for the abstract rigidity lemma is claimed. The new step
is its integrality application to this matched endpoint. New work is
Apache-2.0.
