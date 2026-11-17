# ContentPin.lean: CONTENT-PIN (CONTENT2OPT R1). No sorry, 4 s / 1.6 GB, 10 `#print axioms` within [propext, Classical.choice, Quot.sound]
Nov 17. Imports TokenCancel (Ev/step/run model). PrefixPin/W0Cancel are not imported: W0-CANCEL only explains why the junk part of the row is pinned; the law below needs neither.

**Law, as proved.** Reader `r += c·h1` (state s before it) replaced by `r += c·h2`, rest of the run (`tail`) unchanged.
- `sub_delta` (exact): final row q changes by `coef tail r q · c · (row h2 − row h1)`. `coef` is the downstream difference tracker (`drun`), independent of the rows. `diff_run` is the general propagation lemma (no legality needed; BORN/INIT/CLEAR kill the difference).
- `content_pin` (iff, modulo any linear map π = what the finals see): finals in F unchanged under π iff for all q in F, `(coef_q·c)·π(row h2 − row h1) = 0`. So the condition is row(h2)=row(h1) modulo ker π, on exactly those finals the reader reaches (coef_q·c ≠ 0).
- `content_pin_row` (π = id, reach hypothesis): unchanged iff `row h2 = row h1`. `content_pin_changes`: reach + δ ∉ ker π gives a changed final.
- `token_coord`: with row h1 h1 = 1 and row h2 h1 = 0, the change at coordinate h1 is exactly −coef·c.
- `no_reassign` (corollary): fresh-token helpers (h1 holds its token, h2 has not read it) + reader reaches a final non-trivially => the swap changes that final, in the token coordinate. `fresh_born`: freshly born helpers satisfy the token hypotheses.

**Paper statement, scope (corrections).** The prose is true only with two extra hypotheses, both now explicit:
1. REACH: some final in F has coef·c ≠ 0. Without it the swap is harmless (`dead_reader_preserves`: reader cleared right after, rows differ, finals equal).
2. "Distinct tokens => rows differ" needs row h2 at coordinate h1 = 0 (h2 never read h1's token). A COPY h2 := h1 gives distinct birth tokens but equal rows (`copy_equalises`), so the swap is then harmless. In TC models this is the "token appears only in rows that read it" clause.
Also "modulo the kernel of the downstream map": the correct kernel is that of the finals' observation map π on the row difference; the token coordinate must lie outside ker π (identity observation: always).
Single-op only; multi-op bundles and legality/chart constraints are not modelled (substitution legality is a separate, co-presence condition).
