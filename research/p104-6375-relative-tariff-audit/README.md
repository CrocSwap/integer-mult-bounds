# Exact PR6375 relative power-tariff audit

This package independently extracts the complete frozen PR6375 and retained
PR6372 recursive invoices, then proves a unique interior crossover for their
relative power-tariff gain on `0<s<1`. The strict rational threshold enclosure
`11712509413/13421772800 < sigma < 5856254707/6710886400`
has width `1/13421772800 < 10^-10` and is certified by two different arithmetic
methods. Numerically, sigma is near 0.8726499538.

Candidate source: `247b5c319b9f58fe9ee61dbf80697f8a9a429831`.
Retained baseline: `b556600ffe14be72406b03a47c661f3c7f1aff06`.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
All sources and the fourteen scientific files of checkpoint
`3f366fd299f8761836f7e3171334f9cbd95f0c2e` are preserved byte for byte.

## Exact scope and evidence

The frozen [PROFILE-PROOF.md](PROFILE-PROOF.md), [PROFILES.json](PROFILES.json)
and [ORACLE-PROFILES.json](ORACLE-PROFILES.json) derive both literal local and
complete caller profiles, all six changed input target debits and three paid
shared carrier trips. Paid calls rise 70,656→70,713, productive fields stay 14,214,
and both linear rank-mass surpluses remain 808. Every fixed query and idle is
retained. Two separately written engines import no author or peer code.

For `H_r=r^s`, the exact complete margin difference is

`19[-6+3*3^s-3*4^s+3*5^s+6*8^s-6*9^s]`.

The new [PROOF.md](PROOF.md) gives a whole-domain sign/root argument using a
proper Taylor remainder kernel. The candidate formal margin is smaller below
the unique interior threshold and larger above it until the linear endpoint,
where the difference is zero. This is different from either absolute invoice's
raw kappa root; author coverage of that root retains credit.

The new primary arithmetic engine uses rational log/exp enclosures. Its separate
oracle uses generalized binomial enclosures. They bind and verify the same
strict rational bracket from the preserved complete profile receipts. See
[VALIDATION.md](VALIDATION.md) for commands, environments,
controls, exports and remaining obligations; pending checks are not successes.

## Reproduce

```sh
python3.12 -W error -B scripts/research_package.py --package research/p104-6375-relative-tariff-audit
```

Eight registered normal/optimized commands recompute strict typed receipts.
Standalone scripts also run in a Git-free read-only package copy. No dependency
installation, author native replay or historical heavy suite is required.

## Limits

The tariff and productive-boundary interpretations are declared native/physical
premises. This is an exact formal invoice comparison, not proof of physical
realization, native phases/all columns, scalar endpoints, owned erasure, actual
caller contacts, full ordinary/compiler/outer budgets, a new kappa or a selected
frontier. A positive relative gain does not assert either absolute margin is
positive. All five framework assumptions remain. 

## Open next questions

Structured first steps for remaining native/physical and full-budget
applicability questions are in [TASK.json](TASK.json).

## Credit

Construction: DreamingOfClouds with Claude Opus5.5 (Anthropic); Ali Romman's
6372/6353/6349/6348 lineage and the full retained [NOTICE](sources/NOTICE),
including Cinna Davis, Jacob Alan Sussman, zxv, Cao Yifan and all native/helper/
controller/BIT/analytic predecessors. The author reports a separate read-only
row/ownership/sensitivity audit; it is prior work, not this contribution.

Independent invoice audit6359, scalar audit6376, threshold work5174/5772 and the
canonical general recursive-power-variation/interval tools retain distinct
credit. The elementary Taylor, logarithm and single-crossing methods are not
claimed as new general theorems. New source-bound audit/proof: ToikY with
substantial OpenAI Codex assistance and bounded separately assigned agents.
Same-session reviews and independent implementations remain author-side checks,
pending human scientific acceptance. Apache-2.0.
