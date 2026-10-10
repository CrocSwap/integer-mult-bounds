# PR332 producer-binding portability repair

Frozen PR332 passed both local full replays. Its Linux run
[38083195160](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38083195160)
passed all twenty preceding stages, including exact expanded-byte source
regeneration, then rejected the regenerated gzip container hashes at
`finish.py:41`. Gzip representation depends on the operating system and zlib.
The original producer explicitly allowed equivalent gzip representations.

This separate branch restores that contract at final admission. Every stored
package file remains byte-pinned by the manifest. Both actual input and output
container hashes are checked independently, the exact five filenames are
required, and all complete expanded bytes must agree. Plaintext files retain
raw byte equality. No JSON parsing or normalization replaces byte comparison.
The scalar construction, selectors, all mathematics and vendored sources are
unchanged. The conditional κ and inherited theorem assumptions remain those
of PR332; this is a verification portability repair.

The mandatory production control stage tests ten rejections. The independent
review additionally exercises missing physical files, equal-cardinality key
substitution, JSON-equivalent but byte-different content, stale hashes after
recompression, and invalid gzip CRCs. Valid gzip filenames, timestamps,
compression levels and OS metadata may differ only if the entire expanded
payload stays exact. Saved audit JSON files are retrospective receipts and
are not accepted as construction inputs.

After a fresh complete construction replay, reproduce the independent controls:

```sh
python -B research/p10b-portability-audit/controls.py \
  --package research/p10b-oriented-constructed42 \
  --regeneration /tmp/p10b-portable-proof/source-regeneration \
  --output /tmp/p10b-binding-independent.json
```

Prepared with substantial OpenAI Codex assistance. All inherited author and
AI disclosures remain in the unmodified construction notices.

Two fresh complete immutable replays exited 0: Python 3.11 in 1020.1577 seconds
and Python 3.12 in 831.9726 seconds, each with all 22 stages. Their mathematical
certificates match each other and the original PR332 certificate after removing
only top-level receipt hashes. The source gate independently rechecked all five
complete payloads and both actual container hashes. Saved receipts are external
to the immutable package and never substitute for fresh verification. Linux CI
for this separate repair head remains pending at publication.
