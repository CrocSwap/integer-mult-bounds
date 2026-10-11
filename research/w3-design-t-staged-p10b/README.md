κ = 8.04849251275843e-4

# w3 Design T, then a shared-donor kernel, retiming and reorder on the Design T word, on #353/#357's reordered p10b base, with Sussman's E8 complex unit

A conditional finite construction with **κ = 804849251275843/10¹⁸ ≈ 8.04849251275843 × 10⁻⁴**.

- +5.45792·10⁻⁷ (+0.0679 %) over our #359 (8.04303459176812e-4).
- +1.16955·10⁻⁶ (+0.1455 %) over #358 (8.03679711866262e-4).

The bit side binds.

| side | supplier | coarse saving |
| --- | --- | ---: |
| bit | rohanarun's reordered-design PLAIN12 base word (#353/#357) → our #329 stages (descent, target, restore, sink; #357's staged word, vendored) → our Design T + completion reads + **all 471** twins → **our #359 post-Design-T stages, re-derived on this word**: shared-donor kernel, retiming, reorder, reorder2 | c = 12585899309117/(1.5625·10¹⁶) ≈ 8.05497555783488e-4 |
| complex | Jacob Sussman's E8 unit `gcert1-e8-r783` (wht-power-saving-lean `9c94857`), as in #352/#354/#359 | b = 876248285600677/10¹⁸ |

## What changed relative to #359

- **Base word.** `data/staged` and `data/parity` are #357's shipped snapshots (rohanarun):
  - #325's producer, as vendored in our #329, re-run with the local design reordered by one transposition (`producer/local_design_p10_reordered.json`, from #357) and PLAIN = 12 (#353's recipe);
  - then our #329 discovery re-derives descent (480), target (120), restore (240) and sinks (10).
  - #325's original parity word is kept as `data/parity325` for the #346 byte-for-byte control.
- **Twins.** #357 kept 470 of 471 eligible twins so that the residual sum stays ≡ 0 (mod 5). Here all 471 are kept, as #358 also does; the mod-5 condition is met by trimming the kernel to total rank ≡ 4 (mod 5) instead.
- **Stages after Design T.** These are #359's mechanisms, re-derived on this word:
  - kernel: 334 entries, rank 439, 554 donors, φ −402.05;
  - retiming: 93 gates, φ −48.79;
  - reorder: 130 moves, φ −296.89;
  - reorder2: 2 moves, φ −5.55.
- **Not included.** #358's eighteen signed helper-pair condensations and its T = 300 / eight-level arithmetic.

| word | bit coarse c | κ (E8 b) |
| --- | ---: | ---: |
| #357 (470 twins) | 8.04300919521300e-4 | 8.03654539036015e-4 |
| Design T word here (471 twins; root, not tileable alone) | ≈ 8.043038e-4 | — |
| + kernel (334, rank 439) | 8.04938e-4 | 8.04291732418766e-4 |
| + retiming (93) | 8.05016641237225e-4 | 8.04369110315724e-4 |
| + reorder (130) | 8.05488722823169e-4 | 8.04840432528145e-4 |
| **+ reorder2 (2), this package** | **8.05497555783488e-4** | **8.04849251275843e-4** |

## The transcript stages after Design T (introduced in #359; the counts in this section are #359's, on #354's word)

#354 left out the kernel, the post-sink retiming and the reorder rounds of our #329 stack. Design T rewrites or frees
the cube-layer helpers that most of #329's kernel families used. Here those three stages are **re-derived on the
Design T word itself** (`code/stages.py`, `code/stagelib.py`, frozen selections in `stages/`):

1. **Shared-donor response kernel** (our #329 mechanism; #272/#299/#319/#320 lineage).
   - On the Design T word every σ = 0 helper has its frame-ZERO completion reads at the start of the word.
   - The census re-reads each helper's F₂ response from those reads: 5,930 helpers, first frames of dims 1, 2, 3, 5,
     6, 8, 10 and 12 (L and M starters, singles, block holders, carriers and the remaining non-cube helpers).
   - An entry is a pivot p, donors D and an entrance E (nondegenerate, inside every member's first frame) with
     response(p) = ⊕ response(D).
     - p starts at E and loses its completion reads.
     - After the completion block each donor climbs to E, nested along its entries, and pays d += p at E.
     - At the end each donor pays d −= p at FULL.
   - The packing is the #320/#329 closure:
     - pools: lines plus exact first-frame intersections of rank 2 to 10;
     - 8 seeds;
     - total rank trimmed to 0 mod 5.
   - Result: 323 entries, total entrance rank 435, 553 donors, φ −386.03.
2. **Retiming** (our #329 descent2; #287/#291/#299): 47 gates (5 single, 21 pairs), φ −49.68. MOVEs are re-emitted
   just in time.
3. **Reorder** (our #329 reorder; #299/#306): 130 ADDs move next to a neighbouring operand incidence, φ −296.89.
   A second round moves 2 more, φ −5.55.
   - A third round finds nothing.
   - The retiming search re-run on the final word also finds nothing.

Each stage is bound to the exact input records hash. After applying it, `stagelib.full_check` replays:

- legality: exact nesting by integer annihilators, common ADD frames, the COPY window and final frames;
- exact validity and nondegeneracy of every used frame;
- a formal F₂ replay of every column;
- the source-span rule: every gate frame contains the integer source support of its non-target operands.

The output must equal the frozen records hash. The official #266 checkers, the nondegeneracy audit and the bank
tiling (step 3) then run on the final word.

| #359's word | bit coarse c | κ (E8 b) |
| --- | ---: | ---: |
| #354 (Design T on descent+target+restore+sink) | 8.03782713332806e-4 | 8.03137165163490e-4 |
| + kernel (323 entries, rank 435) | 8.04391808014727e-4 | 8.03745281493820e-4 |
| + retiming (47 gates) | 8.04470622543094e-4 | 8.03823969373136e-4 |
| + reorder (130) | 8.04942063398220e-4 | 8.04294652399288e-4 |
| **+ reorder2 (2), this package** | **8.04950884359437e-4** | **8.04303459176812e-4** |

Final word here: 405,317 records, 1,085 frames new relative to the reordered parity word (all nondegenerate).
Residual census {20: 5,605, 19: 763, 18: 25, 16: 7, 15: 3, 13: 2, 12: 5, 4: 960, 3: 240, 0: 480 freed}. The exact
width-100 tiling with 60 replicas uses our #329 bank template's economy fallback.

## #354's construction (unchanged; summary)

#346 applied Design T and twin condensation to #325's parity-fused word. Here the same transform is applied after
our #329 transcript stages. The transform, the completion-read regeneration and the twin pass are our own code
(`code/dt.py`, `code/comp.py`, `code/twin.py`, `code/classify.py`). On #325's parity word they rebuild #346's
published final word byte for byte (records sha256 `c6a9311a…`); `verify.sh` checks this as a control.

The stages and Design T are not disjoint:

- **descent (#287):** its 480 gates are the four 011 X-mix pairs of every cube, which Design T routes through
  their 2-dim mix frames. Design T's retimed-mix branch moves each mix back to M, so the descent gain is given
  back. The descent frames remain as rank-0 aliases.
- **kernel (#320 shared donor):** 1,190 of #329's 1,339 families use cube-layer helpers (block holders, death
  helpers, carriers) that Design T rewrites or frees. #354 left the kernel out before Design T (`STAGES = descent, target, restore, sink`); this update
  re-derives it after Design T (above).
- **target squares (#268/#287):** these touch only the 480 Y registers. **restorations (#280/#283):** 240 non-cube
  helpers, re-derived on the kernel-free word (same 240). **sinks (#283/#295):** 10, re-derived (same 10 roles).
  All three compose additively with Design T.

| word | local delta vs #325 parity word | bit coarse c | κ (E8 b) |
| --- | --- | ---: | ---: |
| #346 = Design T on #325 | {1:−480, 2:−480, 18:−480} | 8.01725878336075e-4 | 8.01083628465007e-4 (#352) |
| + target | + {1:−120, 16:−120, 17:+120} | 8.02446296230516e-4 | 8.01802892072615e-4 |
| + restore | + {1:+720, 2:−480} | 8.03139840841134e-4 | 8.02495324475724e-4 |
| **+ sinks (#354)** | + {3:−10, 17:−10} | **8.03782713332805e-4** | **8.03137165163490e-4** |

#354's word: R = 8,090 helpers, 480 freed (entrance FULL, no records), 320 new twin line frames; residual census
{20: 5,930, 19: 480, 4: 960, 3: 240}.

## Verify

    bash research/w3-design-t-staged-p10b/verify.sh /tmp/dtst-verify          # full (~3 min)
    bash research/w3-design-t-staged-p10b/verify.sh --quick /tmp/dtst-verify-q

Needs Python 3.11+ with numpy and mpmath, a C++17 compiler (`CXX`) and Boost headers (`BOOST_INCLUDE`). Steps:

0. `MANIFEST.sha256` (every file, none unlisted).
1. The vendored staged word and the parity word are decompressed and hash-checked, and the staged word is priced.
2. Design T, completion reads and twin condensation (all 471 twins) are applied; the result must equal
   `data/designt`. Full mode also rebuilds #346's final word from #325's parity word (`data/parity325`).
   2b. The four frozen post-Design-T stages (kernel, retime, reorder, reorder2), each with its full check and frozen
   output hash; the result must equal the shipped final word (`data/final`).
3. Our exact replay: MOVE nesting by exact integer annihilators, ADD common frames, the COPY window, final frames,
   and a formal F₂ replay of every column (sources restored, targets x_t + y_t, helpers restored). Then #266's
   official `cohort-legality-independent` and `cohort-five-stage-columns` checkers, ported to h = 20 (only the
   constants h, v and R changed; 11,930 columns, six omitted-bridge controls). Then exact nondegeneracy under
   G = I − J/9 of all frames new relative to #325's word, and an exact width-100 bank tiling of the residuals
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
- Reordered-design PLAIN12 base word and its staged snapshot: rohanarun (#353/#357). Keeping all 471 twins follows
  eumemic's #358.
- E8 supplier as complex side: DaysSky (#352).
- E8 unit and the gx/gxcore checkers: Jacob Sussman.
- Official checkers: #266.
- Transcript stages: our #329 and #354, with the #268/#280/#283/#287/#295 lineage (eumemic's #268/#273, rohanarun's
  descent and #300 restart loop) and the #272/#299/#319/#320 shared-donor kernel lineage. The reorder screen follows
  our #299/#306; eumemic's later #330–#347 stages (cross-entrance retimings, nested donors, carrier switches) are not
  used here.

See `NOTICE.md`. Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance; Apache-2.0.
