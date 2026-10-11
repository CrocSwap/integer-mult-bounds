# κ = 8.03654539036015e-4: #354's staged Design T + twins on a reordered-design p10b base word (+0.064 % over #354)

**Conditional κ = 160730907807203/(2·10¹⁷) ≈ 8.03654539036015·10⁻⁴**, +5.17·10⁻⁷ (+0.064 %) over #354 (8.03137165163490·10⁻⁴).
Bit side binds; complex supplier = Sussman's E8 unit as in #352/#354, unchanged.

Change: the base word. #325's producer (in #329's package) is re-run with the 12-entry local design list reordered by one
transposition (`producer/local_design_p10_reordered.json`) and PLAIN = 12. #329's transcript stages (descent, target, restore,
sink; no kernel, as in #354) are re-derived on that word with #329's own discovery scripts (480 descent gates, 120 target groups,
240 restorations, 10 sinks), then #354's Design T + completion reads + twin condensation run unchanged except that twin keeps
470 of 471 eligible planes (residual sum ≡ 0 mod 5 for the width-100 bank tiling). Bit coarse c = 8043009195213/10¹⁶ (was
160756542666561/(2·10¹⁷)). The same chain on #325's original design reproduces #354's κ exactly (control run).
`data/parity` is the new base parity word; `data/parity325` keeps #354's for the #346 control (step 2c).

DRAFT: full verify.sh replay running. Credits: chafreaky (#354, #329), DaysSky (#352), J. Sussman (E8), LJH-217 (#346), #310,
#325/#315. #354's README follows.

---

κ = 8.03137165163490e-4

# w3 Design T and twin condensation on our transcript-staged p10b bit word, with Sussman's E8 complex unit

A conditional finite construction with **κ = 80313716516349/10¹⁷ ≈ 8.03137165163490 × 10⁻⁴**, +0.2563 % over
#352 (801083628465007/10¹⁸ ≈ 8.01083628465007e-4). The bit side binds.

| side | supplier | coarse saving |
| --- | --- | ---: |
| bit | #325's p10b word → our #329 stages (descent, target, restore, sink) → #310's w3 Design T and twin condensation (as ported to h = 20 by #346), reimplemented | c = 160756542666561/(2·10¹⁷) ≈ 8.03782713332805e-4 |
| complex | Jacob Sussman's E8 unit `gcert1-e8-r783` (wht-power-saving-lean `9c94857`), as used by #352 | b = 876248285600677/10¹⁸ ≈ 8.76248285600677e-4 |

## What changed

#346 applied Design T and twin condensation to #325's parity-fused word. Here the same transform is applied after
our #329 transcript stages. The transform, the completion-read regeneration and the twin pass are our own code
(`code/dt.py`, `code/comp.py`, `code/twin.py`, `code/classify.py`). On #325's parity word they rebuild #346's
published final word byte for byte (records sha256 `c6a9311a…`); `verify.sh` checks this as a control.

The stages and Design T are not disjoint:

- **descent (#287):** its 480 gates are the four 011 X-mix pairs of every cube, which Design T routes through
  their 2-dim mix frames. Design T's retimed-mix branch moves each mix back to M, so the descent gain is given
  back. The descent frames remain as rank-0 aliases.
- **kernel (#320 shared donor):** 1,190 of #329's 1,339 families use cube-layer helpers (block holders, death
  helpers, carriers) that Design T rewrites or frees. The kernel is left out here (`STAGES = descent, target,
  restore, sink`).
- **target squares (#268/#287):** these touch only the 480 Y registers. **restorations (#280/#283):** 240 non-cube
  helpers, re-derived on the kernel-free word (same 240). **sinks (#283/#295):** 10, re-derived (same 10 roles).
  All three compose additively with Design T.

| word | local delta vs #325 parity word | bit coarse c | κ (E8 b) |
| --- | --- | ---: | ---: |
| #346 = Design T on #325 | {1:−480, 2:−480, 18:−480} | 8.01725878336075e-4 | 8.01083628465007e-4 (#352) |
| + target | + {1:−120, 16:−120, 17:+120} | 8.02446296230516e-4 | 8.01802892072615e-4 |
| + restore | + {1:+720, 2:−480} | 8.03139840841134e-4 | 8.02495324475724e-4 |
| **+ sinks (this package)** | + {3:−10, 17:−10} | **8.03782713332805e-4** | **8.03137165163490e-4** |

Final word: R = 8,090 helpers, 480 freed (entrance FULL, no records), 320 new twin line frames; residual census
{20: 5,930, 19: 480, 4: 960, 3: 240}.

## Verify

    bash research/w3-design-t-staged-p10b/verify.sh /tmp/dtst-verify          # full (~3 min)
    bash research/w3-design-t-staged-p10b/verify.sh --quick /tmp/dtst-verify-q

Needs Python 3.11+ with numpy and mpmath, a C++17 compiler (`CXX`) and Boost headers (`BOOST_INCLUDE`). Steps:

0. `MANIFEST.sha256` (every file, none unlisted).
1. The vendored staged word and the parity word are decompressed and hash-checked, and the staged word is priced.
2. Design T, completion reads and twin condensation are applied; the result must equal the shipped final word.
   Full mode also rebuilds #346's final word from the parity word.
3. Our exact replay: MOVE nesting by exact integer annihilators, ADD common frames, the COPY window, final frames,
   and a formal F₂ replay of every column (sources restored, targets x_t + y_t, helpers restored). Then #266's
   official `cohort-legality-independent` and `cohort-five-stage-columns` checkers, ported to h = 20 (only the
   constants h, v and R changed; 11,930 columns, six omitted-bridge controls). Then exact nondegeneracy under
   G = I − J/9 of all 1,000 frames new relative to #325's word, and an exact width-100 bank tiling of the residuals
   with 60 replicas.
4. Sussman's `gx.check1` (exact scalar identity) and `gxcore` mirror on the E8 certificate, with a flipped-sign
   control rejected (E5). Then the five-stage price at h = 9, m = 45, W = 4v + R, deficit 4v − 5·cst, and b by both
   rational engines with the 10⁻¹⁶ fallback.
5. Bit coarse saving by both engines (fixed deficit 4v − 5h(h − 2) asserted; residual of a restored helper is
   dim E − σ), then #315's outer assembly: 3 bootstrap steps, η = 10⁻¹², 47 strict constraints, adjacent κ
   rejected.

Regeneration of the staged word (optional): `code/export_stages.py` on our #329 package (`p10b-stages`, `c6b1a28`)
with `portable_bit.STAGES = ('descent','target','restore','sink')` and the two re-derived selections in `stages/`
(the builders `discovery/build_restore_selection.py` and `build_sink_selection.py` with the kernel removed from their
stage lists). Its output after the sink stage is `data/staged` byte for byte.

## Open obligations

These are inherited from #346/#352 and are not ported here: #310's native downstream chain (bank review with
charts, changed projector charts, geometry admission, finite invoice) and #315's prime/finite stages for an edited
word. Only bank feasibility is shown. All inherited interfaces of #315/#325/#329 remain assumptions. This is a
conditional finite construction, not a formal verification of the multiplication theorem.

## Credits

- Bit base word and the p = 10 five-stage pipeline: DreamingOfClouds (#325 on #315).
- Design T and twin condensation: utcorvusvolat-dotcom's w3 work (#310), ported to h = 20 by LJH-217 (#346).
  Both were read as data and reimplemented here.
- E8 supplier as complex side: DaysSky (#352).
- E8 unit and the gx/gxcore checkers: Jacob Sussman.
- Official checkers: #266.
- Transcript stages: our #329, with the #268/#280/#283/#287/#295 lineage.

See `NOTICE.md`. Prepared by Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0.
