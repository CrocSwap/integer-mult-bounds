# U10: two more triangle-hybrid slots on U8, hosted by PR942's T37 owners

```text
kappa = 831019538879371 / 5*10^17 = 0.001662039077758742
```

This is **+7.8530044795e-8 over the selected PR942 result** (`0.001661960547713947`). It is about 28× PR942's own gain over
PR890. The complex side binds, and the PR589 bit supplier is unchanged.

**Status: strict replay passed.** The complete PR942 pipeline on the U10 locals, `verify.py`, ends with
`PASS_U10_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY 0.001662039077758742`. It covers fresh U8 and U10 native chains,
independent owner, construction and partial-bank checks, discovery plus strict controller emission, audit with 15
mutations, the complete invoice (prefix 779 < 1024, row 17495 < 20161), assembly, 69 admission and 12 bit-supplier
controls, payload controls and the final binding. The receipts are in `evidence/strict/` (Linux, Python 3.13), and the
cold PR799/PR741/PR589 ancestry was replayed fresh (`PASS_REBUILT_PR589_PR799_COMPOSITION`).

## What changes: the local word only

PR869 (NewBArch) rewrote eight block-0 slots of PR799's X4 word with a width-neutral "triangle-hybrid" B delivery,
giving U8. In each slot, the copy pair `E += X` has its target reads re-routed:

- two reads are delivered through **holder** registers: `H += V` right after H's last write, so the target's existing
  H-read now also carries V;
- the remaining reads are swapped between E and X;
- the entrance pre-reads are rebuilt;
- holders are restored by an early-cleanup tail at a common low end, or by a FULL-cleanup gate.

`construction/u10/discovery/` turns the move into an exhaustive search over the U8 word. It covers every copy gate, every
E/X assignment of its reads, and every holder choice (ports included, up to two donations). It uses exact pre-read
reconstruction and a chain-only frame optimiser seeded from the inherited frames. Every improving candidate is priced
and checked with the independent `audit_local.py`.

The search found **two new legal slots outside block 0**, on the entering pair 612/613:

| slot | copy | E/X re-routing | donations (holder ← value, reading target) | restores |
|---|---|---|---|---|
| X=444 | `612 += 444` | t146 reads 612, t210 reads 444 | `98 ← 612` (t150), `34 ← 444` (t214) | `98 −= 612` early tail; `34 −= 444` FULL |
| X=446 | `613 += 446` | t147 reads 613, t211 reads 446 | `399 ← 613` (t151), `303 ← 446` (t215) | `399 −= 613` early tail; `303 −= 446` FULL |

Each slot changes the local paid profile by `{3:+2, 4:−4, 5:+2}`, like one PR869 slot. The two slots are additive:

```text
U8  {1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}
U10 {1:2548, 2:338, 3:450, 4:154, 5:76, 8:8}
```

Everything the owner layer sees is unchanged: the width (3778), the width inventory `{4:80, 5:32, 7:54, 8:122, 9:216}`,
the local prefixes (forward 55 bits, backward 72 bits), the A section, the start/end frames, the centres and every kept
B frame. PR942's T37 owner map, order, edits, bank envelope, 1024-bit prefix charge and outer recipe are therefore used
unchanged. The global profile is `333 × U10 + {48:11086, 1:6}`:

```text
{1:848490, 2:112554, 3:149850, 4:51282, 5:25308, 8:2664, 48:11086}
```

The word is given as an explicit recipe, `construction/u10/RECIPE-U10.json`, with 10 B deletes, 10 B inserts with
frames, 2 tails and 2 FULL prepends. It is applied to the pinned U8 word (`090fd574…`) by NewBArch's **unchanged**
`build_tri.py`. The resulting U10 word has content sha256
`776de990f3e1e9eebb075a3d280d1aa029cb5a171d30945128a713f78dd126d1`.

## Evidence

- `evidence/u10/LOCAL-AUDIT-U10.json`: the independent `audit_local.py` reports
  `PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES` (with the parent centre interface).
- `evidence/u10/U10-CONTROLS.json`: NewBArch's unchanged `run_controls.py` gives 14/14 outcomes. These are C0
  identity, the recipe PASS, and drop_restore / restore_full / drop_preread / donation_after both globally and per new
  slot, each rejected at its pinned message.
- `evidence/u10/COLD-END-CONTROLS.json`: 95 per-end layer mutations are rejected, as for U8.
- `evidence/u10/STEPS.json`, `LOCAL-CHECKS.json`: PR635's native chain (native, ledgers, local-replay, wrappers,
  phases) passes on U10 and recounts its paid profile in both orientations. `construction/u10/LOCAL-PINS-U10.json`
  pins the canonical word, the local programs and the Clifford recipes.
- `evidence/ALL-T-BOUND.json`: PR942's all-replica signed-dual bound, rerun with the U10 local profile, gives
  `PASS_ALL_T_U10_SIGNED_DUAL_RELAXATION_BOUND`. Its grid upper is `0.001662039077758742`, equal to the claim, so T37
  remains grid-optimal in the fixed whole-owner family for U10. The two exact engines bracket the complex root
  `[0.00166480605047151514435, 0.001664806050471515144351]`.

## Reproduce

Same requirements as PR942. From the repository root:

```sh
python -B research/complex-u10-t37/verify.py --work /tmp/u10-t37 [--baseline799 /abs/completed-cold799]
```

The stages are those of PR942, plus `u10-native` (`construction/u10/reproduce_u10.py`) right after `u8-native`. The
T37 replay (`T37_LOCAL`) and the independent owner check consume the U10 locals.

## Changes relative to `complex-t37-owners`

The PR942 package is copied with these edits:

- `verify.py`: the `u10-native` stage and U10 inputs.
- `prepare.py`: the adapted `build_parent.py` reads this package's `CLAIM.json` local profile.
- `final_binding.py`: U10 inputs, step checks and constants.
- `independent/all_t_bound.py`: the U10 local profile.
- `independent/check_payload_controls.py`: the new κ.
- `CLAIM.json`, the new `construction/u10/` and `evidence/u10/`, and this README, NOTICE and PROOF header.

`OWNERS.json.gz`, `ORDER.json`, `EDITS.json` and all inherited sources are byte-identical to PR942's.

See [NOTICE.md](NOTICE.md) for credits.
