# Faster exact shared-point verify digests with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, `SharedPointCircuit.verify` builds
`circuit_sha256` with per-active-node and per-partial-output
`json.dumps(..., separators=(',',':'))` updates. Profiling on the historical
full-size circuit (`h=46`, 501510 active nodes, 45540 partial outputs) shows
about half of verify wall time in that JSON encoder path. Open
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984)
left this object as an explicit next question after shipping mixed-point
`scalar_check` digests.

This change writes the same UTF-8 digest lines with an equivalent hand-rolled
formatter (`[node,null,null]`, `[node,[a,b],[common,local]]`,
`[common,[t0,t1,t2],node]`), keeps every support and topology assertion, and
leaves `circuit_sha256` unchanged. The bit-compression certificate does not
list `scripts/shared_point_circuit.py` in `source_sha256`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/shared-point-digest/verify.py
python3.12 -I -O -B research/shared-point-digest/verify.py
python3.12 -B scripts/research_package.py --package research/shared-point-digest
python3.12 -I -B research/shared-point-digest/benchmark.py --rounds 5
```

Expected:

```text
PASS_SHARED_POINT_DIGEST verify_cases=5 encoding_cases=8 certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/shared-point-digest outcome=completed
PASS_IDENTICAL_SHARED_POINT_DIGEST_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `SharedPointCircuit(46).verify`
(construction excluded; nested `ExclusionCircuit.verify` included) gave median
wall time **2.212 → 1.070 seconds (2.07×)**. Timing is host-descriptive and is
not a correctness gate; all samples and environment pins are in
[RESULT.json](RESULT.json). Every verify receipt matches the baseline checker
fieldwise (`roles`, `additions`, `merged_additions`, `circuit_sha256`, flags).

## Equivalence

For each active node the historical encoder emitted

- `json.dumps((node, None, None), separators=(',',':'))+'\n'` → `[node,null,null]\n`
- `json.dumps((node, (a,b), (common,local)), separators=(',',':'))+'\n'` → `[node,[a,b],[common,local]]\n`

and for each partial output

- `json.dumps((common, (t0,t1,t2), node), separators=(',',':'))+'\n'` → `[common,[t0,t1,t2],node]\n`

with default JSON integer formatting (no whitespace). The hand-rolled writer
emits those exact byte strings. A `None` vs `null` spelling mutant and a flat
`[node,a,b,common,local]` mutant differ and are rejected by the package
controls. Support and topology checks remain the historical `assert` gates.

## Open next questions

1. **Question:** Should `research/bit-compression-provenance` refresh its live
   `scripts/shared_point_circuit.py` SHA-256 pin after this equivalence-preserving
   digest rewrite?
   **Why it matters:** That provenance package binds working-tree bytes; leaving
   the old pin keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up that only rewrites that one
   `SOURCES.json` entry after confirming `circuit_sha256` identity.
   **Blocked by:** Pin repair is outside this tooling change.

2. **Question:** Is `ExclusionCircuit.verify`'s leave-two-out expected-support
   genexpr worth a separate identical-receipt rewrite?
   **Why it matters:** Its single `json.dumps` is not hot; the support sum is.
   **First step:** Profile `ExclusionCircuit(45).verify` alone and prototype a
   closed-form support mask if one matches the historical expected bits.
   **Blocked by:** Out of this session’s stop rule.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984)
(mixed-point `scalar_check`; this package answers its SharedPoint open question),
[CrocSwap/integer-mult-bounds#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874).
No competing open PR on the `SharedPointCircuit.verify` digest object at refresh.

Douglas R. Colkitt authored the shared-point / exclusion circuits and
bit-compression screens. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
