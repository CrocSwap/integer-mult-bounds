# Why the new certificate prices as claimed

**1. Same operator.** Every change is one of these:
- re-framing a gate or a set of gates;
- splitting a fan-out (s → t₁…t_k) or fan-in (t += s₁…s_k) gate into elementary additions in the same order;
- moving an elementary addition u += c·s across gates that neither read nor write u and do not write s;
- merging consecutive elementary additions that share kind, frame and the shared register (distinct partners).

Splitting and merging leave the sequence of scalar operations unchanged. In a fan-out every piece reads the unchanged source, and in a fan-in every piece adds into one destination from distinct sources. Moving an addition across operations on disjoint data, or across operations that only read s, commutes, over every coefficient ring and for all initial values.

`cxop.py` checks the result directly: the complete rational operator on all 1,023 registers (x, y and every dirty slot) after A, the scatter and B, and the 8 retained totals at the scatter, equal Sussman's original. The dirt gate and the undo gate that Sussman's invocation theorem derives from the product are therefore the same.

**2. Same family data.** These are asserted equal to the original:
- h, v, R, cst and N;
- the ports, the start and final frames, the scatter table and the retained totals with their frames.

The frame table only grows, by two frames, and is still reduced echelon with no repeats (E0).

**3. Legal frames.** `gx.check1` (E1) re-checks the following, replayed from the gates:
- every step is nested;
- every gate is at one frame;
- the y roles are at frame 0 before the scatter, and the retained slots are at their frames.

The block histograms (E6) and N are recomputed and must match the certificate's fields. In addition, every gate frame contains the x-content support of each non-y operand and of a slot destination after the gate (the source-span rule; zero violations on both certificates).

**4. Price.** In B₃ the profile is 7 × the block histogram plus 2v copies of each idle climb of the layout, with W = 6v + R and deficit 6v − 7·cst = 216. Only the block histogram changes, and b is the largest 10⁻¹⁸ grid point below the exact moment root by both rational engines with the 10⁻¹⁶ fallback, the next grid point excluded.

With the unsplit idle climbs (#375), the largest child is 38 of m = 63, so the halving degree is 2. This is #375's admitted condition, and the guard quantities it uses (m, W, R, h, cst) are unchanged.

**5. Assembly.** PR #315's `outer.assembly` with the bit c = 968197503705007/10¹⁸ (#373) and this b:
- all 47 strict constraints hold;
- the complex side binds;
- κ = 95464544449649/10¹⁷;
- κ + 10⁻¹⁸ is rejected.
