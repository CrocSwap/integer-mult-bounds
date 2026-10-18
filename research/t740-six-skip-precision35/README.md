# T740 six-skip 35-digit release candidate

This package tests the exact next 35-digit complex-moment point above the public PR #3115 claim, which was still open when checked on 2026-10-17. The candidate endpoint is `0.00172973795006427855124289582381734`; at endpoint precision 35 the fixed-grid slacks give exact κ `C35 - 10^-57 - 10^-81`. It exceeds #3115 by about `8.1734e-31` if and only if the entire strict outer release accepts it.

This is a precision extension of the same T740 profile, not a changed paid mechanism. The two independent rational moment engines, 35-digit adjacent-point rejection, and unpaid-child rejection are checked locally. These checks do not establish a κ release.

The outer ledger's free gap is `R0 = 10^-(endpoint_digits+80)`, so this endpoint requires the exact interior point `b = C35 - 10^-115`. The package binds both that rational value and its claim text to the declared endpoint precision.

Run the unmodified predecessor release first:

```sh
python3.12 -B research/t740-six-skip-precision35/baseline.py \
  --repo FULL_GIT_REPO_WITH_GIT_SOURCES_OBJECTS --work /tmp/t740-precision35-baseline
```

Create a Python 3.12 environment from `requirements-full.txt` and use its interpreter for every command. The full release invokes child processes through the active interpreter; the system Python may have incompatible scientific packages.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r research/t740-six-skip-precision35/requirements-full.txt
```

Then run the candidate's complete changed admission and outer release in a fresh workspace:

```sh
python3.12 -B research/t740-six-skip-precision35/reproduce.py \
  --baseline-work /tmp/t740-precision35-baseline \
  --work /tmp/t740-precision35-candidate
```

After both full releases pass, seal only the verified terminal evidence:

```sh
python3.12 -B research/t740-six-skip-precision35/seal.py \
  --baseline-work /tmp/t740-precision35-baseline \
  --work /tmp/t740-precision35-candidate
```

The package pins its scientific inputs to canonical main `997e6a9ca7b4f95d50e366f61412fd640d72a88a`. `FULL_GIT_REPO_WITH_GIT_SOURCES_OBJECTS` must contain the exact heads listed in the predecessor `GIT-SOURCES.json`; fetch those objects before an offline replay if needed. The full run uses the pinned Python dependencies and native C++ build; runtime metadata and any environment difference must be recorded in sealed evidence. The registered package check validates the sealed exact arithmetic and actual outer ledger but does not rerun native providers.

## Frontier check (2026-10-17)

Direct GitHub pages show PR #3115 still open with the exact claim above and the current open-PR listing extending through #3119. The later visible submissions do not claim a higher exponent: #3116 is a local ceiling screen explicitly without a κ claim, #3117 says the complex side still binds and makes no new κ claim, #3118 is a partial set-level covering investigation, and #3119 says it adds no exponent. The canonical Git fetch and cached overlap refresh both failed here because DNS could not resolve `github.com`; this is a direct-page check rather than a refreshed Git snapshot or an exhaustive immutable overlap audit. Recheck the public frontier before relying on this comparison after 2026-10-17.

## Open next questions

This result is a tiny arithmetic refinement only. A potentially larger route is open PR #3116's weighted diagonal rank-batching screen, whose local ceiling is around κ=0.1006 but which explicitly has no constructed endpoint, physical fusion invoice, or bit-supplier admission. Coordinate with that work before pursuing it; a full charged endpoint is still needed. The parallel B-phase/later-A handoff around normal-7 pivots 363/395 also remains a structural route, subject to a complete supplier bill.

Credit the T740 six-skip and precision30 predecessors and all source lineage they retain. No selected-frontier update, independent human review, formal proof, or hosted CI pass is implied by this local package.
