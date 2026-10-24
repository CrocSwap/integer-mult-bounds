# Acceptance addendum: same-chart cache-content control

The new independent control **closes the cache-content mutation coverage gap identified in `REVIEW.md`**. The original source-frame rejection remains accurate for the original control; it is now supplemented by a legally charted content mutation that reaches and fails the zero-row algebra predicate. The scoped acceptance decision is unchanged.

I read `agents/algebra/check_same_chart_cache_mutant.py`, its `SAME-CHART-CACHE-MUTANT.json`, and the root-owned `provider5402-same-chart-cache-control` receipt/stdout. No scientific execution was performed in this acceptance lane. The original acceptance review, binding receipt and scientific checker files were left unchanged.

The script selects the actual first COPY into C1 at event 11207, checks its preceding owned CLEAR at the same chart, and inserts precisely one event:

```
['scalar', ['scale', ['C', 1], -1, 1], 254]
```

This is a permitted signed-power-of-two SCALE on the retained cache's current chart. It preserves the existing source and destination identities, owned CLEAR/COPY rules, persistent-owner protections and chronology. It changes the copied content rather than choosing another-chart source. Prefix/suffix comparisons require every other event to remain identical.

The control deliberately bypasses the source zipper, which would reject the extra instruction before any row-content check. It calls the same frozen independent native interpreter directly. Success requires exactly the exception `zero retag requires complete exact zero row`; a chart/ownership rejection or a different exception does not satisfy the control. The observed result has precisely that exception. Thus a wrong same-chart cache value makes a later asserted zero retag nonzero and is rejected by algebra rather than by frame metadata.

The root guard reports exit zero, no termination, 0.705130 seconds elapsed and sampled peak descendant RSS 48,652,288 bytes. The semantic result records 0.575157 seconds internal execution and status `PASS_SAME_CHART_CACHE_CONTENT_MUTANT_REJECTED`.

Static SHA256 checks confirm:

| Artifact | SHA256 |
| --- | --- |
| Additional checker | `4bf90d4656e03e6716448026ba120c172585c9aced067d35d6ca1a75250d9aad` |
| Semantic result | `c8224338d3143f36ba5668908064971f11e2e684a80d9097b1bbd922cf152b15` |
| Root stdout, matching receipt log hash | `afc4e5719c0e7cf1b2c8c1770d6d5f5f3c8b9411df6b7644419cc138b9be9261` |
| Root guard receipt | `15ff49f21e110782ea6dcbbe2196e22790241f42c3eb823a5a7211a2b2ed2a4e` |

The recorded SHA256 values of `check_provider.py`, `provider_rows.py`, `phase_exact.py` and `prior_dyadic_engine.py` match the current files and the original independent run's frozen values. The result also retains the same previously authenticated source/candidate raw hashes. This addendum adds one narrow successful semantic control; it does not rerun or broaden the full provider's admitted physical implementation, consumer closure, target credit, precision or kappa boundary.
