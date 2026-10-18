# Native local replay and source binding

## Exact selected input

The source word comes from PR1140 at
`8e2e18b93d8c6b302e540ad5edc767cb98cf1514`, path
`research/k8-frame-antichain/inputs/SEVEN-SLOT-WORD.json.gz`.
Its decompressed SHA256 is
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.

It is also the exact decompressed input in the selected PR1094 replay
archive at the experiment base. The archive is
`research/community-frontier1094-audit/selected-replay.tar.gz`; its member
is `candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz`.
The sibling `CANONICAL-WORD.json.gz` has decompressed SHA256
`4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.
The retained scalar/frame receipt binds both hashes and the local profile.
The package retains that receipt and the canonical word. Mask zero changes
only a research metadata field; all scalar gates, frames, endpoints, and
paid data are equal to the raw input.

The source tree's old `evidence/local` files are historical R492 evidence.
They are not the selected rebuilt R480 word. The maintainer's
`docs/research/community-batch1099-review.md` already records this distinction.
This package binds to the selected replay archive.

`audit_local.py` is copied without change from PR1238 at
`50a1c992ce28c95d83d11bc691353aaa289d9d65`, path
`research/end-cap-obstruction/inputs/repo/research/gauge44-slots/independent/audit_local.py`.
`intervals.py` is copied without change from PR1240 at
`1e136b8c4a552050820334ad113628775182f08c`, path
`research/complex-local-word-ceiling/ceiling.py`.
`SOURCES.json` gives their Git blobs and byte hashes. It also pins the native
entry points and the baseline attaining-table source.

## Repeat the native run

Use a checkout of the exact experiment base with the selected native source
directories present. The native source is read only. Put all new files in a
new work directory. The commands below use a Python environment that can run
the retained native tools. The recorded run used Python 3.14.7. The package's
standard-library family check was also run with Python 3.12.

Set the three paths, then run from this repository root:

```sh
NATIVE_ROOT=/absolute/path/to/base-checkout
PYTHON=/absolute/path/to/python
WORK=/absolute/path/to/new/two-accumulator-native
UP="$NATIVE_ROOT/research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2"
SRC="$NATIVE_ROOT/research/complex-k492-owner-repair/vendor/multicold"
export MULTICOLD_SOURCE="$SRC" GAIN_PR564_SOURCE="$SRC"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir "$WORK"
"$PYTHON" -I -B research/two-accumulator-saved-arms/build.py --mask 255 --output "$WORK/RAW.json.gz"
"$PYTHON" "$UP/code/hpe_audit_and_transport.py" --raw "$WORK/RAW.json.gz" --routing "$SRC/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz" --out "$WORK/local"
"$PYTHON" "$UP/code/hpe_emit_local.py" "$WORK/local"
"$PYTHON" "$UP/code/hpe_audit_local.py" "$WORK/local"
"$PYTHON" "$SRC/code/run_portable.py" "$UP/code/hpe_adapters_local.py" "$WORK/local/CANONICAL-WORD.json.gz" "$WORK/local/RESIDUAL-ADAPTERS.json" "$WORK/local/WRAPPER-CHECKS.json"
"$PYTHON" "$SRC/code/run_portable.py" "$SRC/vendor/pr558/code/phases_full.py" "$WORK/local" "$SRC/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford"
```

The recorded all-eight run passes:

- transport and exact 704-column maps in both orientations;
- 24,883 emitted events in each orientation and complete paid mass 5602;
- independent local replay and 25 rejected controls;
- exact residual wrappers and 17 rejected controls;
- all 2,900 directed frame/centre edges with exact global phases and 224
  endpoint adapters.

The new canonical content SHA256 is
`0d5d90211bf938b59c1897589e379dfa16eadb0aa3e832f2b01b01a9ea40e50e`.
The Clifford recipe byte SHA256 is
`816fb074375279ed914f9cc7ca14da285fba8c76d133d8db69a60d9cbe74e293`.
Compressed hashes in inherited receipts describe the recorded environment;
content hashes are the comparison for regenerated compressed files.

The native run is for the all-eight word. The all-256 check has the separate
coverage in the README. No complete global owner, physical operator stream,
or new kappa is constructed by these native commands.

## Comparison with PR1319

The fresh PR1319 head is
`603defe58aac018c6a8457840481390a15846fe4`. Both its base and extra providers
use a different local bill and helper inventory. Each still contains all
the gate values removed from B by these eight recipes, but this does not
establish compatibility. The selected cleanup gates at indices 6794 in
recipe 6 and 6791 in recipe 7 are absent from both providers. Their width
inventories are, respectively,

```text
{4:44,5:44,7:38,8:114,9:240}
{4:40,5:48,7:38,8:114,9:240}
```

Thus the recipes do not apply byte-for-byte to these providers, and the
baseline dual constants in this proof do not apply to their inventories.
The saved-arm restoration also touches the later reader helpers 592 through
599. A composition needs new dirty-input, frame, endpoint, and complete
cost checks. This package makes no claim about that composition.
