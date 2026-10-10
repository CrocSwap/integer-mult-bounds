# Stage argument (additions to PROOF-PR310.md)

Every stage maps a word that passes PR #310's checks to a word that passes the same checks. The final word is
re-admitted by the unchanged native chain: legality, all-column F₂ (global and compact), exact charts, banks, price
and invoice. The stage checks below are extra evidence.

1. **Kernels.**
   - Let p be a pivot with donors d_i and odd integer coefficients a_i, where C_p + Σ a_i C_{d_i} ≡ 0 (mod 2) on the literal prefix responses up to the cut.
   - p's prefix reads are omitted. Adding a_i·p into d_i after the cut and subtracting it at the end changes every target's prefix by C_p + Σ a_i C_{d_i}, which is 0 over F₂, and restores every donor.
   - p enters at E. E is nondegenerate and contained in every member's first frame, so all chains stay nested.
   - Entrance rank 840 ≡ 0 (mod 3). The residual census is tiled exactly, and the bank count equals 117,563 − (35,280 + 840)/3.
   - Zero-response singles have no prefix reads (C_p = 0), so they enter at their first frame with no gates added.
2. **Target prefix.** The dependent's window response equals the signed sum of its retained targets' responses. This is checked exactly with integer fingerprints and over F₂. Removing the window reads and inserting setup and restore leaves every final value unchanged, as the integer replay confirms.
3. **Plateaus.** Each retimed component's gates commute as a block. The new frame is the exact intersection of the next frames, so it is contained in each of them, and the chains stay nested.
4. **Reorder.** A relocated ADD a += c·b crosses no read of a and no write of b. It therefore commutes over every commutative ring. MOVEs are rebuilt from the incidence frames as single nested climbs, with endpoints fixed.
5. **Price.** Rank mass and the deficit (35,200) are unchanged; stock is derived from the actual entrance frames. The exact price is computed against PR304's supplier at 7635/10⁷. At that value the 47 assembly constraints hold at the bit grid cap, and the adjacent grid point is rejected. PR233's supplier is still regenerated and guarded (PR256), but it is not the priced supplier.
