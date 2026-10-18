# P104 Pooled One-Hop Transitivity Obstruction, Cycle-Matching Refutation, and Complete 9-Stage Physical Consumer Bill

## Status and Selected Benchmark Disclosure

- **Priority Card:** `p104-side-correction` (`complex-mechanisms`, weight `20`) in `docs/research/current-priorities.md` and `docs/research/agent-task-catalog.json`.
- **Selected Repository Record:** `certificates/selected-result.json` remains unchanged at $\kappa_{\text{selected}} = 0.001672660197076918$ (`836330098538459 / 500000000000000000`, `no_new_kappa = true`), derived from the complex local exponent $a_{\text{complex}} = 0.0016754626768081035$ (conservative lower enclosure `0.0016754626739466284`, prompt benchmark $b_{\text{selected}} = 0.001675460322$, bit-side benchmark $c_{\text{bit}} = 0.0017334270395898442$).
- **Base & Ancestor Intake Status:** PR `#1991` (`research/p104-native-channel`) has intake status `partially_reviewed` and reports (author-checked) the 4,058-step rank-`2,368` native P104 channel word and its residual cross-Gram target $C = I_{104} - G_{104}/2$ (`4,992` nonzero off-diagonal entries of $\pm 1/2$). PR `#2981` (`research/p104-joint-unit-flags`), PR `#2996`, PR `#3013`, PR `#3019` (`research/p104-coherent-support-witness`), PR `#3038` (`research/p104-fixed-matching-flag-consistency`), PR `#2920` (`research/p104-endpoint-geometric-budget`), PR `#2924` (`research/p104-two-history-lifetime-floor`), PR `#2953` (`research/p104-joint-endpoint-obstruction`), PR `#2741` (`research/p104-consumer-budget-audit`), and PR `#2819` (`research/p104-all-pair-consumer-budget`) have intake status `merged_for_archive_only` and report (author-checked) static endpoint covers, matchings, single-helper flag censuses, and consumer budget bounds.
- **Pinned Verification Inputs vs. External Comparator:** All runtime inputs are pinned verification inputs in `SOURCES.json` at `base_commit = 997e6a9ca7b4f95d50e366f61412fd640d72a88a`. Open PR `#3124` (`p104-cycle4-unit-flags-seed6501` / `p104-alternating-cycle-neighborhood`) is cited strictly as an external comparator (`report (author-checked)`, not read at runtime); its two 4-cycle matchings (`[13, 203, 191, 63]` and `[39, 154, 139, 134]`) are reconstructed directly from pinned `research/p104-coherent-support-witness/CONTROL.json`.

---

## Executive Summary of the Four Unified Pillars

This standalone verification package resolves four tightly coupled structural and budgetary questions for the P104 side-correction channel (`p104-side-correction`):

1. **Pillar 1 — Universal `2,309`-Edge Pooled Intralayer-Transitivity Obstruction:**
   Across the entire `2,309`-edge compatibility graph $\mathcal{E}_{\text{compat}} = \{(a,b) \in \{0,\dots,207\}^2 : A_a \subseteq B_b\}$ of PR `#2981`'s static departure/arrival cover (`CERTIFICATE.json`)—which pools every possible 208-edge perfect matching simultaneously—replacing PR `#2996`'s transitive connected-component closure with 1-hop-per-dimension equal-frame transitivity ($F_{u,d} = F_{w,d}$ requires $(u,w) \in R_d$) leaves `1` required nonzero entry of $C = I_{104} - G_{104}/2$ unreachable: 0-based `(71,102)` (`(Y71, X102)`, 1-based `(72,103)`), where $C_{71,102} = \text{`-1/2`}$. The forward reachability cone of `X102` through Dimension `5` (`1,725` edges) and the backward reachability cone of `Y71`'s `12` Dimension-`8` cap writers through Dimension `6` (`37` edges) have empty intersection (`1,725` $\cap$ `37` = `0`).

2. **Pillar 2 — Direct Refutation of Open PR `#3124`'s Cycle Matchings on Their Own Moved Cycle Vertices:**
   Open PR `#3124` reports (author-checked) a 4-cycle modification `[13, 203, 191, 63]` of PR `#3013`'s matching (`CONTROL.json`) on which fixed helper `91` has `33` / `9,765` passing flags in isolation (`min_missing = 0`). Running the exact `9,765`-flag single-helper consistency census on the moved cycle vertices themselves demonstrates that:
   - Moved cycle vertex `13` (rematched edge `13 -> 180`) has **`0` / `9,765` passing flags** (`min_missing = 1002`, `max_missing = 1026`, histogram `{1002: 225, 1020: 477, 1023: 477, 1025: 117, 1026: 8469}`). All `12` / `12` ordered distinct intermediate neighbor pairs $(u, w)$ from $\{63, 91, 118, 185\}$ violate $A_u \subseteq B_{b(w)}$.
   - Moved cycle vertex `63` (rematched edge `63 -> 185`) also has **`0` / `9,765` passing flags** (`min_missing = 481`, `max_missing = 992`, histogram `{481: 27, 913: 54, 950: 66, 968: 360, 972: 132, 992: 9126}`), whereas moved cycle vertices `203` (`477` passing) and `191` (`225` passing) pass only when `13` and `63` are left relaxed.
   - On the secondary 4-cycle `[39, 154, 139, 134]`, all four moved edges (`(39, 186)`, `(154, 7)`, `(139, 23)`, `(134, 150)`) have `9,765` valid nested flags between $A_a$ and $B_b$, yet helper `91` and all four moved vertices (`39`, `154`, `139`, `134`) fail single-helper consistency with **`0` / `9,765` passing flags** (`min_missing = 91`).

3. **Pillar 3 — Cross-Dimension Subspace-Memory Propagation Obstruction Across All Five Matchings:**
   A valid nested flag $A_h = F_{h,2} \subset F_{h,3} \subset F_{h,4} \subset F_{h,5} \subset F_{h,6} \subset F_{h,7} = B_{b(h)}$ cannot discard the subspace $A_u \subseteq F_{h,d_1}$ acquired at dimension $d_1$ when advancing to $d_2 \ge d_1$: it requires $A_u \subseteq F_{h,d_1} \subseteq F_{h,d_2} \subseteq B_{b(w)}$. Enforcing either 1-step or full cross-dimension subspace memory leaves **`4,781` of `4,992` required pairs missing** on PR `#2981` (`145` helpers with zero intermediate relay pairs) and **`4,783` of `4,992` required pairs missing** on PR `#3013` (`117` zero-relay helpers), PR `#3019` (`116` zero-relay helpers), PR `#3124_A` (`117` zero-relay helpers), and PR `#3124_B` (`122` zero-relay helpers)—leaving only `209` (or `211`) pairs reachable.

4. **Pillar 4 — Complete 9-Stage Physical Consumer Bill & Dual-Endpoint Boundary Untangling Frontier:**
   Evaluating the hosted 9-stage consumer (`m = 73`, `families = 832`, `stages = 9`, $w = \text{`832/9`}$, `centre_per_call = 56`, `total_paid_mass_per_call = 6712`, `base_local_mass_per_call = 2368`, `base_idle_mass_per_call = 4344`, `max_idle_rank_R = 51`) across all `7` helper dirty-restoration profiles and `4` dual-endpoint boundary conversion regimes proves that under true non-persistent dual accounting (**Mode A**, where zero-displacement dual boundary conversions add $\frac{4}{9}\Delta M_{\text{dual}}$ to per-call centre charge without reducing required persistent idle progress):
   - A 208-unit $H_9$ helper cover (`1,872` dirty rank-units/call, `2,472` idle rank-units/call) can tolerate at most **`16.639481` uncredited $H_1$ per dual call** at $b_{\text{selected}} = 0.001675460322$ (`16.748279` at $\kappa_{\text{selected}}$, `14.387536` at $c_{\text{bit}}$).
   - Even dual private zero/erasure alone (`8` $H_7 = 56$ rank-units/dual call) fails at $b_{\text{selected}}$ (`1.002598847 > 1`), and both the 5-boundary fused dual schedule (`260` $H_1 + 8$ $H_7 = 316$ rank-units/dual call, moment `1.019845668 > 1`) and the full physical 8-boundary corrected dual schedule (`416` $H_1 + 8$ $H_7 = 472$ rank-units/dual call, moment `1.030193762 > 1`) are strictly rejected.
   - Coarsening `11`, `26`, or `179` of the `208` unit helpers into higher-rank jumps (`197` units + `11` cheap $(1,7,1)$ helpers, `182` units + `26` $(1,8)$ jumps, or `29` units + `179` $(1,8)$ jumps, each keeping `1,872` dirty rank-units/call) slightly relaxes the idealized `0`-dual moment (`0.99885883`, `0.998788267`, `0.998152901`) and raises the dual $H_1$ break-even to `17.203407`, `18.267166`, and `27.845467`—**yet all three still fail ($M > 1$) as soon as the 4 dual calls' `+8 H7` private collector zero-erasure is charged (`1.002561439`, `1.002490876`, `1.00185551 > 1`)**.

---

## Pillar 1: Universal `2,309`-Edge Pooled Intralayer-Transitivity Obstruction

### Theorem 1 (Pooled Compatibility Graph One-Hop Obstruction)

Let $\mathcal{E}_{\text{compat}} = \{(a,b) \in \{0,\dots,207\}^2 : A_a \subseteq B_b\}$ be the complete `2,309`-edge compatibility graph of PR `#2981`'s static departure planes $A_a$ ($\dim = 2$) and arrival hyperplanes $B_b$ ($\dim = 7$). Because frame equality at a single dimension $d \in \{1,\dots,8\}$ is an equivalence relation ($F_{u,d} = F_{v,d}$ and $F_{v,d} = F_{w,d} \implies F_{u,d} = F_{w,d}$), any multi-helper relay within dimension $d$ on shared frame $V$ requires a direct 1-hop edge $(u,w) \in R_d$.

Under 1-hop-per-dimension propagation on the pooled `2,309`-edge graph $\mathcal{E}_{\text{compat}}$:
- **PR `#2996` transitive connected components (negative control):** `0` missing pairs out of `4,992`.
- **1-hop equal-frame transitivity ($F_{u,d} = F_{w,d}$):** `1` missing pair out of `4,992`, namely 0-based `(71,102)` (`(Y71, X102)`, 1-based `(72,103)`), with required cross-Gram entry $C_{71,102} = \text{`-1/2`}$.

### Exact Reachability Cone Disjointness Proof for `(71,102)` (`C[71, 102] = -1/2`)

- **Source `X102` readers:** `X102` is read only at Dimension `1`, by the `16` compatibility edges incident to departure slots `204` (`7` edges: `(204, 16)`, `(204, 18)`, `(204, 88)`, `(204, 90)`, `(204, 115)`, `(204, 121)`, `(204, 187)`) and `205` (`9` edges: `(205, 82)`, `(205, 87)`, `(205, 117)`, `(205, 119)`, `(205, 149)`, `(205, 150)`, `(205, 180)`, `(205, 194)`, `(205, 207)`).
- **Target `Y71` writers:** `Y71` is written only at Dimension `5` (`2` edges: `(41, 135)` and `(131, 135)`) and Dimension `8` (`12` edges ending at arrival slots `142` and `143`: `(41, 143)`, `(43, 143)`, `(54, 143)`, `(131, 143)`, `(135, 143)`, `(145, 143)`, `(146, 142)`, `(149, 142)`, `(155, 143)`, `(159, 143)`, `(171, 143)`, `(194, 143)`).

| Dimension $d$ | `X102` Forward Cone Size (out of `2,309`) | `Y71` Writer Edges at Dim $d$ | `Y71` Writer Hits by `X102` Forward Cone | `Y71` Dim-`8` Backward Cone Size |
| :---: | :---: | :---: | :---: | :---: |
| `1` | `16` | `0` | `0` | — |
| `2` | `25` | `0` | `0` | — |
| `3` | `52` | `0` | `0` | — |
| `4` | `365` | `0` | `0` | — |
| `5` | `1,725` (`1725`) | `2` | `0` | — |
| `6` | `2,283` (`2283`) | `0` | `0` | `37` (after Dim `6`) |
| `7` | `2,285` (`2285`) | `0` | `0` | `22` (after Dim `7`) |
| `8` | `2,297` (`2297`) | `12` | `0` | `12` (after Dim `8`) |

- At Dimension `5`, neither of `Y71`'s `2` writers (`(41, 135)`, `(131, 135)`) lies in `X102`'s `1,725`-edge forward cone (`0` hits).
- Backward from `Y71`'s `12` Dimension-`8` writers, the 1-hop backward cone has size `12` after Dimension `8`, `22` after Dimension `7`, and `37` after Dimension `6`.
- The intersection between `X102`'s `1,725`-edge forward cone after Dimension `5` and `Y71`'s `37`-edge backward cone before Dimension `6` is identically **`0` edges**. Because every 208-edge perfect matching is a subgraph of $\mathcal{E}_{\text{compat}}$, **no perfect matching of PR `#2981`'s covers can route `(71,102)` (`(72,103)`) under 1-hop-per-dimension equal-frame transitivity**.

---

## Pillar 2 & Pillar 3: Refutation of Open PR `#3124` on Moved Cycle Vertices and Subspace-Memory Propagation

### Propagation Summary Across All Five Matchings (`4,992` Required Support Pairs)

| Matching Name | PR `#2996` Transitive Components Missing | 1-Hop Equal-Frame Missing | 1-Step Subspace Memory Missing | Full Subspace Memory Missing | Helpers with `0` Valid Intermediate Relay Pairs (out of `208`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `PR2981_baseline` (`CERTIFICATE.json`) | `3,095` (`3095`) | `4,242` (`4242`) | `4,781` (`4781`) | `4,781` (`4781`) | `145` |
| `PR3013_rematched` (`CONTROL.json`) | `45` | `3,889` (`3889`) | `4,783` (`4783`) | `4,783` (`4783`) | `117` |
| `PR3019_witness_swap_91_189` (`WITNESS.json`) | `0` | `3,881` (`3881`) | `4,783` (`4783`) | `4,783` (`4783`) | `116` |
| `PR3124_cycle_A_13_203_191_63` | `0` | `3,876` (`3876`) | `4,783` (`4783`) | `4,783` (`4783`) | `117` |
| `PR3124_cycle_B_39_154_139_134` | `91` | `3,898` (`3898`) | `4,783` (`4783`) | `4,783` (`4783`) | `122` |

### Exact `9,765`-Flag Single-Helper Census on Open PR `#3124`'s Moved Cycle Vertices

| Matching / Cycle | Helper Slot | Matched Edge $(a, b)$ | Total Full Flags | Distinct Contact Profiles | Passing Flags (`0` Missing) | Minimum Missing Pairs | Maximum Missing Pairs | Missing-Pairs Histogram |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `PR3124_cycle_A` `[13, 203, 191, 63]` | `91` (unmoved) | `(91, 8)` | `9,765` (`9765`) | `18` | `33` | `0` | `46` | `{0: 33, 45: 444, 46: 9288}` |
| `PR3124_cycle_A` `[13, 203, 191, 63]` | **`13` (moved)** | `(13, 180)` | `9,765` (`9765`) | `22` | **`0`** | **`1,002` (`1002`)** | `1,026` (`1026`) | `{1002: 225, 1020: 477, 1023: 477, 1025: 117, 1026: 8469}` |
| `PR3124_cycle_A` `[13, 203, 191, 63]` | `203` (moved) | `(203, 12)` | `9,765` (`9765`) | `19` | `477` | `0` | `44` | `{0: 477, 44: 9288}` |
| `PR3124_cycle_A` `[13, 203, 191, 63]` | `191` (moved) | `(191, 188)` | `9,765` (`9765`) | `7` | `225` | `0` | `46` | `{0: 225, 43: 252, 46: 9288}` |
| `PR3124_cycle_A` `[13, 203, 191, 63]` | **`63` (moved)** | `(63, 185)` | `9,765` (`9765`) | `20` | **`0`** | **`481`** | `992` | `{481: 27, 913: 54, 950: 66, 968: 360, 972: 132, 992: 9126}` |
| `PR3124_cycle_B` `[39, 154, 139, 134]` | `91` (unmoved) | `(91, 8)` | `9,765` (`9765`) | `7` | **`0`** | **`91`** | `92` | `{91: 477, 92: 9288}` |
| `PR3124_cycle_B` `[39, 154, 139, 134]` | **`39` (moved)** | `(39, 186)` | `9,765` (`9765`) | `21` | **`0`** | **`91`** | `91` | `{91: 9765}` |
| `PR3124_cycle_B` `[39, 154, 139, 134]` | **`154` (moved)** | `(154, 7)` | `9,765` (`9765`) | `13` | **`0`** | **`91`** | `91` | `{91: 9765}` |
| `PR3124_cycle_B` `[39, 154, 139, 134]` | **`139` (moved)** | `(139, 23)` | `9,765` (`9765`) | `4` | **`0`** | **`91`** | `91` | `{91: 9765}` |
| `PR3124_cycle_B` `[39, 154, 139, 134]` | **`134` (moved)** | `(134, 150)` | `9,765` (`9765`) | `1` | **`0`** | **`91`** | `91` | `{91: 9765}` |

### Explicit `12`-Pair Algebraic Proof for Moved Cycle Vertex `13` (`(13, 180)`) on `PR3124_cycle_A`

On `PR3124_cycle_A`, helper `13` ($A_{13} = \text{span}(36, 288) \subseteq B_{180}$) has exactly `4` intermediate-dimension (`d = 3..6`) contact neighbors: `63`, `91`, `118`, and `185`. For helper `13` to relay any signal from neighbor $u \in \{63, 91, 118, 185\}$ at dimension $d_1$ to a distinct neighbor $w \in \{63, 91, 118, 185\} \setminus \{u\}$ at dimension $d_2 \ge d_1$, nested flag monotonicity requires $A_u \subseteq F_{13,d_1} \subseteq F_{13,d_2} \subseteq B_{b(w)}$. Across all `12` ordered pairs $(u, w)$:
- From `u = 63` ($A_{63} = \text{span}(31, 288)$): vector `31` $\notin B_{8}$ (`w = 91`), `31` $\notin B_{131}$ (`w = 118`), `31` $\notin B_{141}$ (`w = 185`).
- From `u = 91` ($A_{91} = \text{span}(2, 424)$): vector `2` $\notin B_{185}$ (`w = 63`), `2` and `424` $\notin B_{131}$ (`w = 118`), `424` $\notin B_{141}$ (`w = 185`).
- From `u = 118` ($A_{118} = \text{span}(178, 365)$): vectors `178, 365` $\notin B_{185}$ (`w = 63`), `178` $\notin B_{8}$ (`w = 91`), `178, 365` $\notin B_{141}$ (`w = 185`).
- From `u = 185` ($A_{185} = \text{span}(253, 288)$): vector `253` $\notin B_{185}$ (`w = 63`), `253` $\notin B_{8}$ (`w = 91`), `253` $\notin B_{131}$ (`w = 118`).

Thus all `12` / `12` ordered distinct neighbor pairs are algebraically incompatible, forcing `0` / `9,765` passing flags and at least `1,002` missing pairs across the `104` targets.

---

## Pillar 4: Complete 9-Stage Physical Consumer Bill & Dual-Endpoint Boundary Untangling Frontier

### Consumer Parameters (`ceiling.py` Model)

- Outer scale: `m = 73`, live data families per replica: `families = 832`, consumer invocations: `stages = 9`, live families per call: $w = \text{`832/9`}$, halving-guard idle rank cap: `max_idle_rank_R = 51`.
- Base native channel per call: `base_local_mass_per_call = 2368` (`2,312` persistent progress + `56` from `8` $H_7$ centre paths), `centre_per_call = 56`, `total_paid_mass_per_call = 6712`, `base_idle_mass_per_call = 4344`.
- **Mode A (True Non-Persistent Dual Accounting):** Dual-endpoint boundary conversions and dual private zero/erasure have net frame displacement `0` across the `832` families and add $\frac{4}{9}(\Delta H_1 + 7\Delta H_7)$ to the per-call centre charge without reducing the required $4,344 - M_{\text{dirty}}$ persistent idle progress mass.
- **Mode B (Favorable Persistent-Credit Relaxation):** Generously credits zero-displacement dual boundary conversions as if they replaced rank-`51` persistent idle mass.

| Helper Dirty-Restoration Profile | Unit $H_9$ Helpers | Extra Dirty Jumps $(n, r)$ | Dirty Mass / Call | Idle Mass / Call | Max Uncredited Dual $H_1$/Dual (Mode A at $b_{\text{selected}}$) | Ideal `0`-Dual Moment ($b_{\text{selected}}$) | Dual `8` $H_7$ Only Mode A ($b_{\text{selected}}$) | Fused `260` $H_1 + 8$ $H_7$ Mode A ($b_{\text{selected}}$) | Full `416` $H_1 + 8$ $H_7$ Mode A ($b_{\text{selected}}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `PR2920_endpoint_only_0_units` | `0` | `[]` | `0` | `4,344` (`4344`) | `44.295334` | `0.997061716` | `1.000764325` | `1.018011147` | `1.02835924` |
| `PR2981_unit_cover_208_units` | `208` | `[]` | `1,872` | `2,472` | **`16.639481`** | `0.998896238` | **`1.002598847`** | **`1.019845668`** | **`1.030193762`** |
| `PR2924_two_history_216_units` | `216` | `[]` | `1,944` | `2,400` | `15.575794` | `0.998966796` | `1.002669405` | `1.019916227` | `1.03026432` |
| `Coarsened_11_helpers_197_units_11_cheap_1_7_1` | `197` | `[(22, 1), (11, 7)]` | `1,872` | `2,472` | `17.203407` | `0.99885883` | **`1.002561439`** | `1.019808261` | `1.030156354` |
| `Coarsened_26_helpers_182_units_26_jump_1_8` | `182` | `[(26, 1), (26, 8)]` | `1,872` | `2,472` | `18.267166` | `0.998788267` | **`1.002490876`** | `1.019737698` | `1.030085791` |
| `Coarsened_179_helpers_29_units_179_jump_1_8` | `29` | `[(179, 1), (179, 8)]` | `1,872` | `2,472` | `27.845467` | `0.998152901` | **`1.00185551`** | `1.019102331` | `1.029450424` |
| `PR2953_joint_endpoint_423_units` | `423` | `[]` | `3,807` | `537` | `-11.947098` | **`1.000792498`** | `1.004495107` | `1.021741929` | `1.032090022` |

---

## Six Explicit Behavioral Negative Controls Verified in `RESULT.json`

1. **`nc1_pooled_components_vs_one_hop`:** Replacing 1-hop equal-frame transitivity ($F_{u,d}=F_{w,d}$) with PR `#2996` transitive connected components on the pooled `2,309`-edge graph drops missing pairs from `1` (`(71,102)` / 1-based `(72,103)`, coefficient `-1/2`) to `0`.
2. **`nc2_pr3124_cycle_a_helper91_only_vs_moved_vertices`:** Inspecting only unmoved helper `91` on `PR3124_cycle_A` `[13, 203, 191, 63]` shows `33` / `9,765` passing flags, whereas auditing moved cycle vertices `13` and `63` shows `0` / `9,765` passing flags on both (`min_missing` `1002` and `481`).
3. **`nc3_pr3124_cycle_b_helper91_only_vs_moved_vertices`:** Auditing `PR3124_cycle_B` `[39, 154, 139, 134]` shows `0` / `9,765` passing flags (`min_missing = 91`) on helper `91` and on all four moved cycle vertices (`39`, `154`, `139`, `134`), each having `9,765` valid nested flags between $A_a$ and $B_b$.
4. **`nc4_subspace_memory_dropping_vs_tracking`:** Dropping cross-dimension subspace inclusion ($A_u \subseteq F_{h,d_1} \subseteq F_{h,d_2} \subseteq B_{b(w)}$) gives `0` missing pairs under transitive components on `PR3019` and `PR3124_A`, whereas tracking subspace memory leaves `4,781` (`4781`) missing pairs on `PR2981` and `4,783` (`4783`) missing pairs on `PR3013`, `PR3019`, `PR3124_A`, and `PR3124_B`.
5. **`nc5_idealized_zero_dual_overhead_vs_physical_dual`:** Omitting dual-endpoint boundary conversion overhead ($\Delta H_1 = 0, \Delta H_7 = 0$) gives moment `0.998896238 < 1` for the 208-unit cover at $b_{\text{selected}}$, whereas charging even the 8-$H_7$ private zero/erasure (`1.002598847 > 1`), the 5-boundary fused dual cost (`1.019845668 > 1`), or the full 8-boundary physical dual cost (`1.030193762 > 1`) strictly exceeds `1`.
6. **`nc6_persistent_credit_vs_nonpersistent_dual_accounting`:** Crediting zero-displacement dual boundary conversions as if they replaced persistent rank-`51` idle progress (Mode B) inflates the 208-unit cover's tolerable dual $H_1$ allowance at $b_{\text{selected}}$ from `16.639481` $H_1$/dual call (Mode A) to `2534.201128` $H_1$/dual call (`0.999021779` Mode B vs `1.019845668` Mode A on the 5-boundary fused schedule).

---

## Reproduction

```bash
python3 -B verify.py
```

Expected output (~7.6 seconds, Python 3.12 standard library only):
```text
PASS_P104_POOLED_ONEHOP_AND_PHYSICAL_CONSUMER_BILL pooled_edges=2309 pooled_onehop_missing=1 pr3124_v13_passing=0 pr3124_v63_passing=0 no_new_kappa
```

---

## Open next questions

1. **Stage-Persistent Dual Collector Hosting Across the 4 Dual Calls:** Can the `4` dual calls in the 9-stage `P104` consumer share a persistent rank-8 collector subspace across consecutive stages so that neither the `+8 H7` private collector zero-erasure (`M = 1.002598847 > 1`) nor the `260 H1` / `416 H1` dual boundary conversions (`M = 1.019845668` / `1.030193762 > 1`, above the `16.639481 H1/dual call` break-even at `b_selected = 0.001675460322`) are incurred per dual call?
2. **Coarsened Multi-Rank Helper Flags Below $m_{\max} = 205$:** Can a coarsened rank-2 or rank-3 helper schedule reduce total helper multiplicity below the physical cap $m_{\max} = 205 < 208$ while bridging `X102`'s `1,725`-edge Dim-5 forward cone to `Y71`'s `37`-edge Dim-6 backward cone and resolving the `4,781 / 4,992` cross-dimension subspace-memory gap?
