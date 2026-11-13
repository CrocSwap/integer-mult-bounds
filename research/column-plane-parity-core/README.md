# Exact parity deletion for column planes

The contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

This answers Open next question 1 of unpaidmoon's
[PR #7282](https://github.com/CrocSwap/integer-mult-bounds/pull/7282), pinned
at `77b12ac33472b168c5ca6353572d76ed9a76e808`. It adds a necessary and
sufficient duplicate-pair deletion test and a complete finite classification
of surviving ordered cores. It does not replay that package's census or
validate its predecessor results.

## Result and claim types

**Scoped written proof.** Choose bases for two binary column planes. Each
external coordinate has one of fifteen nonzero joint four-bit types.
Deleting equal types in pairs leaves exactly the odd-multiplicity types,
independently of deletion order. Six explicit weight inequalities decide
whether both planes retain dimension two and minimum nonzero weight two.
A separate rank-four test decides whether their image spaces stay disjoint.
If the final core passes, every intermediate deletion is safe.

The core has at most **17 used coordinates**, and this bound is sharp.
Theorem 3 also gives an exact multiplicity normal form for all original
pairs that survive complete deletion, at arbitrary finite width.

**Exact finite certificate.** Of `2^15 * 4 * 4 = 524,288` type-labeled
core states, exactly **467,945** pass both tests. Quotienting by the 36
independent plane-basis changes gives exactly **15,710 ordered coordinate
orbits**. The order of the two distinguished columns is preserved.
[PROOF.md](PROOF.md) gives the reduction, full table and count specification.

The direct orbit enumeration and a separate Burnside enumeration agree
at every width. The Burnside path uses permutation cycles and literal
binary generator matrices rather than the direct path's subset lookup
tables. Literal binary rank and weight calculations also check the test
on every type-labeled state. The verifier exercises 1,200 actual pair
deletions and separate rank, distance, cross-coordinate and collapse
controls. No predecessor scientific verifier is imported or executed.

The selected conditional kappa remains `363005817/100000000000`. This
is a local binary geometry result, not a new physical word, paid supplier,
native alphabet, improved bound or complete multiplication theorem.

## Scope, sources and overlap

The `bit-new-register-model` card is explicitly marked **changed scope**
in [TASK.json](TASK.json). The new result answers a deletion question in
the local BIT image-space model. It does not satisfy the card's native
construction and complete-cost acceptance gate.

The base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`.
Revision 8's catalogue predates selected #7000; the contextual picker
reported that mismatch. Selected source-binding orientation passed and
was used only as metadata orientation, not a scientific replay.

The source is unpaidmoon's #7282. Its two exact source notes are retained
unchanged in [source/README.md](source/README.md) and
[source/PROOF.md](source/PROOF.md), with original SHA256 and Git blob IDs
recorded in [SOURCES.json](SOURCES.json). These local committed exports
remove any dependency on fetching an unmerged predecessor commit. The
coordinate model retains the lineage cited there, including #7221,
#7139 and earlier image-space work. The new proof uses the model and
question, rather than a prior construction or prior numerical result.

Live open PRs, recent account PRs, the latest handoff comments, batch
reservations, merged-PR term searches and main-branch README searches
were checked before the claim. A complete 800-open-PR corpus and 7,400
Discussion records were available to the overlap helper. The dedicated
source search found no #7282 reference among this account's 94 recent
open PRs. Its closed-PR refresh timed out, and sparse local note search
was incomplete; explicit main-branch and merged-PR searches supplemented
those gaps. Absence of a match is not a novelty certificate.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/column-plane-parity-core/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/column-plane-parity-core/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/column-plane-parity-core
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/column-plane-parity-core --check-source-history
```

The absolute interpreter path records the local environment. On another
machine substitute its CPython 3.12 executable. The registered commands
use `{python}` and need no dependency installation. Both direct modes
print `PASS_COLUMN_PLANE_PARITY_CORE`, `states_checked=524288`,
`labeled_total=467945` and `orbit_total=15710` as JSON fields.

Local environment: CPython 3.12.15, macOS 27.0.1 arm64. The registered
checks are timed locally and each has a 120-second timeout. Check results
and hosted status are recorded in the PR body.

Not run: Lean, Docker, a selected scientific cold replay, a native or
physical caller, supplier admission, or a complete multiplier. The proof
for all multiplicities is written; the finite census is computational.

## Verification implementation bounds

The checker has no recursion, network access, subprocesses or writes.
The domain is fixed at 32,768 supports and sixteen cross choices, with
36 group actions. Binary elimination scans at most 77 bits over six
rows. Literal multiplicities are at most five per type; group cycles
close within fifteen steps; fixed subsets number at most 32,768. The
largest table storage is 36 arrays of 32,768 unsigned shorts, plus a
524,288-byte visited map and bounded temporary collections.

Python performs managed allocations, a deliberate departure from fixed
allocation rules. The finite bounds above constrain live memory. All
functions are below sixty physical lines. Explicit `require` checks
remain active under `-O`; warning-strict normal and optimized runs are
registered. No shared configuration or frozen evidence is edited.

## Open next questions

- Which surviving core yields a favorable complete native query and
  restoration tariff? Start with one six-coordinate core, specify the
  arbitrary-input alphabet and producer/consumer bill, and stop if the
  complete bill fails. No physical word or tariff is supplied here.
- Can a different projection or legal replacement handle an original
  whose parity core fails? Start with the even-multiplicity counterexample
  in PROOF.md. Unequal-type deletion needs new rank, distance, restoration
  and cost arguments; this theorem supplies none of them.

The structured questions and blockers are in [TASK.json](TASK.json).
