Audit a proposed weakening of PR543's retained scalar interface: replacing
the H1/H3 ban on target feedback with raw endpoint independence does not
justify literal projected cleanup. The shortest three-wire counterexample
is `h += y; y += x; h += y`; its two prescribed cleanup ADDs cancel,
leaving the helper as `h+x`. This is not a flaw in the stated source lemma.

The package proves an exact four-block replacement criterion and checks
the complete finite quotient of arbitrary-length three-wire words:
4,032 states and 24,192 transitions. Of 144 endpoint-admissible states,
138 fail restoration. The two cleanup equations have independent near-miss
witnesses. A separate enumeration of all 43 shorter literal programs
confirms the raw three-ADD minimum; truth tables check every quotient
representative. Unchanged PR589, selected at the pinned experiment base,
passes the full scalar criterion
on all 661 arbitrary input columns.

```text
python research/feedback-cleanup-audit-seed72/verify.py
```

Expected: `PASS_FEEDBACK_CLEANUP_AUDIT_S72 states=4032 naive=144 bad=138 minimum=3 selected_columns=661 controls=8`.

Both H1 and H3 repeat the exclusion being relaxed. Only H4's scalar
reverse rule is retained here; frame legality is not generalized.
No physical circuit, native/precision/hosting admission, supplier or new
kappa is claimed. Exact source pins, proof, certificate and validation
are included. Prepared for @woklerx with substantial OpenAI Codex
assistance, Apache-2.0; predecessor credit is retained in NOTICE.md.
The base-scoped PR942 selection is distinguished from the newer live
PR1042 frontier in README; this note does not audit that new assembly.
