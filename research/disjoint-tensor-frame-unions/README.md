# Faster DisjointTensor.frame_data with identical frame receipts

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, merged
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
left `DisjointTensor.verify_frames` / `frame_data` as an explicit next question
after shipping closed-form verify support masks. Profiling on the historical
full-size circuit (`h=26`, 60372 active nodes) shows about 1.8 of 2.2 seconds
of `verify_frames` inside the per-node reachable-target bit enumeration in
`frame_data`.

[CrocSwap/integer-mult-bounds#1044](https://github.com/CrocSwap/integer-mult-bounds/pull/1044)
already proved exact target-union propagation as an **opt-in** adapter under
`research/disjoint-frame-unions/`. Production `scripts/experiments/disjoint_tensor.py`
still used the historical bit loop. This change promotes the same algebra into
the default path, keeps every descendant bitset, source union and rectangle
`require`, and leaves `verify_frames` receipts fieldwise identical. Only the
source pin for `scripts/experiments/disjoint_tensor.py` changes inside the four
certificates that bind that file.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/disjoint-tensor-frame-unions/verify.py
python3.12 -I -O -B research/disjoint-tensor-frame-unions/verify.py
python3.12 -B scripts/research_package.py --package research/disjoint-tensor-frame-unions
python3.12 -I -B research/disjoint-tensor-frame-unions/benchmark.py --rounds 5
```

Expected:

```text
PASS_DISJOINT_TENSOR_FRAME_UNIONS frame_cases=6 map_cases=6 certs=4 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/disjoint-tensor-frame-unions outcome=completed
PASS_IDENTICAL_DISJOINT_TENSOR_FRAME_UNION_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `DisjointTensor(26).verify_frames`
(construction excluded) gave median wall time **2.232 → 0.465 seconds (4.80×)**.
Timing is host-descriptive and is not a correctness gate; all samples and
environment pins are in [RESULT.json](RESULT.json). Every frame receipt matches
the baseline checker fieldwise (`distinct_nontrivial_transitions`,
`frame_types`, flags).

## Equivalence

For a node \(v\) let \(D(v)\) be its set of reachable output indices. If output
\(i\) has ground-coordinate mask \(T_i\), the historical loop computes

```text
U(v) = OR_{i in D(v)} T_i
```

by walking bits of \(D(v)\). Define \(F(A)=\mathrm{OR}_{i\in A} T_i\). Then
\(F(\emptyset)=0\) and \(F(A\cup B)=F(A)\lor F(B)\). Initializing \(U\) at the
same output nodes as \(D\) and propagating \(U\) alongside \(D\) in the identical
reverse topological order yields \(U(v)=F(D(v))\) at every node. An XOR-of-mask
mutant cancels overlapping paths and is rejected by the package controls.
Rectangle checks still use `require`, so admission stays enforced under `-O`.

## Open next questions

1. **Question:** Should `DisjointTensor.verify`'s `dag_sha256` `json.dumps` path
   get a hand-rolled formatter like the mixed-point / SharedPoint digests?
   **Why it matters:** After support masks and frame_data, `json.dumps` remains a
   secondary share of verify.
   **First step:** Profile the post-mask verify residual and compare a
   hand-rolled `[[i,args,str(support)]]` encoder against the committed digest.
   **Blocked by:** Out of this session’s stop rule.

2. **Question:** Can `research/disjoint-frame-unions` drop its opt-in monkeypatch
   now that production `frame_data` matches the accelerator?
   **Why it matters:** The adapter is redundant on main, but its
   byte-for-byte historical certificate claim is a separate provenance object.
   **First step:** Diff accelerator vs production and decide whether that
   package becomes a pure historical replay fixture.
   **Blocked by:** Do not reopen #1044’s certificate fixture in this PR.

## Overlap and credit

Closest priors (different objects or delivery):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1044](https://github.com/CrocSwap/integer-mult-bounds/pull/1044)
(opt-in exact union propagation; this package promotes it to production),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
(support masks + open `verify_frames` / `frame_data` question this answers).
Open [CrocSwap/integer-mult-bounds#2100](https://github.com/CrocSwap/integer-mult-bounds/pull/2100)
updates `ternary_side.py` inside `certificates/ternary-side.json`; this PR only
rewrites the `disjoint_tensor.py` pin in that shared JSON.
Open [CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861)
updates `binary_phase_frames.py` inside `certificates/parity-side.json`; shared
JSON should carry both pins on merge.

Douglas R. Colkitt authored the disjoint-tensor checkers. Stephan Arrington’s
#1044 supplied the opt-in union algebra. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

### Maintainer integration note (PR2100 + PR2117)

Both optimizations are incorporated together. The shared ternary certificate
therefore changes two source pins. The check permits exactly the reviewed
companion hash, authenticates its live source, and preserves every other
certificate field. Independent baseline equivalence checks remain required for
each optimization. This adds no new mathematical claim or performance result.
