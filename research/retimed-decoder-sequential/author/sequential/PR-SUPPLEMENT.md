## Additional result: sequential decoder-owned bookkeeping

The representation theorem leaves movement and table-operation time open.
This supplement closes that particular decoder-side gap for the same
source-pinned binary Plan and the same explicit resident-service boundary.
It uses sequential sorted tables, complete paid scans, copy-and-clear
rewrites, immutable event and caller-row tapes, separate current-record
buffers, explicit callback action/slot messages and preserved full-Job
continuations. Fixed physical roles are reused and retain historical peaks.

For h>=3000, N=2^h, B=N^92, the entire literal Plan.run has local bookkeeping
below BN^350 tape steps, including at most B groups, exactly N^2 rounds per
group, all B row initializations on every decode, up to C=2N^83 free-slot
scans per open, and repeated chart conversion. An explicit all-size induction
proves N^512<=9^N once N>=2^16. The actual complete-field geometry W/B>=9^N
then gives bookkeeping <W. Binary register operations are lowered by written
loop bounds and a direct bitwise arithmetic witness. The revised sum of
historical role allowances, including the immutable caller input and a
fixed-alphabet encoding, stays below 32BNh bits.

This is a scoped local clock theorem. Plan and event production, native and
leaf bodies, zero allocation/erasure bodies, service-side slot dispatch,
whole-Receiver fields and outer numerical fields remain separately charged.
The checker is a value-exact sequential reference with physical table-cell
counters and conservative register/adapter upper bounds; it is not a claim
about CPython memory or a measured production machine clock. No runtime,
selected assumption, certificate, activation threshold or kappa changes.

Validation covers unchanged source callback traces, complete multi-group
and multi-round runs, preserved caller rows, repeated warm runs, insertion
and deletion, physical lookup distance, action-opcode distinction and
bitwise arithmetic. Original source/proof/codec files and original normal
and optimized receipts remain unchanged. This supplement has its own
scientific freeze and separate independent review.
