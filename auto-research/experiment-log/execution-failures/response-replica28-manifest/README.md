# Replica28 initial full replays stopped at inventory validation

Both Python3.11 and3.14 stopped before output creation with `Package manifest mismatch`. [Python3.11 log](python311-initial.log), [Python3.14 log](python314-initial.log).

The inherited verifier excluded every file whose basename was MANIFEST.json. The new root inventory intentionally included research-notes/chronological/discovery/MANIFEST.json, so the verifier omitted a legitimate nested source file. The correction excludes only ROOT/MANIFEST.json; nested manifests are now hash-checked. No mathematical input or check was removed. Both original failures remain unchanged. Fresh full runs use separate fixed output folders; a later success must have its own receipt.
