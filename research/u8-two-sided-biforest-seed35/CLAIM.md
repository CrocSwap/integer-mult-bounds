# Sprint claim: U8 two-sided signed bi-forest compensation (seed 35)

- **Track**: 20–39 (Complex supplier: improve one specific circuit, frame schedule,
  decoder, or paid recursive profile).
- **OS-random assignment seed**: **35** (`int.from_bytes(os.urandom(8), 'big') % 100`).
- **Start**: 2026-10-13 17:19 UTC. **Expected finish**: 2026-10-13 18:05 UTC.
- **Exact base commit**: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
- **Selected record at base**: reviewed conditional PR942 (`1960cfa919a0945d0ca4cb14ea96237000037903`),
  $\kappa = 1661960547713947/10^{18} = 0.001661960547713947$, on the U8 complex
  local word from PR869/870 (`73e86f69bf9a391e3c334999f7bbe3825dc42759` /
  `b734850dc348800942f0ffd1f0723fdec7539b2b`).
- **Object**: frame-zero arbitrary-helper compensation panel (`6,320` additions,
  `34,728` component primitives across `112` targets and `216` active unwrapped
  helpers) of the selected U8 complex word.
- **Three narrow candidates considered**:
  1. **Two-sided signed bi-forest compensation on the selected U8 word (selected)**:
     prove that leaf-before-parent helper-accumulating forests of arbitrary depth
     have $H^{-1} = I - \sum_b s_b e_{p(b)} e_b^T$ with zero ancestor cross-terms,
     and alternate exact target/helper superroot MSTs on U8's $112 \times 216$
     quarter-integer matrix $C$ to a coordinate-wise fixed point, breaking past
     the `10,883` target-only floor (PR932/PR961) and the disjoint helper-pair
     restriction (PR917).
  2. **4-primitive precondition lowering on U8** (transporting PR883/PR916 to U8):
     saves only `784` real primitives per orientation and largely duplicates PR883/PR916.
  3. **Common-frame scalar swap deferral on U8** (transporting PR969): smaller
     finite saving and does not address the open two-sided compensation question
     on the selected U8 word.
- **Coordination**: GitHub has no pinned sprint coordination issue (only open
  issues `#913` and `#650`), so this claim is recorded locally. Checked open and
  merged PRs through `#1077` (including newly merged `batch1047` on `main`);
  PR932 and PR961 study target-only forests on X4/U8, PR917 studies target forest
  + disjoint helper pairs on historical PR626 CK while leaving X4/U8 and general
  helper forests open, and concurrent bit-supplier PR1040/PR1047 study single-step
  post-star/target retuning on bit R439.
- **Expected deliverable**: one self-contained finite circuit package in
  `research/u8-two-sided-biforest-seed35/` with exact `Fraction` and independent
  integer-dyadic 737-column replay, Prim + all-edge cycle-inequality verification,
  native U8 emitter/auditor verification, and negative controls. No new $\kappa$.

## Completed result (single claim update)

Completed finite circuit construction and verification in
`research/u8-two-sided-biforest-seed35/`:
- At the coordinate-wise MST fixed point `(T5, H5)`, `100` target-forest edges
  (max edge depth 6) and `148` leaf-before-parent helper-forest edges (max edge
  depth 7) plus `1,284` residual additions (`1,780` total additions) reduce the
  U8 compensation panel from `34,728` to **`7,930` component primitives**
  (`15,860` real primitives).
- Complete U8 local scalar programs drop from `193,306 -> 139,710` forward and
  `193,354 -> 139,758` backward real primitives, saving **`53,596` real primitives
  per orientation**: **`5,906` beyond the `10,883` target-only forest floor**
  (PR932/PR961), **`2,074` beyond the `8,967` disjoint helper-pair comparator**
  (PR917 method transported to U8), and **`886` beyond one-pass `(T0, H1)`** (`8,373`).
- Both arithmetic engines (`Fraction` and sparse integer-dyadic rows on all `737`
  input columns), Prim and all `12,544 + 46,656` cycle-exchange inequalities,
  unchanged native `hpe_emit_local.py` / `hpe_audit_local.py` (`25` controls),
  and `12` package controls (including reversed helper preparation/restoration on
  depth-7 $H_5$) pass.
- Positive prefix peaks are `57` bits forward and `73` bits backward ($\le 192$);
  denominator powers remain `3` forward and `19` backward; paid child profile is
  unchanged (`{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}`). No new $\kappa$.
- **Submitted PR**: [PR #1080](https://github.com/CrocSwap/integer-mult-bounds/pull/1080)
  (branch `research/u8-two-sided-biforest-seed35`).
  Receipts: [`EXPECTED.json`](EXPECTED.json), [`RECIPE.json`](RECIPE.json),
  [`PROOF.md`](PROOF.md), [`VALIDATION.md`](VALIDATION.md).
