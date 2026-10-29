# Exact 712-Column Interior Dynamic Range Collapse (`55 -> 18` Bits in `F`, `73 -> 21` Bits in `B`), Backward Adjoint Error-Propagation Ledger, and Physical Recursive Bill for `CONSERVED-QQ16`

**Status:** `PASS_QQ16_INTERIOR_DYNAMIC_RANGE_AND_ADJOINT_LEDGER` — report (author-checked), no new $\kappa$ claimed (`no_new_kappa`).
**Authors:** `dcharb78, with AI assistance`
**Target Task:** `joint-query-controller` (`track = "recursive-interfaces"`, weight `20`, Priority Revision `6` in `docs/research/current-priorities.md` and `docs/research/agent-task-catalog.json`, `base_commit = "997e6a9ca7b4f95d50e366f61412fd640d72a88a"`, `scope_status = "unchanged"`)
**Selected Baseline:** `certificates/selected-result.json` ($\kappa = 0.001672660197076918$, `T37`/`T16`, unchanged exact auditor).
**Provenance Boundary:** Pinned verification inputs (`SOURCES.json`, actual parent lineage) are loaded and SHA-256/git-blob verified at runtime (`#2697`, `#2707`, `#2736`, `#2932`, `#2959`, `#2965`; note that `#1969`, `#2540`, `#2678`, `#2681`, `#2697`, `#2707`, `#2736`, `#2932`, `#2959`, and `#2965` carry `merged_for_archive_only` / `partially_reviewed` status in `docs/research/pr-intake-decisions.json`); concurrent open PRs (`#2995`, `#3017`, `#3036`, `#3068`) are not in `SOURCES.json` and are not read at runtime, serving solely as external comparators / comparison benchmarks.

---

## 1. Executive Summary

Prior archived (`merged_for_archive_only` / `partially_reviewed`) `joint-query-controller` packages reported (author-checked):
- the native-`F17` conserved-helper producer certificate `CONSERVED-QQ16` (`#2697`, `research/joint-query/certificate.json.gz` and `research/joint-query/evidence/CONSERVED-QQ16.json`), which recorded path-sum triangle-inequality Horner bounds of **`55` bits** in `F` (`5413950274051752469/256`) and **`73` bits** in `B` (`573411134169296526275133/64`);
- the `3,823`-event line-normalized `224`-column `Q_Q16` two-sided decoder (`#2707`, `research/qq16-line-normalized-decoder/RESULT.json`);
- the terminal producer-defect transfer law $\delta_R = D(F_0^{-1}\varepsilon_F + \varepsilon_B)$ (`#2965`, `research/qq16-producer-defect-transfer/RESULT.json`) with $\|F_0^{-1}\|_{\infty\to\infty} = 49$, $\|D\|_{\infty\to\infty} = 1923$, and normalized error budget `7587/8192 < 1` whenever $\|\varepsilon_F\|_\infty \le H\cdot 2^{-\beta-8}$ and $\|\varepsilon_B\|_\infty \le H\cdot 2^{-\beta-13}$.

However, `#2965` explicitly left open the **interior fixed-point precision and backward error-propagation ledger** across the `21,025` (`F`) and `21,401` (`B`) scalar gates and the `3,494` (`F`) and `3,510` (`B`) native children of `CONSERVED-QQ16`. Subsequent open PRs (`#2995` and `#3017` by `Wimuks`; `#3036` and `#3068` by `Goodhill1`) inspected only `F_0` (either on the `224`-column data slice or at individual rounding fault sites `24,438`, `3,887`, and `4,060`), leaving the **`B` producer** (`27,019` events, `73`-bit Horner bound), the **backward adjoint sensitivities of all `480` restored helpers**, the **common dyadic grid invariant**, and the **physical recursive bill under `ceiling.ceiling(...)`** unquantified.

This standalone Mode B research package (`verify.py`, stdlib-only, `< 9s` runtime, no checker extensions, unchanged exact auditor) closes that gap with four verified (author-checked) pillars and six negative controls:

1. **Pillar 1 — Exact 712-Column Algebraic Replay & 37-Bit / 52-Bit Dynamic Range Collapse:** Replaying all `712` register columns (`224` data `L[0..223]`, `480` dirty helpers `L[224..703]`, `8` private scratch `C[0..7]` mapped to `704..711`) across all `37` native cases (`F_0` with `26099` events, `F_1..F_8` with `26387` events, and `B_1_2..B_7_8` with `27019` events) proves that massive algebraic cancellation across the `B + restore + cleanup` schedule collapses the true interior $\ell_1$ dynamic range by **37 bits in `F`** (`55 -> 18` bits, exact peak $\ell_1 = 131072 = 2^{17}$) and by **52 bits in `B`** (`73 -> 21` bits, exact peak $\ell_1 = 1154896 < 2^{20.14}$, decomposed into peak data $\ell_1 = 200770$, peak helper $\ell_1 = 954130$, and peak private $\ell_1 = 30$).
2. **Pillar 2 — Exact Backward Adjoint Error-Propagation Ledger (`F` and `B`, `704` Outputs) & Wrapper-Helper Isolation:** Using exact transpose-duality (`704` terminal outputs $\times$ `712` input columns verified bit-for-bit between forward and backward passes), we compute the exact worst-case backward $\ell_1$ error-amplification gains from every `climb`/`native_line` child (`3494` in `F`, `3510` in `B`), `add` gate (`20278` in `F`, `20654` in `B`), and `scale` gate (`715` in `F` and `B`) into both the `224` data outputs and the `480` restored helpers, and prove **Wrapper-Helper Adjoint Isolation**: all wrapper `native_line` children (`8` in `F`, `24` in `B`) and wrapper scalar gates have **exact `0` sensitivity** on all `480` restored helpers (`helpers_wrapper_child_gain = 0`, `helpers_wrapper_gate_gain = 0`).
3. **Pillar 3 — Exact Common Dyadic Grid Invariant (`1/16` in `F`, `1/131072` in `B`) & `50 + \beta`-Bit Precision Floor:** Every intermediate rational coefficient across all `712` columns of `F` and `B` has a power-of-two denominator bounded by `16` ($2^4$, `4` fractional bits) in `F` and `131072` ($2^{17}$, `17` fractional bits) in `B`, with maximum numerator magnitude `65537` ($2^{16}+1$). Executing `F` on the common dyadic grid $2^{-4}$ and `B` on $2^{-17}$ makes all `21025` (`F`) and `21401` (`B`) scalar gates **100% exact integer operations (`eps_gate = 0`, `non_integer_grid_steps = 0`)**. This completely eliminates the cancellation rounding faults reported in `#2995`/`#3017` (at `F_0` event `24438`) and `#3036`/`#3068` (at `F_0` events `3887` and `4060`) and reduces the sufficient fixed-point register width for `#2965` target accuracy $H\cdot 2^{-\beta}$ to **`50 + \beta` bits** (`21` signed integer + `29 + \beta` fractional bits), compared to **`75 + \beta` bits** under rounded-gate execution and **`127 + \beta` bits** under the `73`-bit Horner bound (**saving `52` bits** in `B` and **`37` bits** in `F`).
4. **Pillar 4 — Physical Recursive Bill & Packing-Independent `ceiling.ceiling(...)` Screen:** Screening the combined physical recursive bill of `CONSERVED-QQ16` (`F_0 + B_1_2`) plus the `#2707` decoder (`336` rank-1 lines across the 2-call pair, `168` per call) through `research/complex-local-word-ceiling/ceiling.py` demonstrates that under the unchanged hosted nine-stage coverage law (`centre = 64`), the combined profile `{1: 2596, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}` has exact packing-independent ceiling `a_cap = 0.001633824631` and `kappa_cap = 0.001631159602` (dropping to `a_cap = 0.001512422742`, `kappa_cap = 0.001510138774` when `224` rank-9 $H_9$ endpoint adapters—`112` per call—are paid to exit `F17`). Both lie strictly below the selected baseline $\kappa = 0.001672660197076918$. Only under a hypothetical coverage law that eliminates the `64`-per-call centre tax (`centre = 0`) with an `F17`-native consumer does the surrogate margin reach `a_cap = 0.004579628060`, `kappa_cap = 0.004558750677`.

---

## 2. Pillar 1: Exact 712-Column Algebraic Replay & Interior Dynamic Range Collapse

Each native invocation in `research/joint-query/certificate.json.gz` operates on `712` register columns:
- **`224` data registers (`L[0..223]`):** `112` `X` ports (`L[0..111]`) and `112` `Y` ports (`L[112..223]`).
- **`480` dirty helper registers (`L[224..703]`):** borrowed at non-zero initial states, actively mixed with data wires across `2950` of `3494` children in `F` and `2928` of `3510` children in `B`, and restored to exact identity (`rows[i] == {i: 1}`) at termination.
- **`8` private scratch registers (`C[0..7]`, indexed `704..711`):** initialized by `clear` before use in `private_sweep`, used to host the `8` wrapper `native_line` children (`inverse_0`..`inverse_7`), and zeroed by `clear` (`rows[i] == {}`) at termination.

| Metric | `F_0` (`s = 0`) | `F_1..F_8` (`s = 1..8`) | `B_1_2..B_7_8` (`28` pairs) |
| :--- | :---: | :---: | :---: |
| Total expanded events | `26099` | `26387` | `27019` |
| Scalar gates (`add` / `scale` / `clear`) | `21025` (`20278` / `715` / `32`) | `21025` (`20278` / `715` / `32`) | `21401` (`20654` / `715` / `32`) |
| Native children (`climb` core + `native_line` wrapper) | `3494` (`3486` + `8`) | `3494` (`3486` + `8`) | `3510` (`3486` + `24`) |
| Children reading dirty helper entries (`h_l1 > 0`) | `2950` | `2950` | `2928` |
| Formal path-sum Horner bound (`CONSERVED-QQ16.json`) | `5413950274051752469/256` | `5413950274051752469/256` | `573411134169296526275133/64` |
| Formal Horner ceiling width (bits) | `55` | `55` | `73` |
| Exact interior peak data $\ell_1$ norm (`event`, `reg`) | `131072` (`24611`, `93`) | `131072` (`24611`, `93`) | `200770` (`26594`, `93`) |
| Exact interior peak helper $\ell_1$ norm (`event`, `reg`) | `273` (`19243`, `238`) | `273` (`19243`, `238`) | `954130` (`26599`, `93`) |
| Exact interior peak private $\ell_1$ norm (`event`, `reg`) | `68` (`8162`, `704`) | `68` (`8162`, `704`) | `30` (`9985`, `704`) |
| **Exact interior peak total $\ell_1$ norm (`event`, `reg`)** | **`131072` (`24611`, `93`)** | **`131072` (`24611`, `93`)** | **`1154896` (`26594`, `93`)** |
| **Exact algebraic ceiling width (bits)** | **`18`** | **`18`** | **`21`** |
| **Interior dynamic range collapse (bits saved)** | **`37` (`55 -> 18`)** | **`37` (`55 -> 18`)** | **`52` (`73 -> 21`)** |
| Max dyadic denominator ($2^k$) / fractional bits | `16` (`4` bits) | `16` (`4` bits) | `131072` (`17` bits) |
| Max numerator absolute value | `65537` | `65537` | `65537` |
| Peak child-entry $\ell_1$ norm (`total` = `data` / `helper` max) | `124` (`56` / `68`) | `124` (`56` / `68`) | `166` (`158` / `18`) |
| Terminal max data $\ell_1$ norm / helper leak on data | `27` / `0` | `27` / `0` | `64` / `0` |
| Terminal restored helpers / zeroed private `C` registers | `480` / `8` | `480` / `8` | `480` / `8` |

---

## 3. Pillar 2: Exact Backward Adjoint Error-Propagation Ledger & Wrapper-Helper Isolation

If scalar gate $t$ injects an additive defect $\eta_t$ on register $a_t$ and native child $c$ injects a defect $\zeta_c$ on wire $w_c$, the terminal defect on output register $r \in \{0,\dots,703\}$ is given by the backward adjoint functional $e_r^\top M_{\text{after}}$:
$$|\delta_{\text{out}}(r)| \le G_{\text{child}}(r)\,\varepsilon_{\text{child}} + G_{\text{add}}(r)\,\varepsilon_{\text{add}} + G_{\text{scale}}(r)\,\varepsilon_{\text{scale}}.$$

| Output Sector | Producer Side | Total Child Gain $G_{\text{child}}$ | Wrapper Child Gain | Core Child Gain | Max Single-Child Gain | `add` Gate Gain $G_{\text{add}}$ | `scale` Gate Gain $G_{\text{scale}}$ | Combined Scalar Gate Gain $G_{\text{gate}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Data `X` (`0..111`) | `F` | `132` | `1` | `132` | `2` | `174091/512` | `66311/4` | `2216769809/131072` (`16912.6115`) |
| Data `Y` (`112..223`) | `F` | `118` | `1` | `118` | `2` | `528` | `16392` | `536179/32` (`16755.59375`) |
| **All Data (`0..223`)** | **`F`** | **`132`** | **`1`** | **`132`** | **`2`** | **`528`** | **`66311/4`** | **`2216769809/131072` (`16912.6115`)** |
| **Restored Helpers (`224..703`)** | **`F`** | **`59`** | **`0`** | **`59`** | — | **`5920689/32768`** | **`131163/4`** | **`131599/4` (`32899.75`)** |
| Data `X` (`0..111`) | `B` | `381/2` (`190.5`) | `13` | `381/2` | `12` | `1836679/2` | `16603/4` | `3689923/4` (`922480.75`) |
| Data `Y` (`112..223`) | `B` | `16` | `1` | `16` | `2` | `257` | `5/2` | `258` |
| **All Data (`0..223`)** | **`B`** | **`381/2` (`190.5`)** | **`13`** | **`381/2`** | **`12`** | **`1836679/2`** | **`16603/4`** | **`3689923/4` (`922480.75`)** |
| **Restored Helpers (`224..703`)** | **`B`** | **`393/2` (`196.5`)** | **`0`** | **`393/2`** | — | **`11715/8`** | **`61`** | **`1515` (`1515.0`)** |

**Wrapper-Helper Adjoint Isolation Theorem:** Across both `F` and `B`, `wrapper_writes_to_helpers = 0` and `wrapper_reads_from_helpers = 0`. Consequently, the `8` wrapper `native_line` children in `F`, the `24` wrapper `native_line` children in `B`, and all wrapper scalar gates have **exact zero** backward adjoint sensitivity to all `480` restored helper outputs (`helpers_wrapper_child_gain = 0`, `helpers_wrapper_gate_gain = 0`).

---

## 4. Pillar 3: Common Dyadic Grid Exactness & Coupling to `#2965`

Every scalar coefficient in `F` and `B` is dyadic ($c \in \{ \pm 1, \pm 1/2, \pm 1/4, \pm 3/4, \pm 5/4, \pm 9/4, \pm 2, \pm 3, \pm 4, \pm 8 \}$), and every intermediate rational entry across all `712` columns has denominator dividing `16` ($2^4$) in `F` and `131072` ($2^{17}$) in `B`.
- **Common-Grid Exactness (`eps_gate = 0`):** Representing registers on the fixed-point grid $2^{-4}$ in `F` (`4` fractional guard bits) and $2^{-17}$ in `B` (`17` fractional guard bits) makes all `21025` scalar gates in `F` and all `21401` scalar gates in `B` **exact integer operations (`non_integer_grid_steps = 0`)**.
- **Resolution of `#2995`/`#3017`/`#3036`/`#3068` Rounding Faults:** The cancellation faults reported in `#2995`/`#3017` (at `F_0` event `24438`) and `#3036`/`#3068` (at `F_0` events `3887` and `4060`) are artifacts of truncating `scale`/`add` outputs above the `4`-bit (`F`) and `17`-bit (`B`) dyadic grid floor. On the exact dyadic grid, those instructions execute with zero rounding error (`fault_site_checks = true`).
- **Coupling to `#2965` (`qq16-producer-defect-transfer`):** Under `#2965` ($\|F_0^{-1}\|_{\infty\to\infty} = 49$, $\|D\|_{\infty\to\infty} = 1923$, normalized error budget `7587/8192 < 1`), achieving decoded residual accuracy $\|\delta_R\|_\infty \le H\cdot 2^{-\beta}$ suffices whenever $\|\varepsilon_F\|_\infty \le H\cdot 2^{-\beta-8}$ and $\|\varepsilon_B\|_\infty \le H\cdot 2^{-\beta-13}$:
  1. **Exact Common-Grid Scalar Execution (`eps_gate = 0`):** Only child evaluations contribute error (`G_child(F) = 132 < 2^8` with child-entry norm $\le 124 < 2^7$; `G_child(B) = 381/2 < 2^8` with child-entry norm $\le 166 < 2^8$), requiring **`29 + \beta` fractional bits** and **`21` signed integer bits** (since peak interior $\ell_1 = 1154896 < 2^{20.14}$), for a total fixed-point register width of **`50 + \beta` bits**.
  2. **General Rounded-Gate Execution (`eps_gate > 0`):** Total backward amplification is `F_total_adjoint_gain = 2234071313/131072` ($< 2^{15}$) in `F` and `B_total_adjoint_gain = 3690685/4` ($< 2^{20}$) in `B`, requiring `54 + \beta` fractional bits and **`75 + \beta` total bits** in `B`—still **saving `52` bits** compared to the **`127 + \beta` bits** required under the `73`-bit Horner bound (`horner_B_total_bits_offset = 127`).

---

## 5. Pillar 4: Physical Recursive Bill & Packing-Independent `ceiling.ceiling(...)` Screen

Combining `CONSERVED-QQ16` (`F_0` paid child profile `{1: 2420, 2: 418, 3: 432, 4: 142, 5: 82}`, mass `5530`; `B_1_2` paid child profile `{1: 2436, 2: 418, 3: 432, 4: 142, 5: 82}`, mass `5546`) with the `#2707` decoder (`3823` events, `336` rank-1 lines across the 2-call pair = `168` per call, `2704` scalar adds = `1808` `unit_ADD` + `896` `quarter_ADD`, `312` clears, `464` cover maps) yields a 2-call pair average core+decoder rank-1 count of `2428 + 168 = 2596` per call:

| Profile Screened (`m = 73`, `families = 896`, `stages = 9`, `grid = 10^-12`) | `centre` / call | Paid Local Mass / call | Certified $a_{\text{cap}}$ (`a_hi`) | Certified $\kappa_{\text{cap}} = a_{\text{cap}}/(1+a_{\text{cap}})$ | Relation to Selected $\kappa = 0.001672660197076918$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Selected baseline `{1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}` | `64` | `5586` | `0.001690054110` | `0.001687202646` | Selected ceiling envelope (`+1.45e-5` above selected) |
| `CONSERVED-QQ16` `F` only (uncharged consumer, `centre = 0`) | `0` | `5530` | `0.004730555837` | `0.004708283041` | Uncharged producer-only surrogate margin |
| `CONSERVED-QQ16` `B` only (uncharged consumer, `centre = 0`) | `0` | `5546` | `0.004716424327` | `0.004694284091` | Uncharged producer-only surrogate margin |
| **`CONSERVED-QQ16` pair + `#2707` decoder (`centre = 64` retained)** | **`64`** | **`5770`** | **`0.001633824631`** | **`0.001631159602`** | **Strictly below selected $\kappa$ (`-4.15e-5`)** |
| **`CONSERVED-QQ16` pair + `#2707` decoder + `224` $H_9$ adapters (`centre = 64`)** | **`64`** | **`6778`** | **`0.001512422742`** | **`0.001510138774`** | **Strictly below selected $\kappa$ (`-1.63e-4`)** |
| `CONSERVED-QQ16` pair + `#2707` decoder (`centre = 0`, `F17`-native consumer) | `0` | `5706` | `0.004579628060` | `0.004558750677` | Requires global `centre = 0` coverage law + `F17` consumer |
| `CONSERVED-QQ16` pair + `#2707` decoder + `224` $H_9$ adapters (`centre = 0`) | `0` | `6714` | `0.004239533840` | `0.004221636071` | Requires global `centre = 0` coverage law |

---

## 6. Six Single-Move & Perturbation Negative Controls

1. **Control 1 (`control_1_horner_vs_exact_algebraic_collapse`):** Confirms the `37`-bit (`55 -> 18` in `F`) and `52`-bit (`73 -> 21` in `B`) collapse between path-sum Horner bounds and exact 712-column algebraic replay (`status = "PASS"`).
2. **Control 2 (`control_2_truncated_restoration_suffix`):** Truncating the restoration/cleanup tail after the last dirty-helper write onto data wires (`event 16850` in `F_1`, `event 18714` in `B_1_2`) leaves **`480` unrestored helpers in `F`** (max helper $\ell_1 = 62$) and **`395` unrestored helpers in `B`** (max helper $\ell_1 = 16$), proving the `B + restore + cleanup` suffix is algebraically mandatory (`status = "REJECTS_TRUNCATED_RESTORATION"`).
3. **Control 3 (`control_3_omitted_private_c_clears`):** Omitting the `32` `clear` gates on `C[0..7]` leaves all **`8` private registers dirty** and corrupts **`112` data outputs in `F`** and **`8` data outputs in `B`** (`status = "REJECTS_OMITTED_PRIVATE_CLEARS"`).
4. **Control 4 (`control_4_synthetic_wrapper_helper_coupling`):** Injecting a single synthetic wrapper read from `A_copy` wire `L[112]` into helper `L[224]` immediately raises `helpers_wrapper_child_gain` from `0` to `1` (`status = "REJECTS_WRAPPER_HELPER_COUPLING"`).
5. **Control 5 (`control_5_single_sign_perturbation_at_peak_helper_event`):** Flipping the sign at the `#3036`/`#3068` helper-cancellation site (`event 3887`) and the peak interior $\ell_1$ site (`event 24611`) in `F_1` leaves **`136` helpers unrestored**, leaks helper dirt onto **`4` data outputs**, and blows up the terminal data $\ell_1$ norm from `27` to **`270668033/4096`** (`status = "REJECTS_SINGLE_SIGN_PERTURBATION"`).
6. **Control 6 (`control_6_uncharged_vs_charged_consumer_ceiling`):** Confirms that under the unchanged `centre = 64` coverage law, paying `#2707`'s `336` rank-1 decoder lines forces $\kappa_{\text{cap}} = 0.001631159602 < 0.001672660197076918$ (`status = "CONFIRMS_CENTRE_AND_CONSUMER_BOTTLENECK"`).

---

## 7. Comparison Against Prior & Open `joint-query-controller` PRs

| Package / PR | Scope Covered | `B` Replay (`27019` events) | 712-Col (`480` Helpers + `8` `C`) | Backward Adjoint Ledger | Common Grid (`1/16`, `1/131072`) | `ceiling.ceiling(...)` Screen |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `#2697` (`CONSERVED-QQ16`) | Native producer certificate & Horner bounds (`55` / `73` bits) | Horner only (`73` bits) | Terminal check | No | No | No |
| `#2707` (`qq16-line-normalized-decoder`) | `3823`-event `224`-column `Q_Q16` decoder (`336` rank-1 lines) | N/A | `224`-col decoder | No | No | No |
| `#2965` (`qq16-producer-defect-transfer`) | Terminal transfer $\delta_R = D(F_0^{-1}\varepsilon_F + \varepsilon_B)$ (`49`, `1923`) | Terminal only | `224`-col terminal | No | No | No |
| `#2995` / `#3017` (`Wimuks`) | `F_0` `224`-column data slice & event `24438` rounding fault | No (`F_0` only) | No (`224` data cols) | Partial (`F_0` data) | `F_0` data (`1/16`) | No |
| `#3036` / `#3068` (`Goodhill1`) | `F_0` dirty-helper child count (`2950`) & events `3887`/`4060` | No (`F_0` only) | `F_0` forward only | No | No | No |
| **This Package** | **Full `37`-case `F` & `B` 712-col replay, adjoint ledger, grid & ceiling** | **Yes (`73 -> 21` bits, peak `1154896`)** | **Yes (`712` cols across `37` cases)** | **Yes (`F` & `B`, `704` outputs)** | **Yes (`50 + \beta` bits, `eps_gate = 0`)** | **Yes (`0.001631159602` vs `0.004558750677`)** |

---

## 8. Pinned Upstream Inputs (`SOURCES.json`)

| Path | Usage | `git_blob` | `sha256` |
| :--- | :---: | :--- | :--- |
| `certificates/selected-result.json` | `provenance` | `b1fea0c94436b236cc2b7d41a7be032811b94c81` | `bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129` |
| `docs/research/agent-task-catalog.json` | `provenance` | `67f085acd86acd7d4e03922d9cf4b26bca66fed5` | `47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0` |
| `research/complex-local-word-ceiling/RESULT.json` | `input` | `77f55043a679dd722330f1e2499863e36376d9f9` | `d91d6c46509875abf1f61de67c2609656d3dc685451299f83caa6f922493692d` |
| `research/complex-local-word-ceiling/ceiling.py` | `input` | `6c0f54527d879396f689523bfde19928a9b6157c` | `86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc` |
| `research/joint-query/certificate.json.gz` | `input` | `c6e876d8b48d768214deee265ade428f8983b566` | `a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7` |
| `research/joint-query/evidence/CONSERVED-QQ16.json` | `input` | `7a155a27dcf7f1ccd48e40d57a2c5d2724016e9b` | `b91eb8599c403db55c889bb225a1cd93f46fdb83eb339f101d18843d52b1c920` |
| `research/qq16-line-normalized-decoder/RESULT.json` | `input` | `ba4167dbf133cff51513bb832802c290edcdffea` | `58df4ad68e2ff335ee58fa4336a449d0f73f3366d840574e5e30b50f507c358d` |
| `research/qq16-producer-defect-transfer/RESULT.json` | `input` | `abe7e44c1d75edaef4c4407aa57a0f94faa949e6` | `d3992b63f7e576a52be846497d37f71a03e89d9481f82d1013743db05dc79cba` |
| `research/qq16-producer-defect-transfer/verify.py` | `input` | `8dd78e9e36acb63451eae88c3c558f7f9afc348a` | `1458d3a188a8ec0124e6edd1fdc7d9238c41d7a547fa2c00229763fc698e46c8` |

---

## 9. Standalone Reproduction

```bash
python3 -B research/qq16-interior-dynamic-range-and-adjoint-ledger/verify.py
```

Expected output (`< 9` seconds, Python 3.12 standard library only):
```text
PASS_QQ16_INTERIOR_DYNAMIC_RANGE_AND_ADJOINT_LEDGER F_collapse_bits 37 B_collapse_bits 52 F_peak_l1 131072 B_peak_l1 1154896 F_child_gain 132 B_child_gain 381/2 centre64_kappa_cap 0.001631159602 no_new_kappa
```

---

## Open next questions

1. **Direct $F_{17}$ Consumer Entrance Contract Without $H_9$ Endpoint Adapters:** Can a downstream consumer in the hosted 9-stage template accept the `224` decoded original inputs directly in physical chart $F_{17}$ without paying `224` rank-9 $H_9$ endpoint conversion children (`a_cap = 0.001633824631` vs `0.001512422742` under `centre = 64`, and `a_cap = 0.004579628060`, `kappa_cap = 0.004558750677` under `centre = 0`)?
2. **Exact Dyadic Grid Execution Inside the 3,486 Core Climb Children:** Can the `3,494` (`F`) and `3,510` (`B`) native child interiors execute on the invariant dyadic grids $2^{-4}\mathbb{Z}$ (`F`) and $2^{-17}\mathbb{Z}$ (`B`) with per-child error bounded by $\varepsilon_{\text{child},F} \le H \cdot 2^{-\beta-16}$ and $\varepsilon_{\text{child},B} \le H \cdot 2^{-\beta-21}$ at child-entry $\ell_1$ norms $\le 124$ (`F`) and $\le 166$ (`B`)?

