# Rectangular common-basis construction

The conditional saving is **κ=12260937/10^12=1.2260937×10^-5**, with bit saving **12261239/10^12**. The tensor dimensions change from (25,23,57) to **(28,27,57)**. A dimension-free common-basis argument supplies the A1/A3 profiles, and an exact Schur identity gives a contiguous width-25 A5 block. All inherited analytic and fixed-tape hypotheses remain.

Read the [standalone proof](../../notes/rectangular-semantic-note.tex), [PDF](../../artifacts/rectangular-semantic-note.pdf), [exact certificate](certificate.json), and [current validation receipt](validation.json). The general proof explains simultaneous nonvanishing in the actual prescribed family, including the free second rows and inverse columns needed for A3. Finite samples alone do not prove that result. Detailed intermediate proofs and independent audit notes are preserved alongside the manuscript.

| Macro | Copies | Profile |
|---|---:|---|
| A1 | 6443903466000 | 28, 1, 28, 28, 42922 |
| A3 | 560756196000 | 113 singletons + 55, 644, 41468 |
| A5 | 560756196000 | 29 singletons + 25, 648 |
| Translated auxiliary | 6351210946080 | 27, 43038 |

The new bit values are m=43092, W=13904995529880, maximum child43038 and halving degree553. The complex network and semantic guard are unchanged. Joint row degree increases to **96000**, with coefficient46636 and suffix slope384000; all47 strict constraints, seven margins and eventual cutoffs use those values.

## Reproduction

Use Python3.11 or later, a C++17 compiler, and Tectonic for the manuscript:

```sh
make rectangular-semantic-certificate rectangular-semantic-patch
python3 -m unittest discover -s tests -p 'test_rectangular_semantic.py'
make rectangular-semantic-producers
make rectangular-semantic-note
make verify
```

`witness.py` validates the live pinned PR23/25 proof/control dependencies, source aliases and archived producer receipt hashes, then reconstructs the histogram, moment and semantic assembly. `producer.py` freshly regenerates h27/h28 scalar DAGs, original carrier matching, positive labels and positive matching; it compares complete numerical records and deterministic DAG/link/label SHA256 hashes. Its fresh report is written to `build/rectangular-semantic/producers/replay.json`. Elapsed times and archived report hashes are metadata, not deterministic regeneration claims. The inherited full verification also freshly rebuilds h57; its prior full PR25 receipt is included as evidence.

Negative controls use incorrect boundary prescriptions, omit the necessary first pivot, omit the A5 grouping, and restore old guard/exposure budgets. The next bit grid point fails the same sufficient upper enclosure; this is not a proof that no stronger saving is possible. Source hashes, exact finite controls and arithmetic checks supplement the written inherited mathematical arguments.

The focused patch is against **PR25 commit003f366cfa99e19fbeacd9300a219f2d44c8cff0**. It is not an integrated patch against the original OpenAI release; inherited integrated patches are preserved unchanged. Full rerun completion is reported separately in `validation.json`.

## Attribution

Physical producers and prescribed partial-swap basis: icekylinx PR18. Translated frames: Zhihao Chen PR21. Semantic composition: Zhihao Chen PR23, inheriting RaD/PR20. Source-frame contributions: eumemic; earlier contributors retain the attributions in NOTICE. Rectangular geometry, new compatibility proofs, conservative A5 block, exact controls and assembly: Rohan Arun with substantial OpenAI Codex assistance. No global optimality or practical-speed claim is made.
