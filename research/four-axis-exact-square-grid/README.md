# Sharp four-axis rounding with the exact native square

**No new κ.** This package constructs an exact Gaussian-integer bijection for
one fixed native four-axis block, with the sharp error `sqrt(8) h`, exact sum
preservation, global Gaussian-unit covariance and the native identity
`F² = J`, where `J` complements all four coordinate bits. It also gives
`F⁴ = I`, the literal inverse `JF`, and exact agreement whenever the ideal
output already lies on the Gaussian grid.

CrocSwap/integer-mult-bounds#6758 achieved the same sharp error and global phase
covariance but explicitly failed fourth power. CrocSwap/integer-mult-bounds#6761
then proved that exact-square-compatible odd real rounders need affine-period
index divisible by 4096. The new invariant period has index exactly 4096 and
admits a complete correction-cycle certificate. This attains that predecessor
lower bound; it does not claim a minimum period for arbitrary coupled complex
rounders or a physical table-memory lower bound.

## Result and why it matters

For `A=W16/4`, the period is invariant under `B=SA`, the actual linear action
needed to close the native square. Six explicit parity equations inside the
Walsh integrality lattice define it. A 26,889-byte certificate supplies 568
cycle generators that expand to all 4096 real correction classes. Its real
correction norm is at most 2, with maximum correction numerator coordinate 5.
The native complex map uses the same table for both real lanes.

The complete theorem and quotient definitions are in [PROOF.md](PROOF.md).
For every integer `m`, repeated use of this **same fixed block** satisfies
`F^(2m)=J^m`, while odd powers have error at most `sqrt(8) h` relative to the
corresponding ideal power. Thus rounding error does not grow with the length
of such a word. This resolves the exact-square/fourth-power question retained
in the **Open next questions** of `research/four-axis-phase-covariant-grid`,
introduced by #6758 after Nick Petalas's #6574.

The certificate additionally forces `F(e0)=e3`. Consequently it attains the
sharp squared tensor discrepancy 24 on the explicit array
`X0=lambda e0^T`, `lambda_j=i^wt(j)`, while retaining the uniform sharp error,
bijection, exact sum and native square. The first-row defect is `D1+4e3`;
all other rows are zero. This settles the four-axis bounded-error,
exact-square attainment case left open by the separate
[tensor-obstruction proof](https://github.com/CubeJerry/integer-mult-bounds/blob/408969010e33a5aacdeecc164a554111e09f8f36/research/gaussian-rounding-tensor-obstruction/PROOF.md).
Section 7 of [PROOF.md](PROOF.md) gives the local lower-bound derivation as
well as the exact composition check. This is sharpness for that fixed witness,
not a worst-case tensor-discrepancy optimum or commuting row/column actions.

The finite map strengthens one native precision/group interface. The selected
multiplier, its five inherited assumptions and its κ remain unchanged. The
selected record at the pinned base is #6030 with κ `0.003125804`; stronger open
proposals do not change that accepted record.

## Reproduction and evidence

From the repository root, using CPython 3.12 and its standard library:

```sh
python3 -W error -B research/four-axis-exact-square-grid/verify.py
```

The expected status is `PASS_FOUR_AXIS_EXACT_SQUARE_GRID`, with 4096 real
classes, 568 cycle generators, maximum squared correction norm 64, maximum
absolute correction coordinate 5 and sharp complex squared error 8.

The registered replay runs all four checks in ordinary and `-O` modes:

```sh
python3 -B scripts/research_package.py --package research/four-axis-exact-square-grid --check-only
python3 -B scripts/research_package.py --package research/four-axis-exact-square-grid
```

Executed under CPython 3.12.14: metadata/source-pin validation and all eight
registered ordinary/optimization-mode commands passed. The optional discovery
replay regenerated the certificate byte for byte. These execution results
certify only the declared finite and algebraic scope.

The author check reconstructs a dense rational basis for the period and uses
its inverse for a separate quotient oracle. It checks every real class, 4096
paired complex fixtures, both inverse compositions, the direct native
coefficient formula, global phase, exact sum, and eight translated/signed
fixtures through 4091-bit inputs. The all-complex-input theorem follows from
the componentwise proof; the checker does not enumerate all `4096²` lane
pairs. No floating point, tolerance or Python `assert` is used for its
proof-relevant predicates.

Nine rejection controls cover missing cycles, weighted-sum and radius
corruption, a noninvariant period, a locally valid but square-incompatible
correction orbit, using the forward map as its own inverse, a false smaller
radius, an incorrect native coordinate phase, and falsely asserted row/column commutation. The square-incompatible
control retains integrality, sharp error, weighted sums, oddness and `K`
covariance, demonstrating that those properties alone do not certify the
new identity.

Separately assigned reviewers supplied independent checks:

* [independent_square.py](independent_square.py) imports no author module. It
  constructs a different, largest-mask coset section, uses dense Walsh sums
  and closed two-step orbit formulas, and checks all 4096 transitions,
  correction coverage, sharpness, symmetry and a corrupted correction.
* [review_lift.py](review_lift.py) independently reconstructs the rational
  lattice action and parity ranks, the phase identity, and the decisive
  predecessor lower-bound matrices. Its universal lifting argument and
  exact-on-integral-image observation are preserved in
  [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md).

[independent_sharpness.py](independent_sharpness.py) additionally reconstructs
the new table with a descending-column section, imports no author kernel,
checks the forced cycle and all 256 entries of the tensor witness, and obtains
exact squared discrepancy 24. Its review is retained in
[SHARPNESS-REVIEW.md](SHARPNESS-REVIEW.md).

These checks are independent mathematical/algorithmic review by separately
assigned AI agents. They are not human review, proof-kernel formalization,
supplier admission, or a complete multiplication-theorem audit. The replay
requires no unmerged predecessor Git objects, external network service or
third-party Python package.

The bounded discovery replay is optional and is not a proof obligation:

```sh
python3 -W error -B research/four-axis-exact-square-grid/search.py --output /tmp/four-axis-square-candidate.json
python3 -W error -B research/four-axis-exact-square-grid/independent_square.py /tmp/four-axis-square-candidate.json
```

It fixes the published period and enumerates seed-side real correction
numerators in `[-3,3]^16` with the residue, weighted-sum and energy constraints;
forced partner corrections can reach magnitude 5. The full compatibility graph
has 1120 negation/`K` orbits and 63,018 undirected edges including loops. The
stopping rule forces the compatible cycle `e0 -> e3 -> e15 -> e12 -> e0`
and its negations, then allows seeds 0 through 99 and stops at the first
complete greedy matching. Seed 0 succeeded; later seeds were not run. In CPython 3.12.14 the
replay regenerated the published certificate byte for byte. Integer-set
iteration in a different Python implementation may choose another matching;
any alternative certificate must be verified independently. No exhaustive
search over periods, matchings, or arbitrary rounders is claimed.

## Scope, costs and remaining obligations

The executable fast block uses 160 full-word additions/subtractions and 32
exact quarter divisions. Signs, low-bit reads, residue classification, table
addressing/retrieval, data traffic, scratch return, reversible cleanup and the
inverse's coordinate permutation are additional payable work. The expanded
logical table payload is 32 KiB: 4096 entries of sixteen signed four-bit values,
shared between two real-lane lookups. Twelve-bit class labels do not make
lookup constant-time or free in the repository's physical model. The raw
transform numerator bound is `16 M + 5` when input component magnitudes are
at most `M`; caller precision and word-width invariants remain separate.

The most direct next integration target is the retained four-axis dirty-port
and precision interface from Ali Romman's #6509 and the caller preserved by
#6758. This package provides the exact fixed-block algebra that that family
previously lacked. It does not bind the new classifier/table to every actual
caller input cut, provide a reversible physical lookup implementation, price
its cleanup/routing/compiler stock, or derive a changed complete paid
recursive profile. It therefore makes no κ improvement or claim that this
larger table is economical in a supplier.

No pointwise nearest-output property, norm-inward condition, general native
graph flatness, individual-axis commutation or all-size assumption discharge
is claimed. The source-history preflight requires full Git history; this
workspace is shallow and no ancestry-certification pass is claimed. Canonical
provenance pins and all executable proof data are self-contained as documented
in [SOURCES.json](SOURCES.json).

## Sources and credit

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[TASK.json](TASK.json) retains the exact `uniform-transfer-audit` card and
records the explicitly assigned structural-interface scope change.

The phase predecessor #6758 is pinned at
`362b20bc934500bc503e850059f0d34daa5dcae3`; the exact-square period obstruction
#6761 is pinned at `b78c8938b6d04b7c340c06d4e958947aeecd9270`. Exact inspected
file hashes and Git-blob IDs are recorded as external provenance, not runtime
imports. Nick Petalas's #6574
(`48e312ff18d5b66b0969148f615fdf5ce0f92edd`) supplies the native factorization,
correction predicates, sharp radius and half-grid lower-bound lineage. ToikY's
#6755 review identified the relevant phase/square/caller obligations. Ali
Romman's #6509 is credited for the retained caller used as a future integration
target; that caller has not been imported or reverified in this package.

Prepared by @CubeJerry (Jerry Chen) with substantial OpenAI Codex assistance
for mathematical exploration, implementation and writing. Separate agents
reviewed the all-integer lift/lattice and the full finite transition table;
their exact scope is retained in the review files. New work is Apache-2.0.
Predecessor results and their contributor attribution remain unchanged.

## Open next questions

1. **Can the exact-square block receive a competitive complete physical bill?**
   Bind this particular table and classifier to one exact retained four-axis
   caller. Start with its actual paid input cuts, reversible table access,
   low-bit traffic, helper/scratch restoration, precision and compiler stock;
   only then compare complete target/paid profiles. The current package has no
   such implementation or recurrence.
2. **Can a changed interface support consistent overlapping blocks?**
   The companion tensor-obstruction theorem rules out row/column commutation
   for the current state-free, globally unit-covariant, exact-on-integral-image
   contract, including this map. Start by identifying which property an
   actual caller can relax, or by specifying additional retained state and
   proving its composition law. Its error, reversible cleanup, routing and
   complete paid cost then remain separate obligations. The obstruction does
   not cover every changed lattice or stateful representation.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
