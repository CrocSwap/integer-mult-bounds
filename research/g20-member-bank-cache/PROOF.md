# Exact reuse of immutable containment queries

This contribution was produced by Nick Petalas. Apache-2.0.

The claim is implementation equivalence for the one complete census command
in ToikY's PR6396 at `2a5bc94df6d741b49afbadd36d96eb2aea0f6f1f`.
Its scientific result and proof are credited premises. This contribution
does not audit, admit or extend that result.

The frozen oracle represents each rational space as a tuple of eight-entry
tuples of immutable `Fraction` values. Its `contains(outer, inner)` computes
`rational_space(outer + inner) == outer`, with temporary list conversions.
The function and the called rational elimination read their arguments,
allocate local temporaries and return a Boolean. They change neither an
argument nor external state. Containment is directional, so the ordered pair
of complete spaces is the key. No frame identifier, rank, digest or object
identity substitutes for either space.

The new adapter authenticates seventeen frozen files, loads the unchanged
census and oracle into private namespaces, and replaces exactly the oracle
namespace's `contains` binding. This also reaches `route_edges` through that
function's own globals. The retained function object remains the miss handler.
No source file, compiler statement, census loop or scientific receipt changes.

Induct on calls of the replaced binding. On a miss, the original function
computes the same result as before. The adapter stores it under the full
ordered input pair if capacity remains. On a hit, the key equals the pair
used for a previous completed call, whose result equals the original pure
function's value on these immutable arguments. Returning that stored Boolean
therefore preserves the result. Python dictionaries resolve hash collisions
by equality of the complete keys; a hash alone is never a containment test.
When the table is full, a miss still evaluates the original function and
returns its answer. Exhaustion changes reuse only. Exceptions from a miss
propagate without creating an entry.

Consequently each successful query returns the same Boolean, so the census
executes the same branches, context replacements, direct checks and receipt
construction. It retains the original full `FULL-CENSUS.json` comparison,
including both per-cut digests, every category and every first positive
checkpoint. The independent direct kernels and nonzero Schur control still
execute. No prior census answer is substituted for a current context.

The table is created inside each run and discarded afterwards. It holds at
most 32,768 pairs. Space arguments have at most eight rows of eight rational
coordinates in this fixed source domain. The finite run's observed entry
count is recorded by the new verifier. This is a bound on retained cache
entries, not on all allocations of the original census or Python runtime.

The proof is conditional on the authenticated source's stated immutable input
contract. It gives no theorem for mutable arguments, a stateful predicate,
changed frame geometry or a different caller. Finite controls corroborate
the adapter and source binding; they do not establish the predecessor's
mathematics or independent scientific acceptance.

## Engineering decisions

Build the Lever led to the opt-in replay and alternating benchmark commands.
Prove It Works led to complete receipt equality and actual source corruption
and implementation mutation controls. Explain the Number and the benchmark
checklist led to a separate profile, complete fresh-process measurements,
output/error checks and five alternating pairs.

Power of Ten inspection covers the four new Python programs and their
fixed source-loading boundary. New functions are below sixty lines. There
is no recursion. The cache has a hard entry limit and safe fallback. Fixture
loops have fixed finite domains; benchmark pairs are restricted to five
through ten and each subprocess has a 120-second timeout. Source iteration
is exactly seventeen declared files, and the receipt inventory is bounded
at sixty-four files.

Rules 3, 8 and 9 need managed-runtime deviations. Python allocates dictionary
entries and immutable objects, so no allocation-free steady state is claimed.
The cache entry bound and fixed eight-coordinate source domain constrain its
additional retained state. Dynamic compilation is restricted to authenticated
source modules and the two explicit implementation mutants in the verifier.
The original predicate callback and fixed dictionary function lookups are
required to preserve the private source namespace; no caller-selected code
or plugin discovery is provided. Before adopting this in a service or a
different caller, supply its own input, allocation and dispatch limits.
Warning-strict normal and optimized commands are the available Python
diagnostics. The frozen predecessor code retains its own resource behavior
and is not refactored here.
