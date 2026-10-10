# Fixed prime and seven finite levels on PR249's source527 banks

Conditional κ = **142078438070175647403 / (2·10^23) = 7.10392190350878237015 × 10^-4**.

That is +3.90 × 10^-12 over PR249 (`88799023305857/(1.25·10^17)` = 7.10392186446856 × 10^-4). PR249's word, banks and every one of its checks are unchanged. Only three fixed arithmetic parameters change:

| Parameter | PR249 | This |
|---|---|---|
| Rare-class density in the paid moment | envelope 10^-16 | proved 2m^3/q with the fixed prime q = 2^127 − 1; the full 32m^2 fallback is still paid |
| Finite ordinary levels | 3 | 7 |
| Outer-47 backoff η (β = 10^-9 unchanged) | 10^-12 | 10^-24 |

The first two are PR235's refinement (Gabriele Nespoli), applied here to PR249. All 47 strict inequalities and 7 margins of the unchanged outer assembly still hold at η = 10^-24.

## Reproduce

```sh
python3 -m pip install -r research/five-stage-source527-entrances-fixed-prime/requirements.txt
python3 -B research/five-stage-source527-entrances-fixed-prime/verify.py --output /tmp/pr249-run
```

The verifier first runs PR249's own immutable verifier from the same checkout into a new directory (all eight mandatory stages and the package integrity check) and requires PR249's κ. Then it:

- bisects the coarse saving on the 10^-27 grid with PR249's engine, checks both sides with the independent atanh engine, and checks that the old 10^-16 density fails at this point;
- runs seven acyclic levels from the retained 384599/10^10, each with PR249's cutoff rule at its fully charged q-power coefficient (< 2^80 < q);
- runs the outer-47 assembly on the 10^-24 κ grid and rejects the next grid point;
- reproduces PR249's published κ with η = 10^-12 and three levels.

`--pr249-output DIR` reuses a finished PR249 run. `certificate.json` holds the key values and the SHA-256 of the complete recomputed record; `--dump PATH` writes the full record. `Prime.lean` kernel-checks q with mathlib's Lucas–Lehmer theorem (CI job `prime-kernel`).

## Scope

This is a conditional finite certificate with exactly PR249's hypotheses. The large fixed prime makes initialization and table constants enormous but finite and paid, as argued in PR235's PROOF.md. No construction changes.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
