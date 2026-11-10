# Packed Gaussian Newton membership

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algorithm-preservation proof with finite corroboration
and local performance evidence. At rank nine, a guarded packed transform
uses nine integer subtractions in place of 4608 component subtractions.
These are different arithmetic operations; the count ratio is not a speedup.

For lists of Gaussian integer pairs on ranks zero through nine, with absolute
component bit lengths at most 8192, [packed.py](packed.py) returns exactly
PR5374's membership decision and first failing coefficient tuple. It preserves
the input, including arbitrary signed components. [PROOF.md](PROOF.md) proves
borrow isolation and stage induction for every input in this domain.

This builds on Ali Romman's [PR5374](https://github.com/CrocSwap/integer-mult-bounds/pull/5374)
bounded-residue algorithm and Clear1nsight's
[PR3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382) Gaussian
Newton lattice. Their lattice, sharp modulus and collector results remain
credited premises. No predecessor file or credit line changes.

## Evidence

The new checker passes 1364 guarded digit-pair cases, 65,812 small arrays,
160 signed and component-boundary fixtures, complete transformed-array
comparisons with independent subset sums, malformed-input/source controls,
and a fault injected into the production transform with its guards removed.
All checks use explicit exceptions and remain active under optimized Python.

The opt-in adapter also executes the complete inherited scientific replay
with only the membership functions replaced. Its output is identical,
including all 96 literal collector prefixes. Source decoding, independent
oracles and failure controls remain executed. This is preservation evidence
for the new algorithm, not an audit deliverable for PR5374.

[PERFORMANCE.md](PERFORMANCE.md) records five alternating fresh-process
trials per side. It reports the complete public API separately from the
complete scientific replay and whole-process costs. All timed work runs,
input/results match, and no errors occur. The benchmark prints raw samples
and controlling-file hashes; no timing threshold controls acceptance.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/packed-newton-membership
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-newton-membership/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/packed-newton-membership/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/packed-newton-membership --check-source-history
```

The verifier prints `PASS_PACKED_NEWTON_MEMBERSHIP`, all exact counts and
hashes of its package files. It writes nothing. The generic launcher runs
both normal and optimized checks. For a different checkout, substitute its
CPython 3.12 interpreter path. Timing commands are in PERFORMANCE.md.

[SOURCES.json](SOURCES.json) pins canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` and every imported predecessor
input. [TASK.json](TASK.json) records the change from the broad replay-runtime
card to this exact public validation algorithm. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19380573)
states the original bounded target. No source or result cache is added.

## Limits and credit

The API has a declared finite rank and bit-width domain. It does not replace
the unbounded reference API outside that domain and emits no decoded wide
coefficients. No default caller is patched. Runtime numbers describe one
host and one fixture. A faster logical predicate does not price input
movement, physical validation, allocation, erasure or restoration.

There is no new kappa, selected-frontier change, supplier admission, native
implementation, uniform compiler or complete multiplication theorem. All
five selected framework assumptions remain. No selected cold replay, Lean
or Docker run is claimed. Independent human and formal proof-kernel review
are unclaimed.

Credit Ali Romman for PR5374's algorithm and replay; Chris R / Clear1nsight
for the PR3382 lattice and collector; ywz65, Arham Tahir, Tekalign / PR3025,
Ross Richardson and the retained word, wrapper and period-domain lineage.
Guarded packed arithmetic and Boolean difference transforms are standard
techniques. The new work is their concrete implementation, proof and
source-bound integration for this validator. No literature-priority claim
for the general techniques is made.

## Open next questions

1. Can a physical membership-only consumer benefit after input acquisition,
   movement and restoration are fully charged? First name and price one
   actual consumer. No physical scan or supplier contract is supplied here.
2. Can the unchanged input-validation and independent-decoder work in a
   complete replay be reduced without losing diagnostics? First profile one
   source-bound replacement. This contribution stops at the membership step.

## Implementation bounds

The new call graph has no recursion. Public input is capped at 512 pairs and
8192 bits per component. Plan construction has ten ranks, at most nine stages
and 1024 bytes per mask. A call has at most nine transform stages, 512 packing
iterations and 512 certificate tests. The independent subset oracle has at
most 512 squared iterations per fixture. The finite checker does not retain
its census; source replay has its existing finite bounds. New functions are
at most 60 lines. Exceptions enforce meaningful contracts under `-O`.

Power of Ten rule 3 deviation: CPython allocates integers, byte arrays and
library objects while running. Fixed-capacity allocation is unavailable in
this runtime. The finite input limits bound live data; packed integers use at
most 8192 positive bits, and each source read is capped at 32 MiB and closed
with a context manager. The full source replay retains its predecessor's
managed-memory contract. A fixed-allocation port would be a separate task
if this predicate becomes a physical backend component.

Rules 8 and 9 deviation: the preservation adapter imports a fixed finite set
of authenticated Python modules, and the benchmark selects between two fixed
functions. All targets are explicit and source-pinned. Module/path bindings
are restored after import; no shared predecessor module is modified.
This boundary is retained to execute the actual source replay. Source-drift
controls and the full replay check it. A static native integration would
need its own loader and memory contract.

Warning-strict normal and optimized Python checks, development mode and
source compilation provide diagnostics. No external static analyzer is
available in the selected environment; no repository-wide settings change.
