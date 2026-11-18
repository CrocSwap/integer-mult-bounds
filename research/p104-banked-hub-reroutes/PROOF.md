# Hub reroutes on a banked circuit

## The circuit

Use the banked-transfer reading of #7674 and its successors. Each paid edge `k : A → B` carries a rational linear form. The form is built over the values that are available at chart `A`: independent public inputs whose entrance chart is `A`, and the returned snapshots of earlier paid edges into `A`. Charts act through their canonical Cliffords `T_A`. A paid edge applies `T_B T_A⁻¹` and leaves the normalized signal unchanged. Its job rank is `|dim B − dim A|` for nested charts. A circuit is valid when three conditions hold:

- every scalar read is cocharted;
- the dependency graph is acyclic;
- every public output equals the required normalized value.

For the 400 mains this is the #7669 word's output. For each helper it is its own input.

## One hub reroute

Take a chart `Q` with incoming paid edges `E_in` from one chart `P`, an outgoing paid edge `e₂ : Q → T`, and a chart `R` that `Q` already feeds. Pick `e₁ ∈ E_in`. The reroute does four things:

1. **Re-route `e₁` to `P → R`.** It now carries a value `w₁` available at `P`.
2. **Re-value the other `P → Q` edges.** They carry vectors `U` from the span at `P`. `U` is chosen so that every remaining consumer at `Q` can be recomputed from the retained `Q` values and `U`, up to what its receiver already holds. Each receiver `X` adds back its own local donors: the value it receives may differ from the old one by an element of `V_X`, and `X` restores the old value with a local scalar combination.
3. **Re-value the `Q → R` edges.** They carry vectors `G` in `span(retained Q values, U)`. `R` must be able to recover each old `Q → R` value from `(w₁, G, V_R)`, and so must the old value `v₂` of `e₂`.
4. **Re-source `e₂` as `R → T`.** It sends `v₂` exactly, so `T` is unchanged.

The ranks of `e₁` and `e₂` change from `(a, b)` to `(a', b')`; every other edge keeps its charts. In all 21 reroutes `a + b = a' + b'`, so the rank mass is unchanged and strict concavity of `r ↦ r^{1−κ}` gives the gain. #7682's role-230 change is the case `(P,Q,T,R) = (261, 730, 127, 912)`, with ranks `(3,3) → (4,2)`.

The required vectors were found by a mod-p screen (p = 33554393) over every `(P, Q)` group, in both the forward circuit and its transpose. The transpose reverses the edges and exchanges inputs with outputs; it is the adjoint view used by #7674. Every new form was then solved in exact rationals, and each reroute was accepted only after the whole circuit passed three tests: a cochart and acyclic schedule, GF(2)-nested positive-rank edges, and exact equality of all 1,502 public outputs. In the forward search, new edges are nested pairs. Non-nested candidates such as `912 ↔ 913` have physical rank 2, not 0, and were rejected.

## Physical checks

There are 25 chart pairs that are not MOVEs of the #7669 word. These include the 22 introduced here; the other three already occur in the parent circuits. For each, an exact Gaussian-dyadic state simulation of the canonical-frame circuit of `T_b T_a⁻¹` is run on all 512 basis columns. Every column spreads over exactly `2^r` basis states of equal modulus, with `r = |dim b − dim a|`. Separately, the symplectic rank of every one of the 2,976 transfer pairs equals the dimension difference. The absolute phase of a rank-`r` Clifford job is carried by its monomial adapters, as in the selected framework.

## Exact arithmetic and storage

Coefficient size, the common-root grid, private homes and the term-dependent service changes are in [PHYSICAL.md](PHYSICAL.md).

## Premises

The result is conditional on the five selected-framework assumptions used by #7674, #7682 and #7697:

- uniform native realization at all column multiplicities;
- owned allocation and erasure;
- uniform compiler closure;
- fixed-tape precision and movement;
- analytic recovery.

It also relies on the parent's common-root and banked-storage realization. No new assumption is added.
