# Separate baseline rebuild

The native baseline was rebuilt with unchanged source files and one CPU
thread. Output went to separate directories. No source assertion was
removed, replaced, or patched at runtime.

The roles in the recorded commands are:

| Role | Exact source |
| --- | --- |
| MAIN | base `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` |
| SOURCES, gauge44-leaver8 and gauge44-slots | PR1074 `052afc128954f7b6a2b3c409eb4d72248e4020f2` |
| SOURCES, complex-571-cold14-st2 | PR635 `a6895a69f8ad98ab45777b03e9e6f48888c39f6f` |
| BASE, CELL, CHAIN, SLOTS | separate generated output directories |

The scalar chain used these commands, with each role replaced by its path:

```sh
python3 -B SOURCES/research/gauge44-leaver8/construction/reproduce.py \
  --main MAIN --pr635 SOURCES --out BASE --until word --frozen-cold
python3 -B SOURCES/research/gauge44-leaver8/construction/leaver/reproduce_leaver.py \
  --main MAIN --pr635 SOURCES --word-dir BASE --id k8 --out CELL --word-only
python3 -B SOURCES/research/gauge44-leaver8/construction/leaver/reproduce_leaver_chain.py \
  --main MAIN --pr635 SOURCES --leaver-dir CELL --hamming BASE/hamming \
  --id k8 --out CHAIN
python3 -B SOURCES/research/gauge44-leaver8/construction/barch/build_tri.py \
  CHAIN/frames/FULL-WORD.json.gz \
  SOURCES/research/gauge44-slots/construction/slots/RECIPE-SLOTS-k8.json \
  SLOTS/FULL-WORD.json.gz
```

The base driver, cell driver, and all 21 k8 chain steps exited zero.
The last chain step checked its exact phases. The seven-slot word then
passed the unchanged PR635 native transport, local emission, local
endpoint audit, and residual-adapter checks. The unchanged PR558
`phases_full.py` checked all 2,896 exact phase edges. The recipe digest
matched the seven-slot source pin. `BASELINE-REPLAY.json` records every
command and exit code with the role names above.

The native tools were called through MAIN's retained
`research/complex-k492-owner-repair/vendor/multicold/code/run_portable.py`.
`MULTICOLD_SOURCE` and `GAIN_PR564_SOURCE` both named that `multicold`
directory. `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, and
`VECLIB_MAXIMUM_THREADS` were set to one.

| Output | Content SHA256 |
| --- | --- |
| Raw seven-slot word | `c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8` |
| Canonical seven-slot word | `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c` |
| Exact Clifford recipes | `d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731` |

The raw word is the bundled input. A gzip input is bound by its
decompressed content, not its compression stream. This avoids a false
failure from a different Python or zlib version.

The seven-slot-specific 34 controls and its old owner-map global replay
were not rerun by this lane. The new package's five controls are different
checks of its mathematical claims. The separate owner-packing lane uses
the same completed native baseline for its own full supplier replay.
No new full supplier, outer assembly, or repository-wide cold replay is
claimed by this package.
