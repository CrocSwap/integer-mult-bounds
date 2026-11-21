# Corrections to the lane notes

The notes in `notes/` are lane write-ups made during one working day; where they disagree with this file, this file is right.

- TIGHT55 / DRAT55: the first cube partition (global d-lex-leader plus one cube per orbit-lexmax inactive set) was not a proof. d = (9,9,8,6,6,8,9,4,4,2,9,0,5,6,8,8) satisfies all 384 lex-leader constraints but its inactive set I = mask 1091 is not orbit-lexmax (exact witness: `data/tight55_gap`, verified by its check.py). The sound per-cube re-run was only partly finished in the lane notes; the DRAT-certified repair of the tight B-linear class (budget 55 UNSAT, min 56) is in #7852 (drat/). Statements in notes/tight55.md and notes/drat55.md that predate this are superseded.
- LEVEL-WALL is false (notes/nogain.md): an E8 network via 96 single-port gatherers and 8 hubs has D = 104 and level sum 0. The core target is NET-D56 in drop form.
- CT-COVER is false over every field (notes/ctcover.md, code/ctcover/ctsplit.py): R = 2 < mass 3 by climb sharing.
- ZIGZAG (mass <= cost + relay slack) is refuted (notes/unify.md section 11).
- CONJ DECOMP is false [P Lean decomp_false, source lean_extra/CallerDecomp.lean, not rebuilt here]; a legal Q = 0 non-tight indecomposable word exists (code/decomp/dc1.py).
- S_spec = 865.58 is not a valid floor for the frontier word (notes/additive.md): 'deaths at V' is a compiler convention, not a verifier clause; the quoted class-restricted ceilings .0078006 / .0075768 are unsound as stated. No ceiling below .008 is proved.
- The k = 72 and k = 73 caller bounds (certs/) are conditional LP bounds: RC2 is [P] (Lean rc2_pair) but the extra rows (coord, pfix, shal, dyadic, RC) are paper-[P] and not in Lean. PR #7856 showed the Lean-level Q = 0 rows alone do not give 128.891 at k = 71..73. The Lean chain in #7852 covers k >= 74 (CallerHP closed form) and k >= 77 for Q >= 1.
- 'Padding' (adding tightness-free copies) is false; tightness is a genuine hypothesis (data/direct_sum).
