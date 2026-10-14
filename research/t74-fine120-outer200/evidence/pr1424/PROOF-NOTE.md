# Exact outer witness refinement on the unchanged T74 construction

This note changes only rational witnesses to the inherited conditional bootstrap and outer assembly. It does not change any local word, frame path, owner, paid child, moment endpoint, native recurrence, or bit surcharge.

Let b be the retained native complex lower endpoint, c the retained bit lower endpoint, and a_0 = 384599/10^10 the inherited starting saving. Take eta = beta = 10^-40, and s = min(c,(1-beta)b) - 10^-43. The package verifies 0 < a_0 < s < c and s < (1-beta)b.

Apply the same inherited bootstrap recurrence a_(j+1) = (1-s)s + s a_j twelve times. Induction gives

    a_j = s - (s-a_0) s^j.

Because 0 < s < 1, the sequence is strictly increasing and remains below s. Each application retains the original admissibility tests: a_j < s < 1-a_j; the minimum of the four inherited gaps is positive; and its recomputed integer cutoff N obeys N gap^2 >= 36 and N gap >= 2(4+PAYLOAD). No limit or infinite number of bootstrap operations is used. The assertion that these finite steps transfer to integer multiplication retains the original bootstrap, compiler, realization, precision, exact recovery and analytic assumptions.

For a = a_12, form q = a(1-2 eta) and m = (1-eta)q/(1+q). Choose the largest integer-grid rational k with denominator 10^36 strictly below m. The unchanged outer engine checks all 47 strict inequalities and confirms that the minimum of its seven work margins is m. The next grid point fails for these fixed witnesses; this is not an optimality claim over other witnesses.

The proposed value is 0.001676855229071321886206381217337893. Its difference from PR1377's 0.001676855229071321886144 is exactly 0.000000000000000000000062381217337893. This is a certificate-only improvement of approximately 3.72e-18 percent. It makes no construction or practical-speed claim.

`check_outer_closed.py` separately checks the closed form against every saved bootstrap row, the integer cutoffs, all seven final work margins, the strict grid bracket and five deliberately broken witnesses. The retained outer engine supplies the full 47-constraint replay. The portable admission pipeline additionally checks unchanged supplier identity, owner reconstruction, parent lift, emitted chronology, finite invoice and inherited rejection controls. Native providers are explicitly reused only with their retained source and stage bindings; no fresh native replay is claimed when reuse flags are provided.

Attribution: PR1319 and PR1297 (Rohan Arun), PR1377 (Jeremy Kothe), PR1019, the PR547/548/559 engines and recurrence, PR589 bit supplier, and the full ancestry retained in README and NOTICE. New witness selection and closed-form audit prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0. This is not an unconditional theorem, Lean certification, independent human review or global optimum.
