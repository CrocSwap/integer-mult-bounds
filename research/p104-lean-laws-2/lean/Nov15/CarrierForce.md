# CarrierForce.lean: NEWNATIVE R2 sec B forcedness (carrier + plane stop) and line-stop pinning
Nov 17. Imports Nov15.FrameSep + Mathlib linear algebra (RelaySandwich not needed: it is lattice-only and the argument here is about frames). Kernel-only, 4 s / 1.8 GB, no sorry/native_decide; 9 `#print axioms` all [propext, Classical.choice, Quot.sound].

**Model.** Charts = submodules; port lines `ln u_i`, plane `P = ln u1 ⊔ ln u2` (finrank 2 from independence). Cluster = a family 𝓡 of `FrameSep.Route`s, all public (explicit "no owned register touches the cluster's charts"; per cluster, not global). `HeldAlone 𝓡 u`: a frame holding u is the frame of a carrier of 𝓡 that ascended from `ln u` (R1: c is the only chart where x_a, x2_a sit alone).

**Theorems.**
- `no_two_lines`: a public route never passes both `ln u1` and `ln u2` (a ladder passes exactly one line).
- `chart_eq_plane`: a chart of rank <= 2 holding both ports is P. `finrank_plane`, `line_lt_plane`, `three_stops_distinct` (ℓ1, ℓ2, P pairwise distinct).
- `two_port_exit` (R2 sec B): a register of 𝓡 leaving a rank<=2 chart with both ports (membership) => (i) its chart is P (a stop at P), (ii) two distinct carriers Q1 != Q2 in 𝓡, Q_i ascending ℓ_i -> P. So 2 line stops + 1 plane stop per two-port exit is minimal.
- `line_pin`: a helper co-present with a fixed main event at `ln u1` stops at `ln u1` and never at `ln u2`.

**Scope (stated at once; the paper statement is true as written but needs two explicit hypotheses).**
- `owned_passes_two_lines` (ℚ²): with an owned step one route passes both lines; "no owned register" is essential, so R2's containment check is per cluster (owned MOVEs reach dim 1 elsewhere).
- `no_plane_if_rank3` (ℚ³): carriers ℓ1 -> ⊤, ℓ2 -> ⊤ give a two-port exit at the rank-3 chart with NO frame equal to P. So (i) holds only for exits that LEAVE a rank<=2 chart (R2's "plane stops leave with both ports in the exit row"); a dim-3 exit with no lower stop is not covered, i.e. forcedness of the plane stop is relative to the fixed pre-arrival chart being dim 2.
- Not modelled: mixing by ADD between co-present registers (content = frame membership only); HeldAlone is taken as the hypothesis form of R1's "held alone only at c", not derived; counts of carriers beyond >= 1 per line.
