## What changes and why

The exact source/occurrence codecs and evaluated smaller-rank library do not
by themselves identify an instruction in the fully expanded compiler. Different
chronological cuts can revisit the same physical field, while nested smaller
programs introduce further source-row translations and their own owned banks.

This package constructs the complete **ordered rank-one paid-leaf projection**:
given any leaf ordinal, recover its exact nested whole-call path, canonical
base axis and original source-row or owned-bank identity. The inverse recovers
the ordinal. Every nested whole-call input vector maps injectively to its
persistent caller fields, with the same inverse correspondence on return.
Global leaf-to-owner injection is explicitly false and is tested as a control.

## Exact result and novelty

A new weighted paid-path suffix table stores only (depth, rank-product)
counts, with the actual smaller-program widths and leaf counts at its bottom.
It selects the precise chronological cut without enumerating preceding paths
or replicas. Upward source/complement/exit translations compose through
strict rank descent and preserve the full owned-bank invocation namespace.

Credit CrocSwap/integer-mult-bounds#7345 for evaluated library metadata;
CrocSwap/integer-mult-bounds#7346, CrocSwap/integer-mult-bounds#7347 and
CrocSwap/integer-mult-bounds#7348 for the occurrence, source and complement
port codecs. CrocSwap/integer-mult-bounds#4507 and
CrocSwap/integer-mult-bounds#5071 already prove batching and singleton exit
cuts. An exit-only replica-divmod wrapper was rejected as insufficient novelty.
The new result is their recursive chronological leaf/field composition.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
All eight retained files have exact commit, Git blob and SHA256 pins in
`SOURCES.json`. The package replays without Git or network dependencies.

## Verification and reproduction

```sh
python3 -I -W error -B research/chronological-leaf-owner-index/verify.py
python3 -I -O -W error -B research/chronological-leaf-owner-index/verify.py
```

Expected: `PASS_CHRONOLOGICAL_LEAF_OWNER_INDEX`.
The distinct literal oracle imports no production source/owner/suffix codec.
It materializes classes and actual parent/child slot lists, then recursively
expands every smaller program. It checks 4,102 leaves, 2,970 complete calls
and 3,746 input ports over 78 ranks, with 1,183 owned-field leaves and 106
cross-replica complement batches. Fifteen controls detect merged cuts,
replicas and namespaces, dropped paid multiplicities, wrong returns and
invalid library/port boundaries.

A separate direct digit/last-owned-site oracle checks selected queries among
68,719,476,736 chronological cuts using 13 suffix states and 12 source states.
Another nonexpanded fixture has 94,591,411,200,000 source rows. These are
formal metadata examples, not native supplier witnesses. The written proof
supplies the universal interval and ownership arguments and explicit indexed
and serialized-tape metadata costs with all supplied integer bit lengths.

Separate peer proof review and a direct nonminimal-library recursion oracle
check 24,137 further leaves, 24,205 calls and 25,120 ports, with three detected
semantic mutants. See `independent/REVIEW.md` and its reproducible receipt.

## Limits and kappa status

**No new kappa.** The selected conditional 0.00363005817 and all five framework
assumptions remain. This emits the paid-leaf projection, not the interleaved
scalar/phase/adapter word or global axis embeddings. The actual selected
native manifest/library, physical gathering/return, owned-storage realization,
numerical endpoints and full fixed-tape dispatcher remain open.

The general interface permits A above every target rank but accepts a supplied
valid library and charges its actual bits. The default library generator's
stronger width bound is not transferred to that case. Indexed source names
do not grant free payload access. All unchanged native correctness, adapter,
arbitrary-input and completed-return contracts remain inherited.

Prepared for **@CubeJerry**, with substantial **OpenAI assistance** in research,
proof, implementation and verification. Jacob Alan Sussman, zxv, Mihir
Srivastava, JoyboyBrian and the complete credited compiler/physical lineage
retain attribution. Independent human or formal-kernel acceptance is not
claimed. No selected certificate, frozen predecessor or unrelated file changes.
