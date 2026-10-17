# Precision-40 endpoint refinement above PR #3133

This package replays PR [#3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133) from its exact source commit `51eb9c4ee9e4722010d308aa3309e039d3940cc2` and preserves its words, literal T74 fill, and paid profile. It changes only the exact root endpoint from 24 to 40 decimal places. The new claim is

- `C40 = 0.0017297760894051203342384678198935738683`
- `κ = C40 - 10^-86 - 10^-62 = 0.00172977608940512033423846781989357386829999999999999999999998999999999999999999999999`

This exceeds PR #3133's exact public claim by `46781989357386830000009999999999999999000000009999999999999999/100000000000000000000000000000000000000000000000000000000000000000000000000000000000000`. The 40-digit root bracket passed both rational moment engines; the complete source-export, native, replica-admission, and outer-release replay also passed and is bound by the receipts in `evidence/`. This refines only the reported endpoint: it does not change the construction or selected frontier. The rest of this README is retained construction provenance from PR #3133, not a claim that its historical PR/status snapshot is current.

Reproduce the complete cold chain with `python3.12` and all source Git objects present:

```sh
python3.12 -B research/rank7-coupled-586-588-carrier-fold-precision40/reproduce.py \
  --repo FULL_GIT_REPO_WITH_GIT_SOURCES_OBJECTS \
  --work /tmp/rank7-precision40-replay --jobs 2
```

## Precision-refinement scope

The fixed T74 allocation has a strict root margin: the endpoint is rounded down to a certified rational grid point, and the release subtracts two exact positive slacks. The adapter builder records every declared change in `PRECISION-EDITS.json`; `verify_release.py` adds PR #3133's exact κ to the strict comparison ledger. `check_allocation.py` independently recounts the same paid profile and verifies the refined endpoint with outward 192-bit rational intervals. A new endpoint is accepted only by the full native, outer, and replica-admission replay.

## Open next questions

1. Can precision be increased further before the independent 192-bit interval engine's enclosure becomes the limiting resolution? First step: bound the width of its moment interval at the root and test the next endpoint grid with strict negative controls.
2. Can a literal T740 allocation realize the fixed-inventory cap at approximately `0.001729777494678597`, closing the inherited `1.4053e-9` integer-allocation gap? First step: port the verified PR #3133 profile through its actual owner chronology at T=740 and rerun the complete supplier invoice.
3. Can a genuinely changed frame/warp contract unlock the transverse-cone lock on helpers 584 and 590 without returning the cost in restoration? First step: construct one chronological B_WARP change and price all affected children.

# Coupled `B + restore` dying-helper carrier folds lowering helpers `586` & `588` to rank 7 (`width 6`): conditional κ = 0.001729776089405120334238 − 10⁻⁴⁶ − 10⁻⁷⁰

**Selected frontier & archival base disclosure (`certificates/selected-result.json`, `docs/research/pr-intake-decisions.json`, `docs/research/current-priorities.md` Priority Revision 6):** The official selected conditional bound on `main` remains **`κ = 0.001672660197076918`** (PR #1094). This package is built directly and solely on top of our **actual parent lineage**: **PR #2979** (`mdumitrean`, Marius-Paul Dumitrean), **PR #3015** (`jeremykothe2`, Jeremy Kothe), and **PR #3042** (`dcharb78`), which are recorded in `docs/research/pr-intake-decisions.json` as **archived author claims (`merged_for_archive_only`, `partially_reviewed`)**. Concurrent downstream packages on `main`—**PR #3050** (`petalas`, Nick Petalas), **PR #3051** (`jeremydiviney`, Jeremy Diviney), **PR #3054** (`petalas`), **PR #3056** (`petalas`), **PR #3057** (`petalas`), **PR #3060** (`petalas`), **PR #3064** (`dataisfire`), **PR #3065** (`petalas`), and **PR #3103** (`Arham-Tahir64`) (**archived author claims (`merged_for_archive_only`, `partially_reviewed`)**), alongside open PRs **#3112**, **#3119**, **#3126** (`jwr404`, `V45` invoice/chronology audits), **#3114** (`mdumitrean`), **#3115** (`dataisfire`), and **#3125** (`navinor`, negative ceiling screen of `R489`/`R480` on card `complex-new-helper-inventory`)—were **not** used as inputs to construct this package and are cited solely as **external comparators / scoped optimality baselines**. Per `docs/research/current-priorities.md` (**Priority Revision 6**, `incumbent-optimization` / `complex-new-helper-inventory`), reopening a domain bounded by scoped negative/optimality results requires explicitly naming the **changed hypothesis**:
- **PR #3057** and **PR #3065** (`petalas`, **archived author claims (`merged_for_archive_only`, `partially_reviewed`)**) report (author-checked) that on PR #3042's six-skip words, with scalar operations/order and helper endpoints fixed, **all 6,141 `A`/`B`/`restore` frames are already at their global optimum**.
- **Open PR #3114** (`mdumitrean`) reports (author-checked) that with `A`, `B`, warps, and helper endpoints (`{6:16, 7:52}`) fixed, replacing `restore` by any legal scalar gate sequence and re-solving all frames satisfies `cert(W') >= 10,868,103,087 = cert(PR3042)`—so PR #3042's `-29,976` restore saving (`-12 H1 + 6 H2`) exhausts restore-only improvements under fixed `A`, `B`, and fixed helper endpoints.
- **PR #3051**, **PR #3054**, and **PR #3103** (**archived author claims (`merged_for_archive_only`, `partially_reviewed`)**, plus 30-digit refinement open **PR #3115**) report (author-checked) that at $T=740$ ($20 \mid T$), the fixed helper width inventory `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` attains its continuous relaxation cap (`κ = 0.0017297379500642785512428...`).

**Changed hypothesis in this package (`research/rank7-coupled-586-588-carrier-fold`):** We relax the joint invariance of **`B`-phase carrier routing and `helper_final` terminal subspaces** by coupling a **`B`-phase dying-helper carrier fold** on `(586, 438)` and `(588, 440)` (`B_586_438` and `B_588_440`) with **Stage-1 `helper_final` lowering** of entering helpers `586` ($E_{30} \to V_{30,76,82}$) and `588` ($E_{30} \to V_{30,97,127}$) from rank 8 (`width 7`) to rank 7 (`width 6`), shifting the per-call helper width inventory from **`{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` to `{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}`** (`24` lowered rank-7 helpers instead of `22`, at unchanged `91` private zero buffers and `66,813` physical families). Neither move works alone (Stage-1 lowering of `586` or `588` alone has a negative surrogate margin of **`-3,345`** each; Stage-2 folding at `dim 8` alone has a negative surrogate margin of **`-973`** each), but together they exhibit a **`+4,983` per-helper (`+9,966` joint) positive cross-term synergy**, saving `-2,091,965` local climb units per helper against the rounded guide value `BE = 2,091,300` for a **surrogate margin of `+665` each = `+1,330` together** on top of `R1_E42 + R2_E7`'s `-29,976` (while the $\kappa$ result and `RELAX-CAP` certificate carry the actual claim). Paired with a repacked literal $T=74$ allocation (`allocation/FILL.json.gz`, `T74_optimal_idle39`), the certified literal $T=74$ root is **`κ in [0.0017297760894051203342384, 0.0017297760894051203342385]`** (`+3.99230172e-8` over PR #3042's $T=74$ root and **`+3.81393408e-8` strictly above PR #3054/#3115's $T=740$ cap-attaining root**), and the new continuous relaxation cap rises to **`RELAX-CAP in [0.0017297774946785970118869, 0.0017297774946785970118870]`** (**`+3.95446143e-8` above PR #3054's $T=740$ cap**).
- **Extended Declared-Edit Checker vs. Unchanged Exact Auditor:** The Stage-4 declared-edit applier and independent edit reviewer (`edits/declared_edits.py`, `edits/edits_review.py`, `verify.py`) were extended from single-hunk `restore` replacements to support multi-hunk `B + restore` edits with automatic `warps` index shifting and declared `helper_final` lowerings to codimension-2 subspaces (`V_{30,76,82}`, `V_{30,97,127}`). The exact forward/dual linear auditor (`vendor/audit_local.py`), monotone frame/cleanup engine (`vendor/preload_move.py`), and two-sided structure certificate checker (`structure.py`) are **unchanged and byte-identical to PR #3042's** (and PR #2979 / PR #2917's).

```text
Status / UTC update / priority revision: DONE (conditional candidate) · 2026-10-17 · priority revision 6 · base main 997e6a9c
Selected conditional result on main: κ = 0.001672660197076918 (PR #1094, certificates/selected-result.json)
Archival parent lineage & external comparators: Built solely on PR #2979, PR #3015, and PR #3042 (archived author claims:
    merged_for_archive_only, partially_reviewed in docs/research/pr-intake-decisions.json). Concurrent PRs #3050, #3051, #3054,
    #3056, #3057, #3060, #3064, #3065, #3103 (archived) and #3112, #3114, #3115, #3119, #3125, #3126 (open) are cited solely as external comparators.
Concrete question and changed premise (docs/research/current-priorities.md, Priority Revision 6): PR #3065 reports (author-checked)
    all 6,141 frames in PR #3042's words are globally optimal under fixed gates and fixed helper endpoints, and open PR #3114 reports
    (author-checked) PR #3042's -29,976 restore saving is globally optimal over all restore gate sequences under fixed A, B, and fixed
    helper endpoints {6:16, 7:52}. In PR #2979, entering helpers 586 and 588 were the only two restored helpers whose causal lower bounds
    L_586, L_588 already had dimension 7 (k=0 blocking causal gates), yet Stage-1 lowering alone had a -3,345 surrogate margin each.
    Can coupling a B-phase dying-helper carrier fold on (586, 438) and (588, 440) with Stage-1 helper_final lowering give 586 and 588
    a positive surrogate margin, shift the width inventory to {6:18, 7:50}, and beat both PR #3042 (T=74) and PR #3054/#3115 (T=740)?
Established result and evidence status: yes. Four declared edits in edits/EDITS.json—R1_E42 (26 -> 33 gates skipping {22, 40, 54, 63}),
    R2_E7 (13 -> 15 gates skipping {5, 73}), B_586_438 (6 hunks, 6 -> 5 gates + helper_final[586] -> V_{30,76,82}), and B_588_440
    (6 hunks, 6 -> 5 gates + helper_final[588] -> V_{30,97,127})—move the local profile to {1:2433, 2:724, 3:228, 4:102, 5:20, 8:8}
    and the width inventory to {4:26, 5:2, 6:18, 7:50, 8:99, 9:213} (91 buffers). With the repacked literal T74 allocation
    (T74_optimal_idle39), complete fresh-native admission and modern outer release pass at
    κ = 0.001729776089405120334238 - 10^-46 - 10^-70 (literal root κ in [0.0017297760894051203342384, 0.0017297760894051203342385];
    RELAX-CAP in [0.0017297774946785970118869, 0.0017297774946785970118870]). Author-checked (AI-assisted); not maintainer-reviewed.
Public artifact URL + exact commit: research/rank7-coupled-586-588-carrier-fold (see the PR).
Next useful task: compose the {4:26, 5:2, 6:18, 7:50, 8:99, 9:213} words with a T=740 (20 | T) cap-attaining allocation to close the
    1.4053e-9 T=74 integer-rounding gap, or compose with PR #3060/#3076 native primitive contractions.
Active claim / expiry: released.
```

---

## 1. Headline Comparison Table

| Package / Record | Intake / Review Status (`pr-intake-decisions.json`) | κ (headline; candidate rows carry `− 10⁻⁴⁶ − 10⁻⁷⁰`) | Exact Root / Cap Bracket | Local Profile per Call | Helper Width Inventory | Complete Paid Profile ($T=74$ unless noted) |
|---|---|---|---|---|---|---|
| **Selected Result (PR #1094)** | **Official selected conditional bound (`certificates/selected-result.json`)** | **`0.001672660197076918`** | `20908252463461475 / 12500000000000000000` | Selected `k8` baseline | Selected `k8` baseline | Selected `k8` baseline |
| **PR #2969** (`Dugongue`) | Archived comparator (`allocation/baseline/CLAIM.json`) | `0.00172403522474810487855` | Cap-level at $T=370$ | `{1:2430, 2:628, 3:282, 4:110, 5:26, 8:8}` | `{4:26, 5:2, 7:62, 8:100, 9:218}` (86 buf) | $T=370$ baseline |
| **PR #2979** (`mdumitrean`) | **Archived author claim (`merged_for_archive_only`, `partially_reviewed`)** | `0.001729033982646513517717` | Root `0.0017290339826465...`<br>Cap `0.0017290357648755...` | `{1:2445, 2:706, 3:232, 4:108, 5:18, 8:8}` | `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` (91 buf) | `{1:1645680, 2:470196, 3:159468, 4:71928, 5:13716, 8:5328, 48:28190}` |
| **PR #3015** (`jeremykothe2`) | **Archived author claim (`merged_for_archive_only`, `partially_reviewed`)** | `0.001729150973534224428695` | 1 skip (`63` via `61`) | `{1:2443, 2:707, 3:232, 4:108, 5:18, 8:8}` | `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` (91 buf) | `{1:1644348, 2:470862, 3:159468, 4:71928, 5:13716, 8:5328, 48:28190}` |
| **PR #3042** (`dcharb78`, audited in **#3050**, **#3065**, **#3114**) | **Archived author claim (`merged_for_archive_only`, `partially_reviewed`)** | `0.001729736166387915986812` | Root `[0.0017297361663879159868125, ...6]`<br>Cap `[0.0017297379500642785512428, ...9]` | `{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}` | `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` (91 buf) | `{1:1637688, 2:474192, 3:159468, 4:71928, 5:13716, 8:5328, 48:28190}` |
| **PR #3051 / #3054 / #3103** (`jeremydiviney` / `petalas` / `Arham-Tahir64`) & open **PR #3115** (`dataisfire`) | **Archived author claims (`merged_for_archive_only`, `partially_reviewed`)** / open (#3115) | `0.001729737950064278551242` (`#3054`)<br>`0.001729737950064278551242895823` (`#3115`, `− 10⁻⁵² − 10⁻⁷⁶`) | Attains `{6:16, 7:52}` cap at $T=740$ ($20 \mid T$) | `{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}` | `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` (91 buf) | $T=740$ cap-attaining profile (`6,660` calls) |
| **This Package (`rank7-coupled-586-588-carrier-fold`)** | **New conditional candidate (author-checked, AI-assisted)** | **`0.001729776089405120334238`** | **Root `[0.0017297760894051203342384, 0.0017297760894051203342385]`**<br>**`RELAX-CAP` `[0.0017297774946785970118869, 0.0017297774946785970118870]`** | **`{1:2433, 2:724, 3:228, 4:102, 5:20, 8:8}`** | **`{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}` (91 buf)** | **`{1:1637692, 2:482184, 3:156741, 4:67932, 5:14710, 8:5328, 39:1, 48:28256}`** |

### Exact Certified Gains (`check_cap.py`, `CLAIM.json`)
- **Over PR #3042 ($T=74$ literal root):** **`+3.99230172e-8`** (`0.0017297760894051203342384 - 0.0017297361663879159868125`).
- **Over PR #3051 / PR #3054 / PR #3115 ($T=740$ cap-attaining root):** **`+3.81393408e-8`** (`0.0017297760894051203342384 - 0.0017297379500642785512428`, beating the $T=740$ ceiling of the old `{6:16, 7:52}` inventory already at $T=74$).
- **Continuous Relaxation Cap Gain (`RELAX-CAP` over PR #3054 / PR #3042 cap):** **`+3.95446143e-8`** (`0.0017297774946785970118869 - 0.0017297379500642785512428`).
- **Remaining $T=74$ Integer-Rounding Gap to `RELAX-CAP`:** **`1.4053e-9`** (`0.0017297774946785970118869 - 0.0017297760894051203342385`), which is strictly smaller than PR #3042 / PR #2979's `1.7837e-9` gap at $T=74$ and arises from the $20 \mid T$ fractional-basis period effect (`idle_per_replica = {1: 234, 3: 1323/20, 5: 75/4, 48: 7637/20}` in `certificates/RELAX-CAP.json`) closed at $T=740$ in PR #3024, #3030, #3051, #3054, and #3103 (and partially at $T=148$ in PR #3022, #3028, #3064).
- **Over pinned comparators (`comparators/` & `allocation/baseline/`):**
  - Over PR #2979: `742106758606816521 / 10^24` $\approx$ **`+7.4210675861e-7`**
  - Over PR #2969: `717608082126931961 / (1.25 × 10^23)` $\approx$ **`+5.7408646570e-6`**
  - Over PR #2966: `2870908440834078413 / (5 × 10^23)` $\approx$ **`+5.7418168817e-6`**
  - Over PR #2957: `6058674334382163267 / 10^24` $\approx$ **`+6.0586743344e-6`**
  - Over PR #2942: `3479884770953003121 / (5 × 10^23)` $\approx$ **`+6.9597695419e-6`**

---

## 2. Literal `edits/EDITS.json` Specification (All 4 Edits & `helper_final` Lowerings)

Every gate count (`len(old) -> len(new)`), register ID, rational coefficient, subspace frame basis, and per-edit profile delta below is derived programmatically and literally from `edits/EDITS.json` (which applies identically to `base` and `extra`). Across all 4 edits (`14` hunks total per word) and `2` `helper_final` lowerings, the only registers touched in `edits/EDITS.json` are:
- **`R1_E42` (`14` registers):** `[18, 22, 34, 40, 45, 54, 61, 63, 92, 103, 108, 226, 228, 230]`
- **`R2_E7` (`6` registers):** `[5, 59, 73, 96, 363, 395]`
- **`B_586_438` (`7` registers):** `[75, 136, 140, 144, 187, 438, 586]`
- **`B_588_440` (`7` registers):** `[84, 162, 172, 196, 221, 440, 588]`

### Summary Table of the 4 Declared Edits in `edits/EDITS.json`

| Edit ID | Section & Source Addresses | Hunks & Literal Gate Counts (`len(old) -> len(new)`) | Touched Registers | `helper_final` Lowering (`old -> new`) | Per-Call Profile $\Delta$ | Surrogate Guide $\Delta$ (`c1=2,116,671`, rounded guide `BE=2,091,300`; $\kappa$ carries the claim) |
|---|---|---|---|---|---|---|
| **`R1_E42`** | `restore[162:188]` | 1 hunk: **`26 -> 33`** | `18, 22, 34, 40, 45, 54, 61, 63, 92, 103, 108, 226, 228, 230` (skips `E_42` for `{22, 40, 54, 63}`) | None | **`-8 H1 + 4 H2`** | **`-19,984`** (`+19,984` surrogate margin) |
| **`R2_E7`** | `restore[190:203]` | 1 hunk: **`13 -> 15`** | `5, 59, 73, 96, 363, 395` (skips `E_7` for `{5, 73}`) | None | **`-4 H1 + 2 H2`** | **`-9,992`** (`+9,992` surrogate margin) |
| **`B_586_438`** | `B[52:53]`, `B[784:785]`, `B[794:795]`, `B[1214:1215]`, `B[1230:1231]`, `restore[85:86]` | 6 hunks: **`6 -> 5`** (`1 -> 0` at `B[52:53]`, five `1 -> 1`) | `75, 136, 140, 144, 187, 438, 586` | `586`: `E_30` (`8`) $\to$ `V_{30,76,82}` (`7`) (`[256,128,70,32,18,12,1]`, width `7 -> 6`) | **`+6 H2 - 2 H3 - 3 H4 + 1 H5`** | **`-2,091,965`** vs `BE = -2,091,300` $\implies$ **`+665` surrogate margin** |
| **`B_588_440`** | `B[57:58]`, `B[789:790]`, `B[799:800]`, `B[1222:1223]`, `B[1238:1239]`, `restore[88:89]` | 6 hunks: **`6 -> 5`** (`1 -> 0` at `B[57:58]`, five `1 -> 1`) | `84, 162, 172, 196, 221, 440, 588` | `588`: `E_30` (`8`) $\to$ `V_{30,97,127}` (`7`) (`[256,128,65,33,18,10,6]`, width `7 -> 6`) | **`+6 H2 - 2 H3 - 3 H4 + 1 H5`** | **`-2,091,965`** vs `BE = -2,091,300` $\implies$ **`+665` surrogate margin** |
| **Total** | `B` (`-2` gates, `cleanup` `+2` at `FULL`, warps shifted) + `restore` (`+9` gates) | **14 hunks (`51 -> 58` gates)** | `34` distinct registers | `586, 588` lowered (`{6:16, 7:52} -> {6:18, 7:50}`) | **`-12 H1 + 18 H2 - 4 H3 - 6 H4 + 2 H5`** | **`-4,213,906`** vs `2*BE = -4,182,600` $\implies$ **`+31,306` surrogate margin** |

### 2.1 Edit 1: `R1_E42` (`restore[162:188]`, `26 -> 33` Gates, Skipping `{22, 40, 54, 63}`, `-8 H1 + 4 H2 = -19,984`)
*(From PR #3042 by dcharb78, superseding PR #3015's single-register edit `R1` on `restore[178:180]`; subsequently audited in external PRs #3050 and #3114.)*
- **Exact $\mathbb{Q}$-Linear Map (`old` and `new` are 100% identical across all 14 touched registers):**
  $$X_{18}' = -X_{226}, \quad X_{22}' = -X_{230}, \quad X_{108}' = -X_{22} + 2 X_{34},$$
  $$X_{226}' = -\frac{1}{4} X_{18} - \frac{1}{4} X_{40} + \frac{1}{2} X_{54}, \quad X_{228}' = \frac{1}{4} X_{22} - \frac{1}{2} X_{34} + \frac{1}{4} X_{108},$$
  $$X_{230}' = -\frac{1}{4} X_{22} + \frac{1}{2} X_{34} - \frac{1}{4} X_{40} + \frac{1}{4} X_{45} + \frac{1}{2} X_{54} + \frac{1}{4} X_{61} + \frac{1}{4} X_{63} - \frac{1}{4} X_{92} + \frac{1}{4} X_{103} + \frac{1}{4} X_{228} + \frac{1}{4} X_{230},$$
  and $X_r' = X_r$ for $r \in \{34, 40, 45, 54, 61, 63, 92, 103\}$.
- **Literal Gate Sequence (`33` gates in `new` vs `26` in `old`):**
  1. **Registers `40` and `54` via swap with `226` at Group B's rank-7 subspace $W_B = V_{25,42,51} = [256, 128, 64, 34, 17, 11, 4]$ and `18` at $\text{FULL} = [256, 128, 64, 32, 16, 8, 4, 2, 1]$ (`NEW[0..8]` and `NEW[20..25]`):**
     - `NEW[0..3]` at $W_B$ ($\dim 7$): `['add', 40, 54, -2, 1]`, `['add', 40, 226, -1, 1]`, `['add', 226, 40, 1, 1]`, `['add', 40, 226, -1, 1]` (swapping $X_{40} - 2 X_{54}$ into `226` and $-X_{226}$ into `40` at $\dim 7$).
     - `NEW[4..8]` at $E_{42} = [256, 128, 64, 34, 16, 10, 4, 1]$ ($\dim 8$): `['add', 18, 226, 1, 1]`, `['scale', 18, 1, -4]`, `['add', 18, 226, -1, 1]`, `['add', 226, 18, 1, 1]`, `['add', 18, 226, -1, 1]` (setting $X_{226}' = -\frac{1}{4} X_{18} - \frac{1}{4} X_{40} + \frac{1}{2} X_{54}$ and leaving `18` with $-(X_{40} - 2 X_{54})$).
     - `NEW[20..21]` at $E_{42}$ ($\dim 8$): `['add', 230, 18, -1, 1]` and `['add', 230, 45, -1, 1]` (accumulating $X_{40} - 2 X_{54} - X_{45}$ into `230`).
     - `NEW[22..25]` at $\text{FULL}$ ($\dim 9$): `['add', 40, 18, -1, 1]`, `['add', 18, 40, 1, 1]`, `['add', 40, 18, -1, 1]`, `['add', 40, 54, 2, 1]` (swapping `18` and `40` at rank 9 so $X_{18}' = -X_{226}$, and uncomputing `-2*54` on `40` at rank 9). Both `40` and `54` skip $E_{42}$ and climb `7 -> 9` directly (`-4 H1 + 2 H2 = -9,992`).
  2. **Register `22` via swaps with `228` and `230` at Group A's rank-7 subspace $W_A = V_{30,42,52} = [256, 128, 64, 38, 20, 10, 1]$ (`NEW[9..19]`):**
     - `NEW[9..16]` at $W_A$ ($\dim 7$): `['add', 22, 34, -2, 1]`, 3-add swap `['add', 22, 228, -1, 1]`, `['add', 228, 22, 1, 1]`, `['add', 22, 228, -1, 1]`, and 4-add swap/transfer `['add', 22, 230, -1, 1]`, `['add', 230, 22, 1, 1]`, `['add', 22, 230, -1, 1]`, `['add', 230, 22, 1, 1]`. This places $X_{22}' = -X_{230}$ onto `22` already at $\dim 7$ ($W_A$), so `22` never touches $E_{42}$ and climbs `7 -> 9` directly at `'end'` (`-2 H1 + 1 H2 = -4,996`), while `228` and `230` carry $X_{22} - 2 X_{34}$ into `NEW[17..19]` (`['add', 228, 108, 1, 1]`, `['scale', 228, 1, 4]`, `['add', 108, 228, -4, 1]` at $E_{42}$).
  3. **Register `63` via carrier `61` at $V_{45} = V_{7,42,45} = [256, 128, 64, 35, 16, 11, 5]$ (`NEW[26..32]`, PR #3015's `R1`):**
     - `NEW[26]` at $V_{45}$ ($\dim 7$): `['add', 61, 63, 1, 1]`; `NEW[27]` at $E_{42}$ ($\dim 8$): `['add', 230, 61, -1, 1]`; `NEW[28]` at $\text{FULL}$ ($\dim 9$): `['add', 61, 63, -1, 1]` (so `63` skips $E_{42}$ and climbs `7 -> 9` directly, `-2 H1 + 1 H2 = -4,996`), followed by `NEW[29..32]` at $E_{42}$ ($\dim 8$): `['add', 230, 92, 1, 1]`, `['add', 230, 103, -1, 1]`, `['add', 230, 108, -1, 1]`, `['scale', 230, 1, -4]`.

### 2.2 Edit 2: `R2_E7` (`restore[190:203]`, `13 -> 15` Gates, Skipping `{5, 73}`, `-4 H1 + 2 H2 = -9,992`)
*(From PR #3042 by dcharb78; subsequently audited in external PRs #3050 and #3114.)*
- **Exact $\mathbb{Q}$-Linear Map (`old` and `new` are 100% identical across all 6 touched registers):**
  $$X_5' = -X_{395}, \quad X_{59}' = -X_{363}, \quad X_{96}' = X_5 + X_{395}, \quad X_{73}' = X_{73},$$
  $$X_{363}' = -\frac{1}{4} X_{59} + \frac{1}{4} X_{73} + \frac{1}{4} X_{363}, \quad X_{395}' = -\frac{1}{4} X_5 + \frac{1}{4} X_{96} - \frac{1}{4} X_{395}.$$
- **Literal Gate Sequence (`15` gates in `new` vs `13` in `old`):**
  1. **Register `73` via pivot `363` at Group C's rank-7 subspace $W_C = V_{7,25,30} = [256, 128, 64, 32, 19, 11, 6]$ and carrier `59` at $\text{FULL}$ (`NEW[0..6]`):**
     - `NEW[0]` at $W_C$ ($\dim 7$): `['add', 363, 73, 1, 1]` (folding $X_{73}$ into `363` at $\dim 7$).
     - `NEW[1..5]` at $E_7 = [256, 128, 64, 32, 16, 8, 5, 3]$ ($\dim 8$): `['add', 59, 363, -1, 1]`, `['scale', 59, 1, -4]`, `['add', 59, 363, -1, 1]`, `['add', 363, 59, 1, 1]`, `['add', 59, 363, -1, 1]` (producing $X_{363}'$ on `363` and $-X_{363} - X_{73}$ on `59`).
     - `NEW[6]` at $\text{FULL}$ ($\dim 9$): `['add', 59, 73, 1, 1]` (cleaning $-X_{73}$ from `59` at rank 9 so `73` skips $E_7$ and climbs `7 -> 9` directly, `-2 H1 + 1 H2 = -4,996`).
  2. **Register `5` via pivot `395` at Group D's rank-7 subspace $W_D = V_{7,51,52} = [256, 128, 64, 37, 21, 8, 3]$ and carrier `96` at $\text{FULL}$ (`NEW[7..14]`):**
     - `NEW[7]` at $W_D$ ($\dim 7$): `['add', 395, 5, 1, 1]` (folding $X_5$ into `395` at $\dim 7$).
     - `NEW[8..13]` at $E_7$ ($\dim 8$): `['add', 96, 395, -1, 1]`, `['scale', 96, 1, 4]`, `['add', 96, 395, -1, 1]`, `['add', 395, 96, 1, 1]`, `['add', 96, 395, -1, 1]`, `['scale', 96, -1, 1]` (producing $X_{395}'$ on `395` and $X_5 + X_{395}$ on `96`).
     - `NEW[14]` at $\text{FULL}$ ($\dim 9$): `['add', 5, 96, -1, 1]` (setting $X_5' = -X_{395}$ at rank 9 so `5` skips $E_7$ and climbs `7 -> 9` directly, `-2 H1 + 1 H2 = -4,996`).

### 2.3 Edit 3: `B_586_438` + `helper_final["586"]` (`6` Hunks, `6 -> 5` Gates, Lowering `586` from $E_{30}$ to $V_{30,76,82}$, `+665` Surrogate Margin)
- **Algebraic, Subspace & `cleanup` Mechanism:**
  In `w_base`, entering helper `586` (`start_extra = [30]`, $\dim 1$) and dying cold helper `438` ($\dim 3$ at `B[759]: 586 += 438`) feed target `136` via `B[52]: 136 += 1/2*586` ($\dim 1$) and `B[784]: 136 -= 1/2*586` ($\dim 6$). Because `B[759]: 586 += 438` occurs between `B[52]` and `B[784]`, the net contribution of `B[52]` and `B[784]` to wire `136` is simply:
  $$\frac{1}{2} X_{586} - \frac{1}{2}(X_{586} + X_{438}) = -\frac{1}{2} X_{438}.$$
  Later at `B[1215]: 136 += 75`, wire `136` receives **source register `75`** (which has no other readers after `B[794]` and ends at $\text{FULL}$, $\dim 9$). By deleting `B[52]`, moving `B[794]: 140 -= 1/2*438` to `B[784]` at the 4D join frame $J_{140,438} = [257, 129, 32, 30]$, and folding `75 -= 1/2*438` into `B[794]` at the 5D join frame $J_{75,438} = [257, 129, 70, 32, 30]$, both `438` and `586` traverse a monotone 5-step nested subspace tower entirely inside $L_{586} = V_{30,76,82} = E_{30} \cap E_{76} \cap E_{82} = [256, 128, 70, 32, 18, 12, 1]$ ($\dim 7$):
  $$U_{759}(3) \;\subset\; J_{140,438}(4) \;\subset\; J_{75,438}(5) \;\subset\; U_{1214,L}(6) \;\subset\; L_{586}(7).$$
  Compared with PR #3042, `B` loses 1 gate (`B[52]`), `restore` is unchanged except for the frame at `restore[85]`, and inverse-reverse `cleanup` gains 1 gate at $\text{FULL}$ (`75 += 1/2*438`), which costs no frame steps and leaves the total `B + restore + cleanup` gate count unchanged.
- **Literal 6 Hunks in `edits/EDITS.json` (`B_586_438`, `6 -> 5` gates total):**
  1. **Hunk 0 (`B[52:53]`, `1 -> 0` gates):** deletes `['add', 136, 586, 1, 2, [30]]` ($\dim 1$), shifting all `B` warps with position $> 52$ by $-1$.
  2. **Hunk 1 (`B[784:785]`, `1 -> 1` gates):** replaces `['add', 136, 586, -1, 2, [289, 161, 64, 18, 10, 6]]` ($\dim 6$) with `['add', 140, 438, -1, 2, [257, 129, 32, 30]]` ($\dim 4$, normals `[6, 10, 12, 18, 20, 24, 30, 64, 70, 74, ...]`).
  3. **Hunk 2 (`B[794:795]`, `1 -> 1` gates):** replaces `['add', 140, 438, -1, 2, [256, 128, 76, 32, 30, 1]]` ($\dim 6$) with `['add', 75, 438, -1, 2, [257, 129, 70, 32, 30]]` ($\dim 5$, normals `[6, 24, 30, 74, 76, 82, 84, ...]`).
  4. **Hunk 3 (`B[1214:1215]`, `1 -> 1` gates):** lowers the frame of `['add', 144, 438, -1, 2]` from `[256, 128, 70, 32, 20, 10, 1]` ($\dim 7$, normals `[30, 74, 84]`) to `[256, 128, 70, 32, 30, 1]` ($\dim 6$, normals `[6, 24, 30, 74, 76, 82, 84]`).
  5. **Hunk 4 (`B[1230:1231]`, `1 -> 1` gates):** lowers the frame of `['add', 187, 586, -1, 2]` from `[288, 160, 64, 18, 10, 6, 1]` ($\dim 7$, normals `[30, 416, 446]`) to `[288, 160, 70, 18, 12, 1]` ($\dim 6$, normals `[30, 76, 82, 416, 446, 492, 498]`).
  6. **Hunk 5 (`restore[85:86]`, `1 -> 1` gates):** lowers the frame of `['add', 586, 438, -1, 1]` from `[256, 128, 64, 32, 18, 10, 6, 1]` ($\dim 8$, $E_{30}$) to `[256, 128, 70, 32, 18, 12, 1]` ($\dim 7$, $V_{30,76,82}$), and lowers `helper_final["586"]` from `[256, 128, 64, 32, 18, 10, 6, 1]` (`8` basis vectors) to `[256, 128, 70, 32, 18, 12, 1]` (`7` basis vectors, reducing `width(586)` from $8 - 1 = 7$ to $7 - 1 = 6$).
- **Exact Per-Register Profile Delta (`B_586_438` + `helper_final["586"]`):**
  - `586`: `[1, 3, 6, 7, 8] -> [1, 3, 6, 7]` (`-1 H1 = -2,116,671`)
  - `136`: `[0, 1, 2, 6, 7, 8] -> [0, 1, 2, 7, 8]` (`-1 H1 - 1 H4 + 1 H5 = -9,006`)
  - `140`: `[0, 1, 2, 6, 7, 8] -> [0, 1, 2, 4, 7, 8]` (`-1 H1 + 1 H2 + 1 H3 - 1 H4 = +3,102`)
  - `75`: `[1, 2, 3, 7, 9] -> [1, 2, 3, 5, 7, 9]` (`+2 H2 - 1 H4 = +9,979`)
  - `438`: `[0, 1, 2, 3, 6, 7, 8, 9] -> [0, 1, 2, 3, 4, 5, 6, 7, 9]` (`+1 H1 + 1 H2 - 1 H3 = +6,877`)
  - `144`: `[0, 1, 2, 4, 7, 8] -> [0, 1, 2, 4, 6, 7, 8]` (`+1 H1 + 1 H2 - 1 H3 = +6,877`)
  - `187`: `[0, 1, 2, 4, 7, 8] -> [0, 1, 2, 4, 6, 7, 8]` (`+1 H1 + 1 H2 - 1 H3 = +6,877`)
  - **Total for `B_586_438`:** **`+6 H2 - 2 H3 - 3 H4 + 1 H5 = -2,091,965` units/call** vs rounded guide `BE = -2,091,300` $\implies$ **`+665` surrogate margin per call**.

### 2.4 Edit 4: `B_588_440` + `helper_final["588"]` (`6` Hunks, `6 -> 5` Gates, Lowering `588` from $E_{30}$ to $V_{30,97,127}$, `+665` Surrogate Margin)
- **Algebraic, Subspace & `cleanup` Mechanism:**
  Symmetrically, entering helper `588` (`start_extra = [30]`, $\dim 1$) and dying cold helper `440` ($\dim 3$ at `B[763]: 588 += 440`) feed target `221` via `B[57]: 221 -= 588` ($\dim 1$) and `B[789]: 221 += 588` ($\dim 6$), whose net contribution to `221` is $-X_{588} + (X_{588} + X_{440}) = +X_{440}$. Deleting `B[57]`, moving `172 += 440` to `B[789]` at the 4D join frame $J_{172,440} = [268, 161, 65, 30]$, and folding `84 += 440` into **source register `84`** at `B[799]` (before `B[1223]: 221 += 84`) at the 5D join frame $J_{84,440} = [262, 161, 65, 20, 10]$ routes `440` and `588` along the 5-step nested subspace tower inside $L_{588} = V_{30,97,127} = E_{30} \cap E_{97} \cap E_{127} = [256, 128, 65, 33, 18, 10, 6]$ ($\dim 7$):
  $$U_{763}(3) \;\subset\; J_{172,440}(4) \;\subset\; J_{84,440}(5) \;\subset\; U_{1222,L}(6) \;\subset\; L_{588}(7).$$
  Compared with PR #3042, across `B_586_438` and `B_588_440` combined, `B` loses 2 gates (`B[52]` and `B[57]`), `restore` is unchanged except for the frames at `restore[85]` and `restore[88]`, and `cleanup` gains 2 gates at $\text{FULL}$ (`75 += 1/2*438` and `84 -= 440`), costing no frame steps and keeping the total gate count unchanged.
- **Literal 6 Hunks in `edits/EDITS.json` (`B_588_440`, `6 -> 5` gates total):**
  1. **Hunk 0 (`B[57:58]`, `1 -> 0` gates):** deletes `['add', 221, 588, -1, 1, [30]]` ($\dim 1$), shifting all `B` warps with position $> 57$ by an additional $-1$.
  2. **Hunk 1 (`B[789:790]`, `1 -> 1` gates):** replaces `['add', 221, 588, 1, 1, [256, 161, 97, 18, 10, 6]]` ($\dim 6$) with `['add', 172, 440, 1, 1, [268, 161, 65, 30]]` ($\dim 4$, normals `[12, 18, 30, 97, 109, 115, 127, ...]`).
  3. **Hunk 2 (`B[799:800]`, `1 -> 1` gates):** replaces `['add', 172, 440, 1, 1, [268, 128, 64, 32, 30, 1]]` ($\dim 6$) with `['add', 84, 440, 1, 1, [262, 161, 65, 20, 10]]` ($\dim 5$, normals `[30, 97, 127, 160, 190, 193, 223, 266, 276, ...]`).
  4. **Hunk 3 (`B[1222:1223]`, `1 -> 1` gates):** lowers the frame of `['add', 162, 440, 1, 1]` from `[262, 128, 64, 32, 20, 10, 1]` ($\dim 7$, normals `[30, 266, 276]`) to `[262, 128, 65, 33, 20, 10]` ($\dim 6$, normals `[30, 97, 127, 266, 276, 363, 373]`).
  5. **Hunk 4 (`B[1238:1239]`, `1 -> 1` gates):** lowers the frame of `['add', 196, 588, 1, 1]` from `[256, 160, 96, 18, 10, 6, 1]` ($\dim 7$, normals `[30, 224, 254]`) to `[256, 161, 96, 18, 10, 6]` ($\dim 6$, normals `[30, 97, 127, 129, 159, 224, 254]`).
  6. **Hunk 5 (`restore[88:89]`, `1 -> 1` gates):** lowers the frame of `['add', 588, 440, -1, 1]` from `[256, 128, 64, 32, 18, 10, 6, 1]` ($\dim 8$, $E_{30}$) to `[256, 128, 65, 33, 18, 10, 6]` ($\dim 7$, $V_{30,97,127}$), and lowers `helper_final["588"]` from `[256, 128, 64, 32, 18, 10, 6, 1]` (`8` basis vectors) to `[256, 128, 65, 33, 18, 10, 6]` (`7` basis vectors, reducing `width(588)` from $8 - 1 = 7$ to $7 - 1 = 6$).
- **Exact Per-Register Profile Delta (`B_588_440` + `helper_final["588"]`):**
  - `588`: `-2,116,671`; `221`: `-9,006`; `172`: `+3,102`; `84`: `+9,979`; `440`: `+6,877`; `162`: `+6,877`; `196`: `+6,877`.
  - **Total for `B_588_440`:** **`+6 H2 - 2 H3 - 3 H4 + 1 H5 = -2,091,965` units/call** vs rounded guide `BE = -2,091,300` $\implies$ **`+665` surrogate margin per call**.

---

## 3. Single-Move Negative Controls & 91-Helper Exhaustion Proofs

### 3.1 Single-Move Negative Controls: Why `586` and `588` Lose Under Stage-1 Alone (`-3,345`) and Stage-2 Alone (`-973`), But Gain `+665` Surrogate Margin Each (`+1,330` Together) When Coupled

In PR #2979 (`construction/STAGE-PRICES.json`, lines 773–803), helpers `586` and `588` were the **only two restored helpers in the entire word** whose causal lower bounds $L_{586} = V_{30,76,82}$ and $L_{588} = V_{30,97,127}$ already had dimension 7 ($k = 0$ blocking causal gates) that remained unlowered at `end_dim = 8` ($E_{30}$). Evaluating the two single-move controls against the coupled rewrite explains why neither a frame-only solver (PR #2979 Stage 1 / PR #3065) nor a fixed-endpoint gate search (PR #2957 Stage 3 / PR #3114) could discover this improvement:

| Configuration (per helper `586` or `588`, and joint for the pair) | `helper_final` (`586, 588`) | `B`-Phase Gate Topology | Local Profile $\Delta$ (per helper / joint) | Local Climb Cost $\Delta$ (per helper / joint) | Rounded Guide Charge (`BE = 2,091,300`) | **Surrogate Margin (per helper / joint; $\kappa$ carries the claim)** |
|---|---|---|---|---|---|---|
| **1. Stage-1 Lowering Alone (Fixed Scalar Gates)** | $\dim 7$ ($V_{30,76,82}$, $V_{30,97,127}$) | Unfolded (`B[52], B[784]` and `B[57], B[789]` kept; frames intersected with $L_h$) | `-1 H1 + 7 H2 - 2 H3 - 2 H4` each<br>(`-2 H1 + 14 H2 - 4 H3 - 4 H4` joint) | `-2,087,955` each<br>(`-4,175,910` joint) | `+2,091,300` each<br>(`+4,182,600` joint) | **`-3,345` each (`-6,690` joint — LOSES)** |
| **2. Stage-2 Carrier Fold Alone at `dim 8` (Fixed Endpoints)** | $\dim 8$ ($E_{30}$, unchanged) | Folded (`B[52], B[57]` deleted; `140, 172` at $\dim 4$; `75, 84` at $\dim 6 = \text{meet}(B[1214], B[1215])$) | `-1 H1 + 2 H2 - 2 H4 + 1 H5` each<br>(`-2 H1 + 4 H2 - 4 H4 + 2 H5` joint) | `+973` each<br>(`+1,946` joint) | `0` (`width 7` unchanged) | **`-973` each (`-1,946` joint — LOSES)** |
| **3. Coupled Carrier Fold + `dim 7` Lowering (`B_586_438`, `B_588_440`)** | **$\dim 7$ ($V_{30,76,82}$, $V_{30,97,127}$)** | **Folded along 5-step subspace towers (`140, 172` at $\dim 4$; `75, 84` at $\dim 5$)** | **`+6 H2 - 2 H3 - 3 H4 + 1 H5` each**<br>**(`+12 H2 - 4 H3 - 6 H4 + 2 H5` joint)** | **`-2,091,965` each**<br>**(`-4,183,930` joint)** | **`+2,091,300` each**<br>**(`+4,182,600` joint)** | **`+665` each (`+1,330` joint — WINS)** |

- **Origin of the `+4,983` per-helper (`+9,966` joint) positive cross-term synergy:**
  1. Under **Stage-1 lowering alone**, keeping `B[784]: 136 -= 1/2*586` (and `B[789]: 221 += 588`) inside $L_{586}$ forces `B[784]`'s frame to drop from $\dim 6$ to $\dim 5$, which adds an extra intermediate stop to both `586` (`[1, 3, 5, 6, 7]` instead of `[1, 3, 6, 7]`, costing `+6,877`) and `136` (`[0, 1, 2, 5, 7, 8]` instead of `[0, 1, 2, 7, 8]`, costing `+3,102` vs baseline and `+12,108` vs the folded `[0, 1, 2, 7, 8]` trajectory).
  2. Under **Stage-2 folding at `dim 8` alone**, `B[1214]: 144 -= 1/2*438` remains at $\dim 7$ and `restore[85]: 586 -= 438` remains at $\dim 8$ ($E_{30}$), so folding `438` into `140` ($\dim 4$) and `75` ($\dim 6$) inserts an extra stop on `438` (`[0, 1, 2, 3, 4, 6, 7, 8, 9]`, costing `+6,877`) while `586` only saves `-8,098` (`[1, 3, 7, 8]` vs `[1, 3, 6, 7, 8]`), resulting in a surrogate margin of `-973` per helper.
  3. When **coupled**, `B[1214]` and `B[1230]` drop to $\dim 6$ inside $L_{586}$ while `586` and `136` bypass `B[784]` completely, eliminating both the `+6,877` stop on `586` and the `+12,108` stop on `136` simultaneously (`-3,345 - 973 + 4,983 = +665` surrogate margin per helper).

### 3.2 Exhaustive 91-Helper Causal Lower-Bound Scan & Structural Obstruction Proofs for All Remaining Candidates

Tracing the causal lower bound $L_h = \text{lo}[\text{last}[h]]$ across all **91 restored helpers** in the word (`26` at `end_dim = 4`, `30` at `end_dim = 7`, `35` at `end_dim = 8`) by the minimum number $k$ of blocking causal gates in `B + restore` whose removal drops $\dim(L_h)$ shows that beyond `586` and `588` ($k = 0$), every remaining candidate with $k \le 2$ is blocked by one of three exact structural locks:

1. **The Double Cone Lock on Entering Quartet Sisters `584` and `590` ($\dim 8 \to 7$ at $E_{51}$, $k = 1$ blocking gate):**
   - **Free-Operator Algebra Status (`PASS`):** Replacing `B[59]` with `214 += 566`, `B[1196]` with `168 -= 1/2*439`, and `B[1204]` with `214 += 444` while deleting `B[13, 48, 60, 753, 765]` and `restore[82, 91]` leaves `584` and `590` with **0 gates in the entire circuit** and passes 100% of `audit_local.py`'s forward and dual free-operator checks across all 632 inputs.
   - **Causal Frame-Chain Obstruction (`FAIL`, 28–74 DAG `lo <= hi` violations across all chronological placements):** Why did `586` and `588` ($E_{30}$) lower cleanly to $\dim 7$ while their even-quartet sisters `584` and `590` ($E_{51}$) are locked at $\dim 8$?
     - For `586/438` (and `588/440`), both remaining consumers `187` (`B[1230]`, receiving dying helper `506`) and `144` (`B[1214]`, receiving dying helper `530`) have causal lower bounds contained inside the **same** 7D subspace $L_{586} = V_{30,76,82}$ (and $L_{588} = V_{30,97,127}$).
     - For `584/439` (and `590/444`), the two consumers sit in **transverse 7D cones** inside $E_{51}$: the right consumer `115` (`B[1244]: 115 -= 1/2*439`, or `130` at `B[1252]: 130 += 444`) receives **post-warp cold helper `273`** (`B_WARP[541]`, or `289` from `B_WARP[545]`) at $\text{lo\_dim} = 5$ (`[21, 51, 67, 86, 112]`), hard-pinning `B[1244]` to $\text{lo} = \text{hi} = W_{\text{right}} = E_{51} \cap E_{67} \cap E_{112}$ ($\dim 7$); whereas the left consumer `168` (`B[1196]`, or `214` at `B[1204]`) receives entering helper `554` (`B[771]: 168 += 554`, or `566` at `B[59]`), which is upper-bounded by `B[913]: 273 += 554` (`hi_dim = 6`) inside $U_{6,\text{left}} \subseteq W_{\text{left}} = E_{51} \cap E_{82} \cap E_{97}$ ($\dim 7$). Because $U_{6,\text{left}} \not\subseteq W_{\text{right}}$, their join is $\text{join}(U_{6,\text{left}}, W_{\text{right}}) = E_{51}$ ($\dim 8$).

2. **The Restored-Dirt Isolation Lock on Entering Carrier Helpers `531, 543` and `554, 555, 566, 567` ($\dim 8 \to 7$, $k = 1$ `B` gate):**
   - **Causal Frame-Chain Status (`PASS` when `B[916]: 305 += 531` and `B[918]: 321 += 543` are removed):** Deleting `B[916]` and `B[918]` alone drops `531` and `543` to $L_{586} = V_{30,76,82}$ and $L_{588} = V_{30,97,127}$ ($\dim 7$, `width 7 -> 6`) with 0 DAG violations, because `restore[57..59]` and `restore[64..66]` automatically lie inside $L_{586}$ and $L_{588}$.
   - **Free-Operator Algebra Obstruction (`FAIL`, `bad_read = [531, 587]` / `[543, 589]`, `bad_targets = [36, 37, 46, 47]`):** At `B[275]: 351 -= 531`, `B[659]: 351 += 1`, and `B[660]: 531 += 351`, helper `531` isolates the clean sum $X_{351} + X_1$ (cancelling $X_{531}$), while `351` retains $-X_{531}$ and immediately absorbs $-\frac{1}{2}(X_{587} + X_{436})$ at `B[661, 786]`. Because consumer `305` is a **warped cold helper** (`B_WARP[385]` before `B[916]` and `B_WARP[611]` after `B[1586]`), routing `305` onto `351` pollutes `305` and output targets `36, 37, 46, 47` with restored helpers `531, 587` and breaks inverse-warp `cleanup` across `B_WARP[611]`. The exact same lock holds for `543` (`321`/`367`), `554, 555` (`273`), and `566, 567` (`289`).

3. **The Grassmann `6 + 6 - 4 = 8` and `5 + 5 - 3 = 7` Fork-and-Uncompute Lock on the 12 Three-Gate Cold Helpers (`500, 501, 512, 513` at $\dim 8$ and `572..575, 580..583` at $\dim 7$, $k = 1$ gate):**
   - Each of these 12 cold helpers $h$ has 1 gate in `A` ($p \mathrel{-}= h$) and 3 post-`A` gates: `B[idx_fold]: h += p` ($\dim 3$), `B[idx_c1]: c_1 += h` ($\dim 6$ or $5$), and `restore[idx_rest]: h -= p` ($\dim 8$ or $7$), while partner $p$ feeds a second consumer `B[idx_c2]: c_2 += p` ($\dim 6$ or $5$).
   - **Why `restore: h -= p` is locked at $\dim 8$ (for `500..513`) and $\dim 7$ (for `572..583`):** At `restore: h -= p`, the gate frame must contain $\text{join}(\text{lo}[c_1], \text{lo}[c_2])$. By Grassmann's identity $\dim(U_1 + U_2) = \dim(U_1) + \dim(U_2) - \dim(U_1 \cap U_2)$:
     - For `500, 501` ($p = 310, 308$ at $E_{102}$) and `512, 513` ($p = 326, 324$ at $E_{75}$), $\dim(\text{lo}[c_1]) = 6$, $\dim(\text{lo}[c_2]) = 6$, and $\dim(\text{lo}[c_1] \cap \text{lo}[c_2]) = 4$, forcing $\dim(\text{join}(\text{lo}[c_1], \text{lo}[c_2])) = 6 + 6 - 4 = 8$.
     - For `572..575, 580..583` ($p = 408, 105, 412, 414, 424, 44, 428, 430$), $\dim(\text{lo}[c_1]) = 5$, $\dim(\text{lo}[c_2]) = 5$, and $\dim(\text{lo}[c_1] \cap \text{lo}[c_2]) = 3$, forcing $\dim(\text{join}(\text{lo}[c_1], \text{lo}[c_2])) = 5 + 5 - 3 = 7$.
   - **Why free-algebra splitting (`c_1 += h` at $\dim 3$ + `c_1 += p` at $\dim 6/5$) fails causally (`26` DAG violations per helper):** Consumer $c_1$ is warped by `B_WARP` immediately before `B[idx_c1]` (with pre-warp `hi_dim = 2`), and consumer $c_2$ executes chronologically *before* $c_1$ (`B[825..828]` before `B[835..844]`; `B[853..864]` before `B[885..896]`), so $h$ cannot be discharged into $c_1$ before $c_1$'s `B_WARP` nor uncomputed against $p$ before $p$ climbs to $\text{lo}[c_2]$.

---

## 4. Relaxation Cap (`certificates/RELAX-CAP.json`) & Literal $T=74$ Allocation (`T74_optimal_idle39`)

- **Fixed-Capacity Relaxation Cap (`tools/relax_exact.py`, `check_cap.py`):**
  The exact same 10-pattern optimal LP basis over all 2,551 count-vector patterns remains primal feasible and dual optimal for the shifted width inventory `{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}` and local profile `{1:2433, 2:724, 3:228, 4:102, 5:20, 8:8}`:
  - Per-replica basis counts (`certificates/RELAX-CAP.json`): `8:[8]` $\times 672$, `32:[7,8,8,9]` $\times 61/4$, `32:[4,9,9,9]` $\times 234$ (`idle=1`), `48:[9,9,9,9,9]` $\times 1323/20$ (`idle=3`), `32:[9,9,9]` $\times 75/4$ (`idle=5`), `32:[6,8,9,9]` $\times 162$, `32:[5,9,9,9]` $\times 18$, `16:[8,8]` $\times 53/4$, `16:[7,9]` $\times 1739/4$, and `48:[]` $\times 7637/20$ (`idle=48`).
  - Shifting two roles per call from width $7 \to 6$ (`+18` bins of `32:[6,8,9,9]` per replica) eliminates $9/10$ of an `idle=3` bin and $9/2$ of an `idle=5` bin per replica while freeing $+9/10$ of a completely empty `48:[]` (`idle=48`) bin per replica (`+66.6` empty `cap=48` bins across $T=74$), raising the exact relaxation cap to:
    $$\kappa_{\text{cap}} \in \left[\frac{17297774946785970118869}{10^{25}},\; \frac{1729777494678597011887}{10^{24}}\right] = [0.0017297774946785970118869,\; 0.0017297774946785970118870].$$
- **Literal $T=74$ Realization (`allocation/FILL.json.gz`, `T74_optimal_idle39`):**
  - Because `width(586)` and `width(588)` shrink from $7 \to 6$ (`allocation/PROVIDERS.json` indices `356` and `358`), naive in-place compaction without repacking `FILL.json.gz` would open 1-unit idle holes inside 1,332 zero-idle bins (`16:[7,9]` and `32:[7,7,9,9]`).
  - Applying the LP basis shift on the $T=37$ chronological Hall-marriage window structure (converting 1 early `32:[7,7,9,9]` bin and 88 early `16:[7,9]` bins with `hi <= 44` to `32:[6,8,9,9]` and `16:[8,8]` to satisfy Hall's condition on the 45 early calls $t \in [0, 44]$, while converting 420 late `16:[8,8]` bins to `16:[7,9]` and adding $+666$ `32:[6,8,9,9]` bins per 37 replicas) and consolidating the two $T=37$ remainder bins across the two halves of $T=74$ yields `allocation/FILL.json.gz` (`271,728` role rows, `SHA256 = 68b8bae90144248774b1920cd27f9519caa3dc427704d8a9da6d4c491d912fc4`):
    - **Literal $T=74$ idle histogram:** `{1: 17314, 3: 4893, 5: 1390, 39: 1, 48: 28256}` (`+66` completely empty `48:[]` bins, `-63` `idle=3` bins, and `-338` `idle=5` bins vs PR #2979 / PR #3042).
    - **Complete $T=74$ paid profile (`allocation/PROFILE.json`):** `{1: 1637692, 2: 482184, 3: 156741, 4: 67932, 5: 14710, 8: 5328, 39: 1, 48: 28256}` (rank mass $74 \times 65,088 = 4,816,512$).
    - **Certified literal $T=74$ root (`tools/root.py`):** **`κ in [0.0017297760894051203342384, 0.0017297760894051203342385]`** (headline `0.001729776089405120334238 - 10^-46 - 10^-70`).

---

## 5. Verification & Replay

1. **Bounded Registered Check (`run_registered.py`, Python 3.12 stdlib, ~55s):**
   - `verify_manifest.py` / `MANIFEST.json`: verifies exact SHA256 pins for all 155 files in the package.
   - `verify.py`: rebuilds all stage-1, stage-2, stage-3 (`data/WORD-{base,extra}.json.gz`), and stage-4 (`edits/FINAL-WORD-{base,extra}.json.gz`) words from `data/PARENT-{base,extra}.json.gz` and the declared records; runs `vendor/audit_local.py` (`PASS_INDEPENDENT_EXACT_BORROWING_WORD`, forward and dual across all 632 inputs, 91 restored endpoints and buffers) and `vendor/preload_move.py` (`frame_report`) on every stage word; and rejects **100 semantic tamper controls** (`{'stage1': 20, 'stage2': 52, 'stage3': 14, 'stage4': 14}`).
   - `edits/edits_review.py`: independently applies `edits/declared_edits.py` (`R1_E42`, `R2_E7`, `B_586_438`, `B_588_440`), runs `vendor/audit_local.py` forward and dual over all 632 inputs on both parent and candidate words, and rejects **21 semantic tamper controls per word** (`PASS_INDEPENDENT_EDIT_REVIEW {'base': 21, 'extra': 21}`).
   - `check_allocation.py`: runs the vendored PR #2839 owner engine (`allocation/vendor/independent_owners.py`) on `allocation/FILL.json.gz` (`271,728` roles, six width classes `{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}`, 91-buffer physical stock `66,813`), rejects 5 owner controls, and verifies strict moment improvement over PR #2969 (`PASS_RANK7_LITERAL_OWNERS_AND_EXACT_MOMENT`).
   - `check_cap.py`: verifies Fractions-only relaxation cap certificates (`certificates/RELAX-CAP.json` and `certificates/RELAX-STAGES.json`), the literal gap `1.4053e-9`, 5 cap controls, and exact gains over PR #2979, PR #2969, PR #2966, PR #2957, and PR #2942 (`PASS_LITERAL_ALLOCATION_BELOW_FIXED_INVENTORY_CAP_WITH_RECORDED_GAP`).
   - Cryptographic binding of all stored receipts in `evidence/` (`OVERLAY-DERIVATION.json`, `EDITS-DERIVATION.json`, `EDITS-REVIEW.json`, `ADAPTER-DERIVATION.json`, `FULL-NATIVE-RECEIPT.json`, `ADMISSION-RESULT.json`, `RELEASE-RECEIPT.json`, `FULL-REPLAY-RESULT.json`) to the exact words, allocation, and `CLAIM.json`.
2. **Complete Cold/Retained Replay (`reproduce.py` & `verify_release.py`):**
   ```sh
   python3.12 -B scripts/research_package.py --package research/rank7-coupled-586-588-carrier-fold
   OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
     python3.12 -B research/rank7-coupled-586-588-carrier-fold/reproduce.py --repo . --work /tmp/rank7-coupled-replay --jobs 2
   ```

---

## Base Package Lineage Summary (PR #2979, `mdumitrean`)

This package retains PR #2979's three-stage producer chain (`data/PARENT-{base,extra}.json.gz` $\to$ `data/WORD-{base,extra}.json.gz`) unchanged before applying Stage 4 (`edits/EDITS.json` $\to$ `edits/FINAL-WORD-{base,extra}.json.gz`):
- **Stage 1 (`data/STAGE1-FRAME-EDITS.json`):** Joint codimension-2 end-frame lowering of 22 restored helpers in five shared rank-7 groups (`V45`: `249, 251, 265, 267`; `A`: `331, 450, 451, 508, 509`; `B`: `299, 448, 449, 484, 485`; `C`: `452, 453, 532, 533`; `D`: `454, 455, 556, 557`; 139 gate frame edits, margin `+142,394` units; single-lowering negative controls verified in `verify.py` and independently in open PR #3112).
- **Stage 2 (`data/TRANSFORM-{226,228,230,363,395}.json`):** Five rank-8 paired extractions at normal 42 (`226, 228, 230`) and normal 7 (`363, 395`), raising the buffer count from 86 to 91 (margin `+66,903` units).
- **Stage 3 (`data/REWRITES-2957.json`):** Jeremy Kothe's fourteen PR #2957 rewrites re-addressed with exact preimages (`vendor/declared_rewrites.py`, margin `+52,350` units).

---

## Open next questions

1. **Closing the `1.4053e-9` integer-rounding gap at $T=740$ ($20 \mid T$):**
   The optimal LP basis in `certificates/RELAX-CAP.json` has per-replica counts with denominators $4$ and $20$ (`idle_per_replica = {1: 234, 3: 1323/20, 5: 75/4, 48: 7637/20}`), which become exact integers whenever $20 \mid T$. Composing the `{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}` words with a $T=740$ chronological flow allocation (as PR #3024, #3030, #3051, #3054, #3103, #3115 did for the `{6:16, 7:52}` inventory) should close the remaining `1.4053e-9` integer gap and reach `RELAX-CAP in [0.0017297774946785970118869, 0.0017297774946785970118870]`.
2. **Unlocking the Double Cone Lock on `584` and `590` via joint `B_WARP` re-synthesis:**
   In the free operator algebra, entering helpers `584` and `590` can be completely eliminated (`0` gates in `A+B+restore` across all 632 forward and dual inputs), but post-warp cold helpers `273` and `289` (`B_WARP[541, 545]`) pin right consumers `115` and `130` to $W_{\text{right}} = E_{51} \cap E_{67} \cap E_{112}$ ($\dim 7$) while entering helpers `554` and `566` pin left consumers `168` and `214` to $U_{6,\text{left}} \subseteq E_{51} \cap E_{82} \cap E_{97}$ ($\dim 6$). Jointly re-synthesizing `B_WARP[541, 545]` on `273, 289` and the `554, 566` consumer cone is required to align the two 7D cones inside $E_{51}$.
3. **Composing with native-tariff contractions (PR #3056, #3060, #3076):**
   Re-addressing the commuting `A`/`restore`/`cleanup` native-tariff contractions from PR #3056, #3060, and #3076 on top of `edits/FINAL-WORD-{base,extra}.json.gz` can lower the native primitive operation count while preserving the `{1:2433, 2:724, 3:228, 4:102, 5:20, 8:8}` paid profile and `{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}` width inventory.

---

## Credit

- **PR #2979 (`mdumitrean`, Marius-Paul Dumitrean)**: the base words, Stage 1–3 producer, rank-7 overlay, cap machinery, and checkers.
- **PR #3015 (`jeremykothe2`, Jeremy Kothe)**: the declared literal edit stage (`edits/`, `tools/build_edits.py`, `edits/edits_review.py`) and edit `R1` (`63` via carrier `61`).
- **PR #3042 (`dcharb78`, with AI assistance)**: the six restore carrier/pivot skips (`R1_E42`, `R2_E7`) on PR #2979's words that serve as the direct starting words for `B_586_438` and `B_588_440`.
- **Inherited lineage**: Jeremy Diviney (PR #2908), Mason Hale (PR #2917), Jeremy Kothe (PR #2966 / #2957 / #2948 / #2894 / #2833), Dugongue (PR #2969 / #2863 / #2839), Marius-Paul Dumitrean (PR #2942 / #2930 / #2843), RossRichardson (PR #2918), Yiyang Lu (PR #2857 / #2848), philippeVV (PR #2853), Gareth Davidson (PR #1995 / #2013), Tekalign (`independent_owners.py`), icekylinx (`audit_local.py`), and themilkman216.
- **New here (`dcharb78`, with substantial AI assistance)**: the coupled `B + restore` dying-helper carrier folds (`B_586_438` and `B_588_440`) and `helper_final` lowerings on `586` and `588`, the single-move negative controls and 91-helper causal exhaustion proofs, the repacked `T74_optimal_idle39` allocation (`allocation/FILL.json.gz`), the 21-control per-word edit review and 100-control four-stage replay, and the complete fresh-native admission and release receipts. Apache-2.0.
