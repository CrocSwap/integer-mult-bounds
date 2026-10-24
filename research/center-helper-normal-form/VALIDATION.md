# Executed validation

Scientific implementation commit: 5c2c40c8f8fcbcb8cdb7bc501670f46505ced07d.
Linux x86_64, CPython 3.12.15, standard library only.

- Registered metadata/source-pin check and full registered replay: PASS.
- Direct isolated optimized replay: PASS.
- All 640 native primal and raw inverse-transpose columns: PASS.
- Both basis inverses and both operator inverses: PASS.
- All native scalar charts, paid ranks and the 758 boundary gates: PASS.
- Both complete positive scalar envelopes remain below 2^192.
- Wrong boundary sign, omitted footer and wrong footer chart: rejected.
- Committed-byte/source-history preflight: PASS, 11 scientific files.
- Committed export and archive integrity: PASS, 11 files.
- Fresh extracted Git-free export replay, PATH=/nonexistent and isolated
  optimized CPython 3.12.15: PASS.
- Whitespace check: PASS.

Scientific source main: b58ad9ef4d4e861b0eaa5dba41742bdc072dca51, revision 7.
PR4694 frozen head: 039a3e4f8906400cd05908ed86b8f9c6866e6113, preserved in ancestry.
Its current head at the submission refresh was 2add42d1edf14a263abe90a3bcde67fc1ba30768.
The ABI and original round-three payload are unchanged. The new cache sections
are credited; the direct cache and scalar-span failures are not overturned.
The live queue through #4696 and the cached overlap report were read. Remote
cache pagination was complete at its reported timestamps; sparse local coverage
was incomplete. No exclusive novelty claim is made.

The first authoring run caught a stale assumption that the cold helper pool
contained 213 fields. The actual round-three source has 326; every one of the
106 observed helpers is in that pool. Final normal and optimized replays use
and authenticate the actual count.

No new physical phase audit, complete controller, compiler/outer admission,
selected cold replay, full Lean proof or independent human acceptance is
claimed. No higher K or independent productive-center credit is claimed.

Continuation: consumer.py adds a conditional two-call homogeneous three-field
identity. Exact cyclic-group-ring coefficients, the actual inverse transpose,
two independent dense rational specializations and five failure controls pass.
The complete registered replay and isolated optimized replay pass after this
addition. The actual native provider is explicitly not realized; no source
invoice or K is assigned to this conditional identity.
