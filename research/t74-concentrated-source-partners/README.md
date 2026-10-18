# Concentrated source-partner compensation in T74

This construction removes four centre splits per call by assigning the eight
source-partner aliases jointly to later helper roles. Every compensation,
restoration, cleanup buffer and changed native instruction is included. The
changed local words are hosted in Jeremy Kothe's credited PR2673 allocation,
transferred by a helper-index bijection that preserves every occupied interval.

The exact complex-moment root is bracketed by

```
0.001715599770234969498858 < root < 0.001715599770234969498859.
```

**Author-checked conditional point:** κ = **0.001715599770234969498857**, giving
`T(n) = O(n (log n)^0.998284400229765030501143)` under the inherited premises.
This is about **0.05829% above PR2673's κ** and **2.5671% above the selected
PR1094 κ**. The complete fresh predecessor, both changed native programs,
strict global assembly and exact outer replay passed. `CLAIM.json` binds the
published rational to `evidence/FULL-RESULT.json` and the outer ledger.
This is an incremental improvement within the conditional framework, not an
unconditional multiplication theorem, practical speed measurement, global
optimum or formal-kernel proof.

## What changes

The source-partner construction is due to [zxv, PR2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530).
The comparison words and complete pipeline are pinned from
[Jeremy Kothe, PR2588](https://github.com/CrocSwap/integer-mult-bounds/pull/2588).
The final hosting source is [Jeremy Kothe, PR2673](https://github.com/CrocSwap/integer-mult-bounds/pull/2673),
at `45aadf0fc7f0dedfb0df959479a20cc1c7be4917`. Its local words are identical
to PR2588 after decompression. Source heads and raw hashes are recorded in
`PREDECESSORS.json`, `SOURCE-PINS.json` and `BOUNDED-SOURCES.json`; the final
publication bindings cover this hosting source as well.

The new assignments `(helper, lender, partner)` are

```
(680,49,33) (681,83,74) (682,98,85) (684,101,55)
(688,68,4)  (689,80,88) (690,88,80) (692,31,12).
```

Their corrections lift twelve targets onto two lines. Eight new line-45 targets are
absent from the centre cut's readers; only four line-30 targets require a split.
Thus four paths of paid ranks `7+1` become rank `8`. The eight saved A-phase
rank-one operations are exactly repaid in B. The complete local change is

\[
\Delta H_{\rm local}=4(H_8-H_7-H_1).
\]

Both providers have local profile
`{1:2363, 2:632, 3:318, 4:120, 5:26, 7:4, 8:4}` with rank mass 5,251.
The 422-helper width inventory remains `{4:33,5:9,7:62,8:78,9:240}`;
there are still 78 dedicated zero cleanup buffers and 58 defined rank-zero
chart operators. The complete word executes 140 chart warp events: 24 in A,
58 in B and 58 in cleanup.

PR2673 supplies the invocation order, dispatch and full owner allocation.
For stages `s=0..8` and replicas `r=0..73`, its literal order sorts by
`(8*s + 2*r + delta[s], s, r)`, where
`delta = [-10,-1,-5,-8,1,0,0,0,0]`. The priority-ordering idea follows
PR2621 (themilkman216); PR2673's offset search and fill are Jeremy Kothe's.
PR2559 supplies the credited evacuation method.

Within each width class, increasing old compact helper indices are matched to
increasing new indices. Every row keeps its time, owner, port, offset and width.
All 281,052 source and transferred roles are checked against reconstructed
windows, preserving the complete idle profile
`{1:21978,3:6594,5:554,32:1,48:26558}`. There is no additional owner-move or
timing-patch claim in this final composition.

Across 666 calls, the entire paid-profile difference from PR2673 is

\[
\Delta H_{\rm global}=2664(H_8-H_7-H_1).
\]

The complete profile is

| Rank | Count |
| --- | ---: |
| 1 | 1,595,736 |
| 2 | 420,912 |
| 3 | 218,382 |
| 4 | 79,920 |
| 5 | 17,870 |
| 7 | 2,664 |
| 8 | 2,664 |
| 32 | 1 |
| 48 | 26,558 |

Rank mass remains 4,816,512. Physical inventory is
`66,814 = 66,304 + 422 + 8 + 78 + 2`, with deficit 23,680 and prefix 2,048.
For `0<p<1`, strict subadditivity gives `8^p<7^p+1`. The complete change
therefore strictly improves the moment throughout the relevant range. This is
an exact argument, independent of the numerical search. [PROOF.md](PROOF.md) gives the correction identities,
chronology, full charge and conditional composition.

The unchanged-coverage, rank-51 packing relaxation for this new local profile
has upper endpoint `0.001744165345454`; the bounded root exceeds 98.36% of that
upper bound. This is a relaxation, not a claim of an attainable optimum or a
barrier for different local interfaces.

## Reproduce

The publication verification command uses Python 3.12 and only the standard
library. It checks the mathematical construction and binds the retained
completed full-admission receipts:

```sh
python3.12 -B scripts/research_package.py \
  --package research/t74-concentrated-source-partners
```

It checks exact free-operator forward and inverse-transpose identities on all
646 independent input columns for each provider; every frame, centre path and
cleanup instruction; the complete physical owner assignment; exact rational
moment brackets; and semantic rejection controls. It also binds the final
full-admission evidence. It does **not** rerun native compilation or the long
predecessor chain. `--check-only` validates package metadata, not the mathematics.
`verify.py --discovery` omits publication receipt binding and is not the
publication verification command.

For a complete fresh admission, from the repository root:

```sh
python3.12 -m venv /tmp/t74-replay-env
/tmp/t74-replay-env/bin/pip install \
  -r research/t74-concentrated-source-partners/requirements-full.txt
/tmp/t74-replay-env/bin/python -B \
  research/t74-concentrated-source-partners/fetch_sources.py \
  --repo . --out /tmp/t74-frozen-sources
CPLUS_INCLUDE_PATH=/path/to/boost_1_87_0 \
/tmp/t74-replay-env/bin/python -B \
  research/t74-concentrated-source-partners/full_replay.py \
  --sources /tmp/t74-frozen-sources --main . --work /tmp/t74-full-replay
```

Use new output directories. A C++17 compiler and Boost headers are required by
the retained exact fine-moment engine. Python dependencies are pinned to the
tested versions; `gmpy2` is optional and was absent in the recorded run. The
replay creates fresh Python cache namespaces and fresh native/phase receipts.
It accepts no externally supplied baseline or native cache. Sources are exact
Git exports and every file is authenticated before and after replay. All local
execution inputs are also checked for changes during the run.

The full command reproduces the PR2530 and PR2588 words, regenerates both new
words and compares their complete payloads with the publication artifacts,
runs a complete fresh PR2588 predecessor release, lowers and audits both new
native programs, and replays the PR2673 ownership, lift, rebind, Lemma G, strict global
assembly, geometry controls and the exact outer ledger. `admit.py` is an internal
stage; calling it directly with an arbitrary baseline is not a supported fresh
admission command. Regenerated gzip containers may differ across environments;
mathematical equality uses their entire decompressed JSON payloads.

The inherited target-swap negative fixture needed a precise correction:
its old first-two-additions swap merely commuted two identical additions in the
new prelude. The replacement selects different sources at the same frame,
produces an explicitly nonzero residual and rejects in both providers. No
mathematical acceptance check was weakened. The original failed fixture and
independent regression proof are retained under `evidence/mutation-regression/`.

## Scope and remaining premises

This is a proof of the stated finite symbolic construction and strict paid-moment
improvement, with executable exact certificates. Its use in the claimed
integer-multiplication exponent retains the predecessor's all-size compiler,
common-label/mutable-source realization, whole-call physical hosting,
precision/tape, exact recovery, analytic transfer, recurrence and bit H1–H5
premises. Finite native and outer checks do not discharge those premises.
The selected maintainer-reviewed record on main remains PR1094. This package
does not modify it.

The package follows the explicit donor request, refining the
`complex-new-helper-inventory` card to a changed local cost interface with the
same width multiset. [TASK.json](TASK.json) records the scientific base, revision-5
family checkpoint, recent-results review and exact remaining obligations.
No search exhaustiveness is claimed.

## Open next questions

Can another legal simultaneous assignment eliminate the remaining four centre
splits? The first useful step is a concrete target-support obstruction or an
exact compensated candidate with the same endpoint contract. A changed candidate
must survive the complete paid/native/global replay.

Can the final order admit another strict whole-role exchange? Pin the published
fill, exhibit the literal exchange and check every affected window, family and
prefix before expanding a search. The packing relaxation alone is not a
construction. Structured next steps and blockers are in `TASK.json`.

## Credit

Prepared by Mason Hale with substantial OpenAI Codex assistance, including
separate computational and proof reviews by other Codex agents. No independent
human review is claimed. Credit zxv's PR2530 mechanism, tekuuu's PR2436 lifted
targets, Jeremy Kothe's PR2462/2588 construction and pipeline and PR2673
priority search/fill, themilkman216's PR2621 priority-ordering idea, Philippe
Van Velzen's PR2559 evacuation, and Rohan Arun's owner lineage.
Retained source notices preserve the native, bit and outer suppliers' full
attribution. See [NOTICE](NOTICE). New work is Apache-2.0.
