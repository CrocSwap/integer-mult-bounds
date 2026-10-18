# PROOF-NOTE-SW4: read-set exchange on four entering-copy pairs

Construction by BRoute (`construction/sw4/`, with the author's notes in `construction/sw4/NOTES.md`). Driver:
`construction/sw4/reproduce_sw4.py`.

## The move
In P6k4 (`0390ec65…`; research/gauge44-promo-p6sw applied the same exchange to P6k3 `a38bb414…`), each of four entering packet copies h is written first as h = E_h + r: copy gate add(h, r, 1)
from a non-target face register r, with E_h being h's entering content. The pairs are (h, r) =
(461, 25), (581, 89), (591, 415), (603, 431). For each pair the read sets of h and r are exchanged in phase B:
- every post-copy target read add(t, h, c) becomes add(t, r, c), and t's entrance pre-read add(t, h, −c) (taken
  while h = E_h) is deleted;
- every target read add(t, r, c) becomes add(t, h, c), with a pre-read add(t, h, −c) inserted after h's last existing
  pre-read and before h's copy gate.

Since h − r = E_h after the copy, each target's value is unchanged at the end of B. The builder checks this for every
register mod p (p = 2147483629). Moved and inserted gates take the plain join of their operands' current frames.
Every other B gate and every early-cleanup tail keeps span(old frame + current operand frames). Targets must stay
inside u_t^⊥, and tails and ends must contain the current frame. start_extra, helper_final, cleanup and the helper
numbering are unchanged.

## Effect
Output `d232183f…`. Width 3778 is unchanged. The profile goes from {1:2572, 2:326, 3:430, 4:194, 5:56, 8:8} to
{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}, a delta of {1:−24, 2:+16, 3:+8, 4:−8}, the same as on P6k3. The four
exchanges are additive. The fourth promotion group (659, 661–663; gates B420–431) commutes exactly with the exchange:
there is no index or register overlap, and SW4Reviewer checked that applying the k3→k4 frame and start differences
to f35a852b gives d232183f. Ideal κ +3.271e-7 over P6k4.

## Checks rerun on every rebuild
- `build_sw4.py` (standard library only): the input sha pin; the 16 explicit moves of `SW4-RECIPE-P6k4.json`; B-end
  state exactness mod p; frame caps, tails and ends; the output sha, profile and W. It also runs 4 controls, all of
  which must hold, each at the exact site pinned in the recipe's `rejection_expected` (all three keys N1, N2 and N3 are required):
  - C0: the identity recipe reproduces the input B and early_cleanup byte for byte;
  - N1: h2r without deleting the pre-read is rejected by exactness, with changed B-end rows exactly {168, 171};
  - N2: a partial exchange (one read only) is rejected by the frame cap, first at ('cap', B1192, register 169), 10 violations;
  - N3: an inserted pre-read with the wrong sign is rejected by exactness, with changed rows exactly {129, 130, 169, 170}.
- The per-end layer-end controls (`../layers_p6n/layer_end_controls.py`, Q6Reviewer-signed): 95 rejected.
- PR635's native chain, with the canonical word, local programs and Clifford recipes pinned (`LOCAL-PINS-sw4-P6k4.json`).
  The native transport audit re-checks every column and native frame of the exchanged word.

## Scope of the search (BRoute)
The search was exhaustive within the single-pair family only. NP has 107 copy pairs, and 54 of them have movable
reads. Over those, every nonempty subset of one pair's movable reads gives 602 candidates: 564 are frame-illegal, and
the 38 legal ones are all full single-pair exchanges, of which exactly these 4 are positive. Cross-pair combinations
of partial moves were not enumerated.
