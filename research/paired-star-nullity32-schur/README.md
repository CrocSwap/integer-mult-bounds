# One nullity-32 class has Schur-complement ranks summing to at least 4

**No new kappa.** The selected frontier stays \(781451/250000000\). For one
nullity-32 class in the partial \(\mathbb F_4\) census of two thin maps on
the three-leaf paired star, the two Schur complements have ranks summing to
at least 4. Equivalently, the two thin matrices have rank sum at least 8.
The bound is sharp. That block shape does not cover every class on which the
\(2^{20}\) frontier fills.

The argument is in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
caller or query demand removes real work. This package answers the first
follow-up stated by the open census PR #7006: one nullity-32 class, its
Schur complements, and whether that shape is every capped class. It is not
a caller, a native bill, or a change of kappa. Source commits, Git blobs
and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record
and catalogue are historical provenance.

Evidence is split in three layers.

1. **Proof.** Over every field of characteristic 2, the block family
   \[
   Z = \begin{pmatrix} P & I & I+Q & 0 \\ I & R & 0 & S \\ I+T & 0 & U & 0 \\ 0 & V & 0 & W \end{pmatrix},
   \quad
   Z+D = \begin{pmatrix} P & 0 & Q & I \\ 0 & R & 0 & S \\ T & 0 & U & 0 \\ I & V & 0 & W \end{pmatrix}
   \]
   satisfies \(\operatorname{rank}(E_Z)+\operatorname{rank}(E_D) \ge 4\), where
   \(E_Z\) and \(E_D\) are the \(6\times 6\) Schur complements in PROOF.md.
   The zero blocks give Schur ranks \(2+2\) and matrix ranks \(4+4\). Another
   point gives Schur ranks \(0+4\) and matrix ranks \(2+6\).

2. **Identification of one class.** Resolution indices \((0,0,0)\),
   permutation index \(0\) and thin gaps \(2,4\) have \(\mathbb F_2\)-nullity
   32. Each free entry has a private generator, \(Z_h = Z_g + D\), and the
   fixed columns are the identity blocks of that family. The \(\mathbb F_4\)
   points are exactly the block family. This is a finite check of one affine
   space, not a sample.

3. **The shape does not cover every capped class.** The same enumerator
   returns \(-3\) on the named class, after the frontier fills while the
   partial rank sum is still at most 6. It also returns \(-3\) on resolution
   indices \((0,0,0)\), permutation index \(4\), gaps \(2,4\), which has
   nullity 24 and component sizes \(4,4,4,4,2,2,2,2\). A return of \(-3\) is
   an incomplete search, not a rank bound. It is enough to show that a capped
   class can sit outside the proved shape. A separate mask pass, with no rank
   search, finds 1746 affine signatures, 24 of nullity 32, and exactly one
   copy of the named mask. Those 24 classes are not a rank census.

The registered smoke test evaluates the Schur identity on the 65536 tuples
with each block in \(\{0,I,E_{11},E_{12}\}\) and on 20000 further tuples.
That finite check is not the proof. The proof is the case analysis.

## Reproduce

Python 3.12 and gcc with OpenMP. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-nullity32-schur
```

The command prints `PASS_NULLITY32_SCHUR` and `PASS_SHAPES`. The class check
is one dynamic-program cap on each of the two named words. The shape pass
screens the 1244160 orders and does not run the rank search.

## Open next questions

- Do the other nullity-32 masks have Schur complements summing to at least 4?
  The mask pass finds 24 such classes and one copy of the identity-block
  pattern proved here. Exchanging the two thin maps preserves the sum, but
  the remaining masks are not that exchange.
- Does the nullity-24 class at resolutions \((0,0,0)\), permutation 4, gaps
  \(2,4\), also have rank sum at least 8? Its \(2^{20}\) run returns \(-3\),
  which is not a bound. Its components are four rows of four variables and
  four rows of two, so the block elimination above does not apply.
- Can every capped class in the partial \(\mathbb F_4\) census be given a
  Schur decomposition whose ranks sum to at least 4? That would replace the
  unfinished frontier with a proof and still would not be a larger-field
  census.

## Credit

The paired-star contract is PR #5747. The \(\mathbb F_2\) two-map rank 8 is
the merged result PR #6940. The partial \(\mathbb F_4\) census, the star
matrix \(D\), and the enumerator used here are the open PR #7006 at
`8889385a5bbe64df6f1378047b35d89e1aea355c`; this package does not rerun that
rank search as a substitute. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Independent human review and a proof-assistant proof are
unclaimed.

## Workflow feedback

The \(2^{20}\) cap on this class is an ordering artifact: three row pairs
cannot reach rank sum 8, so the frontier fills on a family the Schur
elimination settles. A link to the feedback discussion is enough:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200
