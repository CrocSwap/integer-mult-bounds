# Exact Gaussian operators and frame-correct data updates

`NativeAlgebra.lean` is a self-contained Mathlib-only toolkit in namespace
`IntegerKappa.Native`. Its 27 theorems apply to arbitrary arrays and arbitrary
dirty values. They give exact sufficient constructions for operator rewrites,
inverse wrappers, literal-family reordering and source/target data adapters.
They do not assert a new numerical kappa or an all-size multiplication theorem.

## Native kernel, including scalar phase

For an additive address group and an address vector `v`, the definitions are

```text
shift v f x       = f (x+v)
step v f x        = ((1+i)/2)*f x + ((1-i)/2)*f (x+v)
inverseStep v f x = ((1-i)/2)*f x + ((1+i)/2)*f (x+v).
```

No scalar phase is quotiented out. `weightedShift_composition` proves the full
two-coefficient composition formula whenever `v+v=0`. Its specializations prove
`step_square`, `step_fourth`, both inverse identities and `inverseStep_eq_cube`.
The construction `stepEquiv v hv` packages the actual positive and inverse
kernels as a complex linear equivalence, and `stepLinear v` supplies a linear
map directly usable by the data ABI below. These are all-input identities;
there is no zero-helper premise or finite basis probe in their statements.

`step_natural`, `inverseStep_natural`, and `step_chart_conjugation` transport the
operators through an actual additive address map or equivalence. The axis on
the other side is the actual image `A v`.

Two more statements handle monomial phases. If `χ(x+v)=χ(x)`,
`step_monomial_natural` commutes the phase through the positive kernel. If
`χ(x+v)=-χ(x)`, `step_monomial_anticommuting` gives the exact formula

```text
step v (χ * (f ∘ A)) = i * χ * ((inverseStep (A v) f) ∘ A).
```

The scalar `i` is part of the conclusion. This is useful when a chart reverses
a direction or an inverse wrapper is assembled: the binary action alone cannot
delete that scalar. With `χ(x)^2=1`, `inverseStep_sign_wrapper` specializes this
to the exact `-i * χ * step v (χ*f)` inverse construction.

The coefficient linearity facts support direct Gaussian-dyadic scalar
programming. `step_commute` and `word_perm` prove exact arbitrary Gaussian-word
reordering, not just equality on a selected input.

## Literal physical-family certificates

An instruction of `familyStep` contains both a family label and an axis.
`familyStep_commute` and `familyWord_perm` prove that permuting these literal
pairs preserves every family stream. A permutation of axis dimensions alone
cannot instantiate the theorem. This gives a reusable sufficient algebraic
assembly step for verified pending-child block reordering.

The theorem does not supply physical time windows, source exclusions, or
inherited phase/translation metadata. A concrete controller must provide those
separately, as in the source-bound owner checks of PR2260. No theorem here
transfers an axis factor to a different physical family.

For the current owner refinement, the scalar/native local word is unchanged;
the new witness changes which exact pending-axis blocks host its complete helper
operations. After the concrete normalizers and direction/unit wrappers identify
the actual pending factors, use `familyWord_perm` separately inside each fixed
child boundary to assemble the assigned blocks with their exact residual suffix.
Use `step_chart_conjugation` with the actual chart, and the monomial lemmas when
its phases require them. Neither statement moves a factor across an inherited
translation or phase boundary. The current finite certificate's improved profile
and its exact numerical saving are checked by the accompanying controller and
arithmetic replays; they are not an additional hypothesis hidden in these
universal Lean lemmas.

## Source and target ABI

For arbitrary linear equivalences `source` and `target`, and a logical linear
operator `U`, the explicit implementable algebraic adapter is

```text
framedKernel source target U = target ∘ U ∘ source.symm.
```

`framedKernel_encoded` proves its action on every source-encoded input.
`framed_add_decode` proves that its scaled accumulation into the actual target
encoding decodes to exactly `y+c•U x`. A common encoding is covered by
`shared_frame_add`. `framedKernel_comp` proves exact cancellation at a shared
intermediate frame, so multiple certified kernels can be assembled without
assuming that unrelated source and target frames coincide.

This interface is useful for source/target frame issues such as the QQ16
bare-data-frame audit in PR2252. To establish an ADD, instantiate the actual
encodings and `U`, then use the displayed adapter. A shared-frame ADD theorem
does not automatically identify two distinct encodings.

`dirty_relay_restoration` proves that the difference of a relay after and before
its update transfers exactly `c•U x` for every initial relay value.
`framed_dirty_relay_restoration` combines that universal cancellation with the
actual source/target ABI. No arbitrary dirty register is silently treated as a
fresh zero register.

## Reuse and verification

The weighted-shift representation and literal-family permutation argument extend
the earlier `SelectiveBorrowing` Factors module supplied with PR2260. Discovery
also inspected the registered Gaussian scalar/lattice modules and the shared
source DAG. The public file repeats only the required small definitions and
their proofs; it imports no personal project module or external solver.

The source was checked with Lean 4.33.0 / Mathlib 4.33.0. All 27 named theorems
receive transitive axiom audits restricted to `propext`, `Classical.choice`, and
`Quot.sound`. Exact kernel checking is the proof evidence; search catalog hits
and source-only indexing are not counted as verification. From a compatible
Mathlib project, run:

```sh
lake env lean research/kappa-lemma-toolkit/NativeAlgebra.lean
```

The module proves operator semantics, not implementations or runtime charges for
arbitrary `LinearEquiv` parameters. To use it in a new kappa construction, give
the concrete chart/native witnesses and their costs, certify the complete owner
and child profiles, and perform the project's retained numerical and analytic
assembly checks.
