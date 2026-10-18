# Centre-source rank census for dependent selected-call pairs (PR2048 open question 2)

**Status:** research note and scoped negative result. This is a finite certificate in a declared scalar
projection. It is not a native obstruction, not a formal proof and not a new kappa. The selected frontier
is unchanged.

## Question

PR1918 found that one forward pair with disjoint data (selected calls time 0 and time 1) has stacked
centre-source rank 16. It also gave a scoped linear-transcript lemma: sharing needs d >= rank. PR2048 lifted
that pair to native frames. Its open question 2 asks about pairs whose sources depend on each other in time.

This package replays all 144 selected `local_cover_sweep` calls in the same projection. It asks two things:

- Do pairs that share source owners, or that pass data from one call to a later one, have rank below 16?
- What is the rank of all 1,152 centre-source rows?

## Projection (inherited from PR1918, extended to every call)

- **Scalar operations.** `clear`, `copy`, `scale` and `add` are exact over Q. `climb`, `adapter` and
  `residual_adapter` act as the identity. The `center` event is the read cut.
- **Calls only.** The calls run in `execution_schedule` order from a formal initial vector with one
  independent variable per physical owner (14,336 owners). The 144 `bridge` events, 160
  `idle_cover_sweep` events, terminal events, bank padding and translate are **not executed**. For every
  dependent pair, the receipt counts the bridge and idle events between the two calls on their replicas.
- **Centre-source rows.** Row k is the value of private register `C_k` at its rank-8 `center` event.
  - Forward: the centre copies `L[word.centers[k]]`. The verifier checks that these 8 copies are
    `C_k <- L[92,57,81,224,11,240,9,256][k]` and that each row equals PR1918's phase-start cut.
  - Backward: the centre gathers 56 target-role terms, with coefficients +1/4 or -1/4.
- **Composition per orientation.** Each orientation gets one exact local replay over 704 roles. The
  verifier checks clean private exit and these exact endpoints:
  - forward: `L_i += L_{i-112}` for 112 <= i < 224;
  - backward: `L_i -= L_{i+112}` for 0 <= i < 112.

  Every call is bound to its program through `local_program_sha256`.

## Results

1. **Global rank 1152/1152.** This holds exactly over Q and also mod 2^61-1. The forward rows (80 calls)
   have rank 640 and the backward rows (64 calls) have rank 512.

   So in this projection, no centre-source row of any call is a linear combination of other calls' rows.
   This is a statement about the formal rows only. It does **not** by itself give PR1918's lemma bound
   (d >= rank) for groupings of calls. That lemma needs the output-increment rank with initial target
   and helper dirt held fixed, on separate output panels. This package computes neither the fixed-dirt
   source-only rank nor panel separation. A reviewer found that the centre-scatter destination panels
   do overlap: for example, f0->f2 pairs share all 88 destination owners.

2. **Every dependent pair has rank 16 (1,539 pairs).**

   | Dependency class | Pairs |
   |---|---:|
   | Share roles 0..111 owners (all 112 of them) | 96 |
   | Earlier write is read later, roles 0..223 (same 96 pairs) | 96 |
   | Share a formal support variable | 1,525 |

   By orientation: 1,141 forward-forward, 259 backward-forward and 139 forward-backward. Every pair also
   has rank 16 when restricted to the formal variables of its own roles 0..223 owners. **The null
   expectation holds, and no deficient pair exists in the declared projection.**

   The 96 shared-data pairs are exactly six classes of 16 same-replica pairs: f0->b1, b1->f2, b3->f4,
   b5->f6, b7->f8 and f0->f2.

3. **The roles 0..111 block restriction is not robust for dependent pairs.** PR1918 also reported the
   rank of its pair restricted to the formal variables of roles 0..111. For two forward calls these are
   the source-data blocks. For a backward call, roles 0..111 are the block the call *writes* (its target);
   it reads roles 112..223. So for pairs that include a backward call this restriction is **not** a
   source-data statistic. It is reported here only as the same column restriction PR1918 used.

   On this restriction, 671 of the 1,539 dependent pairs have rank below 16:

   | Rank on roles 0..111 variables | Pairs |
   |---:|---:|
   | 16 | 868 |
   | 9..15 | 89 |
   | 8 | 501 |
   | 1..7 | 30 |
   | 0 | 51 |

   All 96 shared-data pairs have rank 8 here, in all six classes (f0->b1, b1->f2, b3->f4, b5->f6,
   b7->f8, f0->f2). The other 575 pairs below 16 are shared-support-only pairs. A generic composition
   effect explains much of this: f0 does T += D and b1 then does D -= T, so after both calls the D owners
   hold -T_orig. Restricting to owner variables then drops later calls' dependence on their own data.
   `roles_0_111_block_rank_by_dependency_class` in RESULT.json gives the breakdown.

   **Certified exact identity, forward0 -> backward1 only.** For the 16 same-replica f0->b1 pairs, both
   calls use the same 224 owners and no bridge or idle event touches the replica between them. The
   verifier checks, for every k and every replica:

   `backward1 centre k |_D = (1/4) * forward0 centre k |_D`

   It also checks that the forward-0 centre reads no target-block variable, and that backward-1 restricted
   to T has rank 8. RESULT.json stores exact left-kernel witnesses for the rank-8 restriction, checked by
   direct evaluation. The b7->f8 class also has no intervening unmodelled event; its rank on this
   restriction is 8 too, but no identity is certified for it.

   **This is not a reuse lead on its own.** The rank drops to 8 only when the target block *and* every
   helper and other owner are zeroed. The verifier checks that zeroing only the target-block variables,
   with helpers and other owners left formal, keeps rank 16 for all 16 f0->b1 pairs. The reason is that
   the forward-0 centre copies helper roles too (`word.centers` includes roles 224, 240 and 256), so it
   reads helper contents that the backward-1 centre does not. An independent reviewer replay, not part of
   this verifier, also found rank 16 when T is set to a shift of D with helpers left formal.

4. **Sensitivity diagnostics.** These are *not* the template's semantics, and are reported only to
   show which assumptions the full rank rests on.
   - Zero every owner first touched in a helper role (>= 224). The global rank drops to 570. 55 calls
     have all-zero rows, including every backward call in stages 3, 5 and 7.
   - Zero every owner not first touched in roles 0..111. The global rank drops to 418.

   In the native schedule, the omitted bridge and idle events carry data into these owners, so these
   collapses are expected projection effects. They show that the full-rank result depends on owner
   contents that the calls-only projection does not model.

## Reproduce

From the repository root, standard library only. It takes about 30 s and under 200 MB of peak RSS.
It has been run only under Python 3.14.4:

```sh
python3 -I -B research/selected-centre-chrono-source-census/verify.py
```

Expected output, as one line:

```text
PASS_SELECTED_CENTRE_CHRONO_SOURCE_CENSUS calls=144 rows=1152 global_rank_q=1152 global_rank_mod_p=1152 dependent_pairs=1539 formal_pair_rank_hist={'16': 1539} pair_local_rank_hist={'16': 1539} deficient_formal_or_pair_local=0 f0_b1_same_block_data_only_ranks=[(8, 16)] f0_b1_target_zeroed_ranks=[(16, 16)] controls=8
```

The package hook below declares Python 3.12. It has **not** been run, because Python 3.12 was not
available. Only the direct command above was checked:

```sh
python3 scripts/research_package.py --package research/selected-centre-chrono-source-census
```

## Controls (each must fail or change the receipt)

**Internal controls, run on every verification:**

- Reproduce PR1918: its 16 source maps match exactly, with rank 16 and data-only rank 16.
- Duplicated rows give rank 8.
- Reversed-order rows give rank 8.
- The forward centre copies equal `word.centers`.
- Perturbing one phase-A `add` coefficient in the backward program changes the program binding and
  changes or rejects the local map.
- Omitting one backward centre gather `add` changes the centre input.
- Omitting the final private `clear` is rejected as a dirty exit.
- Flipping one bit in the archive or in a member changes its SHA256. This is only a hash-sensitivity
  check; rejection by the loader is shown by the external controls below.
- rank mod p never exceeds rank over Q.

**External controls, run in a scratch copy on 2026-10-14:**

| Change | Result |
|---|---|
| None (clean copy) | PASS |
| `global_rank_q` edited in RESULT.json | `result receipt differs` |
| One byte of the archive copy flipped | `pin mismatch: ...selected-replay.tar.gz` |
| PR1918 `source_rank` edited | `pin mismatch: ...selected-centre-composed-source-rank/RESULT.json` |
| One kernel-witness coefficient changed from `-1/4` to `-1/2` | `result receipt differs` |

## Sources and pins

- **Base commit:** `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- **Archive:** `research/community-frontier1094-audit/selected-replay.tar.gz`, sha256
  `f1da8061...d529d6`. The members are pinned in verify.py: GLOBAL-TEMPLATE `2acf02b4...7760`,
  LOCAL-PROGRAMS `241fde27...ef3a` and CANONICAL-WORD `16bc0ebb...d219`.
- **Selected record:** `certificates/selected-result.json`, sha256 `10b9e340...fa32`.
- **PR1918 receipt:** `research/selected-centre-composed-source-rank/RESULT.json`, sha256 `31555505...a668`.

Full digests and Git blobs are in [SOURCES.json](SOURCES.json). Program digests are bound per call:
forward `071ecdac...`, backward `f36c5831...`.

## Scope, inherited assumptions, unresolved obligations

- **Inherited assumptions.**
  - PR1918's scalar projection: frames, adapters, residual adapters and climbs act as the identity.
  - The centre event is the read cut.
  - Physical owners carry independent formal values before the first call.
- **Not executed.** Bridges, idle cover sweeps, terminal events, padding and translate. Rank under the
  native schedule is **not** certified. The native schedule inserts bridge and idle maps between calls;
  it is not a specialization of these formal variables. The full-rank statements could therefore fail
  natively, and the deficient restricted statistics could be higher or lower natively.
- **Unresolved.**
  - A native lift (PR2048-style) of any of these statements.
  - A fixed-dirt, source-only output-increment rank with panel separation, which PR1918's lemma needs
    before any bound on groupings of calls can be stated.
  - Persistent-storage, transport, restoration, hosting and precision invoices for any reuse.
- No kappa follows from any outcome here.

## Open next questions

These are also listed in [TASK.json](TASK.json).

1. **Execute bridges and idle sweeps.** Do the conclusions hold when bridges and idle sweeps run at owner
   level?
   - *Why it matters:* the full rank depends on owner contents that these events change (result 4).
   - *First step:* derive the owner-level scalar semantics of one bridge from `route_semantics` and
     DATA-PHASES, then replay replica 0, stages 0-2.
   - *Blocker:* these events are pair- and family-level, and the frame data is outside this projection.
2. **Fixed-dirt source rank for groupings.** What is the source-only output-increment rank of a group of
   calls, with initial target and helper dirt held fixed, and are its output panels separate?
   - *Why it matters:* only that quantity feeds PR1918's lemma (d >= rank). The formal full rank here
     does not imply a lower bound for groupings, and the centre-scatter panels of some pairs overlap.
   - *First step:* for the 16 f0->f2 pairs (shared 88 destination owners), compute the output-increment
     map from the source block only and its rank.
   - *Blocker:* the source/dirt split must be defined per orientation (D for forward, T for backward).
3. **Native lift of the 1/4 identity.** Does the `(1/4)` D-part identity lift to native 512-address
   frames?
   - *Why it matters:* the identity only holds on the D block. The full rows stay rank 16 even with T
     zeroed, because forward-0 also reads helper contents. Any reuse would still need storage, transport,
     restoration, hosting and precision fully priced.
   - *First step:* apply PR2048's native lift to calls 0 and 4.
   - *Blocker:* native centre semantics.

## Credit and overlap

- **Projection, replay logic and lemma:** PR1918 (Adam Gall,
  `research/selected-centre-composed-source-rank`). This package reimplements its replay with credit and
  pins its receipt.
- **Open question 2:** open PR2048 (commdata2338).
- **Related work:**
  - Early-fanout and zero-storage test: PR2076 and Discussion #2058 (1337isnot1337). The census claimed
    there was abandoned and never run.
  - Owner-aliasing census: PR1829 (Cinna Davis).
  - Nonadjacent owner aliasing: Discussion #1963.
  - Sharing budgets: PR1708 (1337isnot1337), PR1748 (ToikY), PR1791 (rtyu193-rgb), PR1664 (An664) and
    merged PR1888 (RossRichardson, mixed-rank centre-sharing overhead limits).
  - Same f0/b1 stage-pair data boundary, studied as an F2 frame intersection: Discussion #1986
    (1337isnot1337).
- **Selected construction:** the #1094 lineage (Rohan Arun et al.; see `certificates/selected-result.json`).
- **Review:** three independent AI-assisted reviews in this session (reproducibility, mathematical
  audit, provenance). The audit corrected the interpretation of results 1 and 3.
- **Concurrent idea:** a sibling local session drafted a similar census card and aborted it. Nothing was
  reused.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
