# Pareto-selected R420 block 6: 54 to 47 XORs

This finite circuit result replaces phase-B block 6 of eumemic's retained
PR543 R420 word. On the same twelve input wires and exact transfer, the block
falls from **54 to 47 XOR gates**. Rebuilding the literal reverse cleanup
reduces the whole local R420 word from **26,916 to 26,902 scalar ADDs**. The
paid histogram, rank mass, and hosted bit lower remain unchanged. **No new κ is
claimed.**

The selection rule is the concrete change tested here: upstream keeps the
randomized pivoted-LU sample with the smallest cancellation-free positive
norm, while this replay records the gate-count/norm Pareto frontier and chooses
the fewest gates among candidates no worse than the original norm. In the fixed
20,000-candidate stream, all 20,000 candidates were valid. The retained
nondominated score pairs were `(47, 5477)` and `(48, 4025)`; the baseline was
`(54, 5513)`. The 47-gate candidate is therefore a Pareto improvement over the
baseline, but the search does not prove a minimum or rule out circuits outside
this sampler.

## Reproduce the finite search and local checks

From the repository root, with standard-library Python 3.11 or later:

```sh
python3 -I -B research/r420-block6-budgeted-lu/verify.py
```

The verifier checks all source pins against the exact base and Git blobs,
recreates the fixed sample and complete candidate word, compares every
proof-relevant field with the stored certificate, verifies selected-record
bindings, checks H1–H5 and the inherited interface over all 660 columns, and
runs the 9 negative plus 1 positive mutation controls. Expected summary:

```text
PASS_R420_BLOCK6_BUDGETED_LU baseline=54 candidate=47 local_ADDs=26916->26902
CANDIDATE_SHA256 492409b42341db62be992b1ed2d402d6aa9d4dacbb64e2fe49a496afe05ed286
```

To write a fresh search artifact, choose a new output directory:

```sh
python3 -I -B research/r420-block6-budgeted-lu/search.py --output /tmp/r420-block6-new-run
```

The verifier compares canonical decompressed JSON, not gzip container bytes.
`search-certificate.json` records the block matrix, wire assignment, sampled
frontier, deterministic PRNG seed, and stopping rule.

## Reproduce native and hosted checks

The full pipeline requires the pinned R420 source environment, NumPy, SymPy,
SciPy, a C++17 compiler, and Boost headers. In a fresh virtual environment:

```sh
python3 -m venv /tmp/r420-block6-env
/tmp/r420-block6-env/bin/python -m pip install -r research/e8-bit-r420/requirements.txt
PYTHON="/tmp/r420-block6-env/bin/python -B" python3 -I -B research/r420-block6-budgeted-lu/hosted.py --output /tmp/r420-block6-receipts
```

`hosted.py` uses the pinned `verify.sh` with two narrow adaptations: step 1
accepts the checked candidate word instead of comparing it to the original
generated word, and the final comparison to the original `EXPECTED.json` is
replaced by the candidate receipts. Provenance, independent local replay,
native cohort checks, five/nine/eleven-stage hosting and prices, and R480/R489
controls run through the existing pipeline.

## Recorded result

The adapted full pipeline passed with Python 3.14.7, NumPy 2.5.3, SymPy 1.14.0,
SciPy 1.18.1, GCC 16.2.1, and Boost 1.92. The main receipts are summarized in
[`VALIDATION.json`](VALIDATION.json).

- Native legality: **29,860** records, **26,902** common-frame ADDs, rank mass
  **5,112**, and nine full-frame COPY/ERASE pairs.
- Five, nine, and eleven stages: **900**, **1,380**, and **1,620** formal
  columns; every payload prefix remains 100 bits.
- Nine-stage bit lower: `413456747036699736067/250000000000000000000000`, with
  **120,960/120,960** residuals hosted whole and zero banks. Its two-level
  coefficient is 418 bits and remains within the existing 512-bit charge.
- Eleven-stage bit lower: `82015816228313440961/50000000000000000000000`, with
  **36,960/36,960** residuals hosted whole and zero banks; the physical prefix
  is 4,710 bits, charged at 4,736.
- Historical PR535/PR531 outer assemblies and the R480/R489 controls reproduce
  their existing receipts. The current selected κ and the exact nine/eleven-
  stage `c` values are unchanged by this local circuit edit.

## Scope and credit

The object is PR543's R420 phase-B block index 6, frame 548, `B[417:471]`.
Assignment seed is **06**, and the exact base is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The input/output
transfer, D and A phases, scatter, helpers, retained totals and recursive
children remain fixed. The selected record at the base is κ =
`0.001672660197076918`, supplied by PR1094 and its reviewed chain; its bit side
is PR589 on PR555's punctured R439 word. The separate historical R420 word
remains below that selected bit supplier.

The R420 word is pinned to PR543 source commit
`2065fe4f72a914d907f1046603f5a36f17018535`. Its PR493 dependency package is
bound by the pinned `DEPENDS.json` and carrier-skeleton manifest; every live
input used here is listed with both a SHA-256 and Git blob in `SOURCES.json`.

The search changes the selector, not the underlying LU sampler. It is distinct
from #661's fixed-gate-stream frame audit, from #670/#674's block-3/block-5
circuits, from #789/#790's block-7/block-9 factor schedules, from #810's
block-8 circuit, and from #1363's block-4 norm-selected sample. PR1015 explores
multi-write shears on a different R439 word; none of its code is imported.
Credit eumemic and the PR543/370/493 geometry, word generator, and checker
lineage; credit yongjae321 (#670), x0hu (#674), Yuzhou Wang (#789), Jerry Lin
(#810), and commdata2338 (#790) for distinct R420 block work. This package is
prepared for **@1337isnot1337** with substantial **OpenAI Codex assistance**.
No independent human review is claimed.

All-size compiler/realization, mutable-basis/common-label, physical hosting,
precision/tape, and analytic-transfer obligations remain inherited and
conditional. This finite circuit evidence is not a proof of the full
multiplication theorem.

## Open next questions

- **Question:** does an exact search outside the randomized LU class shorten
  this fixed block further? **Why it matters:** a shorter circuit could reduce
  the finite native word, although changing κ would still require an eligible
  supplier and complete assembly. **First step:** compare the stored 47-gate
  candidate with a separately implemented fixed-output multi-write shear
  search on the same 12-by-12 transfer. **Blocked by:** no such search or
  all-class minimality certificate is included here.
- **Question:** does the small 418-bit increase in the nine-stage coefficient
  affect a future invoice with tighter charges? **Why it matters:** the
  current 512-bit charge hides that local price change. **First step:** evaluate
  the candidate against an explicitly named future outer assembly's strict
  inequalities. **Blocked by:** the selected result uses a different bit
  supplier and this historical word is not currently composed into it.
