# Valuation 1 outside the T-commutant

**No new kappa.** A 4-by-4 matrix over F_2 that commutes with the paired-star
stage operator T has even (1+x)-valuation, so valuation 1 is impossible inside
that commutant. Outside it, the explicit idempotents E_11, E_22 and
E_33 + E_44 have valuations 1, 1 and 2, and their gates multiply to
I + x I_4. The same nine diagonal gates, three on each stage, multiply to the
pure operator product_j (I + x_j E_j) on the eight-dimensional three-leaf
space. The coefficient of e stays zero. The selected frontier stays
781451/250000000.

The proofs, the census domains, and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed query
demand removes real work. This package answers the open question left by
PR #6956: whether a stage factor that is not a T-commuting projector can have
(1+x)-valuation 1, so that three factors can total valuation 4. The field,
block size and leaf count stay F_2, d = 2 and g = 3.

The evidence classes are separate. Sections 2 and 3 of the proof are
identities. Section 4 writes two triples whose products are checked by hand
and by the verifier. Section 5 is an exhaustive finite census of four finite
domains: all 65,536 matrices, all 256 commutant matrices, all 802-by-802
idempotent pairs after E_11, and all 65,536 middle factors after one fixed
non-idempotent matrix. Section 6 is the pure three-stage operator identity.
None of these is a truncated search, and the E_11 classification is not a
census of every triple in M_4(F_2)^3.

PR #6956 still excludes three nonzero T-commuting projectors. This package
does not rerun that 15,625-triple multiplication. It only checks that the same
256-element commutant contains those 26 projectors, each of even valuation.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package uses
that record and edits neither file. Source commits, Git blobs and SHA256 pins
are in [SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance. The predecessor notes are pinned as provenance as well;
the verifier recomputes the matrices and does not read those files.

Overlap was refreshed against open upstream PRs and discussions at
2026-11-10T08:50:39Z (`python3 scripts/find_overlap.py --refresh`). The only
records containing both the commutant and this valuation question are PR #6956
and its finding
`https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507190`,
which leave the question open. No open PR states this triple.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-valuation-one-factor
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_VALUATION_ONE_FACTOR`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-valuation-one-factor/verify.py
```

## Open next questions

- Can a constant matrix R be inserted beside one exhibited factor so that the
  coefficient of e becomes I, while the pure product remains
  product_j (I + x_j E_j)? The coupled31 target is (I + e I) times that pure
  product, and the word in this package has coefficient of e equal to zero.
  The first step is to keep the diagonal gates and expand (I + x E_11)(I + e R)
  on stage 0. Nothing external blocks that equation. One rejected R is not a
  proof that none exists. This is not the unsplit full call E_j, and it is not
  a g = 13 or g = 31 word.
- For a rank-1 idempotent other than E_11, are the idempotent triples that
  multiply to I + x I_4 exactly the orthogonal triples with third factor
  I + A + B? The census here fixes the first factor as E_11. The orthogonal
  identity is available for every idempotent, and the remaining first factors
  are a separate finite census. The first step is to repeat the 802-by-802
  multiplication for the idempotent with rows (1, 1, 0, 0). Nothing external
  blocks that scan. A second first factor would still leave non-idempotent
  triples unclassified; the 128-element slice already shows that those exist
  for one fixed leading factor.

## Credit

The paired-star contract, the operator T, and the pure target are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The
T-commuting projector obstruction and the question answered here are PR #6956.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
