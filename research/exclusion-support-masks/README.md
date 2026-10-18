# Faster exact exclusion leave-two-out supports with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, `ExclusionCircuit.verify` checks each
leave-two-out output support with

`sum(1<<i for i,p in enumerate(self.inputs) if a not in p and b not in p)`.

Profiling on the historical full-size circuit (`n=45`, 990 outputs, 11566
additions) shows nearly all verify wall time in that genexpr. Open
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994)
left this object as an explicit next question after shipping shared-point verify
digests (its single `json.dumps` is not hot).

This change precomputes per-vertex incident-pair masks and asserts the
equivalent closed form `full ^ (vertex[a] | vertex[b])`, keeps every support and
topology assertion, and leaves `circuit_sha256` unchanged. The four certificates
that pin `scripts/exclusion_circuit.py` update only that source hash.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/exclusion-support-masks/verify.py
python3.12 -I -O -B research/exclusion-support-masks/verify.py
python3.12 -B scripts/research_package.py --package research/exclusion-support-masks
python3.12 -I -B research/exclusion-support-masks/benchmark.py --rounds 5
```

Expected:

```text
PASS_EXCLUSION_SUPPORT_MASKS verify_cases=8 mask_cases=1997 certs=4 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/exclusion-support-masks outcome=completed
PASS_IDENTICAL_EXCLUSION_SUPPORT_MASK_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `ExclusionCircuit(45).verify`
(construction excluded) gave median wall time **0.092 → 0.008 seconds
(11.08×)**. Timing is host-descriptive and is not a correctness gate; all
samples and environment pins are in [RESULT.json](RESULT.json). Every verify
receipt matches the baseline checker fieldwise (`additions`, `scratch_roles`,
`nonzero_coefficients`, `circuit_sha256`, flags).

## Equivalence

For excluded vertices `a,b`, the historical expected support is the bitmask of
all pair-inputs that contain neither `a` nor `b`. With `full = (1<<C(n,2))-1`
and `vertex[v]` the mask of pairs incident to `v`,

`full ^ (vertex[a] | vertex[b])`

clears exactly those incident pairs and equals the genexpr. A mutant that uses
`full ^ vertex[a] ^ vertex[b]` incorrectly retains the `(a,b)` bit and is
rejected by the package controls. Support and topology checks remain the
historical `assert` gates.

## Companion rewrite

The sibling reverse-frame genexpr in `ExclusionCircuit.verify_embedding` is
rewritten in the same production file and packaged as
`research/exclusion-embedding-masks/` (same four certificate pins, one re-hash).

## Open next questions

1. **Question:** Should `research/bit-compression-provenance` and other packages
   that pin live `scripts/exclusion_circuit.py` bytes refresh those SHA-256
   entries after this equivalence-preserving rewrite?
   **Why it matters:** Those provenance packages bind working-tree bytes; leaving
   the old pin keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up that only rewrites those
   `SOURCES` / `SOURCE-PINS` entries after confirming `circuit_sha256` identity.
   **Blocked by:** Pin repair outside the four binding certificates is outside
   this tooling change.

2. **Answered in-tree:** `ExclusionCircuit.verify_embedding` reverse-frame closed form lands in the same production file as `research/exclusion-embedding-masks/` (identical receipts; one re-pin).

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994)
(shared-point digests; this package answers its ExclusionCircuit open question),
[CrocSwap/integer-mult-bounds#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874).
No competing open PR on the `ExclusionCircuit.verify` leave-two-out support
object at refresh.

Douglas R. Colkitt authored the exclusion / shared-point circuits and
bit-compression screens. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
