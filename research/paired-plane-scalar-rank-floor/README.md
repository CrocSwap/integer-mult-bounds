# A 48-to-50 scalar-rank bracket for the fixed paired-plane mask

For the **fixed 56 matched planes from PR1825**, every matrix satisfying the
strict scalar plane-port fitting mask has rank at least **48**, over every
field. An explicit matrix in this package has rank **50** over every field.
Thus the minimum scalar fitting rank for this mask lies in `[48, 50]`.
In particular, no refactorization with 23 scalar rank-one channels can fit it,
even with arbitrary coefficients and arbitrary values on all free entries.

This is a finite algebraic result for the strict mask adopted in
[PR1889](https://github.com/CrocSwap/integer-mult-bounds/pull/1889).
It is not a native copy-rank price, a new coverage identity, a plane-port
supplier, or a new multiplication constant. It does not settle which endpoint
contract a different hosted implementation could realize.

## Exact model and proof

The selected P112 labels are vectors `q_i` in `F_2^9`. PR1825's matching
partitions the 112 ports into 56 pairs `(i,j)` with `q_i.q_j=0` and
`q_i.q_i=q_j.q_j=1`. Both ports of a pair have the same nondegenerate plane
`E=span(q_i,q_j)`. Two planes are orthogonal exactly when all four basis
pairings vanish. These binary label tests define the mask; the scalar matrix
can be over **any field**, independently of the binary label field.

A fitting scalar matrix `K` has `K_ii=1`, and `K_ij=0` when `i!=j` and the
planes at `i,j` are not orthogonal. Entries between orthogonal planes are free;
no symmetry, integral lift, coefficient sign, or factor support restriction is
imposed on `K`.

**Lower bound.** `CERTIFICATE.json` lists these 24 pairwise nonorthogonal planes
(zero-based indices in the pinned matching):

```text
2 6 8 17 18 19 21 22 24 28 29 34 35 36 38 39 41 42 43 45 46 51 52 53
```

Take both ports from every listed plane. A plane is not orthogonal to itself,
so the two distinct ports inside each pair also have a required zero. The
resulting 48-by-48 principal submatrix of **every** fitting `K` is `I_48`.
Its determinant is one in every field. Therefore `rank(K)>=48`. If
`K=sum_{s=1}^r a_s b_s^T`, then `rank(K)<=r`, proving the channel-count floor.
Changing any free entry cannot alter this principal submatrix.

**Upper bound.** The same certificate partitions the 56 planes into 25
nonempty classes, each consisting of pairwise orthogonal planes. For each
class and each of the two positions in a matched pair, let `v` indicate the
ports in that position. Set `K=sum v v^T` over the resulting 50 vectors.
Each port belongs to exactly one support. The diagonal is one; distinct ports
of the same plane occupy different supports; any other nonzero offdiagonal
entry joins orthogonal planes. Thus `K` fits. The disjoint supports prove
rank at most 50, and choosing one representative from each gives `I_50`,
proving rank exactly 50 in every field. This construction uses only 0 and 1.

These two witnesses suffice for the bracket. Optimality of the clique or of
the class partition is not asserted or needed. `discover.py` records the
deterministic search that found them; verification checks the witnesses directly.

## Relation to prior work and the task card

The picker selected `recursive-interfaces`; `coverage-law-change` was chosen.
Its first working command, `python3 -B research/complex-local-word-ceiling/verify.py`,
passed. The scope was refined to a necessary scalar endpoint obligation of the
two-unpaid-coordinate proposal, as recorded in `TASK.json`.

- [PR1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825), head
  `d16fb8936795ff101e4d2f63cfdc6a25066ebabf`, supplies the matched planes and
  binary factorization. The matching is retained by PR1889's pinned fixture.
- Adam Gall's [PR1889](https://github.com/CrocSwap/integer-mult-bounds/pull/1889)
  shows the binary factors cannot be lifted in the parity-preserving class and
  asks for arbitrary rational/complex scalar fitting matrices. The 48 floor
  removes that parity hypothesis for the channel-count obstruction.
- Cinna Davis's [PR2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126),
  head `06be72298adf84f3eef0e36f54ac31c357956417`, already supplies the scalar
  fit `I_112`. This package does not claim the first fitting matrix; it supplies
  a smaller-rank fit and a field-independent lower witness for the fixed mask.
- JeremyDiviney's [PR2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203),
  head `c3c85ea8c226640334b1d2246071f230d81cc137`, charges both native payloads
  in the identity-block implementation. Fifty scalar channels here do not
  mean fifty native copy units. No physical savings are inferred.
- Philippe Van Velzen's [Discussion1587 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18925407)
  gives independence-based copy floors for other plane choices; its
  [follow-up](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18927273)
  gives a 2-integral cost obstruction and distinguishes endpoint targets.
  Those are different cost and contract claims; the present bracket fixes
  PR1825's matching and the strict scalar target explicitly.

The exact source bytes, Git blobs and base are pinned in `SOURCES.json`.
The selected archive member is
`candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json`, SHA256
`c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`.
The source archives and prior packages are unchanged. See `OVERLAP.json` for
live search coverage and the reviewed neighboring results.

## Reproduce and evidence

Validated locally on Windows with CPython 3.12.7, including isolated optimized
execution. From repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/paired-plane-scalar-rank-floor --check-only
python3.12 scripts/research_package.py --package research/paired-plane-scalar-rank-floor
```

The registered read-only commands check the pinned sources, all 11,672 required
matrix entries, the forced `I_48`, the constructed `I_50`, 120 dirty scalar
updates, and four algebraic negative controls. `check_vectors.py` independently
reconstructs the mask with explicit nine-coordinate vectors and the matrix by
channel labels, importing no package code. It also checks dirty updates modulo
2, 3, 5 and 101; these examples supplement the field-independent proof.
`check_cli.py` repeats optimized replay after relocation and rejects a corrupted
clique, receipt, and source fixture. Runtime checks do not rely on `assert`.

The dirty check is the algebraic update `z <- z+K*x` for arbitrary initial `z`;
it does not implement native calls, scratch restoration, or the hosted drop
operation. The free offdiagonal entries are allowed by this mask, and `K` is
not claimed to equal `I_112` on arbitrary source vectors.

`RESULTS.json` is checked, not overwritten, by default. To regenerate it
explicitly after reviewing a change:

```sh
python3.12 -I -B research/paired-plane-scalar-rank-floor/verify.py --write-receipt
```

## Open next questions

Can a scalar fitting matrix of rank 48 or 49 be constructed for this fixed
mask, or can the lower bound reach 50? A first step is an exact low-rank
completion on the free plane blocks; a negative search alone would not prove
optimality. Any field dependence must be stated, although the present bracket
holds uniformly.

Separately, can a scalar fitting factorization be translated into a fully
charged native implementation below the two-unpaid-coordinate budget? That
requires pairing-rank costs, payload multiplicity, the endpoint identity and
scratch restoration. Channel count alone cannot answer it.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance in proof, code,
validation and writing. No independent human review is claimed. The matched
plane data and endpoint discussion are due to the credited predecessor authors;
this package adds the fixed-mask rank bracket and exact witnesses. New work is
Apache-2.0.
