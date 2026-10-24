# Executed validation and remaining obligations

Local verification on 2026-10-23 used CPython 3.12.15, standard library only.

Passed:

```sh
python3.12 -B scripts/research_package.py --package research/coded-active-feedback --check-only
python3.12 -B scripts/research_package.py --package research/coded-active-feedback
```

The registered replay executed the normal isolated, warning-strict verifier
with `--full-search`, followed by its optimized component/pilot verifier.
Every one of the 8,281 regenerated policy records and exact basis dimensions
matched the decompressed receipt. Both modes passed the component identity,
four-input contamination formula, binomial/recurrence coupling-rank checks,
196 directly verified pilot certificates, normal-form fixtures, source hashes,
and positive/corruption controls. No package source or receipt changed.

The initial full search and the registered replay are separate completed runs;
the optimized replay does not repeat the full 8,281-case synthesis. Gzip
payloads are compared as parsed JSON, including all proof-relevant fields.

Canonical main was refreshed before submission and remained
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`. Priority revision 7 and the
selected conditional kappa 0.00302015 were unchanged. The submission overlap
refresh completed at 12:49:20 UTC: 334 open PRs, 4,438 Discussion records,
and complete coverage of the 6,996 tracked local notes, plus this untracked
package's two indexed notes. Coverage is titles/bodies and indexed notes,
not arbitrary diffs or unpublished work. Related PR5200 is scoped in README.

This validates the stated component and bounded formal experiment. It does
not independently validate the source native ABI, physical phase conventions,
all-width helper contracts, a complete changed caller, scalar tape tariff,
rounding, compiler, BIT, outer transfer or a multiplication theorem. There is
no autonomous new job or new kappa. Human and proof-kernel review are absent.

Committed-byte/source-history preflight and portable-export replay are
reported separately in the PR after the commit exists. Hosted status is
likewise reported there only after observing the exact published head.
