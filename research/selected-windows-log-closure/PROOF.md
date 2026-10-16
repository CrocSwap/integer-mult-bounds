# Acceptance boundary of the composed caller

Let a side consist of the 105 named output byte strings, the outer execution
log, and a context giving six input roles and three external input byte strings.
The reference side is separately authenticated against the immutable reviewed
archive. The candidate side is produced by a freshly executed source-bound
successor; it is not accepted solely because an arbitrary file tree compares.

The unchanged PR2344 adapter first requires the six native keys to be exactly
the declared role keys, with their actual same-side hashes. It rejects ambiguous
or colliding roles and translates only those keys. The unchanged PR2101
`prepare` then authenticates all 30 raw references: six input roles, two invoice
links, and both copies of eleven inner-log hashes. It also requires equal
ordered stage arrays, successful integer exit codes, and valid fresh timings.
This happens before any log representation is altered, including on a side
whose bytes happen to equal the other side's bytes.

Define `L(b)` by replacing each CRLF pair in byte string `b` with LF and rejecting
if any CR remains. This is the entire added log policy. The eleven log names
come from the fixed PR2101 stage policy. Every other log byte is retained, and
no JSON string value or gzip payload receives this transformation. In each
stage array, replace only the authenticated raw log hash with `SHA256(L(b))`.
Serialization retains exact integers, decimals, Booleans, strings and object
contents; it does not round through binary floating point.

The unchanged complete PR2101 comparator now compares the two resulting file
sets. Thus a changed inner log with repaired raw references still changes its
complete normalized byte string and is rejected, unless its sole difference
is the declared CRLF/LF representation. An unrepaired reference is rejected
earlier, even if its two logs would normalize identically. Rebinding hashes
without the earlier authentication would not have this property.

All other predecessor obligations remain: exact 105-file inventories; complete
typed JSON and decompressed gzip payload comparison; independently authenticated
invoice references and complete invoice comparison; exact six-role acquisition;
only the 22 declared fresh timing locations may differ. Copied historical times,
unknown fields and all unclassified digests remain literal. The complete outer
log separately passes `L`, then PR2101's 13-line validator binds every printed
stage time to the same-side array and checks both exact final result lines.

This establishes the declared representation equivalence of two authenticated
final-stage executions under the hash assumptions already used by the source
manifests. It does not establish correctness of arbitrary outputs, a mathematical
theorem about the supplier, or platform-independent cold ancestry. A reviewer
must still trust the reference binding and the inherited stage checks.
