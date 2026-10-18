Audit the unchanged selected PR589 word across the complete finite
nine-stage scalar schedule. The source's conservative product is safe
at 177 bits. A proved recurrence preserving separate data-bank bounds
and fresh stage helpers gives a 132-bit bound; a full positive-program
replay reaches exactly 127 bits. All 220,905 scalar events and 4,839
independent input columns are covered.

```text
python research/nine-stage-prefix-audit-seed70/verify.py
```

Expected: `PASS_NINE_STAGE_PREFIX_AUDIT_S70 exact_bits=127 envelope_bits=132 coarse_bits=177 controls=23`.

The checker compares its expansion with the pinned exporter, checks the
actual source schedule and prefix formula, bounds every intermediate
scalar value, restores all Boolean columns, and rejects each of eighteen
bridge omissions plus five precision/source controls. The proof explains
why three nonnegative local coefficients suffice for arbitrary inputs.

This is finite precision evidence, not a source bug or 128-bit physical
admission. The 192-bit production charge, selected supplier and kappa
remain unchanged. Native, cover/hosting, compiler and outer error
obligations are not readmitted. It differs from PR1067's signed local
inverse-D bound on PR967: this uses PR589's entire global schedule with
positive coefficients throughout.

Prepared for @woklerx with substantial OpenAI Codex assistance,
Apache-2.0. Full predecessor credit is in NOTICE.md, including the
PR386/436/443/463/510/555/589 lineage and Dylan Crow's source exporter.
