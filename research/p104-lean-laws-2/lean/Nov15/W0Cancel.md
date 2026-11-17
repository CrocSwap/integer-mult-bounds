# W0Cancel.lean: NEWARCH law W0-CANCEL BELOW V + R3 deferral corollary. No sorry, 9 s, 2.0 GB RSS
Nov 17. Imports RankLaw (-> TokenCancel). Axioms: [propext, Classical.choice, Quot.sound] (core theorems only propext/Quot.sound). Source: NEWARCH SPEC3 s3, SPEC4 s4, SPEC5.

**Model.** TokenCancel's ops (Ev/St/step/LegalEv/Legal: co-presence, no MOVE leaves V). `S : Submodule` = S_V (span of V-ending helper directions and X/X2 finals); `S.mkQ` = off-S_V part (W0 junk: Y/Y2 and below-V-helper coordinates). `NoEntry V`: no MOVE/BORN/INIT lands at V in the segment.

**Results.**
- `vblind` / `vblind_run`: legal run, nothing enters V => the V-residents' rows at the end lie in the span of the V-residents' rows at the start. Ops at any chart != V never write a V-resident (co-presence + nothing leaves V); V ops only combine V-residents. So the V mix cannot create or import junk and cannot see anything else.
- `vblind_mod`: off-S_V part of each final V-resident is a combination of the arrival off-S_V parts.
- `w0_cancel` (the LAW, corrected joint form): if the arrival off-S_V parts of the V-residents are linearly independent and a V-resident ends with off-S_V part 0, its final row is 0. Contrapositive: a nonzero in-S_V final row with independent junk at arrival needs the junk cancelled BEFORE arrival (an op at a chart != V, while the register is still below V, between junk arrival and the last pre-V read).
- `defer_rows_in_S` / `defer_perturbation_in_S` (R3 corollary, HubSettle's invertible `VMixM`): `C * X' = R` with C invertible and all target rows in S => every pre-V row X'_g in S; so the perturbation X' - X of a deferral lies in S_V row by row.
- `defer_nonV_unchanged`: if both programs end in a V-only suffix (`vonly_const`: it fixes loc and every off-V row) and end with equal rows, every off-V register has the same row before the suffix: no non-V final row changes.

**Finding (prose false as written).** "A direction w not in S_V present in a V-ending row must be cancelled by an op at a chart strictly below V" fails per row. `counter_individual` (ℚ, Reg=Fin 3, S_V = span{e1,e2}): r1 = e1+e0, r2 = e2+e0 (built at chart 2), both MOVE to V, then `add 1 2 (-1)` at V gives r1 = e1-e2 in S_V with no below-V op after the junk arrived. The junk is cancelled at V against a V-resident carrying the same junk; r2 keeps it.
- Corrected statement: the junk can only be reduced inside the dependencies among the arrival off-S_V parts of V-residents (`vblind_mod`). It is a joint/rank statement: with independent arrival junk (the SPEC situation: each Y/Y2 W0 direction rides its own V-ender) nothing at V helps (`w0_cancel`). The SPEC3/4/5 "0/1,679 stops legal" numbers already used the joint all-set rank test, so they are unaffected; any per-row reading is not.

**Scope / hypotheses (not proved here).**
- No MOVE out of V and the NoEntry condition are inputs (the [C] fact of T1(b); NoEntry holds for a V-only suffix). Entry to V after the arrival state is handled by applying the theorems at the later entry state.
- R3's invertible V mix (VMixM) is HubSettle's assumption; the operational mix may include CLEAR/SCALE 0, in which case `w0_cancel`'s zero-row conclusion is the statement, not equality of spans.
- That the 1,925/2,614 hh ops move W0 content and the junk is independent at arrival are [C] facts on #7630 (r3a/r3b), not formalized.
