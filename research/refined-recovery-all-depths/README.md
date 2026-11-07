# Optimal refined-recovery fiber at every depth t ≥ 27

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped proof with exact finite corroboration; no κ.** This answers open
question 1 of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)
(`research/refined-recovery-longer-chains`, head `b6de532e`): the optimum at
t ≥ 27, which that PR leaves at "strictly larger than F^t". The answer holds
up to a relative factor of 5.5·10⁻⁶, and it fixes the exact tag size.

    13^(8t) / 2^104  ≤  min_U max_y |fiber(y)|  ≤  (1 + 5.46·10⁻⁶) · 13^(8t) / 2^104     (t ≥ 27)

| depth t | 27 | 28 | 29 | 30 | 40 | 100 |
|---|---:|---:|---:|---:|---:|---:|
| optimal tag bits ⌈log₂ OPT⌉ | **696** | **725** | **755** | **785** | **1081** | **2857** |
| identity frames ⌈log₂ A_t⌉ | 796 | 825 | 855 | 885 | 1181 | 2957 |

The optimal tag is ⌈8t·log₂13⌉ − 104 bits for every t ≥ 27. The only possible
exceptions are depths where {8t·log₂13} lies within 7.9·10⁻⁶ of 1; the first such
depth is t = 584,977. Past depth 26, the best mode-preserving frames save exactly
the 104 parity bits of PR6660's dimension cap against the trivial chain count
13^(8t), and essentially nothing more. That is exactly 100 bits better than
identity frames (checked for 27 ≤ t ≤ 400).

**Proof in two lines.**

- *Lower bound, for every frame sequence.* Poisson summation writes the zero
  fiber as a sum of positive terms Π_j 13^(8 − wt h_j). The 2^(r−ρ) characters
  that vanish on the span each contribute 13^(8t), so |fiber(0)| ≥ 13^(8t)/2^ρ
  ≥ 13^(8t)/2^104. Informally, the zero target receives at least its average
  share of all chains.
- *Upper bound.* Take #6828's FRAMES27 (rank 104, ε₀ = 5.45·10⁻⁶) and repeat the
  last frame (U_j = I). Appending stages inside the span can only lower ε₀. Then
  #6848's theorem (max fiber = zero fiber when ε₀ ≤ 4.2·10⁻⁴) gives
  max_y = |fiber(0)| ≤ (1+5.46·10⁻⁶)·13^(8t)/2^104.

**What this implies for #6828.** The main term beats #6828's AM–GM floors for
t ≥ 28. Its balanced E-valued patterns would give zero fibers *below* 13^(8t)/2^104
there, so they are not realizable.

See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-all-depths/verify.py
python3.12 -I -O -W error -B research/refined-recovery-all-depths/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-all-depths
```

Each run prints `PASS_REFINED_RECOVERY_ALL_DEPTHS` in about one second. It
checks:

* C and the coset sums from the pinned matrix, and ŵ(h) = 13^(8 − wt h) for all
  h ∈ C;
* the Poisson identity, the main-term bound and monotonicity of ε₀, exactly, on
  twelve random small instances;
* θ exactly, and θ < ε*/75;
* the exact tag bits and the 100-bit saving with big integers for 27 ≤ t ≤ 400;
* the first possibly ambiguous depth, by a 60-digit scan up to 600,000;
* RESULT.json.

## Limitations

The upper bound relies on two packages that are open and unmerged, and does not
replay either:

* #6828, for the FRAMES27 value and rank;
* #6848, for the max-fiber theorem.

Like those packages, it also cites PR6660's chain bijection and dimension cap,
and PR6327's box facts. Neither fork commit is reachable here, so SOURCES.json
does not pin them. The exact value of OPT(t) for t ≥ 28 is pinned only to the
relative window 5.46·10⁻⁶, not exactly. The tag size is ambiguous at sparse
depths, the first being t = 584,977. The package supplies no codec, physical tag,
caller or restoration cost. κ, the selected frontier and its five assumptions are
unchanged. No independent human or proof-kernel review is claimed.

## Open next questions

1. **Exact OPT(t) at t ≥ 28.** Minimize ε₀ = Σ 13^(−wt) over the 104-dimensional
   character codes realizable by frames. This is a weight-enumerator problem for
   a code inside C^t.
2. **Faster convergence.** Since ε₀(t) is non-increasing, how fast can it go to
   0? A random-code heuristic suggests 2^(104−4t)·(16F/13^8)^t.

## Credit

Nick Petalas's PR6660 supplies the chain bijection, the dimension cap and the open
question. CubeJerry's PR6327 supplies the chain model, F and A_t. zxv's #5444
supplies M. #6828 supplies FRAMES27 and #6848 the max-fiber theorem. Poisson
summation is classical.
