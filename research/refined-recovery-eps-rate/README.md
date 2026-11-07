# How fast the refined-recovery optimum approaches 13^(8t)/2^104

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped proof with exact finite corroboration; no κ.** This answers open
question 2 of [#6849](https://github.com/CrocSwap/integer-mult-bounds/pull/6849):
how fast the second-order term ε_t can go to 0, where

    OPT(t) = 2^(−104)·13^(8t)·(1 + ε_t)       (t ≥ 29).

**Theorem.** For every t ≥ 29,

    (2^104−1)·13^(−4t·2^104/(2^104−1))  ≤  ε_t  ≤  (2^104−16)·q^t + 14·13^(−4t) + 13^(−8t),   q = (1+14·13⁻⁴+13⁻⁸)/16,

so ε_t decays at between **4.0** and **14.8 bits per stage**. At t = 29 the upper
bound is 2.48·10⁻⁴. [#6850](https://github.com/CrocSwap/integer-mult-bounds/pull/6850)'s
periodic frames give a decay of about 0.57 bits per stage; this bound gives 4.

| t | 29 | 30 | 40 | 60 |
|---|---:|---:|---:|---:|
| log₂ upper bound on ε_t | −11.98 | −15.98 | −55.97 | −135.96 |
| log₂ lower bound on ε_t | −325.3 | −340.1 | −488.1 | −784.1 |

**Why.**

- *Upper bound.* In PR6660's frame family W_j = I + V_jE, the stage maps are
  φ_j = μ + ψ_j. Here ψ_j ranges over all linear maps Q → R′, a 100-dimensional
  complement of im μ in the 104-dimensional V. Averaging S = Σ_{χ≠0} Π_j 13^(−wt)
  over uniformly random ψ_j gives exactly the formula above. So some frames, and
  in fact at least half of them up to a factor 2, achieve it. Since this is below
  #6848's threshold, their max fiber is their zero fiber.
- *Lower bound.* Every stage map is injective, so each χ ↦ χ∘φ_j hits every word
  of C equally often. The average total weight is therefore 4t, and Jensen gives
  the bound.

See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-eps-rate/verify.py
python3.12 -I -O -W error -B research/refined-recovery-eps-rate/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-eps-rate
```

Each run prints `PASS_REFINED_RECOVERY_EPS_RATE` in under a second. It checks:

* that dim R′ = 100 and dim(im μ + R′) = 104, from the pinned M;
* that η maps onto C;
* the first-moment formula, by exact full enumeration in toy dimensions;
* the Jensen weight identity on random toys;
* that E_t < ε* for 29 ≤ t ≤ 60, with E_28 > ε* as a control;
* the decay rates.

## Limitations

The result cites PR6660 (dimension cap, frame family), #6848 (max-fiber theorem)
and #6849 (Poisson identity). These are open and unmerged, and are not replayed
here.

The upper bound is existential. It comes from a first moment and supplies no
explicit frames beyond t = 27. The gap between 4.0 and 14.8 bits per stage
remains open. At t = 28 the first moment exceeds the threshold, and #6850
covers that depth instead.

The package supplies no codec, physical tag, caller or restoration cost. κ, the
selected frontier and its five assumptions are unchanged. No independent human or
proof-kernel review is claimed.

## Open next questions

1. **Exact rate.** Is the true decay rate 4 bits per stage? A Delsarte-style
   linear-programming bound on S, or structured codes (the per-stage maps form an
   F2-linear code over GF(16)-sized blocks), should decide it.
2. **Explicit frames.** Give explicit near-optimal frames for t ≥ 29, for example
   with algebraic-geometry codes.

## Credit

Nick Petalas's PR6660 (frame family, dimension cap, the question); CubeJerry's
PR6327; zxv's #5444; #6848, #6849 and #6850. The first-moment and Jensen
arguments are classical.
