# Constant insertion beside the valuation-1 factor

**No new kappa.** Beside the stage-0 gate `I + x E_11` in the nine-gate word
of PR #7027, no matrix `R` with entries in `F_2[x, y, z]` makes the
coefficient of `e` equal to `I`. The pure product remains
`product_j (I + x_j E_j)` for every such insertion. The coupled31 operator
`(I + e I)` times that pure product is a different equation: it holds for
exactly one polynomial matrix, the constant `R = I`. Every constant matrix
supported on the stage-0 block fails both equations. The selected frontier
stays 781451/250000000.

The hypotheses, the diagonal identity, the census counts, and the limits are
in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed query
demand removes real work. This package answers the first open question of PR
#7027: expand `(I + x E_11)(I + e R)` on the stage-0 block, and decide whether
one constant matrix inserted beside that factor makes the coefficient of `e`
equal to `I` while the pure product stays `product_j (I + x_j E_j)`. The
field, the block, and the nine diagonal gates stay those of #7027.

The evidence classes are separate. Sections 3 through 5 of the proof are
identities in the integral domain `F_2[x, y, z]`. They cover every polynomial
matrix, including every constant 8-by-8 matrix, without enumerating `2^64`
matrices. Section 6 is an exhaustive census of two finite domains: all
65,536 constant 4-by-4 matrices, and all 65,536 ways to embed one on the
stage-0 block. The local three-gate equation `C = (1 + x) I_4` has exactly
one constant solution, `R = I_4`. The eight-dimensional equations `C = I`
and `C = P` have none in that embedded domain. The endpoint witness `R = I_8`
is the unique polynomial solution of `C = P` for this single slot. It is a
witness for that operator identity, not a T-commuting full-call word.

PR #6956 still excludes three nonzero T-commuting projectors. This package
does not rerun that census. The unsplit call `E_j` is a different pure factor,
and the other-idempotent classification is a different question.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package uses
that record and edits neither file. Source commits, Git blobs and SHA256 pins
are in [SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance. The predecessor notes are pinned as provenance as well;
the verifier recomputes the matrices and does not read those files. The #7027
package is not on this base. Its head is
`1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0`, and the identities used here are
recomputed.

Overlap was refreshed against open upstream PRs and discussions at
2026-11-10T10:05:04Z (`python3 scripts/find_overlap.py`). The insertion
question appears as an open question of PR #7027 and of
https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19514176.
The handoff pointer is
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514178.
No open PR solves the insertion. The unsplit two-map result and the g=13 and
g=31 gap results are different words.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-constant-r-insertion
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_CONSTANT_R_INSERTION`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-constant-r-insertion/verify.py
```

## Open next questions

- Can two constant matrices, placed in two different gaps of this same
  diagonal word, make the coefficient of `e` equal to the pure product? A
  single gap admits only `R = I` for that equation, but two gaps add, and the
  off-diagonal scales depend on the gap. Any finite number of constant
  insertions already fails to make the coefficient equal to `I`, by the same
  diagonal divisibility. The first step is to solve the off-diagonal system
  for insertions immediately after stage-0 `E_11` and immediately after
  stage-0 `E_22`. Nothing external blocks that linear algebra. A solution
  would still not be a T-commuting full-call word.
- For the non-idempotent leading factor `N` exhibited in PR #7027, does one
  constant matrix beside `I + x N` make the stage-0 coefficient of `e` equal
  to `I`, or the eight-dimensional coefficient equal to the pure product?
  Sections 3 through 5 use diagonality, and `N` is not diagonal. The first
  step is to expand `(I + x N)(I + e R)` and multiply by the other two
  non-idempotent factors. Nothing external blocks that expansion. It is not
  the other-idempotent census, and it is not an unsplit call `E_j`.

## Credit

The paired-star contract, the operator `T`, and the pure target are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The
T-commuting projector obstruction is PR #6956. The valuation-1 triple and the
question answered here are PR #7027. Prepared by unpaidmoon with substantial
Cursor Grok assistance. Independent human review and a proof-assistant proof
are unclaimed.
