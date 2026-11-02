# Reviewed conditional phase-cell fusion

With the explicit additional supplied matrix-exponent premise `omega_C<=9/4`, the reviewed local corollary gives **`kappa=0.001673360105405778`**, a gain of `6.9990832886e-7` over the selected conditional exponent. Its status is `PASS_CONDITIONAL_MATRIX_PHASE_FUSION_REVIEW`.

The separate Strassen-based transfer gives `kappa=0.001672922349588871` with status `PASS_CONDITIONAL_PHASE_FUSION_REVIEW`, without that additional matrix premise. Both retain the original supplier and all-size computational assumptions. The upstream selected certificate is unchanged.

- `phase_fusion_note.tex` is the standalone proof note.
- `CAPPED-INTERIORS.md` records the local gauge and boundary-count change.
- `check_capped_outer.py` recomputes 44 positive rational slacks and five rejecting controls; `CAPPED-OUTER-ARITHMETIC.json` records the reviewed local status.
- `MATRIX-COROLLARY.md` and `check_matrix_corollary.py` give the additional corollary; `MATRIX-COROLLARY-ARITHMETIC.json` contains 47 positive slacks and six rejecting controls. `MATRIX-COROLLARY-REVIEW.json` records its separate review and source hashes.
- `OUTER-AUDIT.md`, `check_outer.py`, and `OUTER-ARITHMETIC.json` preserve the weaker uncapped arithmetic as history.

Run `python3 -B work/phase_assembly_ultra/check_capped_outer.py` and `python3 -B work/phase_assembly_ultra/check_matrix_corollary.py` from the workspace root.

The old `Vd` row and the unrecentered full-cell gauge both reject this result. The improvement uses the reviewed Gaussian circuits, support-limited compact supplier, anchored capped gauges, and grouped sparse/halo scans. Tightening the old arithmetic alone cannot produce it.
