# Split-key kernel search on the T74 pivot-566+554 base word (no new κ)

**Negative result. No κ is claimed and no construction is changed.**

In the open κ claims built on PR1673's capped outer (PR1928 and predecessors), κ sits within 1e-10010 of the T74 complex supplier's own saving. So only a cheaper T74 local word can raise it. The last two gains on that supplier were single **helper-donor kernels**: PR1625 at pivot 566 and PR1672 at pivot 554.

- Each kernel deletes one read `t += c·s`, which removes a rank-3 split (−6,763 cost units).
- It then restores exactness with a few inserted reads that cost one rank-2 split (+4,913).
- Net per call: H1 +1, H2 −2, H3 +1, which is −1,850 units. That was worth about +4.1e-8 in κ each time.

PR1957 found no third kernel. Its compensation search only lets inserted reads use registers that hold **a multiple of the deleted read's source value**. It ran that search on 16 one-split reads, 85 large-gain B reads and 5 sampled A-section pre-cancels.

This package does two things:

1. **Completes the A-section deletion relaxation.** PR1957 priced 327 of the 3,451 A gates; this package prices the other 3,124.
2. **Widens the compensation family to split keys.** Inserted reads may use any value in a small linearly dependent family: every value held by the deleted read's source or target register over the whole (deleted) word, plus every value added into either of them. Because the keys are dependent, the exact rank-one identity `Σ λ_j col_j ⊗ key_j = d ⊗ v` splits into one column equation per basis vector of their span. Each split-key search contains the non-interacting part of PR1957's same-key family as a special case.

The model is first order:

- values and columns are computed on the deleted word;
- an insert that writes register `x` may not precede (or share a position with) an insert that reads `x`;
- candidates are priced by PR1957's frame-cost oracle;
- every proposed solution is re-priced exactly by PR1957's `abkernel.price` (full A+cut+B+tail map, residual-register rule, exact optimal frames).

## Results (`RESULTS.json`, recomputed by `tools/summarize.py`)

**Full A-section relaxation (3,451 gates, all solved).** Gains:

| Deletion gain | Count | Note |
|---:|---:|---|
| −23,583 to −16,589 | 108 | data butterflies |
| −9,826 | 172 | two rank-2 splits |
| −8,857 | 48 | rank-5 split 1\|4; accumulations at A3403–A3450; 40 first priced here |
| −6,763 | 32 | cold-pivot pre-cancels A1215–A1246; 27 first priced here |

The pre-cancels follow the dirty-register read idiom. For example, A1220 `479 −= 527` cancels the stale part of 527 before B818 makes `527 = x527 + x6` and B1038 adds it into 479.

**Strict split-key searches.** Settings: budget |gain| − 1, at most 12 inserts, |λ| ≤ 4 in half steps, CP-SAT. Every kernel-sized deletion in A and B was searched:

- all 32 A pre-cancels;
- all 48 A reads at −8,857;
- B783/B802 (−6,763);
- B1177/1178/1185/1186 (−8,857);
- B822/840/858/876 (−6,100);
- B857/875 (−3,050);
- the 16 one-split reads at −4,913.

Outcome: **all 108 searches are either proven infeasible by CP-SAT (104) or shape-infeasible (4: the −6,100 B reads).** There is no exact profitable kernel.

Four −8,857 jobs (A3439–A3442) first stopped at the 60 s CP-SAT limit under load with status UNKNOWN. They were rerun at 300 s, where infeasibility was proved. Both sets of logs are kept in `data/logs/`. The only exact solutions found are cost-neutral relocations of the deleted read itself; for example, A3403 `60 += 28` moved to the end of A has delta 0.

**Positive control.** On PR1672's pivot-566-only word (`step0-gauge44`), the same search deletes B342 and **rediscovers k554-signed-001 exactly**: the same five inserts, exact delta −1,850. It also finds three other −1,850 variants with six inserts. Flipping one coefficient of the rediscovered kernel makes the exact pricer reject it as inexact.

**Diagnostic.** For B783 and B802, the per-insert oracle cap was loosened to 3× the budget and the summed budget was dropped. Under those settings the only exact compensation within 12 inserts is re-inserting the deleted read itself (delta 0). So for these two reads the obstruction is algebraic, not an artifact of oracle pricing.

## Scope and limitations

- **Base word only.** Every search here uses the base `gauge44-word-566` word, which serves 249 of the 666 T74 calls. The extra word was not searched.
- **First-order model.** Interacting inserts are excluded. When interactions were allowed, the model proposed zero-oracle-cost B783 compensations that were inexact only because of interaction. They are not ruled out as a family.
- **Bounded family.** Searches are limited to one level of keys, at most 12 inserts and |λ| ≤ 4. Multi-deletion kernels are not searched. Neither are the non-kernel-sized deletions: data butterflies, and B delivery reads below −8,857.
- **Finite searches.** These are finite searches of a stated family on fixed words, not a lower bound on the supplier.
- **Pending dependency.** The words and tools come from open PR1957. This branch carries PR1957's commit unchanged, with Rohan Arun's authorship, until it merges. The package is pinned to that commit.

## Reproduce

Generic replay (standard library only, about 1 s): checks pins and recomputes `RESULTS.json`.

```sh
python3 scripts/research_package.py --package research/t74-split-key-kernel-search --check-only
python3.12 scripts/research_package.py --package research/t74-split-key-kernel-search
```

Solver stages (Python 3.11+, NumPy, OR-Tools; times on a 12-core x86-64 machine under load):

```sh
python3 -B research/t74-split-key-kernel-search/verify.py --stage relax      # ~45 s: 12 sampled A deletions re-solved
python3 -B research/t74-split-key-kernel-search/verify.py --stage control    # ~3 min: rediscovers k554-signed-001, tamper rejected
python3 -B research/t74-split-key-kernel-search/verify.py --stage negative   # ~5-7 min: A1215 and B783 re-proved infeasible
```

Full searches:

```sh
OUT_DIR=/abs/out python3 -B research/t74-split-key-kernel-search/tools/skkernel.py \
  research/t74-k554-local-exhaustion/inputs/gauge44-word-566.json.gz '[[["A",1215]],[["B",783]]]' 12 3 60
```

Settings: 12 inserts, 3 solutions, 60 s per solve. Expect about 2 minutes per −6,763 job and about 5 minutes per −8,857 accumulator job.

- Diagnostic runs add `SK_CANDCAP=3 SK_NOBUD=1`.
- The A relaxation reruns PR1957's `tools/relaxAsec.py` on comma-separated index lists; it takes about 3.3 s per gate.
- The search logs are in `data/logs/`, and per-job outputs in `data/{strict,diagnostic,control}/`.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Interacting inserts.** Does an exact profitable kernel exist once inserts may write registers that later inserts read? First step: compute the exact residual of an interacting first-order proposal and compensate it in a second round. Blocked on a residual-repair or bilinear search model.
2. **Extra word.** Does the extra word (417 of the 666 calls) give the same negative answer? First step: rerun the relaxations and B783/B802/A-pre-cancel searches on `extra-word-566`. Blocked only on compute (about 20 minutes of relaxation on 11 cores, plus the searches).
3. **Wider key family.** Can a key family that recurses through registers added into the source or target reach the four shape-infeasible −6,100 B reads? Blocked on candidate-generation speed; the −8,857 jobs already take about 5 minutes with 52 keys.

## Credit

- **Rohan Arun (PR1957):** local-exhaustion toolkit (`abkernel.py`, frame-cost oracle, relaxation drivers), B relaxation data and the A-section sample. All are reused unchanged.
- **PR1186:** exact frame toolkit, as vendored by PR1957.
- **mdumitrean (PR1625):** pivot-566 kernel.
- **jeremykothe2 / LeverRank (PR1672):** pivot-554 kernel, used as the positive control.
- **PR1319/PR1297 lineage:** T74 words.
- **PR1673 (Vlado Vojdanovski):** the outer under which κ ≈ b.

Related negative results on older words: PR1337 and discussion 1314 ran helper-donor kernel censuses on the #1297/#1305 words, before the 566 and 554 kernels, in a restricted family. This package searches the current words with a different, wider compensation family.

Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code), as disclosed in TASK.json. New work is Apache-2.0.
