# Reproduce the frozen nine-module parsed-chart chain

This is a source-only reproduction recipe for manifest `reusable-parsed-chart-chain-source-manifest-v1` at SHA-256 `eba964392e9a8b2fbb9b6888056ec391186d3dd25567f5b830b016b9dfbad57e`. These instructions were inspected, not executed for publication. All individual sources already have their separately recorded native acceptance. The newer `JsonTableGather` follow-on and concrete L450/owner-table applications are outside this package.

## Exact prerequisites and layout

Use Lean **4.21.0** and a prepared Mathlib checkout at **308445d7985027f538e281e18df29ca16ede2ba3**, with package revisions pinned by that commit's `lake-manifest.json` and coherent existing `.olean` dependencies. The import path below omits the unused Cli package. No new installation or cache rebuild is prescribed here. Do not mix Mathlib/runtime versions or use an ambient `LEAN_PATH`.

Set these absolute paths for your prepared environment:

```sh
set -eu
export LEAN_HOME=/absolute/path/to/lean-4.21.0-linux
export MATHLIB=/absolute/path/to/mathlib4
export PACKAGE=/absolute/path/to/the/new/parsed-chart/package
export PUBLIC_REPO=/absolute/path/to/integer-mult-bounds
export BUILD=$(mktemp -d)
mkdir "$BUILD/src" "$BUILD/objects" "$BUILD/logs"
"$LEAN_HOME/bin/lean" --version
test "$(git -C "$MATHLIB" rev-parse HEAD)" = 308445d7985027f538e281e18df29ca16ede2ba3
```

`PACKAGE/sources` contains the eight unchanged new sources listed below. The shared syntax is **not repackaged**. Obtain it from the exact already-public PR1831 commit in a repository that has that Git object:

```sh
git -C "$PUBLIC_REPO" show 542f914ca0e5df4026341d08c84385cb1a71cfdf:research/lean-current1094-route-table-certificate/sources/SelectedSourceSyntax.lean > "$BUILD/src/SelectedSourceSyntax.lean"
cp "$PACKAGE"/sources/*.lean "$BUILD/src/"
```

If the Git object is not available, fetch the exact public commit from `https://github.com/jamesyc/integer-mult-bounds.git` before the `git show` step. Do not substitute a moving branch tip or another syntax file. The public dependency is [PR1831](https://github.com/CrocSwap/integer-mult-bounds/pull/1831), exact head `542f914ca0e5df4026341d08c84385cb1a71cfdf`, tree `04d942fe978ef6f818d0a51f911cdcf67d3b1df2`, syntax blob `4c32caf97240b63b39c0af0a7120c4663028a674`.

Verify all nine exact bytes before compiling:

```sh
cat > "$BUILD/src/SHA256SUMS" <<'EOF'
08d3398cca39262cdc62506bfcdf09cea8d85f98587f1d7d2b59c211454c7684  SelectedSourceSyntax.lean
0d50bd4c37d00e3212fbef0512c33a7c0f47f66ff4bf33cfd9bc65e03f42c61c  StrictParsedIndexCodec.lean
460028e8183d53a3287c013c0e10c492814a4446a4ae1a7a4996e628e1f621db  CheckedBinaryChart.lean
ef0bd93d05bbb6671fe227c49188c14788b35afb7326e05f1b04b164b38e7c73  CheckedPermutationTables.lean
deeb292a0887b1be38133359a6b4458c9da1f2d6d10a3b301df321fd3e9781ec  ParsedBinaryChartCertificate.lean
ba4e0dd153b509fec6d3401f8eb6a7ba1dc8fb3e5aeee58e383419c9626b483c  BinaryChartCanonicalEncoding.lean
8e6c2bde41c72f73e73f41415b857aaa044c2544ffc4cb2fd3fb813a4c98481c  CheckedTableGather.lean
b7336f0b164d433d1d3c69d6fedb80f025867267d81fb30d47f178a5a2d6187d  StrictJsonValueBridge.lean
ed544d3a5b8d1089a3b06b66633b613c6a39b757f0c42a67596a406cd01fe1af  JsonBinaryChartInterpreter.lean
EOF
(cd "$BUILD/src" && sha256sum -c SHA256SUMS)
```

## Isolated import path and serial check order

The only research object directory is the fresh output directory. All other paths are the exact prepared official dependencies:

```sh
export LEAN_NUM_THREADS=1
unset LEAN_OPTS
export LEAN_PATH="$BUILD/objects:$MATHLIB/.lake/packages/batteries/.lake/build/lib/lean:$MATHLIB/.lake/packages/Qq/.lake/build/lib/lean:$MATHLIB/.lake/packages/aesop/.lake/build/lib/lean:$MATHLIB/.lake/packages/proofwidgets/.lake/build/lib/lean:$MATHLIB/.lake/packages/importGraph/.lake/build/lib/lean:$MATHLIB/.lake/packages/LeanSearchClient/.lake/build/lib/lean:$MATHLIB/.lake/packages/plausible/.lake/build/lib/lean:$MATHLIB/.lake/build/lib/lean:$LEAN_HOME/lib/lean"
```

Use the exact topological order below. Run only one compiler at a time, stop on the first nonzero exit, preserve complete stdout/stderr, and require at least 8GiB free disk. A 60-second wall cap and 4GiB address-space cap per root reproduce the bounded policy; these are operational limits, not a theorem about cost. Existing research installations must also use their canonical shared compiler lock. Do not run the whole chain concurrently.

```sh
set -eu
for module in SelectedSourceSyntax StrictParsedIndexCodec CheckedBinaryChart CheckedPermutationTables ParsedBinaryChartCertificate BinaryChartCanonicalEncoding CheckedTableGather StrictJsonValueBridge JsonBinaryChartInterpreter; do
  test ! -e "$BUILD/objects/$module.olean"
  timeout --signal=TERM --kill-after=5s 60s bash -c '
    ulimit -v 4194304
    exec "$LEAN_HOME/bin/lean" -j1 -o "$BUILD/objects/$1.olean" "$BUILD/src/$1.lean"
  ' _ "$module" > "$BUILD/logs/$module.stdout" 2> "$BUILD/logs/$module.stderr"
  test -s "$BUILD/objects/$module.olean"
done
```

This is a fresh-reader recipe, not a claim that this combined shell loop was run in the original acceptance session. Individual historical invocations, resource observations and failures/repairs remain in their immutable evidence. Source hashes, theorem/probe results and exact import closure are the reproducibility target; an object hash may also depend on invocation/path details and is not substituted for kernel checking.

## Acceptance checks

Do not treat exit zero alone as mathematical acceptance. Compare every embedded `#print axioms` and complete printed type against the source and packaged independent terminal evidence. Reject `sorryAx`, errors, unresolved goals, unexpected warnings or unexplained stdout. All observed accepted generic probes use only `propext`, `Classical.choice` and `Quot.sound`, or no axioms. The unchanged sources include their preparation-time uncompiled comments; the additive completed and independent terminal receipts record actual acceptance.

`SelectedSourceSyntax` has no embedded probe and is an exact public dependency. The eight new sources contain 48 probes and 9 full-type inspections in total; the exact declarations are enumerated in the accompanying bounded identity report. Preserve source attribution/license notices and the original evidence instead of rewriting them.

## Exact scope

At the author-checked context kappa=836330098538459/500000000000000000=0.001672660197076918, these generic theorems validate strict parsed indices, checked inverse permutation tables, binary chart certificates, canonical encoding, ordered functional gathering and actual Lean.Json AST chart interpretation. They are independent of kappa.

The five-array chart grammar is a new certificate interface. It has not been equated with a current provider-file format. JSON byte parsing and lexical spelling, external artifact correspondence, complex phases/affine translations, physical chart direction/Hosting/executor and time/space/precision cost remain separate. No full multiplication theorem or change of kappa is asserted.
