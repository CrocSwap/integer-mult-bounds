# Independent path audit of the complete T740 phase map

This audit corroborates [PR3297](https://github.com/CrocSwap/integer-mult-bounds/pull/3297)
at `bab1899ce1c6fd43d073ac7c3a8e7c3e69008c0e`, for **owner replica 0 and port 0 only**.
The exact [receipt](RESULT.json) records 183 primitive gates, 1,174 uncancelled
signed paths, all 72 normalized matrix terms and 21 valid monomial divisions
recovering the twenty phase coordinates. No discrepancy was found in this scope.
The injectivity theorem and inverse belong to PR3297; this is independent
verification, not a new phase-map theorem or a new kappa.

## What this adds

PR3297 already contains primary and independent sparse matrix replays. This
package supplies a separately implemented source projection and an **uncancelled
path expansion**. It does not import or execute either predecessor checker.
`source.py` reads the pinned raw JSON and reconstructs the thirty hosted rows,
local phase adapters, residual phases, bridges and signed terminal exchanges.
`paths.py` retains all signed paths separately until the end. Cancellation of
1,174 paths then gives the exact 72-term matrix in the byte-for-byte predecessor
export. The different intermediate representation tests cancellation and source
binding beyond calling an existing checker.

`inverse.py` independently substitutes those terms into the published inverse.
Each of its 21 divisors must reduce to a single Laurent monomial with coefficient
`+1` or `-1`. The receipt shows coefficient `+1` in every case. Thus no divisor
can vanish when all twenty phase coordinates are nonzero. No floating-point
arithmetic or sampled-character acceptance is used for these identities.
[The proof and audit boundary](PROOF.md) explain why this checks the exact claim.

The ten test groups include a direct Gaussian-integer matrix oracle, every
six-bit parity function on every six-bit character, individual observability of
all twenty sites, and five source-semantic mutants. They also reject a corrupted
matrix coefficient, nonmonomial/zero/nonunit divisors, source/export corruption,
invalid journal preimages and exhausted path/gate capacities. Tests remain active
under Python optimization. These are author checks, not independent human or
proof-kernel review.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py \
  --package research/t740-phase-map-path-audit
```

The registered commands run the full source-bound audit and all ten behavioral
groups in normal and optimized modes. The receipt is deterministic. To inspect
a newly computed receipt without overwriting the retained one:

```sh
python3.12 -Werror -B research/t740-phase-map-path-audit/verify.py --emit
```

Local verification used CPython 3.12.15 and 3.13.5 on x86_64 Linux/WSL2.
`ruff check research/t740-phase-map-path-audit` supplies repository diagnostics.
The commit and final hosted-check status belong to the PR and session handoff,
not to this scientific input receipt.

## Sources and cold-checkout closure

The scientific base is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) binds every external runtime input to that canonical
ancestry, with Git blobs and SHA256 hashes. The selected record and catalogue
are provenance only. The source projection authenticates the base fill and
145-edit lift journal, then reconstructs this owner's thirty hosted rows.
It does not rehash the serialized full 2,717,280-row T740 expansion or rerun its
allocation legality census.

[EXPORT.json](EXPORT.json) identifies the original path, exact head, blob,
SHA256, author and public URL of `inputs/PR3297-RESULT.json`. This file is retained
byte-for-byte as the expected answer, not treated as an available foreign Git
object. The independently reconstructed answer must equal it. No runtime fetch,
foreign PR-head object or peer's unpublished work is needed in a cold checkout.
The published inverse is reimplemented with its attribution retained; no
predecessor Python code is vendored.

## Limits and family decision

This is one finite symbolic certificate and a scoped audit under the inherited
completed-call, eight-data-stream interpretation. It does not revalidate that
interpretation's physical realization, helper-bank behavior or native compiler.
Source acquisition, routing, stock, precision, tape, restoration, the complete
consumer, both supplier caps and the outer/all-size theorem remain separate.
There is no supplier admission, native execution, complete multiplication theorem
or selected-frontier change.

Hosted prefixes, local phase adapters, translations, charts and event order are
fixed. Other owners and ports are not checked here. The separately reserved
source-normalization extension is outside this package and is not a dependency.
Ross Richardson's arbitrary-address reciprocal-chart repair changes
a different contract and is also outside this audit. No construction or search
expansion follows from corroborating the fixed-word theorem. Equal phase
functions need not have identical bases; rank preservation requires independent
replacement axes.

## Open next questions

- Does a specified legal change of charts or hosting evade the fixed-word phase
  obstruction without repaying its saving? This matters to the T740 supplier
  decision. Start with an explicit completed-call operator and a complete cost
  ledger, not another fixed-schedule rank search. The legal source/consumer,
  native and physical contracts are blockers.
- Can the theorem be transported to other actual owner/port contexts? This audit
  does not do so. The separately reserved extension must bind its own hosted
  projection and ambient normalization; do not infer it from the present receipt.

## Credit

Sagar Thakrar, `thakrarsagar`, supplied PR3297's complete phase map and rational
inverse, following the same contributor's PR3272 five-site result. Credit
Tekalign for PR3204's four-site rigidity, Gonzalo Mier for PR3196/3199/3263,
Nick Petalas for
PR3187's source-bound physical replay, Gareth Davidson for PR1387's obstruction,
Jeremy Diviney for PR3148's fill, dcharb78 for PR3133's retained allocation and
credits, and Rohan Arun for the audited assignment mechanism. Marius-Paul
Dumitrean, Jeremy Kothe and the retained geometry/native/word lineage keep their
predecessor attribution. Canonical source notices are unchanged.

Nick Petalas. Apache-2.0. Assistance and review limits are recorded in TASK.json.
