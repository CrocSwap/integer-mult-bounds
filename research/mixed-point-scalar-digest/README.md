# Faster exact mixed-point scalar digests with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, the historical mixed-point audit
(`scripts/audit_mixed_point.py`) and the early-sharing screen both call
`scalar_check` on large cancellation-free circuits. Profiling shows a large
share of that helper’s time in per-node `json.dumps((node, args), …)` and
per-output `json.dumps((i, node), …)` while building `circuit_sha256`.

This change writes the same UTF-8 digest lines with an equivalent hand-rolled
formatter (`[node,null]`, `[node,[a,b]]`, `[i,node]`), keeps every support and
topology `require`, and leaves `circuit_sha256` unchanged. No certificate
`source_sha256` pin lists `audit_mixed_point.py`; the mixed-point and
early-sharing mathematical payloads stay fieldwise identical to the committed
files.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/mixed-point-scalar-digest/verify.py
python3.12 -I -O -B research/mixed-point-scalar-digest/verify.py
python3.12 -B scripts/research_package.py --package research/mixed-point-scalar-digest
python3.12 -I -B research/mixed-point-scalar-digest/benchmark.py --rounds 5
```

Expected:

```text
PASS_MIXED_POINT_SCALAR_DIGEST scalar_cases=7 encoding_cases=5 certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/mixed-point-scalar-digest outcome=completed
PASS_IDENTICAL_MIXED_POINT_SCALAR_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `scalar_check` on the fixed
mixed-point circuit set (block-only and hybrid `h=50`, then four factored
rounds; construction excluded from the timed window) gave median wall time
**10.004 → 4.444 seconds (2.25×)**. Timing is host-descriptive and is not a
correctness gate; all samples and environment pins are in
[RESULT.json](RESULT.json). Every scalar receipt matches the baseline checker
fieldwise (`roles`, `circuit_sha256`, flags).

## Equivalence

For each active node the historical encoder emitted

- `json.dumps((node, None), separators=(',',':'))+'\n'` → `[node,null]\n`
- `json.dumps((node, (a,b)), separators=(',',':'))+'\n'` → `[node,[a,b]]\n`

and for each output index

- `json.dumps((i, node), separators=(',',':'))+'\n'` → `[i,node]\n`

with default JSON integer formatting (no whitespace). The hand-rolled writer
emits those exact byte strings. A `None` vs `null` spelling mutant differs and
is rejected by the package controls. Support and topology `require` calls are
unchanged, including under `-O` (they use `require`, not `assert`).

## Open next questions

1. **Question:** Can the same byte-identical hand-rolled digest pattern
   accelerate `SharedPointCircuit.verify` / `ExclusionCircuit.verify` without
   changing `circuit_sha256`?
   **Why it matters:** Those verifiers still call `json.dumps` once per active
   node on large common-point circuits.
   **First step:** Profile `SharedPointCircuit.verify` for the h=50
   bit-compression local circuit and compare a hand-rolled line writer against
   the committed digest.
   **Blocked by:** Out of this session’s stop rule; `scalar_check` was the
   profiled mixed-point bottleneck.

2. **Question:** Should `certificates/mixed-point-audit.json` refresh its stale
   `rational_span_frames.py` `source_sha256` pin (live digest already differs on
   main)?
   **Why it matters:** The pin is historical provenance for an unchanged
   mathematical payload; leaving it avoids mixing a tooling PR with an
   unrelated pin repair.
   **First step:** Open a dedicated provenance follow-up that only rewrites the
   three `source_sha256` entries after a clean certificate regenerate.
   **Blocked by:** Pin repair is outside this tooling change.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217),
and `research/rational-containment-performance/` (mixed-point `contained`
adapter). No competing open PR on the `scalar_check` digest object at refresh.

Douglas R. Colkitt authored the mixed-point and early-sharing screens and
original checkers. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
