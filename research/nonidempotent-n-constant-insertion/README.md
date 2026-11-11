# Constant insertion beside the non-idempotent factor N

**No new kappa.** For the non-idempotent leading factor `N` exhibited in
PR #7027, one matrix inserted immediately beside `I + x N` does not make the
coefficient of `e` equal `I`. On the exhibited stage-0 triple, that
coefficient equals `(1 + x) I_4` if and only if the inserted matrix is `I_4`.
The selected frontier stays 363005817/100000000000.

The proofs, the census domain, and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. This package answers a different question:
open question 3 of PR #7103, which is the non-idempotent slot left open by
PR #7039. The factor stays the exhibited `N`. The insertion stays one matrix
beside `I + x N`. Scope status is `changed` for that reason.

The evidence classes are separate. The right-hand expansion
`(I + x N)(I + e R) M` is an identity for every trailing matrix `M`: the
`(0, 0)` entry of the coefficient of `e` is divisible by `1 + x`, so the
coefficient is never `I`. The exhibited gates `B = E_22` and `C` are one
such trailing product. On that triple, both sides, the coefficient equals
`(1 + x) I_4` exactly for `R = I_4`, for entries in `F_2[x, y, z]`. The
`65,536` constant 4-by-4 matrices are an exhaustive finite census of the
constant special case, not a search sample and not the polynomial proof.
Embedding the same triple on stage 0 of the three-stage word, and inserting
the same one matrix beside `N`, never makes the eight-dimensional coefficient
equal `I_8`. That last statement is a proof by the same `(0, 0)` entry. It
is not a census of `M_8(F_2)`.

`R = I_4` is a witness for the stage-0 equation "coefficient = `(1 + x) I_4`".
It is not a witness for coefficient `I`, and it is not a kappa witness.

The diagonal identity of PR #7039 and PR #7103 does not apply. `N` is not
diagonal: the matrix unit `E_21` contributes `x(1 + x)` to position `(1, 1)`.
The two-gap classification of PR #7103 and the polynomial count of PR #7191
stay on the diagonal word. This package does not rerun the 128-element
middle-factor census of PR #7027.

`current-priorities.md` at this base can still print an older decimal. The
live selected record is 363005817/100000000000. This package uses that record
and edits neither file. Source commits, Git blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record and catalogue are historical
provenance. The verifier recomputes the matrices and does not read the
predecessor packages.

Overlap was checked on 2026-11-11 against open upstream PR titles for the
non-idempotent insertion, against the bodies of PR #7027, PR #7039 and
PR #7103, and against `cursor/*` branches on `unpaidmoon/integer-mult-bounds`.
No open PR and no fork branch answers this slot. PR #7191 classifies
polynomial entries in the diagonal gaps of PR #7103. A later GitHub search
for the same phrase returned HTTP 403, so closed-PR body coverage is
incomplete; the open-PR title search had already been run.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/nonidempotent-n-constant-insertion
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_NONIDEMPOTENT_N_CONSTANT_INSERTION`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/nonidempotent-n-constant-insertion/verify.py
```

No Lean, Docker, native, or selected-frontier replay was run.

## Open next questions

- Which constant 8-by-8 matrices `R`, inserted immediately on the right of
  the embedded `I + x N` in the three-stage word of the proof, make the
  coefficient of `e` equal the pure product `P`? The endpoint operator asks
  for coefficient `P`, and this package only excludes `I`. Column 0 of that
  equation is already settled: it forces column 0 of `R` to be the first
  basis vector. The first step is column 1 of the same linear system.
  Nothing external blocks that column. The result would still not be a
  census of all `2^64` matrices unless the solved linear system is shown to
  have no free bit. This is not the diagonal two-gap problem of PR #7103 or
  PR #7191.
- For a middle matrix other than `E_22` in the 128-element slice of PR
  #7027, which constant matrices make the stage-0 coefficient equal
  `(1 + x) I_4`? Section 2 already rules out coefficient `I` for every
  trailing matrix, so this question is only the pure stage target. The first
  step is to repeat the closed-form multiplication for one other middle
  matrix accepted by that slice. Nothing external blocks that matrix. This
  package does not rerun the slice.

## Credit

The paired-star contract, the operator `T`, and the pure target are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The factor
`N` and the question's geometric setting are PR #7027. The diagonal
obstruction, and the statement that it does not cover `N`, are PR #7039.
The question answered here is open question 3 of PR #7103. Prepared by
unpaidmoon with substantial Cursor Grok assistance. Independent human review
and a proof-assistant proof are unclaimed.
