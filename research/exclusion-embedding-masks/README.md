# Faster exact exclusion embedding reverse masks with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, `ExclusionCircuit.verify_embedding`
checks each reverse-frame source expected support with

`sum(1<<i for target,i in target_index.items() if not set(source)&set(target))`.

Profiling on the historical full-size circuit (`n=45`, 990 sources, 12556
reversible roles) shows most `verify_embedding` wall time in that genexpr. Open
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
left this object as an explicit next question after shipping `verify`
leave-two-out support masks. Landed together with the leave-two-out `verify` closed form from
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
so `scripts/exclusion_circuit.py` and its four certificate pins update once.

This change precomputes per-vertex incident sorted-output masks and asserts the
equivalent closed form `full ^ (vertex[a] | vertex[b])`, keeps every forward and
reverse nesting assertion, and leaves embedding receipts fieldwise identical.
The four certificates that pin `scripts/exclusion_circuit.py` update only that
source hash. `circuit_sha256` is unchanged; `ExclusionCircuit.verify` carries the sibling
leave-two-out closed form from #2001 in the same production file.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/exclusion-embedding-masks/verify.py
python3.12 -I -O -B research/exclusion-embedding-masks/verify.py
python3.12 -B scripts/research_package.py --package research/exclusion-embedding-masks
python3.12 -I -B research/exclusion-embedding-masks/benchmark.py --rounds 5
```

Expected:

```text
PASS_EXCLUSION_EMBEDDING_MASKS embedding_cases=8 mask_cases=1997 certs=4 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/exclusion-embedding-masks outcome=completed
PASS_IDENTICAL_EXCLUSION_EMBEDDING_MASK_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only
`ExclusionCircuit(45).verify_embedding` (construction excluded; compile remains
inside the timed method) gave median wall time **0.323 → 0.059 seconds
(5.46×)**. Timing is host-descriptive and is not a correctness gate; all
samples and environment pins are in [RESULT.json](RESULT.json). Every embedding
receipt matches the baseline checker fieldwise (`reversible_roles`, forward and
reverse nesting flags, `no_forbidden_source_target_path`).

## Equivalence

For a source edge `(a,b)`, the historical reverse expected support is the
bitmask of all sorted leave-two-out output targets that are vertex-disjoint from
`{a,b}`. With `full = (1<<C(n,2))-1` over that sorted-output index and
`vertex[v]` the mask of targets incident to `v`,

`full ^ (vertex[a] | vertex[b])`

clears exactly those incident targets and equals the genexpr. A mutant that uses
`full ^ vertex[a] ^ vertex[b]` incorrectly retains the `(a,b)` bit and is
rejected by the package controls. Forward coefficient and nesting checks remain
the historical `assert` gates.

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

2. **Question:** When open
   [CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
   (`verify` leave-two-out masks) and this `verify_embedding` rewrite both land,
   should maintainer merge keep both closed forms in one file with a single
   updated source pin?
   **Why it matters:** Both PRs edit the same historical checker for different
   methods; certificate pins will need one combined hash after merge.
   **First step:** Rebase the later PR onto the earlier merge commit and re-hash
   `scripts/exclusion_circuit.py` once.
   **Blocked by:** Upstream merge order is a maintainer action; this package
   co-lands with #2001's leave-two-out closed form in one production pin.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
(`verify` leave-two-out masks; this package answers its `verify_embedding` open
question),
[CrocSwap/integer-mult-bounds#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874).
No competing open PR on the `ExclusionCircuit.verify_embedding` reverse-frame
support object at refresh.

Douglas R. Colkitt authored the exclusion / shared-point circuits and
bit-compression screens. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
