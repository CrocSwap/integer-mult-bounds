# RankLawC.lean: RankLaw condition (ii) when U meets span(non-V targets). No sorry, ~15 s, < 2.2 GB RSS
Imports the RankLaw olean (header has the build chain). Axioms: [propext, Classical.choice, Quot.sound].

Notation (end rows of the run with the V-hub ops deleted):
- X = those end rows;
- A = span X[G1];
- B = span of the V targets Rf[G1];
- N = span of the non-V targets.

Hypotheses are those of `RankLaw.rank_law` (legal, NZ, Good, token span, hNon, hTgt), with no hUN.

- `eq_iff_of_sup_eq`: if A ⊔ N = B ⊔ N, then A = B ⟺ A ≤ B ∧ B ⊓ N ≤ A.
- `rank_law_gen` (no U at all): V mix ⟺ (i) no lossy CLEAR/COPY ∧ (ii) every X g ∈ B ∧ (iii) B ⊓ N ≤ A.
- **`rank_law_proj` (the corrected (ii) for any U ⊇ B).** Let π be any linear map with π = 0 on the V targets and ker π ⊓ (U ⊓ N) = ⊥ (π reads the (U ⊓ N)-component).
  Then V mix ⟺ (i) ∧ (ii') every X g ∈ U **and π(X g) = 0** ∧ (iii).
  - So "zero W0 part" must be strengthened to "zero W0 part and zero (U ⊓ N)-component".
- `rank_law_indep`: if B ⊓ N = ⊥, (iii) is vacuous and (ii) reads "X g ∈ span V targets".
  - This holds on #7623: the 1501 public target rows have rank 1501 (CopyCheck.md), and owned targets are 0.
- `rank_law_of_gen`: the original `rank_law` is `rank_law_proj` with π = 0.
  - When U ⊓ N = ⊥, (iii) is automatic because B ⊓ N ≤ U ⊓ N = ⊥.

Hand examples (why each extra clause is needed):
- **(ii').** RankLaw finding 2: G1 = {g}, N = {n}, Rf g = e1, Rf n = e2, U = everything, X g = e1 + e2.
  - Here X g ∈ U but π(X g) ≠ 0 for π = e2-coordinate, and there is no V mix.
- **(iii).** One token e1; Rf g = Rf n = e1; X n = e1, X g = 0; empty run, so no loss.
  - X g ∈ B, but A = 0 ≠ B.
  - Only possible with dependent targets.

**Finding.** RankLaw's prose "(ii) zero W0 part" is false when U ⊓ N ≠ 0, which is the natural case U = T_X + tokens: helper tokens e_h are non-V targets.
- Minimal fix: "(ii) every V-ender row is in U and has zero (U ⊓ N)-component"; with dependent targets, add (iii).
