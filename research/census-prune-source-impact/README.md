# Whole-tree source impact of the bit-0 word-census prune

**Source-impact audit with a finite calibration. No new f(7) bound, no new κ,
no change to any frozen package or to the selected frontier.**

Card `census-pruning-audit` asks whether the word-census parity error reported
in Nicholas Stone's [PR2973](../f7-weight-parity-census-correction/README.md)
invalidates an exclusion that is still relied on. Earlier packages already
reconstruct `01021323` (#3096, #3821), trace the false prune into #2542 and
inventory six named call sites plus #2691's native rule
([#3215](../f7-set-word-pruning-boundary/README.md)), and replay the corrected
census independently (#3005, #3333). #3215 states that its inventory "is not a
whole-repository dependency proof". This package does that whole-tree check.

**Answer at base `cef4b52f2a59009865bf8eabde1be3f159063703`.** The pruning rule
is disproved. No final bound is disproved, and no exclusion that the current
f(7) line relies on uses the faulty rule. Three word exclusions are retired and
already have replacement evidence. Six set-level packages carry stale anchors
or citations of the old lower bound. Those anchors and citations need reading
notes, not revalidation.

## 1. The disproved rule, pinned

| Old engine | Location | Rule |
|---|---|---|
| PR2542 `cyclic_census` (Aaron Wang) | byte-identical in `universal-f7-singleton-seedb859517b/engine.py` (PR2542), `universal-f7-singleton-l20-seed06704c39/engine.py` (PR2634), `f7-17point-cover-audit-seedcfa215c2/vendor/pr2542_engine.py` (PR2773); SHA-256 `82e4c407…175e4` | groups prefix states by `nq & 1` (coordinate bit 0) and prunes on the caller's balanced budget |
| PR2691 `f7_census.c` (Nicholas Stone) | `universal-f7-singleton-l20-census-complete-seedfd938f30/f7_census.c` | the same `nq & 1` grouping with `#define BUDGET 27` |

Corrected engines pinned as replacements are #2973 `corrected_census.c`, #3005
`census.cpp`, #3333 `replay.c` and #3818 `union_census.c`, which #4221's driver
runs. Each groups by Hamming-weight parity (popcount). None contains the faulty
bytes, a `cyclic_census` call or `nq & 1` grouping. This is a textual source
check, not a proof that these engines are sound.

**Calibration, recomputed independently.** `01021323` has prefix states
`0,1,3,2,6,4,12,8,0`. Its eight states are distinct and cover all 16 masks.
The weight split is `(4,4)` with within-class excess 0. The bit-0 split is
`(6,2)` with excess 8. The balanced budget is `C(4,2)+C(4,2)-7 = 5`, while
the actual-size bit-0 budget is `C(6,2)+C(2,2)-7 = 9`. The old rule therefore
prunes this word at its eighth state, and the weight-parity rule does not.

**Faulty bytes bound to the false prune.** The verifier loads the faulty
engine from authenticated bytes. It compares the engine with a separately
written oracle on the complete `n=4, L=8` simple restored domain. Without a
budget the engine returns exactly the oracle's 22 universal words. With the
balanced budget 5 it returns 16. The six missing words are
`01021323, 01023123, 01023213, 01213203, 01231203, 01231302`. An independent
bit-0/balanced replay rejects exactly these six words. The weight-parity rule
rejects none of the 22. The count matches #3096's recorded six simple false
prunes. This is a deliberate repetition, used only to tie the hash to the
defect.

## 2. Whole-tree inventory

`verify.py --rescan` walked 90,399 `.md/.json/.txt/.py/.c/.cpp/.cc/.h` files
under `research/`, `docs/`, `certificates/`, `scripts/` and `tests/`. The scan
looked for files that contain the faulty bytes, define or call
`cyclic_census`, use the native `nq&1` and `BUDGET` rule in C, quote the old
receipts, or state `20 <= f(7)` / `f(7) >= 20`. The receipts are #2542 L18
15,775,992 nodes, #2634 partial L20 798,901,058 nodes and #2691 L20
6,305,209,079 nodes. Every matching file falls under one of 21 classified
prefixes in [INVENTORY.json](INVENTORY.json). There are **0 unclassified**
files and **0 stale prefixes**.

| Class | Files | Packages (PR, author) | Consequence |
|---|---:|---|---|
| Retired word exclusion | 28 | #2542, #2634 (navinor); #2691 (NicholasStone) | Their L18 simple-cycle, partial L20 and `(10,10)` L20 zero-hit receipts are filter counters, not exclusions. The replacement evidence is #2973's L18 `(9,9)` row and five L20 rows, corroborated by #3005 and #3333. #3058 §1–2 gives `f(7) >= 22` with no word census. |
| Set-level, historical anchor | 28 | #2773, #2870, #2911, #2933 (navinor) | Their set-level rows split by **weight parity**, as their README quotes show, so the bit-0 error does not transfer to them. #2773's `verify.py` re-runs the old L18 call from its vendored faulty engine and asserts `hits == 0`. #2870's `verify.py` and the #2911/#2933 `ANCHOR-REPRO.json` files record the same zero (`l18_universal: 0` or `universal_words=0`). These are reproducibility anchors of an unsound filter, not exclusion evidence. |
| Set-level, stale citation | 9 | #2961, #3023 (navinor) | They state the gap `20 <= f(7) <= 24` at their base. The bound remains true through replacement evidence. #3023 already records the #2973 correction. |
| Audit caller | 6 | #3096 (jwr404), #3215, #3224 (commdata2338), #3333 (1337isnot1337) | They call the faulty engine deliberately, to exhibit the false prune. |
| Replacement | 3 | #2973 (NicholasStone) | Cites the old receipt as history only. |
| Intake archive | 33 | `research/community-*` | Frozen maintainer intake records that quote PR bodies. They are not claims. |
| PR-title list | 9 | ledger and recent-PR snapshots | Store #2542's title, which reads "f(7) >= 20". |

Twenty-six representative files are pinned by SHA-256 with quoted evidence and
role invariants. A faulty-bytes file must carry the faulty-engine role, a
caller must call `cyclic_census`, and a replacement must not call it or group
by `nq & 1`. The #3058 row must still state that `f(7) >= 22` follows from
§1–2 and that it uses none of the #2542/#2634/#2691 censuses.

### Which downstream exclusions need revalidation

* **Need replacement evidence.** Exactly the three retired word exclusions
  above. All three already have it in merged packages. This audit does not
  re-run those replacements.
* **Need no revalidation for this error.** The set-level 17- and 18-point
  results of #2773 through #3023. Their own premises, such as the Sidon floor
  censuses and the Fourier and vanishing censuses, are separate obligations
  and are not checked here.
* **Need a reading note only.** The L18 `universal=0` anchors in #2773, #2870,
  #2911 and #2933, and the `20 <= f(7)` citations in #2773 through #3023. The
  bound now rests on #2973/#3058 rather than #2542. Annotating frozen packages
  is a maintainer decision, so no file is edited here.

**Bounded repair justified:** none beyond the replacement evidence that is
already merged and a possible annotation index (open question 1). Launching
another census would not change any decision identified here.

## Limits

The scan is syntactic. A consumer that relies on the old result without the
faulty bytes, a `cyclic_census` call, the receipts or the `20 <= f(7)` form
would be missed, for example prose such as "length 18 is excluded" with no
numbers. PR-number citations of #2542, #2634 and #2691 appear in 60+ packages,
mostly through the copied card text in `TASK.json`. They were inspected by
hand for the `f7-*`, `connector-*` and KB3 packages, not classified by
machine. The rescan is bound to the base commit: later trees may add
consumers, so it is a manual mode, not the registered command. The registered
command checks the pinned rows, the calibration and the controls. No Lean,
Docker or seven-label census was run. Scientific acceptance of #2973, #3058
and #4221's `f(7)=24` claim is outside this package.

## Reproduce

Python 3.12 standard library, from the repository root:

```sh
python3.12 -B research/census-prune-source-impact/verify.py          # ~0.1 s
python3.12 -O -B research/census-prune-source-impact/verify.py
python3.12 -I -W error -B research/census-prune-source-impact/verify.py
python3.12 -B research/census-prune-source-impact/verify.py --rescan # ~40 s, base-bound
python3 scripts/research_package.py --package research/census-prune-source-impact --check-only
python3.12 -B scripts/research_package.py --package research/census-prune-source-impact
```

The expected marker is
`PASS_CENSUS_PRUNE_SOURCE_IMPACT pinned=26 false_prunes_n4L8=6/22 controls=7 no_new_kappa`.
`--rescan` appends `rescan_files=90399`. `--emit` prints the observed record
without comparing it to [RESULT.json](RESULT.json).

There are seven controls, and each must fail. They are: an audit caller
relabelled as a replacement; the native bit-0 rule relabelled as a
replacement; a tampered pin; the #3058 evidence weakened to `f(7) >= 20`;
planted unclassified consumers in a temporary tree; the balanced bit-0 budget
on `01021323`; and bit-0 grouping substituted into the corrected rule, which
loses universal words. A separate mutation run killed all seven source
mutants: an off-by-one budget, weight replaced by bit 0, a changed word, a
relabelled stale citation, a relabelled faulty engine, a removed intake
prefix and a changed recorded result.

## Open next questions

1. **Should frozen packages with historical L18 anchors carry a reading note?**
   #2773's `verify.py` prints `REPRO PR2542 L18 ... universal_words=0` from
   the unsound filter, and #2870, #2911 and #2933 store the same counter. A
   reader can take these for exclusion evidence. First step: a maintainer
   decides between a central annotation index keyed by the paths in
   `INVENTORY.json` and successor entry points. Blocked by: the frozen-package
   policy, which is a maintainer decision.
2. **Can the single-engine L22 exclusions get a second implementation?** The
   current `f(7)=24` word line at L22 (#3818, #4221) rests on one C engine,
   whose union prune #3899 is auditing on tiny domains. First step: extend
   #3005's separately written census past its `L <= 20` gate on one small
   split, such as `(11,7)`. Blocked by: #3005's length gate and unmeasured L22
   throughput.
3. **Can the rescan be made semantic?** Phrase-level citations of the old
   exclusions are not machine-detected. First step: add the patterns
   "length 18 excluded" and "L = 18 ... excluded" and classify any new hits.
   Blocked by: nothing structural. The false-positive rate is unmeasured.

The structured versions are in [TASK.json](TASK.json).

## Credit

Ross Richardson supplied the PR943 prefix-walk model. Aaron Wang (navinor)
supplied PR2542/PR2634's word engine and the PR2773–PR3023 set-level chain.
Nicholas Stone supplied PR2691's native census and PR2973's correction, which
introduced `01021323`. Nick Petalas supplied PR3005, PR3708, PR3818 and
PR4221. conorholds supplied PR3058. jwr404 supplied PR3096 and PR3821,
commdata2338 supplied PR3215 and PR3224, and 1337isnot1337 supplied PR3333.
Douglas Colkitt supplied the research-package framework. This package adds
only the whole-tree inventory, its classification and the hash-to-defect
binding. It claims no priority over any of those results.

Prepared by JoyboyBrian with substantial assistance from Anthropic Claude
(Claude Code, Opus 5.5). No independent human review is claimed. Apache-2.0.
