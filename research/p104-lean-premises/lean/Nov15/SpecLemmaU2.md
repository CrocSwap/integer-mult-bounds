# Nov15/SpecLemmaU2.lean 
Extends SpecLemmaU.lean (import Nov15.SpecLemmaU). Kernel-only: no sorry, no native_decide; 10 `#print axioms` all [propext, Classical.choice, Quot.sound]; ~23 s / 2.1 GB. Paper statements are TRUE as written (no counterexample).

Model (explicit coordinates `Ix E = Fin 4 ⊕ (Fin 2 ⊕ E)`: C4 = inl, e5 = I5, e6 = I6, E' = E): D = Dm (-1 on C4 and e5, +1 on e6, E'); P = 1 - X T Y^T, X = (e5,e6,u), Y = (e5,e6,η), u, η vanish on e5, e6 (RB6 normalisation); hypothesis det P = -1 (full matrix; the three-reflection fact stays a hypothesis); Λ = P⁻¹ D; char ≠ 2.

## Discharge of hrk / hE (as the inequalities actually needed)
- `kb` (generic): injection ker f → ker S × B bounds `dim ker f + rank S ≤ #cols + dim B`.
- `key3` (η_E = 0), `key4` (η_E ≠ 0): `3 + rank S ≤ rank(Λ-1)` from the kernel equations (`fix_eqs`: w_C = (σ3/2) u_C, σ1 = 2 w5, σ2 = 0, σ3 u_E = 0, via `rows_eq`), with S = `S3`/`S4` = Msys (4x3 or 4x4: extra row (0,0,δ[,0]) iff u_E ≠ 0, extra column T e3 iff η_E ≠ 0). This replaces `hrk` (equality) by `≥`, which is all the argument uses; u_C ≠ 0 is not needed.
- `Em1_bound`: `rank(T - diag(0,2,0)) ≤ 2` (η_C ≠ 0) ⇒ `dim ker(Λ+1) ≥ 4` via the explicit injection (t, c) ↦ w with C4 = t_3 c0 + c (η_C·c0 = 1, η_C·c = 0), e5 = t_0, e6 = t_1, E' = 0. Replaces `hE`.
## The E-part cases (rank S ≤ 1 ⇒ rank(T - Dp) ≤ 2)
`case1` (neither; via SpecLemmaU.core_neither_rank), `case2` (u_E only: T = [2e1 | 0 | *], det ⇒ k·t33 = 0), `case3` (η_E only: a_i·(κc3 - c2) = 2δ_i3 ⇒ T e3 = 0 after det), `case4` (both: T e3 = 0; no k needed, T = diag(2,0,0)). Matches the audit's G-dependence argument (S depends on u_E, η_E only through the flags and κ_C).
## Composition
`spec0_core_U4`: 4 ≤ rank(Λ-1) (all k, all E-cases), and rank = 4 ⇒ Λ² = 1 for k = η·u ≠ 0; the k = 0 involution step is the named hypothesis `hk0` (parallel Singular run). Case η_C = 0 goes through `lemmaU_mat_T`. (u_C = 0 needs no separate branch.)
## Still named hypotheses
det P = -1, the RB5 structure (u, η normalisation, D shape), INV, k = 0 involution (`hk0`), the Singular k = 0 radical checks and the 720-order reduction. Not formalised: Sylvester ⇒ p0+q0 ≤ 2 is in SpecLemmaU; its link to this model (V = e56 ⊕ <u>) is by hypothesis.
