# Exact interior-carry criterion for compact controls

**Mathematical audit / research note; no new kappa.** The retained guard is
correct. Outside it, a compact-control word can produce the correct target
while corrupting a dirty temporary. This package proves an exact full-map
agreement criterion for the earlier-source word with nonsaturated temporary
digits: only interior target carries matter; the final outgoing carry is
harmless. The resulting invariant repair envelope is smaller, with the
unchanged physical word and complete inherited repair charges.

For `B=2^G`, `A=2^(K-1)`, `n>=1`, `G>=1`, `K>=G+1`, `0<=rho<K`, and
`t_i<=B-2`, full correctness is equivalent to

```text
g_i + z_i*t_i < A    for 0 <= i < n-1.
```

The good fraction on complete independent fields is exactly

```text
((B-1)/B)^n * (1-(B-2)/(4*A))^(n-1).
```

At `n=2,K=6,G=2`, this is `567/1024`, versus the old guard's `9/64`.
It is an envelope fraction, not a runtime improvement. The
[proof](PROOF.md) includes necessity, dirty-field restoration, the harmless
last carry, invariant repair, full charges, inherited assumptions and credit.

## Reproduce

Python 3.10+ and its standard library, from the repository root:

```sh
python3 -I -O -B research/compact-guard-audit-seed71/test_package.py
```

Expected markers:

```text
PASS_COMPACT_GUARD_AUDIT states=1679360 source_samples=1536 domains=6 no_new_kappa
PASS_COMPACT_GUARD_PACKAGE relocated_isolated_optimized=PASS faults=7 [source_drift, nonstrict_guard, forbid_last_carry, target_only, omit_highest_xor, receipt_drift, occupied_output]
```

The package test runs a minimal relocated checkout from an unrelated
directory, with assertions disabled, and requires seven real subprocess
faults to fail. For a direct receipt comparison, run
`python3 -I -O -B research/compact-guard-audit-seed71/verify.py`.
Ordinary verification does not regenerate artifacts. `--write PATH` writes
a new receipt only and rejects an occupied path.

## Evidence and scope

| Check | Completed evidence |
|---|---:|
| Complete finite address quotients | 1,679,360 states in six declared domains |
| Target-only false acceptances | 89,360 states with wrong dirty temporary |
| Local integer/carry cases | 161,448 cases across 25 radix pairs |
| Physical predecessor comparisons | 1,536 seed-71 samples, including arbitrary back fields |
| Highest selected-bit completion | 3,358,720 actual repaired-record checks |
| Sorted repair | Every record in every finite quotient; exact hole/key equality |
| Wrong `T(q)` repair keys | All holes still filled; wrong record identities detected in every domain |

[EXPECTED.json](EXPECTED.json) records domains, counts, exact fractions and
deterministic map/payload hashes. The independent census implements the
four modular updates directly; it imports no predecessor generator or
simulator. The predecessor is imported only for the separately counted
physical differential samples. The quotient retains every target bit at or
above `rho`; the proof justifies omitted spectator fields. The six finite
domains do not exhaust the universally quantified theorem.

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. Required SHA256 and Git-blob
pins are in [SOURCES.json](SOURCES.json); selection-at-base is context only.
The selected #1094 certificate, its source packages, and `upstream/` are
unchanged. [CLAIM.json](CLAIM.json) records seed 71, three candidate tasks,
overlap checks and the stopping rule. [VALIDATION.json](VALIDATION.json)
separates completed checks from unrun obligations.

This extends the multi-digit target-guard question beyond John-Michael
Smith's #763 later-source audit and @martinxxx9's #1108 one-digit law.
It does not reopen their closed searches. Douglas Colkitt's compact
construction and OpenAI's source framework receive predecessor credit;
full attribution and inspected PR heads are in the proof and source record.

The result remains an address theorem with written proof and finite
supporting evidence. Later-source extension, production adoption, physical
tape implementation, recursive hosting/precision, analytic transfer and
the full multiplication theorem are outside this audit.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in mathematics, code, verification and writing. Apache-2.0.
No independent human peer review or proof-assistant verification is claimed.
