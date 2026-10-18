# Generated gzip receipts and exact mathematical payloads

Fixed checked-in gzip input files retain immutable SHA 256 byte pins. This
contribution does not loosen those pins or rewrite PR2260's frozen evidence.
For a newly generated factor archive, the verifier first checks the archive
against its own emitted compressed-byte hash, then decompresses and hashes the
exact payload bytes. The complete mathematical/source/mutation receipt is still
compared field by field. Only the generated compressed representation hash and
elapsed time are normalized; the replacement exact-payload pin is
`8725504a9f3947652966e57c77a335206bc4a09e2831fec2ceb87ea7d3c7546d`.

This addresses the reproducibility issue reported in PR2265: gzip compressed
bytes can vary with compression-library builds even when the certificate payload
is identical. The old frozen package remains unchanged. The new complete replay
recomposes its actual local/native and owner checks and uses the independent
physical auditor directly, with exact payload admission for the new table.

`check_portability.py` invokes the same admission function on six generated
representations: compression levels 0/1/6/9, a filename/timestamp header and an OS
header variation. All preserve the exact mathematical receipt. Eleven controls
reject changed payloads, JSON whitespace, wrong/missing archive hashes, altered
mass/count/source/control fields, a missing mathematical key, CRC corruption
and truncation. This was executed on one installed Python/zlib environment;
it is not a claim to have run multiple library builds. Exact decompressed byte
comparison, rather than comparison of parsed JSON objects, detects whitespace
or other payload changes as well as semantic changes.
