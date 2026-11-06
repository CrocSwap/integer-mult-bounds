# Sharp joint interval transport for the balanced dirty word

**Scoped written theorem with exact finite corroboration; no new kappa.**

For the unchanged [#628](https://github.com/CrocSwap/integer-mult-bounds/pull/628)
balanced word, with h=ceil(log2 n) shared dirty scratch registers, the sharp
uniform joint interval coefficient envelope is

```text
F(h) = floor(h^2/2) + h + 2,  h >= 0.
```

Every ordered pair of complete ideal-leaf cuts and both word orientations
are covered. The bound holds without commutation for contractive operator
factors. For commuting factors whose every subset product has norm at most
G>=1, the bound is F(h)G. The word, scratch allocation and leaf interfaces
are unchanged. Uniform sharpness means the maximum over n of each height;
it does not assert equality for every n.

This closes the explicit sharp-constant question in Arham Tahir's
[#1374](https://github.com/CrocSwap/integer-mult-bounds/pull/1374) and Nick
Petalas's [#5872](https://github.com/CrocSwap/integer-mult-bounds/pull/5872).
The latter upper bound was h^2+2h+3 for h>=1. The matching all-height lower
family is entirely credited to #1374; this package supplies the new upper
proof. The exact destination-only result of Philippe Van Velzen's
[#2177](https://github.com/CrocSwap/integer-mult-bounds/pull/2177) is separate.

| Height h | #5872 upper bound | New sharp envelope |
| --- | --- | --- |
| 1 | 6 | 3 |
| 2 | 11 | 6 |
| 3 | 18 | 9 |
| 4 | 27 | 14 |
| 8 | 83 | 42 |
| 16 | 291 | 146 |

## Why the bound improves

[PROOF.md](PROOF.md) proves that an inverse of a positive prefix has no two
consecutive occupied source-column entries in row order `(target,z1,...,zh)`.
Its scratch block has at most one occupied direction per scratch pair.
Together, these give total scratch-row mass at most floor((h+1)^2/2).

The six chronological phase-pair formulas always place an inverse-positive
prefix or positive suffix on the right of a cross-child product. That
direction matters: an ordinary positive prefix can violate the new scratch
mass bound. Applying the invariant to the correct factor, and retaining one
endpoint cancellation in the first-to-last phase pair, proves F(h).

Hanson Sun's [#1085](https://github.com/CrocSwap/integer-mult-bounds/pull/1085)
entry invariant is an explicit proof premise. Charles Bethin's
[#1278](https://github.com/CrocSwap/integer-mult-bounds/pull/1278) supplies the
phase decomposition and the squarefree theorem needed for the commuting
subset-product corollary. These retained proofs were read in full; their
all-size premises are not established by the finite certificate here.

## Exact verification and reproduction

The Python 3.12 standard-library verifier imports no predecessor executable.
Its free noncommutative polynomials retain repeated indices and collect
equal words before measuring mass; no commutative or squarefree quotient
is imposed. A separate scalar engine skips completed subtrees using the
four phase formulas and uses rational Gauss-Jordan inversion. Its sampled
prefixes are checked against the literal polynomial engine.
That compressed-prefix/Gauss-Jordan corroboration strategy follows #1374;
the implementation here is separately written and imports none of its code.

- All positive prefixes at every n=1..64: **95,735 boundaries**, checking
  the new inverse source-occupancy and scratch-mass invariants, both
  prefix/inverse scratch-pair restrictions, protected boundaries, full
  restoration and literal inverse word order. There are **317** sampled
  exact inverse identities and independent scalar-prefix comparisons.
- **89,528 nonempty intervals**, both orientations, at
  n=1,2,3,5,8,11,16. Every surviving monomial is checked without assuming
  squarefreeness. Empty intervals are identities. This corroboration does
  not claim priority for the predecessor's finite maxima.
- **2,118** exact phase-identity checks, including reverse order: all child
  cuts at n=2,3,4,5 and five selected child cuts at n=8,11,16.
- The predecessor's attaining scalar family is checked by literal free
  algebra at h=1..6 and by compressed exact matrices at h=1..32, the last
  having n=4,294,967,296 factors without expanding its word.
- **15 controls** cover adjacent source occupancy, reciprocal scratch
  support, an oversized entry, invalid capacities/sign, applying the
  scratch bound in the wrong prefix direction, unreversed inversion, a
  changed leaf sign, noncommutation, absence of a squarefree quotient,
  a false linear bound, an understated sharp bound and wrong matrix order.

From the repository root:

```sh
python3 -B -W error -X dev research/chronological-dirty-intervals/verify.py
python3 -B -W error -X dev -O research/chronological-dirty-intervals/verify.py
python3 -B scripts/research_package.py --package research/chronological-dirty-intervals
python3 -B scripts/check_research_commit.py --package research/chronological-dirty-intervals --check-source-history
```

Expected markers are `PASS_CHRONOLOGICAL_DIRTY_INTERVALS`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Default verification is read-only and compares every deterministic field
with [CERTIFICATE.json](CERTIFICATE.json). `--write PATH` is explicit
certificate authoring, not evidence that a preexisting certificate passed.
The stdout receipt hashes every package .py/.md/.json file present at run
time. The mathematical replay works from a Git-free export of this package;
source-provenance validation additionally requires the pinned Git history.

The finite emitter is capped at 64 factors. The compressed scalar oracle
is capped at 2^32 factors and only uses +-1 coefficients. All fixtures,
cut selections and stopping coverage are explicit in the code/certificate.
Python-managed allocation is used; no fixed-allocation implementation is
claimed. No network, subprocess, numerical solver or floating point is used
by the mathematical verifier. Normal and optimized execution are required
by [VERIFY.json](VERIFY.json).
Both registered commands passed on Linux x86_64 with CPython 3.12.14;
the separate package metadata/source-pin check also passed.
The committed-byte preflight passed. Its optional `--check-source-history`
extension could not complete because this checkout is shallow; it reports
`source-history check requires full Git history`. No history-wide ancestry
validation is claimed. The base and all declared sources use the same
pinned canonical-main commit; there are no unmerged-source dependencies.

## Scope and provenance

Base canonical main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[SOURCES.json](SOURCES.json) pins exact Git and SHA256 bytes for the selected
record, task card, dispatcher, imported proof premises, lower family, prior
upper bound and destination-only context. They are historical provenance,
not runtime imports. The assignment narrows the archived
`commuting-dirty-precision` follow-up to the still-open sharp joint constant;
it is explicitly a changed scope from the current caller-admission card.

The lead checked live overlap before assignment and found #5872's explicit
remaining sharp question. This package does not treat that bounded overlap
search as proof of global novelty. The written all-size induction, finite
corroboration and imported lower theorem are distinct claims. Independent
human review and formal proof-kernel verification are unclaimed.

The selected conditional kappa 0.003125804 and its five framework assumptions
remain unchanged. Internal rounded leaves, inverse preimages, nonlinear error
support, precision/tape integration, preparation, physical movement, compiler,
stock, analytic recovery and a complete caller invoice remain unproved or
unrun here. No actual cyclic rounding failure or precision minimum follows.

## Open next questions

1. What is the exact joint envelope for **each n**, rather than the sharp
   height-uniform envelope? For example n=3 has finite maximum four, below
   F(2)=six. Derive recurrences that retain unequal child heights and the
   available phase cuts. The obstacle is simultaneous attainability of
   support and source-occupancy maxima. This may refine sufficient bounds
   for specific unchanged words; it is not a reason to expand a supplier.
2. Can a concrete rounded caller benefit from this joint bound after its
   actual perturbation support is retained? Start with its exact leaf error
   contract and compare the destination-supported #2177 bound before using
   a joint bound. Negative-leaf preimages, preparation, internal magnitudes
   and the full physical invoice must still be supplied. No such integration
   is attempted here.

Structured versions and the frozen stop decision are in [TASK.json](TASK.json).

## Credit

Prepared for **@CubeJerry**, with substantial **OpenAI Codex assistance** in
mathematics, implementation, verification and writing. New material is
Apache-2.0. Chafik Boukhalfa supplies #628/#905 and the retained word lineage;
Hanson Sun supplies #1085; Charles Bethin supplies #1278 and #1416; Arham
Tahir supplies #1374's exact lower family and sharp-constant question; Nick
Petalas supplies #5872's predecessor upper improvement and explicit handoff;
Philippe Van Velzen supplies the separate #2177 result. Philipp/mightyOil,
Gareth Davidson and 0xkilgore retain the precision, perturbation, counting
and restoration lineage credited in those predecessor sources.
