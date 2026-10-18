# Lean audit of the common-label tensor lift

The same well-labelled role program lifts to every finite column set when
its **unary labels and recipes** are tensored and its **role coefficients**
are retained once. This package kernel-checks that conditional implication
on the unchanged `LemmaG.Stream` semantics, including ADD, SCALE, COPY,
CLEAR, and arbitrary dirty inputs. It independently formalizes the tensor
step already argued in [PR2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287),
sections 2 and 4. It does not claim a new tensor identity or certify that
PR's entire layer implementation.

## Exact statement

Let `K,R` be commutative semirings, `φ : K →+* R`, `ι` a finite role set,
`J` a finite column set, and `M_j` an `R`-module. For every label `A` and
column `j`, supply an invertible `R`-linear map `T_j(A)` and an `R`-linear
recipe `rec_j(A,B)`. Let `es` be one fixed `K`-coefficient role program.
Assume:

1. `es` is `Stream.WellLabelled` at the initial labels. ADD uses equal
   current labels and COPY uses its source's declared label.
2. For every relabel event actually in `es`, every column and every vector,
   `rec_j(A,B)(v) = T_j(B)(T_j(A)^-1(v))`.

Define `T(A) = ⨂_j T_j(A)` and `rec(A,B) = ⨂_j rec_j(A,B)`, over `R`.
`conjugation_extended` proves, for **every** role input `h`:

```text
physRun(rec, mapEvent φ es, h)[r]
  = T(final_label[r]) (Σ_s φ(S(es)[r,s]) • T(initial_label[s])^-1(h[s])).
```

`S` is the original Lemma G scalar shadow, including COPY and CLEAR.
`Coefficients.shadow` proves the coefficient embedding commutes with the
entire ordered shadow program. Rational role scalars can thus be embedded
in `ℂ` once while the address tensor is taken over `ℂ`; taking that tensor
over `ℚ` is not an implicit step of this statement.

`unit_row_extended` gives the uncontaminated unary endpoint for any output
whose original shadow row is its unit row. Other initial roles may be
arbitrarily dirty. This row conclusion alone does not claim that its input
column is zero in other outputs.

The proof first establishes equality of **linear maps** for tensor recipes
using Mathlib's tensor universal property, then applies the original
`Stream.conj_matrix`. The input is never assumed decomposable. For finite
coordinate sets `A_j`, `coordinates` explicitly identifies

```text
⨂[R] j, (A_j → R)  ≃ₗ[R]  (((j : J) → A_j) → R).
```

`coordinates_surjective` and `coordinates_tprod` prove this is the full
array space and agrees with the coordinate product on pure tensors.
Transporting the displayed run identity through this linear equivalence
gives its full-array interpretation. No independence across columns,
helpers or live families is needed.

## Boundary witnesses and finite replay

`Counterexamples.lean` proves that the one-role word SCALE(2), followed by
the unary recipe `(1/2)I`, is the identity in one column but becomes `(1/2)I`
in two columns when the role coefficient remains 2. Its scalar shadow is
2, not a unit row. A bare one-column physical endpoint therefore cannot
replace the quantified common-label/recipe hypotheses.

Other kernel-checked witnesses distinguish a role SCALE(-1) from the unary
tensor phase `(-1)^2`, reject tensoring a sum-of-operators identity, and show
that the 2-by-2 diagonal array cannot be a pure rational tensor. These are
failures of proposed shortcuts, not defects asserted against PR2287.

The separate standard-library Gaussian-rational replay runs a 19-event,
four-role word with noncommuting, column-dependent 2-by-2 labels, unary
`i` phases, dyadic scalars and dirty private input. Literal execution uses
Kronecker products of unary recipes; the endpoint oracle uses elementary
role-matrix products and direct coordinate products. Widths 0–4 cover
124 full basis inputs, 20 dense inputs, and 100 program prefixes. Eleven
controls detect tensoring role coefficients, dropping unary phases,
reversing recipe composition, destructive COPY, omitted CLEAR, three
invalid label cases, and three endpoint/sign/sum shortcuts.

This finite experiment diagnoses the definitions. The all-width assertion
is the Lean theorem, not extrapolation from the finite replay.

## Reproduce and evidence

From the repository root, the registered Python 3.12 replay checks source
bindings, exact finite receipts and eight groups of failure controls:

```sh
python3.12 scripts/research_package.py --package research/lean-common-label-tensor-lift
```

It reports `kernel_checked=false`. To run Lean explicitly:

```sh
python3.12 -I -O -B research/lean-common-label-tensor-lift/verify.py \
  --lake /absolute/path/to/lean-4.33.0-rc1-linux/bin/lake \
  --work-dir /tmp/common-label-tensor-fresh-build \
  --fetch-cache --out /tmp/common-label-tensor-result.json
```

The build and output paths must not exist. Alternatively pass `--packages`
with an existing package cache instead of `--fetch-cache`. The harness
checks the actual Lean version/commit, every dependency Git revision and
tracked-source cleanliness, then builds local proofs in a fresh directory.
It audits all 21 named theorem targets, accepting only `propext`,
`Classical.choice` and `Quot.sound`; three deliberately false proofs must
fail in Lean on their mathematical goals. It uses no `sorry`, custom
axioms, `native_decide`, or externally evaluated proof admission.

Lean `4.33.0-rc1` (`62eed1db4d67327ec8120be05f1a1b0847d74561`) and Mathlib
`55b7917b472489c7c56a0fa6393af05cfd536599` are pinned in
[PROOF-SOURCES.json](PROOF-SOURCES.json) with all dependency commits.
[KERNEL.json](KERNEL.json) records the actual local kernel run;
[FINITE.json](FINITE.json) records the finite oracle. The dedicated
`lean-common-label-tensor-lift.yml` workflow runs the explicit kernel mode.
Hosted CI status is separate from these local receipts. The unchanged
upstream Lemma G file emits unused-simp warnings on this toolchain.

## Source boundary and scope

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. The OS-random assignment was `uniform-transfer-audit`, seed
`4a3cc8c48a6df8825159187df733f074`; the refined question is recorded in
[TASK.json](TASK.json). [SOURCES.json](SOURCES.json) pins the unchanged
main Lemma G semantics and notice as live inputs. The copied PR2287 proof
and notice are byte-exact at `8c60765b5dea9d862b3b190d55da102a576031bf`.
Only its common-label tensor argument is audited here.

This is a conditional semantic bridge. It does not establish that a
specific R480 native recipe implementation satisfies the hypotheses,
rerun the 24,767-event words or selected cold replay, certify current
hosting/caller chronology, or prove recursive row allocation, tape cost,
precision, FFT error transfer or integer packing. The selected frontier
and κ are unchanged. PR2284's height recurrence, the Gaussian-parity
packages and PR2298's outer composition address different obligations;
none is claimed as new work here.

## Open next questions

1. Instantiate this theorem with the current serialized R480 event stream
   and exact unary recipe certificates. This connects the implication to
   the selected source, including private-role typing. Start by generating
   Lean events and label obligations from one pinned orientation; the
   blocker is a source-faithful formal importer and native recipe
   representation, not another small-width matrix replay.
2. Bind the physical tensor-recipe interpreter to `PiTensorProduct.map`,
   including unary phase powers and restored spectators. Start with one
   PR2250 directed monomial adapter and prove its coordinate action. The
   theorem assumes that linear recipe; it does not certify the tape
   interpreter implementing it. Neither question changes κ alone.

Structured first steps and blockers are also in [TASK.json](TASK.json).

## Credit

Gareth Davidson (`bitplane`) prepared this independent formal audit with
substantial OpenAI Codex assistance. No independent human review or
sub-agent work is claimed. New material is Apache-2.0.

Jose Manuel (`jmbarrancoml`, with OpenAI Codex) supplied PR2287's written
lifting argument. DreamingOfClouds (with Claude Opus 5.5 / Claude Code)
supplied the unchanged Lemma G formalization; its lineage includes Zhihao
Chen / jacklightChen (PR425), chafreaky (PR458), Dugongue (PR471), and
jamesyc's package/axiom conventions (PR487/488). Mathlib supplies the tensor
construction, map extensionality and basis equivalence. The fresh-build
harness is adapted from our PR2295, not presented as a new verification
method. Original notices are retained under `sources/`; their references
describe their original packages, not new dependencies whose complete
claims were verified here.
