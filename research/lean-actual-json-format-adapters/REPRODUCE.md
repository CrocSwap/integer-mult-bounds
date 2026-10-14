# Reproduce the four actual JSON adapters

The checked versions are Lean `leanprover/lean4:v4.21.0` and Mathlib revision `308445d7985027f538e281e18df29ca16ede2ba3`. The latter's `lake-manifest.json` fixes its package dependencies. Use these versions rather than moving branch heads. No private object files, review receipts or environment snapshots are needed.

These are reproduction instructions, not a report that this new guide has itself been replayed. The observed acceptance of the exact source bytes is summarized in `ACCEPTANCE.json`.

## 1. Select fresh scratch and acquire public dependencies

Prerequisites: an existing Lean 4.21.0/elan installation, Git, Python 3.9 or later, network access to the public repositories and enough storage for Mathlib. `PACKAGE` is this published package directory, which must contain the four unchanged files in `sources/` as well as the public manifest and fetch script. Choose a new location for `REPRO`; this must not be an existing development checkout.

```sh
set -eu
unset LEAN_PATH LEAN_OPTS
PACKAGE="$(pwd)/research/lean-actual-json-format-adapters"
REPRO="$(mktemp -d)"
export PACKAGE REPRO

git clone --no-checkout https://github.com/leanprover-community/mathlib4.git "$REPRO/mathlib4"
git -C "$REPRO/mathlib4" checkout --detach 308445d7985027f538e281e18df29ca16ede2ba3
test "$(git -C "$REPRO/mathlib4" rev-parse HEAD)" = 308445d7985027f538e281e18df29ca16ede2ba3
test "$(cat "$REPRO/mathlib4/lean-toolchain")" = leanprover/lean4:v4.21.0
LEAN_VERSION="$(cd "$REPRO/mathlib4" && lake env lean --version)"
case "$LEAN_VERSION" in
  'Lean (version 4.21.0,'*) printf '%s\n' "$LEAN_VERSION" ;;
  *) printf 'Unexpected compiler: %s\n' "$LEAN_VERSION" >&2; exit 1 ;;
esac
(cd "$REPRO/mathlib4" && lake exe cache get)
python3 "$PACKAGE/fetch_sources.py" "$PACKAGE" "$REPRO/adapter-check"
```

The fetch script downloads only the nine immutable public source files in the manifest, in the declared topological order, and copies the four package sources. Each byte count and SHA256 is verified before the file is retained. All direct research imports are checked against the manifest. Hash mismatch, unexpected imports or an existing output directory stops preparation. A partial output directory is evidence of incomplete preparation and should not be compiled; choose a fresh directory when retrying.

The exact public prerequisites are:

- `SelectedSourceSyntax` at `jamesyc/integer-mult-bounds`, revision `542f914ca0e5df4026341d08c84385cb1a71cfdf`, path `research/lean-current1094-route-table-certificate/sources/SelectedSourceSyntax.lean`.
- The eight modules from PR1879 at `jamesyc/integer-mult-bounds`, revision `981afe759f7dd206188b1c1a62250c6425bcd76a`, under `research/lean-parsed-binary-chart-chain/sources/`. The manifest lists every complete path and hash individually.

The script uses immutable raw-source URLs, never PR merge refs or branch names. It does not download the selected 144-call tables, rebuild archives, run a supplier or execute Lean.

## 2. Check the exact thirteen-module source closure

The research order, also written to `module-order.txt`, is:

1. CheckedBinaryChart
2. SelectedSourceSyntax
3. StrictParsedIndexCodec
4. CheckedPermutationTables
5. StrictJsonValueBridge
6. CheckedTableGather
7. ParsedBinaryChartCertificate
8. BinaryChartCanonicalEncoding
9. JsonTableGather
10. JsonBinaryChartInterpreter
11. JsonOwnerFieldAdapter
12. JsonGlobalCallAdapter
13. JsonPackedColumnDictionary

A standalone clean reproduction can compile that closure once. If exact accepted predecessor objects are already available, they may be reused instead of recompiled, after verifying their source/version alignment. The following clean-scratch commands use one compiler at a time, a 60-second per-command stop and a 4-GiB address-space limit. They are Linux shell commands; resource fit on a different system is not asserted. Mathlib setup is separate from these research-module checks.

```sh
export SRC="$REPRO/adapter-check/src"
export OUT="$REPRO/adapter-check/objects"
export ORDER="$REPRO/adapter-check/module-order.txt"
mkdir "$OUT"
cd "$REPRO/mathlib4"
unset LEAN_PATH LEAN_OPTS
lake env bash -c '
  set -eu
  cd "$SRC"
  export LEAN_PATH="$OUT:$SRC${LEAN_PATH:+:$LEAN_PATH}"
  export LEAN_NUM_THREADS=1
  while IFS= read -r module; do
    (ulimit -v 4194304
     timeout --signal=TERM --kill-after=2s 60s lean -s65536 -j1 \
       -o "$OUT/$module.olean" "$module.lean") \
       >"$OUT/$module.stdout" 2>"$OUT/$module.stderr"
    test -s "$OUT/$module.olean"
  done < "$ORDER"
'
```

The loop stops on the first failing compiler command. Keep its stdout, stderr and any incomplete outputs to diagnose that attempt. A stopped run is not acceptance of later modules. The four new sources must each complete with an object, no error or warning, and the probes/types specified below. This guide makes no aggregate-time or speedup claim.

## 3. Inspect the acceptance conditions

Each new source contains its own exact `#print axioms` and `#check` commands. Compare all nineteen probe declarations and axiom lists, plus all six printed types, with `ACCEPTANCE.json`. Whitespace and pretty-printer universe names are presentational; bounds, hypotheses, output order and every conjunct are substantive. Reject `sorryAx`, unexpected axioms, missing declarations/types, diagnostics or a nonzero exit.

The dictionary type's printed proof ellipsis is the scalar-check proof carried by its certified value. The Lean declaration keeps that proof obligation explicit. There is no omitted physical-executor hypothesis and no claim that a byte-level provider artifact has passed the checker.

Author-checked context: kappa = 836330098538459/500000000000000000 = 0.001672660197076918. Reproduction does not run or revalidate the selected supplier and does not change kappa.
