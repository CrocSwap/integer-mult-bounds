# Grade-14 paid cuts for conditional integer multiplication

The two finite application checks give **κ ≥ 0.00387992802601** for the construction in #7831 under its five framework premises. The gain over the open predecessor is **0.00000000000095**. The repository’s maintainer-selected result has a separate review process.

Use 832 tensor factors, split paid ranks at 14^832, and retain productive ranks at or above 16^832. A homogeneous grade-14 paid tuple now fits in one call. Applying the predecessor's cutoff base 10 at the same power would require ceil(14^832 / 10^832) calls. The charged source words and the rational caller are inherited. This trades a larger tensor and a larger uniform threshold for a small improvement in the exponent.

At trial 0.003879928046104 the price checker and the independent interval implementation both bound the paid moment, paid tail and discarded target tail. Their outward caps are 499999999999967/500000000000000, 175703845856227/200000000000000 and 29486835542931/31250000000000. The normalized strict surplus exceeds 0.000000000054911999. On the full ambient 134^832 the shifted-log factor is 20/21, the logarithm power is 325, and log₂ N is 1642800000000000. Both inherited uniform and delayed losses are 1/10¹¹. Four strict stock stages admit ordinary BIT saving 0.003879928026095. The expanded rational caller and its independent audit agree on the advertised bound across 54 strict and four functional checks.

The five premises are native_all_columns, owned_erasure, compiler, precision_tape and analytic_recovery. Lean checks the exact rational separation and cutoff comparison. The full finite replay also verifies the 12 explicit inputs, 127 inherited sources, both native words and the application charges. The Lean file covers the stated arithmetic lemmas.

## Reproduce

From this directory, use CPython 3.12 and a fresh output directory. The fetch step downloads pinned public inputs and verifies their hashes. A populated source cache can be replayed offline by omitting the fetch flag.

```sh
python3.12 -IB verify.py --work inputs --out replay --fetch
lean Grade14.lean
cmp RESULT.json replay/RESULT.json
cmp BIT.json replay/BIT.json
cmp AUDIT.json replay/AUDIT.json
```

The Lean replay used Lean 4.34.1. The strict separation lemma uses propext, Classical.choice and Quot.sound. The cutoff comparison is axiom-free.

## Open next questions

The unchanged signed BIT crossing is below 0.003879928046155. A substantially higher exponent calls for a new BIT profile. A practical first experiment is to audit a multi-coordinate helper projection with shared endpoints and replay all bridge and cleanup charges in both orientations.

## Credit

Submitted by [@RohanArun](https://x.com/RohanArun) through [the original X request](https://x.com/RohanArun/status/2123655584797143516). Codex performed the schedule experiment, finite replays and Lean check. Dugongue and contributors supplied the preceding verifier, tensor estimate and caller. The Apache-2.0 predecessor code and attribution are retained. [PR #7831](https://github.com/CrocSwap/integer-mult-bounds/pull/7831) · [PR #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) · [PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786) · [Predecessor notice](https://github.com/CrocSwap/integer-mult-bounds/blob/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/NOTICE)
