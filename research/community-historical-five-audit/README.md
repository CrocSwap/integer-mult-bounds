# Five early contributions, retained for reproducible historical use

See the [scoped review](../../docs/research/community-historical-five-review.md).
These are alternatives and historical checkpoints, not replacements for the
[selected frontier](../../certificates/selected-result.json).

The complete source trees for PRs **2, 4, 8, 9 and 12** are stored in
`sources.tar.gz` as deduplicated Git blobs. `SOURCES.json` maps every original
path, mode, blob and SHA256 to its exact PR head. Original copyright, notices,
upstream sources and AI-assistance disclosures remain in each tree. The archive
contains 532 distinct blobs and covers all 126 original changed paths; it is not
a collection of current-main patches to apply blindly.

- `DISPOSITIONS.json`: scoped decisions for every changed path, attribution,
  integration status and subsequent GitHub closure receipts.
- `EXECUTION.json`: exact replay recipes, local environment and regenerated
  artifact pins. The receipts do not replace executing the checks.
- `MANIFEST.json`: immutable source/evidence byte pins.
- `replay.py`: offline integrity checks and safe extraction into a new directory.

Run the inexpensive evidence check:

```sh
python3 research/community-historical-five-audit/replay.py
```

Extract an original complete tree for inspection:

```sh
python3 research/community-historical-five-audit/replay.py --pr 4 --extract /tmp/pr4-historical
```

To extract and execute all recorded focused checks, add `--run` and use Python
3.11 or later. Choose a fresh destination. PR9 and PR12 require a C++17 compiler;
PR12 uses several GB of RAM and runs the complete six-dimension census serially.
The recipes compare regenerated tracked files with their original bytes.

```sh
python3.12 research/community-historical-five-audit/replay.py --pr 12 --extract /tmp/pr12-historical --run
```

The source trees contain historical README/frontier statements. Resolve today's
result through the selected record instead. PR4's original PDF predates its final
correction; use the editable source and regenerated certificate. No PDF rebuild,
full inherited test suite, or full formal theorem verification is claimed here.
The general algorithmic, tape and analytic interfaces remain inherited hypotheses.

## Open next questions

- Continue the remaining 92 carry-forwards from the original 100-PR batch,
  starting with their per-file questions. Shared source blobs permit reuse only
  when the contextual inputs and obligations also agree.
- Can the retained alternatives inform today's finite-network bottleneck? Start
  by pricing their complete child profiles under the current interface; old κ
  comparisons are not evidence of a current improvement.
- General tensor, fixed-tape and analytic formalization remains separate from
  these finite circuit receipts. A successful local replay does not close it.
