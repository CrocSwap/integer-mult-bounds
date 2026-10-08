# Conditional 373/10^11 > 2^-28 witness

This contribution is based directly on `main`. It imports the necessary
PR #3 and PR #5 dependencies with attribution; it is not a PR against either
contributor's branch. The pinned `upstream/` source remains unchanged.

The new scalar interchange motif uses F3 and five-subsets of 28 points. Its
weighted triple-exclusion producer retains pair totals and resynthesizes all
common-four-point stars. Independent exact support enumeration and template
verification give a role upper bound of 11,840,940 and interchange saving
`3/400000000 = 7.5e-9`. A new paired disjoint-triple producer, using PR #3's
binary phase labels and PR #4's bank-sharing argument, gives complex saving
`39/10^9`. PR #5's fast resampling then supports the exact conditional bound
`kappa = 373/10^11 = 3.73e-9 > 2^-28`.

The minimum final margin is `934813/250000000000000`; its strict gap over
the declared kappa is `2313/250000000000000`. These are asymptotic exponent
comparisons, not practical benchmarks or a full formalization.

## Reproduce

```sh
python3 scripts/prime_field_network.py
python3 scripts/make_prime_field_patch.py
make verify
make prime-field-note
```

The producer requires Python's standard library, a C++17 compiler, roughly
1.2 GB memory and under 30 MB temporary storage. No large generated DAG,
binary executable, network access or external optimization solver is needed.
The compact templates are regenerated deterministically. C++ hash tables
use full equality checks on exact source-support keys.

## Proof and checks

- [Construction note](../../notes/prime-field28-construction.tex) and
  [PDF](../../artifacts/prime-field28-note.pdf).
- [Exact certificate](../../certificates/prime-field28.json).
- [Pinned-source patch](../../patches/prime-field28.patch).
- Full local output coefficients, all global support equalities and all
  replacement boundary sums are checked. Every replacement addition has
  disjoint support. The common-pair identity proves positive definiteness
  for every rational node label, including replacement nodes.
- All 98,280 matching images are distinct and meet their source in two points.
- At h=8, all 1,156 scalar basis inputs, including dirty scratch, are tested;
  both rational frame directions are checked exactly.
- The h=28 complex circuit is checked for every coefficient, binary label,
  injection residual and compiled role in both orientations.
- Negative controls reject the uncompressed stars, old center losses,
  weaker complex saving, invalid guard and an oversized headline exponent.

Publication checks: all **188 tests** and **20 independent patch checks** pass.
The six-page note and 89-page patched manuscript compile with pdfLaTeX;
the manuscript has no undefined references or duplicate internal labels.
The imported PR #3/#5 files are byte-identical to the attributed source commit.

The general tensor-stage argument, finite-alphabet tape transfer, retained
analytic interfaces and rounding are written proof obligations. Finite tests
are not represented as formal verification of the multiplication theorem.

## Attribution

New construction: **Zhihao Chen (jacklightChen)**, with substantial
**GPT-6 Astra (OpenAI Codex)** assistance, as identified by the contributor.
This records the first submission of this specific construction by these
contributors to this repository, not a claim of worldwide priority.
Follow-on research using this construction should explicitly acknowledge
Zhihao Chen and cite this note and PR. Retain all earlier attribution.

The inherited compact-control framework is by Douglas Colkitt; aligned
pairing is also developed in [PR #2](https://github.com/CrocSwap/integer-mult-bounds/pull/2).
Eumemic's Claude-assisted [PR #3](https://github.com/CrocSwap/integer-mult-bounds/pull/3)
and [PR #5](https://github.com/CrocSwap/integer-mult-bounds/pull/5) supply the
complex interface and fast Gaussian resampling. Retained totals and stage
sharing are developed in dleen's [PR #4](https://github.com/CrocSwap/integer-mult-bounds/pull/4);
eumemic's [PR #6](https://github.com/CrocSwap/integer-mult-bounds/pull/6) also
uses cheaper retained centers. The new contribution is the F3 five-subset
motif, paired degree-three recursion, four-point-star resynthesis, stronger
paired complex producer and their improved composition.
