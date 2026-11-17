# Gauge.lean: REBUILD-ALT r3 coefficient gauge. No sorry, ~8 s
Lane LEAN-NEXT11, Nov 16. Source: ROUNDLOG "ALT: r3 (1)", alt/r3/gen5.py (Gauge, apply_gauge). Axioms [propext, Classical.choice, Quot.sound].

**Gauge covariance (`run_gauge`, `row_preserved`).**
- Time-indexed unit gauge g t r. ADD i+=a·j becomes a·g(i)/g(j); SCALE u of i becomes u·g'(i)/g(i). Events, partners, charts and MOVEs are unchanged.
- `Adm`: the gauge of r may change only at a SCALE, INIT or CLEAR of r. A born register gets gauge 1. COPY i j sets g'(i) = g(j).
- Then run(gauged start, gauged list) = gauged run.
- Every register whose final gauge is 1 (every non-V-ender, and every register in a non-free segment) ends on its old row, with identical locations.
- A V-ender ends on (unit)·(old row).

**Hub re-absorption (`valid_gauge`, uses HubSettle.Valid).**
- Valid(Xn, X0, Rn, R0, Rn0, Fn0, M) ⇒ Valid(Dv·Xn, Dv·X0·D0⁻¹, Rn, R0, Rn0·D0⁻¹, Fn0, D0·M), with the V mix C·Dv⁻¹.
  - D0 = start gauge on the {0}-born rows; Dv = end gauge on the V-enders.
  - In words: prefix row × c, V mix × 1/c, as gen5's docstring says.
- `valid_gauge_A`: if the gauges are units of A (e.g. Z[1/30]), A-integral M and C stay A-integral (InGL). gen5 only uses forest edges with A-unit coefficients (`unit(Q(v))`), so this applies.

**Forest (`lam`, `lam_norm`, `lam_fixed`, `lam_mem`).**
- Parent map with a decreasing depth on free segments, and a unit edge coefficient with orientation (true: a·λ(s)/λ(par s), i.e. ADD target or SCALE after-segment).
- λ = 1 off free segments, and every forest edge becomes exactly 1.
- λ lies in any subgroup containing the edge coefficients.
- `seg_adm` + `forest_gauge`: segment bookkeeping (`SegAdm`) gives an admissible gauge. The composed run fixes every register whose final segment is not free.

**Scope / model notes (nothing found false).**
- Model COPY is coefficient-free, so a COPY ties i's new segment to j's (gen5 rescales COPY coefficients instead and never uses them as forest edges). Over the model this is the `SegAdm` copy clause.
- INIT/CLEAR also free the gauge (rows are 0), which is slightly more freedom than the prose's "split at SCALEs".
- "1,443 coefficients set to 1 for 1,443 free segments" requires every forest component to be anchored at a non-free segment or at 'G'. gen5's union-find roots at 'G', and `lam` covers exactly that case. A component with no anchor would leave one free unit, which is still harmless (`lam_mem`).
