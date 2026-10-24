# Sharper witnesses for #4483: p16 rank `2^1587000000`, native4453 `2^713000000`, p7 `2^2253000000`

**Claim type:** a compiler improvement with certified finite witnesses. **No new κ.** It uses zxv's
[#4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483) theorem unchanged: the adaptive-height
direct compiler with its shifted-logarithmic majorant. It keeps each profile's raw native invoice,
uniform saving and κ, and changes only the free geometry of the witness: `p`, `c`, the height base `M`,
`ℓ₀`, `s`, `λ` and the rational guards.

## Results

| profile | κ (unchanged) | #4483 H | **new H** | exponent ratio |
| --- | ---: | ---: | ---: | ---: |
| p16 (#4470) | 0.00302015 | 2,800,000,000 | **1,587,000,000** | **1.764×** |
| p7 | 0.00268647 | 3,040,000,000 | **2,253,000,000** | 1.349× |
| native4453 (#4453) | 0.00300120 | 1,300,000,000 | **713,000,000** | **1.823×** |
| native4453, matched uniform | 0.00300120 | 4,300,000,000 | **2,580,000,000** | 1.667× |

Here the sufficient uniform rank is `N = 2^H`. Against p16's pre-#4483 rank `2^558100005581`, the new
exponent is about 352× smaller.

The witnesses are `WITNESS-p16.json`, `WITNESS-p7.json`, `WITNESS-native4453.json` and
`WITNESS-native4453-matched-uniform.json`:

| | t₀ | p | c | M | ℓ₀ | s | λ | t_hi | U | V | Q | d | β | η_min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p16 | .99697984 | 3/5 | 400 | 768 | 140 | 3/100 | 3/25 | .9974293 | .9848 | .9609 | 1.0017 | 1.04 | .5632 | .982 |
| p7 | .99731352 | 1/10 | 40 | 288 | 44 | 3/25 | 2/5 | .9976537 | .9436 | .7921 | 1.0012 | 1.72 | .321 | .9845 |
| native4453 (both) | 29909963/30000000 | 2/5 | 200 | 768 | 140 | 1/20 | 3/20 | .9973512 | .9817 | .9417 | 1.0013 | 1.02 | .5743 | .982 |

**Why H drops.** The final funding (17) pays `ln A0 = (1−t₀) ln n₀ − p ln(c + ln n₀)` against
`(z − t₀) H ln 2`. A much smaller ordinary base `n₀ = m·M^{ℓ₀}` shrinks `A0`. Here `n₀` is `145·768^{140}`
instead of `145·1024^{650}` for p16, and `121·288^{44}` instead of `121·256^{100}` for p7. Larger `p`
and `c`, a smaller `s` and a larger `λ` keep the recurrence inequality (20) satisfied at that smaller `ℓ₀`.

## Certification (`verify.py`, two registered commands, about 6 minutes each)

For each witness, separately written code re-certifies every finite gate of #4483's PROOF.md with its own
certified interval arithmetic (from my #4529):

- the guards (18);
- the mirror guard (4) on every window and each of 20 t-slices;
- the recurrence inequality (20);
- the final funding (17).

| | D (lower) | required | worst mirror ratio | τ(n₀) ≤ t_hi | final margin |
| --- | ---: | ---: | ---: | --- | ---: |
| p16 | 0.05144604 | 0.04297994 | 0.56312 | 0.9974292421 ≤ .9974293 | 0.00297292 |
| p7 | 0.02373829 | 0.02336096 | 0.32098 | 0.9976536953 ≤ .9976537 | 0.00011386 |
| native4453 | 0.04714719 | 20/453 ≈ 0.04415 | 0.57424 | 0.9973511396 ≤ .9973512 | 0.00134278 |
| native4453, matched | 0.04714719 | 20/453 | 0.57424 | same | 0.00116679 |

At `H − 10⁶` each witness fails only the final funding, so each H is least at million granularity. Each
witness is also accepted by **#4483's own `compiler.certify`** on main.

## Not covered

- #4483's theorem itself, and its native and outer premises. The consumer points are unchanged because the
  uniform saving is unchanged.
- Global optimality of the geometry. These are scan results, not optima.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/adaptive-witness-retune --check-only
python3.12 -B scripts/research_package.py --package research/adaptive-witness-retune
python3.12 -B research/rank-convergence/compiler.py <profile.json> research/adaptive-witness-retune/WITNESS-p16.json
```

## Open next questions

1. **How far can `H` fall?**
   - *Why it matters:* the exponent of the explicit rank for κ = 0.00302015.
   - *First step:* include `a, b > 1` and non-power-of-two `M`, and optimize `ℓ₀` jointly with the guards.
     The binding constraint is (20) at small `ℓ₀`.
2. **Allowing layer splits `a, b > 1` gives only about 3% more for p16 in a float scan.** The gain comes
   from `n₀`, not from the layer split.

## Credit

- The theorem, the compiler and the baseline witnesses are zxv's (#4483).
- The profiles come from #4470 / #4479 (p16) and the p7 lineage.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
