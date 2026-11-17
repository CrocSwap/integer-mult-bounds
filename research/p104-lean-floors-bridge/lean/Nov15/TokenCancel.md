# TokenCancel.lean: BIG-TOKENCANCEL T1 (hub blindness) + T2 (difference lemma). No sorry, ~6 s, 1.7 GB RSS
Lane LEAN-NEXT6, Nov 16. Source: cards/WILD/BIG/TOKENCANCEL/THEORY.md. Axioms (3 printed): [propext, Quot.sound].

**Model.**
- Registers Reg, charts C, hubs z (= {0}) and V. Rows are in initial-row coordinates.
- Events: born (row e_i), init (row 0), move, add i += a·j (i ≠ j), scale, clear, copy. Each event carries its chart.
- Legal = births/INITs of absent registers and co-presence at the event's chart, plus the two [C] facts of T1(a)/(b): no MOVE enters z, and no MOVE leaves V (0 of 6,257 on #7623).
- `hubOp` = an add/scale/clear/copy at z or V.

**T1.**
- `sigRun` is the interior coefficient program: it tracks the e_h-coefficient and ignores hub ops. `sigRun_filter` shows it depends only on the non-hub-op subsequence.
- `T1_hub_blind`: in a legal run where h is not born at z (h off-hub born), every register not at V at the end has row[h] = sigRun on the interior subsequence.
- `T1_two_runs`: two legal runs with the same interior subsequence agree on the e_h-coefficient of every register that is off V at the end of both.
- Proof invariant: rows not at V carry the program's value; rows at z carry 0.
- The hypothesis z ≠ V is NOT needed. T1' (the joint-hub D-mix corollary) is plain invertibility and is not formalized.

**T2.**
- y's row changes only through `addK a r` (contact y += a·row_k, with r_k = 1), `addO w` (w_k = 0) and `scale u` of y.
- `T2_difference`: if y₀_k = 0 and y's final e_k-coefficient is 0, then
  - the effective coefficient sum is 0;
  - the net receipt from k lies in span{r_i − r1} for ANY reference row r1, in particular row_k at the first contact. So content k carried into the first contact never reaches y net.
- `T2_coeff`: final e_k-coefficient = A.

**Finding (scope, T2).** The literal "Σ a_i = 0" is FALSE if y is SCALEd between contacts. Example: y += k, y *= 2, y += (−2)·k gives Σ a = −1, yet y_k = 0.
- Minimal fix: use effective coefficients a_i·Π(later scales of y), or require that y is not SCALEd between contacts.
- The conclusion (receipt ∈ span of post-first-contact differences) survives SCALE.
- CLEAR/COPY of y and relays through third registers remain outside scope, as the prose says.

**T2 corrected (LEAN-NEXT7, Nov 16).** Same file, axioms [propext, Quot.sound] (the counterexample also uses Classical.choice).
- `contacts ops` lists (a_i · Π(later scales of y), row_k(t_i)) for each contact.
- `yRun_closed` gives the closed forms of the coefficient and receipt trackers.
- `T2_corrected`: under T2's hypotheses,
  - Σ effective coefficients = 0;
  - the net receipt = Σ eff_i · row_k(t_i) = Σ eff_i · (row_k(t_i) − r1) for ANY r1 (take r1 = row_k(t_1)).
- `contacts_noscale`: without SCALEs of y, eff_i = a_i, so the literal prose "Σ a_i = 0" holds.
- `T2_literal_false`: the finding, formal over ℚ. y += k, y *= 2, y += (−2)k gives final y_k = 0 and Σ a = −1, while effective Σ = 0.
