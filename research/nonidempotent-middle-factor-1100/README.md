# Middle factors after rows (1, 1, 0, 0)

**No new kappa.** For the rank-1 idempotent A in M_4(F_2) with rows
(1, 1, 0, 0), and for an arbitrary 4-by-4 matrix B over F_2, set
C = I + A + B. The product (I + x A)(I + x B)(I + x C) equals I + x I_4
for exactly 296 matrices B. The selected frontier stays
363005817/100000000000.

The 296 matrices are three block families on im(A) ⊕ ker(A):

| Family | Count | Shape |
|---:|---:|---|
| 1 | 58 | B and C both idempotent, and A B = B A = 0 |
| 2 | 119 | B idempotent, C not, B A = 0 and A B ≠ 0 |
| 3 | 119 | B not idempotent, C idempotent, A B = 0 and B A ≠ 0 |

Families 1 and 2 are the 177 idempotent middle factors counted by PR #7040.
Family 3 is the new set of 119 non-idempotent middle factors. No accepted
matrix has both B and C non-idempotent. Exactly eight accepted matrices
satisfy B^2 = 0. The proof, the census domain, and the limits are in
[PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. This package answers the open middle-factor
question of PR #7040 for the same named matrix. The field and the block
stay F_2 and 4 by 4. The idempotent-pair census of #7040, the E_11 census
of #7027, the constant-insertion questions, and the g = 13 and g = 31
profiles are not redone.

Two evidence classes are claimed. Sections 2 through 6 of the proof are a
coefficient lemma and a block classification. The lemma holds for every
idempotent first factor in M_n(F_2); the count 296 does not. Section 7 is
an exhaustive finite census: the 16-bit integer runs from 0 through 65535,
each matrix once, with the third factor set equal to I + A + B, and the
gate product tested. The accepted set equals the set built from the three
families. This is not a truncated search, not a sample, and not a kappa
improvement.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record in `certificates/selected-result.json`
is 363005817/100000000000. This package uses that record and edits neither
file. Source commits, Git blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance. The verifier recomputes the matrices and does not
read the predecessor package.

Canonical `CrocSwap/integer-mult-bounds` main was fetched at session start
and again before submission. Both fetches returned
`e54523517d0f03e58352e647c403a5af3e525a57`. Two GraphQL searches of open
pull requests, one for the named rows together with the 65,536-matrix
wording and one for the middle-factor wording, returned #7040, #7027,
#7039 and #7099. The body of #7039 does not contain this matrix or this
scan; it is the constant-insertion package. #7040 leaves the question open.
#7027 classifies idempotent triples after E_11. #7099 lists the #7040
middle-factor question as still open. The latest 40 comments on Discussion
#1166, from 2026-11-11T08:58:58Z through 2026-11-11T10:21:39Z, do not answer
it. The 65,536 count in the #7196 note on that thread is a different
second-map domain. Fork `cursor/*` branches were listed; the only branch
for this matrix is the #7040 branch
`cursor/rank1-idempotent-triple-1100-be7e`, which stops at idempotent
middle factors.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/nonidempotent-middle-factor-1100
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_NONIDEMPOTENT_MIDDLE_1100`. The checks raise `SystemExit`, so
optimized mode does not strip them. Directly:

```sh
python3 -B research/nonidempotent-middle-factor-1100/verify.py
```

Checked counts: 296 accepted matrices, in families of 58, 119 and 119; 177
idempotent middle factors and 177 idempotent third factors, with overlap
58; ranks 1, 63, 196, 36, 0 in ranks 0 through 4; eight solutions with
B^2 = 0. The witness W = (0, 1, 0, 0) is multiplied by hand in `PROOF.md`
and again by the verifier. The identity, the one-bit neighbor A of W, the
both-nonzero block matrix (4, 5, 0, 0), and one shifted third factor are
rejected. No Lean, Docker, native, or selected-frontier replay was run.

The ascending decimal list of the 296 accepted 16-bit integers, one per
line with a trailing newline, has SHA256
`07a59d5644b30bf5c78ec67fd58bdee01cc1048fc5dc20ea574fffe3e4ec5659`.

## Open next questions

- For the rank-1 idempotent E_11, which of the 65,536 matrices B satisfy
  (I + x E_11)(I + x B)(I + x (I + E_11 + B)) = I + x I_4? The coefficient
  lemma of this package forces the third factor and reduces the equation to
  B(I + E_11 + B) = 0 for every idempotent first factor. The count 296 uses
  the named kernel of rows (1, 1, 0, 0) and is not a count for E_11. The
  same three-family arithmetic depends only on a 3-dimensional kernel, so a
  basis carrying this A to E_11 would transport the families, but that
  transport is not written here and E_11 was not scanned. The first step is
  either to exhibit one such basis and push the three families across it,
  or to let the 16-bit integer run from 0 through 65535 for E_11. Nothing
  external blocks that scan. One transported witness is not a count. This
  is not the constant-insertion question and not a g = 13 or g = 31 word.

- For this same named A, which of the 65,536 matrices B satisfy the reversed
  product (I + x B)(I + x A)(I + x (I + A + B)) = I + x I_4? Family 3 of the
  ordered product proved here has A B = 0 and B A ≠ 0, so the two orders are
  different equations. The first step is the same 16-bit scan with the first
  two factors exchanged. Nothing external blocks that scan. One rejected
  order is not a classification.

## Credit

The question is the open middle-factor question of PR #7040,
`research/rank1-idempotent-triple-1100`, head
`2bac9bfafe5fa009bce2141c07b703c977b18456`. That package proved the
idempotent-triple equivalence and counted the 58 orthogonal triples and the
177 idempotent middle factors with B A = 0. The E_11 classification and the
orthogonal product identity it extends are PR #7027. The row-mask convention
is the one used there. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Independent human review and a proof-assistant proof are
unclaimed. Apache-2.0.
