# R420 phase-B block 4: 58 to 51 XOR gates

This is a finite circuit improvement in eumemic's retained PR543 R420 E8 word.
The bounded search shortens the block-4 transform at frame 546 from 58 to 51
binary XOR operations. Rebuilding its required literal cleanup changes the
complete word from **26,916 to 26,902 scalar ADDs**. No helper, target, source
access, COPY, retained total, or recursive child is removed.

The output assignment changes seven register routes after block 4, so this is
not a local replacement with all later records left untouched. The complete
word is regenerated, cleanup is rebuilt, and the paid profile, stage bounds,
and hosted pricing are checked on that word. The result does **not** change the
currently selected construction or κ; the R420 word is a historical alternative
and remains below the current selected bit supplier.

## Reproduce the circuit and exact endpoint

From the repository root, using only Python's standard library:

```sh
python3 -I -B research/r420-block4-resynthesis/verify.py
```

The verifier reruns the fixed 20,000-sample search, rebuilds the full candidate
from the pinned R420 plan, checks the exact stored word and operation
certificate, audits H1-H5 and the interface on all 660 source/target/helper
columns, verifies literal reverse cleanup, and runs the inherited 9/9 mutation
controls. Expected summary:

```text
PASS_R420_BLOCK4_RESYNTHESIS baseline=58 candidate=51 local_ADDs=26916->26902 routes_changed=7
```

`search-certificate.json` records the input wires, target order, exact target
rows, baseline and replacement operations/assignments, optimizer cost, search
seed and stopping rule. `candidate-word.json.gz` is the exact canonical word
that was replayed. Compression bytes are not used as a mathematical equality
test; its decompressed canonical JSON hash is recorded in the certificate.

## Reproduce the native and hosted checks

The full repository pipeline needs Python 3.11 or later with NumPy, SymPy, and
SciPy, plus a C++17 compiler and Boost headers. In an isolated environment:

```sh
python3 -m venv /tmp/r420-block4-env
/tmp/r420-block4-env/bin/python -m pip install -r research/e8-bit-r420/requirements.txt
/tmp/r420-block4-env/bin/python -I -B research/r420-block4-resynthesis/hosted.py
```

`hosted.py` runs the pinned R420 `verify.sh` pipeline against the checked-in
candidate. It skips only the original-word byte-comparison step and the final
summary that compares against the original `EXPECTED.json`; the source
manifest/provenance checks, exact replay, mutation controls, native cohort
checks, both hosted pricing paths, and R480/R489 controls run unchanged. Use
`--output /new/path` to retain the full receipts. The changed-word receipts
are summarized in `VALIDATION.json`.

## Full checks recorded

The additional checks were run with Python 3.14.7, NumPy 2.5.3, SymPy 1.14.0,
SciPy 1.18.1, GCC 16.2.1, and the system Boost headers. See
[`VALIDATION.json`](VALIDATION.json) for the exact receipts and limits.

- Official legality and paid-profile replay: **29,860** records, **26,902**
  common-frame ADDs, nine full-frame COPY/ERASE pairs, rank mass **5,112**.
- Native five-, nine-, and eleven-stage checks: **900**, **1,380**, and
  **1,620** formal columns; each retained the 100-bit payload prefix bound.
- Nine-stage pricing: `c = 413456747036699736067/250000000000000000000000`
  and **120,960/120,960** residuals hosted whole, with zero banks.
- Eleven-stage pricing: `c = 82015816228313440961/50000000000000000000000`
  and **36,960/36,960** residuals hosted whole, with zero banks.
- The published PR535 and PR531 outer assemblies reproduced their exact
  historical κ values. They remain historical controls, not replacements for
  the repository's current selected result.

## Scope and attribution

The candidate is in the randomized pivoted-LU class implemented by the
retained `research/e8-bit-r420/code/nodeopt.py`. The fixed block-4 optimizer
seed is 28, from its existing `7 * block_index` rule; exactly 20,000 samples
were completed. This is a bounded construction search, not an optimality
claim. No candidate outside that sampler is excluded.

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The selected
record at that base is κ = 0.001672660197076918 from PR1094 and its reviewed
chain; its bit supplier is PR589 on PR555's punctured R439 word. This package
changes neither that selected supplier nor the current frontier. It uses the
separate Apache-2.0 R420 source of PR543 and its existing PR370/493 geometry,
generator, and checker lineage. The full-word and hosted replay structure also
credits Ali Romman's PR688. Hosted pricing reuses the PR510/493 pipelines and
the cited PR535/531 outer receipts. Concurrent R420 block circuits #670/#674,
#789/#810/#790 (yongjae321, x0hu, Yuzhou Wang, Jerry Lin, commdata2338) are
distinct and are not imported.

All-size compiler/realization assumptions, the mutable-basis/common-label
interface, physical analytic transfer, and the complete multiplication
theorem remain inherited and conditional. This is finite circuit evidence,
not a formal proof of multiplication. Prepared for **@1337isnot1337** with
substantial **OpenAI Codex assistance**; no independent human review is
claimed.

## Open next questions

- **Relevance:** this improves one finite historical bit-word circuit but does
  not change the selected construction or its κ. A broader supplier result
  would need a candidate that survives complete frame, cleanup, and recursive
  pricing checks.
- **Feasible first step:** run an independently structured search over block
  4's fixed 12-wire transfer, beginning with bounded exact-depth reachability
  or a different circuit representation, and compare its witnesses against the
  included 51-gate circuit.
- **Blockers:** no search outside the retained randomized pivoted-LU sampler
  has been completed here; any supplier-level use also needs an eligible
  full-word construction and all inherited compiler, hosting, precision,
  mutable-basis, and analytic obligations.
