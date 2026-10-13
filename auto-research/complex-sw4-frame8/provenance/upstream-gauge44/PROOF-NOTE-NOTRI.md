# PROOF-NOTE-NOTRI: #645's gauge44 word without K-triangles (R = 504)

Construction by PartialK; review by NotriReviewer (scratch/NotriReviewer/FINAL-REPORT.md). Drivers:
`construction/notri/reproduce_notri.py` (this word) and `construction/layers_np/reproduce_np.py` (layers on it).

## Why the triangles were the blocker
- In #645's gauge44, a K-block has I = 6 low registers with rank C = 4, so L = 2. Only the 2-row priority completion
  fits there. The (p,−) triangle reads climb copies loc17/19/21 and source loc2.
- Without the triangles, I = 8. With the 2-row completion, rank C stays 6 (L = 2), which is why the plain removal sweep
  restored nothing. With the 6-row completion (`PRIO6.json`, the list blocks 3–10 already use), rank C = 4, so L = 4,
  the cap. All 14 blocks then pair at rank 4: 56 rank-four cold ends, R = 504, width 3818, profile
  {1:2506, 2:336, 3:472, 4:184, 5:56, 8:8}, rank mass 5674.

## Constructor changes (NotriReviewer §1)
- **`cgx.py`** is #645's `construct_gauge_xcentre.py`, parameterised by XPARAM. On this path the only change that takes
  effect is the K-block priority: `PRIO[c]` is placed in front of the inherited rows. The prepended rows equal the
  shared 6-row list of blocks 3–10 (all 8 lists identical). Every completion assert is kept (`qr_rank(M)==4`,
  `len(M)==8`, the exact block-total rows). An empty TRI schedule is an input #645 already supports (`NH = 504 − 3·0`).
  `HELPER-MAP` is the identity on 728. The `exch`, `COPYL` and `hyb` branches are inert here (defaults, empty, not
  reached).
- **`port_stage_x.py`** is PR635's `build_port_stage.py`. The helper map only has to be injective rather than onto;
  with no triangles it is onto again.
- **`cold44x.py`** is #645's `build_gauge_cold44.py`. Its per-block pin `r == len(L) == (2 if K-block else 4)` is
  replaced by `r == len(L)` together with the explicit per-block pin `PAIRING_RANKS` (set by the driver to [4]*14,
  and to #645's pattern in `--control-g44`). Helpers outside the 224+16b ranges join their blocks (EXTRAH, empty here).
  Every other assert is kept (U, nonlocal premix, `rank(Qmat) == NB`).
- **Control.** `reproduce_notri.py --control-g44` runs the same scripts with #645's four triangles and no XPARAM. It
  reproduces #645's gauge44 word `78c7aada…` exactly, with ranks [2,2,2,4,4,4,4,4,4,4,4,2,2,2].

## Exactness and locals (NotriReviewer §2)
- Replay: 0 bad rows over 27,932 gates, all dyadic; forward, inverse and adjoint are exact. None of the 6,448
  compensation additions reads an ended helper, and the precondition never touches one.
- 0 FULL-remainder gates touch an ended helper; E⊂U holds for every entering end. The delta against gauge44
  ({1:−8, 2:−68, 3:+24, 4:+24}, width +24) matches the reported profiles.
- (N): all 17 pairs pass (14 cold dim-4 pairs with 4 helpers each, plus 3 dim-8 entering pairs).
- `audit_local.py --main`: PASS. Payload: prefix bits 66 forward and 72 backward, against 192.
- Native locals: 25 controls rejected, Lemma A on 22 frames, 17 wrapper mutants rejected. The rebuilt locals equal
  the strict locals (`PartialK/runs/none_p6/local`): byte-identical except CLIFFORD-REVIEW and SCALAR-FRAME-AUDIT,
  which differ only in their `seconds` field.

## Layers on this word (G44Stack)
The layers are research/gauge44-layered's (see `PROOF-NOTE-LAYERS.md`), mapped to the 504 numbering:
- the 6 pivot swaps 494→566, 495→567, 506→578, 507→579, 519→543, 531→555, which are neutral (same 46 HPE helpers,
  same 56 cold ends);
- s4 566/567/578/579 at U24;
- x30 608/610/543/555 at U30;
- BlockCombine's b6;
- q4.

p123 is negative on this base and dropped; j3 is dead (L = 0 at U24 and U30). The chain is regroup `864ff4a1` → swap
`beb3579f` → layered `a9de804f`, with profile {1:2534, 2:346, 3:458, 4:178, 5:56, 8:8} and width 3800. On that word
the signed `layer_end_controls.py` rejects 59/59 and `audit_local.py` passes with 216 entering helpers, 120 low ends,
66 cold ends and 728 columns. NotriReviewer independently reproduced a9de804f from the packaged recipes.
