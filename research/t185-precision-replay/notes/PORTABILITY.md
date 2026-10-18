# Independent PR2863 portability diagnosis

The published wrapper does **not** reproduce unmodified on this Linux/Python
3.12.14 environment. Two packaging issues are separated from the mathematics.

1. Exact head `34328b1d5e5bebac62d5cabec993dfbfd7b2123f` contains 162 of the
   164 files listed by its unchanged manifest. Including `MANIFEST.json`
   itself, the publication has 163 files and the complete package requires
   165 files. The only absent entries are `.gitattributes` and
   `vendor/pr2857/.gitattributes`. Both expected SHA-256 values are
   `705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da`.
   The seven exact bytes `* -text\n`, retained in pinned PR2857, recover them in
   a separate copy. No mathematical input, checker or manifest was changed.
2. After that exact recovery, all five finite stages pass, but the wrapper's
   compressed-file equality check rejects `FILL.json.gz`. The stored and
   regenerated 3,415,347-byte containers differ only at byte offset 9, the gzip
   OS-header field: `ff` versus `03`. Their complete 14,452,025-byte payloads
   agree exactly, with SHA-256
   `7a972fdb2228dc04ca8319e2c3db26ee01a0c68ab86465b642100a35d72834dc`.
   The other four named generated data files agree byte-for-byte.

The local runtime is Python 3.12.14, with build/runtime zlib 1.3.2. Its actual
standard-library `gzip.compress` implementation delegates `mtime=0` to zlib.
PR2863's published native environment records Python 3.13.5 on Windows.
The observed failure is a container-header difference; no broader cross-runtime
claim is needed for the diagnosis.

## Separate finite replay

`verify_portable.py` is a new follow-up adapter, not a modified predecessor
wrapper. It authenticates the original exact missing-file pattern and every
present source byte against a pinned manifest hash, authenticates the recovered
copy's complete inventory, and checks the recovered bytes exactly. It freshly
executes all five original mathematics stages serially with assertions enabled.
Every command, exit code, entry-script hash, complete input-manifest hash,
runtime, output/log hash and elapsed time is recorded in `fresh-replay/RESULT.json`.

For generated gzip output it compares **every decompressed byte**, as required
by the repository's `CONTRIBUTING.md` section on regenerated compressed
artifacts. Stored immutable gzip inputs still require their exact original
container hashes. Original wrapper release/native/claim bindings and the
1,163-pattern LP status check are retained. Original and recovered inputs are
reauthenticated after execution.

Run from this directory, with a new external output path:

```sh
python3 -B verify_portable.py \
  --original ../pr2863/research/shared-kernel-packing \
  --recovered ../repaired-pr2863 \
  --work ./another-fresh-replay
```

The recorded run exited 0 with
`PASS_INDEPENDENT_PORTABLE_FINITE_REPLAY`. It reused no previous component
outputs. All five preserved mathematics stages passed freshly, including
their own controls. Additional controls accept a header-only change with an
identical payload, reject a validly recompressed altered owner-row call
coordinate, reject a truncated gzip trailer, and reject substituting a
header-varied container for an immutable source file.

This does not claim that the original wrapper passes. It is an independently
implemented reproduction adapter for the published finite construction and
packing certificate. It authenticates stored complete native/outer receipts;
it does not freshly execute those expensive stages or establish the inherited
all-size multiplication theorem. The coordinating session runs those separately.
No new mathematical exponent or runtime speedup is claimed here.

Credit Dugongue/PR2863 for the construction, checkers and packing proof,
Yiyang/Lyy-iiis/PR2857 for retained inputs, and all contributors in their
unchanged notices. New adapter and diagnosis prepared for digitalis-p with
substantial OpenAI Codex assistance. Apache-2.0; no independent human review.
