# FloorEndToEnd.lean: the class-K floor rows as theorems about the word. No sorry, ~9 s, 2.25 GB
Lane LEAN-NEXT17, Nov 16. Imports Nov15.FloorGlue (so ExportLaw, Floor). Build: `lake env lean -o .lake/build/lib/lean/Nov15/FloorEndToEnd.olean Nov15/FloorEndToEnd.lean`.
Axioms: the 21 printed theorems use exactly [propext, Classical.choice, Quot.sound]. No `sorry`, no `native_decide`, no `axiom`. Any field K with decidable equality (ℚ in use).

## What is now a theorem (was a hypothesis in Floor / FloorGlue)

**Model (§1–3).** A multi-chart op model with the shipped verifier's ops and legality (independent.py `native()`):
- Ops: INIT (owned, row 0), CLEAR, MOVE, ADD, SCALE, COPY (`i := a·j`). Public registers start at their initial frame with their own token.
- `LegalEvG` is the verifier's checks, with the coefficient-size and smoothness checks dropped. So the model is a relaxation and the theorems cover more words.
  - INIT/CLEAR only on owned registers.
  - ADD/COPY need i ≠ j and co-location; SCALE needs u ≠ 0.
  - **l.51**: a public MOVE a → b needs a < b; an owned MOVE needs a < b or b < a.
- `Accepted` = legal, plus Pub = registers with an initial frame, H ⊆ Pub, plus the Jacobian check on helpers.
  - The Jacobian check is `bad_inputs == []`: target[r] = {r: 1} for every non-main public r, so a helper ends as its own token.
  - independent.py *reports* `bad_inputs`; it does not assert it. Acceptance means the report is [].
- Charts `C`: any finite partial order. For the verifier, take frame indices with a ≤ b iff a = b or span a ⊊ span b; then a < b iff span a ⊊ span b, which is l.51's `<`. Fresh frames are just more elements of C.
- Each global word projects to one ExportLaw run per chart (`proj`), via the one-step simulation `step_sim`:
  - initial residents → `born`; MOVE in → `arrive r row`; MOVE out and CLEAR → `depart`; INIT → `arrive o 0`; ops at c → ops.
  - `proj_legal`: the projection is a legal ExportLaw run from the empty state, and its final state holds exactly the registers ending at c, with their global rows.

**Derived facts.** Each was a hypothesis before and is now proved on the word.

| Former hypothesis | Now proved by |
|---|---|
| op semantics (adds stay in a chart, a MOVE carries only its own row) | the model itself, plus `step_sim` / `proj_legal` |
| **hOnce** (kept registers enter a chart once; "[C] on #7623") | `hOnce_proj`: for EVERY accepted word and every public register (kept and helpers), from l.51 alone (`once_aux`) |
| class N for helpers | `Accepted.helper_final` (the verifier's Jacobian check) plus the simulation |
| ρ kills helper tokens | ρ is concrete: `rhoH` deletes helper coordinates |
| `hent` | `entry_count'`: FloorGlue.entry_count with oa sharpened (see the finding below) |
| K_c, R(c), hop rows ⊆ S_c | `K_held`, `R_held`, `move_held`, `tail_held`, `snapRow_held` |
| hP (R0(a)): ρS_c ⊆ span ρK_c + span ρ(helper arrivals) | `hP_word`, via forward_span on the projection |
| hvec (a helper arrival was held at its tail, tail < head) | `hvec_word`, from l.51 |
| hd(c) = fibre of the global stay list | `hd_fibre`, `sum_hd`. `stays` = (helper, chart) pairs with an arrival that later leaves. These are distinct by hOnce |

**Class K (§5).** `ClassK D w`, relative to word-independent data D (D.Kρ, D.Rρ, D.ka, D.oa, D.kb):
- (K1) every nonzero kept/owned arrival ρ-row and every kept birth token at c is in D.Kρ c;
- (K2) every element of D.Kρ c is such a row or a token final of a kept ender (`Kfin`);
- (R) D.Rρ c ⊆ ρ-rows of non-helper registers at c at some visited state;
- kaW, oaW, kbW ≤ D's counts.
- `classK_of_counts`: the literal counts used by the data (indep_word.py nka = kept public MOVE arrivals, noa = owned MOVE arrivals, nkb = kept births) satisfy the count conditions.
- So "kept stream fixed (as rsdata/indep_word read it off #7623), helpers free, verifier-accepted" implies ClassK D₀. #7623 is in ClassK D₀, with D₀ its own kept data.

**The row families as theorems about the word (§6, §8).** For every class-K word w:
- `R1_row` / `lam_row` (λ rows):
  - hd(c) ≥ max(0, rank(ρK_c + ρR(c)) − ka − oa − kb).
  - GAPMAP's needK is redundant here: needK ≤ max(0, needR) on all 977 GAPMAP charts (checked this lane; 0 exceptions).
- `F4_row` (u rows, R2/F4):
  - Hypotheses: ψ kills ρK_t and every ρK_{s'} with s' < t, s' ≠ s, and ψ(n) ≠ 0 for some n ∈ ρR(t).
  - Conclusion: w has a helper MOVE out of s itself into some c with s < c ≤ t whose ρ-row ψ sees.
- `R3_row` (α/β rows):
  - Hypotheses: helper MOVEs into c from pairwise distinct tails, each serving a certified commodity with c ≤ t_j, plus RA ⊆ ρR(c) killed by every ψ_j.
  - Conclusion: hd(c) ≥ rank(ρK_c + RA) − ka − oa − kb + #hops. RA = ∅ gives α (hd ≥ #hops − slr); RA = ρR(c) gives β (hd ≥ needR + #A-hops).
- The LP point x(w), as in rsnative.py:
  - y = hd on Nat;
  - z_{s,c} / a_{s,c} = there is a hop s → c serving some (resp. some type-A) certified commodity of source s;
  - x_m = head m is used by a serving hop into a non-Nat chart.
- Row theorems for x(w):
  - `alpha_row`, `beta_row`, `gamma_row` (a ≤ z);
  - `u_row`: Σ_{Nat c, s<c≤t} (a or z) + Σ_{heads} x ≥ 1, for any head set containing head(s, c) for every non-Nat c with s < c ≤ t;
  - `objective_le`: Σ_{c∈Nat} hd(c) + Σ_m x_m ≤ #stays, given slr ≤ 0 off Nat.
- `R1_floor_word`: cost ≥ κ·Σ_c max(0, needR_c) on every class-K word. This is λ rows only, no LP, given per-stay cost ≥ κ.
- The structural conditions on the row data hold by rslp.py's construction (read this lane):
  - u row k = (t, s) lists z/a for every Nat c with span s ⊊ span c ⊆ span t (a superset of our c ≤ t), and every minimal head s+v with v ∈ span t \ span s (a superset of our head(s, c));
  - α and β sum over all z / a columns into c;
  - γ pairs each a with its z;
  - Nat = {L > 0 or slr ≠ 0}.

## What remains (exact list for PROVED.md §3)
1. **Per-stay cost ≥ κ** (hypothesis `hκ : ∀ p ∈ stays, κ ≤ cost p`).
   - Why not discharged: the op model has no D0. The step needs GAPMAP §1's attribution (each public MOVE a→b of a register with final dim e is charged h_e(a,b); the telescoping identity D0(r) = f(e−d0) − Σ f(gaps) is asserted per register on #7623) plus JunkLB2.T4_stop_cost (h ≥ f(2) when b − a ≥ 1 and e − b ≥ 1).
   - The geometric side conditions ARE available here: l.51 gives b − a ≥ 1 (strict span containment raises dim), and a paid stay departs upward, so e > b.
   - What is missing is a formal D0 for words (f, h, the telescoping identity). This is a modelling gap, not a proof gap.
2. **Extraction = family instances** (checked input, Python, two independent extractions agree):
   - each of the 892 exported rows (FloorCertData) is an instance of λ/α/β/γ/u with D = D₀;
   - the rhs numbers are the exact ranks (needR, slr over ℚ; indep_R1.py);
   - each u row's ψ is `Certified` (rsess.py exact Fractions; indep_F4.py re-verified 2,850);
   - type-A flags imply ψ kills ρR(c) (indep_R3.py);
   - Nat ⊇ {slr ≠ 0}.
   - Why not discharged: the row → family labels and D₀ (378-coordinate rational rows, 2,850 functionals) are not exported into Lean. A generator lane could export them and kernel-check them with `decide` (rank certificates, ψ·w = 0 checks), at a cost similar to FloorCertCheck.
3. **D₀ is #7623's kept data in the Lean definitions' sense** (K1, K2, R, counts). This is the same checked input as item 2: the Python replay implements `keptArr` / `keptFin` / `keptSnap` / `kaM` / `oaM` / `kbM`.
4. **Gluing to FloorCert.** FloorCert's `stops_ge_780` needs x on the 18,868 support columns. That is x(w) restricted, which is sound: dropped columns meet no kept row and cost ≥ 0. With items 2 and 3, every class-K word gives #stays ≥ 780, and with item 1, cost ≥ 1,081.31 D0/call.
   - `WellFoundedLT C` is an instance argument; it holds for finite C.

## Findings
- **Gap in the old chain, fixed (oa).** The data count oa as owned MOVE arrivals only (rsdata/indep_word `noa`: INITs not counted). ExportLaw/FloorGlue's count oa = all owned entries, and an owned INIT is `arrive o 0`.
  - So FloorGlue.chart_floor does not by itself imply the exported λ/α/β rows wherever owned INITs sit: 61 Nat charts carrying 93 of #7623's 180 INITs. The proved bound there was weaker by the INIT count.
  - Minimal fix, proved: `forward_count'`, with zero-row entries free, i.e. dim φ(S_c) + |Tk| ≤ #entries − #zero entry rows. Then `entry_count'` / `chart_floor'` hold with oa := owned entries − zero-row entries ≤ owned MOVE arrivals (`oaW_le`).
  - The prose (RANKSTEINER: "oa = owned arrivals") is right; FloorGlue.md's "oa = owned entries" is the over-weak form.
- **Code-level scope note (not a false theorem).** indep_word.py replays COPY as `vec[r] = vec[src]` and ignores the coefficient. The verifier's COPY is row_r := q·row_s.
  - Harmless on #7623: one COPY, q = 1.
  - It would matter for an extraction on a word with a scaled COPY. Fix: `vec[r] = {a: q*v ...}`.
- hOnce is not just "[C] on #7623": it is a theorem for every verifier-accepted word (l.51). The same holds for helpers' strict ascent (FANOUT F1's "checked: only 24 owned moves do not ascend").
- No other prose statement was found false.
