## §3 Lemma N (CHECKED, lemmaN.c, 72 s) and Pencil audit
**Directions.**
- The direction list (1200 directions with |Off| ≤ 76, lnprep.py) is complete.
- |Off| ≤ 76 needs ≥ 36 P112 lines ⊥ h. The only subsystems with that many lines are E7, D7, E6+A1 and E6.
- An E6 or E6+A1 always contains ≥ 2 frame lines, because the frame lines ⊥ an A2 are the complement of two overlapping Hamming supports. So those types give |Off| ≥ 77 or 78 and drop out.
- What remains: root (53), f (56) and D7 (70/73/76), each with a unique direction.

**Result.**
- For all 43435 7-flats F, at most 2 directions h have |Off(h)∖F∖G| ≤ 4 for some 7-flat G.
- This holds with no shared L, which is stronger than Lemma N.

**Pencil Lemma (SMALL2 §7).** Audited step by step, all correct:
- λ(A) is independent;
- x ∉ span λ(A);
- every fundamental circuit C_y contains x;
- distinct y give distinct directions, and Off(h_y)∖F_x∖L ⊆ F_y;
- so a − e ≤ 2, i.e. d ≤ 2.
