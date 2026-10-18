# Volume I independent mathematical peer review

Disposition: all100 numbered entries A001–A100 reviewed; no unresolved theorem-level error found in the reviewed revision. This is an informal mathematical review, not Lean verification or a claim of global novelty.

Reviewed source: `drafts/01-algebra.md`.

SHA-256: `1c767d0a388432a9bde41ba8140417e87da65ecf1c16df047425631f3c7a6074`.

The inventory is96 proved statements with full proof blocks and4 explicitly unproved conjectures (A010, A030, A060, A100). I read the statements and proofs across all ten sections, including final revisions to A032, A059, A071 and inherited section hypotheses. I checked sufficiency conclusions rather than treating a necessary obstruction as a construction.

## Findings corrected before this disposition

The original A059 chart-transition statement claimed symmetry of T for arbitrary S. Taking the identity symplectic map and nonsymmetric S would refute that statement. The present statement and proof correctly say T is symmetric if and only if S is symmetric, on exactly the domain where a+bS is invertible. Isotropy is preserved in both directions, so the corrected proof works in characteristic two as well. The inverse-chart argument is also valid. This strengthens Volume II's elementary graph parameterization by giving exact transition coordinates and their domain.

A002 and A032 now use left cosets gH and gG_x consistently. A032's final proof explicitly starts with an existing transporter g₀ and proves that every candidate with the same combined character lies in g₀G_x, so its sufficient conclusion does not merely compare two already existing transporters. A078 says component solutions multiply to a global solution, avoiding a possible reading that they multiply to the identity. A071 explicitly requires a group homomorphism commuting with the automorphisms; the kernel argument depends on this hypothesis. Sections VIII and IX declare their group and finite-Galois/semilinear assumptions before the dependent statements.

## Proof checks by section

- A001–A010: transporter cosets, kernel quotient and fibre-transitivity arguments retain actual existence and compatibility hypotheses. The algorithmic proposal A010 is not asserted proved.
- A011–A020: restriction and extension maps, determinant padding, radical-algebra reconstruction and normalized unital isotopy are constructive. A019's normalization by the invertible product ab preserves multiplication in the required order. No unmarked recovery gadget is silently assumed.
- A021–A030: Smith normal form, simultaneous power correction, cyclic character tests and nonmodular averaging use their stated characteristic and finite-generation hypotheses. The lattice algorithm conjecture is separate from the established finite-dimensional constructions.
- A031–A040: contraction images, torus weights, finite-group invariant generation/separation and Reynolds arguments preserve the infinite-field or nonmodular hypotheses where needed. Finite-orbit separation uses an invariant product, so it does not incorrectly divide by group order in modular characteristic.
- A041–A050: quiver endomorphism algebras, Fitting decomposition, local endomorphism rings, Krull–Schmidt and field-of-definition tests are supported by actual linear-algebra constructions. The finite-field determinant-grid criterion is sufficient under its degree bound and is not asserted necessary.
- A051–A060: simultaneous flag bases, common stabilizers and paired inverse-transpose lifts are explicit; corrected A059 has the exact chart-domain condition. A060 explicitly leaves the ordinary unmarked tensor gadget unproved and does not claim an isomorphism reduction from marked data alone.
- A061–A070: cyclic roots, Kummer separability, norm determinants and coprime-degree descent retain separability, coprimality and quadratic characteristic assumptions. A069 reconstructs marked scalar-linearity, with that scope stated.
- A071–A080: nonabelian Lang-correction factors have the proper order; primary projections and finite-abelian character separation yield sufficient corrections under their explicit hypotheses. Existence of a kernel solution is not inferred from obstruction vanishing without the needed surjectivity criterion.
- A081–A090: Dedekind independence supplies the nonzero Hilbert90 construction and trace-one argument. Semilinear basis construction and descent of morphisms, subspaces and algebra identities start from an actual compatible action; they do not invent such an action from coefficients alone.
- A091–A100: Schur complements, determinant/inverse update, rank extensions, Grassmann charts and finite-field evaluation are exact. A096's modular reconstruction uses both a height bound and exact verification of the recovered equation. A099 is explicitly a first-order dual-number deformation statement. A100 is a bounded-dimension rational-height conjecture under effective stabilizer assumptions, not a theorem about arbitrary rational transporters.

## Remaining scope notes

The conjectures have explicit desired outputs and meaningful missing constructions or bounds. Their global open status is not established by this review. Standard algebraic facts used as background are not newly proved atlas discoveries. Source provenance and literature completeness remain matters for the author's ledger; this review does not replace a source audit or formal kernel/transitive-axiom check. No compiler, prover or external model was run for this informal review.
