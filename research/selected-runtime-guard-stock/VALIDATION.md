# Validation record

Checked on 2026-10-17 using Linux 6.6.87.2-microsoft-standard-WSL2, x86_64,
CPython 3.12.15 and CPython 3.13.5. Standard library only. The tested source
baseline is canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`.

## Observed checks

The following commands passed against the retained package bytes:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/selected-runtime-guard-stock
python3 -Werror -I -B research/selected-runtime-guard-stock/test_verify.py
ruff check research/selected-runtime-guard-stock/*.py
git diff --check
```

The registered replay runs the source-authenticated primary checker, the
separate checker and all eleven optimized behavioral groups. Its markers were:

```text
PASS_RUNTIME_GUARD_STOCK selected_Q=9475 depth2_factor=9475 literal_probes=3 rejected_controls=9 no_new_kappa
PASS_INDEPENDENT_GUARD_STOCK lcm_cases=315 pointwise_rows=8640 old_format_depths=8
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-runtime-guard-stock outcome=partial
```

All eleven groups also passed under ordinary CPython 3.13.5. Both interpreter
modes exercise optimized child CLI runs. The receipt controls reject missing
receipts, a changed object and a boolean substituted for the integer atom width.
The exact typed scientific receipt is [RESULT.json](RESULT.json). No timing or
performance improvement is claimed.

Temporary bytecode namespaces, isolated corruption fixtures and logs used an
external session-owned directory via `TMPDIR`, never frozen source inputs.
The verifier emits no scientific outputs by default. The initial required
receipt was explicitly generated to an external new file and then retained;
subsequent replays compared it without regeneration.

## Source and mathematical review

Two local review passes checked different obligations:

1. The divisor induction, non-coprime cases, zero depth, shorter children,
   pointwise reuse premise, group-order envelope and the exact old-format gate.
2. The logical/physical NODE quotient and compatibility expressions, actual
   child-stock handoff, fixed modulus, imported source closure, cleanup and
   receipt/source failure behavior.

The first retained module audit initially expected a function-local `oracle`
import before it had been loaded. The fixed twelve-module closure is now
explicitly imported and all actual module paths are checked after byte
validation. The earlier throwaway literal probe also used a noncanonical modulus
bank width; the retained probes use each modulus's bit length plus its required
single high-bit margin. Neither failed probe supplied the retained receipt.

These were local reviews and separately implemented finite checks, not
independent human review, separate reviewer sessions or proof-kernel evidence.
All new functions are below 60 physical lines. Ruff and warnings-as-errors checks
passed. Managed allocation and fixed import-boundary deviations are documented
in the README; unmodified predecessor source is not reformatted or repaired.

## Freshness and scope

A pre-submission canonical fetch at 2026-10-17T19:10:17Z still resolved to the
same main commit. Priorities, revision-6 catalogue, family status and selected
record were unchanged. The refreshed overlap corpus had complete pagination:
288 open PRs at 19:09:47Z and 2,068 Discussion records at 19:10:15Z. The exact
9475/compatibility search found the named predecessors and this investigation's
claim, with no new matching scope. This corpus omits arbitrary code diffs and
unpublished work; it is not a novelty certificate.

The canonical claim is [Discussion2319 comment19002967](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19002967).
PR2420's dual-format minimum and PR3223's adjacent NODE audit remain predecessor
results. The present package changes only its own scoped research directory.

Unrun obligations include a complete selected GL64 payload, the large-prime
physical caller, the backend stock-selector change, all-size physical refinement,
actual dirty-state/consumer composition, H2 time/precision/tape obligations,
selected cold replay, Lean and Docker. Nothing in the finite q=3 quotient probes
is presented as admission to the selected large-prime supplier domain.
