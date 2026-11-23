# Portable integration replay

The parent `verify_binary.py` replays all four accepted checkers in normal and
optimized Python: binary census author, capacity-corollary author, independent
census reviewer and independent capacity reviewer. It preserves every copied
author and reviewer byte. `PORTABLE-FILES.json` lists the 44 exact exported
files, their lengths and SHA256 hashes; no source or path adapter was applied.

```sh
python3 -I -W error -B verify_binary.py --output /tmp/retimed-binary-review
```

The wrapper can be invoked by absolute path from any directory. The output
directory must be outside this research package. Child processes receive fresh
bytecode-cache namespaces, isolated Python, warnings-as-errors and an explicit
normal or optimized mode. No network, runtime bootstrap or external Git object
database is used. The complete wrapper has a 175-second budget, with each child
limited to the remaining budget and at most 90 seconds.

Before execution, the wrapper authenticates the original author freeze,
both independent acceptance receipts, all retained source/dependency manifests,
the complete exact-copy inventory, the final storage application and the
unchanged parent joined theorem. It also binds the already retained literal
`periodic.Job.select` owner-alias implementation.

The author checkers and census peer write JSON to stdout. The capacity peer
accepts explicit author and output paths. Its development-location strings
remain unchanged as provenance; the actual command uses the portable arguments.
The census peer already supports its parent directory as the author package,
so its existing locator works unchanged under `review/`.

Each replay result must equal the frozen accepted evidence in every
mathematical field. The capacity peer's `python` version field is treated as
environment metadata for comparison with its original receipt. Normal and
optimized results must still match each other byte-for-byte, including that
version. A before/after file snapshot verifies that the wrapper changed no
frozen package file. Replay JSON, logs and the final result are written only
to the requested external directory.

This wrapper verifies portable replay and the reviewed dependency join. It does
not change the scientific claims, source head, selected kappa or canonical
premises recorded by the components.
