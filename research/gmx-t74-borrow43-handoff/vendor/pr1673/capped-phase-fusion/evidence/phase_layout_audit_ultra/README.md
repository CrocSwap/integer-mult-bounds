# Independent grouped phase-layout audit

Result: **positive conditional layout audit** for the sparse-union stages in
`work/radical_reduction_ultra/REFINED-PHASE-FUSION.md`.

Read `AUDIT.md` for the complete movement argument. Its central step is
that U is a union of coordinate strips, while each individual axis support
`U_i=E_i x [L]^(g-1)` is a complete rectangle. Extract U_i, apply a single
small-field transpose, run the actual sparse axis factor, and merge it back.
This gives the claimed per-group `O(Vg²W polylog(p)/d)` cost without a
computed-key sort and without inventing missing zero entries.

The audit also supplies one-group monotone q_j embedding/extraction and
checks square target-grid augmentation. All full scans occur per group or
per constant sparse window, not per axis. Non-dyadic microhalos remain on
the separate sparse correction path. Their layout uses the earlier
`work/halo_layout_ultra/` construction.

Required qualifications:

- Use the maximum physical bandwidth W for both narrow and broad operators
  when carving and defining J/E; narrow w alone is insufficient.
- Scatter before each dense A/A^-1 stage. Only the sparse factors preserve
  U. Two sparse windows suffice in the six-stage grouped order.
- Generate actual factor pages once per complete microbox, or retain a
  proved sequential page schedule. Scrambled coarse coordinates do not
  grant random catalogue access.
- The dense tensor compiler, actual Gaussian coefficient identity, and
  completed precision/error proof remain separate dependencies.

Reproduce exact controls:

```
python3 -B work/phase_layout_audit_ultra/check_union.py
python3 -B work/phase_layout_audit_ultra/check_q_embedding.py
```

The first verifies all entries of two 12-by-12 rational factorizations,
their two-axis tensor application, full extracted E_i rectangles and a
negative control where dense A^-1 escapes the union. The second verifies
monotone product embeddings, exact half-tie image membership, original
source order, square augmentation and every inverse entry including holes.
`PARAMETERS.json` gives the current layout exponents. `MANIFEST.json`
binds the files. No frozen source or selected result was changed, and no
larger multiplication exponent is asserted by this audit alone.

The independent capped-interior extension is signed off in
`CAPPED-SIGNOFF.md`; run `check_capped_layout.py` for its 1,831 finite
partitions, Schur fill-support checks and exact capped layout inequalities.
It replaces W/d by W/B without changing the union-rectangle construction.
