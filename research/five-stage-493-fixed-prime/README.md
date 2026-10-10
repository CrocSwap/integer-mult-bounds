# Fixed prime and seven finite levels on PR240's five-stage banks

Conditional κ = **709424410568125629699 / 10^24 = 7.09424410568125629699 × 10^-4**.

That is +3.91 × 10^-12 over PR240 (`28376976266399/(4·10^16)` = 7.09424406659975 × 10^-4). PR240's banked five-stage word, its 493-source helper and all of its checks are unchanged. Only three fixed arithmetic parameters change:

| Parameter | PR240 | This |
|---|---|---|
| Rare-class density in the paid moment | envelope 10^-16 | proved 2m^3/q with the fixed prime q = 2^127 − 1, full 32m^2 fallback still paid |
| Finite ordinary levels | 3 | 7 |
| Outer-47 backoff η (β = 10^-9 unchanged) | 10^-12 | 10^-24 |

The first two are PR235's refinement of PR237 (Gabriele Nespoli), applied here to PR240. The third is new: all 47 strict inequalities and 7 margins of PR234's unchanged assembly still hold at η = 10^-24; it adds about 2.1 × 10^-15 on its own.

## Reproduce

```sh
git worktree add --detach ../pr210 13311491eb74a3a9a443ba4e318c68c263f064f0
git worktree add --detach ../pr234 af3fe331ca60c936229e060681ffccbc1c208678
python3 -m pip install sympy==1.14.0
python3 -B research/five-stage-493-fixed-prime/verify.py --pr210-root ../pr210 --pr234-root ../pr234 [--full]
```

The verifier first runs PR240's own verifier from the same checkout (all F2 and integer columns, telescope, five-stage lowering, geometry, primes, finite bill, 231 charts, 176,915 banks and the 60-colouring) and requires PR240's certificate to be reproduced. Then it:

- bisects the coarse saving `177482012714287685545103/(2.5·10^26)` on the 10^-27 grid with PR234's engine, checks both sides with an independent atanh engine, and checks that the old 10^-16 density fails at this point;
- runs seven acyclic levels from the retained completed saving 384599/10^10, with PR234's cutoff checks;
- runs the outer-47 assembly on the 10^-24 κ grid and rejects the next grid point;
- reproduces PR240's published κ with η = 10^-12 and three levels;
- recomputes the fully paid q-power constant with PR240's fresh finite-bill values (coefficient 62,150,081,742,953,667,360 < 2^80 < q).

About 5 minutes; `--full` also runs PR234's fresh verifier (about 10). `certificate.json` holds the key values and the SHA-256 of the complete recomputed record; `--dump PATH` writes the full record. `Prime.lean` kernel-checks q with mathlib's Lucas–Lehmer theorem (CI job `prime-kernel`).

## Scope

This is a conditional finite certificate with exactly PR234/PR240's hypotheses. The large fixed prime makes initialization and table constants enormous but finite and paid, as argued in PR235's PROOF.md. No construction changes.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
