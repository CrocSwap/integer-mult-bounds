# No-edge pattern dimension 4, joint image 5

**Result.** A complete no-edge pool of pattern dimension 4 can act
irreducibly on a joint image of dimension 5. For every ambient width at
least 5, the five projectors

```text
N_v = (e_0 + e_2)(e_1 + e_2)^T,
N_u = (e_1 + e_2)(e_0 + e_2)^T,
N_o = (e_0 + e_1 + e_2)(e_0 + e_1 + e_2)^T,
N_a = (e_2 + e_3)(e_0 + e_1 + e_3)^T,
N_b = (e_0 + e_2 + e_3 + e_4)(e_1 + e_4)^T
```

are the complete pool of their pattern span. That span is four-dimensional
and contains no matrix unit. The joint image is the coordinate span of
e_0 through e_4, and the action is irreducible. **No new κ.** The selected
value remains `781451/250000000`.

This is an existence proof under the same complete-pool and no-matrix-unit
hypotheses as #6921 and #6962. It is not an upper bound, and it is not a
classification of every pattern-dimension-4 pool. The first three
projectors are the normal-form triple, which by itself is reducible on a
three-dimensional image. N_a and N_b are the added data.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers the open
question of #6962: whether irreducible joint image 5 occurs for a complete
no-edge pool in pattern dimension 4. The reason is recorded in
[TASK.json](TASK.json). The original native acceptance gate is unmet, and
the selected frontier is unchanged.

[PROOF.md](PROOF.md) is the argument. Section 3 shows every nonzero pattern
has weight at least 2 and at least two columns. Section 4 uses that column
count to reconstruct every lift inside the fifteen-element pattern space,
then rules out support outside the first five coordinates. Section 6
records a strongly connected hit digraph, and Section 7 turns that
connectivity into the invariant-subspace exclusion.

[verify.py](verify.py) repeats the finite parts: the fifteen pattern
weights and lifts, the six digraph edges, the complete pool at widths 5, 6
and 7, and every subspace of the joint image. The subspace count is 374,
the sum of the Gaussian binomial coefficients on F2^5. The normal-form
triple is retained as a reducible control, and its old invariant line is
checked to be broken by the full pool. These checks corroborate the
width-independent argument. They do not enumerate all four-dimensional
pattern spaces.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. Nothing here reruns the selected baseline as a scientific
replay.

Overlap was checked on 2026-11-10 against upstream main
`17469fff78c22941280f04d39dc5a1faee09c840`. The question is the open item
in merged #6962 and in its finding, discussion comment 19507179. #6921
stops at pattern dimension 3. A search of open upstream pull requests for
this question returned no match. #6785 is a one-edge exclusion. No match
is not a novelty certificate; those distinctions are from reading the
records.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/no-edge-dim4-image-five/verify.py
python3 -I -O -B research/no-edge-dim4-image-five/verify.py
python3 -B scripts/research_package.py --package research/no-edge-dim4-image-five --check-only
python3 -B scripts/research_package.py --package research/no-edge-dim4-image-five
```

The verifier prints `PASS_NO_EDGE_DIM4_IMAGE_FIVE`.

## Open next questions

1. **Irreducible dimension above 5, still at pattern dimension 4.** Can a
   complete no-edge pool of pattern dimension 4 act irreducibly on a joint
   image of dimension 6 or more? The pool above attains 5, so any upper
   bound is at least 5. The smallest next step is one explicit pool with a
   written invariant-subspace check, or a scoped upper bound under these
   same hypotheses. No support reduction here makes an exhaustive search
   finite, so a search that finds nothing would not be a proof.

## Credit

#6921 isolated the normal-form triple and proved the irreducible bound 3
for pattern dimension at most 3; that theorem is not reproved, and the
triple is used here only as an explicit reducible subconfiguration.
#6962 showed that the bound 3 fails in pattern dimension 4 and left joint
image 5 open; the four-cycle is not redone. CubeJerry, #6838, for the
parity pool, which attains total dimension 5 and is reducible, so it is
not this witness. Nick Petalas, #5921, for the fiber lemma; this proof
reconstructs lifts from rows and does not rely on that lemma. Prepared by
unpaidmoon with substantial Cursor Grok assistance. New work is Apache-2.0.
