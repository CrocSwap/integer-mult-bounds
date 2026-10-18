# Exact payloads and immutable source pins

Every checked-in input is bound by its exact source bytes. Generated gzip
representations are not mathematical identities: compression level, zlib
version and headers may change bytes without changing the exact payload.

`new/repack/build_fill.py` validates exact canonical payload hashes and literal
owner mathematics. In the full verifier, fresh reconstruction must equal both
the decompressed bytes and decoded JSON of the immutable uploaded owner file.
Only then does the work directory adopt that already pinned representation
before parent lifting. This keeps PLAN assignment hashes and SPEC input hashes
bound to the uploaded artifact, without weakening their mathematical checks.
Internal native/phase receipt byte references are still checked against their
actual runtime files; semantic identities support regeneration across runs.

An actual forced-compression-level1 reconstruction and parent lift changed the
generated compressed bytes, preserved exact payloads and reproduced PLAN and
CONSTRUCTION after this work-only normalization. Independent repack replay
also checked five compression levels per output. These are representation
controls on one installed Python/zlib environment, not a claim to have tested
every Python build. The source tree stays unchanged during complete replay.

The predecessor rebuild script wrote runtime audit/control receipts into its
own source tree. The new rebuild writes all outputs into an external temporary
directory. Fresh complete verification checks every source hash again at exit.
