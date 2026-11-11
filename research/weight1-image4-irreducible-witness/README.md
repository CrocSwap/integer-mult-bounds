# A weight-1 no-edge pool of image dimension 4 can be irreducible

**Witness, proved for one pool. No new κ.** The selected record stays
`363005817/100000000000`.

## Result

Over `F2`, the four projectors

```text
N_i = (e_i + e_{i+1} + e_{i+2}) e_i^T,    i in Z/4Z,
```

are the complete pool of their off-diagonal pattern span at every ambient
width at least 4. That span has dimension 4 and contains no matrix unit.
Every covector has weight 1. The joint image has dimension 4, its common
kernel is zero, and the action is irreducible.

The answer to open question 2 of #7138 is therefore no. Not every weight-1
no-edge pool of pattern dimension 4 and joint-image dimension 4 is
reducible. The argument is in [PROOF.md](PROOF.md).

This is one witness. The four disjoint weight-1 lines of #7138 meet the
same dimension counts, also have trivial common kernel, and are reducible
because each line is invariant. The kernel test, which needs image
dimension at least `dim P + 1`, does not decide either example.

These operators are the transposes of the #6962 four-cycle. That cycle has
covector weight 3. Transposing swaps the image and the covector, so the
weight-1 hypothesis holds here and fails there. Irreducibility is proved
again for the transposed action.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status is **changed**.
The card asks for a larger or nonabelian register alphabet. This package
answers the weight-1 image-dimension-4 question left by #7138. The reason
is recorded in [TASK.json](TASK.json). The original native acceptance gate
is unmet, and the selected frontier is unchanged. No register-alphabet
construction round is opened.

[PROOF.md](PROOF.md) is the argument. Section 2 puts every factor on the
first four coordinates and then rules out every covector of weight at
least 2 by a pair computation on `Z/4Z`. Section 4 splits an invariant
subspace according to which images it contains. Section 5 recalls the four
disjoint lines without reproving their completeness. Section 6 records the
column shape forced by a trivial kernel; it is not a classification.

[verify.py](verify.py) repeats the finite parts: the sixteen pattern
weights, the six pairs, both support checks at widths 4 through 8, the
complete subspace lattice of `F2^4` (67 subspaces), and the controls.
Deleting one witness projector leaves an invariant line. The four disjoint
lines are reducible. The #6962 four-cycle is irreducible under the same
lattice scan and has covector weight 3, so the scan is not hard-wired to
one answer and that cycle stays outside the weight-1 hypothesis. These
checks do not replace the width-independent casework, and they do not
enumerate all four-dimensional pattern spaces.

Evidence class: a proof for this pool, plus an exhaustive census of its
67 image subspaces and finite pool scans at widths 4 through 8. Not a
census of all weight-1 pattern spaces, and not a search.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. On that commit, `docs/research/current-priorities.md` still
quotes an older selected checkpoint. This package follows
`certificates/selected-result.json`. Nothing here reruns the selected
baseline as a scientific replay.

Overlap was checked on 2026-11-11 against open upstream pull requests.
A search for `pattern dimension 4` returned #7094, #7138, and #7139.
#7094 is the heavier irreducible dimension-5 witness. #7138 proves the
weight-1 image bound 6 and reducibility for image dimension at least 5,
and leaves image dimension 4 open. #7139 proves the all-width image bound
6 and that dimension 6 is reducible. Searches for `weight-1 image`,
`joint-image dimension 4`, and `every weight-1` returned no further open
pull request. Local notes at the base commit do not contain this witness.
The offline overlap helper had no remote snapshot; those distinctions are
from the live pull-request search and from reading the packages. No match
is not a novelty certificate.

The predecessor package is fork pull request 260, head
`5690b63f877654bca13e3d4777c081e7d538d7bc`, branch
`cursor/weight1-pattern-dim4-reducible-b5eb`. No fork `cursor/*` branch
already named this image-dimension-4 witness.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/weight1-image4-irreducible-witness/verify.py
python3 -I -O -B research/weight1-image4-irreducible-witness/verify.py
python3 -B scripts/research_package.py --package research/weight1-image4-irreducible-witness --check-only
python3 -B scripts/research_package.py --package research/weight1-image4-irreducible-witness
```

The verifier prints `PASS_WEIGHT1_IMAGE4_IRREDUCIBLE` with `pool=4`,
`image_dim=4`, `kernel_dim=0`, and `new_kappa=null`.

Not run: Lean, Docker, the selected cold replay, and any enumeration of
all 4096 diagonal-ones matrices. An incomplete search is not evidence in
this package.

## Open next questions

Which weight-1 no-edge pools of pattern dimension 4 and joint-image
dimension 4 are irreducible, up to coordinate permutation? The witness
shows that reducibility can fail, and the four disjoint lines show that it
need not fail. Section 6 of the proof says that any irreducible example
has exactly four columns of dimension 1. The smallest next step is to
enumerate the 4096 matrices over `F2` with ones on the diagonal and to
decide which invertible strongly connected matrices admit extra
coordinates that preserve the weight-1 and no-matrix-unit hypotheses,
after writing why that list is complete. This package does not run that
enumeration. Extra coordinates are not bounded here, so those 4096
matrices are not yet an exhaustive domain.

## Credit

The fiber lemma is Nick Petalas, #5921, and is not an input: membership of
the witness pool is the support casework in Section 2. CubeJerry, #6838,
proved the pattern-dimension-at-most-3 total-image bound. #6921 proved the
irreducible bound 3 for pattern dimension at most 3. #6962, package
`research/pattern-dim4-irreducible-image`, gave the four-cycle whose
transpose is the witness; that irreducibility proof is not reused. #7138,
fork pull request 260, proved the weight-1 image bound 6 and left this
dimension-4 question open; its four disjoint lines are the reducible
control. #7139 proved the all-width image bound 6. #7094 is the heavier
irreducible dimension-5 witness and is outside the hypothesis. This
package does not replace those arguments.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. No independent human or formal-kernel review is claimed.
