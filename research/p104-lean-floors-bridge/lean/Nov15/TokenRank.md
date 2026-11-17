# TokenRank.lean: BIG-TOKENRANK TR1 box law, the swap canceller, "the regress stops", TR3 cut lemma, TR4. No sorry, ~5 s, 2.1 GB RSS
Lane LEAN-NEXT8, Nov 16. Source: cards/WILD/BIG/TOKENRANK/THEORY.md (TR1, TR3/TR4, "why no class-K row"), RESULT.md §b.
Axioms (9 printed): [propext, Classical.choice, Quot.sound].

Build (imports the oleans of ExportLaw and TokenCancel):
  lake env lean -o .lake/build/lib/lean/Nov15/ExportLaw.olean Nov15/ExportLaw.lean
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean Nov15/TokenRank.lean

**Part A: TR1 box law.** ExportLaw's one-chart model, from the empty state.
- Exits = departure rows + CLEARed/COPY-overwritten rows + final rows. Entries = arrival rows (an owned INIT arrives as 0) + birth tokens.
- `TR1_span`: span(exits) = span(entries).
  - Holds for every legal word, including CLEAR and even COPY (via ExportLaw.forward_span and E1_reverse).
- `TR1_count`: |exits| = |entries| + #(CLEAR/COPY events).
- `TR1_pure` (TR1(b), (c)): if no arrival row has an H_c coordinate, then span(exits) ∩ (c-pure) = A_c := span(arrival rows, tokens of non-H_c births).
  - It does not need H_c ⊆ births at c.
- `Ac_finrank`: dim A_c ≤ #arrivals + #(non-helper births).
- `TR1_tokens`: every token born at c has a nonzero coordinate in some exit row.

**Part B: swap and regress.**
- `swap`, `swap_token`: suppose h's row is exactly e_h. Then `j -= h; h += j` is legal and gives:
  - h ← j's old row, j ← (j's old row) − e_h, everything else unchanged;
  - h's e_h coordinate becomes r_j(h) and j's becomes r_j(h) − 1.
- `regress_stops`, `regress_stops_swap`: two legal words with the same entries have the same span(exits), hence the same A_c and the same token directions.
  - So inserting a swap (two ADDs) anywhere changes nothing that TR1 counts: the debt −e_h on j is not a new direction.
  - This is the formal content of "TR1 counts directions, not carriers".

**Part C: TR3/TR4.** TokenCancel's multi-chart model, plus co-presence (`Co`) and the cut hypothesis (`Cut`): every MOVE into Ω comes from Ω or from s0.
- `TR3_claim`: suppose Φ kills the rows initially in Ω, the birth tokens born in Ω, and every row moving s0 → Ω. Then Φ kills every row in Ω at every time (`Always`).
- `TR3_cor` (duality form): for every register in Ω at the end, π_B(row) ∈ span π_B(rows moving s0 → Ω), for any B none of whose registers is born in Ω (e.g. B = Kept_s).
- `flow`: (p-moves s0 → Ω) + (at s0 at the end) ≤ (MOVEs in and INITs at s0) + (births at s0) + (at s0 at the start).
- `TR4`. Hypothesis: no non-helper born at s0 moves s0 → Ω (the kept departers go outside D(t)). Then:
  - (helper MOVEs s0 → Ω) ≥ ρ − (non-helper MOVE/INIT arrivals at s0);
  - ρ = rank of the B-projections of the rows of any registers ending in Ω.

**Findings (prose statements false as written).**
1. **TR1(a) "|exits| = |entries|" is false with CLEAR.** That clause is in TR1's own op list, and so is "one vector per entered register".
   - `TR1_count_literal_false` over ℚ: born b; clear b. One entry, two exits (the cleared e_b and the final 0).
   - Minimal fix: |exits| = |entries| + #CLEAR (`TR1_count`), or count a CLEAR as also an INIT entry of 0. The span law is unaffected.
2. **TR4 depends on what hd(s) counts.**
   - Lean proves it with hd = all helper departures s → Ω, birth stays included.
   - If hd(s) means PAID stays (helper departures − hb, as in FloorGlue), TR4 is FALSE once a helper is CLEARed at s.
   - Hand counterexample, run exactly in Python:
     - h1, h2, h3, k born at s;
     - h3 += h1; CLEAR h3; h3 += h1; h2 += h1; h1 += h2; h1 −= h3; h1 += k;
     - k (= e_k, s-pure) → outside D(t); h1 (= e1 + e2 + e_k) and h2 (= e1 + e2) → ω ∈ Ω (both birth stays);
     - h3 (= e1) stays, or leaves outside D(t);
     - kept k2 born at ω, k2 += h1 − h2, so k2 = e_k2 + e_k.
     - Then ρ_t = 1, kept/owned arrivals = 0 and paid hd(s) = 0.
   - Minimal fix: count birth stays into Ω in hd, or forbid CLEAR of helpers at s.
   - On #7623 the CLEARs at dim-1 charts are all owned, so the numeric "TR4 adds 0" (ρ_t = 0 everywhere) is unaffected.

**Scope.**
- The swap's "h carries no token" needs r_j(h) = 0 (j has not yet read h); it is stated as a hypothesis-free formula.
- TR2 (the per-h linear system) and the class-K pricing stay prose / [C].
- B being born only at s0 is an input (`hB`), and so is the q-marking of births at s0 (`hq`).
