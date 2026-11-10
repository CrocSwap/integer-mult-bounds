# Pattern dimension 4 irreducible image

**Result.** The no-edge irreducible joint-image bound does not stay 3 when
the pattern space has dimension 4. For every ambient width at least 4, the
four projectors

```text
N_i = e_i (e_i + e_{i+1} + e_{i+2})^T,    i in Z/4Z,
```

are the complete pool of their pattern span. That span is four-dimensional
and contains no matrix unit. The joint image is four-dimensional and the
action is irreducible. **No new κ.** The selected value remains
`781451/250000000`.

This is an existence result under the same complete-pool and no-matrix-unit
hypotheses as #6921. It is not an upper bound, and it is not a classification
of every pattern-dimension-4 pool.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers open question 2
of #6921, which #6921 left open because its Fano-plane case split stops at
pattern dimension 3. The reason is recorded in [TASK.json](TASK.json). The
original native acceptance gate is unmet, and the selected frontier is
unchanged. Question 1 of #6921, paid-rank accounting after a relation split,
is not this result.

[PROOF.md](PROOF.md) is the argument. Section 4 puts every factor on the
first four coordinates and then splits the support of the image vector by
size. Section 5 splits invariant subspaces into lines, planes, and
hyperplanes. Section 6 recomputes the #6838 width-6 parity pool: pattern
dimension 4, total image 5, and a four-dimensional invariant kernel. That
pool is reducible, so it does not by itself show that the irreducible bound
changes.

[verify.py](verify.py) repeats the finite parts: the covector matrix, the
sixteen pattern weights, the six plane pairs, both support checks at widths
4 through 8, the complete subspace lattice of F2^4 (67 subspaces), and the
negative controls. Deleting one cycle projector leaves an invariant line.
The #6921 three-projector example remains irreducible, and the normal-form
triple remains reducible, so the lattice scan is not hard-wired to one
answer. These checks do not replace the width-independent casework, and
they do not enumerate all four-dimensional pattern spaces.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. Nothing here reruns the selected baseline as a scientific
replay.

Overlap was rechecked on 2026-11-10 against 885 open upstream PRs and 6934
discussion records at base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The
only records containing the question are #6921 and its finding,
discussion comment 19474334. Both leave pattern dimension 4 open. #6785 is
a one-edge exclusion and #6782 is an edge-quotient bound. No match is not
a novelty certificate; those distinctions are from reading the records.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/pattern-dim4-irreducible-image/verify.py
python3 -I -O -B research/pattern-dim4-irreducible-image/verify.py
python3 -B scripts/research_package.py --package research/pattern-dim4-irreducible-image --check-only
python3 -B scripts/research_package.py --package research/pattern-dim4-irreducible-image
```

The verifier prints `PASS_PATTERN_DIM4_IRREDUCIBLE_IMAGE`.

## Open next questions

1. **Irreducible dimension above 4, still at pattern dimension 4.** Can a
   complete no-edge pool of pattern dimension 4 act irreducibly on a joint
   image of dimension 5 or more? The four-cycle attains 4, so the old bound
   fails, but it gives no replacement ceiling. The parity pool attains total
   dimension 5 and is reducible. The smallest next step is one explicit pool
   with a written invariant-subspace check, or a scoped upper bound under
   these same hypotheses. No support reduction here makes an exhaustive
   search finite, so a search that finds nothing would not be a proof.

## Credit

Nick Petalas, #5921, for the fiber lemma and the joint-image question; this
proof does not rely on the fiber lemma. CubeJerry, #6838, for the total-image
bound in pattern dimension at most 3 and for the parity pool rechecked in
Section 6. #6921 proved the irreducible bound 3 for pattern dimension at
most 3 and isolated this dimension-4 question; that theorem is not reproved.
#6785 and #6782 are one-edge and edge-quotient context. Prepared by
unpaidmoon with substantial Cursor Grok assistance. New work is Apache-2.0.
