import All
/-! Axiom audit of every headline theorem (run by `check.sh`).
Expected for each: `[propext, Classical.choice, Quot.sound]` or a subset; never `sorryAx` / `Lean.ofReduceBool`. -/
-- (K) generic core: any invoice F cs t = Σ c·r^(1-t); kernel-checked piece chains ⇒ lo ≤ kroot cs ≤ hi, F(kroot) = 0, unique root
#print axioms CertKit.kroot_bracket
#print axioms CertKit.loOK_sound
#print axioms CertKit.upOK_sound
#print axioms CertKit.logsOK_sound
-- (T) word t7669 (#7669's word replayed, #7113 caller): legal trace, correct rows, κ bracket to 10 digits
#print axioms CertT7669.certified
#print axioms CertT7669.bracket
#print axioms CertT7669.FW_eq
#print axioms CertT7669.kword_bracket
#print axioms CertT7669.kword_root
#print axioms CertT7669.valid_below
#print axioms CertT7669.invalid_above
#print axioms CertT7669.crossing_lo_closed
#print axioms UniRows.A.rows7669
#print axioms UniInhabit.paid7_hist
#print axioms UniInhabit.cred7_hist
-- (W) word w_s4 (128-bit chain made by gen_chain.py): same headline
#print axioms CertWs4.certified
#print axioms CertWs4.bracket
#print axioms CertWs4.FW_eq
#print axioms CertWs4.kword_bracket
#print axioms CertWs4.kword_root
#print axioms CertWs4.valid_below
#print axioms CertWs4.invalid_above
#print axioms UniRowsWs4.A.rowsWs4
#print axioms UniInhabitWs4.paid7_hist
#print axioms UniInhabitWs4.cred7_hist
-- (C) the caller block derived in the kernel from the #7113 caller file (callerfacts.py)
#print axioms CertCaller.cdat_hist
#print axioms CertCaller7113.tHist
#print axioms CertCaller7113.pHist
#print axioms CertCaller7113.calls_known
#print axioms CertCaller7113.dc_eq
#print axioms CertCaller7113.Tcal_eq
#print axioms CertCaller7113.Pcal_eq
#print axioms CertCaller7113Link.kwordT_bracket
#print axioms CertCaller7113Link.kwordW_bracket
