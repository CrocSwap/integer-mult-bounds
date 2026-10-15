# Faster exact partial-swap verify digests with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, the partial-swap fork of
`SharedPointCircuit.verify` (`scripts/partial_swap/shared.py`) builds
`circuit_sha256` with per-active-node and per-partial-output
`json.dumps(..., separators=(',',':'))` updates. Profiling on the historical
full-size circuit (`h=46`, 501510 active nodes, 45540 partial outputs) shows
about half of verify wall time in that JSON encoder path. Open
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994)
applied the same byte-identical formatter to the canonical
`scripts/shared_point_circuit.py`; this package applies it to the distinct
partial-swap producer copy, which still used `json.dumps`.

This change writes the same UTF-8 digest lines with an equivalent hand-rolled
formatter (`[node,null,null]`, `[node,[a,b],[common,local]]`,
`[common,[t0,t1,t2],node]`), keeps every support and topology assertion, and
leaves `circuit_sha256` unchanged. `certificates/partial-swap-network.json`
updates only the `scripts/partial_swap/shared.py` `source_sha256` pin.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/partial-swap-digest/verify.py
python3.12 -I -O -B research/partial-swap-digest/verify.py
python3.12 -B scripts/research_package.py --package research/partial-swap-digest
python3.12 -I -B research/partial-swap-digest/benchmark.py --rounds 5
```

Expected:

```text
PASS_PARTIAL_SWAP_DIGEST verify_cases=5 encoding_cases=8 certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/partial-swap-digest outcome=completed
PASS_IDENTICAL_PARTIAL_SWAP_DIGEST_RECEIPTS
```

Default verify is read-only aside from the already-committed pin-only certificate
refresh. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only
`partial_swap.shared.SharedPointCircuit(46).verify` (construction excluded;
inlined local support checks included) gave median wall time
**2.176 → 1.050 seconds (2.07×)**. Timing is host-descriptive and is not a
correctness gate; all samples and environment pins are in
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

1. **Question:** Should research packages that pin live
   `scripts/partial_swap/shared.py` bytes refresh that one SHA-256 entry after
   this equivalence-preserving digest rewrite?
   **Why it matters:** Those provenance packages bind working-tree bytes;
   leaving old pins keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up that only rewrites that one
   `SOURCES.json` entry after confirming `circuit_sha256` identity.
   **Blocked by:** Pin repair outside `certificates/partial-swap-network.json`
   is outside this tooling change.

2. **Answered in-tree:** `partial_swap.shared.SharedPointCircuit.__init__` merge/lookup rewrite lands in the same production file as `research/partial-swap-init/` (identical DAG/`circuit_sha256`; one re-pin).

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994)
(canonical `shared_point_circuit.py` verify digests; this package applies the
same formatter to the partial-swap fork),
[CrocSwap/integer-mult-bounds#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874).
No competing open PR on the `partial_swap.shared` verify digest object at
refresh. #2001's ExclusionCircuit / DisjointTensor support-mask files are not
touched.

Douglas R. Colkitt authored the shared-point / exclusion circuits. icekylinx
adapted the partial-swap producer copy. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
