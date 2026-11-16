# Idempotent triples after rows (1, 1, 0, 0)

**No new kappa.** For the rank-1 idempotent A in M_4(F_2) with rows
(1, 1, 0, 0), the ordered idempotent triples (A, B, C) whose gates
multiply to I + x I_4 are exactly the triples with A B = B A = 0 and
C = I + A + B. There are 58 of them, one for each idempotent endomorphism
of ker(A). The selected frontier stays 781451/250000000.

The proof, the census domains, and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. This package answers open question 2 of
PR #7027: the same idempotent-triple question for one rank-1 matrix other
than E_11. The field and block stay F_2 and 4 by 4. The E_11 census, the
T-commutant valuation identity, the constant-R insertion, and the g = 13
and g = 31 profiles are not redone.

The evidence classes are separate. Section 2 of the proof is the
coefficient equivalence for every idempotent triple in M_n(F_2). Sections
3 and 4 prove the counts 58 and 177 for this matrix, and the same kernel
bijection gives the count 58 for every rank-1 idempotent in M_4(F_2).
Section 5 is an exhaustive finite census: all 65,536 matrices, all
802-by-802 idempotent pairs after this A, the subspaces of F_2^3 and
F_2^4, and the 512 endomorphisms of the kernel. Section 6 writes two
orthogonal triples and one non-idempotent third factor. The census of
this one first factor is not a census of the other rank-1 matrices, and
the coefficient proof is not a search.

Exactly 177 idempotent matrices B satisfy B A = 0. For 119 of them
A B is not zero, the third factor I + A + B is not idempotent, and the
gate product is still the target. Those 119 are not idempotent triples.
One of them is the witness with rows (3, 0, 0, 0).

Each of the 58 triples embeds on stage 0 as a factorisation of I + x E_0.
The nine-factor three-stage word is not rebuilt.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package
uses that record and edits neither file. Source commits, Git blobs and
SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and
catalogue are historical provenance. The verifier recomputes the matrices
and does not read the predecessor files.

Canonical main was fetched at session start and again before submission.
Both fetches returned `17469fff78c22941280f04d39dc5a1faee09c840`.
`python3 scripts/find_overlap.py --refresh` at 2026-11-10T10:12:49Z
searched 339 open PR records and 7013 discussion records with complete
pagination, together with the local notes. The only open statement of
this question is open question 2 of PR #7027. Its finding
`https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19514176`
does not answer it. The local phrase search otherwise hits only the
unrelated group-algebra expression in
`research/s3-shortest-word-rigidity`. Fork `cursor/*` branches and open
fork PRs were listed separately; none classifies this matrix.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/rank1-idempotent-triple-1100
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_RANK1_IDEMPOTENT_TRIPLE_1100`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/rank1-idempotent-triple-1100/verify.py
```

## Open next questions

- For this same idempotent A with rows (1, 1, 0, 0), which of the 65,536
  matrices B, not necessarily idempotent, satisfy
  (I + x A)(I + x B)(I + x (I + A + B)) = I + x I_4? The linear
  coefficient forces the third factor for every B. The counts 58 and 177
  classify only idempotent middle factors, and the 119 one-sided witnesses
  show that a non-idempotent third factor can already hit the target.
  The first step is to let the 16-bit integer run from 0 through 65535,
  set the third factor equal to I + A + B, and test the product. Nothing
  external blocks that scan. One rejected B is not a classification. This
  is not the E_11 slice, not the constant-R insertion beside a valuation-1
  factor, and not a g = 13 or g = 31 word.

## Credit

The question is open question 2 of PR #7027. The E_11 classification and
the orthogonal product identity proved there are the predecessor. The
paired-star coordinates are from PR #5747 (Ali Romman). The T-commuting
projector obstruction is PR #6956. Prepared by unpaidmoon with substantial
Cursor Grok assistance. Independent human review and a proof-assistant
proof are unclaimed.
