# Michiel Kosters and Abe: parallel historical contributions

Reviewed 2026-10-08 after Douglas supplied the repository and suggestion.
These contributions concern the earlier compact-control checkpoint
`83/10^12 = 8.3e-11`. They deserve acknowledgement independently of whether
later constructions supersede them. Neither changes the current selected
conditional witness, approximately `5.1016920170078e-5`.

## Abe / @abe_asfaw: removing a redundant complex center

Douglas supplied Abe's suggestion to factor the complex central matrix
`M_ST = (|S intersect T|-1)/2` through h centers instead of h+1, with dyadic
coefficients. No public announcement URL was supplied. The mathematical
suggestion and account attribution are recorded from Douglas's message;
the suggestion is summarized here.

The rank claim is correct at the proposed h=24. For h>=4, the triple-incidence
matrix B has column rank h, and

```
M = B (I - J_h/9) B^T / 2.
```

The middle factor is invertible for h!=9, so rank(M)=h. At h=9 it instead has
rank h-1; this exception is outside the candidate under consideration.
Rank alone would not establish a dyadic implementation. An explicit one is
to retain the total sum and all point sums except point 0. For a target S:

```
0 not in S:  (sum_{j in S} g_j - total)/2
0 in S:     total - (sum_{j not in S} g_j)/2
```

Both formulas recover the original coefficients using only additions,
subtractions and halves. They eliminate one center without division by three.
The identical rank-h principle, with another explicit dyadic factor, is already
preserved in our [historical note](../../docs/research/dyadic-central-factor.md)
and [proof](../../notes/dyadic-central-factor.tex). We credit Abe's parallel
observation without making an unsupported priority or dependency claim.

Our [checker](verify.py) verifies all 4,096,576 central coefficients at h=24,
then uses the old uncompressed side-role count and the suggested counts
`W=2N+I(v*z_c+h)`, `L=I*h^2`. Exact logarithm enclosures identify h=24 as best
for integers h=21,...,199 and exclude h>=200 with a decreasing upper bound.
The complex saving is approximately **5.30775793289321e-10**. An explicit
conservative saving `5307/10^13` supports the historical assembly candidate

```
kappa = 21/(2*10^11) = 1.05e-10
minimum margin = 1057471/10^16
strict gap = 7471/10^16
ratio to old checkpoint = 105/83 (about 26.5% improvement)
```

This checks scalar coefficients, counts, a guard size hypothesis and the
assembly inequalities. It does not by itself replay a complete modified
multitape implementation or its precision induction. The existing center
note supplies the relevant common-frame/dirty-scratch reasoning for that
style of factor change.

## Michiel Kosters / user-supplied @one_line_proof

Source: [mathematics_ai, integer-multiplication-109](https://github.com/michielkosters/mathematics_ai/tree/2e0aa64ca09c87fc94f8575f59493f70cf929d71/problems/integer-multiplication-109),
commit `2e0aa64ca09c87fc94f8575f59493f70cf929d71`.
GitHub identifies the owner as Michiel Kosters. Douglas supplied the X
association; the GitHub profile does not independently link that handle.
No specific announcement post was supplied.

The proposed construction combines a weighted-hypergraph disjoint-sum circuit,
coordinate frames and an alternating-residual repair, compressed dyadic
centers, whole-bank stage reuse and globally aligned bit pairing. The finite
candidate is **609/10^12 = 6.09e-10**, about 7.34 times the old checkpoint.
The source credits the existing DAG compiler, paired exclusions, stage reuse
and compact-control assembly. Its own README explicitly leaves the complete
motif-to-tape transfer and precision integration unverified.

We reproduced:

* Five local tests, including weighted lower-rank hyperedges, small full/lazy
  circuits, paired bit outputs/frames and dirty-scratch restoration.
* The full supplied certificate, including its complete h=26 disjoint-output
  check and h=50 bit support/frame checks.
* Independent rational saving enclosures and all 31 constraints/seven margins
  using our retained compact-control arithmetic. The minimum margin is
  `761619/1250000000000000`; its gap over the candidate is
  `369/1250000000000000`.

There is a reproducibility defect in the published manifest: 13 hashes expect
CRLF line endings, whereas the committed files use LF. The unmodified verifier
therefore stops at `aligned_bit_circuit.py` in a normal LF checkout. Every
mismatch is explained exactly by converting LF to CRLF; no content edits are
needed. Our wrapper copies the source to a temporary directory, restores only
those manifest-expected bytes, verifies their hashes, and runs the unmodified
checker there. Both the defect and the successful replay remain explicit in
[verification.json](verification.json). A portable upstream fix would generate
hashes from committed bytes or specify canonical LF hashing.

The new research source is referenced by commit rather than copied into this
repository. Only the vendor directory carries an explicit license in the
reviewed tree. This review adds our own checker and result receipt, and makes
no claim that the complete multiplication theorem has been independently proved.

## Reproduction

```sh
# Abe's scalar/count/assembly checks, using only this repository:
python3 research/parallel-announcements/verify.py

# Also replay Michiel's pinned checkout (the argument is the problem directory):
python3 research/parallel-announcements/verify.py \
  --kosters-root /path/to/mathematics_ai/problems/integer-multiplication-109
```

Use the pinned commit above and an unmodified checkout. The wrapper records
the actual committed file hashes, the line-ending reconstruction and exact
arithmetic results. Neither author's contribution is used to claim a new
frontier or exclusive priority.
