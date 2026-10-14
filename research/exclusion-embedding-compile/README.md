# Faster ExclusionCircuit.verify_embedding compile with identical receipts

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, merged
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
replaced the reverse-frame expected-support genexpr inside
`ExclusionCircuit.verify_embedding` with a closed-form mask. Profiling on the
historical full-size circuit (`n=45`, 12556 reversible roles) shows the residual
wall time is dominated by `compile`'s `edge[node,pos]` tuple-key maps and by
per-gate `set(ins+outs)` nesting loops.

This change keeps every compile map field and every `verify_embedding` receipt
identical while:

1. walking `sorted(self.active)` once and wiring slots through parallel
   `edge0` / `edge1` maps;
2. updating forward/reverse frames with pivot-first `ins[1:]` / `outs[1:]`
   iteration (historically `set(ins) & set(outs) == {pivot}`);
3. propagating descendants on a dense array instead of a per-active dict.

`ExclusionCircuit.verify`, `circuit_sha256`, and both closed-form leave-two /
reverse masks are unchanged. Only the source pin for
`scripts/exclusion_circuit.py` changes inside the four certificates that bind
that file.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/exclusion-embedding-compile/verify.py
python3.12 -I -O -B research/exclusion-embedding-compile/verify.py
python3.12 -B scripts/research_package.py --package research/exclusion-embedding-compile
python3.12 -I -B research/exclusion-embedding-compile/benchmark.py --rounds 5
```

Expected:

```text
PASS_EXCLUSION_EMBEDDING_COMPILE cases=8 certs=4 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/exclusion-embedding-compile outcome=completed
PASS_IDENTICAL_EXCLUSION_EMBEDDING_COMPILE_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only
`ExclusionCircuit(45).verify_embedding` (construction excluded) gave median wall
time **0.056 → 0.033 seconds (1.71×)**.
Timing is host-descriptive and is not a correctness gate; all samples and
environment pins are in [RESULT.json](RESULT.json). Every compile map and
embedding receipt matches the baseline checker fieldwise.

## Equivalence

- **Compile:** same `roles`, `gates`, `sources`, and `outputs`. Parallel
  `edge0[node]` / `edge1[node]` store the same slots as the historical
  `edge[node,0]` / `edge[node,1]` tuple keys. Binary-gate uniqueness
  `ins[0] != ins[1]` plus fresh `outs[1:]` ids preserve
  `set(ins) & set(outs) == {pivot}`.
- **Nesting:** for every historical gate, `set(ins+outs)` equals
  `{pivot} ∪ set(ins[1:]) ∪ set(outs[1:])` with those three parts pairwise
  disjoint except the shared pivot, so pivot-first updates match the set loop.
- **Descendants:** inactive nodes stay at bit-zero on the dense array and are
  skipped; active reverse propagation matches `sorted(self.active, reverse=True)`.

A compile-map mutant that swaps two output slots is rejected by both baseline
and optimized `verify_embedding` under non-`-O` runs. Temp-copy digest
corruption of production bytes is rejected by the package digest gate.

## Open next questions

1. **Question:** Should `research/bit-compression-provenance` and other packages
   that pin live `scripts/exclusion_circuit.py` bytes refresh those SHA-256
   entries after this equivalence-preserving rewrite?
   **Why it matters:** Those provenance packages bind working-tree bytes; leaving
   the old pin keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up that only rewrites those
   `SOURCES` / `SOURCE-PINS` entries after confirming embedding receipts stay
   identical.
   **Blocked by:** Pin repair outside the four binding certificates is outside
   this tooling change.

2. **Question:** Is `ExclusionCircuit.compile` alone worth a soft CI regression
   timer, or should `RESULT.json` stay descriptive only?
   **Why it matters:** Host-descriptive medians already gate nothing; a soft
   timer could catch accidental compile regressions without claiming a kappa
   effect.
   **First step:** Propose a non-blocking timer on `ExclusionCircuit(45).compile`
   in the existing research-packages workflow after this PR lands.
   **Blocked by:** Maintainer CI policy; out of this session’s stop rule.

## Overlap and credit

Closest priors (different objects or delivery):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861)
(open; primary pin `binary_phase_frames.py`),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
(leave-two / reverse masks; this package answers the residual compile/nesting
object after those masks),
[CrocSwap/integer-mult-bounds#2100](https://github.com/CrocSwap/integer-mult-bounds/pull/2100)
(open; same `ternary-side.json` file, different pin key `ternary_side.py`),
[CrocSwap/integer-mult-bounds#2117](https://github.com/CrocSwap/integer-mult-bounds/pull/2117)
(open; same shared JSON files, different pin key `disjoint_tensor.py`),
[CrocSwap/integer-mult-bounds#2150](https://github.com/CrocSwap/integer-mult-bounds/pull/2150)
(open; mixed-point `Circuit.verify`; different file). No competing open PR on
`ExclusionCircuit.compile` / residual `verify_embedding` nesting at refresh.

Douglas R. Colkitt authored the exclusion / shared-point / positive-side checkers.
Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
