# Faster DisjointTensor.verify output supports with identical receipts

**Tooling improvement; no new kappa.**
Landed with open [CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001) so shared certificate JSON files carry both the `exclusion_circuit.py` and `disjoint_tensor.py` source pins without a merge conflict.
 At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, the historical disjoint-tensor
checker (`scripts/experiments/disjoint_tensor.py:DisjointTensor.verify`) spends
most of its wall time on the leave-intersecting-inputs expected-support genexpr

```text
sum(1<<i for i,S in enumerate(self.inputs) if not S&T)
```

for every triple output `T` on the certificate circuit (`h=26`, 2600 inputs).

This change replaces that genexpr with an equivalent closed-form point-incidence
mask `full ^ OR_{p in T} vertex[p]`, keeps every support and embedding
`require`, and leaves `dag_sha256` unchanged. Only the source pin for
`scripts/experiments/disjoint_tensor.py` changes inside the four certificates
that bind that file.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/disjoint-tensor-support-masks/verify.py
python3.12 -I -O -B research/disjoint-tensor-support-masks/verify.py
python3.12 -B scripts/research_package.py --package research/disjoint-tensor-support-masks
python3.12 -I -B research/disjoint-tensor-support-masks/benchmark.py --rounds 5
```

Expected:

```text
PASS_DISJOINT_TENSOR_SUPPORT_MASKS verify_cases=6 mask_cases=7416 certs=4 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/disjoint-tensor-support-masks outcome=completed
PASS_IDENTICAL_DISJOINT_TENSOR_SUPPORT_MASK_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `DisjointTensor(26).verify`
(construction excluded) gave median wall time **1.101 → 0.606 seconds (1.82×)**.
Timing is host-descriptive and is not a correctness gate; all samples and
environment pins are in [RESULT.json](RESULT.json). Every verify receipt matches
the baseline checker fieldwise (`roles`, `additions`, `dag_sha256`, flags).

## Equivalence

Precompute `vertex[p] = OR { 1<<i : input i contains point p }` and
`full = (1<<len(inputs))-1`. For each output mask `T`,

- historical: bits of inputs `S` with `S&T == 0`
- closed form: `full ^ OR_{p in T} vertex[p]`

An input that meets `T` in one or more points is cleared exactly once by the
OR, matching the Boolean filter. An XOR-of-vertex mutant cancels inputs that
meet `T` twice and is rejected by the package controls. Embedding, recurrence
and `dag_sha256` paths are unchanged. Support checks use `require`, so admission
stays enforced under `-O`.

## Open next questions

1. **Question:** Is `DisjointTensor.verify_frames` / `frame_data` worth a
   separate identical-receipt rewrite?
   **Why it matters:** On `h=26`, `verify_frames` dominates the full certificate
   wall time via point-union loops; it is a different object from the verify
   expected-support path measured here.
   **First step:** Profile `DisjointTensor(26).verify_frames` alone and check
   whether ancestor/target-union construction can reuse precomputed incidence
   without changing transition receipts.
   **Blocked by:** Out of this session’s stop rule.

2. **Question:** Should `DisjointTensor.verify`'s `dag_sha256` `json.dumps` path
   get a hand-rolled formatter like the mixed-point / SharedPoint digests?
   **Why it matters:** `json.dumps` is a secondary share of verify after the
   support genexpr; a byte-identical encoder would be a different object.
   **First step:** Profile the post-mask verify residual and compare a
   hand-rolled `[[i,args,str(support)]]` encoder against the committed digest.
   **Blocked by:** Out of this session’s stop rule.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
(ExclusionCircuit leave-two-out / embedding masks on `scripts/exclusion_circuit.py`;
this package rewrites the triple-disjoint expected-support path inside
`scripts/experiments/disjoint_tensor.py` only). No competing open PR on the
`DisjointTensor.verify` support-mask object at refresh.

Douglas R. Colkitt authored the disjoint-tensor compression screen and original
checker. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
