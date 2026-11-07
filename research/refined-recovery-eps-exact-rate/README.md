# Refined recovery: ε_t decays at exactly 4·log₂13 bits per stage

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped proof with exact finite corroboration; no κ.** This answers open
question 1 of [#6851](https://github.com/CrocSwap/integer-mult-bounds/pull/6851).
That PR showed the second-order term ε_t of

    OPT(t) = 2^(−104)·13^(8t)·(1 + ε_t)

decays at between 4.0 and 14.8 bits per stage. Here:

    lim_{t→∞} −log₂ ε_t / t = 4·log₂13 ≈ 14.8018

So the Jensen lower bound of #6851 gives the true rate.

**How.**

- *#6851's gap.* The first-moment bound there was dominated by rare characters χ
  whose total weight W(χ) is near 0.
- *Concentration.* In PR6660's frame family with random ψ_j, each W(χ) is a sum of
  t − 1 independent weights of uniform words of C, with mean 4.
- *Union bound.* A Chernoff bound P(W < w) ≤ r^(−w)·m(r)^(t−1), with
  m(r) = (1+14r⁴+r⁸)/16, combined with a union bound over the 2^104 characters,
  yields frames in which every χ has W(χ) ≥ w_t. Then S ≤ (2^104−1)·13^(−w_t).
- *Limit.* Cramér's theorem gives w_t/t → 4.

| t | 60 | 100 | 200 | 400 | 1000 |
|---|---:|---:|---:|---:|---:|
| w_t / t | 1.33 | 2.00 | 2.66 | 3.09 | 3.44 |
| log₂ ε_t ≤ | −192 | −636 | −1865 | −4470 | −12640 |
| log₂ ε_t ≥ (Jensen) | −784 | −1376 | −2856 | −5817 | −14698 |

See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-eps-exact-rate/verify.py
python3.12 -I -O -W error -B research/refined-recovery-eps-exact-rate/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-eps-exact-rate
```

Each run prints `PASS_REFINED_RECOVERY_EPS_EXACT_RATE` in about 30 s. It checks:

* the weights of C, and that m(1/13) equals #6851's q;
* the exact rational Chernoff certificates for every tabulated t, with the
  largest admissible w_t;
* the Cramér certificates for slopes 3, 3.5, 3.9 and 3.99;
* the control that no certificate exists at slope 4.

## Limitations

The result cites PR6660's frame family, #6848's max-fiber theorem, and the
Poisson identity and Jensen bound of #6849 and #6851. All are unmerged, and none
is replayed here.

The upper bound is existential, from a union bound, and the convergence of the
rate is slow. For t < 60 the bound of #6851 is better.

The package supplies no codec, physical tag, caller or restoration cost. κ, the
selected frontier and its five assumptions are unchanged. No independent human or
proof-kernel review is claimed.

## Open next questions

1. **Second-order constant.** Determine lim (−log₂ε_t − 4t·log₂13), or at least
   the √t-order correction from the Chernoff gap.
2. **Explicit frames.** Find explicit near-constant-weight character codes, for
   example from a Singer cycle of GF(2^104) restricted to a subgroup orbit.

## Credit

Nick Petalas's PR6660; CubeJerry's PR6327; zxv's #5444; #6848, #6849 and #6851.
Chernoff and Cramér bounds are classical.
