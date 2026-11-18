# Causal helper splits on a banked circuit

## The circuit and the parent

The banked-transfer reading of #7674 is used throughout. Each paid edge `k : A → B` carries a rational linear form. The form is built over the values available at chart `A`: independent public inputs entering at `A` and returned snapshots of earlier paid edges into `A`. A paid edge applies `T_B T_A⁻¹` and leaves the normalized signal unchanged. A valid circuit has cocharted reads, an acyclic dependency graph, and the required public outputs. Each of the 400 mains must equal the #7700 word's output, and each helper must return its own input.

The parent is #7708, rebuilt by our own code. We fold the authenticated #7700 word, apply the #7704 relay, then apply the 46 published #7708 cuts in order. That reproduces its κ crossing 0.00374039009047.

## One split

Let `G` be the 615 helper roles that enter at chart `E = 3` and exit at chart `X = 127`. In normalized coordinates each returns its own input. Pick a chart `C` with `E ⊂ C ⊂ X` (strictly nested). At `C` choose:

- a set of **prefix** values `A`: the arrivals at `C`, and the inputs entering at `C`, that do not depend on the departures chosen next;
- a set of **departures** `Dp` from `C`.

We need a functional `ℓ` that is a rational combination of the values in `A`, supported only on the inputs of `G`. We also need an output direction `v`: the change in all public outputs caused by adding fixed multiples `c_k` of one new array to the departures `k ∈ Dp`. It must be supported only on the outputs of `G`, with `ℓ(v) = 1`. Choose a role `r ∈ G` with `ℓ_r ≠ 0`.

The construction has four steps:

1. **Encode the inputs.** The group inputs at chart 3 are re-encoded as `x_j = u_j + v_j u_r` for `j ≠ r`, and `x_r = v_r u_r − Σ_{j≠r} ℓ_j u_j / ℓ_r`. Then `ℓ(x) = u_r`, and the encoding is invertible for arbitrary arrays.
2. **Retire role `r` at `C`.** Its output is the prefix combination `ℓ(x) = u_r`, which is available at `C`.
3. **Add a fresh role `n` entering at `C`.** Add `c_k (g − ℓ(x))` to each departure `k`, where `g` is the new input. Linearity gives the old exit fields `y = x + v(g − u_r)`.
4. **Decode at chart 127.** The fresh output is `ℓ(y) = g`, and each other helper outputs `y_j − v_j ℓ(y) = u_j`.

The mains never see the change, because `v` vanishes outside `G`. Role `r` now pays rank `dim C − dim E` and the fresh role pays `dim X − dim C`, in place of one rank-9 target. The gain is `f(d) + f(9 − d) − f(9)` with `f(r) = r^{1−κ}`, which is strictly positive by concavity.

A mod-p screen over every chart and every departure cut found exactly three charts on this circuit: 498 (4 | 5), 480 (2 | 7) and 595 (1 | 8). The same screen finds exactly #7697's chart 595 on the #7682 circuit. Each split was rebuilt in exact rationals and accepted only after the whole circuit passed four checks: schedule, nesting, equality of all mains with the word, and every helper being the identity. The rescreen after the three splits finds no further split.

## Exact arithmetic and storage

Coefficient size, the common-root grid, private homes and the service bills are in [PHYSICAL.md](PHYSICAL.md).

## Premises

The result is conditional on the five selected-framework assumptions used by #7674, #7682, #7697, #7704 and #7708:

- uniform native realization at all column multiplicities;
- owned allocation and erasure;
- uniform compiler closure;
- fixed-tape precision and movement;
- analytic recovery.

It also relies on the parent's banked-storage and common-root realization. No new assumption is added.
