# New conditional κ constructions, 4 November 2026

The new complete complex construction gives **conditional κ = 0.00330720**, an increase of **0.00000300** (about **0.09079%**) over the independently replayed **0.00330420** in [PR6716](https://github.com/CrocSwap/integer-mult-bounds/pull/6716).

A separate integral transfer improves the **ordinary BIT saving to 0.00376669**. This is **0.00001671** above the first qualified BIT result of this session, 0.00374998, and **0.00002212** above the original R091 ordinary BIT bound 0.00374457. The BIT number is a dependency bound; it is not the overall multiplication κ.

All results retain the same five assumptions: **native_all_columns, owned_erasure, compiler, precision_tape, analytic_recovery**. They do not assert an unconditional theorem, scientific admission, a materialized enormous uniform multiplier, or a change to the repository's selected frontier.

## What changed

A paid common-idle job can be fragmented to expose an earlier independently productive output. The extra paid call is essential and is included. On the exact two-pair root, two rank-41 targets become independent ranks 32 and 9, while their paid rank-40 idles become paid ranks 32 and 8. The signed gain is

```
208 * ((H9-H8) - (H41-H40)) > 0,    H(r)=r^(1-κ).
```

The inequality is strict because concave power increments decrease. The six child sizes are (4,4,1,1,4,4); all 18 native calls, 15 thin queries, binary idles, helper targets and ordinary work are included. The literal caller has 34 arbitrary independent inputs and 606 instructions. Two coefficient engines check every one of its 1,156 forward and reverse coefficients. Its complete invoice has 13,670 productive fields, 66,852 paid requests and rank-mass surplus 760. Two rational interval engines certify the raw crossing in (0.0033072446848, 0.0033072446849); the stated κ leaves a strict compiler and transfer gap.

The same caller has integral unimodular bases. After simplifying λ=1 in q²=1, its integer identity reduces legally modulo two and transfers to the actual BIT source. This is not reduction of a dyadic denominator modulo two. The binary caller has 34 arbitrary independent inputs and 356 instructions; all 1,156 forward and reverse coefficients pass. Its raw crossing is in (0.0037667234775, 0.0037667234776). Finite admission and two full ordinary-wrapper steps, with atom retuned to 0.004, establish ordinary saving 0.00376669.

## Read the evidence

- [Complex proof](two-fragment/PROOF.md), [complete certificate](two-fragment/RESULT.json), [literal caller](two-fragment/CONTROLLER.json), [independent algebra receipt](two-fragment/INDEPENDENT.json).
- [BIT proof](bit/FRAGMENT-PROOF.md), [complete certificate](bit/FRAGMENT-BIT-ADMISSION.json), [literal binary caller](bit/FRAGMENT-CALLER.json.gz).
- [First paid-fragment proof](fragment/PROOF.md) explains the general dual-pair construction and its exact dyadic witness. The admitted 17-stage intermediate is in [fragment17](fragment17/PROOF.md).
- [Research conclusions](RESEARCH-NOTES.md) record the principal paying insight, the saturated query budget and precisely scoped negative tests. Pilot scripts remain in the surrounding task directory; this bundle contains the inputs required for the claims.

## Reproduce

The claims were replayed in disposable copies under Python **3.11.11** and **3.14.5**, using only the standard library. From this directory:

```sh
python3 -I -B verify_bundle.py
```

The runner authenticates every bundled byte, makes a temporary copy, verifies the complete changed complex caller/physical maps/invoice/compiler/outer ledger, then replays both new BIT admissions. It compares the mathematical receipts while ignoring runtime-only `seconds` fields and compression-only hash differences after comparing the complete decompressed caller. Original files remain unchanged. Native proof evidence is reused from the once fully replayed, hash-bound unchanged supplier; it is not rerun by default.

To additionally repeat the original full unchanged native-source replay:

```sh
python3 -I -B verify_bundle.py --full-native
```

The full native replay was completed during the session; the optional export command is supplied for reviewers. No historical Lean or Docker suite is needed. Successful logs are retained in [validation](validation/); log paths quoted in the original frozen construction proofs refer to those retained logs. The small additional proof checks are `python3 -I -B allocation_tail.py` and `python3 -I -B internal_prefix_lemma.py`.

## Source and credit

The mathematical baseline is exact PR6716 commit `a467457692bc9e11113d9b2e2e34ea8ffb553b58`, with its complete 45-file inventory in [LOCAL-PINS.json](sources/pr6716/LOCAL-PINS.json). It embeds the exact PR6702 source, commit `edd6a37a9ff87b254fb7466184348d1432d0c8c0`. Original notices and licences remain intact. The new paid-fragment construction, integral transfer and this research session were developed with OpenAI Codex for [zxv](https://github.com/zxv).

The final upstream refresh at 21:42 UTC found no newer κ claim. PR6716 had added independent application evidence at head `4a40713f10d47da5894d7673eb6d0ab2ebdf0687`; its construction, caller, root, pricing and result files remained unchanged. [PR6720](https://github.com/CrocSwap/integer-mult-bounds/pull/6720) independently audits the predecessor's cut and 35-input caller. Those later reviews do not constitute independent review of this new construction.
