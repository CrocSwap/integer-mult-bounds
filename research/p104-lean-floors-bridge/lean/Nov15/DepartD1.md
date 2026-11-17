# DepartD1.lean: BITE-DEPART Lemma D1 (a_S ≤ d + e_S + oa), extending ExportLaw T4*. No sorry, ~6 s, 2.0 GB RSS
Lane LEAN-NEXT16, Nov 16. Source: cards/WILD/BIG/BITE-DEPART/RESULT.md §3 and t4rho.py (d = public ARRIVALS that depart; e_S = ARRIVED enders with an S coordinate; oa = owned arrivals + INITs). Imports the ExportLaw olean. Axioms: [propext, Classical.choice, Quot.sound].

**Results.**
- `D1_all` (class N only): a_S ≤ (ALL public departures) + #(public enders with π_S(final) ≠ 0) + oa. Proof: ExportLaw.T4_star with Xs = everything.
- `D1` (card form): a_S ≤ d + e_S + oa, under
  - class N (a public ender with π_S(final) = 0 ends as its token; a public register born at c that ends there ends as its token);
  - hOnce ([C] on #7623, ExportLaw.md);
  - **hArr**: public arrival rows carry no coordinate of a register born at c.

  Proof: ExportLaw.T4_card with π' = π_S ∘ (kill the c-born coordinates). π' agrees with π_S on the arrival rows (hArr), kills every c-born token, and so leaves xb = 0.

**FOUND FALSE AS STATED (general form).** "Any class-N word with SPEC finals, any chart c ≠ V" is false without hArr. `D1_false` is a run over ℚ:
- x (an S register) is born at c;
- helper h arrives with row e_h + e_x, the x-coordinate brought below c by an owned descent elsewhere;
- h −= x, then x departs.

Then a_S = 1, but d = e_S = oa = 0. Every other hypothesis of `D1` holds.
- Where the card's proof breaks: "rows at c lie in Arr_c + O_c + span(c-born tokens)" is true, but bounding a_S also needs the c-born part of the arrivals to be counted. That part is counted only if it is a departure (`D1_all`), or excluded (hArr).
- **Minimal fix:** add hArr. It holds automatically when no owned register carries a c-born token below c; public registers only ascend, so only an owned descent can do it. Alternatively, count born-at-c departers in d (`D1_all`).
- **Not binding on #7623:** t4rho.py's exact check found 0 violations on 976 charts. Whether hArr holds on #7623 itself was not checked (the 24 owned descents could in principle carry c-born tokens).
