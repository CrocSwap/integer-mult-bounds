# Sixteen replicas on the seven-slot k8 word (#1018): conditional κ = 0.001672245809535804

This package runs the two-bank T16 whole-owner controller on [research/gauge44-slots](../gauge44-slots) (#1018).
The local word (`c2b29430…`), its 480 helper widths and the PR589 bit supplier are unchanged. The only new
object is a 16-replica owner map.

- **κ = 0.001672245809535804** (conservative 0.001672245806684428). That is +5.81×10⁻⁷ over #1018's T8
  κ 0.00167166528321877. The complex side binds.
- **Change:** T16 on #1018. `data/OWNERS.json.gz` (`fa087f7d…`, 69,120 whole-helper roles, 144 calls) is an exact
  pattern-flow LNS repack (integer pattern counts + König edge colouring) on the actual T16 window geometry. It is
  frozen data. The verifier runs no constructor and no optimizer: `t16/lift16.py` checks every role inside its
  owner's actual bridge-aware window, the controller audit re-derives the profile, and `t16/indep16.py` independently
  rechecks windows, whole widths, charts, prefix and row. Idle profile `{1:2256, 2:1, 3:410, 16:37, 48:4853}`.
  Prefix 397 < 512; physical row coefficient 16469 < 20161.
- **Code:** `code/` is byte-identical to the signed research/gauge44-barch-t16 code (the #870 T16 adaptation of
  #858's source edits). `t16/` holds #858's `build_parent.py` and the generic-R `lift16.py`/`indep16.py` (R taken from the
  word; the parent namespace stays at 504). The T8 package's `data/` moves to `data/T8/` and `data/SPEC-T8.json`;
  the `bind8` stage replays #1018's T8 admission.
- **Controls:** 69 admission, 12 bit-supplier, 15 controller mutations and 6 independent T16 controls.
- **Credit:** the T16 two-bank controller, parent lift, actual-window reconstruction and independent checker are
  Hao Yan's (@FanPUYen) [#858](https://github.com/CrocSwap/integer-mult-bounds/pull/858). The T16 code adaptation is
  from #870. The word and T8 package are #1018's (rohanarun's #987 slots on the #1005 leaver word).

## Verification

```sh
# 1. #1018's own replay (research/gauge44-slots README): it writes the new word's locals to /tmp/slots/local
python -B research/gauge44-slots/construction/slots/verify_slots.py \
  --main . --pr635 /tmp/gauge44-pr635 --baseline /tmp/lvc --work /tmp/slots
# 2. this package (about 2 minutes)
python -B research/gauge44-slots-t16/verify_manifest.py
python -B research/gauge44-slots-t16/verify_t16.py --main . --local /tmp/slots/local --work /tmp/slots-t16
# PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY 0.001672245809535804
```

Step 1 must use research/gauge44-slots itself: this package's inherited `verify_global.py` is removed, and the T8
admission runs inside `verify_t16.py` as `bind8`. Everything below is #1018's README, unchanged.

---

# Seven triangle-hybrid slots on the k8 leaver word: conditional κ = 0.00167166528321877

This package adds one construction layer to [research/gauge44-leaver8](../gauge44-leaver8) (#1005): seven
additional triangle-hybrid B-delivery slots on #1005's final word `db2c7cfb…`. **Credit:** the slot search and
the first two slots (X = 444, 446) are **rohanarun's #987**; the other five (X = 236, 238, 434, 436, 439) were found by
running #987's search on the k8 word. The mechanism is NewBArch's #869 triangle-hybrid delivery.

- **κ = 0.00167166528321877**. That is +2.78×10⁻⁷ over #1005 (0.001671387264390146). The complex side binds; the bit
  supplier is PR589's, unchanged.
- **Construction:** #1005's reviewed `construction/barch/build_tri.py` and `run_controls.py`, both **unchanged**,
  with the new recipe `construction/slots/RECIPE-SLOTS-k8.json`. The output word is `c2b29430…`, profile
  `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, and widths are unchanged.
- **Controls:** 34. These are C0 identity, the recipe, and the four mutants (`drop_restore`, `restore_full`, `drop_preread`,
  `donation_after`) applied globally and to each of the seven slots. Every mutant is rejected and pinned in
  `construction/slots/SLOT-PINS-k8.json`.
- **Frames:** the exact global frame optimiser (gopt2) finds no gain on the slot word, so there is no frame step.
- **Owners:** #1005's K8c8 owner map is rebound to the new word (widths and idle counts are unchanged). The admitted
  data in `data/` passes the strict replay.

## Verification (explicit reuse of a completed #1005 replay, as research/complex-t37-owners does for #799)

```sh
# Completed #1005 chain (the README commands of research/gauge44-leaver8), or any completed run of it:
python -B research/gauge44-leaver8/construction/leaver/reproduce_leaver_chain.py \
  --main . --pr635 /tmp/gauge44-pr635 --leaver-dir /tmp/lv --hamming /tmp/notri-base/hamming --id k8 --out /tmp/lvc
# This package (about 3 minutes):
python -B research/gauge44-slots/verify_manifest.py
python -B research/gauge44-slots/construction/slots/verify_slots.py \
  --main . --pr635 /tmp/gauge44-pr635 --baseline /tmp/lvc --work /tmp/slots
# PASS_SLOTS_ON_CHECKED_K8_BASELINE 0.00167166528321877
```

`verify_slots.py` rechecks the baseline: its complete step receipt (every chain step exited 0), the final word against
#1005's frame-recipe pin, its canonical, program and Clifford locals against `CHAIN-PINS-k8`, and all five
layer-end control counts. It then rebuilds only the slot layer and its controls, the native locals of the new word, the
independent `audit_local`, and the strict global replay of this package's data. Everything below is #1005's README,
unchanged; this package differs from it only in `construction/slots/`, `data/`, this section, `RESULT.json` and `MANIFEST.json`.

---

# Gauge44 without K-triangles, with earlier jp8 layers, the p6n ends, entrance promotions, a read-set exchange, #741's frames, a joint exchange, a triangle-hybrid B rewrite, no-helper mutable-leaver cells and PR589's bit supplier: conditional κ = 0.001671387264390146

Under the retained all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact-recovery, analytic-transfer and bit H1–H5 interfaces (as in #645), and the PR589 bit supplier,

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{1671387264390146}{10^{18}}=0.001671387264390146.
$$

**The construction is icekylinx's [#645](https://github.com/CrocSwap/integer-mult-bounds/pull/645) (`research/gauge44-global`).** This package builds the research/gauge44-barch construction (items 1–8) and then rebuilds its word around **no-helper mutable-leaver cells** (item 9):
1. **No-triangle word (PartialK).** #645's gauge44 chain is run with **none** of the four (p,−1) K-triangles, so there are R = 504 helpers. In the six K-blocks {0,1,2,11,12,13}, the completion priority is extended by the 6-row list `construction/notri/PRIO6.json`. Every block then pairs at rank 4, giving **56** rank-four cold ends instead of 44. `construction/notri/reproduce_notri.py` rebuilds this word from a #645 `reproduce.py --until word` output. It uses PartialK's generalisations of #645's and PR635's constructors (`cgx.py`, `port_stage_x.py`, `cold44x.py`; each differs from its original only in the documented parameters). It pins:
   - the pairing ranks [4]*14, inside `cold44x.py` and again in the driver;
   - the word (`3e99ba77…`);
   - the canonical word, the local programs and the Clifford recipes.
   `--control-g44` instead rebuilds #645's own gauge44 word (`78c7aada…`) with the same scripts.
2. **Layers on the no-triangle word (G44Stack).** `construction/layers_np/reproduce_np.py` applies to the no-triangle regroup word (`864ff4a1…`):
   - research/gauge44-layered's six pivot swaps, mapped to the 504-helper numbering (`PIVOT-SWAP-NP.json`, swap word `beb3579f…`);
   - the greedy HPE (46, `HPE-RECIPE-NP.json`);
   - the exact cold44 (same 56 ends);
   - the entering ends s4 (566/567/578/579 at U24) and x30 (608/610/543/555 at U30), plus BlockCombine's b6 and q4 dim-8 cold ends (`COLD-LAYERS-RECIPE-NP.json.gz`). p123 is negative on this base and dropped; j3 is dead.
   The layered word is pinned (`a9de804f…`): profile `{1:2534, 2:346, 3:458, 4:178, 5:56, 8:8}`, width 3800. The signed research/gauge44-layered files `construction/layers/build_pivot_swap.py` and `construction/layers/layer_end_controls.py` are used unchanged, and the latter must reject exactly 59 controls. The global code is research/gauge44-layered's (spot-width rule): SPEC `width_spot_helpers` [270,282,294,306] and `pivot_swap` → `construction/layers_np/PIVOT-SWAP-NP.json`, giving spot widths [9,9,8,8].
3. **p6n ends (NoTriReopen).** `construction/layers_p6n/reproduce_p6n.py` applies `COLD-LAYERS-RECIPE-P6N.json.gz` to the NP swapped HPE word with PR635's unchanged `build_cold_end.apply`. That is NP's cold-layer recipe plus six b-type dim-8 cold ends: [512,513], [311,510] and [522,327], which rebuild p123's lane as clean pairs. The result is the p6n word (`34b683fa…`): profile `{1:2540, 2:358, 3:446, 4:178, 5:56, 8:8}`, width 3794. The per-end layer-end controls (`construction/layers_p6n/layer_end_controls.py`, the variant Q6Reviewer signed for research/gauge44-pq6) must reject exactly 95 mutants. See `PROOF-NOTE-P6N.md`.
4. **Entrance promotions (BlockInvert).** `construction/promo/reproduce_promo.py --base p6n --k p6n-k4` applies the minimal recipe `PROMO-RECIPE-p6n-k4.json` to the p6n word with BlockInvert's deterministic constructor `build_promotion.py`. The recipe promotes the 16 entering helpers 627, 629–631, 635, 637–639, 651, 653–655, 659 and 661–663 (four E4 kernel groups) from E4 to E5, the time-reverse dual of end deepening. It re-chooses the frames of the gates affected. Only frame annotations and start frames move; the scalar program is unchanged. The promoted word is pinned (`0390ec65…`): profile `{1:2572, 2:326, 3:430, 4:194, 5:56, 8:8}`, widths `{4:80, 5:32, 7:54, 8:122, 9:216}`, width 3778. BlockInvert's `promo_controls.py` runs #645's independent `audit_local.py` on the honest word and must reject 11 recipe- and word-level mutants at pinned sites. The per-end layer-end controls (95) and the native chain then run with pins. The recipe is minimal: 48 entry-gate frame raises and no other frame re-choices. See `PROOF-NOTE-PROMO.md`.
5. **Read-set exchange (BRoute).** `construction/sw4/reproduce_sw4.py` runs BRoute's standard-library builder `build_sw4.py` with `SW4-RECIPE-P6k4.json`, 16 explicit moves, on the promoted word (`0390ec65…`). For the entering-copy pairs (h, r) = (461,25), (581,89), (591,415) and (603,431), the phase-B target read sets of h and its face register r are exchanged. The entrance pre-reads are deleted or inserted so that every register's value at the end of B is unchanged; the builder checks this mod p. Frames are repaired monotonically, and the width is unchanged. The SW4 word is pinned (`d232183f…`): profile `{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}`, width 3778. Four controls (C0 identity, N1 kept pre-read, N2 partial exchange, N3 wrong sign) must all hold, each at its exact rejection site pinned in the recipe. The per-end layer-end controls (95) and the native chain then run with pins. See `PROOF-NOTE-SW4.md` and `construction/sw4/NOTES.md`.
6. **#741's eight B frames (chafreaky).** `construction/frames/reproduce_frames.py` applies chafreaky's [#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741) frame recipe, `FRAME-RECIPE-sw4.json`, byte-identical to #741's. Ported by CompetitorMine, it raises eight B-gate frames with the scalar program unchanged, giving #741's word `e7804702…`. It runs 3 pin controls, #741's 10 focused native controls, 95 layer-end controls and the native chain with pins.
7. **Joint exchange X4 (JointXF).** `construction/jx/reproduce_jx.py` runs JointXF's standard-library builder `build_jx.py` with `RECIPE-X4.json` on #741's word (step 6's output). It makes four disjoint instances of the read-set exchange, each over two target-sharing copy pairs: (448,472), (458,592), (470,604) and (482,614). The moved reads keep their stored frames, and #741's frames are included. All edits are explicit, and B-segment exactness is checked by Fraction replay. The final word is pinned (`1e1d99ba…`): profile `{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8}`, width 3778. All seven pinned controls are rerun; C1 reproduces #741's word. See `PROOF-NOTE-FRAMES-X4.md`.
8. **Triangle-hybrid B rewrite (NewBArch).** `construction/barch/reproduce_barch.py` runs NewBArch's standard-library builder `build_tri.py` with `RECIPE-U8.json` on the X4 word (step 7's output). Eight disjoint slots receive a width-neutral B-delivery rewrite: an entering copy donates into a halves-copy so that one target read gets X+H, with holder restores and entrance pre-reads. The U8 word is pinned (`090fd574…`): profile `{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}`, width 3778. All 38 pinned controls are rerun (identity, the recipe word passing audit_local, and four audit_local-rejected mutants, globally and per slot). See `PROOF-NOTE-BARCH.md`.
9. **Leaver cells, re-stacked (LeaverSAT, LeaverSAT2).** `construction/leaver/reproduce_leaver.py --id k8` replaces the no-triangle word's construction with all eight all-K cells (01±, 23±, 45±, 67±). Each cell is LeaverSAT's 21-gate circuit, which uses the face-event leaver sources as mutable intermediates (R = 480, cell word `58e14a02…`). `construction/leaver/reproduce_leaver_chain.py --id k8` then re-applies items 2–8 with the signed builders unchanged and LeaverSAT's re-indexed recipes: swap, HPE, cold44, NP, p6n, 16 promotions, the re-indexed X4 exchange (the identity on this word) and 6 U8-style hybrids (`c836d892…`). It adds LeaverSAT2's exact global frame re-optimisation (`FRAME-RECIPE-LV-k8.json`), which gives the final word **`db2c7cfb…`**. Every intermediate word, control count and native pin is pinned (`LEAVER-PINS-k8.json`, `CHAIN-PINS-k8.json`). The per-word layer-end controls are the Q6Reviewer-signed `layer_end_controls_leaver.py` v2 (95 each), on the p6n, promoted, jx and hybrid words (`LEC-REASON-PINS-STACK-k8.json`) and on the re-framed final word (`LEC-REASON-PINS-k8.json`); its declared not-applicable sites are sha-proven identities or unbuildable mutants, each replaced by a same-class substitute that must be rejected. Items 5 and 6 don't apply on this word: the sw4 copies are dropped, and none of #741's frames survive. Items 1–8 remain in the package as the construction record of research/gauge44-barch. See `PROOF-NOTE-LEAVER.md`.
10. **Owner map (chafreaky's [#685](https://github.com/CrocSwap/integer-mult-bounds/pull/685), adapted by G44Pack).** The map is G44Pack3's K8c8, from its pattern-flow LNS (`pflns`) on the R = 480 k8 word. Its lineage is the #685/#741 map (chafreaky) via G44Pack's relabel and rewidth, followed by G44Pack3's LNS. It was admitted with this package's own code (NEWWORD discovery, `freeze_spec.py`, strict) at κ 0.001671387264390146. Only PLAN and OWNERS change. These are search inputs only; no verifier reads them.
11. **Expected values.** `data/SPEC.json` is re-derived by #645's discovery → `code/freeze_spec.py` → strict chain.

- **κ = 0.001671387264390146** (conservative 0.001671387261540186). That is +0.4298% over research/gauge44-leaver (k5 cells, κ 0.001664233607446043; same chain on five cells, FO_c1 map) and +0.5672% over [#942](https://github.com/CrocSwap/integer-mult-bounds/pull/942) (κ 0.001661960547713947) and +1.3279% over #645, +0.9174% over research/gauge44-notri-layered (0.001656193765416678) and +0.7701% over research/gauge44-promo (0.00165861362787227) and +0.7273% over research/gauge44-promo-p6 (0.001659319032684569) and +0.7075% over research/gauge44-promo-p6sw (0.001659645685315104) and +0.5869% over research/gauge44-frames-x (0.001661634653669567) and +0.5679% over research/gauge44-barch (0.001661948695165034) and +0.6131% over [#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741) (chafreaky, κ 0.001661202643272239) and +0.6654% over [#685](https://github.com/CrocSwap/integer-mult-bounds/pull/685) (chafreaky, κ 0.001660339298410333). The complex side certifies 0.001674185476674086429846 and PR589's bit supplier gives 0.001733427039589844234749, so **the complex side binds**. Under PR543 the bit side would cap κ at 0.001651096360425895 (`PROOF-NOTE-BIT.md`).
- **Evidence.** This package's own code admitted G44Pack3's K8c8 map (NEWWORD discovery → `freeze_spec.py` → strict): `verify_global.py` passes (`PASS_GAUGE44_STRICT_GLOBAL_REPLAY`, κ 0.001671387264390146) against G44Pack3's k8 locals, with SPEC `width_spot_helpers` [258,270,282,294] and `pivot_swap` → `construction/leaver/PIVOT-SWAP-k8.json`. It equals G44Pack3's own strict κ for K8c8. `RESULT.json` is that replay's `REPLAY.json`, converted to LF. The locals rebuilt by `reproduce_leaver_chain.py --id k8` match G44Pack3's strict locals byte for byte in every file except CLIFFORD-REVIEW and SCALAR-FRAME-AUDIT. Those two differ only in their `seconds` field, and the comparison normalises only that field (canonical `d1bf3c6f…`, programs `683f8323…`/`2d184e4d…`, Clifford `e3bfdfa2…`, pinned in `CHAIN-PINS-k8.json`). For this package, `data/SPEC.json` and a fresh `verify_global.py` replay on locals rebuilt by the two drivers are the binding record.
- **Independent price.** `independent/GAUGE44-INDEPENDENT-PRICE.json` is regenerated on this package's `data/PLAN.json` with the ported `independent/price_profile.py`: `PASS_FROZEN_PROFILE_TWO_EXACT_ENGINE_AND_OUTER47_CROSSCHECK`, κ equal to the strict replay.
- **Independent local audit.** `evidence/layers/LOCAL-AUDIT-LAYERED.json` is #645's `independent/audit_local.py`, run with `--main` on the final leaver word (content `db2c7cfb…`): `PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES`, 192 entering helpers, 78 low ends, 48 cold ends, 704 checked columns. Rerunning it reproduces the receipt except `elapsed_seconds` and, across zlib versions, `compressed_sha256`.
- **Historical #645 files (PR543-based, 492 helpers).** These are #645's files, retained unchanged and **not** updated for this package: `LOCAL-VALIDATION.json`, `CONSTRUCTION.md`, `hosting/`, `evidence/` (except `evidence/layers/`), the rest of `independent/`, `construction/reproduce.py` and its inputs, and `code/prepare_global.py`. They describe #645's word, owner map, PR543 supplier and κ 0.001649483702558979. `code/prepare_global.py` is #645's one-shot owner-map preparer, hard-wired to #645's parent plan and R = 492. No verifier imports it. This package's PLAN/OWNERS are frozen search output, and the strict replay checks them. `construction/reproduce.py` is still used for its `--until word` shadow and hamming inputs; its 492-word output is then superseded by `construction/notri/`. `construction/layers/reproduce_layers.py` is research/gauge44-layered's driver for the 492-helper layered word, shipped unchanged as signed; it is not used here.
- **Construction and code files** by committed LF SHA-256:
  - `construction/notri/reproduce_notri.py` 90148c2a0422b4f92164298a283de73d413ab3d4cb7151a0e6b643a37ea025a8 (no-triangle driver)
  - `construction/notri/cgx.py` 3da039d4184097c14802f9dbf972520d5b807671196f5e47a2247bc9f29bb418 (PartialK's generalised construct_gauge_xcentre.py)
  - `construction/notri/port_stage_x.py` 38310744d054e393ea35e996047cddeb2d212141aaaaa4b07f7a4663b11db8e7 (PartialK's generalised build_port_stage.py)
  - `construction/notri/cold44x.py` f0bc3500efb2c839a0f8cb03dbb9ea0a54f1dfc71ef81e5373b3d638ac5b8296 (PartialK's generalised build_gauge_cold44.py plus the PAIRING_RANKS pin)
  - `construction/notri/PRIO6.json` de0412511b0dd1af13e9717bc791126ac0e91c569b5391fd6c70268083045d15 (completion priority)
  - `construction/layers_np/reproduce_np.py` 1a304144a250d00d14154692ba522365b036777cf2b6fac466095e8ba733c16c (NP layer driver)
  - `construction/layers_np/PIVOT-SWAP-NP.json` d49b8d316da1cbdaf995dd0e8314d3c67cc9cd4d5902e9d85ccb907be645bef5 (layer input)
  - `construction/layers_np/HPE-RECIPE-NP.json` 43900139f618bdc06b8319098fb8dccaf4fc315b43ef7c067ca2cd778cdba2c1 (layer input)
  - `construction/layers_np/COLD-LAYERS-RECIPE-NP.json.gz` 3164cfb71baaeba4ac43427bc14075a225fc3a32ecd9341e58aa52c03a4ee2c0 (layer input)
  - `construction/layers/build_pivot_swap.py` 8e8bced88be2e592ded40929499bac385ca92fcc1fa59183c22229dbf34093b8 (signed, unchanged)
  - `construction/layers/layer_end_controls.py` 7829187bfc8f909948d5250e0ec00f02c89f5fe98306a3ed88daee36cb3c92ef (signed, unchanged)
  - `construction/layers/reproduce_layers.py` 435699f6f79c6c7fb8d6cc5a8382576d6ac88747583a975ff671e45440b93c4e (signed, unchanged, unused here)
  - `construction/promo/reproduce_promo.py` f979be666c3f5cf57e342a8427863c0b35b67ca4d3be495ac386f6870deb2026 (promotion driver)
  - `construction/promo/build_promotion.py` 9c9e2001b8d68bbe934d136026276fe97bd9bf6f94d4d78441fc28e14aca4daf (BlockInvert's constructor)
  - `construction/promo/promo_controls.py` 786c51f84b53698c2c833083506c4432c30eb0ed3b71e7dbe458a70c7413c372 (BlockInvert's controls)
  - `construction/promo/make_recipe.py` ba9e4fdc0c1be7f6a150a5a50909911257a1a8c7cc5d03d61f541178fc07c122 (discovery-side recipe writer (search, not run))
  - `construction/promo/PROMO-RECIPE-p6n-k4.json` fa6065d142646f7ab1f268912ce0cf5a1a6cd33c3994ff96bd6e204cf16b3e90 (minimal recipe)
  - `construction/promo/LOCAL-PINS-p6n-k4.json` a92bb02266596956bd53e9c86e8bbcc6639c92b4a4a248a1521f8eb79228271f (native pins)
  - `construction/layers_p6n/reproduce_p6n.py` aa7d6bcbed05aa1c689437c07a26e5c95be3c700c0c1fb7bcf91c432a88436ca (p6n driver)
  - `construction/layers_p6n/layer_end_controls.py` fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e (per-end controls (Q6Reviewer-signed variant))
  - `construction/layers_p6n/COLD-LAYERS-RECIPE-P6N.json.gz` 17e218a17e47c58fe2cde775ab2314d3d84030a61327b7f13da61cae3b374ad4 (p6n recipe)
  - `construction/layers_p6n/P6N-SPEC.json` 132a59635077d6afe80f99964a6935fce1dc2ece6587d74209c6f9c60025c8f1 (p6n end spec)
  - `construction/sw4/reproduce_sw4.py` 3d082e0cc576fb1b4fb9e5dd11d63bab697c8a8626e2837813cd00d100b1aeac (SW4 driver)
  - `construction/sw4/build_sw4.py` 9a295f3d534594a6b1326d8a6647e947670d1c6fbc92f37f5169661fde4c8f66 (BRoute's builder (stdlib))
  - `construction/sw4/SW4-RECIPE-P6k4.json` fa58d0ffc95d10b7453daefe4b34404a52895f94126ef973e92e92106cd615fa (16-move recipe with pinned rejection sites)
  - `construction/sw4/LOCAL-PINS-sw4-P6k4.json` 3c06bf68b28ff125a6a2372bb70cefd76fb9fe1333438cd34dfb5b617cd70327 (native pins)
  - `construction/frames/reproduce_frames.py` dc39ada9a2eb387310be181f3cea5dbd4b538632a888cd7372ece5e38a771832 (#741 frames driver)
  - `construction/frames/build_frames.py` 200847a7e8b3125cbeea0765dad67650e0bf83d32b66d72ba4977e99b8ee8eeb (#741's builder (chafreaky; ported))
  - `construction/frames/frame_controls.py` 477de854ec9184a2c73d6ac3857a9d0cbd6bc04b71d10a105e7344434b492a77 (#741's controls (chafreaky; ported))
  - `construction/frames/FRAME-RECIPE-sw4.json` a2c7ca4d44671386d05974e2627645b42bbb7da7a35cefff6e9fa158b6ac8473 (#741's recipe, byte-identical)
  - `construction/frames/LOCAL-PINS-frames-sw4.json` bc416b8f6443d59c715fb358c4d70fa27eae2d306388ffe0e2a303f60d929f7f (native pins)
  - `construction/jx/reproduce_jx.py` 5c7afebb4eb7fcdeb7e971cfbc457cf071850e2da21c3c71295efdd453c2399c (X4 driver)
  - `construction/jx/build_jx.py` 3cc7550b0c24bb54e245c6f7f16de489fd7844721fbb64aac628f38f43887916 (JointXF's builder (stdlib))
  - `construction/jx/RECIPE-X4.json` 9d42c6b38e8124f5ffe15da56c260a7fba7260626bf3c5f8cbd93aa4a71ceadd (explicit recipe with pinned controls)
  - `construction/jx/LOCAL-PINS-jx-X4.json` 95c5114c8e937c2737a1b9f9da97303f2e5e129d39e6dfcc4010e99bfdb9c974 (native pins)
  - `construction/barch/reproduce_barch.py` 19bc970aa6af25ab0e7fa96fb65c64dd0c5243976d8f2cb733cba839155482c1 (U8 driver)
  - `construction/barch/build_tri.py` 0fba65b31c2fd71864c291358bb0ad8d5f7e1be07e21df23f0ae73d7b966002e (NewBArch's builder (stdlib))
  - `construction/barch/run_controls.py` 42639bf62bf57795e3ea615c1944c67efed00f28591333daeb3139bf63d04476 (NewBArch's controls (38 outcomes))
  - `construction/barch/RECIPE-U8.json` 292f0e9f82824c4111728cf4de929bf6e43320fbbdc77658aae9681906b0d652 (explicit recipe)
  - `construction/barch/LOCAL-PINS-barch-U8.json` 2d16f99e1f71fd66378f5f767cf4cfa2a58264919a95074c7b31029f39a3c9f5 (control set and native pins)
  - `construction/leaver/reproduce_leaver.py` 831bfdf2247b5d864b74c3b2b6a475718053d48570851d48bd1c5471d410ee30 (cell driver)
  - `construction/leaver/cgx_leaver.py` 3af491c63dd96204a7c36006c7e419c2e5ce77e5bc453ccd2495c1e41f83f87c (cell constructor)
  - `construction/leaver/reproduce_leaver_chain.py` 2bc3fc3f32e0f957a0731b79254c553ca48fc6d4d47c4f99d6cd31e1901d85b5 (chain driver)
  - `construction/leaver/layer_end_controls_leaver.py` 4ba676f1ea326b739a64c3477f64eeb295f8151514f78fa7e62b71e4373a6206 (per-word reason re-pins and declared not-applicable sites, v2 (Q6Reviewer-signed))
  - `construction/leaver/build_frames_lv.py` 2eb80d612aa59a7bd8b04a122045e3bd2b83a21954e3164943cd20cf6050a21b (LeaverSAT2's frame builder)
  The global code is research/gauge44-layered's, unchanged: assemble 4c270a99, assembly_controls e4c0f782, audit_allcold a87d7f48, bind 1d39bcc7, witness 779c5172. The bit-supplier code is research/gauge44-bit589's, unchanged: verify_global 16bd5e54, bit_supplier_controls e6d33fb6, price_profile d2f548ad.
- **Line endings.** These files had CRLF in the admitted trees and are committed as LF only (`crlf.replace(b'\r\n', b'\n') == lf`, no lone `\r`):
  - `construction/jx/build_jx.py`: CRLF 775c2ae60eec9abc…, committed (LF) 3cc7550b0c24bb54…
  - `construction/jx/RECIPE-X4.json`: CRLF 228079b304358500…, committed (LF) 9d42c6b38e8124f5…
  - `construction/barch/build_tri.py`: CRLF 2432372f148a4d34…, committed (LF) 0fba65b31c2fd718…
  - `construction/barch/run_controls.py`: CRLF 18e1f5953403784f…, committed (LF) 42639bf62bf57795…
  - `construction/barch/RECIPE-U8.json`: CRLF 3e97088ad641eb6e…, committed (LF) 292f0e9f82824c41…
  - `data/SPEC.json`: CRLF b2515d29d54e5027…, committed (LF) 1208c7c3ae84c158…
  - `RESULT.json`: CRLF 454c25d5b0cd7df7…, committed (LF) 72bf797ce995ff61…
  - `independent/GAUGE44-INDEPENDENT-PRICE.json`: CRLF 0b8482888e64327f…, committed (LF) 6e222b252f345344…
  - `evidence/layers/LOCAL-AUDIT-LAYERED.json`: CRLF 6b63fc2bbea96cb5…, committed (LF) a596d7262374a023…


Clean-clone verification, from the repository root (Python 3.11+, assertions on; prepare the pinned #635 supplier as in the #645 section below):

```sh
python -B research/gauge44-leaver8/verify_manifest.py
python -B research/gauge44-leaver8/construction/reproduce.py \
  --main . --pr635 /tmp/gauge44-pr635 --out /tmp/notri-base --until word
python -B research/gauge44-leaver8/construction/notri/reproduce_notri.py \
  --main . --pr635 /tmp/gauge44-pr635 --word-dir /tmp/notri-base --out /tmp/notri-word --word-only
python -B research/gauge44-leaver8/construction/layers_np/reproduce_np.py \
  --main . --pr635 /tmp/gauge44-pr635 --notri-dir /tmp/notri-word --hamming /tmp/notri-base/hamming --out /tmp/notri-np
python -B research/gauge44-leaver8/construction/layers_p6n/reproduce_p6n.py \
  --main . --pr635 /tmp/gauge44-pr635 --np-dir /tmp/notri-np --out /tmp/p6n
python -B research/gauge44-leaver8/construction/promo/reproduce_promo.py \
  --main . --pr635 /tmp/gauge44-pr635 --base p6n --base-dir /tmp/p6n --k p6n-k4 --out /tmp/promo
python -B research/gauge44-leaver8/construction/sw4/reproduce_sw4.py \
  --main . --pr635 /tmp/gauge44-pr635 --promo-dir /tmp/promo --recipe P6k4 --out /tmp/sw4
python -B research/gauge44-leaver8/construction/frames/reproduce_frames.py \
  --main . --pr635 /tmp/gauge44-pr635 --sw4-dir /tmp/sw4 --out /tmp/frames
python -B research/gauge44-leaver8/construction/jx/reproduce_jx.py \
  --main . --pr635 /tmp/gauge44-pr635 --frames-dir /tmp/frames --out /tmp/x4
python -B research/gauge44-leaver8/construction/leaver/reproduce_leaver.py \
  --main . --pr635 /tmp/gauge44-pr635 --word-dir /tmp/notri-base --id k8 --out /tmp/lv --word-only
python -B research/gauge44-leaver8/construction/leaver/reproduce_leaver_chain.py \
  --main . --pr635 /tmp/gauge44-pr635 --leaver-dir /tmp/lv --hamming /tmp/notri-base/hamming --id k8 --out /tmp/lvc
python -B research/gauge44-leaver8/independent/audit_local.py \
  --word /tmp/lvc/frames/FULL-WORD.json.gz --main . --output /tmp/lvc-audit.json
python -B research/gauge44-leaver8/verify_global.py \
  --main . --local /tmp/lvc/local --work /tmp/lvc-global
# kappa 0.001671387264390146
```

Optional control: `reproduce_notri.py ... --control-g44 --out /tmp/notri-ctl` rebuilds #645's gauge44 word `78c7aada…`.

## Predecessor: #645's README (unchanged below; paths read `research/gauge44-global`)

### Gauge44: conditional κ = 0.001649483702558979

New contributions by **icekylinx**, with **OpenAI GPT-6 Astra** assistance.
Local review and packaging used OpenAI Codex. Original notices and Apache-2.0 licenses are retained.

Under the retained all-size compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape, exact-recovery, analytic-transfer and bit
H1–H5 interfaces,

$$
T(n)=O\!\left(n(\log n)^{1-\kappa_{645}}\right),\qquad
\kappa_{645}=\frac{1649483702558979}{10^{18}}=0.001649483702558979
$$

(This is #645's own κ. **This package's κ is the one at the top of this README.**)

The certified complex saving is `0.001652208994368411824947`. The unchanged
[#543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) bit supplier gives
`0.001653826988146798944268`, so the complex side binds. The conservative complex
model separately certifies κ `0.001649483699681650`.

### Construction

This replaces the local supplier and all 72 owner assignments of pinned
[#635](https://github.com/CrocSwap/integer-mult-bounds/pull/635). Source/copy exchanges
at equal rank-one frames alter the factory's arbitrary-helper-input propagation.
An invertible completion of the retired rows and source-carried coordinate totals
then expose 44 rank-four cold endpoints. Exact input premixes, low-frame tails
and a recomputed full inverse realize them.

| Per-invocation quantity | Complete #635 JP8 | Gauge44 |
| --- | ---: | ---: |
| Source / target ports | 112 / 112 | 112 / 112 |
| Helpers | 492 | 492 |
| Rank-four cold endpoints | 22 | 44 |
| Helper residual width | 3,894 | 3,794 |
| Paid local rank mass | 5,750 | 5,650 |

The new paid local profile is `{1:2514, 2:404, 3:448, 4:160, 5:56, 8:8}`.
The explicit whole-family assignment covers 35,424 helper roles on 7,168 live
and 7,670 physical families. It retains the rank deficit 2,560 and charges every
idle remainder. Exact integer majorization certificates justify the owner
updates; the resulting map is a coordinate fixed point, with no claim of joint
optimality.

The assembled κ is 0.809306% above #635. `data/FRONTIER.json` records Pro's dated
comparison snapshot; it is not a live ranking of community results.

### Proof and evidence

- `CONSTRUCTION.md`: exact cold-space calculation, dyadic realization and attribution.
- `hosting/PROOF.md`: capacity, exchange and majorization arguments.
- `independent/CENTRE-GUARD-REVIEW.md`: ordered center-frame interface and source carriers.
- `data/SPEC.json`, `evidence/ASSEMBLY.json`: strict component moments and outer parameters.
- `evidence/audit/`: actual controller, physical charts and finite invoice.
- `construction/INPUTS.json`, `data/UPSTREAM-PINS.json`: inherited input hashes.
- `MANIFEST.json`, `SOURCES.json`, `LOCAL-VALIDATION.json`: submitted bytes, provenance and local checks.

Original Pro run receipts are retained as evidence; their raw logs remain in
the original archive outside the submission. Fresh replay writes new logs to
the selected output directory.

### Incremental reproduction

Use Python 3.11 or newer with assertions enabled. The required replay uses only
the standard library. The optional historical seed-discovery optimizer is not
part of admission.

Prepare the pinned #635 supplier in a separate directory (the main dependencies
are already present in this repository):

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git a6895a69f8ad98ab45777b03e9e6f48888c39f6f
mkdir -p /tmp/gauge44-pr635
git archive FETCH_HEAD research/complex-571-cold14-st2 | tar -x -C /tmp/gauge44-pr635
```

From the repository root, with fresh output directories:

```sh
python -B research/gauge44-global/verify_manifest.py
python -B research/gauge44-global/construction/reproduce.py \
  --main . --pr635 /tmp/gauge44-pr635 \
  --out /tmp/gauge44-local --until phases
python -B research/gauge44-global/verify_global.py \
  --main . --local /tmp/gauge44-local/local --work /tmp/gauge44-global
```

The dedicated workflow also runs the independent literal-word audit, exact owner
reproduction, preserved-assertion comparison and independent pricing on Python
3.11 and 3.14. `hosting/README.md` and `independent/README.md` give those commands.
No ancestral full replay, optimizer search or PDF generation is required.

The result remains a finite conditional witness. It does not establish an
unconditional multiplication theorem or a complete Lean formalization.
