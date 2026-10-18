# P112: extra terms inside the minimal factor spaces do not lower the COPY-power minimum

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

For the fixed PR #2021 two-column P112 completion with `(j,k)=(0,1)` and
coefficient `+1`, the sharp separately billed minimum over **any finite number
of complex rank-one terms**, with both factors inside the matrix's minimal
nine-dimensional column and row spaces, is

```
min sum_i rho_i^q = 7*8^q + 7^q + 1,        0 < q <= 1.
```

Here `rho_i` is the actual binary support-pairing rank of term `i`. COPY has
minimum 64. For `0<q<1`, this exceeds the eight-rank-eight bill `8*8^q`.
The result extends [PR #2321](https://github.com/CrocSwap/integer-mult-bounds/pull/2321)
from exactly nine terms to arbitrary finite length **under the two stated
factor-space inclusions**. In the nine-term setting those inclusions follow
automatically from rank; in the overcomplete setting they are restrictions.
Zero-COPY nonzero terms are allowed.

[PROOF.md](PROOF.md) gives the new rank/compensation argument. It reconstructs
PR #2321's finite support classification and credits its nine-term attaining
profile `(8,8,8,8,8,8,8,7,1)`. With exactly eight mixed projections, projected
duality controls the exceptional cost-seven terms. With more mixed terms,
the aggregate cost-seven contribution has rank at most three.

An exact ten-term boundary control leaves the right factor space and attains
`(8,8,8,8,8,8,8,8,0,0)`. Thus the theorem cannot be applied to arbitrary
factorizations of this matrix. This is a scoped obstruction, not a completed
supplier or an improvement of the selected multiplication exponent.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/p112-overcomplete-factor-spaces --check-only
python3 -I -B scripts/research_package.py --package research/p112-overcomplete-factor-spaces
```

The registered verifier reports:

```
PASS_P112_OVERCOMPLETE_FACTOR_SPACES kernels=1022 class_pairs=132 entries=12544 COPY=64 controls=7
```

It binds the live prototype to its SHA256 and Gram/binary convention, recomputes
all character kernels over the rationals, checks their intersections and all
class pairings, and uses two binary rank elimination methods. It verifies the
nine-term attainer, an eleven-term in-space zero-COPY cancellation fixture,
and the ten-term out-of-space boundary, with all-entry matrix multiplication.
It checks integer majorization premises for all real `q` in the stated interval.
Meaningful rejection controls cover altered physical factors, omitted
compensation, a V/V undercharge, changed source bytes, a changed character
kernel, a Hermitian-transpose substitution, and an undercharged certificate.
An exact nonreal phase fixture checks the ordinary-transpose convention.

[CERTIFICATE.json](CERTIFICATE.json) records the deterministic finite evidence,
including the coefficient witness and complete rank table. Normal replay is
read-only and compares the entire certificate. `verify.py --write NEW_FILE`
regenerates evidence into a new file exclusively; it refuses to overwrite.
No predecessor program or pending PR checkout is needed for replay. The
universal argument is written mathematics; the checker certifies its finite
premises, not a formalization of that argument.

## Task, overlap and scope

[TASK.json](TASK.json) records the original `complex-new-helper-inventory` card,
priority revision 4, the selection nonce and explicit scope change to the
more-terms handoff in [discussion #2006](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18940755).
The claim is in [discussion #2006](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18942846). This algebraic side result
screens whether additional terms alone can improve one fixed masked decoder's
power bill; it does not pass the original physical-inventory acceptance gate.

The fixed completion is from this account's merged
[PR #2021](https://github.com/CrocSwap/integer-mult-bounds/pull/2021), head
`9943467c4b24d2050275a202e3866cfc522afbe7`. PR #2321 at
`0665be26c2db1bd7f393d829e786698b34b626e4` proves the exactly-nine-term result.
A concurrent coefficient-family investigation varies the completion coefficient
while retaining nine terms; this package fixes coefficient `+1` and changes
term count. It does not vary ports or audit PR #2308's shared-plane completion.
[SOURCES.json](SOURCES.json) pins the main-branch prototype and records
predecessor proof provenance. Pending predecessor code is not a runtime dependency.

## Open next questions

- What is the sharp power minimum for this same matrix when factors may leave
  either minimal factor space? The explicit ten-term boundary already beats
  the in-space minimum for `q<1`. A useful first step is to classify the explicit
  one-dimensional extension `col(R)+Ce_0` of the right space and seek a lower bill than
  `8*8^q`. The present character catalogue does not cover that extension.
- Can a concrete physical implementation share COPY work across terms?
  Separate support billing is a theorem premise. A useful next step is one
  legal sharing construction with its frames, restoration, precision and
  reserve fully charged; no such realization is supplied here.

## Credit

The completion and COPY65 predecessor are from commdata2338's PR #2021.
Hanhong Zhao (@Hope7Happiness), PR #2321, supplied the complete support catalogue,
sharp nine-term theorem and rational attainer. This package independently
reconstructs those finite premises and extends the proof to arbitrary length
within both minimal spaces. Related support/compensation lineage includes
Arham Tahir (PR #1591), Gareth Davidson (@bitplane, PR #1652),
woklerx (PR #1077/#1447), DreamingOfClouds (PR #717), and themilkman216
(PR #968), together with the PR #845 root-geometry lineage.

New work is Apache-2.0. OpenAI Codex performed the derivation, implementation,
checking and writing. No independent human review or formal verification is
claimed. See [TASK.json](TASK.json) for the assistance disclosure.
