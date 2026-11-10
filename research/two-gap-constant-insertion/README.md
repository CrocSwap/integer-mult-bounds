# Two constant insertions after stage-0 E_11 and E_22

**No new kappa.** In the nine diagonal gates of PR #7027, constant matrices
`R` and `S` may sit in the gaps immediately after stage-0 `I + x E_11` and
stage-0 `I + x E_22`. Over `F_2`, with `e` central and `e^2 = 0`, the
coefficient of `e` equals the pure product for exactly `2^50` pairs. It is
never the identity. The selected frontier stays 781451/250000000.

The argument and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. This package answers a different question:
the first open question of PR #7039, at the two gaps named in its first
step. The field stays `F_2[x, y, z][e]/(e^2)`. It is not a caller, a native
bill, or a change of kappa. Source commits, Git blobs and SHA256 pins are
in [SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000 from PR #6030.
This package uses that record and edits neither file.

The classification is an identity. The machine check multiplies every one
of the 64 matrix units in each gap and compares the two gap scales at all
64 positions. The solution count is the number of free bits in that solved
system. The `2^50` pairs were not listed one by one. A failed search is
not what this record claims.

Overlap was checked on 2026-11-10 against open upstream PRs by title and
body search, and against live `cursor/*` branches on
`unpaidmoon/integer-mult-bounds`. The question is the first open question
of PR #7039. The valuation-1 word is PR #7027. No open PR and no fork
branch solves these two gaps. The non-idempotent factor `N`, other gap
pairs, and the g=13 and g=31 schedules were left in place. `gh` GraphQL
overlap refresh returned HTTP 403 for this integration, so closed-PR body
coverage is incomplete; the targeted issue search is the check that was
run.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/two-gap-constant-insertion
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_TWO_GAP_CONSTANT_INSERTION`. The checks raise `SystemExit`, so
optimized mode does not drop them. Directly:

```sh
python3 -B research/two-gap-constant-insertion/verify.py
```

## Open next questions

- For another pair of gaps in this same nine-gate word, which constant
  pairs make the coefficient of `e` equal to the pure product? PR #7039
  asks about two gaps in general. This package closes only the adjacent
  pair after stage-0 `E_11` and `E_22`, where the scales differ by `1 + x`
  exactly on the pairs that meet coordinate 1. The first step is to recompute
  `a_ij` and `b_ij` for the gap after stage-0 `E_22` and the gap after
  stage-1 `E_11`, then solve the 64 entry equations. Nothing external blocks
  that calculation.
- Can entries in `F_2[x]`, rather than constants, satisfy the same two-gap
  equation? On a blocked position the constant equation `R + (1 + x) S = 0`
  has only the zero solution, while `S = 1` and `R = 1 + x` is a polynomial
  solution of that one entry. The first step is to allow degree at most 1
  in `x` on one blocked position and keep the diagonal condition. Nothing
  external blocks that entry. It leaves the constant-matrix count above
  unchanged.
- For the non-idempotent leading factor `N` exhibited in PR #7027, does one
  constant matrix beside `I + x N` make the stage-0 coefficient of `e`
  equal to `I`? The diagonal cancellation used here needs the gate to be
  diagonal. The first step is to expand `(I + x N)(I + e R)` and compare
  the result with `I`. Nothing external blocks that expansion.

## Credit

The paired-star contract, the operator `T`, and the pure target are from
PR #5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The
valuation-1 triple is PR #7027. The one-insertion theorem and the question
answered here are PR #7039. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Independent human review and a proof-assistant proof are
unclaimed. Apache-2.0.
