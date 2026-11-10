# No-edge irreducible joint image

**Result.** For a complete no-edge pool of binary rank-one idempotents whose
off-diagonal patterns span a space of dimension at most 3, the joint image is
either of dimension at most 3, or of dimension 4 and reducible. Dimension 3
is sharp at every ambient width. **No new κ.** The selected value remains
`781451/250000000`.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status: **changed**. The card
asks for a new register alphabet. This package answers the scalar question left
open by #6838: can such a pool act irreducibly on a four-dimensional joint
image? It cannot. The reason is recorded in [TASK.json](TASK.json). The
original native acceptance gate is unmet, and the selected frontier is
unchanged.

[PROOF.md](PROOF.md) is the all-width argument. It uses the fiber lemma from
#5921 and the total-image bound dim V ≤ 4 from #6838 as inputs. The new step
is the reducibility of every four-dimensional no-edge image, together with an
explicit irreducible three-dimensional example. A four-pattern cap is handled
by an idempotent gram matrix. Every other four-dimensional pool contains either
a column triple, whose odd covectors span at most three dimensions, or a
normal-form triple, which leaves an invariant line or hyperplane.

The sharp example, on coordinates 0, 1, 2, 3, is

```text
N0 = e0 (e0+e1+e2)^T
N1 = e1 (e0+e1+e3)^T
N2 = e2 (e0+e2+e3)^T
```

Its pattern space is three-dimensional and contains no matrix unit. Both
factors of every realizable projector are supported on these four coordinates,
and the only realizable projectors are the three above. Their action on
span(e0, e1, e2) has no invariant line or plane.

[verify.py](verify.py) repeats the parts of the argument that are finite:
all 168 elements of GL(3, 2), the exact pool on four coordinates and the
one-bit extension, the seven four-point caps, and negative controls. The
parity pool from #6838 is reducible. The normal-form triple by itself is
reducible. Deleting one sharp projector leaves an invariant line. These checks
do not replace the width-independent case analysis.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. Nothing here reruns the selected baseline as a scientific
replay.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/no-edge-irreducible-image/verify.py
python3 -I -O -B research/no-edge-irreducible-image/verify.py
python3 -B scripts/research_package.py --package research/no-edge-irreducible-image --check-only
python3 -B scripts/research_package.py --package research/no-edge-irreducible-image
```

The verifier prints `PASS_NO_EDGE_IRREDUCIBLE_IMAGE`.

## Open next questions

1. **Word accounting after a valid split.** Does bound 3 improve the paid-rank
   obstruction for a three-relation word once the relation, cube-span, and
   coordinate-call hypotheses of #6777 and #6782 are in force? The scalar
   theorem does not supply that split. The smallest next step is to state
   those hypotheses and only then count endpoints.

2. **Pattern dimension 4.** Does an irreducible no-edge pool of pattern
   dimension 4 exist, and what is its joint-image dimension? The Fano-plane
   case split stops at pattern dimension 3. #6838 already notes that the
   parity construction one dimension higher has total joint image 5. The
   smallest next step is to decide whether that example is irreducible.

## Credit

Nick Petalas, #5921, for the fiber lemma and the joint-image question.
CubeJerry, #6838, for the sharp total-image bound 4 and for isolating the
irreducible question; #6782 for the edge-quotient context. #6785 asks the
zero-edge irreducible question and answers a different one-edge statement;
its proof assumes a nonzero edge space. The relation-word setting of #6777
is context, not a proof dependency. Prepared by unpaidmoon
with substantial Cursor Grok assistance. New work is Apache-2.0.
