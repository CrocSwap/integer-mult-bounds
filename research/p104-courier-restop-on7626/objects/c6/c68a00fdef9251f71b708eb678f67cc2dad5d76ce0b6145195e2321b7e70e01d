# Prospective materialized first-gate exact replay

**Static assessment: the exact checker is independently invocable from the proposed byte-materialized tree, provided the export includes the nine pinned inputs listed below. This recipe has not been executed from a materialized export.** It is not a cold replay of full qualification, native, pricing, physical, signed, or common-U resources. The retained original first-gate receipt records the actual prior run; this document does not claim a new reviewer run.

The checker at `kappa-swarm30-20261116/agents/04-exact-oracle/check.py` uses only Python standard-library modules and explicit command-line paths. It has no hard-coded filesystem root or import of local scientific modules. `SOURCE.json` contains a historical absolute `path` field, but this checker reads only its source head and hash fields; it does not dereference that field. The three manifests contain historical metadata but the checker derives candidate projection from their actual typed source-clock edits and does not open paths named in them. `--out` must name a directory that does not exist; it is created exclusively and receives `result.json`.

`prepare_export.py` maps original paths relative to the original `outputs/` directory, so a successful `reproduce.py --work /absolute/NEWDIR` is intended to materialize `NEWDIR/kappa-swarm30-20261116/...`. The currently reviewed full-qualification freeze lists all nine needed files, with these SHA-256 values. Verify their presence and hashes in the actual final `EXPORT-MAP.json` and materialized output before presenting this as a usable package recipe; no final materialization has been tested here.

| Materialized path relative to `NEWDIR/kappa-swarm30-20261116/` | SHA-256 |
|---|---|
| `agents/04-exact-oracle/check.py` | `57bcc50235cdfa534439f47fe70f7fb69fe2cbcab2f0a8d569b4a8b8eb15ddf0` |
| `inputs/SOURCE.json` | `e6a571caa1fd126ae1a12a42e9150fe5d86cc34b29ab79e92ba587ddf77cc5dd` |
| `inputs/source7626-word.json.gz` | `501876971143a0588403d653852b2305893d9b385be94f0f5d7134ebd97e03f0` |
| `agents/01-courier/candidate-word.json.gz` | `9d38de35cba24f617b132205c6ead4aa99cd2ba6413fcaab2141a53aaadd7109` |
| `agents/01-courier/EDITS.json` | `72c9dd53271a170c87927c8a8fa1961cfb8bca2f2c937c24d609dba53143d961` |
| `agents/02-restop/candidate-word.json.gz` | `3acb5ddf69ecc706ce5b591b3d2bfbc6731193401128cc4dfc8cc56c4edb38b9` |
| `agents/02-restop/EDITS.json` | `017224a5609d2f274fad6b27c82c61c61b90aaf94d404ca349708e1766cb1e1f` |
| `agents/joint/candidate-word.json.gz` | `3b0947df9d291308279a00e009f9c1f845151b5b40f81960a53a2949cb44c9a9` |
| `agents/joint/EDITS.json` | `5a3e0bcad804b9c91758bd2acdf8fa9490a8202e98b9b58305477b70f83a9857` |

After materialization and byte verification, a reviewer can choose an **existing absolute materialized directory** for `TREE` and a **nonexistent separate output directory** for `EXACT_OUT`, then run with Python 3.12 (the original environment):

```sh
TREE=/absolute/path/to/NEWDIR
EXACT_OUT=/absolute/path/to/new-exact-output
ROUND="$TREE/kappa-swarm30-20261116"
python3 -I -B "$ROUND/agents/04-exact-oracle/check.py" \
  --source "$ROUND/inputs/source7626-word.json.gz" \
  --source-metadata "$ROUND/inputs/SOURCE.json" \
  --case courier "$ROUND/agents/01-courier/candidate-word.json.gz" "$ROUND/agents/01-courier/EDITS.json" \
  --case restop "$ROUND/agents/02-restop/candidate-word.json.gz" "$ROUND/agents/02-restop/EDITS.json" \
  --case joint "$ROUND/agents/joint/candidate-word.json.gz" "$ROUND/agents/joint/EDITS.json" \
  --out "$EXACT_OUT"
```

Expected successful status is `PASS_LITERAL_EXACT_ONLY`, exit 0, with three named PASS cases, fixed source inventory 204 CLEARs, 700 interfaces, 455 owned stream events, one COPY, 68 labels, peak 50, source-free controls and eight manifest/actual-mutant rejection controls. Compare the resulting `result.json` with the retained first-gate `exact/result.json` (original SHA-256 `ebef891409dca22052498c5e19bf8d01f31f7aadc6d93b6bba1e5c6c8811a645`); record the actual hash and any mismatch instead of assuming reproducibility. The original bounded job reported approximately 164 seconds for the whole first-gate case, including its price screen, under its own fixed controls; this is historical, not a runtime promise for another machine. The checker runs several full symbolic replays and needs appropriate local resources.

This execution would reproduce the source-bound literal arbitrary-entry paired exact check and negative controls. It would not establish physical columns or absolute phase, independent source-certificate admission, complete signed 17-call application, price, resource limits, U implementation, full controller custody, or an unconditional κ theorem. The byte materializer does not rewrite absolute paths in other archived scripts or receipts; those must not be assumed portable from this isolated checker recipe.
