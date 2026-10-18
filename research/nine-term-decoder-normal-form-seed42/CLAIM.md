# Local sprint claim (no coordination post was made)

- Recorded: 2026-10-13T19:40Z. Track 40-49, structural decoder research. Assignment seed **42**,
  drawn once with `python -c "import secrets; print(secrets.randbelow(100))"` (OS randomness).
- Base commit: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` (main; selected PR1094, kappa 0.001672660197076918).
- Initial object: whole-decoder copy ratio of exact 8-term complex decoders for punctures p >= 25
  (beyond PR968's p <= 24; PR1020 settled only the single-term threshold).
- Candidates considered: (1) the p >= 25 ratio question; (2) n >= 9-term decoders (PR968 scope, PR717
  mixed-beta); (3) E-graph-only masked decoders (needs PR717 D1 spec).
- Pivot (one, evidence-driven): any complex-only gain beyond P104 is already capped by the PR589 bit
  supplier (PR968 section G), so the p >= 25 ratio question has little practical value. While
  pricing it, the n = 9 normal form (Corollaries B/C) emerged, and n >= 9 became the object.
- Method: exact linear algebra (written proofs) plus exact F2/rational census and constructions;
  bounded annealing over frames (seeds 0-2, 3000 moves).

## Result

- Delivered as `research/nine-term-decoder-normal-form-seed42/` (research note / scoped structural
  result, no kappa claim).
- Theorem A (normal form for any m), Corollary B (m = 9: at most one factor leaves the root code),
  Corollary C (one-sided 9-term = overcomplete representation), Lemma D (|S| <= 2 reduces to 8 terms),
  Propositions E-G (rigid unmasked terms, ratio classes, exact P120 cost 81 - sum delta_k and its
  necessary conditions; 39,255 non-spanning support pairs).
- No 9-term construction or search run beat 72 (P120), 64/112 or 7/13; best ratio 0.6036.
- Overlap at submission: PR1180 (both factors root-linear, any m), PR1191 (masked identities),
  PR1197 (P112 ten-term restricted cases): complementary, credited.
