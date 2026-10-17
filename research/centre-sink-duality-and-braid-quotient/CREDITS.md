# Credits and Provenance

## 1. Pinned Verification Inputs (`SOURCES.json`)

All machine-checked verification inputs read by `verify.py` derive from the six files pinned in `SOURCES.json` at `base_commit = 997e6a9ca7b4f95d50e366f61412fd640d72a88a`:

1. **Selected Certificate (`certificates/selected-result.json`, `#1094`) and Selected Replay Archive (`research/community-frontier1094-audit/selected-replay.tar.gz`):**
   - Supplies the validated selected record $\kappa = 0.001672660197076918$ and the decompressed `split-centres` (`728` roles, `21,483` events) and `hosted` (`gauge44`, `704` roles, `24,767` events) global templates, local words (`LOCAL-PROGRAMS.json.gz`), and `DATA-PHASES.json` Clifford recipes.
   - Credit: Rohan Arun (`#1094`), Jeremy Kothe, Hao Yan, icekylinx, DreamingOfClouds, Douglas Colkitt, Cinna Davis (`1337isnot1337`, `#1708`), Sagar Thakrar (`#1012`), Ryan Haines, Scratch-net, Chafik Boukhalfa, and the retained selected-construction lineage.
2. **Packing-Independent Local-Word Ceiling Solver (`research/complex-local-word-ceiling/ceiling.py` and `RESULT.json`):**
   - Supplies the 256-bit rational interval solver `ceiling.ceiling(centre=...)` and `ceiling.relax(...)` (`a_ceiling = 0.001690054110`, `kappa_ceiling = 0.001687202646`) and the `#1012` coverage-identity framing.
   - Credit: Douglas Colkitt (with AI assistance).
3. **Reverse Centre-Phase Guard Certificate (`research/centre-shared-return-guard/RESULT.json`, `#1748`):**
   - Supplies the pinned two-panel reverse centre-phase bill (`16/368/32` separate vs `8/360/16` fused) and 1-bit positive gather guard (`11/2` per panel), building on Cinna Davis / `1337isnot1337` (`#1708` forward fanout), Sagar Thakrar (`#751` common-target backward batching), Ryan Haines (`#830`), and Scratch-net (`R480`).
   - Credit: `@ToikY` (with AI assistance).
4. **Originating Task Catalogue (`docs/research/agent-task-catalog.json`, revision `6`):**
   - Supplies the `centre-path-sharing` task card under track `recursive-interfaces`.

## 2. Prior Centre-Sharing Formulations, Theorems, and Open Questions Built Upon Here

While `verify.py` computes all matrices and censuses directly from `selected-replay.tar.gz` without importing code from the packages below, this package builds directly on their problem formulations, structural theorems, and open questions:

1. **Two-Stage Cover-Owner Block Repair, Route-Product Uniqueness, and the 50-Edge Braid Graph (`#2391`, `#3071`, `#3097`):**
   - **Aaron Wang (`navinor`, `#2391`)** and **`ywz65` (`research/centre-owner-observation-floor`)** formulated the native centre-reuse question, the two-stage block-repair equation $\ker S \cap \ker T$, and the $104|B|$ owner-local observation floor.
   - **Ross Richardson (`#3071`, `research/centre-block-repair-information`)** proved the uniqueness of all $112 \times 111 = 12,432$ ordered route products $\rho_p \rho_q$ ($p \neq q$) — establishing $C_4$-freeness of the bipartite repair incidence graph — and proved the $104|B|$ floor for $|B| \le 6$.
   - **`Gonzalo-Mier` (`#3097`, `research/centre-seven-owner-information-floor`)** identified the `50` order-3 braid edges $(\rho_p \rho_q)^3 = I$ as the unique mechanism generating 6-cycles in the bipartite repair incidence graph and proved the $|B| = 7$ Fano exclusion.
   - **New here (Pillar 3):** Intersects the `896` linearly dependent column triples of the $8 \times 112$ cut matrix $R$ with the `50` order-3 braid edges to prove the **Dependent-Triple Braid Sparsity Theorem** (`846` dependent triples contain `0` braid edges, `50` contain `1` braid edge, and `0` contain $\ge 2$ braid edges), showing that every degree-3 vertex lies in at most `1` six-cycle and closing $7 \le |B| \le 12$ (`|B| >= 13`).
2. **Charged $k$-Call Shared-Centre Relaxation, Overhead Budgets, and Schedule Lookup (`#3075`, `#3120`):**
   - **Aaron Wang (`navinor`, `#3075`, `research/centre-shared-kcall-charged-seed615415`, and open PR `#3120`, `research/centre-demand-rank-floor`)**, **`rtyu193-rgb` (`research/centre-sharing-overhead-budget`)**, `research/idle-axis-hosting`, and `research/p112-batch-centre-floor` formulated the charged $k$-call displace/additive relaxation models, posed the open physical 144-call sink-sharing and demand-coupling questions answered in Pillars 1–2, and reported the `16 present / 1,136 missing` `S_split` schedule-lookup scan whose positional-vs-global owner indexing resolution (`1,152 / 1,152` resolved) is given in Pillar 1.
3. **Clifford Route-Involution Extraction and Forward/Backward Quarter Identity (`#2199`, `#1918`, `#2048`):**
   - **Sagar Thakrar (`#2199`, `frontier1094-recipes-exact-seed76`)**, **Adam Gall (`#1918`)**, **`commdata2338` (`#2048`)**, and **Aaron Wang (`navinor`, `research/selected-centre-quarter-native`)** established the `DATA-PHASES.json` Clifford route-involution extraction and the scalar `-1/4` forward/backward centre relationship on data ports `0..111`.
   - **New here (Pillars 2 & 4):** Generalizes that relationship to three exact 704-role forward/backward local cut/response duality laws across all 704 local registers (including the 115 active helpers) and proves the chronological Replica 0 $(F_0 \to B_1 \to F_2)$ pre-centre demand cancellation (`rank_D0_f2 = 0`) and Stage-8 zero-feedback circle ceiling brackets.

## 3. Package Authorship and License

- **New here (`dcharb78`, with AI assistance):** Pillar 1 (`1,152 / 1,152` positional sink resolution across `split-centres` and `hosted` `gauge44` into 5 Data Sinks + 3 Helper Sinks), Pillar 2 (three exact 704-role forward/backward duality laws and the `10,296`-pair Two-Regime Dichotomy identifying the `96` same-replica shared-data pairs), Pillar 3 (Dependent-Triple Braid Sparsity Theorem closing $7 \le |B| \le 12$), Pillar 4 (chronological $(F_0 \to B_1 \to F_2)$ circle cancellation, Stage-8 zero-feedback circle, and 13-row `ceiling.ceiling(centre=...)` stratification), and the 8 behavioral negative controls in `verify.py`.
- **License:** Apache-2.0.
