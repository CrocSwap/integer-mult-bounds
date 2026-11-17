# FloorGlue.lean: Floor's `hent` derived from ExportLaw + hOnce; chart floors summed into the global floor. No sorry, ~5 s
Lane LEAN-NEXT7, Nov 16. Imports the oleans of ExportLaw.lean and Floor.lean (build commands in the file header). Axioms: [propext, Classical.choice, Quot.sound].

- `entry_count`: Floor's `hent` is DERIVED here, no longer assumed.
  - Setting: one chart, a legal ExportLaw run from the empty state. Registers are partitioned into helpers H, kept Kp and owned Ow. hOnce holds for Kp only.
  - Result: dim S_c ≤ hd + he + ka + oa + hb + kb, and hb ≤ helper departures.
  - The terms:
    - hb = helpers born at c and gone at the end;
    - he = helper enders;
    - hd = helper departures − hb (paid stays);
    - ka = kept registers that arrive (not born at c);
    - kb = kept births;
    - oa = owned entries (owned registers are unrestricted).
  - Route: ExportLaw.forward_count (φ = id) for dim S_c ≤ #entries. Then the entries split by class (`nEnt_eq_sum`), and stay_count for the helpers.
- `chart_floor`: Floor.stay_floor on an ExportLaw run, with Tok = helper enders ∪ (helpers born at c and gone).
  - Result: rank ρ(X) ≤ hd + ka + oa + kb for any rows X held at c.
  - Remaining hypotheses: class N (a helper at c at the end is its own token) and ρ killing helper tokens.
- `sum_chart_floors`: per-chart floors L(c) ≤ hd(c) give Σ_c L(c) ≤ #stays.
  - Distinct stays: each paid stay has one chart `at_`, so hd(c) = #stays at c.
- `global_floor_direct`: cost ≥ κ·Σ_c L(c), given cost ≥ κ for each stay.
- `global_floor_of_certificate`: cost ≥ κ·bᵀy (Floor.floor_of_certificate with HD = #stays).

**Left as checked input:**
- the LP data, i.e. the rows A x ≥ b satisfied by the native's x, with objective ≤ #paid stays (the native-feasibility map is still prose);
- the dual vector y (lp2.py / rslp.py);
- per-stop cost ≥ κ (JunkLB2.T4_stop_cost);
- identifying ExportLaw's per-chart hd (helper departures − hb) with the global stay list's fibre at c.
