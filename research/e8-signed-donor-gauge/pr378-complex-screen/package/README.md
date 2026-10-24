κ = 9.5464544449649e-4

# Jacob Sussman's E8 complex unit, re-timed by far piece relocation, in the seven-stage bridged word B₃

A conditional finite construction with **κ = 95464544449649/10¹⁷ ≈ 9.5464544449649 × 10⁻⁴**:

- +4.0188·10⁻⁷ (+0.0421 %) over DaysSky's #375 (9.5424356568133e-4), which is Sussman's original unit in the same layout;
- +2.5031·10⁻⁷ (+0.0262 %) over aliromman's #365 certificate in the same layout (9.54395132518163e-4, computed here).

The complex side binds. The bit side is #370's E8 bit word in #373's B₃ construction. It is unchanged and does not bind.

| side | supplier | layout | coarse saving |
| --- | --- | --- | ---: |
| complex | **this package's certificate** `gcert1-e8-r783-far` (Sussman's E8 unit, same operator, new frames and gate order) | B₃ unsplit (#375): m = 63, W = 6v + R = 1,503, deficit 216, max child 38, halving degree 2 | b = 477778832512643/(5·10¹⁷) ≈ **9.55557665025286e-4** |
| bit | #370's `bitE8-r865` in #373's B₃ (split at 27) | m = 56, W = 1,585, deficit 216 | c = 968197503705007/10¹⁸ (= #373) |

| complex certificate | B₃ split b (#363/#373) | B₃ unsplit b (#375) | κ (unsplit, bit #373) |
| --- | ---: | ---: | ---: |
| Sussman's `gcert1-e8-r783` | 9.32783231884153e-4 | 9.55155017966616e-4 | 9.5424356568133e-4 (= #375) |
| #365 (aliromman, 4 moves) | 9.32928054566567e-4 | 9.55306874505079e-4 | 9.54395132518163e-4 |
| **this package** | 9.33167230469274e-4 | **9.55557665025286e-4** | **9.5464544449649e-4** |

## What changed in the certificate

The scalar program is the same. The verifier checks that the full rational operator on all 1,023 registers, with every
initial value a variable, and the 8 retained totals are identical to Sussman's original. h, v, R = 783, cst = 72,
N = 9,039, the ports, start/final frames, scatter table and retained totals are also unchanged.

Only the frames at which additions happen, and the position of some elementary additions, change:

1. **Split.** Every fan-out or fan-in gate is split into elementary single additions, in the original order.
2. **Retiming.** Moves stay inside each gate's feasible frame interval, the source-span rule included. There are three kinds:
   - single gates;
   - connected same-frame blocks;
   - sub-blocks (time prefixes and suffixes of a block). These generalise #365's move 4, which re-frames two gates of a four-gate block.

   The candidate frames are:
   - the participants' neighbour frames;
   - the join of the lower bounds;
   - the meet of the upper bounds;
   - the lower join plus one vector of the meet.
3. **In-group piece relocation.** A subset of one gate's additions moves to the start or end of its group, at a frame of its own.
4. **Far piece relocation** (new here). An elementary addition moves forward or backward across gates it commutes with
   as a scalar operation: they neither read nor write its written register, and do not write its read register. It
   then takes its best frame between its new neighbours. This is the generalisation of #365's moves 1 and 2.
5. **Merge.** Consecutive elementary additions with the same kind, frame and shared register are merged back into fan-out
   or fan-in gates. The result has 775/1,226 gates in A/B, against 773/1,220, and two new frames.

The greedy search, which uses the χ ledger χ(r) = r((m/r)^a − 1) at m = 63, first reaches #365's certificate value
exactly (b = 9.32928054566567e-4 split). It then finds 14 further far relocations, each worth 0.253·a. Started from
#365's certificate it reaches the same final value. The block-histogram change against Sussman's original is
x {1:+1, 2:+1, 3:+1, 4:+1, 5:−2}, y {1:+2, 2:+8, 4:−22, 5:+2, 6:+10}, s {1:−1, 2:−7, 3:+5}.

Not profitable on this unit, and not used:
- a shared-donor response kernel through exterior gauges (Sussman's E7/Q2 rule). The 783 slot responses have rank 120, but every relation at a line entrance loses, and higher entrances have no dependent members;
- lowering a retained total's copy rank. No rational combination of the 8 totals is supported in any of the 511 hyperplanes of F₂⁹.

## Verify

    bash research/e8-complex-far-retiming/verify.sh --quick /tmp/e8st-q     # ~15 s
    bash research/e8-complex-far-retiming/verify.sh /tmp/e8st-full          # adds the regeneration (~1 min)

Only Python 3.11+ and the standard library are needed. The steps are:

0. `MANIFEST.sha256`: every file listed, none unlisted.
1. Inputs pinned by git blob id:
   - Sussman's certificate, `gx.py` and `gxcore.py`, the same bytes as in #363/#365/#375;
   - #370's bit word, the same bytes as #373's `data/bit`.
2. On both Sussman's original and ours:
   - Sussman's `gx.check1` (E0–E7, including the exact scalar replay E5) and the `gxcore` mirror histogram;
   - a flipped-sign control, which must be rejected with E5;
   - our source-span rule (the x-content support of every non-y operand, and of a slot destination, lies in the gate frame).

   Then the full rational operator identity, the unchanged family data, and the histogram delta.
3. Our reimplementation of the bridged layout B_K (#363's rule, Sussman's coordinate-frame stage geometry):
   - nested climbs, equal-frame twin gates, stage entries, final frames, and m − 1 moves per role;
   - the exchange identity X_p = −y_p, Y_p = x_p;
   - B₂ gives Sussman's idle climbs, and B₃ gives #363's for h = 9 and #373's for h = 8.
4. Coarse savings and κ:
   - bit c in B₃ (split, = #373) from our own replay of the bit word's local histogram;
   - complex b in B₃, split and unsplit, by both rational engines with the 10⁻¹⁶ fallback and the next grid point excluded;
   - PR #315's `outer.assembly`: 47 strict constraints, adjacent κ rejected, complex-bound.

   Regressions: Sussman's split b is #363's 932783231884153/10¹⁸, and the unsplit κ is #375's 95424356568133/10¹⁷.
5. Full mode only: our search (`code/cxfar.py`, `code/cxfinal.py`) re-run from Sussman's original must regenerate the shipped certificate byte for byte (decompressed).

## Admitted conditions and open obligations

- **No Lean proof of B₃** on either side, and **no Lean proof of the new certificate**. Sussman's Lean theorem
  `wht_main_block_B2Ge8x` covers his original certificate in B₂. Here the certificate is checked with his `gx.check1` and
  `gxcore`, plus the full operator identity against the original.
- **#375's halving-degree-two guard** for the unsplit complex idle climbs (max child 38 at m = 63: 63² > 2·38²) is
  admitted as #375 states it: the row coefficient is 2·1903 + 9909 + 252 = 13,967 < 20,161, with m ≤ 72. The stock
  quantities in it (m, W, R, h, cst) are unchanged here.
- **#352/#363's portable complex checks are not re-run on the new certificate.** That covers labels, scalar words and lifetimes, the splice, and the parts of the finite guard that read scalar-macro counts. Its gate count changes from 773/1,220 to 775/1,226 (+0.4 %).
- **The bit side is #373's claim.** We re-certify only c from #370's word with our own engines and layout. #373's checks
  of the bit word (seven-stage formal columns, geometry, banks, finite bill) are not re-run here.
- Everything #375/#373/#363/#352 admits: the complex interfaces, precision/recovery and rows, and the analytic transfer.
- This is a conditional finite construction, not a formal verification of the multiplication theorem.

## Credits

- **Jacob Sussman:** the E8 unit `gcert1-e8-r783`, `gx`/`gxcore`, the bridged five-stage word and the stage geometry (wht-power-saving-lean, Apache-2.0).
- **aliromman (#365):** the first coupled re-timing of this unit. Our block, sub-block and piece moves generalise its four moves, and our search reproduces its certificate value before going further.
- **DaysSky (#363, #373, #375):** B_K, the seven-stage bit construction and the halving-degree-two complex layout.
- **utcorvusvolat-dotcom (#370):** the E8 bit word.
- **rohanarun (#374):** the #365 composition in split B₃, which we compare against.
- **Our stage lineage:** retiming/descent (#287/#291/#299 via our #329/#359) and reorder (#299/#306), ported to Sussman's format. The far piece relocation is new here.
- PR #315's moment engines and outer assembly (DreamingOfClouds).

Prepared by Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance. Apache-2.0 (`LICENSE`). See `NOTICE.md` and `PROOF.md`.
