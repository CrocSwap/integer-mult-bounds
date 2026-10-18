# Sharp source-XOR cost for the ten-query mutable-source connector

**Scoped recursive-interface result; no new kappa.** The five-source common-B
connector of [PR1340](https://github.com/CrocSwap/integer-mult-bounds/pull/1340)
uses ten map queries, two readouts for each of the 31 nonzero masks, and twelve
source XORs. This package reduces the source XORs to **four and proves four
is the generic minimum at those query/readout counts**. The word must work for
every admissible B and A_m; specialized maps can be cheaper. All arbitrary dirty sources,
connector and private scratch restore. The common exact F2-linear B and
temporary exclusive access to source rows remain essential.

The new closed path is `0,4,5,1,3,7,6,14,28,16,0`. Only two edges combine
sources, each with a compute/query/uncompute pair. Every mask is a difference
of two boundary points. It derives from Ross Richardson's PR943 twelve-toggle
repair by omitting two boundaries, retaining predecessor attribution.

For fewer than four source XORs, restoring the sources leaves only the empty
word or two identical XORs. Connector-restoration parity then reduces every
full-span ten-query case to five independent directions, each queried twice.
The retained 945-pairing obstruction excludes full mask coverage. The new
proof is in [PROOF.md](PROOF.md), with exact evidence in
[CERTIFICATE.json](CERTIFICATE.json).

In PR1340's complete five-factor recursive fixture the arbitrary-map leaves
stay at 2016, internal nodes at 648, and borrowed dirty rows at four. Complete
source XORs fall from 12 to 4 and root instructions from 84 to 76. Its abstract
complete tariff falls from **2760 to 2744**, saving 16 units. A physical bill
must charge actual ports, routing, frames, precision, preparation and dispatch;
no selected supplier instance or physical runtime improvement is established.
The exact tariff conditions against the two read-only repairs are in the proof.

## Reproduce and evidence

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/mutable-source-shear-cost
```

Expected: `PASS_MUTABLE_SOURCE_SHEAR_COST`,
`PASS_INDEPENDENT_SOURCE_SHEAR_COST`, six passing package test groups, and
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The primary checker verifies the complete root and recursively expanded maps
and their literal inverses in a free noncommutative module on all **40**
arbitrary incoming rows. The separate checker imports no primary code. It
agrees on every one of the 945 pairing coverage sets via endpoint matching and
integer Walsh autocorrelation, checks all **8421** source-XOR words of length
at most three using column images, independently rebuilds the full invoice,
and performs **3456** dense matrix executions at L=1,2,3,4 on all dirty basis
inputs and mixed states. Seven semantic controls and eight on-disk corruptions
address restoration, source-map equality, readouts, factor order, scratch,
unpaid XORs, claimed optimality and source/certificate drift. Optimized isolated
read-only relocation and deterministic export are included.

[VALIDATION.md](VALIDATION.md) records exact commands and environments. The
finite checks support the explicit algebraic proof and bounded exclusion;
there is no proof-assistant or independent human review claim. No selected
cold replay, native supplier/compiler/owner admission, physical precision/tape
admission, all-size outer theorem or new exponent is claimed.

## Scope, overlap and source pins

Started at current main `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` after reading
AGENTS.md, autoresearch.md and CONTRIBUTING.md. Selector nonce
`7176f7cd8b71e813c3cb4218f83a8733` proposed recursive interfaces; the
`connector-alphabet-change` card is refined to PR1340's explicitly unoptimized
source-XOR cost. This is a complementary result on the same mechanism, not
a new mechanism claim. [TASK.json](TASK.json) records the scope, bounded method,
budget, predecessor and next questions. The [claim discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1352)
records entry and completion.

[SOURCES.json](SOURCES.json) pins the base, catalogue, selected context and live
PR943 inputs. [PREDECESSOR.json](PREDECESSOR.json) pins PR1340 at
`f1dcab36fa63f8226f70dd07e26f44afb9d39b51` with exact Git blobs and SHA256 hashes
for its three retained source files. No pending executable is imported. The
selected record, upstream files and frozen predecessor packages are unchanged.

## Open next questions

The practical next question is whether a supported supplier has a common-B
boundary with temporarily writable source rows. Trace one exact source-return
boundary and charge these four XORs, routing, precision and dispatch against
both read-only repairs. No such instance or favorable physical tariff is known
here; source immutability or an unfavorable complete price should stop adoption.

The remaining mathematical question is the weighted optimum when extra queries
or readouts trade against source mutations. Start with a bounded eleven-query
or four-readout domain and retain complete restoration. This theorem fixes ten
queries and two readouts per output, and supplies no bound on arbitrary longer
words. Structured questions and blockers are in TASK.json.

## Credit and license

Prepared by **Arham Tahir** with substantial **OpenAI Codex assistance** in
algebra, implementation, both checks and writing; no subagents. New material
is Apache-2.0 under the repository LICENSE.

Credit Arham Tahir's PR1340 for the common-map mutable-source extension,
ten-query minimum and complete-price fixture; **Ross Richardson's PR943/934**
for the universal path obstruction/repair, carried connectors and dirty
recursive lowering; **shhxera/CubeJerry's PR889** for common-factor batching;
and **Chafik Boukhalfa's PR628** for the dirty-product commutator lineage.
The retained PR943 NOTICE names the additional predecessor work. PR1185/1215
extend/check the read-only six-source model and are complementary. Douglas
Colkitt and the selected Rohan Arun/Jeremy Kothe construction's cumulative
community attribution remain intact.
