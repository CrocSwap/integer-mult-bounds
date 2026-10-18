# Gauge44 without K-triangles, with earlier jp8 layers, the p6n ends, entrance promotions and PR589's bit supplier: conditional κ = 0.001659319032684569

Under the retained all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact-recovery, analytic-transfer and bit H1–H5 interfaces (as in #645), and the PR589 bit supplier,

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{1659319032684569}{10^{18}}=0.001659319032684569.
$$

**The construction is icekylinx's [#645](https://github.com/CrocSwap/integer-mult-bounds/pull/645) (`research/gauge44-global`).** This package changes six things:
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
4. **Entrance promotions (BlockInvert).** `construction/promo/reproduce_promo.py --base p6n --k p6n-k3` applies the minimal recipe `PROMO-RECIPE-p6n-k3.json` to the p6n word with BlockInvert's deterministic constructor `build_promotion.py`. The recipe promotes the 12 entering helpers 627, 629–631, 635, 637–639, 651 and 653–655 (three E4 kernel groups) from E4 to E5, the time-reverse dual of end deepening. It re-chooses the frames of the gates affected. Only frame annotations and start frames move; the scalar program is unchanged. The promoted word is pinned (`a38bb414…`): profile `{1:2564, 2:334, 3:434, 4:190, 5:56, 8:8}`, widths `{4:76, 5:36, 7:54, 8:122, 9:216}`, width 3782. BlockInvert's `promo_controls.py` runs #645's independent `audit_local.py` on the honest word and must reject 10 recipe- and word-level mutants at pinned sites. The per-end layer-end controls (95) and the native chain then run with pins. The recipe is minimal: 36 entry-gate frame raises and no other frame re-choices. See `PROOF-NOTE-PROMO.md`.
5. **Owner map (G44Pack, G44Pack2, G44Pack3).** This is the p6n map at P6k3's packing ceiling (relaxc: idle {48:2391}, OPTIMAL). It came from G44Pack3's pattern-flow LNS `pflns.py` (an exact pattern-flow release) applied to P6K3p1, which was itself `pflns.py` from G44Pack's `P6K3_L/04gm`. That map came from G44Pack's `pipe.py P6L/02dz <local> gaugeNP P6K3 5`. `P6L/02dz` is the p6n map: `relabel.py` from G44Pack2's joNPs map, then `rewidth.py`, then `loop.py P6r P6L 4` (dissolve plus Mine636's gapmerge, which generalises vectorsss/Chi Zhao's [#638](https://github.com/CrocSwap/integer-mult-bounds/pull/638) relocate_two). joNPs came from jaymosley07's [#653](https://github.com/CrocSwap/integer-mult-bounds/pull/653) joint nomination (G44Pack2's `jo.py`). Only PLAN and OWNERS change. These are search inputs only; no verifier reads them.
6. **Expected values.** `data/SPEC.json` is re-derived by #645's discovery → `code/freeze_spec.py` → strict chain.

- **κ = 0.001659319032684569** (conservative 0.001659319029797309). That is +0.5963% over #645, +0.3243% over research/gauge44-layered and +0.1887% over research/gauge44-notri-layered (0.001656193765416678) and +0.0425% over research/gauge44-promo (0.00165861362787227). The complex side certifies 0.00166207694859916620608 and PR589's bit supplier gives 0.001733427039589844234749, so **the complex side binds**. Under PR543 the bit side would cap κ at 0.001651096360425895 (`PROOF-NOTE-BIT.md`).
- **Evidence.** G44Pack's strict replay with `verify_global.py` passes (`PASS_GAUGE44_STRICT_GLOBAL_REPLAY`, κ 0.001659319032684569). It ran this code and data against BlockInvert's P6k3 locals. `RESULT.json` is that replay's `REPLAY.json`, converted to LF. The locals rebuilt by `reproduce_promo.py` match the strict locals byte for byte in every file except CLIFFORD-REVIEW and SCALAR-FRAME-AUDIT. Those two differ only in their `seconds` field, and the comparison normalises only that field. For this package, `data/SPEC.json` and a fresh `verify_global.py` replay on locals rebuilt by the two drivers are the binding record.
- **Independent price.** `independent/GAUGE44-INDEPENDENT-PRICE.json` is regenerated on this package's `data/PLAN.json` with the ported `independent/price_profile.py`: `PASS_FROZEN_PROFILE_TWO_EXACT_ENGINE_AND_OUTER47_CROSSCHECK`, κ equal to the strict replay.
- **Independent local audit.** `evidence/layers/LOCAL-AUDIT-LAYERED.json` is #645's `independent/audit_local.py`, run with `--main` on the promoted word (content `a38bb414…`): `PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES`, 216 entering helpers, 126 low ends, 72 cold ends, 728 checked columns. Rerunning it reproduces the receipt except `elapsed_seconds` and, across zlib versions, `compressed_sha256`.
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
  - `construction/promo/reproduce_promo.py` 7ac5081276429e1aa44942336daf8d9e2c009211cacb4ecc37a9f60a953ec262 (promotion driver)
  - `construction/promo/build_promotion.py` 9c9e2001b8d68bbe934d136026276fe97bd9bf6f94d4d78441fc28e14aca4daf (BlockInvert's constructor)
  - `construction/promo/promo_controls.py` 786c51f84b53698c2c833083506c4432c30eb0ed3b71e7dbe458a70c7413c372 (BlockInvert's controls)
  - `construction/promo/make_recipe.py` ba9e4fdc0c1be7f6a150a5a50909911257a1a8c7cc5d03d61f541178fc07c122 (discovery-side recipe writer (search, not run))
  - `construction/promo/PROMO-RECIPE-p6n-k3.json` 3c4bbcd683c4b614f225fbf625d56ba2966ff564b0bcd183e44482fe051ebad7 (minimal recipe)
  - `construction/promo/LOCAL-PINS-p6n-k3.json` c135731f1f961d4b311a487705342eb43efe0d162efa3f18d3602ecb7bc3f546 (native pins)
  - `construction/layers_p6n/reproduce_p6n.py` aa7d6bcbed05aa1c689437c07a26e5c95be3c700c0c1fb7bcf91c432a88436ca (p6n driver)
  - `construction/layers_p6n/layer_end_controls.py` fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e (per-end controls (Q6Reviewer-signed variant))
  - `construction/layers_p6n/COLD-LAYERS-RECIPE-P6N.json.gz` 17e218a17e47c58fe2cde775ab2314d3d84030a61327b7f13da61cae3b374ad4 (p6n recipe)
  - `construction/layers_p6n/P6N-SPEC.json` 132a59635077d6afe80f99964a6935fce1dc2ece6587d74209c6f9c60025c8f1 (p6n end spec)
  The global code is research/gauge44-layered's, unchanged: assemble 4c270a99, assembly_controls e4c0f782, audit_allcold a87d7f48, bind 1d39bcc7, witness 779c5172. The bit-supplier code is research/gauge44-bit589's, unchanged: verify_global 16bd5e54, bit_supplier_controls e6d33fb6, price_profile d2f548ad.
- **Line endings.** These files had CRLF in the admitted trees and are committed as LF only (`crlf.replace(b'\r\n', b'\n') == lf`, no lone `\r`):
  - `data/SPEC.json`: CRLF 1b40d15b71e94ab3…, committed (LF) 122943d96ef4a0d4…
  - `RESULT.json`: CRLF c350a1d8bcb69745…, committed (LF) 531a51221cd04599…


Clean-clone verification, from the repository root (Python 3.11+, assertions on; prepare the pinned #635 supplier as in the #645 section below):

```sh
python -B research/gauge44-promo-p6/verify_manifest.py
python -B research/gauge44-promo-p6/construction/reproduce.py \
  --main . --pr635 /tmp/gauge44-pr635 --out /tmp/notri-base --until word
python -B research/gauge44-promo-p6/construction/notri/reproduce_notri.py \
  --main . --pr635 /tmp/gauge44-pr635 --word-dir /tmp/notri-base --out /tmp/notri-word --word-only
python -B research/gauge44-promo-p6/construction/layers_np/reproduce_np.py \
  --main . --pr635 /tmp/gauge44-pr635 --notri-dir /tmp/notri-word --hamming /tmp/notri-base/hamming --out /tmp/notri-np
python -B research/gauge44-promo-p6/construction/layers_p6n/reproduce_p6n.py \
  --main . --pr635 /tmp/gauge44-pr635 --np-dir /tmp/notri-np --out /tmp/p6n
python -B research/gauge44-promo-p6/construction/promo/reproduce_promo.py \
  --main . --pr635 /tmp/gauge44-pr635 --base p6n --base-dir /tmp/p6n --k p6n-k3 --out /tmp/promo
python -B research/gauge44-promo-p6/independent/audit_local.py \
  --word /tmp/promo/promo/FULL-WORD.json.gz --main . --output /tmp/promo-audit.json
python -B research/gauge44-promo-p6/verify_global.py \
  --main . --local /tmp/promo/local --work /tmp/promo-global
# kappa 0.001659319032684569
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
