# ExportLaw.lean: BIG-EXPORTLAW E1, E2, T4*, scope counterexamples (Lean 4 + Mathlib), no sorry, ~6 s, 2.0 GB RSS
Source: cards/WILD/BIG/EXPORTLAW/THEORY.md (E1, E2, T4*, E4) and RESULT.md (d). Lane LEAN-NEXT4, Nov 16.
Self-contained, namespace ExportLaw. Event model = JunkLB2's `Ev` (arrive / born / add / depart) extended with scale, clear, copy. Axioms (all 12 printed): [propext, Classical.choice, Quot.sound].

**Model.** One chart F, events in time order, rows in initial-row coordinates (Reg → K), from the empty state.
- `arrive i v` (owned INIT = `arrive o 0`), `born b` (row = e_b), `add i j c` (i ≠ j), `scale i u` (u ≠ 0), `depart i`, `clear i` (row := 0), `copy i j` (row_i := row_j).
- Legal: arrivals/births of absent registers; every op on present registers only (co-presence).
- `held` = S_F, every row present at any state. `removed` = departing, cleared and COPY-overwritten rows.

**E1, `E1_reverse` (any word).** span S_F ≤ span(final rows at F) + span(removed rows). Exactly the card's statement and proof (backward step: ADD/SCALE invertible, arrivals add, depart/clear/copy remove one row).

**E2, `E2_export` (class N), STRONGER than the card.**
- Statement: rank(ρR + ρK_F) + |HB| ≤ ke + kd + od + oe + (helper departures).
  - R: any set of rows held at F (e.g. kept rows at kept events). K_F: span of the final rows of kept enders.
  - HB: helpers born at F and gone at the end (free birth stays). Since helper departures = hp + hb, this is hp ≥ rank − ke − kd − od − oe.
  - **No −clr term.** `E2_card` derives the card's version (with −clr, in ℤ) as a corollary.
- Hypotheses:
  - H (helpers), Kp (kept), Ow (owned) partition the registers;
  - class N: a helper still at F at the end ends as its own token;
  - ρ is linear and kills helper tokens.
- NOT needed (the card's proof uses them): kept enders' rows free of helper coordinates; "helpers born at F that depart do not end at F".
- Proof route: NOT through E1. It uses
  - the forward span law (`forward_span`: S_F ⊆ span(arrival rows + birth tokens), valid with CLEAR and COPY);
  - `forward_count`: dim φ(S_F) + |tokens held at F and killed by φ| ≤ #entries;
  - the stay count (`stay_count`: entries = departures + enders, per register class).
  The killed tokens are those of helpers born at F and gone, plus helper enders.

**T4\*, `T4_star` (class N, owned arrivals counted).**
- Statement: dim π(S_c) + |BNX| ≤ (public departures) + |Ey| + (owned entries), where BNX = non-X registers born at c and gone at the end.
- Card form d + y + oa + xb: public departures = (departures ending arrival stays) + (departures ending birth stays). The birth-stay departures of non-X births cancel against |BNX|; those of X births are ≤ xb.
- **`T4_card` (LEAN-NEXT5), now formal:** dim π(S_c) ≤ d + |Ey| + oa + xb, with d = public registers not born at c that depart, and xb = |born at c ∩ X|. The extra hypothesis is `hOnce`: each PUBLIC register enters c at most once. In a Legal run this means it leaves at most once and never returns. Owned registers are unrestricted. Helper `nDep_eq_sum`.
- hOnce on #7623 [C, exact]: cards/WILD/BIG/EXPORTLAW/lean5/once.py on LOANBUILD/hit_loan_14 (GAPMAP's #7623 build). 1,501 public registers, 7,711 (register, chart) entries, 0 repeats. Every one of the 6,210 public moves strictly raises the chart dimension. One owned (register, chart) pair is entered twice, which is allowed.
- Hypotheses:
  - class N: a public non-Y ender ends as its own token;
  - π kills those tokens and the tokens of non-X births.
- No "arrivals carry no c-born coordinates" (owned registers may descend), matching the card.

**Scope: which terms can be dropped.**
- `drop_owned_false`, **found false**: dropping od, oe, clr together. Chart-1090 mirror:
  - owned o1 (1510) arrives carrying e2 and stays; kept x arrives with e0; x += o1; x departs;
  - owned o2 (1520) INITs, o2 += o1, o2 departs.
  - Kept rows {e0, e0+e2} have rank 2 > 1 = ke + kd + hp. With od = oe = 1, E2 holds.
- `drop_od_false`, `drop_oe_false`: dropping od alone, or oe alone, is also false (one owned register that departs, resp. ends).
- **Dropping clr alone is TRUE** (`E2_export`). This corrects the card's "the proof needs all three": od and oe are each necessary, clr is not.
- All counterexamples are concrete runs over ℚ, checked by `simp`/`decide`. Since ρ = id and there are no helpers or kept enders, K_F = 0, hp = hb = 0.

**Still prose / not formalized.**
- The class-K pricing (rank computed from the fixed kept stream, independent of the build). The theorems are per build, as is the card's proof.
- ~~rank_p ≤ rank_Q~~: proved in Nov15/RankModP.lean (LEAN-NEXT5).
- Summation over charts (distinct stays).
- E3 / E5 (local tightness [H], relay negative).
