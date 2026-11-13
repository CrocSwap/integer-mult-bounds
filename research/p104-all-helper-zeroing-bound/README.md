# Global funding bounds for helper restrictions with fixed native operations

Three source-scoped theorems exclude a complete signed-moment gain on the exact
#7481 native when its operations and paid ranks are retained and only
identically zero MOVEs are omitted. All new basis conversion, zero transfers,
storage, ownership and ordinary work is optimistically free.

| Allowed helper restriction | Proved kappa interval | Certificate |
| --- | --- | --- |
| Any subset of the 1,101 original helper coordinates set to zero | `0 <= kappa <= 1/2` | 468 MOVEs charged to 467 lost helper targets |
| Arbitrary scalar linear input subspaces, independently inside every group with matching entrance AND exit frames | `0 <= kappa <= 1/100` | 430 row components and 612 exact subset inequalities |
| Any helper-input relation surjective onto a retained subset of original helper coordinates, independently of mains; correlations may cross boundary groups | `0 <= kappa <= 1/4` | Rank 463, five exact relations, 442 singleton row spaces and four dependent blocks; 31 dependent-subset funding inequalities |

Main inputs remain arbitrary and independent. The second theorem includes
correlations within a compatible helper group; it does not allow correlations
between groups, address-dependent operators or correlations with main inputs.
The proof debits every lost productive direction before reporting paid savings.
**No new kappa or unconditional multiplication theorem is claimed.**

The third theorem permits nonlinear or operator-valued helper preparations when
the retained original inputs remain jointly arbitrary. It charges each demoted
original helper target. It does not assign old target prices to new decoded
productive coordinates. `GRAPH-PROOF.md` gives the exact surjectivity and whole-
array argument; all preparation and cleanup remain optimistically free.

## Why the certificate covers all choices

Exactly 5,811 original MOVEs have nonzero main coefficients and cannot vanish.
The other 468 have only helper support. `PROOF.md` supplies a simple assignment
for all coordinate subsets. Its only double charge has two rank-one MOVEs paid
by one rank-four target, valid throughout the square-root tariff range.

`SUBSPACE-PROOF.md` handles arbitrary correlated inputs through annihilators.
A deleted MOVE's projected coefficient row must lie in the killed group's
annihilator. A source-derived weighted rank inequality therefore charges all
removed MOVEs to the number of productive directions lost. Only 21 row
components are nontrivial; the largest has six rows. All 612 nonempty component
subsets are checked exactly. The universal subspace conclusion follows by
linear algebra, not by sampling input subspaces.

The independent prime-field interpreter regenerates the actual projected rows,
checks the component direct sums and proves rank lower bounds using nonzero
minors. Modular zeros are never promoted to rational zeros. The price envelope
uses the integer comparison `9*1000^100 < 1023^100`, so no floating point or
sampled kappa grid appears in the proof.

For the global theorem, a new independent rational interpreter reconstructs
all 468 helper-only rows. Exact dependencies and a nonzero minor modulo
1,000,003 give rank 463. Their row spaces decompose into 442 singletons and
blocks of 11, 5, 5 and 5 rows. All 2,140 local subsets are checked; only 31 are
dependent. Independent prefix ranks give their minimum linear basis prices,
and every one satisfies `6*price >= 11*paid_rank_sum`. The exact inequality
`9*6^4 < 11^4` extends this to every power price in the quarter interval.
A block Laplace expansion combines the bounds despite overlapping helper
columns. The proof covers all helper restrictions in the stated class, not
just the enumerated subsets or sampled preparations.

## Complete caller and source pins

The wrapper reconstructs every target and paid entry of the retained signed
caller: 17 native calls, 22,461 productive fields, 110,519 paid jobs and linear
rank surplus 1,424. Other caller operations and main targets are fixed. Each
native occurrence may choose its own restriction; each has nonpositive gain.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Source #7481: `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b`.
Native SHA256: `acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
The exact caller, native word, invoice and original notice are bundled;
`SOURCES.json` records original paths, Git blobs and hashes. #7481 is unselected;
this package does not admit its claimed complete bound.

## Reproduction

From the repository root:

```sh
python3 -I -W error -B research/p104-all-helper-zeroing-bound/verify.py
python3 -O -I -W error -B research/p104-all-helper-zeroing-bound/verify.py
python3 scripts/research_package.py --package research/p104-all-helper-zeroing-bound
```

Expected status: `PASS_HELPER_COORDINATE_AND_SUBSPACE_FUNDING_NO_GAIN`.
The standard-library replay needs no network or external Git object and does
not modify package files. Controls reject changed source bytes, omitted or
duplicated MOVEs, forged ranks, a false component direct sum and an overpriced
dependent row pair. Correctly funded dependent and independent examples pass.
Executed final checks are recorded in `VALIDATION.json`.

## Novelty and limitations

#7307 studied unchanged-owned-word zero-input and direct-CLEAR predicates.
Here the helper input space changes, lost targets are charged, and the
certificates cover all coordinate subsets and all matching-boundary scalar
subspaces. The global original-coordinate result further permits cross-group
correlations through the verified rank condition and overlapping-column
composition proof. The source, #7113 signed caller and all predecessor work retain
their credit. These results do not permit new frame choices, changed scalar
contacts, altered main inputs, target splitting or
new productive boundaries. All five foundational assumptions and whole-job
accounting conventions remain inherited. Neutral restrictions may still enable
a different source or change finite ordinary constants.

## Open next questions

Can a restriction combine with changed scalar contacts, cache deletions of
nonzero MOVEs or frame choices to improve the full bill? Can a different
productive interface avoid the rank funding? Those questions require a new exact source,
complete target debits and a physically valid caller; this package does not
supply them or rule them out.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance in
exact rational research, a separate modular implementation, mathematical review
and packaging. Retain Clear1nsight's #7481, Rohan Arun's #7113 lineage, ToikY's
#7307 and all source notices. Independent checking here means separate
algorithmic evidence, not independent human or proof-kernel acceptance.
Apache-2.0; retain `NOTICE`, `LICENSE` and `inputs/PREDECESSOR-NOTICE`.
